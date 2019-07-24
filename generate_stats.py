#This file is the script that users will actually run to generate the full set of statistics for a file

# set the path to find the current installation of pyMOAB
import sys
import argparse
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range
# import the new module that defines each of the functions
import dagmc_stats






def report_stats(stats, verbose):
    """
    Method to print a table of statistics.
    
    inputs
    ------
    stats : a dictionary with information about certain statistics for a model
    """
    
    if verbose: #if the user wants verbosity, print with more words
        for native_type, native_range in stats['Native Ranges'].items():
            print("There are {} entities of type {}.".format(native_range.size(), native_type))
        for entityset_type, entityset_range in stats['EntitySet Ranges'].items():
            print("There are {} entities of type {}.".format(entityset_range.size(), entityset_type))
    else: #or, print with minimal words
        for native_type, native_range in stats['Native Ranges'].items():
            print("Type {}: {}".format(native_type, native_range.size()))
        for entityset_type, entityset_range in stats['EntitySet Ranges'].items():
            print("Type {}: {}".format(entityset_type, entityset_range.size()))
        
            

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
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
    stats['Native Ranges'] = dagmc_stats.get_native_ranges(my_core, root_set, entity_types)     # get Ranges of various entities
    stats['EntitySet Ranges'] = dagmc_stats.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim']) 
    return stats
    
    
def main():

    # allows the user to input the file name into the command line
    parser = argparse.ArgumentParser() 
    parser.add_argument("filename", help = "the file that you want read")
    parser.add_argument("-v", "--verbose", action = "store_true", help = "increase output verbosity") #optional verbosity setting
    args = parser.parse_args() 
    input_file = args.filename
    verbose = args.verbose


    my_core = core.Core() #initiates core
    my_core.load_file(input_file) #loads the file
    root_set = my_core.get_root_set() #dumps all entities into the meshset to be redistributed to other meshsets
    stats = collect_statistics(my_core, root_set)
    report_stats(stats, verbose)
    
    
if __name__ == "__main__":
    main()
    