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
        self._tri_data = pd.DataFrame(
            columns=['tri_eh', 'aspect_ratio', 'area'])
        self._surf_data = pd.DataFrame(
            columns=['surf_eh', 'tri_per_surf', 'coarseness'])
        self._vol_data = pd.DataFrame(
            columns=['vol_eh', 'surf_per_vol', 'coarseness'])

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
                self._my_moab_core.get_entities_by_type_and_tag(self.root_set, types.MBENTITYSET,
                                                                self.dagmc_tags['geom_dim'], [dimension])

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
        sing_names = [ name[:-1] for name in plural_names]
        all_names =  plural_names + sing_names

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
                'ID is not in the given dimension range! ' +\
                    'Empty list will be returned.')
        return meshset


'''
    def __populate_triangle_data(self, meshset):
        """Populate triangle areas and triangle aspect ratios

        inputs
        ------
        meshset : set of entities that are used to populate data. By default,
                  the root set will be used and data of the whole geometry will
                  be populated.

        outputs
        -------
        none
        """
        tris = self.get_tris(meshset)
        for tri in tris:
            if tri not in self._tri_data.tri_eh:
                tri_data_row = {'tri_eh': tri}
                side_lengths = list(self.get_tri_side_length(tri).values())
                s = .5*(sum(side_lengths))
                p = np.prod(s - side_lengths)
                # sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2
                tri_data_row['area'] = np.sqrt(s * p)
                tri_data_row['aspect_ratio'] = np.prod(side_lengths) / (8 * p)
                self._tri_data = self._tri_data.append(tri_data_row, ignore_index=True)
        return

    def get_tri_side_length(self, tri):
        """
        Get side lengths of triangle

        inputs
        ------
        tri : triangle entity

        outputs
        -------
        side_lengths : a dictionary that stores vert : the opposite side length of
        the vert as key-value pair
        """

        side_lengths = {}
        s = 0
        coord_list = []

        verts = list(self._my_moab_core.get_adjacencies(tri, 0))

        for vert in verts:
            coords = self._my_moab_core.get_coords(vert)
            coord_list.append(coords)

        for side in range(3):
            side_lengths.update({verts[side-1]:
                                 np.linalg.norm(coord_list[side] -
                                 coord_list[side-2])})
            # Although it may not be intuitive, the indexing of these lists takes
            # advantage of python's indexing syntax to rotate through
            # the `verts` of the triangle while simultaneously referencing the side
            # opposite each of the `verts` by the coordinates of the vertices that
            # define that side:
            #    side       side-1   index(side-1)     side-2   index(side-2)
            #     0           -1           2             -2             1
            #     1            0           0             -1             2
            #     2            1           1              0             0
        return side_lengths
'''
