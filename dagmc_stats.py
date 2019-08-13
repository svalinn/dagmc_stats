# set the path to find the current installation of pyMOAB
import sys
import numpy as np
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range


def get_dagmc_tags(my_core):
    """
    Get a dictionary with the important tags for DAGMC geometries
    
    inputs
    ------
    my_core : a MOAB Core instance
    outputs
    -------
    dagmc_tags : a dictionary of relevant tags
    """

    dagmc_tags = {}
    dagmc_tags['geom_dim'] = my_core.tag_get_handle('GEOM_DIMENSION', size = 1, tag_type = types.MB_TYPE_INTEGER, 
                                                 storage_type = types.MB_TAG_SPARSE, create_if_missing = True)#geometric dimension
    
    dagmc_tags['category'] = my_core.tag_get_handle('CATEGORY', size = 32, tag_type = types.MB_TYPE_OPAQUE, 
                                                 storage_type = types.MB_TAG_SPARSE, create_if_missing = True) #category
    
    dagmc_tags['global_id'] = my_core.tag_get_handle('GLOBAL_ID', size = 1, tag_type = types.MB_TYPE_INTEGER, 
                                                  storage_type = types.MB_TAG_SPARSE, create_if_missing = True) #id

    return dagmc_tags


def get_native_ranges(my_core, meshset, entity_types):
    """
    Get a dictionary with MOAB ranges for each of the requested entity types
    
    inputs
    ------
    my_core : a MOAB Core instance
    meshset : a MOAB meshset to query for the ranges of entities
    entity_types : a list of valid pyMOAB types to be retrieved
    
    outputs
    -------
    native_ranges : a dictionary with one entry for each entity type that is a Range of handles to that type
    """

    native_ranges = {}
    for entity_type in entity_types:
        native_ranges[entity_type] = my_core.get_entities_by_type(meshset, entity_type) 
    return native_ranges

def get_entityset_ranges(my_core, meshset, geom_dim):
    """
    Get a dictionary with MOAB Ranges that are specific to the types.MBENTITYSET type
    
    inputs
    ------
    my_core : a MOAB Core instance
    meshset : the root meshset for the file
    geom_dim : the tag that specifically denotes the dimesion of the entity
    
    outputs
    -------
    entityset_ranges : a dictionary with one entry for each entityset type, and the value is the range of entities that corrospond to 
                        each type

    """
    entityset_ranges = {}
    entityset_types = ['Nodes', 'Curves', 'Surfaces', 'Volumes']
    for dimension, set_type in enumerate(entityset_types):
        entityset_ranges[set_type] = my_core.get_entities_by_type_and_tag(meshset, types.MBENTITYSET, geom_dim, 
                                                                          [dimension])
    return entityset_ranges

def get_triangles_per_vertex(my_core, native_ranges):
    """
    This function will return data about the number of triangles on each surface in a file
    
    inputs
    ------
    my_core : a MOAB Core instance
    native_ranges : a dictionary containing ranges for each native type in the file (VERTEX, TRIANGLE, ENTITYSET)
    
    outputs
    -------
    t_p_v : a list of the number of triangles each vertex touches
    """
    
    t_p_v_data = np.array([])
    tri_dim = 2
    vertex_dim = 0
    for vertex in native_ranges[vertex_dim]:
        t_p_v = np.append(t_p_v, my_core.get_adjacencies(vertex, tri_dim).size())
    return t_p_v