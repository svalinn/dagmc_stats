import pandas as pd
import numpy as np
from pymoab.rng import Range
from pymoab import core, types

class DagmcStats:

    tri_vert_struct = np.dtype({'names': ['tri', 'vert', 'angle',
    'side_length'], 'formats': [np.uint64, np.uint64, np.float64, np.float64]})


    def __init__(self, filename, populate=False):
        # read file
        self._my_moab_core = core.Core()
        self._my_moab_core.load_file(filename)
        self.root_set = self._my_moab_core.get_root_set()
        entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
        
        # some metadata
        self.native_ranges = get_native_ranges(root_set, entity_types)
        self.dagmc_tags = get_dagmc_tags()
        self.entityset_ranges = get_entityset_ranges(root_set, dagmc_tags['geom_dim'])

        # initialize data frames
        self._vert_data = pd.DataFrame(columns = ['vert_eh', 'roughness','t_p_v'], index='vert_eh')
        self._tri_data = pd.DataFrame(columns = ['tri_eh', 't_a_r', 'tri_area'], index='tri_eh')
        self._surface_data = pd.DataFrame(columns = ['surf_eh', 't_p_s', 'coarseness'], index='surf_eh')
        self._volume_data = pd.DataFrame(columns = ['volume', 's_p_v', 'coarseness'], index='volume')

        """
        TODO: args(not part of init->user input when query
        tar_meshset = args.tar_meshset
        if tar_meshset == None:
            tar_meshset = root_set
        
        # TODO: default data to populate data frames??
        if populate:
            #  xxx
        return
        """


    def get_native_ranges(meshset, entity_types):
        """
        Get a dictionary with MOAB ranges for each of the requested entity types

        inputs
        ------
        meshset : a MOAB meshset to query for the ranges of entities
        entity_types : a list of valid pyMOAB types to be retrieved

        outputs
        -------
        native_ranges : a dictionary with one entry for each entity type that is a
                        Range of handles to that type
        """

        native_ranges = {}
        for entity_type in entity_types:
            native_ranges[entity_type] = self._my_moab_core.get_entities_by_type(
                meshset, entity_type)
        return native_ranges


    def get_dagmc_tags():
        """
        Get a dictionary with the important tags for DAGMC geometries

        inputs
        ------
        none

        outputs
        -------
        dagmc_tags : a dictionary of relevant tags
        """
        tag_data_list = { 'geom_dim' : { 'name': 'GEOM_DIMENSION', 'size': 1, 'type': types.MB_TYPE_INTEGER },
                  'category' : { 'name': 'CATEGORY', 'size': 32, 'type': types.MB_OPAQUE },
                  'global_id' : { 'name': 'GLOBAL_ID', 'size': 1, 'type': types.MB_TYPE_INTEGER }
                  }

        for key, tag_data in tag_data_list:
            dagmc_tags[key] = self._my_moab_core.tag_get_handle(tag_data['name'],
                                                          size=tag_data['size'],
                                                          tag_type=tag_data['type'],
                                                          storage_type=types.MB_TAG_SPARSE,
                                                          create_if_missing=True)
        return dagmc_tags
    
    


