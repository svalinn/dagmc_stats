# set the path to find the current installation of pyMOAB
import sys
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
import numpy as np
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
    dagmc_tags['geom_dim'] = my_core.tag_get_handle('GEOM_DIMENSION', size = 1, tag_type = types.MB_TYPE_INTEGER, #creates tag for the geo-
                                                 storage_type = types.MB_TAG_SPARSE, create_if_missing = True)# geometric dimension
    
    dagmc_tags['category'] = my_core.tag_get_handle('CATEGORY', size = 32, tag_type = types.MB_TYPE_OPAQUE, #creates tag for the word of 
                                                 storage_type = types.MB_TAG_SPARSE, create_if_missing = True) #the category
    
    dagmc_tags['global_id'] = my_core.tag_get_handle('GLOBAL_ID', size = 1, tag_type = types.MB_TYPE_INTEGER, #creates tag for each entity
                                                  storage_type = types.MB_TAG_SPARSE, create_if_missing = True) #id

    return dagmc_tags


def get_entity_ranges(my_core, meshset, entity_types, dagmc_tags):
    """
    Get a dictionary with MOAB ranges for each of the requested entity types
    
    inputs
    ------
    my_core : a MOAB Core instance
    meshset : a MOAB meshset to query for the ranges of entities
    entity_types : a list of valid pyMOAB types to be retrieved
    dagmc_tags : a dictionary of relevant tags. 
    outputs
    -------
    entity_ranges : a dictionary with one entry for each entity type that is a Range of handles to that type
    """

    entity_ranges = {}
    for entity_type in entity_types:
        entity_ranges[entity_type] = my_core.get_entities_by_type(meshset, entity_type) 
        if entity_type == 11:
            entity_ranges['Volumes'] = my_core.get_entities_by_type_and_tag(meshset, types.MBENTITYSET, dagmc_tags['geom_dim'], [3])
            entity_ranges['Surfaces'] = my_core.get_entities_by_type_and_tag(meshset, types.MBENTITYSET, dagmc_tags['geom_dim'], [2])
            entity_ranges['Curves'] = my_core.get_entities_by_type_and_tag(meshset, types.MBENTITYSET, dagmc_tags['geom_dim'], [1])
    return entity_ranges

def get_surfaces_per_volume(my_core, entity_ranges):
    """
    Get the number of surfaces that each volume in a given file contains
    
    inputs
    ------
    my_core : a MOAB core instance
    entity_ranges : a dictionary of the ranges of each tag in a file
    
    outputs
    -------
    pdf : a histogram that displays the number of surfaces of each volume (matplotlib)
    """
    
    freqs = []
    for volumeset in entity_ranges['Volumes']:
        freqs.append(my_core.get_child_meshsets(volumeset).size())
    stats = {}
    stats['minimum'] = min(freqs)
    stats['maximum'] = max(freqs)
    stats['median'] = np.median(freqs)
    stats['average'] = np.average(freqs)
    return stats


def make_verts_dictionary(vert_list):
    """
    returns a dictionary of frequency of the values of the triangles per vertex (ie {number of triangles per vertex: occurences})
    
    inputs
    -----
    vert_list : a list of all vertices in a file
    
    outputs:
    --------
    sorted_dict: a dictionary that has information about triangles per vertex, sorted by its keys.
    """
    
    vertices_and_frequencies = {} 
    #makes dictionary with each vertex and the number of triangles on it
    for vert in vert_list:
        try:
            vertices_and_frequencies[vert] += 1
        except KeyError:
            vertices_and_frequencies[vert] = 1
    number_of_frequencies = {}
    #makes dictionary with the number of triangles, and the number of vertices that have that number
    for vertex in vertices_and_frequencies:
        try:
            number_of_frequencies[vertices_and_frequencies[vertex]] += 1
        except KeyError:
            number_of_frequencies[vertices_and_frequencies[vertex]] = 1
    sorted_dict = {}
    #sorts the dictionary
    for frequency in sorted(number_of_frequencies.keys()):
        sorted_dict[frequency] = number_of_frequencies[frequency]
    return(sorted_dict)


def find_median(sorted_dict):
    """
    finds the median of a dictionary with format {value:occurences}
    
    inputs
    ------
    sorted_dict : a dictionary sorted by its keys
    example dictionary:
    {3:2, 4:5, 6:3} = [3,3,4,4,4,4,4,6,6,6]
    
    
    outputs
    -------
    mean : the median of the dataset 
    
    """
    
    #finds the number of data points
    length = sum(sorted_dict.values())
    half = length / 2
    sum_var = 0
    #finds the index of the middle of the dataset
    for val in sorted_dict.values():
        if half-sum_var > 0:
            sum_var += val
        else:
            break
    index = (list(sorted_dict.values()).index(val))
    #returns the median based off some characteristics of the dataset
    if sum(list(sorted_dict.values())[index:]) != sum(list(sorted_dict.values())[:index]):
        if sum(list(sorted_dict.values())[index:]) > sum(list(sorted_dict.values())[:index]):
            return list(sorted_dict.keys())[index]
        else:
            return list(sorted_dict.keys())[index-1]
    else:
        return (list(sorted_dict.keys())[index-1] + list(sorted_dict.keys())[index]) / 2


def find_mean(sorted_dict):
    """
    finds the mean of a dictionary with format {value:occurences}
    
    inputs
    ------
    sorted_dict : a dictionary sorted by its keys
    
    example dictionary:
    {3:2, 4:5, 6:3} = [3,3,4,4,4,4,4,6,6,6]
    
    outputs
    -------
    mean : the mean of the dataset
    
    """
    
    total = 0
    for key, value in sorted_dict.items():
        total += key*value
    mean = total / sum(sorted_dict.values())
    return mean


def get_triangles_per_vertex(my_core, all_meshset):
    """
    gets stats for the number of trianges touching each vertex in a file
    
    inputs
    ------
    my_core : a MOAB core instance
    all_meshset : a meshset containing all mesh entities in a file
    
    outputs
    -------
    triangles_per_vertex_stats : a dictionary with certain statistics
    """
    
    tri_meshset = my_core.create_meshset() #creates a meshset
    tri_range = my_core.get_entities_by_type(all_meshset, types.MBTRI) #retrieves all entities with type triangle
    my_core.add_entities(tri_meshset, tri_range) #adds the entities into the new meshset
    all_verts = [] 
    freq_list = []
    for tri in range(tri_range.size()): #range should be the length of the tri_range, working on scalability, so may not be
        connect = my_core.get_adjacencies(tri_range[tri], 0) #stores the vertices of each triangle
        for vert in range(3):
            all_verts.append(connect[vert]) #adds each individual vertex into a list
    sorted_dict = make_verts_dictionary(all_verts)
    #makes a dictionary of all statistics
    triangles_per_vertex_stats = {}
    triangles_per_vertex_stats['minimum'] = min(sorted_dict.keys())
    triangles_per_vertex_stats['maximum'] = max(sorted_dict.keys())
    median = find_median(sorted_dict)
    triangles_per_vertex_stats['median'] = median
    mean = find_mean(sorted_dict)
    triangles_per_vertex_stats['average'] = mean
    return triangles_per_vertex_stats


def get_triangles_per_surface(my_core, entity_ranges):
    """
    This function will return statistics about the number of triangles on each surface in a file
    
    inputs
    ------
    my_core : a MOAB Core instance
    entity_ranges : a dictionary containing ranges for each type in the file (VOLUME, SURFACE, CURVE, VERTEX, TRIANGLE, ENTITYSET)
    
    outputs
    -------
    triangles_per_surface_stats : a dictionary of certain stats about triangles per surface
    """
    
    tri_dict = {}
    for surface in entity_ranges['Surfaces']:
        triangles = my_core.get_entities_by_type(surface, types.MBTRI)
        try:
            tri_dict[triangles.size()] += 1
        except KeyError:
            tri_dict[triangles.size()] = 1
    sorted_dictionary = {}
    for number in sorted(tri_dict.keys()):
        sorted_dictionary[number] = tri_dict[number]
    triangles_per_surface_stats = {}
    triangles_per_surface_stats['minimum'] = min(tri_dict.keys())
    triangles_per_surface_stats['maximum'] = max(tri_dict.keys())
    median = find_median(sorted_dictionary)
    triangles_per_surface_stats['median'] = median
    mean = find_mean(sorted_dictionary)
    triangles_per_surface_stats['mean'] = mean
    return triangles_per_surface_stats

    