import pandas as pd
import numpy as np
from pymoab.rng import Range
from pymoab import core, types

class DagmcStats:

    tri_vert_struct = np.dtype({'names': ['tri', 'vert', 'angle',
    'side_length'], 'formats': [np.uint64, np.uint64, np.float64, np.float64]})


    def __init__(self, filename, populate=False):
        # read file
        my_core = core.Core()
        self._my_moab_core = core.Core()#TODO
        self._my_moab_core.load_file(filename)
        self.root_set = self._my_moab_core.get_root_set()
        #self._my_moab_core = my_core.load_file(...)
        #root_set = my_core.get_root_set()
        entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
        
        # some metadata
        self._native_ranges = get_native_ranges(my_core, root_set, entity_types)
        self.dagmc_tags = get_dagmc_tags(my_core)
        self.entityset_ranges = get_entityset_ranges(my_core, root_set,
                                                    dagmc_tags['geom_dim'])

        # initialize data frames
        self._vert_data = pd.DataFrame(columns = ['vert_eh', 'roughness','t_p_v'])
        self._tri_data = pd.DataFrame(columns = ['tri_eh', 't_a_r', 'tri_area'])
        self._surface_data = pd.DataFrame(columns = ['surf_eh', 't_p_s', 'coarseness'])
        self._volume_data = pd.DataFrame(columns = ['volume', 's_p_v', 'coarseness'])
        
        self._vert_data = df_vert.set_index('vert_eh')
        self._tri_data = df_tri.set_index('tri_eh')
        self._surface_data = df_surf.set_index('surf_eh')
        self._volume_data = df_volume.set_index('volume')
        
        # TODO: args(not part of init->user input when query
        tar_meshset = args.tar_meshset
        if tar_meshset == None:
            tar_meshset = root_set
        
        # TODO: default data to populate data frames??
        if populate:
            #  xxx
        return


    def get_native_ranges(my_core, meshset, entity_types):
        """
        Get a dictionary with MOAB ranges for each of the requested entity types

        inputs
        ------
        my_core : a MOAB Core instance
        meshset : a MOAB meshset to query for the ranges of entities
        entity_types : a list of valid pyMOAB types to be retrieved

        outputs
        -------
        native_ranges : a dictionary with one entry for each entity type that is a
                        Range of handles to that type
        """

        native_ranges = {}
        for entity_type in entity_types:
            native_ranges[entity_type] = my_core.get_entities_by_type(
                meshset, entity_type)
        return native_ranges


    def get_dagmc_tags:
        """
        Get a dictionary with the important tags for DAGMC geometries

        inputs
        ------
        my_core : a MOAB Core instance

        outputs
        -------
        dagmc_tags : a dictionary of relevant tags
        """

        dagmc_tags = {}
        # geometric dimension
        dagmc_tags['geom_dim'] = \
            my_core.tag_get_handle('GEOM_DIMENSION',
                                   size=1, tag_type=types.MB_TYPE_INTEGER,
                                   storage_type=types.MB_TAG_SPARSE,
                                   create_if_missing=True)
        # the category
        dagmc_tags['category'] = \
            my_core.tag_get_handle('CATEGORY',
                                   size=32,
                                   tag_type=types.MB_TYPE_OPAQUE,
                                   storage_type=types.MB_TAG_SPARSE,
                                   create_if_missing=True)
        # id
        dagmc_tags['global_id'] = \
            my_core.tag_get_handle('GLOBAL_ID',
                                   size=1,
                                   tag_type=types.MB_TYPE_INTEGER,
                                   storage_type=types.MB_TAG_SPARSE,
                                   create_if_missing=True)
        return dagmc_tags
    
    


