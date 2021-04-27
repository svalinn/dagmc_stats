import pandas as pd
import numpy as np
from pymoab.rng import Range
from pymoab import core, types
import warnings

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
        self.entityset_types = {0:'Nodes', 1:'Curves', 2:'Surfaces', 3:'Volumes'}
        self.native_ranges = {}
        self.__set_native_ranges()
        self.dagmc_tags = {}
        self.__set_dagmc_tags()
        self.entityset_ranges = {}
        self.__set_entityset_ranges()

    def __set_native_ranges(self):
        """Set the class native_ranges variable to a dictionary with MOAB
        ranges for each of the requested entity types

        inputs
        ------
        none

        outputs
        -------
        none
        """
        for entity_type in self.entity_types:
            self.native_ranges[entity_type] = self._my_moab_core.get_entities_by_type(
                self.root_set, entity_type)

    def __set_dagmc_tags(self):
        """Set the class dagmc_tags variable to a dictionary with the
        important tags for DAGMC geometries

        inputs
        ------
        none

        outputs
        -------
        none
        """
        tag_data_list = {'geom_dim': {'name': 'GEOM_DIMENSION',
                                      'size': 1,
                                      'type': types.MB_TYPE_INTEGER},
                         'category': {'name': 'CATEGORY',
                                      'size': 32,
                                      'type': types.MB_TYPE_OPAQUE},
                         'global_id': {'name': 'GLOBAL_ID',
                                       'size': 1,
                                       'type': types.MB_TYPE_INTEGER}}

        for key, tag_data in tag_data_list.items():
            self.dagmc_tags[key] = self._my_moab_core.tag_get_handle(tag_data['name'],
                                                                     size=tag_data['size'],
                                                                     tag_type=tag_data['type'],
                                                                     storage_type=types.MB_TAG_SPARSE,
                                                                     create_if_missing=False)

    def __set_entityset_ranges(self):
        """Set a dictionary with MOAB Ranges that are specific to the
        types.MBENTITYSET type

        inputs
        ------
        none

        outputs
        -------
        none
        """
        for dimension, set_type in self.entityset_types.items():
            self.entityset_ranges[set_type] = \
                self._my_moab_core.get_entities_by_type_and_tag(self.root_set, types.MBENTITYSET,
                                                                self.dagmc_tags['geom_dim'], [dimension])

    def get_tris(self, meshset=None):
        """Get triangles of a volume if geom_dim is 3
        Get triangles of a surface if geom_dim is 2
        Else get all the triangles

        inputs
        ------
        meshset : set of entities that are used to populate data. Default value
                  is None and data of the whole geometry will be populated.

        outputs
        -------
        tris : a list of triangle entities
        """
        meshset_lst = []
        tris_lst = []

        if meshset is None or meshset == self.root_set:
            meshset_lst.append(self.root_set)
        else:
            dim = self._my_moab_core.tag_get_data(self.dagmc_tags['geom_dim'], meshset)[0][0]
            # get triangles of a volume
            if dim == 3:
                surfs = self._my_moab_core.get_child_meshsets(meshset)
                meshset_lst.extend(surfs)
            # get triangles of a surface
            elif dim == 2:
                meshset_lst.append(meshset)
            else:
                warnings.warn('Meshset is not a volume nor a surface! Rootset will be used by default.')
                meshset_lst.append(self.root_set)

        for item in meshset_lst:
            tris = self._my_moab_core.get_entities_by_type(item, types.MBTRI)
            tris_lst.extend(tris)
        return tris
