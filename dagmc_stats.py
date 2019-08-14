# set the path to find the current installation of pyMOAB
import sys
import numpy as np
sys.path.append(
    '/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab.rng import Range
from pymoab import core, types

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
    dagmc_tags['geom_dim'] = my_core.tag_get_handle('GEOM_DIMENSION', size=1, tag_type=types.MB_TYPE_INTEGER,   
                                                    storage_type=types.MB_TAG_SPARSE, create_if_missing=True)  # geometric dimension

    dagmc_tags['category'] = my_core.tag_get_handle('CATEGORY', size=32, tag_type=types.MB_TYPE_OPAQUE,  
                                                    storage_type=types.MB_TAG_SPARSE, create_if_missing=True)  # the category

    dagmc_tags['global_id'] = my_core.tag_get_handle('GLOBAL_ID', size=1, tag_type=types.MB_TYPE_INTEGER,  
                                                     storage_type=types.MB_TAG_SPARSE, create_if_missing=True)  # id

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
        native_ranges[entity_type] = my_core.get_entities_by_type(
            meshset, entity_type)
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


def get_triangle_aspect_ratio(my_core, meshset, entityset_ranges):
    """
    Gets the triangle aspect ratio (according to the equation: (abc)/(8(s-a)(s-b)(s-c)), where s = .5(a+b+c).)
    
    inputs
    ------
    my_core : a MOAB Core instance
    entityset_ranges : a dictionary with one entry for each entityset type, and the value is the range of entities that corrospond to 
                        each type
    meshset : a meshset containing a certain part of the mesh
    
    outputs
    -------
    t_a_r : (list) the triangle aspect ratios for all triangles in the meshset
    """

    
    t_a_r = []
    tris = core.get_entities_by_type(entity_ranges['Surfaces'][0], types.MBTRI)
    for triangle in tris:
        side_lengths = []
        s = 0
        verts = list(core.get_adjacencies(triangle, 0))
        coord_list = []
        for side in range(3):
            coords = list(core.get_coords(verts[side]))
            coord_list.append(coords)
        coord_array = np.array(coord_list)
        for length in range(3):    
            sum_squares = 0
            for vert in range(3):
                sum_squares += coord_array[vert,length]**2
            side_lengths.append(math.sqrt(sum_squares))
            s += .5*(side_lengths[length])
        top = np.prod(side_lengths)
        bottom = 8*(s-side_lengths[0])*(s-side_lengths[1])*(s-side_lengths[2])
        print(top, bottom, s)
        t_a_r.append(top/bottom)
    print(t_a_r)
            
            
        
        











