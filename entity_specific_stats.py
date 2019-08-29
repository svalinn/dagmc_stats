import sys
import numpy as np
sys.path.append(
    '/opt/tljh/user/lib/moab/lib/python3.6/site-packages/pymoab-5.1.0-py3.6-linux-x86_64.egg')
from pymoab.rng import Range
from pymoab import core, types


def print_spv_data(spv_data):
    """
    Prints the actual data for surfaces per volume
    i.e. the number of surfaces each volume handle contains
  
    inputs
    ------
    data[spv_key] : a dictionary containing every volume paired with the number of child surfaces
    
    """
    print('Volume                          Surfaces')
    for volume, surfaces in spv_data.items():
        print("{} ({})        {}".format(volume, ids, surfaces))
        

def print_tps_data(tps_data):
    """
    Prints the actual data for triangles per surface
    i.e. the number of triangles each surface handle contains
    
    inputs
    ------
    data[tps_key] : a dictionary containing every surface paired with the number of triangles it contains
    
    """
    print('Surface                        Triangles')
    for surface, triangles in tps_data.items():
        print("{} ({})        {}".format(surface, ids, triangles))
        