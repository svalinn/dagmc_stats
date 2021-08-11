from pymoab import core, types
from pymoab.rng import Range
import dagmc_stats.DagmcFile as df
import dagmc_stats.DagmcQuery as dq
import pandas as pd
import numpy as np
import warnings

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


def test_get_tris_vol():
    """Tests the get_tris function for volume meshset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    vols = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [3])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=vols[0])
    obs_tris = three_vols_query.get_tris()
    exp_tris = []
    meshset_lst = []
    surfs = three_vols._my_moab_core.get_child_meshsets(vols[0])
    meshset_lst.extend(surfs)
    for item in meshset_lst:
        exp_tris.extend(
            three_vols._my_moab_core.get_entities_by_type(item, types.MBTRI))
    assert(sorted(obs_tris) == sorted(exp_tris))


def test_get_tris_surf():
    """Tests the get_tris function for surface meshset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    surfs = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [2])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=surfs[0])
    obs_tris = three_vols_query.get_tris()
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        surfs[0], types.MBTRI)
    assert(sorted(obs_tris) == sorted(exp_tris))


def test_get_tris_rootset():
    """Tests the get_tris function given the rootset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=three_vols.root_set)
    obs_tris = three_vols_query.get_tris()
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        three_vols.root_set, types.MBTRI)
    assert(sorted(obs_tris) == sorted(exp_tris))


def test_get_tris_dimension_incorrect():
    """Tests the get_tris function given incorrect dimension
    """
    test_pass = np.full(2, False)
    three_vols = df.DagmcFile(test_env['three_vols'])
    # check if get_tris function generates warning for meshset with invalid dimension
    verts = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [0])
    with warnings.catch_warnings(record=True) as w:
        three_vols_query = dq.DagmcQuery(three_vols, meshset=verts[0])
        obs_tris = three_vols_query.get_tris()
        warnings.simplefilter('always')
        if len(w) == 1:
            test_pass[0] = True
            if 'Meshset is not a volume nor a surface! Rootset will be used by default.' in str(w[-1].message):
                test_pass[1] = True
    assert(all(test_pass))


def test_calc_tris_per_vert_vol():
    """Tests part of the calc_triangles_per_vertex function"""
    three_vols = df.DagmcFile(test_env['three_vols'])
    vols = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [3])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=vols[0])
    three_vols_query.calc_tris_per_vert()
    assert(sorted(three_vols_query._vert_data['tri_per_vert']) == [
           4, 4, 4, 4, 5, 5, 5, 5])


def test_calc_tris_per_vert_surf():
    """Tests the calc_tris_per_vert function for surface meshset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    surfs = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [2])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=surfs[0])
    three_vols_query.calc_tris_per_vert()
    assert(sorted(three_vols_query._vert_data['tri_per_vert']) == [4, 4, 5, 5])


def test_calc_tris_per_vert_rootset():
    """Tests the calc_tris_per_vertfunction given the rootset
    """
    three_vols = df.DagmcFile(test_env['three_vols'])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=three_vols.root_set)
    three_vols_query.calc_tris_per_vert()
    exp_tpv_len = len(three_vols._my_moab_core.get_entities_by_type(
        three_vols.root_set, types.MBVERTEX))
    assert(len(three_vols_query._vert_data['tri_per_vert']) == exp_tpv_len)


def test_calc_tris_per_vert_dimension_incorrect():
    """Tests the calc_tris_per_vert function given incorrect dimension
    """
    test_pass = np.full(2, False)
    three_vols = df.DagmcFile(test_env['three_vols'])
    # check if get_tris function generates warning for meshset with invalid dimension
    verts = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [0])
    with warnings.catch_warnings(record=True) as w:
        three_vols_query = dq.DagmcQuery(three_vols, meshset=verts[0])
        three_vols_query.calc_tris_per_vert()
        warnings.simplefilter('always')
        if len(w) == 1:
            test_pass[0] = True
            if 'Meshset is not a volume nor a surface! Rootset will be used by default.' in str(w[-1].message):
                test_pass[1] = True
    assert(all(test_pass))
