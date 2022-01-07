import pandas as pd
import numpy as np
from pymoab.rng import Range
from pymoab import core, types
import warnings


class DagmcFile:

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
        self.entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
        self.entityset_types = {0: 'nodes',
                                1: 'curves', 2: 'surfaces', 3: 'volumes'}
        self.native_ranges = {}
        self.__set_native_ranges()
        self.dagmc_tags = {}
        self.__set_dagmc_tags()
        self.entityset_ranges = {}
        self.__set_entityset_ranges()
        self.dim_dict = {}
        self.__set_dimension_meshset()

        # if populate is True:
        #    self.__populate_triangle_data(meshset)

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
                list(self._my_moab_core.get_entities_by_type_and_tag(self.root_set, types.MBENTITYSET,
                                                                self.dagmc_tags['geom_dim'], [dimension]))

    def __set_dimension_meshset(self):
        """Set the class dim_dict variable to a dictionary with the
        meshset for each dimension

        inputs
        ------
        none

        outputs
        -------
        none
        """
        for set_type, entityset_range in self.entityset_ranges.items():
            dim_ms = self._my_moab_core.create_meshset()
            self._my_moab_core.add_entity(dim_ms, entityset_range)
            self.dim_dict[set_type] = dim_ms

    def get_meshset_by_id(self, dim, ids=[]):
        """Get meshset of the geometry with specified dimension and ids

        inputs
        ------
        dim : (Integer or String) Dimension of the meshset. 0: 'node(s)',
                                1: 'curve(s)', 2: 'surface(s)', 3: 'volume(s)'
        ids : (Integer) Global ID(s) of the meshset

        outputs
        -------
        meshset : meshset of the geometry with given dimension and ids. First,
                  dim will be checked. If dim is invalid, the root set will be
                  returned. Then, if id is empty, all entities with the given
                  dim will be returned. If is is not in the given dim range),
                  an empty list will be returned.
        """
        plural_names = list(self.entityset_types.values())
        sing_names = [name[:-1] for name in plural_names]
        all_names = plural_names + sing_names

        if isinstance(dim, int) and dim in self.entityset_types.keys():
            dim = self.entityset_types[dim]
        elif type(dim) == str and dim.lower() in all_names:
            dim = dim.lower()
            if dim[-1] != 's':
                dim = dim + 's'
        else:
            # invalid dim
            warnings.warn('Invalid dim!')
            return []

        # if no id is passed in
        if len(ids) == 0:
            return self.entityset_ranges[dim]

        meshset = []
        for id in ids:
            meshset.extend(self._my_moab_core.get_entities_by_type_and_tag(self.dim_dict[dim],
                                                                           types.MBENTITYSET, self.dagmc_tags['global_id'], [id]))
        # if id is not in the given dim range
        if not meshset:
            warnings.warn(
                'ID is not in the given dimension range! ' +
                'Empty list will be returned.')
        return meshset
