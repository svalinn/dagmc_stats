# This file is the script that users will actually run to generate the full set of statistics for a file

# set the path to find the current installation of pyMOAB
import sys
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range

# import the new module that defines each of the functions
import dagmc_stats

def report_stats(entity_ranges):
    """
    Method to print a table of statistics.
    
    inputs
    ------
    entity_ranges : a dictionary with one entry for each entity type that is a Range of handles to that type
    """

    for type, eh_range in entity_ranges:
        print("There are {} entities of type {}.".format(type, len(eh_range)))

def main():

    # starting with a single input file - will need to convert this to a user option
    input_file = "3vols.h5m"

    core = mb.core.Core() #initiates core
    all_meshset = core.create_meshset() #creates meshset
    core.load_file(input_file, all_meshset) #dumps all entities into the meshset to be redistributed to other meshsets

    # get tags
    dagmc_tags = get_dagmc_tags(core)
    
    # get Ranges of various entities
    entity_types = [types.MBVERTEX, types.MBTRI]
    entity_ranges = get_entity_ranges(core, all_meshset, entity_types)

    
if __name__ == "__main__":
    main()
    
