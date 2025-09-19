import os
import numpy as np
import pytest

from mdsa_tools.Viz import visualize_reduction, replicatemap_from_labels


def test_visualize_reduction_largebins_saves_file(tmp_path, small_embedding):

    '''
    Tests vizualizing 2-dimensional embeddings as a scatter-plot but, with no
    provided colormappings

    Since this defaults to using each individual value as its own bin this also changes the colorbar
    used to be a continous one vs a discrete one b/c most matplot colormaps cap out at 256
    discrete bins

    '''

    out = tmp_path / "viz_continuous.png"
    visualize_reduction(
        embedding_coordinates=small_embedding,
        color_mappings=None,      # triggers continuous colormap branch
        savepath=str(out),        # function expects a file path here
        title="Test Continuous",
        cmap=None,
        axis_one_label=None,
        axis_two_label=None,
        cbar_label=None,
        gridvisible=False
    )

    assert out.exists(), "visualize_reduction did not create the output file"
    assert out.stat().st_size > 0, "output image is empty"

    return

def test_visualize_reduction__saves_file(tmp_path, small_embedding,less_than_256_bin_colormappings):
    
    '''
    Tests vizualizing 2-dimensional embeddings as a scatter-plot *with* colormappings
    that are less than or equal to 256 unique bins

    Since this creates a discrete color bar instead of a continous one 
    '''

    out = tmp_path / "viz_discrete.png"
    visualize_reduction(
        embedding_coordinates=small_embedding,
        color_mappings=less_than_256_bin_colormappings,      # triggers continuous colormap branch
        savepath=str(out),        # function expects a file path here
        title="Test Discrete",
        cmap=None,
        axis_one_label=None,
        axis_two_label=None,
        cbar_label=None,
        gridvisible=False
    )

    assert out.exists(), "visualize_reduction did not create the output file"
    assert out.stat().st_size > 0, "output image is empty"

    return

def test_replicatemap_from_labels_saves_png(tmp_path, simple_labels_and_frames):
    '''test replicate map creation and if it saves (specificaly with no color mappings)'''
    
    labels, frame_list = simple_labels_and_frames
    save_dir = './tests/test_output/test_repmap'
    replicatemap_from_labels(
        labels=labels,
        frame_list=frame_list,
        savepath=save_dir,
        title="Replicate Map Test",
        xlabel="Frame",
        ylabel="Replicate",
        cmap=None,
    )

    return


