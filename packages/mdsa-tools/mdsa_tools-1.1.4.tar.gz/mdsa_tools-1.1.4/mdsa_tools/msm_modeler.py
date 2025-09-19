'''
Use results of systems analysis as candidate states for MarkovStateModel Kinetics analysis (or foundations of)
- cluster pca/umap embeddings at different target n_dimensions,
- or pull H-bond values via systems_analysis.extract_hbond_values()
  and use those in replicate maps instead of k-means labels.

Some features are specific to our workflow (see the paper) we use (cohesion over time, transition matrices,
implied timescales, ck test, etc.).

See Also
--------
mdsa_tools.Viz.visualize_reduction
    plot pca/umap embeddings.
mdsa_tools.Data_gen_hbond.create_system_representations
    build residue–residue H-bond adjacency matrices.
numpy.linalg.svd
    linear algebra under the hood.
    
'''

import numpy as np
import os
import pandas as pd


class MSM_Modeller:
    """
    tiny helper for poking at candidate states and building a very simple msm
    from an embedding space (think: pca/umap coords + k-means labels).

    Parameters
    ----------
    labels : array-like (n_frames,)
        integer state/cluster labels per frame (0-based, lines up with centers rows).
    centers : array-like (n_states, n_dims)
        cluster centers in the same space as `reduced_coordinates`; row i == label i.
    reduced_coordinates : array-like (n_frames, n_dims)
        low-d embedding coords (pca/umap) for all frames, concatenated by replicate.
    frame_scale : list[int]
        number of frames per replicate in the same order used for labels/coords.

    Attributes
    ----------
    labels, centers, reduced_coordinates, frame_scale : stored as given (or None)
    transition_probability_matrix : np.ndarray
        set after calling create_transition_probability_matrix(); shape (n+1, n+1)
        with headers (row/col 0 hold state ids).

    Notes
    -----
    intentionally lightweight—we stash the common artifacts so you don’t have to
    pass them to every call.
    """

    def __init__(self, labels, centers, reduced_coordinates, frame_scale):
        """init with labels/centers/coords/frame sizes—nothing fancy."""
        self.labels = labels if labels is not None else None
        self.centers = centers if centers is not None else None
        self.frame_scale = frame_scale if frame_scale is not None else None
        self.reduced_coordinates = reduced_coordinates if reduced_coordinates is not None else None

    # -------------------------------------------------------------------------
    # candidate state evaluation
    # -------------------------------------------------------------------------
    def rmsd_from_centers(self, X, labels, centers):
        """
        per-cluster rmsd of points to their assigned cluster center.

        Parameters
        ----------
        X : array-like (n_samples, n_dims)
            points in embedding space (pca/umap) for the slice you care about.
        labels : array-like (n_samples,)
            cluster labels for each row of X (0-based).
        centers : array-like (n_states, n_dims)
            cluster centers; centers[i] corresponds to label i.

        Returns
        -------
        np.ndarray (n_present_states, 2)
            columns: (cluster_id, rmsd). ints then floats.

        Notes
        -----
        euclidean norm in the embedding space; no cluster-size weighting.
        """
        results = []
        for k in np.unique(labels):
            m = (labels == k)
            d = np.linalg.norm(X[m] - centers[int(k)], axis=1)
            rmsd = float(np.sqrt(np.mean(d**2)))
            results.append((int(k), rmsd))
        return np.array(results)

    def evaluate_cohesion_slidingwindow(
        self,
        labels=None,
        centers=None,
        reduced_coordinates=None,
        frame_scale=None,
        step_size=None,
    ):
        """
        fixed-size *sliding window* per replicate. at window j, take a slice of
        length `step_size` from each replicate, concat, then compute per-cluster
        rmsd to centers for that slice. advance by `step_size` each step.

        Parameters
        ----------
        labels, centers, reduced_coordinates, frame_scale : optional
            override stored attributes. shapes follow __init__.
        step_size : int, default 10
            window length (in frames) and hop size.

        Returns
        -------
        pandas.DataFrame
            columns: ['cluster', 'rmsd', 'window'] where window is 1-based.

        Notes
        -----
        - replicates shorter than the current window start contribute nothing.
        - windows never cross replicate boundaries.
        - handy for checking “settling”/drift of clusters over time.
        """
        reduced_coordinates = reduced_coordinates if reduced_coordinates is not None else self.reduced_coordinates
        frame_scale = frame_scale if frame_scale is not None else self.frame_scale
        step_size = step_size if step_size is not None else 10
        labels = labels if labels is not None else self.labels
        centers = centers if centers is not None else self.centers

        slidingwindow = 0
        window_df_all = []
        for j in range(1, (np.max(frame_scale) // step_size) + 1):
            print(f"shrink: {j}")

            mask = []
            # build a boolean mask per replicate, then concat them
            for rep_length in frame_scale:
                if slidingwindow > rep_length:
                    mask.append(np.full(rep_length, False))
                    continue
                replicate_bools = np.full(rep_length, False)
                replicate_bools[slidingwindow:slidingwindow + step_size] = True
                mask.append(replicate_bools)

            slidingwindow += step_size  # slide

            window_mask = np.concatenate(mask)
            window_labels = labels[window_mask]
            window_coordinates = reduced_coordinates[window_mask, :]

            rmsd_results = self.rmsd_from_centers(window_coordinates, window_labels, centers)
            windowdf = pd.DataFrame(rmsd_results, columns=('cluster', 'rmsd'))
            windowdf['window'] = j
            window_df_all.append(windowdf)

        return pd.concat(window_df_all)

    def evaluate_cohesion_shrinkingwindow(
        self,
        labels=None,
        centers=None,
        reduced_coordinates=None,
        frame_scale=None,
        step_size=None,
    ):
        """
        *shrinking-from-the-start* window (aka keep the tail). at step j, drop
        the first `creepingstart` frames of each replicate and use the rest.

        Parameters
        ----------
        labels, centers, reduced_coordinates, frame_scale : optional
            override stored attributes. shapes follow __init__.
        step_size : int, default 10
            how much to move the left edge each step.

        Returns
        -------
        pandas.DataFrame
            columns: ['cluster', 'rmsd', 'window'].

        Notes
        -----
        complements the sliding-window view—asks whether cohesion improves as
        you toss early frames.
        """
        reduced_coordinates = reduced_coordinates if reduced_coordinates is not None else self.reduced_coordinates
        frame_scale = frame_scale if frame_scale is not None else self.frame_scale
        step_size = step_size if step_size is not None else 10

        labels = labels if labels is not None else self.labels
        centers = centers if centers is not None else self.centers

        creepingstart = 0
        window_df_all = []
        for j in range(1, (np.max(frame_scale) // step_size) + 1):
            print(f"shrink: {j}")

            mask = []
            for rep_length in frame_scale:
                if creepingstart > rep_length:
                    mask.append(np.full(rep_length, False))
                    continue
                replicate_bools = np.full(rep_length, True)
                replicate_bools[0:creepingstart] = False
                mask.append(replicate_bools)

            window_mask = np.concatenate(mask)
            window_labels = labels[window_mask]
            window_coordinates = reduced_coordinates[window_mask, :]

            rmsd_results = self.rmsd_from_centers(window_coordinates, window_labels, centers)
            windowdf = pd.DataFrame(rmsd_results, columns=('cluster', 'rmsd'))
            windowdf['window'] = j

            creepingstart += step_size
            window_df_all.append(windowdf)

        window_df_all = pd.concat(window_df_all)
        print(window_df_all)
        return window_df_all

    ###########################################################################
    # implied timescales + ck test
    ###########################################################################
    def compute_implied_timescales(self, lags, labels=None, frame_list=None, n_timescales=10):
        """
        implied timescales τ_i(lag) = -lag / ln(|λ_i|) from eigenvalues of T(lag).

        Parameters
        ----------
        lags : list[int]
            lag times (frames) at which to estimate the transition matrix.
        labels, frame_list : optional
            override stored labels/frame_scale.
        n_timescales : int, default 10
            number of slowest timescales to return (skip the trivial λ=1).

        Returns
        -------
        dict[int, np.ndarray]
            map lag -> array (n_timescales,) of slowest implied timescales.

        Notes
        -----
        uses eigenvalues of the row-normalized T; takes real(abs(.)).
        timescales are in frames—multiply by dt for physical time.
        """
        results = {}
        for lag in lags:
            T = self.create_transition_probability_matrix(
                labels=labels, frame_list=frame_list, lag=lag
            )[1:, 1:]  # strip header row/col

            eigvals, _ = np.linalg.eig(T.T)  # rows sum to 1 → use T^T
            eigvals = np.real(eigvals)
            eigvals = np.sort(np.abs(eigvals))[::-1][1:n_timescales + 1]  # drop 1.0

            timescales = -lag / np.log(eigvals)
            results[lag] = timescales
        return results

    def chapman_kolmogorov_test(self, labels=None, frame_list=None, lag=None, steps=4):
        """
        ck check: compare T(lag)^k vs T(k*lag) for k=1..steps.

        Parameters
        ----------
        labels, frame_list : optional
            override stored labels/frame_scale.
        lag : int, default 30
            base lag (frames).
        steps : int, default 4
            number of multiples (k) to compare.

        Returns
        -------
        dict[int, tuple[np.ndarray, np.ndarray]]
            k -> (T_pred, T_direct), both (n_states, n_states).
        """
        labels = labels if labels is not None else self.labels
        lag = lag if lag is not None else 30
        frame_list = frame_list if frame_list is not None else self.frame_scale

        T_tau = self.create_transition_probability_matrix(labels, frame_list, lag=lag)[1:, 1:]

        results = {}
        for k in range(1, steps + 1):
            T_pred = np.linalg.matrix_power(T_tau, k)
            T_direct = self.create_transition_probability_matrix(labels, frame_list, lag=lag * k)[1:, 1:]
            results[k] = (T_pred, T_direct)
        return results

    ###########################################################################
    # transition probability matrix
    ###########################################################################
    def create_transition_probability_matrix(self, labels=None, frame_list=None, lag=None):
        """
        build a row-normalized transition matrix from labels (no cross-replicate jumps).

        Parameters
        ----------
        labels : array-like (n_frames,), optional
            override stored labels. integer states per frame (0-based).
        frame_list : list[int], optional
            override stored frame_scale. frames per replicate, in concat order.
        lag : int, default 1
            transition lag (frames). skip replicates with length <= lag.

        Returns
        -------
        np.ndarray (n_states+1, n_states+1)
            header row/col hold state ids; core block is row-normalized probs.

        Notes
        -----
        - we keep rows with zero outgoing counts as all zeros.
        - prints raw counts pre-normalization (quick sanity check).
        """
        labels = labels if labels is not None else self.labels
        frame_list = frame_list if frame_list is not None else self.frame_scale
        lag = lag if lag is not None else 1

        unique_states = np.unique(labels)
        number_of_states = len(unique_states)
        transtion_prob_matrix = np.zeros((number_of_states, number_of_states))

        iterator = 0
        for trajectory_length in frame_list:
            current_trajectory = labels[iterator:iterator + trajectory_length]
            iterator += trajectory_length

            if lag >= trajectory_length:
                continue

            for i in range(current_trajectory.shape[0] - lag):
                current_state = current_trajectory[i]
                next_state = current_trajectory[i + lag]
                transtion_prob_matrix[current_state, next_state] += 1

        row_sums = transtion_prob_matrix.sum(axis=1, keepdims=True)
        print(f"matrix counts before rownorm:\n{transtion_prob_matrix}")

        transition_probs = np.divide(
            transtion_prob_matrix,
            row_sums,
            out=np.zeros_like(transtion_prob_matrix),  # avoid /0
            where=row_sums > 0,
        )

        final_transition_prob_matrix = np.zeros((number_of_states + 1, number_of_states + 1))
        final_transition_prob_matrix[1:, 1:] = transition_probs
        final_transition_prob_matrix[0, 1:], final_transition_prob_matrix[1:, 0] = unique_states, unique_states

        self.transition_probability_matrix = final_transition_prob_matrix
        return final_transition_prob_matrix

    def extract_stationary_states(self, final_transition_prob_matrix=None):
        """
        stationary distribution π from the transition matrix.

        Parameters
        ----------
        final_transition_prob_matrix : np.ndarray, optional
            if None, rebuild from stored labels/frame lengths at lag=1.

        Returns
        -------
        np.ndarray (n_states,)
            π (nonnegative, sums to 1), aligned with the header state order.
        """
        if final_transition_prob_matrix is None:
            final_transition_prob_matrix = self.create_transition_probability_matrix()

        T = final_transition_prob_matrix[1:, 1:]
        eigvals, eigvecs = np.linalg.eig(T.T)

        print(f"eigenvals:{eigvals},eigvecs:{eigvecs}")

        idx = np.argmin(np.abs(eigvals - 1))
        stationary = np.real(eigvecs[:, idx])
        print(f"idx:{idx},stationary:{stationary}")

        stationary = stationary / stationary.sum()
        print(f"stationary:{stationary}")

        print("Eigenvalues:", eigvals)
        print("Stationary distribution:", stationary)
        return stationary

    def evaluate_Chapman_Kolmogorov(
        self,
        transition_probability_matrix=None,
        n=None,
        labels=None,
        original_lag=None,
    ):
        """
        single-number ck summary via frobenius norm:
        Δ = || T(lag)^n − T(n*lag) ||_F  (smaller is “more markovian”).

        Parameters
        ----------
        transition_probability_matrix : np.ndarray, optional
            if None, builds from stored data with `original_lag`.
        n : int, default 4
            exponent on T(lag) for the predicted evolution.
        labels : array-like, optional
            override stored labels if rebuilding.
        original_lag : int, default 1
            lag used to construct T(lag) when rebuilding.

        Returns
        -------
        float
            frobenius norm of the difference.
        """
        transition_probability_matrix = (
            transition_probability_matrix
            if transition_probability_matrix is not None
            else self.create_transition_probability_matrix()
        )
        original_lag = original_lag if original_lag is not None else 1
        n = n if n is not None else 4
        labels = labels if labels is not None else self.labels  # kept for symmetry

        transition_prob_data = transition_probability_matrix[1:, 1:]
        post_timestep_data = np.linalg.matrix_power(transition_prob_data, n)
        transition_probability_matrix[1:, 1:] = post_timestep_data

        total_lag = original_lag * n
        matrix_from_total_lag = self.create_transition_probability_matrix(lag=total_lag)
        diff = matrix_from_total_lag[1:, 1:] - transition_probability_matrix[1:, 1:]
        frob = np.linalg.norm(diff, ord='fro')
        return frob


    if __name__ == "__main__":
        # quick sketch of a pipeline; adjust paths for your env if you actually run it.
        from mdsa_tools.Analysis import systems_analysis
        import numpy as np
        import matplotlib.cm as cm
        import os
        from mdsa_tools.msm_modeler import MSM_Modeller as msm

        # pipeline setup (as in data generation)
        redone_CCU_GCU_fulltraj = np.load('/Users/luis/Downloads/redone_unrestrained_CCU_GCU_Trajectory_array.npy', allow_pickle=True)
        redone_CCU_CGU_fulltraj = np.load('/Users/luis/Downloads/redone_unrestrained_CCU_CGU_Trajectory_array.npy', allow_pickle=True)

        from mdsa_tools.Viz import visualize_reduction
        persys_frame_list = (([80] * 20) + ([160] * 10))
        persys_frame_short = ([80] * 20)
        persys_frame_long = ([160] * 10)

        # try just gcu
        all_systems = [redone_CCU_GCU_fulltraj]
        Systems_Analyzer = systems_analysis(systems_representations=all_systems, replicate_distribution=persys_frame_list)
        Systems_Analyzer.replicates_to_featurematrix()
        X_pca, _, _ = Systems_Analyzer.reduce_systems_representations()
        cluster_labels, cluster_centers = Systems_Analyzer.cluster_system_level(
            data=X_pca, k=6, outfile_path='../manuscript_explorations/GCU_solo/GCU_pcaspace_clustersolo'
        )

        visualize_reduction(
            X_pca,
            color_mappings=cluster_labels,
            savepath='../manuscript_explorations/GCU_solo/GCU_pcaspace_clustersolo',
            cmap=cm.inferno_r
        )

        # replicate maps to visualize transitions
        from mdsa_tools.Viz import replicatemap_from_labels

        GCU_with_filler = np.concatenate((cluster_labels, np.full(shape=(3200,), fill_value=np.max(cluster_labels) + 1)))
        replicatemap_from_labels(
            GCU_with_filler,
            persys_frame_list * 2,
            savepath='../manuscript_explorations/replicate_maps/6klust_replicate_map',
            title='6klust_replicate_map'
        )

        fourk_modeller = msm(cluster_labels, cluster_centers, X_pca, frame_scale=persys_frame_list)
        GCU_transition_prob_matrix = fourk_modeller.create_transition_probability_matrix()
        stationarystates = fourk_modeller.extract_stationary_states()

        np.savetxt('../manuscript_explorations/GCU_solo/GCUsolo_transition_prob_matrix.csv', GCU_transition_prob_matrix, delimiter=',')
        os._exit(0)

        coordinates = [X_pca[0:3200, :], X_pca[3200:, :]]
