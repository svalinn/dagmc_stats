# This file is the script that users will actually run to generate the full set of statistics for a file

# set the path to find the current installation of pyMOAB
import sys
import numpy as np
import argparse
import sys
sys.path.append(
    '/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')

from pymoab.rng import Range
from pymoab import core, types

# import the new module that defines each of the functions
import dagmc_stats


def report_stats(stats, verbose):
    """
    Method to print a table of statistics.
    
    inputs
    ------
    stats : a dictionary with information about certain statistics for a model
    """
    
    if verbose:  # if the user wants verbosity, print with more words
        for nr, size in stats['native_ranges'].items():
            print("There are {} entities of native type {} in this model".format(
                 size.size(), nr))
        for er, size in stats['entity_ranges'].items():
            print("There are {} {} in this model".format(size.size(), er))
        for statistic, value in stats['T_P_S'].items():
            print("The {} number of Triangles per Surface in this model is {}.".format(
                 value, statistic))
        for statistic, value in stats['S_P_V'].items():
            print("The {} number of Surfaces per Volume in this model is {}.".format(
                 value, statistic))
        for statistic, value in stats['T_P_V'].items():
            print("The {} number of Triangles per Vertex in this model is {}.".format(
                 value, statistic))
            
    else:  # or, print with minimal words
        for nr, size in stats['native_ranges'].items():
            print("Type {} : {}".format(nr, size.size()))
        for er, size in stats['entity_ranges'].items():
            print("{} : {}".format(er, size.size()))
        print("Triangles per Surface:")
        for statistic, value in stats['T_P_S'].items():
            print("{} : {}".format(statistic, value))
        print("Surfaces per Volume:")
        for statistic, value in stats['S_P_V'].items():
            print("{} : {}".format(statistic, value))
        print("Triangles per Vertex:")
        for statistic, value in stats['T_P_V'].items():
            print("{} : {}".format(statistic, value))
def get_stats(data):
    """
    gets the minimum, maximum, median, and mean for a dataset
    
    inputs
    ------
    data : a dataset in list form
    
    outputs
    -------
    statistics : a dictionary of statistics for a given dataset
    """
    
    statistics = {}
    statistics['minimum'] = min(data)
    statistics['maximum'] = max(data)
    statistics['median'] = np.median(list(data))
    statistics['mean'] = np.mean(list(data))
    return statistics


def collect_statistics(my_core, root_set):
    """
    Collects statistics for a range of different areas
   
    inputs
    ------
    my_core : a MOAB Core instance
    root_set : the root set for a file
    
    outputs
    -------
    stats : a dictionary containing statistics for a variety of different areas
    """
    
    stats = {}
    data = {}
    
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    
    entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
    native_ranges = dagmc_stats.get_native_ranges(my_core, root_set, entity_types)     # get Ranges of various entities
    
    entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
  
    stats['native_ranges'] = native_ranges
    stats['entity_ranges'] = entityset_ranges
    
    
    spv_key = 'S_P_V'
    data[spv_key] = dagmc_stats.get_surfaces_per_volume(
                                my_core, entityset_ranges)
    stats[spv_key] = get_stats(data[spv_key].values())
    
    tps_key = 'T_P_S'
    data[tps_key] = dagmc_stats.get_triangles_per_surface(
                                my_core, entityset_ranges)
    stats[tps_key] = get_stats(data[tps_key].values())
 
    tpv_key = 'T_P_V'
    data[tpv_key] = dagmc_stats.get_triangles_per_vertex(
                                my_core, native_ranges)
    stats[tpv_key] = get_stats(data[tpv_key])
    
    return stats, data
    

def main():

    # allows the user to input the file name into the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the file that you want read")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")  # optional verbosity setting
    args = parser.parse_args()
    input_file = args.filename
    verbose = args.verbose


    my_core = core.Core() #initiates core
    my_core.load_file(input_file) #loads the file
    root_set = my_core.get_root_set() #dumps all entities into the meshset to be redistributed to other meshsets
    stats, data = collect_statistics(my_core, root_set)
    report_stats(stats, verbose)


if __name__ == "__main__":
    main()
