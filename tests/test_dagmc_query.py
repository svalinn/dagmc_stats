from pymoab import core, types
from pymoab.rng import Range
import dagmc_stats.DagmcFile as ds
import dagmc_stats.DagmcQuery as dq
import pandas as pd
import numpy as np
import warnings

test_env = [{'input_file': 'tests/3vols.h5m'}, {
    'input_file': 'tests/single-cube.h5m'}, {'input_file': 'tests/pyramid.h5m'}]

def test_pandas_data_frame():
    """Tests the initialization of pandas data frames
    """
    single_cube = ds.DagmcStats(test_env[1]['input_file'])
    single_cube_query = dq.DagmcQuery(single_cube)
    exp_vert_data = pd.DataFrame(
        columns=['vert_eh', 'roughness', 'tri_per_vert'])
    assert(single_cube_query._vert_data.equals(exp_vert_data))

    exp_tri_data = pd.DataFrame(
        columns=['tri_eh', 'aspect_ratio', 'area'])
    assert(single_cube_query._tri_data.equals(exp_tri_data))

    exp_surf_data = pd.DataFrame(
        columns=['surf_eh', 'tri_per_surf', 'coarseness'])
    assert(single_cube_query._surf_data.equals(exp_surf_data))

    exp_vol_data = pd.DataFrame(
        columns=['vol_eh', 'surf_per_vol', 'coarseness'])
    assert(single_cube_query._vol_data.equals(exp_vol_data))

def test_get_tris_vol():
    """Tests the get_tris function for volume meshset
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    vols = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [3])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=vols[0])
    obs_tris = three_vols_query.get_tris()
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        vols[0], types.MBTRI)
    assert(list(obs_tris).sort() == list(exp_tris).sort())


def test_get_tris_surf():
    """Tests the get_tris function for surface meshset
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    surfs = three_vols._my_moab_core.get_entities_by_type_and_tag(
        three_vols.root_set, types.MBENTITYSET, three_vols.dagmc_tags['geom_dim'], [2])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=surfs[0])
    obs_tris = three_vols_query.get_tris()
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        surfs[0], types.MBTRI)
    assert(list(obs_tris).sort() == list(exp_tris).sort())


def test_get_tris_rootset():
    """Tests the get_tris function given the rootset
    """
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    three_vols_query = dq.DagmcQuery(three_vols, meshset=three_vols.root_set)
    obs_tris = three_vols_query.get_tris()
    exp_tris = three_vols._my_moab_core.get_entities_by_type(
        three_vols.root_set, types.MBTRI)
    assert(list(obs_tris).sort() == list(exp_tris).sort())


def test_get_tris_dimension_incorrect():
    """Tests the get_tris function given incorrect dimension
    """
    test_pass = np.full(2, False)
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
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

def test_calc_tris_per_vert():
    """Tests part of the get_triangles_per_vertex function"""
    three_vols = ds.DagmcStats(test_env[0]['input_file'])
    three_vols_query = dq.DagmcQuery(three_vols)

    three_vols_query.calc_tris_per_vert()
    vertices = three_vols._my_moab_core.get_entities_by_type(three_vols.root_set, types.MBVERTEX).size()
    assert(len(three_vols_query._vert_data['t_p_v']) == vertices)
