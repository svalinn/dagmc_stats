from pymoab.rng import Range
from pymoab import core, types
import pandas as pd
import numpy as np
import warnings

class DagmcQuery:
    def __init__(self, dagmc_file, meshset=None):
        self.dagmc_file = dagmc_file
        self.meshset = meshset
        # initialize data frames
        self._vert_data = pd.DataFrame()
        self._tri_data = pd.DataFrame()
        self._surf_data = pd.DataFrame()
        self._vol_data = pd.DataFrame()
    
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
        meshset_lst = []
        tris_lst = []

        if self.meshset is None or self.meshset == self.dagmc_file.root_set:
            meshset_lst.append(self.dagmc_file.root_set)
        else:
            dim = self.dagmc_file._my_moab_core.tag_get_data(self.dagmc_file.dagmc_tags['geom_dim'], self.meshset)[0][0]
            # get triangles of a volume
            if dim == 3:
                surfs = self.dagmc_file._my_moab_core.get_child_meshsets(self.meshset)
                meshset_lst.extend(surfs)
            # get triangles of a surface
            elif dim == 2:
                meshset_lst.append(self.meshset)
            else:
                warnings.warn('Meshset is not a volume nor a surface! Rootset will be used by default.')
                meshset_lst.append(self.dagmc_file.root_set)

        for item in meshset_lst:
            tris = self.dagmc_file._my_moab_core.get_entities_by_type(item, types.MBTRI)
            tris_lst.extend(tris)
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
        t_p_v_data = []
        tri_dimension = 2
        for vertex in self.dagmc_file.native_ranges[types.MBVERTEX]:
            tpv_val = self.dagmc_file._my_moab_core.get_adjacencies(vertex, tri_dimension).size()
            if ignore_zero and tpv_val == 0:
                continue
            row_data = {'vert_eh': vertex, 'tri_per_vert': tpv_val}
            t_p_v_data.append(row_data)
        if self._vert_data.empty:
            self._vert_data = self._vert_data.append(t_p_v_data)
        else:
            self._vert_data.set_index('vert_eh').join(self._vert_data.append(t_p_v_data).set_index('vert_eh'))

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
        t_a_r_data = []
        tris = get_tris()
        for tri in tris:
            side_lengths = list(get_tri_side_length(tri).values())
            s = .5*(sum(side_lengths))
            top = np.prod(side_lengths)
            bottom = 8*np.prod(s-side_lengths)
            t_a_r = top/bottom
            row_data = {'tri_eh': tri, 'aspect_ratio': t_a_r}
            t_a_r_data.append(row_data)
        if self._tri_data.empty:
            self._tri_data = self._tri_data.append(t_a_r_data)
        else:
            self._tri_data.set_index('tri_eh').join(self._tri_data.append(t_a_r_data).set_index('tri_eh'))

    def calc_area_triangle(self, tris=[]):
        """
        Calculate the triangle area data (according to the Heron's formula:
        sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2)

        inputs
        ------
        tris : (list) triangles whose area will be calculated. The default value is
        an empty list and will lead to calculation of all triangle areas in the
        geometry

        outputs
        -------
        none
        """
        tri_area = []
        if not tris:
            tris = get_tris()
        for tri in tris:
            side_lengths = list(get_tri_side_length(self.dagmc_file._my_moab_core, tri).values())
            # sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2
            s = sum(side_lengths)/2
            s = np.sqrt(s * np.prod(s - side_lengths))
            row_data = {'tri_eh': tri, 'area': s}
            tri_area.append(row_data)
        if self._tri_data.empty:
            self._tri_data = self._tri_data.append(tri_area)
        else:
            self._tri_data.set_index('tri_eh').join(self._tri_data.append(t_a_r_data).set_index('tri_eh'))