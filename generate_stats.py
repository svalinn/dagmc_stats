# This file is the script that users will actually run to generate the full set of statistics for a file

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





def report_stats(entity_ranges, surface_per_volume_stats, triangle_per_vertex_stats, triangle_per_surface_stats, verbose):
    """
    Method to print a table of statistics.
    
    inputs
    ------
    entity_ranges : a dictionary with one entry for each entity type that is a Range of handles to that type
    """
    type_legend = {0:'Vertex', 2:'Triangle', 11: 'EntitySet'}
    if verbose: #if the user wants verbosity, print with more words
        for entity_type, eh_range in entity_ranges.items():
            if type(entity_type) == int:
                entity_type = type_legend[entity_type]
            print("There are {} entities of type {}.".format(eh_range.size(),entity_type))
        for stat, number in surface_per_volume_stats.items():
            print('The {} number of Surfaces per Volume in this file is {}'.format(stat, number))
        for stat, number in triangle_per_vertex_stats.items():
            print('The {} number of Triangles per Vertex in this file is {}'.format(stat, number))
        for stat, number in triangle_per_surface_stats.items():
            print('The {} number of Triangles per Surface in this file is {}'.format(stat, number))
    else: #or, print with minimal words
        for entity_type, eh_range in entity_ranges.items():
            if type(entity_type) == int:
                entity_type = type_legend[entity_type]
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

def main():

    # allows the user to input the file name into the command line
    parser = argparse.ArgumentParser() 
    parser.add_argument("filename", help = "the file that you want read")
    parser.add_argument("-v", "--verbose", action = "store_true", help = "increase output verbosity") #optional verbosity setting
    args = parser.parse_args() 
    input_file = args.filename
    verbose = args.verbose
    #input_file = "3vols.h5m"

    my_core = core.Core() #initiates core
    all_meshset = my_core.create_meshset() #creates meshset
    my_core.load_file(input_file) #loads the file
    all_meshset = my_core.get_root_set() #dumps all entities into the meshset to be redistributed to other meshsets
    # get tags
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
    native_ranges = dagmc_stats.get_native_ranges(my_core, all_meshset, entity_types)     # get Ranges of various entities
    entity_ranges = dagmc_stats.get_entityset_ranges(my_core, all_meshset, native_ranges, dagmc_tags)
    surface_per_volume_stats = dagmc_stats.get_surfaces_per_volume(my_core, entity_ranges) #get stats for surface per volume
    triangle_per_vertex_stats = dagmc_stats.get_triangles_per_vertex(my_core, entity_ranges) #get stats for triangle per vertex
    triangle_per_surface_stats = dagmc_stats.get_triangles_per_surface(my_core, entity_ranges) #get stats for triangle per surface
    report_stats(entity_ranges, surface_per_volume_stats, triangle_per_vertex_stats, triangle_per_surface_stats, 
                 verbose) #report the statistics
    #show_histograms()
if __name__ == "__main__":
    main()