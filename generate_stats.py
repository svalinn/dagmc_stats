#This file is the script that users will actually run to generate the full set of statistics for a file

# set the path to find the current installation of pyMOAB
import sys
import numpy as np
import argparse
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range
# import the new module that defines each of the functions
import dagmc_stats
import entity_specific_stats

def report_stats(stats, data, verbose, spv_data, tps_data):
    """
    Method to print a table of statistics.
    
    inputs
    ------
    stats : a dictionary with information about certain statistics for a model
    """
    
    if verbose: #if the user wants verbosity, print with more words
        for statistic, value in stats['S_P_V'].items():
            print("The {} number of Surfaces per Volume in this model is {}.".format(value, statistic))
    else: #or, print with minimal words
        print("Surfaces per Volume:")
        for statistic, value in stats['S_P_V'].items():
            print("{} : {}".format(statistic, value))
    if spv_data:
        entity_specific_stats.print_spv_data(data['spv_dict'])
    if tps_data:
        entity_specific_stats.print_tps_data(data['tps_dict'])
        
        
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
    
    spv_key = 'S_P_V'
    tps_key = 'T_P_S'
    tpv_key = 'T_P_V'
    
    data[spv_key] = dagmc_stats.get_surfaces_per_volume(my_core, entityset_ranges) #dict
    data[tps_key] = dagmc_stats.get_surfaces_per_volume(my_core, entityset_ranges) #dict
    data[tpv_key] = dagmc_stats.get_surfaces_per_voluem(my_core, entityset_ranges) #list
    
    stats[tps_key] = get_stats(data[tps_key].values())
    stats[spv_key] = get_stats(data[spv_key].values())
    stats[tpv_key] = get_stats(data[tpv_key])
    
    return stats, data
    
    
def main():

    # allows the user to input the file name into the command line
    parser = argparse.ArgumentParser() 
    parser.add_argument("filename", help = "the file that you want read")
    parser.add_argument("-v", "--verbose", action = "store_true", help = "increase output verbosity") #optional verbosity setting
    parser.add_argument("--tps_data", action = "store_true", help = "display the triangles per surface raw data")
    parser.add_argument("--spv_data", action = "store_true", help = "display the surfaces per volume raw data")
    args = parser.parse_args() 
    input_file = args.filename
    verbose = args.verbose
    tps_data = args.tps_data
    spv_data = args.spv_data

    my_core = core.Core() #initiates core
    my_core.load_file(input_file) #loads the file
    root_set = my_core.get_root_set() #dumps all entities into the meshset to be redistributed to other meshsets
    stats, data = collect_statistics(my_core, root_set)
    report_stats(stats, data, verbose, spv_data, tps_data)
    
    
if __name__ == "__main__":
    main()
    