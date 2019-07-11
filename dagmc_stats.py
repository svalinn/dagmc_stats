# set the path to find the current installation of pyMOAB
import sys
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range
import numpy as np
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
                                                 storage_type = types.MB_TAG_SPARSE, create_if_missing = True)# metric dimension
    
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
    dagmc_tags : the MOAB tags created in a file
    outputs
    -------
    entity_ranges : a dictionary with one entry for each entity type that is a Range of handles to that type
    """

    entity_ranges = {}
    for entity_type in entity_types:#goes through each entitytype given
        entity_ranges[entity_type] = my_core.get_entities_by_type(meshset, entity_type) 
        if entity_type == 11: #if the type is mbentitytypes
            entity_ranges['Volumes'] = my_core.get_entities_by_type_and_tag(meshset, types.MBENTITYSET, dagmc_tags['geom_dim'], [3]) #get all of the entities that are a certain dimension (volumes, surfaces, curves) and part of the set
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
    pdf : a histogram that displays the number of surfaces each volume has (matplotlib)
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
    divisions = int(len(vert_list)/10000)
    broken_up_verts = []
    for cut in range(divisions+1):
        broken_up_verts.append(list(vert_list[cut*10000:cut*10000+10000]))
    
    vertices_and_frequencies = {}
    for cut in range(divisions+1):
        for vert in broken_up_verts[cut]:
            number_of_vertex = vert
            try:
                vertices_and_frequencies[number_of_vertex] += 1
            except KeyError:
                vertices_and_frequencies[number_of_vertex] = 1
    number_of_frequencies = {}
    for vertex in vertices_and_frequencies:
        try:
            number_of_frequencies[vertices_and_frequencies[vertex]] += 1
        except KeyError:
            number_of_frequencies[vertices_and_frequencies[vertex]] = 1
    sorted_dict = {}
    for frequency in sorted(number_of_frequencies.keys()):
        sorted_dict[frequency] = number_of_frequencies[frequency]
    return(sorted_dict)


def find_median(sorted_dict):
    length = 0
    for value in sorted_dict.values():
        length += value
    half = length / 2
    sum_var = 0
    for val in sorted_dict.values():
        if half-sum_var > 0:
            sum_var += val
        else:
            break
    index = (list(sorted_dict.values()).index(val))
    if sum(list(sorted_dict.values())[index:]) != sum(list(sorted_dict.values())[:index]):
        if sum(list(sorted_dict.values())[index:]) > sum(list(sorted_dict.values())[:index]):
            median = list(sorted_dict.keys())[index]
        else:
            median = list(sorted_dict.keys())[index-1]
    else:
        median = (list(sorted_dict.keys())[index-1] + list(sorted_dict.keys())[index]) / 2
    return(median)
        
def find_mean(sorted_dict):
    total = 0
    for key, value in sorted_dict.items():
        total += key*value
    mean = total / sum(sorted_dict.values())
    return(mean)

def get_triangles_per_vertex(my_core, all_meshset):
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
    triangles_per_vertex_stats = {}
    triangles_per_vertex_stats['minimum'] = min(sorted_dict.keys())
    triangles_per_vertex_stats['maximum'] = max(sorted_dict.keys())
    median = find_median(sorted_dict)
    triangles_per_vertex_stats['median'] = median
    mean = find_mean(sorted_dict)
    triangles_per_vertex_stats['average'] = mean
    return triangles_per_vertex_stats

