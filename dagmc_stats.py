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
    
