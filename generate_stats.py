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
import entity_specific_stats


def report_stats(stats, data, verbose, display_options):

    """
    Method to print a table of statistics.
    
    inputs
    ------
    stats : a dictionary with information about certain statistics for a model
    data : a dictionary with the data for each statistical area
    verbose : a setting that determines how wordy (verbose) the output is
    display_options : a dictionary with different settings to determine which statistics
                      get printed
    """
  
    if verbose: #if the user wants verbosity, print with more words
        if display_options['NR']:
            for nr, size in stats['native_ranges'].items():
                print("There are {} entities of native type {} in this model".format(
                    size.size(), nr))
        if display_options['ER']:
            for er, size in stats['entity_ranges'].items():
                print("There are {} {} in this model".format(size.size(), er))
        if display_options['TPS']:
            for statistic, value in stats['T_P_S'].items():
                print("The {} number of Triangles per Surface in this model is {}.".format(
                    statistic, value))
        if display_options['SPV']:  
            for statistic, value in stats['S_P_V'].items():
                print("The {} number of Surfaces per Volume in this model is {}.".format(
                    statistic, value))
        if display_options['TPV']:
            for statistic, value in stats['T_P_V'].items():
                print("The {} number of Triangles per Vertex in this model is {}.".format(
                    statistic, value))
        if display_options['TAR']:
            for statistic, value in stats['T_A_R'].items():
                print("The {} Triangle Aspect Ratio in this model is {}.".format(
                    statistic, value))
    else: #or, print with minimal words
        if display_options['NR']:
            for nr, size in stats['native_ranges'].items():
                print("Type {} : {}".format(nr, size.size()))
        if display_options['ER']:
            for er, size in stats['entity_ranges'].items():
                print("{} : {}".format(er, size.size()))
        if display_options['TPS']:
            print("Triangles per Surface:")
            for statistic, value in stats['T_P_S'].items():
                print("{} : {}".format(statistic, value))
        if display_options['SPV']:
            print("Surfaces per Volume:")
            for statistic, value in stats['S_P_V'].items():
                print("{} : {}".format(statistic, value))
        if display_options['TPV']:
            print("Triangles per Vertex:")
            for statistic, value in stats['T_P_V'].items():
                print("{} : {}".format(statistic, value))
        if display_options['TAR']:
            print("Triangle Aspect Ratio:")
            for statistic, value in stats['T_A_R'].items():
                print("{} : {}".format(statistic, value))

    if display_options['SPV_data']:
        entity_specific_stats.print_spv_data(data['S_P_V'])
    if display_options['TPS_data']:
        entity_specific_stats.print_tps_data(data['T_P_S'])

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


def collect_statistics(my_core, root_set, tar_meshset):
    """
    Collects statistics for a range of different areas
   
    inputs
    ------
    my_core : a MOAB Core instance
    root_set : the root set for a file
    tar_meshset : the meshset for the triangle aspect ratio statistic
    
    outputs
    -------
    stats : a dictionary containing statistics for a variety of different areas
    """
    
    stats = {}
    data = {}
    
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    
    entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
    native_ranges = dagmc_stats.get_native_ranges(my_core, root_set, entity_types)     # get Ranges of various entities
    
    entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, root_set,
                                                        dagmc_tags['geom_dim'])
  
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
    
    tar_key = 'T_A_R'
    data[tar_key] = dagmc_stats.get_triangle_aspect_ratio(
                                my_core, tar_meshset, dagmc_tags['geom_dim'])
    stats[tar_key] = get_stats(data[tar_key])
    
    return stats, data
    

def main():

    # allows the user to input the file name into the command line

    parser = argparse.ArgumentParser() 
    parser.add_argument("filename", help = "the file that you want read")
    parser.add_argument("-v", "--verbose", action = "store_true", help = "increase output verbosity") #optional verbosity setting
    parser.add_argument("--tps_data", action = "store_true", help = "display the triangles per surface raw data")
    parser.add_argument("--spv_data", action = "store_true", help = "display the surfaces per volume raw data")
    parser.add_argument("--nr", action = "store_true",
                        help = "display native ranges (default is to display all statistics)")
    parser.add_argument("--er", action = "store_true",
                        help = "display entityset ranges (Volume, Surface, Curve, Node)")
    parser.add_argument("--spv", action = "store_true",
                        help = "display surface per volume stats") 
    parser.add_argument("--tpv", action = "store_true",
                        help = "display triangles per vertex stats")
    parser.add_argument("--tps", action = "store_true",
                        help = "display triangles per surface stats")
    parser.add_argument("--tar", action = "store_true",
                        help = "display triangle aspect ratio stats")
    parser.add_argument("--tar_meshset", type = np.uint64, help =
                        "meshset for triangle aspect ratio stats")
    args = parser.parse_args() 

    input_file = args.filename
    verbose = args.verbose
    tps_data = args.tps_data
    spv_data = args.spv_data
    display_options = {'NR':args.nr, 'ER':args.er, 'SPV':args.spv, 'TPV':args.tpv,
                       'TPS':args.tps, 'TAR':args.tar, 'TPS_data':args.tps_data, 'SPV_data':args.spv_data} 
    if not(True in display_options.values()):
        display_options = {'NR':True, 'ER':True, 'SPV':True, 'TPV':True, 'TPS':True,
                           'TAR':True, 'TPS_data':False, 'SPV_data':False}
    my_core = core.Core() #initiates core
    my_core.load_file(input_file) #loads the file
    root_set = my_core.get_root_set() #dumps all entities into the meshset to be redistributed to other meshsets
    
    tar_meshset = args.tar_meshset
    if tar_meshset == None:
        tar_meshset = root_set

    stats, data = collect_statistics(my_core, root_set, tar_meshset)
    report_stats(stats, data, verbose, display_options)

if __name__ == "__main__":
    main()
    