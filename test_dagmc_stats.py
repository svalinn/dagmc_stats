
# set the path to find the current installation of pyMOAB
import sys
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range

# import the new module that defines each of the functions
import dagmc_stats
from collections import OrderedDict
import statistics
import nose
import random as rd
test_input = "3vols.h5m"

my_core = core.Core()
my_core.load_file(test_input)
test_set = {}
for x in range(rd.randint(1,10)):
    test_set[rd.randint(10*x,10*x+10)] = rd.randint(1,10000)
def test_get_tags():

    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    assert(len(dagmc_tags) == 3)

def test_get_median():

    # Sort the dictionary
    values_sorted = OrderedDict(sorted(test_set.items(), key=lambda t: t[0]))
    index = sum(values_sorted.values())/2

    # Decide whether the number of records is an even or odd number
    if (index).is_integer():
        even = True
    else: 
        even = False

    x = True

    # Compute median
    for value, occurences in values_sorted.items():
        index -= occurences
        if index < 0 and x is True:
            median_manual = value
            break
        elif index == 0 and even is True:
            median_manual = value/2
            x = False
        elif index < 0 and x is False:

            median_manual += value/2
            break

    # Create a list of all records and compute median using statistics package
    values_list = list()
    for val, count in test_set.items():
        for count in range(count):
            values_list.append(val)

    median_computed = statistics.median(values_list)
    median = dagmc_stats.find_median(test_set)
    assert(median == median_manual == median_computed)
    
def test_median():
    my_mean = dagmc_stats.find_mean(test_set)
    values_list = list()
    for val, count in test_set.items():
        for count in range(count):
            values_list.append(val)
    computed_mean = statistics.mean(values_list)
    assert(my_mean == computed_mean)

    
    
    
    
    
    
    
    