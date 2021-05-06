from pymoab import core, types
from pymoab.rng import Range
import dagmc_stats.DagmcStats as ds
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


def test_get_tris_vol():
    """
    Tests the get_tris function for volume meshset
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    vols = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [3])
    obs_tris = three_vols.get_tris(meshset=vols[0])
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        vols[0], types.MBTRI)
    assert(list(obs_tris).sort() == list(exp_tris).sort())


def test_get_tris_surf():
    """
    Tests the get_tris function for surface meshset
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    surfs = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [2])
    obs_tris = three_vols.get_tris(meshset=surfs[0])
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        surfs[0], types.MBTRI)
    assert(list(obs_tris).sort() == list(exp_tris).sort())


def test_get_tris_rootset():
    """
    Tests the get_tris function given the rootset
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    obs_tris = three_vols.get_tris(meshset=three_vols.root_set)
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        three_vols.root_set, types.MBTRI)
    assert(list(obs_tris).sort() == list(exp_tris).sort())


def test_get_tris_dimension_incorrect():
    """
    Tests the get_tris function given incorrect dimension
    """
    test_pass = np.full(2, False)
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    # check if get_tris function generates warning for meshset with invalid dimension
    verts = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [0])
    with warnings.catch_warnings(record=True) as w:
        three_vols.get_tris(meshset=verts[0])
        warnings.simplefilter('always')
        if len(w) == 1:
            test_pass[0] = True
        if 'Meshset is not a volume nor a surface! Rootset will be used by default.' in str(w[-1].message):
            test_pass[1] = True
    assert(all(test_pass))


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
    
