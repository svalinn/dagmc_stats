import pandas as pd
import numpy as np
from pymoab.rng import Range
from pymoab import core, types


class DagmcStats:

    tri_vert_struct = np.dtype({'names': ['tri', 'vert', 'angle', 'side_length'],
                                'formats': [np.uint64, np.uint64, np.float64, np.float64]})

    def __init__(self, filename, populate=False):
        # read file
        self._my_moab_core = core.Core()
        self._my_moab_core.load_file(filename)
        self.root_set = self._my_moab_core.get_root_set()
        entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]

        # some metadata
        self.native_ranges = get_native_ranges(root_set, entity_types)
        self.dagmc_tags = get_dagmc_tags()
        self.entityset_ranges = get_entityset_ranges(
            root_set, dagmc_tags['geom_dim'])

        # initialize data frames
        self._vert_data = pd.DataFrame(
            columns=['vert_eh', 'roughness', 'tri_per_vert'], index='vert_eh')
        self._tri_data = pd.DataFrame(
            columns=['tri_eh', 'aspect_ratio', 'area'], index='tri_eh')
        self._surface_data = pd.DataFrame(
            columns=['surf_eh', 'tri_per_surf', 'coarseness'], index='surf_eh')
        self._volume_data = pd.DataFrame(
            columns=['volume', 'surf_per_vol', 'coarseness'], index='volume')

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

    # Todo: more documentation for dictionary
    def get_native_ranges(meshset, entity_types):
        """Get a dictionary with MOAB ranges for each of the requested entity types

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

    def get_dagmc_tags(self):
        """Get a dictionary with the important tags for DAGMC geometries

        inputs
        ------
        none

        outputs
        -------
        dagmc_tags : a dictionary of relevant tags
        """
        tag_data_list = {'geom_dim': {'name': 'GEOM_DIMENSION', 'size': 1, 'type': types.MB_TYPE_INTEGER},
                         'category': {'name': 'CATEGORY', 'size': 32, 'type': types.MB_OPAQUE},
                         'global_id': {'name': 'GLOBAL_ID', 'size': 1, 'type': types.MB_TYPE_INTEGER}
                         }

        for key, tag_data in tag_data_list:
            dagmc_tags[key] = self._my_moab_core.tag_get_handle(tag_data['name'],
                                                                size=tag_data['size'],
                                                                tag_type=tag_data['type'],
                                                                storage_type=types.MB_TAG_SPARSE,
                                                                create_if_missing=True)
        return dagmc_tags

    def populate_triangle_data(self, meshset=None, aspect_ratio=True, area=True):
        """Populate triangle areas and triangle aspect ratios
        inputs
        ------
        meshset : set of entities that are used to populate data. Default value
                  is None and data of the whole geometry will be populated.
        aspect_ratio : boolean value that determines whether or not to populate
                  triangle aspect ratio values. Default value is True.
        area : boolean value that determines whether or not to populate
                  triangle area values. Default value is True.

        outputs
        -------
        none
        """
        tris = get_tris(meshset)
        df_tri['tri_eh'] = tris

        for tri in tris:
            tri_data_row = {'entity_handle': tri}
            side_lengths = list(get_tri_side_length(tri).values())
            s = .5*(sum(side_lengths))
            p = np.prod(s - side_lengths)
            if area:
                # sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2
                tri_data_row['area'] = np.sqrt(s * p)
            if aspect_ratio:
                tri_data_row['aspect_ratio'] = np.prod(side_lengths) / (8 * p)
        df_tri = df_tri.append(tri_data_row, ignore_index=True)
        return

    # Todo
    def get_tris(self, meshset):
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
        dim = _my_moab_core.tag_get_data(dagmc_tags['geom_dim'], meshset)[0][0]
        # get triangles of a volume or a surface
        if dim == 3 or dim == 2:
            tris = _my_moab_core.get_entities_by_type(meshset, types.MBTRI)
        else:
            # get all the triangles
            tris = _my_moab_core.get_entities_by_type(root_set, types.MBTRI)
        return tris

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
        coord_list = []

        verts = list(_my_moab_core.get_adjacencies(tri, 0))

        for vert in verts:
            coords = _my_moab_core.get_coords(vert)
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

    # overload this somehow: either optional parameters, or different names

    def query_triangle_area(self, tri):
        """Query triangle areas given triangle entity handles

        inputs
        ------
        tri : triangle entity handles

        outputs
        -------
        triangle areas that correspond to the given triangle entity handles
        """
        return self._tri_data.query('tri_eh == tri')

    def query_triangle_area_from_surf(self, surf):
        """
        query triangle areas given surface entity handles

        inputs
        ------
        surf : surface entity handles

        outputs
        -------
        triangle areas that correspond to the given surface entity handles
        """
        # gets the areas of the triangles that make up a single surface
        tris = get_tris(surf)
        return self._tri_data.query('surf_eh == @tris')
