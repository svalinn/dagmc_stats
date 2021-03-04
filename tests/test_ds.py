from pymoab import core, types
from pymoab.rng import Range
import dagmc_stats.DagmcStats as ds

test_env = [{'input_file': '3vols.h5m'}, {
    'input_file': 'single-cube.h5m'}, {'input_file': 'pyramid.h5m'}]


def test_load_file():
    """Tests loading file and check the values of all the variables that are set in the constructor
    """

    single_cube = ds.DagmcStats(test_env[1]['input_file'])

    print(single_cube.root_set)
    assert(single_cube.root_set == 0)

    print(single_cube._vert_data)
    print(single_cube._tri_data)
    print(single_cube._surf_data)
    print(single_cube._vol_data)
    pass


def test_load_file_populate():
    # another test to test load_file() with populate=True
    pass


test_load_file()
