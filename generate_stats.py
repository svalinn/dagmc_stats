# This file is the script that users will actually run to generate the full set of statistics for a file

# set the path to find the current installation of pyMOAB
import numpy as np
import argparse
import dagmc_stats
from pymoab.rng import Range
from pymoab import core, types
import sys
sys.path.append(
    '/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
# import the new module that defines each of the functions


def report_stats(stats, verbose):
    """
    Method to print a table of statistics.

    inputs
    ------
    stats : a dictionary with information about certain statistics for a model
    """

    if verbose:  # if the user wants verbosity, print with more words
        for statistic, value in stats['T_P_S'].items():
            print("The {} number of Triangles per Surface in this model is {}.".format(
                value, statistic))
    else:  # or, print with minimal words
        print("Triangles per Surface:")
        for statistic, value in stats['T_P_S'].items():
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
    statistics['median'] = np.median(data)
    statistics['mean'] = np.mean(data)
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
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
    native_ranges = dagmc_stats.get_native_ranges(
        my_core, root_set, entity_types)     # get Ranges of various entities
    entityset_ranges = dagmc_stats.get_entityset_ranges(
        my_core, root_set, dagmc_tags['geom_dim'])
    t_p_s_data = dagmc_stats.get_triangles_per_surface(
        my_core, entityset_ranges)
    t_p_s_stats = get_stats(t_p_s_data)
    stats['T_P_S'] = t_p_s_stats
    return stats


def main():

    # allows the user to input the file name into the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the file that you want read")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")  # optional verbosity setting
    args = parser.parse_args()
    input_file = args.filename
    verbose = args.verbose
    #input_file = "3vols.h5m"

    my_core = core.Core()  # initiates core
    my_core.load_file(input_file)  # loads the file
    # dumps all entities into the meshset to be redistributed to other meshsets
    root_set = my_core.get_root_set()
    stats = collect_statistics(my_core, root_set)
    report_stats(stats, verbose)


if __name__ == "__main__":
    main()
