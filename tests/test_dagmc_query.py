from pymoab import core, types
from pymoab.rng import Range
import dagmc_stats.DagmcFile as df
import dagmc_stats.DagmcQuery as dq
import pandas as pd
import numpy as np
import warnings
import pytest

test_env = {'three_vols': 'tests/3vols.h5m',
            'single_cube': 'tests/single-cube.h5m', 'pyramid': 'tests/pyramid.h5m'}


def test_pandas_data_frame():
    """Tests the initialization of pandas data frames
    """
    single_cube = df.DagmcFile(test_env['single_cube'])
    single_cube_query = dq.DagmcQuery(single_cube)
    exp_vert_data = pd.DataFrame()
    assert(single_cube_query._vert_data.equals(exp_vert_data))

    exp_tri_data = pd.DataFrame()
    assert(single_cube_query._tri_data.equals(exp_tri_data))

    exp_surf_data = pd.DataFrame()
    assert(single_cube_query._surf_data.equals(exp_surf_data))

    exp_vol_data = pd.DataFrame()
    assert(single_cube_query._vol_data.equals(exp_vol_data))


def test_get_entities_rootset():
    """Tests the get_entities function for rootset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    three_vols_query = dq.DagmcQuery(three_vols)
    exp = [three_vols.root_set]
    assert(three_vols_query.meshset_lst == exp)


def test_get_entities_vol():
    """Tests the get_entities function for volume meshset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    vol = three_vols.entityset_ranges['volumes'][0]
    three_vols_query = dq.DagmcQuery(three_vols, vol)
    exp = list(three_vols._my_moab_core.get_child_meshsets(vol))
    assert(three_vols_query.meshset_lst == exp)


def test_get_entities_surf():
    """Tests the get_entities function for surface meshset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    surf = three_vols.entityset_ranges['surfaces'][0]
    three_vols_query = dq.DagmcQuery(three_vols, surf)
    exp = [surf]
    assert(three_vols_query.meshset_lst == exp)


def test_get_entities_incorrect_dim():
    """Tests the get_entities function given incorrect dimension
    """
    test_pass = np.full(3, False)
    three_vols = df.DagmcFile(test_env['three_vols'])
    # check if get_tris function generates warning for meshset with invalid dimension
    vert = three_vols.entityset_ranges['nodes'][0]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        three_vols_query = dq.DagmcQuery(three_vols, vert)
        if len(w) == 1:
            test_pass[0] = True
            if 'Meshset is not a volume nor a surface! Rootset will be used by default.' in str(w[-1].message):
                test_pass[1] = True
        exp = [three_vols.root_set]
        test_pass[2] = (three_vols_query.meshset_lst == exp)
    assert(all(test_pass))


def test_get_tris_vol():
    """Tests the get_tris function for volume meshset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    vol = three_vols.entityset_ranges['volumes'][0]
    three_vols_query = dq.DagmcQuery(three_vols, vol)
    obs_tris = three_vols_query.get_tris()
    exp_tris = []
    meshset_lst = []
    surfs = three_vols._my_moab_core.get_child_meshsets(vol)
    meshset_lst.extend(surfs)
    for item in meshset_lst:
        exp_tris.extend(
            three_vols._my_moab_core.get_entities_by_type(item, types.MBTRI))
    assert(sorted(obs_tris) == sorted(exp_tris))


def test_get_tris_surf():
    """Tests the get_tris function for surface meshset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    surf = three_vols.entityset_ranges['surfaces'][0]
    three_vols_query = dq.DagmcQuery(three_vols, surf)
    obs_tris = three_vols_query.get_tris()
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        surf, types.MBTRI)
    assert(sorted(obs_tris) == sorted(exp_tris))


def test_get_tris_rootset():
    """Tests the get_tris function given the rootset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    three_vols_query = dq.DagmcQuery(three_vols, three_vols.root_set)
    obs_tris = three_vols_query.get_tris()
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        three_vols.root_set, types.MBTRI)
    assert(sorted(obs_tris) == sorted(exp_tris))


def test_get_tris_dimension_incorrect():
    """Tests the get_tris function given incorrect dimension
    """
    test_pass = np.full(3, False)
    three_vols = df.DagmcFile(test_env['three_vols'])
    # check if get_tris function generates warning for meshset with invalid dimension
    vert = three_vols.entityset_ranges['nodes'][0]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        three_vols_query = dq.DagmcQuery(three_vols, vert)
        obs_tris = three_vols_query.get_tris()
        if len(w) == 1:
            test_pass[0] = True
            if 'Meshset is not a volume nor a surface! Rootset will be used by default.' in str(w[-1].message):
                test_pass[1] = True
        exp_tris = three_vols._my_moab_core.get_entities_by_type(
            three_vols.root_set, types.MBTRI)
        test_pass[2] = (sorted(obs_tris) == sorted(exp_tris))
    assert(all(test_pass))


def test_calc_tris_per_vert_vol():
    """Tests part of the calc_tris_per_vert function"""
    three_vols = df.DagmcFile(test_env['three_vols'])
    vol = three_vols.entityset_ranges['volumes'][0]
    three_vols_query = dq.DagmcQuery(three_vols, vol)
    three_vols_query.calc_tris_per_vert()
    assert(sorted(three_vols_query._vert_data['tri_per_vert']) == [
           4, 4, 4, 4, 5, 5, 5, 5])


def test_calc_tris_per_vert_surf():
    """Tests the calc_tris_per_vert function for surface meshset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    surf = three_vols.entityset_ranges['surfaces'][0]
    three_vols_query = dq.DagmcQuery(three_vols, surf)
    three_vols_query.calc_tris_per_vert()
    assert(sorted(three_vols_query._vert_data['tri_per_vert']) == [4, 4, 5, 5])


def test_calc_area_triangle_vol():
    """Tests part of the calc_area_triangle function
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    vol = three_vols.entityset_ranges['volumes'][0]
    three_vols_query = dq.DagmcQuery(three_vols, vol)
    three_vols_query.calc_area_triangle()
    np.testing.assert_almost_equal(
        list(three_vols_query._tri_data['area']), list(np.full(12, 50)))


def test_calc_triangle_aspect_ratio_vol():
    """Tests part of the calc_triangle_aspect_ratio function
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    vol = three_vols.entityset_ranges['volumes'][0]
    three_vols_query = dq.DagmcQuery(three_vols, vol)
    three_vols_query.calc_triangle_aspect_ratio()
    exp = (10*10*10*np.sqrt(2))/(8*5*np.sqrt(2)*5*np.sqrt(2)*(10-5*np.sqrt(2)))
    np.testing.assert_almost_equal(
        list(three_vols_query._tri_data['aspect_ratio']), list(np.full(12, exp)))


def test_update_tri_data():
    """Tests the upadte_tri_data function
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    surf = three_vols.entityset_ranges['surfaces'][0]
    three_vols_query = dq.DagmcQuery(three_vols, surf)
    three_vols_query.calc_triangle_aspect_ratio()
    exp_tar = (10*10*10*np.sqrt(2))/(8*5*np.sqrt(2)
                                     * 5*np.sqrt(2)*(10-5*np.sqrt(2)))
    np.testing.assert_almost_equal(
        list(three_vols_query._tri_data['aspect_ratio']), list(np.full(2, exp_tar)))
    three_vols_query.calc_area_triangle()
    np.testing.assert_almost_equal(
        list(three_vols_query._tri_data['area']), list(np.full(2, 50)))

@pytest.mark.parametrize("function,message", [('calc_tris_per_vert()','Tri_per_vert already exists. tris_per_vert() will not be called.')])
def test_duplicate_tpv(function, message):
    """Tests the case where calc_tris_per_vert() is called on the same meshset for multiple times
    """
    test_pass = np.full(3, False)
    three_vols = df.DagmcFile(test_env['three_vols'])
    surf = three_vols.entityset_ranges['surfaces'][0]
    three_vols_query = dq.DagmcQuery(three_vols, surf)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        eval('three_vols_query.' + function)
        eval('three_vols_query.' + function)
        if len(w) == 1:
            test_pass[0] = True
            if message in str(w[-1].message):
                test_pass[1] = True
    test_pass[2] = (
        sorted(three_vols_query._vert_data['tri_per_vert']) == [4, 4, 5, 5])
    assert(all(test_pass))

def test_coarseness():
    """Tests the calc coarseness function
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    vol = three_vols.entityset_ranges['volumes'][0]
    three_vols_query = dq.DagmcQuery(three_vols, vol)
    three_vols_query.calc_coarseness()
    np.testing.assert_almost_equal(
        list(three_vols_query._surf_data['coarseness']), list(np.full(6, 0.02)))

def test_coarseness_area_called():
    """Tests the case that the calc_triangle_function was called before the
    calc_coarseness function
    """
    test_pass = np.full(3, False)
    three_vols = df.DagmcFile(test_env['three_vols'])
    surf = three_vols.entityset_ranges['surfaces'][0]
    three_vols_query = dq.DagmcQuery(three_vols, surf)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        three_vols_query.calc_area_triangle()
        three_vols_query.calc_coarseness()
        if len(w) == 1:
            test_pass[0] = True
            if 'Triangle area already exists. Calc_area_triangle() will not be called.' in str(w[-1].message):
                test_pass[1] = True
    test_pass[2] = (list(three_vols_query._surf_data['coarseness'] == [0.02]))
    assert(all(test_pass))

def test_roughness():
    single_cube = df.DagmcFile(test_env['single_cube'])
    single_cube_query = dq.DagmcQuery(single_cube)
    single_cube_query.calc_roughness()
    #print(single_cube_query._vert_data)
    #three_vols = df.DagmcFile(test_env['three_vols'])
    #surf = three_vols.entityset_ranges['surfaces'][0]
    #three_vols_query = dq.DagmcQuery(three_vols, surf)
    #print(three_vols_query.get_roughness())
