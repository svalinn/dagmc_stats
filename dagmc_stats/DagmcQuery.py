from pymoab.rng import Range
from pymoab import core, types
import pandas as pd
import numpy as np
import warnings


class DagmcQuery:
    def __init__(self, dagmc_file, meshset=None):
        """This class provides the functionality for making queries about
        various metrics for the meshset(s) of interest.

        inputs
        ------
            dagmc_file : DagmcFile instance
            meshset: the meshset on which query will be performed.
                The rootset will be used by default.

        outputs
        -------
            none
        """
        self.dagmc_file = dagmc_file
        self.meshset_lst = []
        if meshset is None:
            self.meshset_lst =  self.dagmc_file.entityset_ranges['surfaces']
        else:
            self.__get_entities(meshset)
        self.__get_tris()
        self.__get_verts()
        # initialize data frames
        self._vert_data = pd.DataFrame()
        self._tri_data = pd.DataFrame()
        self._surf_data = pd.DataFrame()
        self._vol_data = pd.DataFrame()
        self._tri_vert_data = []

        # dictionary for storing global (across the meshset list) of
        # the metrics calculated
        self._global_averages = {}

    def __get_entities(self, meshset):
        """convert the list of meshsets to its corresponding list of surfaces

        inputs
        ------
            meshset: the list of meshsets on which query will be performed.

        outputs
        -------
            none
        """
        # allow mixed list of surfaces and volumes that create a
        # single list of all the surfaces together
        if type(meshset) != list:
            # convert single item to list for iterating
            meshset = [meshset]
        for m in meshset:
            dim = self.dagmc_file._my_moab_core.tag_get_data(
                self.dagmc_file.dagmc_tags['geom_dim'], m)[0][0]
            # get surfaces of a volume
            if dim == 3:
                surfs = self.dagmc_file._my_moab_core.get_child_meshsets(
                    m)
                self.meshset_lst.extend(surfs)
            # get surface
            elif dim == 2:
                self.meshset_lst.append(m)
            else:
                warnings.warn('Meshset is not a volume nor a surface!')

        self.meshset_lst = list(set(self.meshset_lst))
        # if no items in the meshset list is a surface or volume,
        # then use rootset by default instead
        if len(self.meshset_lst) == 0:
            warnings.warn('Specified meshset(s) are not surfaces or ' +
                            'volumes. Rootset will be used by default.')
            self.meshset_lst = self.dagmc_file.entityset_ranges['surfaces']

    def __get_tris(self):
        """Get triangles of a volume if geom_dim is 3
        Get triangles of a surface if geom_dim is 2
        Else get all the triangles

        inputs
        ------
            none

        outputs
        -------
            tris : a list of triangle entities
        """
        tris_lst = []
        for meshset in self.meshset_lst:
            tris = self.dagmc_file._my_moab_core.get_entities_by_type(
                meshset, types.MBTRI)
            tris_lst.extend(tris)
        self.tris = tris_lst

    def __get_verts(self):
        """Get vertices of a volume if geom_dim is 3
        Get vertices of a surface if geom_dim is 2
        Else get all the vertices

        inputs
        ------
            none

        outputs
        -------
            verts : a list of vertex entities
        """
        verts = set()
        for item in self.meshset_lst:
            verts.update(self.dagmc_file._my_moab_core.get_entities_by_type(
                item, types.MBVERTEX))
        self.verts = list(verts)

    def get_tri_side_length(self, tri):
        """Get side lengths of triangle

        inputs
        ------
            tri : triangle entity

        outputs
        -------
            side_lengths : a dictionary that stores
                vert: the opposite side length of the vert as key-value pair
        """

        side_lengths = {}
        s = 0
        coord_list = []

        verts = list(self.dagmc_file._my_moab_core.get_adjacencies(tri, 0))

        for vert in verts:
            coords = self.dagmc_file._my_moab_core.get_coords(vert)
            coord_list.append(coords)

        for side in range(3):
            side_lengths.update({verts[side - 1]:
                                 np.linalg.norm(coord_list[side] -
                                                coord_list[side - 2])})
            # Although it may not be intuitive, the indexing of these lists
            # takes advantage of python's indexing syntax to rotate through
            # the `verts` of the triangle while simultaneously referencing the
            # side opposite each of the `verts` by the coordinates of the
            # vertices that define that side:
            #    side       side-1   index(side-1)     side-2   index(side-2)
            #     0           -1           2             -2             1
            #     1            0           0             -1             2
            #     2            1           1              0             0
        return side_lengths

    def calc_tris_per_vert(self, ignore_zero=True):
        """calculate triangle per vertex data

        inputs
        ------
            ignore_zero : (boolean) whether or not to ignore zero
                tris_per_vert values

        outputs
        -------
            none
        """
        if 'tri_per_vert' in self._vert_data:
            warnings.warn('Tri_per_vert already exists. ' +
                          'tris_per_vert() will not be called.')
            return
        t_p_v_data = []
        tri_dimension = 2
        for vert in self.verts:
            tpv_val = self.dagmc_file._my_moab_core.get_adjacencies(
                vert, tri_dimension).size()
            if ignore_zero and tpv_val == 0:
                continue
            row_data = {'vert_eh': vert, 'tri_per_vert': tpv_val}
            t_p_v_data.append(row_data)
        self.__update_vert_data(t_p_v_data)
        
    def calc_tris_per_surf(self):
        """calculate triangle per surface data

        inputs
        ------
            none

        outputs
        -------
            none
        """
        if 'tri_per_surf' in self._surf_data:
            warnings.warn('Tri_per_surf already exists. ' +
                          'tris_per_surf() will not be called.')
            return
        t_p_s_data = []
        for surf in self.meshset_lst:
            num_tris = self.dagmc_file._my_moab_core.get_entities_by_type(
                surf, types.MBTRI).size()
            row_data = {'surf_eh': surf, 'tri_per_surf': num_tris}
            t_p_s_data.append(row_data)
        self.__update_surf_data(t_p_s_data)

    def __update_vert_data(self, new_data):
        """Update _vert_data dataframe

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
        """Update _tri_data dataframe

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
        """Update _surf_data dataframe

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
        """Calculate triangle aspect ratio data (according to the equation:
        (abc)/(8(s-a)(s-b)(s-c)), where s = .5(a+b+c).)

        inputs
        ------
            none

        outputs
        -------
            none
        """
        if 'aspect_ratio' in self._tri_data:
            warnings.warn('Triangle aspect ratio already exists. ' +
                          'Calc_triangle_aspect_ratio() will not be called.')
            return
        t_a_r_data = []
        for tri in self.tris:
            side_lengths = list(self.get_tri_side_length(tri).values())
            s = 0.5 * (sum(side_lengths))
            top = np.prod(side_lengths)
            bottom = 8 * np.prod(s - side_lengths)
            t_a_r = top / bottom
            row_data = {'tri_eh': tri, 'aspect_ratio': t_a_r}
            t_a_r_data.append(row_data)
        self.__update_tri_data(t_a_r_data)

    def calc_area_triangle(self):
        """Calculate the triangle area data (according to the Heron's formula:
        sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2)

        inputs
        ------
            none

        outputs
        -------
            none
        """
        if 'area' in self._tri_data:
            warnings.warn('Triangle area already exists. ' +
                          'Calc_area_triangle() will not be called.')
            return
        tri_area = []
        for tri in self.tris:
            side_lengths = list(self.get_tri_side_length(tri).values())
            # sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2
            s = sum(side_lengths)/2
            s = np.sqrt(s * np.prod(s - side_lengths))
            row_data = {'tri_eh': tri, 'area': s}
            tri_area.append(row_data)
        self.__update_tri_data(tri_area)

    def calc_coarseness(self):
        """
        Calculate the density of facets on a surface (num tris / total area)

        inputs
        ------
            none

        outputs
        -------
            none
        """
        if 'coarseness' in self._surf_data:
            warnings.warn('Coarseness already exists. ' +
                          'Calc_coarseness() will not be called.')
            return

        coarseness = []
        surf_area = []
        self.calc_area_triangle()
        for surf in self.meshset_lst:
            tris = self.dagmc_file._my_moab_core.get_entities_by_type(
                surf, types.MBTRI)
            area = self._tri_data.loc[self._tri_data['tri_eh'].isin(
                list(tris)), 'area'].sum()
            cval = len(tris) / area
            row_data = {'surf_eh': surf, 'coarseness': cval}
            area_data = {'surf_eh': surf, 'area': area}
            coarseness.append(row_data)
            surf_area.append(area_data)
        self.__update_surf_data(coarseness)
        self.__update_surf_data(surf_area)

        weighted_coarseness = (self._surf_data['coarseness'] * self._surf_data['area']).sum()
        total_area = self._surf_data['area'].sum()
        average_coarseness = weighted_coarseness / total_area
        self._global_averages['coarseness_ave'] = average_coarseness

    def __get_tri_vert_data(self):
        """Build a numpy structured array to store triangle and vertex related
        data in the form of triangle entity handle | vertex entity handle
        | angle connected to the vertex | side length of side opposite to
        vertex in the triangle

        inputs
        ------
        none

        outputs
        -------
        none
        """
        tri_vert_struct = np.dtype({
            'names': ['tri', 'vert', 'angle', 'side_length'],
            'formats': [np.uint64, np.uint64, np.float64, np.float64]})
        self._tri_vert_data = np.zeros(len(self.tris) * 3, dtype=tri_vert_struct)
        tri_vert_index = 0

        for tri in self.tris:
            side_lengths = self.get_tri_side_length(tri)  # {vert: side_length}
            side_length_sum_sq_half = sum(map(lambda i: i**2,
                                          side_lengths.values())) / 2.
            side_length_prod = np.prod(list(side_lengths.values()))
            verts = side_lengths.keys()
            for vert_i in verts:
                side_i = side_lengths[vert_i]
                d_i = np.arccos((side_length_sum_sq_half -
                                (side_i**2)) * side_i / side_length_prod)
                tri_vert_entry = np.array((tri, vert_i, d_i, side_i),
                               dtype=tri_vert_struct)
                self._tri_vert_data[tri_vert_index] = tri_vert_entry
                tri_vert_index += 1

    def __gaussian_curvature(self, vert_i):
        """Get gaussian curvature value of a vertex
        Reference: https://www.sciencedirect.com/science/article/pii/
        S0097849312001203
        Formula 1

        inputs
        ------
            vert_i : vertex entity handle

        outputs
        -------
            gc : gaussian curvature value of the vertex
        """
        vert_entries = self._tri_vert_data[self._tri_vert_data['vert'] == vert_i]
        sum_alpha_angles = sum(vert_entries['angle'])
        gc = np.abs(2 * np.pi - sum_alpha_angles)
        return gc

    def __get_lri(self, vert_i, gc_all):
        """Get local roughness value of a vertex
        Reference: https://www.sciencedirect.com/science/article/pii/
        S0097849312001203
        Formula 2, 3

        inputs
        ------
            vert_i : vertex entity handle
            gc_all : dictionary in the form of vertex : gaussian curvature
                value of the vertex

        outputs
        -------
            Lri : local roughness value of the vertex
        """
        DIJgc_sum = 0
        Dii_sum = 0
        adj_tris = self.dagmc_file._my_moab_core.get_adjacencies(
                vert_i, 2, op_type=0)
        adj_tris = list(set(adj_tris) & set(self.tris))
        vert_j_list = list(self.dagmc_file._my_moab_core.get_adjacencies(
            adj_tris, 0, op_type=1))
        vert_j_list.remove(vert_i)
        for vert_j in vert_j_list:
            # get tri_ij_list (the list of the two triangles connected to both
            # vert_i and vert_j)
            tri_j_list = self.dagmc_file._my_moab_core.get_adjacencies(
                vert_j, 2, op_type=0)
            tri_ij_list = list(set(adj_tris) & set(tri_j_list))
            # rows with tri value as tri_ij_list[0] or tri_ij_list[1]
            select_tris = (self._tri_vert_data['tri'] == tri_ij_list[0]) | \
                          (self._tri_vert_data['tri'] == tri_ij_list[-1])
            # rows with vert value not equal to vert_i and not equal to vert_j
            vert_filter = (self._tri_vert_data['vert'] != vert_i) & \
                            (self._tri_vert_data['vert'] != vert_j)
            beta_angles = self._tri_vert_data[select_tris & vert_filter]['angle']
            Dij = 0.5 * (1. / np.tan(beta_angles[0]) +
                         1. / np.tan(beta_angles[-1]))
            DIJgc_sum += (Dij * gc_all[vert_j])
            Dii_sum += Dij
        Lri = abs(gc_all[vert_i] - DIJgc_sum / Dii_sum)
        return Lri

    def __calc_average_roughness(self):
        """Calculate global average roughness using equation 5 of reference
        below and update the global averages dictionary.

        https://www.sciencedirect.com/science/article/pii/S0097849312001203

        inputs
        ------
            none

        outputs
        -------
            none
        """
        self.calc_area_triangle()  # get area data if not already calculated
        vert_area = []
        for vert in self.verts:
            # get adjacent triangles and their areas
            tris = self.dagmc_file._my_moab_core.get_adjacencies(
                vert, 2, op_type=0)
            area_sum = self._tri_data.loc[
                self._tri_data['tri_eh'].isin(tris)]['area'].sum()
            row_data = {'vert_eh': vert, 'area': area_sum}
            vert_area.append(row_data)
        self.__update_vert_data(vert_area)
        
        # si = 1/3 of total area of adjacent triangles
        # sum of denominator
        si_total = (self._vert_data['area'].sum())/3.0
        # sum of numerator
        lri_si_total = (self._vert_data['area']/3.0 * self._vert_data['roughness']).sum()
        # calc average according to formula 5
        average_roughness = lri_si_total / si_total

        # update global average dictionary
        self._global_averages['roughness_ave'] = average_roughness

    def calc_roughness(self):
        """Calculate local roughness values of all the non-isolated vertices
        and calculates the average roughness for each surface of the meshset
        list and the average of the entire meshset list.

        reference:
        https://www.sciencedirect.com/science/article/pii/S0097849312001203

        inputs
        ------
            none

        outputs
        -------
            none
        """
        self.__get_tri_vert_data()
        gc_all = {}
        for vert_i in self.verts:
            gc_all[vert_i] = self.__gaussian_curvature(vert_i)
        roughness_per_vert = []
        for vert in self.verts:
            rval = self.__get_lri(vert, gc_all)
            row_data = {'vert_eh': vert, 'roughness': rval}
            roughness_per_vert.append(row_data)
        self.__update_vert_data(roughness_per_vert)

        # calculate average for meshset list
        self.__calc_average_roughness()
        
        # calculate triangle average roughness
        self.__calc_tri_roughness()
        
    def __calc_tri_roughness(self):
        """Calculate triangle average roughness by averaging roughness values
        of the triangle vertices.

        inputs
        ------
            none

        outputs
        -------
            none
        """
        tri_roughness = []
        for tri in self.tris:
            three_verts = list(self.dagmc_file._my_moab_core.get_adjacencies(tri, 0, op_type=1))
            sum_lr = self._vert_data.loc[
                self._vert_data['vert_eh'].isin(three_verts)]['roughness'].sum()
            rval = sum_lr/3.0
            row_data = {'tri_eh': tri, 'roughness': rval}
            tri_roughness.append(row_data)
        self.__update_tri_data(tri_roughness)
