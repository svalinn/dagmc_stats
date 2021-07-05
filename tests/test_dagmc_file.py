from pymoab import core, types
from pymoab.rng import Range
import dagmc_stats.DagmcFile as ds
import dagmc_stats.DagmcQuery as dq
import pandas as pd
import numpy as np
import warnings

test_env = [{'input_file': 'tests/3vols.h5m'}, {
    'input_file': 'tests/single-cube.h5m'}, {'input_file': 'tests/pyramid.h5m'}]


def test_load_file():
    """Tests loading file and check the values of all the variables that are
    set in the constructor
    """

    single_cube = ds.DagmcStats(test_env[1]['input_file'])
    assert(single_cube.root_set == 0)

    # tests for pandas data frames
    exp_vert_data = pd.DataFrame(
        columns=['vert_eh', 'roughness', 'tri_per_vert'])
    assert(single_cube._vert_data.equals(exp_vert_data))

    exp_tri_data = pd.DataFrame(
        columns=['tri_eh', 'aspect_ratio', 'area'])
    assert(single_cube._tri_data.equals(exp_tri_data))

    exp_surf_data = pd.DataFrame(
        columns=['surf_eh', 'tri_per_surf', 'coarseness'])
    assert(single_cube._surf_data.equals(exp_surf_data))

    exp_vol_data = pd.DataFrame(
        columns=['vol_eh', 'surf_per_vol', 'coarseness'])
    assert(single_cube._vol_data.equals(exp_vol_data))


def test_load_file_populate():
    # another test to test load_file() with populate=True
    pass


def test_set_native_ranges():
    """Tests set_native_ranges
    """
    single_cube = ds.DagmcStats(test_env[1]['input_file'])
    test_pass = np.full(len(single_cube.entity_types), False)
    for i, native_range_type in enumerate(single_cube.entity_types):
        range = single_cube._my_moab_core.get_entities_by_type(
            single_cube.root_set, native_range_type)
        if native_range_type == types.MBENTITYSET:
            test_pass[i] = (range[:-4] == single_cube.native_ranges[native_range_type])
        else:
            test_pass[i] = (range == single_cube.native_ranges[native_range_type])
    assert(all(test_pass))


def test_set_dagmc_tags():
    """
    Tests different aspects of the set_dagmc_tags function
    """
    single_cube = ds.DagmcStats(test_env[1]['input_file'])
    assert(len(single_cube.dagmc_tags) == 3)
    assert(single_cube.dagmc_tags['category'])
    assert(single_cube.dagmc_tags['geom_dim'])
    assert(single_cube.dagmc_tags['global_id'])


def test_set_entityset_ranges():
    """
    Tests different aspects of the set_entityset_ranges function
    """
    single_cube = ds.DagmcStats(test_env[1]['input_file'])
    test_pass = np.full(len(single_cube.entityset_types), False)
    for dimension, set_type in single_cube.entityset_types.items():
        type_range = single_cube._my_moab_core.get_entities_by_type_and_tag(
            single_cube.root_set, types.MBENTITYSET, single_cube.dagmc_tags['geom_dim'], [dimension])
        test_pass[dimension] = (
            type_range == single_cube.entityset_ranges[set_type])
    assert(all(test_pass))

def test_set_dimension_meshset():
    """
    Tests different aspects of the set_dimension_meshset function
    """
    single_cube = ds.DagmcStats(test_env[1]['input_file'])
    range = single_cube._my_moab_core.get_entities_by_type(
                            single_cube.root_set, types.MBENTITYSET)
    assert(set(single_cube.dim_dict.values())==set(range[-4:]))

def test_get_meshset_by_id():
    """
    Tests the get_meshset_by_id function given valid dim and id
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    test_pass = np.full(3, False)
    # get volume 0
    exp = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [3])[0]
    obs = three_vols.get_meshset_by_id('volumes', ids=[1])
    if obs == exp:
        test_pass[0] = True

    obs_singular = three_vols.get_meshset_by_id('volume', ids=[1])
    obs_upper = three_vols.get_meshset_by_id('Volumes', ids=[1])
    obs_integer = three_vols.get_meshset_by_id(3 , ids=[1])
    if obs == obs_singular == obs_upper == obs_integer:
        test_pass[1] = True

    # get volumes 0, 1
    exp = list(three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [3])[0:2])
    obs = three_vols.get_meshset_by_id('volumes', ids=[1,2])
    if obs == exp:
        test_pass[2] = True
    assert(all(test_pass))

def test_get_meshset_by_id_empty_id():
    """
    Tests the get_meshset_by_id function given no id
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    exp = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [3])
    # When no id is passed in, get_meshset_by_id() function should return the meshset of the given dimension.
    obs = three_vols.get_meshset_by_id('volumes', ids=[])
    assert(obs == exp)

def test_get_meshset_by_id_out_of_range_dim():
    """
    Tests the get_meshset_by_id function given id not in the dim
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    test_pass = np.full(3, False)
    exp = []
    with warnings.catch_warnings(record=True) as w:
        obs = three_vols.get_meshset_by_id('volumes', ids=[4])
        warnings.simplefilter('always')
        if obs == exp:
            test_pass[0] = True
        if len(w) == 1:
            test_pass[1] = True
            if 'ID is not in the given dimension range! Empty list will be returned.' in str(w[-1].message):
                test_pass[2] = True
    assert(all(test_pass))

def test_get_meshset_by_id_invalid_dim():
    """
    Tests the get_meshset_by_id function given invalid dim
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    test_pass = np.full(3, False)
    exp = three_vols.root_set
    with warnings.catch_warnings(record=True) as w:
        obs = three_vols.get_meshset_by_id('vertices', ids=[])
        warnings.simplefilter('always')
        if obs == exp:
            test_pass[0] = True
        if len(w) == 1:
            test_pass[1] = True
            if 'Invalid dim!' in str(w[-1].message):
                test_pass[2] = True
    assert(all(test_pass))

'''
def test_populate_triangle_data():
    """
    Tests different aspects of the populate_triangle_data function
    """
    single_cube = ds.DagmcStats(test_env[1]['input_file'], populate=True)
    exp_tri_data = pd.DataFrame(
        columns=['tri_eh', 'aspect_ratio', 'area'])
    tris = single_cube._my_moab_core.get_entities_by_type(single_cube.root_set, types.MBTRI)
    for tri in tris:
        tri_data_row = {'tri_eh': tri}
        tri_data_row['area'] = 50
        tri_data_row['aspect_ratio'] = (10*10*10*np.sqrt(2))/(8*5*np.sqrt(2)*5*np.sqrt(2)*(10-5*np.sqrt(2)))
        exp_tri_data = exp_tri_data.append(tri_data_row, ignore_index=True)
    pd.testing.assert_frame_equal(single_cube._tri_data,exp_tri_data)
'''
