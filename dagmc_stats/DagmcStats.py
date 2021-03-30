import pandas as pd
import numpy as np
from pymoab.rng import Range
from pymoab import core, types


class DagmcStats:

    def __init__(self, filename, populate=False):
        """Constructor

        inputs
        ------
        filename : name of the file
        populate : boolean value that determines whether or not to populate the data

        outputs
        -------
        none
        """
        # read file
        self._my_moab_core = core.Core()
        self._my_moab_core.load_file(filename)
        self.root_set = self._my_moab_core.get_root_set()

        # initialize data frames
        self._vert_data = pd.DataFrame(
            columns=['vert_eh', 'roughness', 'tri_per_vert'])
        self._vert_data = self._vert_data.set_index('vert_eh')

        self._tri_data = pd.DataFrame(
            columns=['tri_eh', 'aspect_ratio', 'area'])
        self._tri_data = self._tri_data.set_index('tri_eh')

        self._surf_data = pd.DataFrame(
            columns=['surf_eh', 'tri_per_surf', 'coarseness'])
        self._surf_data = self._surf_data.set_index('surf_eh')

        self._vol_data = pd.DataFrame(
            columns=['vol_eh', 'surf_per_vol', 'coarseness'])
        self._vol_data = self._vol_data.set_index('vol_eh')
        
        self.entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
        self.native_ranges = {}
        self.__set_native_ranges()
        self.dagmc_tags = {}
        self.__set_dagmc_tags()

    def __set_native_ranges(self):
        """Set the class native_ranges variable to a dictionary with MOAB
        ranges for each of the requested entity types

        inputs
        ------
        none

        outputs
        -------
        native_ranges : a dictionary with one entry for each entity type that is a
                        Range of handles to that type
        """
        for entity_type in self.entity_types:
            self.native_ranges[entity_type] = self._my_moab_core.get_entities_by_type(
                self.root_set, entity_type)

    def __set_dagmc_tags(self):
        """Get a dictionary with the important tags for DAGMC geometries

        inputs
        ------
        none

        outputs
        -------
        dagmc_tags : a dictionary of relevant tags
        """
        tag_data_list = {'geom_dim': {'name': 'GEOM_DIMENSION', 'size': 1, 'type': types.MB_TYPE_INTEGER},
                         'category': {'name': 'CATEGORY', 'size': 32, 'type': types.MB_TYPE_OPAQUE},
                         'global_id': {'name': 'GLOBAL_ID', 'size': 1, 'type': types.MB_TYPE_INTEGER}
                         }

        for key, tag_data in tag_data_list.items():
            self.dagmc_tags[key] = self._my_moab_core.tag_get_handle(tag_data['name'],
                                                                size=tag_data['size'],
                                                                tag_type=tag_data['type'],
                                                                storage_type=types.MB_TAG_SPARSE,
                                                                create_if_missing=False)
