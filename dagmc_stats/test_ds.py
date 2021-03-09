from pymoab import core, types
from pymoab.rng import Range
import DagmcStats as ds

test_env = [{'input_file': '../tests/3vols.h5m'}, {
    'input_file': '../tests/single-cube.h5m'}, {'input_file': '../tests/pyramid.h5m'}]


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


def test_load_file_populate():
    # another test to test load_file() with populate=True
    pass
