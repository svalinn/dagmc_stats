#This file is the script that users will actually run to generate the full set of statistics for a file

# set the path to find the current installation of pyMOAB
import sys
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range
import matplotlib.pyplot as plt
import numpy as np
# import the new module that defines each of the functions
import dagmc_stats
import argparse





def report_stats(entityset_ranges, native_ranges, surface_per_volume_stats, triangle_per_vertex_stats, triangle_per_surface_stats, verbose):
    """
    Method to print a table of statistics.
    
    inputs
    ------
    entity_ranges : a dictionary with one entry for each entity type that is a Range of handles to that type
    """
    if verbose: #if the user wants verbosity, print with more words
        for native_type, native_range in native_ranges.items():
            print("There are {} entities of type {}.".format(native_range.size(),native_type))
        print('Type 0: Vertices \nType 2: Triangles \nType 11: EntitySets')
        for set_type, set_range in entityset_ranges.items():
            print("There are {} {} in this model".format(set_range.size(), set_type))
        for stat, number in surface_per_volume_stats.items():
            print('The {} number of Surfaces per Volume in this file is {}'.format(stat, number))
        for stat, number in triangle_per_vertex_stats.items():
            print('The {} number of Triangles per Vertex in this file is {}'.format(stat, number))
        for stat, number in triangle_per_surface_stats.items():
            print('The {} number of Triangles per Surface in this file is {}'.format(stat, number))
    else: #or, print with minimal words
        for entity_type, eh_range in entityset_ranges.items():
            print("Type {}: {}".format(entity_type, eh_range.size()))
        for entity_type, eh_range in native_ranges.items():
            print("Type {}: {}".format(entity_type, eh_range.size()))
        print("Surfaces per Volume:")
        for stat, number in surface_per_volume_stats.items():
            print('{}:{}'.format(stat, number))
        print("Triangles per Vertex:")
        for stat, number in triangle_per_vertex_stats.items():
            print('{}:{}'.format(stat, number))
        print('Triangles per Surface:')
        for stat, number in triangle_per_surface_stats.items():
            print('{}:{}'.format(stat, number))

def main(input_file, verbose = False):

    

    my_core = core.Core() #initiates core
    all_meshset = my_core.create_meshset() #creates meshset
    my_core.load_file(input_file) #loads the file
    all_meshset = my_core.get_root_set() #dumps all entities into the meshset to be redistributed to other meshsets
    # get tags
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
    native_ranges = dagmc_stats.get_native_ranges(my_core, all_meshset, entity_types)     # get Ranges of various entities
    entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, all_meshset, dagmc_tags['geom_dim'])
    surface_per_volume_stats, s_p_v_data = dagmc_stats.get_surfaces_per_volume(my_core, entityset_ranges) #get stats for surface per volume
    triangle_per_vertex_stats, t_p_v_data = dagmc_stats.get_triangles_per_vertex(my_core, native_ranges) #get stats for triangle per vertex
    triangle_per_surface_stats, t_p_s_data = dagmc_stats.get_triangles_per_surface(my_core, entityset_ranges) #get stats for triangle per surface
    report_stats(entityset_ranges, native_ranges, surface_per_volume_stats, triangle_per_vertex_stats, triangle_per_surface_stats, 
                 verbose) 
    return s_p_v_data, t_p_v_data, t_p_s_data
if __name__ == "__main__":
    main()