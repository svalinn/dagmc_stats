from pymoab import core, types
from pymoab.rng import Range
import dagmc_stats.DagmcStats as ds
import pandas as pd

test_env = [{'input_file': 'tests/3vols.h5m'}, {
    'input_file': 'tests/single-cube.h5m'}, {'input_file': 'tests/pyramid.h5m'}]


def test_load_file():
    """Tests loading file and check the values of all the variables that are set in the constructor
    """

    single_cube = ds.DagmcStats(test_env[1]['input_file'])
    assert(single_cube.root_set == 0)
    
    # tests for pandas data frames
    exp_vert_data = pd.DataFrame(
            columns=['vert_eh', 'roughness', 'tri_per_vert'])
    exp_vert_data = exp_vert_data.set_index('vert_eh')
    assert(single_cube._vert_data.equals(exp_vert_data))
    
    exp_tri_data = pd.DataFrame(
            columns=['tri_eh', 'aspect_ratio', 'area'])
    exp_tri_data = exp_tri_data.set_index('tri_eh')
    assert(single_cube._tri_data.equals(exp_tri_data))
    
    exp_surf_data = pd.DataFrame(
            columns=['surf_eh', 'tri_per_surf', 'coarseness'])
    exp_surf_data = exp_surf_data.set_index('surf_eh')
    assert(single_cube._surf_data.equals(exp_surf_data))
    
    exp_vol_data = pd.DataFrame(
            columns=['vol_eh', 'surf_per_vol', 'coarseness'])
    exp_vol_data = exp_vol_data.set_index('vol_eh')
    assert(single_cube._vol_data.equals(exp_vol_data))


def test_load_file_populate():
    # another test to test load_file() with populate=True
    pass
