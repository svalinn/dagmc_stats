
# set the path to find the current installation of pyMOAB
import sys
sys.path.append('/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab import core, types
from pymoab.rng import Range

# import the new module that defines each of the functions
import dagmc_stats

import nose

test_input = "3vols.h5m"

my_core = core.Core()
meshset = my_core.create_meshset()
my_core.load_file(test_input, meshset)

def test_get_tags():

    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    assert(len(dagmc_tags) == 3)
def test_get_ranges():
    
    entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
    dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
    entity_ranges = dagmc_stats.get_entity_ranges(my_core, meshset, entity_types, dagmc_tags)
    assert(len(entity_ranges) == 6)
    

    
