import numpy as np

def test_importer_file_creation(importer):
    rep=importer.create_systems_rep()
    print(rep)
    np.save(f'./tests/test_output/GCU_1_in_10_s',rep)
    return