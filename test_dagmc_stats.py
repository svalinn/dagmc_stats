# set the path to find the current installation of pyMOAB
import sys
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range

# import the new module that defines each of the functions
import dagmc_stats
import nose

test_input = "3vols.h5m"

my_core = core.Core()
my_core.load_file(test_input)

root_set = my_core.get_root_set()
entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]

def test_get_tags():
    """
    Tests different aspects of the get_dagmc_tags function
    """
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    assert(len(dagmc_tags) == 3)

    
def test_get_native_ranges():
    """
    Tests different aspects of the get_native_ranges function
    """
    native_ranges = dagmc_stats.get_native_ranges(my_core, root_set, entity_types)
    vertex_range = my_core.get_entities_by_type(root_set, types.MBVERTEX)
    assert(vertex_range == native_ranges[0])
    triangle_range = my_core.get_entities_by_type(root_set, types.MBTRI)
    assert(triangle_range == native_ranges[2])
    entityset_range = my_core.get_entities_by_type(root_set, types.MBENTITYSET)
    assert(entityset_range == native_ranges[11])

    
def test_get_entityset_ranges():
    """
    Tests different aspects of the get_entityset_ranges function
    """
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
    node_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [0])
    assert(node_range == entityset_ranges['Nodes'])
    curve_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [1])
    assert(curve_range == entityset_ranges['Curves'])
    surface_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [2])
    assert(surface_range ==entityset_ranges['Surfaces'])
    volume_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [3])
    assert(volume_range == entityset_ranges['Volumes'])

    
def test_get_triangles_per_vertex():
    "Tests part of the get_triangles_per_vertex function"
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    native_ranges = dagmc_stats.get_native_ranges(my_core, root_set, entity_types)
    t_p_v_data = dagmc_stats.get_triangles_per_vertex(my_core, native_ranges)
    vertices = my_core.get_entities_by_type(root_set, types.MBVERTEX).size()
    assert(len(t_p_v_data) == vertices)
    

def test_get_triangles_per_surface():
    """
    Tests some parts of the get_triangles_per_surface function
    """
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entityset_ranges = dagmc_stats.get_entityset_ranges(
        my_core, root_set, dagmc_tags['geom_dim'])
    t_p_s_data = dagmc_stats.get_triangles_per_surface(
        my_core, entityset_ranges)
    surfaces = my_core.get_entities_by_type_and_tag(
        root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [2]).size()
    assert(len(t_p_s_data) == surfaces)
    triangles = my_core.get_entities_by_type(root_set, types.MBTRI).size()
    assert(sum(t_p_s_data) == triangles)
    

def test_get_triangle_aspect_ratio():
    """
    Tests part of the get_triangle_aspect_ratio function
    """
    t_a_r_data = dagmc_stats.get_triangle_aspect_ratio(my_core, root_set)
    known_triangles = my_core.get_entities_by_type(root_set, types.MBTRI)
    assert(len(t_a_r_data) == known_triangles.size())
    
    

def test_get_surfaces_per_volume():
    """
    Tests different aspects of the get_surfaces_per_volume function
    """
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
    s_p_v_data = dagmc_stats.get_surfaces_per_volume(my_core, entityset_ranges)
    known_volumes = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [3])
    for eh in range(known_volumes.size()):
        surfs = my_core.get_child_meshsets(known_volumes[eh]).size()
        assert(surfs == s_p_v_data[eh])
