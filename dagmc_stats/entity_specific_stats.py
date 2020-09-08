import numpy as np
from pymoab.rng import Range
from pymoab import core, types


def get_spv_data(my_core, entityset_ranges, global_id):
    """
    Gets the actual data for surfaces per volume
    i.e. the number of surfaces each volume handle contains, 
    as well as the Global ID for the volume
  
    inputs
    ------
    my_core : a MOAB Core instance
    spv_data : a dictionary containing every volume paired with the number of child surfaces
    global_id : a MOAB Tag given to each entity in a mesh
    """
    spv_data = []
    for volume in entityset_ranges['Volumes']:
        spv_data.append((volume, my_core.tag_get_data(global_id, volume)[0][0], my_core.get_child_meshsets(volume).size()))
    return spv_data

def get_tps_data(my_core, entityset_ranges, global_id):
    """
    Gets the actual data for triangles per surface
    i.e. the number of triangles each surface handle contains, 
    as well as the Global ID for the surface
  
    inputs
    ------
    my_core : a MOAB Core instance
    tps_data : a dictionary containing every surface paired with the number of corrosponding triangles
    global_id : a MOAB Tag given to each entity in a mesh
    """
    tps_data = []
    for surface in entityset_ranges['Surfaces']:
        tps_data.append((surface, my_core.tag_get_data(global_id, surface)[0][0], my_core.get_entities_by_type(
                                                                                    surface, types.MBTRI).size()))
    return tps_data

