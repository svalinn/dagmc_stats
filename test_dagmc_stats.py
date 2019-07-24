
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
    triangle_range = my_core.get_entities_by_type(root_set, types.MBTRI)
    entityset_range = my_core.get_entities_by_type(root_set, types.MBENTITYSET)
    assert(vertex_range == native_ranges[0], triangle_range == native_ranges[2], entityset_range == native_ranges[11])

    
def test_get_entityset_ranges():
    """
    Tests different aspects of the get_entityset_ranges function
    """
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
    node_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [0])
    curve_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [1])
    surface_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [2])
    volume_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [3])
    assert(node_range == entityset_ranges['Nodes'], curve_range == entityset_ranges['Curves'], surface_range ==
           entityset_ranges['Surfaces'], volume_range == entityset_ranges['Volumes'])
    
def test_get_triangles_per_surface():
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
    t_p_s_data = dagmc_stats.get_triangles_per_surface(my_core, entityset_ranges)
    surfaces = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [2]).size()
    triangles = my_core.get_entities_by_type(root_set, types.MBTRI).size()
    assert(len(t_p_s_data) == surfaces, sum(t_p_s_data) == triangles)
    
    
    
    