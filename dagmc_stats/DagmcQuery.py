from pymoab.rng import Range
from pymoab import core, types
import pandas as pd
import numpy as np
import warnings


class DagmcQuery:
    def __init__(self, dagmc_file, meshset=None):
        """Constructor

        inputs
        ------
        dagmc_file : DagmcFile instance
        meshset: the meshset on which query will be performed. The rootset will be used by default.

        outputs
        -------
        none
        """
        self.dagmc_file = dagmc_file
        self.meshset_lst = []
        if meshset is None:
            self.meshset_lst.append(self.dagmc_file.root_set)
        else:
            self.__get_entities(meshset)
        # initialize data frames
        self._vert_data = pd.DataFrame()
        self._tri_data = pd.DataFrame()
        self._surf_data = pd.DataFrame()
        self._vol_data = pd.DataFrame()

    def __get_entities(self, meshset):
        if meshset is None or meshset == self.dagmc_file.root_set:
            self.meshset_lst.append(self.dagmc_file.root_set)
        else:
            dim = self.dagmc_file._my_moab_core.tag_get_data(
                self.dagmc_file.dagmc_tags['geom_dim'], meshset)[0][0]
            # get triangles of a volume
            if dim == 3:
                surfs = self.dagmc_file._my_moab_core.get_child_meshsets(
                    meshset)
                self.meshset_lst.extend(surfs)
            # get triangles of a surface
            elif dim == 2:
                self.meshset_lst.append(meshset)
            else:
                warnings.warn(
                    'Meshset is not a volume nor a surface! Rootset will be used by default.')
                self.meshset_lst.append(self.dagmc_file.root_set)

    def get_tris(self):
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
        tris_lst = []
        for meshset in self.meshset_lst:
            tris = self.dagmc_file._my_moab_core.get_entities_by_type(
                meshset, types.MBTRI)
            tris_lst.extend(tris)
        return tris_lst

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

        verts = list(self.dagmc_file._my_moab_core.get_adjacencies(tri, 0))

        for vert in verts:
            coords = self.dagmc_file._my_moab_core.get_coords(vert)
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

    def calc_tris_per_vert(self, ignore_zero=True):
        """
        calculate triangle per vertex data

        inputs
        ------
        ignore_zero : (boolean) whether or not to ignore zero tris_per_vert values

        outputs
        -------
        none
        """
        if 'tri_per_vert' in self._vert_data:
            warnings.warn(
                'Tri_per_vert already exists. tris_per_vert() will not be called.')
            return
        t_p_v_data = []
        tri_dimension = 2
        verts = []
        for item in self.meshset_lst:
            verts.extend(self.dagmc_file._my_moab_core.get_entities_by_type(
                item, types.MBVERTEX))
        verts = list(set(verts))
        for vert in verts:
            tpv_val = self.dagmc_file._my_moab_core.get_adjacencies(
                vert, tri_dimension).size()
            if ignore_zero and tpv_val == 0:
                continue
            row_data = {'vert_eh': vert, 'tri_per_vert': tpv_val}
            t_p_v_data.append(row_data)
        self.__update_vert_data(t_p_v_data)

    def __update_vert_data(self, new_data):
        """
        Update _vert_data dataframe

        inputs
        ------
        new_data : vert data to be added to the _vert_data dataframe

        outputs
        -------
        none
        """
        if self._vert_data.empty:
            self._vert_data = self._vert_data.append(new_data)
        else:
            self._vert_data = self._vert_data.merge(
                pd.DataFrame(new_data), on='vert_eh', how='left')

    def __update_tri_data(self, new_data):
        """
        Update _tri_data dataframe

        inputs
        ------
        new_data : triangle data to be added to the _tri_data dataframe

        outputs
        -------
        none
        """
        if self._tri_data.empty:
            self._tri_data = self._tri_data.append(new_data)
        else:
            self._tri_data = self._tri_data.merge(
                pd.DataFrame(new_data), on='tri_eh', how='left')
                
    def __update_surf_data(self, new_data):
        """
        Update _surf_data dataframe

        inputs
        ------
        new_data : surface data to be added to the _surf_data dataframe

        outputs
        -------
        none
        """
        if self._surf_data.empty:
            self._surf_data = self._surf_data.append(new_data)
        else:
            self._surf_data = self._surf_data.merge(
                pd.DataFrame(new_data), on='surf_eh', how='left')

    def calc_triangle_aspect_ratio(self):
        """
        Calculate triangle aspect ratio data (according to the equation:
        (abc)/(8(s-a)(s-b)(s-c)), where s = .5(a+b+c).)

        inputs
        ------
        none

        outputs
        -------
        none
        """
        if 'aspect_ratio' in self._tri_data:
            warnings.warn(
                'Triangle aspect ratio already exists. Calc_triangle_aspect_ratio() will not be called.')
            return
        t_a_r_data = []
        tris = self.get_tris()
        for tri in tris:
            side_lengths = list(self.get_tri_side_length(tri).values())
            s = .5*(sum(side_lengths))
            top = np.prod(side_lengths)
            bottom = 8*np.prod(s-side_lengths)
            t_a_r = top/bottom
            row_data = {'tri_eh': tri, 'aspect_ratio': t_a_r}
            t_a_r_data.append(row_data)
        self.__update_tri_data(t_a_r_data)

    def calc_area_triangle(self):
        """
        Calculate the triangle area data (according to the Heron's formula:
        sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2)

        inputs
        ------
        none

        outputs
        -------
        none
        """
        if 'area' in self._tri_data:
            warnings.warn(
                'Triangle area already exists. Calc_area_triangle() will not be called.')
            return
        tri_area = []
        tris = self.get_tris()
        for tri in tris:
            side_lengths = list(self.get_tri_side_length(tri).values())
            # sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2
            s = sum(side_lengths)/2
            s = np.sqrt(s * np.prod(s - side_lengths))
            row_data = {'tri_eh': tri, 'area': s}
            tri_area.append(row_data)
        self.__update_tri_data(tri_area)

    def calc_coarseness(self):
        """
        Calculate the surface coarseness data
        
        inputs
        ------
        none

        outputs
        -------
        none
        """
        if 'coarseness' in self._surf_data:
                warnings.warn(
                    'Coarseness already exists. Calc_coarseness() will not be called.')
                return
        coarseness = []
        surf_list = []
        if self.meshset_lst == [self.dagmc_file.root_set]:
            surf_list = self.dagmc_file.entityset['surfaces']
        else:
            surf_list = self.meshset_lst
        self.calc_area_triangle()
        for surf in surf_list:
            tris = self.dagmc_file._my_moab_core.get_entities_by_type(
                surf, types.MBTRI)
            row_data = {'surf_eh' : surf,
            'coarseness' : len(tris)/self._tri_data.loc[self._tri_data['tri_eh'].isin(list(tris)), 'area'].sum()}
            coarseness.append(row_data)
        self.__update_surf_data(coarseness)
