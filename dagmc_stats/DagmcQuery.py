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
            self.meshset_lst.append(self.dagmc_file.root_set)
        else:
            self.__get_entities(meshset)
        # initialize data frames
        self._vert_data = pd.DataFrame()
        self._tri_data = pd.DataFrame()
        self._surf_data = pd.DataFrame()
        self._vol_data = pd.DataFrame()

        # dictionary for storing global (across the meshset list) of
        # the metrics calculated
        self._global_averages = {}

    def __get_entities(self, meshset):
        if meshset is None or meshset is self.dagmc_file.root_set:
            self.meshset_lst.append(self.dagmc_file.root_set)
        else:
            # allow mixed list of surfaces and volumes that create a
            # single list of all the surfaces together
            if type(meshset) != list:
                # convert single item to list for iterating
                meshset = [meshset]
            for m in meshset:
                dim = self.dagmc_file._my_moab_core.tag_get_data(
                    self.dagmc_file.dagmc_tags['geom_dim'], m)[0][0]
                # get triangles of a volume
                if dim == 3:
                    surfs = self.dagmc_file._my_moab_core.get_child_meshsets(
                        m)
                    self.meshset_lst.extend(surfs)
                # get triangles of a surface
                elif dim == 2:
                    self.meshset_lst.append(m)
                else:
                    warnings.warn('Meshset is not a volume nor a surface!')

            # if no items in the meshset list is a surface or volume,
            # then use rootset by default instead
            if len(self.meshset_lst) == 0:
                warnings.warn('Specified meshset(s) are not surfaces or ' +
                              'volumes. Rootset will be used by default.')
                self.meshset_lst.append(self.dagmc_file.root_set)

    def get_tris(self):
        """Get triangles of a volume if geom_dim is 3
        Get triangles of a surface if geom_dim is 2
        Else get all the triangles

        inputs
        ------
            meshset : set of entities that are used to populate data.
                Default value is None and data of the whole geometry will
                be populated.

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

    def get_verts(self):
        """Get vertices of a volume if geom_dim is 3
        Get vertices of a surface if geom_dim is 2
        Else get all the vertices

        inputs
        ------
            meshset : set of entities that are used to populate data.
                Default value is None and data of the whole geometry will
                be populated.

        outputs
        -------
            verts : a list of vertex entities
        """
        verts = []
        for item in self.meshset_lst:
            verts.extend(self.dagmc_file._my_moab_core.get_entities_by_type(
                item, types.MBVERTEX))
        verts = list(set(verts))
        return verts

    def get_surfs(self):
        """Get all surfaces in the query object. If rootset or volume, get all
        surfs in the rootset or volume. If query is already a surface, return
        the meshset list

        inputs
        ------
            meshset : set of entities that are used to populate data.
                Default value is None and data of the whole geometry will
                be populated.

        outputs
        -------
            surfs : a list of surface entities
        """
        surfs = []
        if self.meshset_lst == [self.dagmc_file.root_set]:
            surfs = self.dagmc_file.entityset_ranges['surfaces']
        else:
            surfs = self.meshset_lst
        return surfs

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
        verts = self.get_verts()
        for vert in verts:
            tpv_val = self.dagmc_file._my_moab_core.get_adjacencies(
                vert, tri_dimension).size()
            if ignore_zero and tpv_val == 0:
                continue
            row_data = {'vert_eh': vert, 'tri_per_vert': tpv_val}
            t_p_v_data.append(row_data)
        self.__update_vert_data(t_p_v_data)

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
        tris = self.get_tris()
        for tri in tris:
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
            warnings.warn('Coarseness already exists. ' +
                          'Calc_coarseness() will not be called.')
            return

        coarseness = []
        surfs = self.get_surfs()
        self.calc_area_triangle()
        total_area = 0.
        weighted_coarseness = 0.  # surf coarseness * surf area
        for surf in surfs:
            tris = self.dagmc_file._my_moab_core.get_entities_by_type(
                surf, types.MBTRI)
            area = self._tri_data.loc[self._tri_data['tri_eh'].isin(
                list(tris)), 'area'].sum()
            cval = len(tris) / area
            row_data = {'surf_eh': surf, 'coarseness': cval}
            coarseness.append(row_data)
            total_area += area
            weighted_coarseness += cval * area
        self.__update_surf_data(coarseness)

        # calculate weighted average
        # = sum(coarseness_i * area_i) / sum(area_i), i = surface
        average_coarseness = weighted_coarseness / total_area
        self._global_averages['coarseness_ave'] = average_coarseness

    def __get_tri_vert_data(self):
        """Build a numpy strcutured array to store triangle and vertex related
        data in the form of triangle entity handle | vertex entity handle
        | angle connected to the vertex | side length of side opposite to
        vertex in the triangle

        inputs
        ------
        none

        outputs
        -------
        tri_vert_data : a numpy structured array that stores the triangle
            and vertex related data
        all_verts : (list) all the vertices that are connected to
            triangle in the geometry
        """
        all_verts = set()
        tri_vert_struct = np.dtype({
            'names': ['tri', 'vert', 'angle', 'side_length'],
            'formats': [np.uint64, np.uint64, np.float64, np.float64]})
        tris = self.get_tris()
        tri_vert_data = np.zeros(len(tris) * 3, dtype=tri_vert_struct)
        tri_vert_index = 0

        for tri in tris:
            side_lengths = self.get_tri_side_length(tri)  # {vert: side_length}
            side_length_sum_sq_half = sum(map(lambda i: i**2,
                                          side_lengths.values())) / 2.
            side_length_prod = np.prod(list(side_lengths.values()))
            verts = list(self.dagmc_file._my_moab_core.get_adjacencies(
                tri, 0, op_type=1))
            for vert_i in verts:
                all_verts.add(vert_i)
                side_i = side_lengths[vert_i]
                d_i = np.arccos((side_length_sum_sq_half -
                                (side_i**2)) * side_i / side_length_prod)
                bar = np.array((tri, vert_i, d_i, side_i),
                               dtype=tri_vert_struct)
                tri_vert_data[tri_vert_index] = bar
                tri_vert_index += 1
        return tri_vert_data, list(all_verts)

    def __calc_gaussian_curvature(self, tri_vert_data):
        """Get gaussian curvature values of all non-isolated vertices

        inputs
        ------
        tri_vert_data : numpy structured array that stores the triangle and
        vertex related data

        outputs
        -------
        gc_all : dictionary in the form of vertex : gaussian curvature value
        of the vertex
        """
        verts = self.get_verts()
        gc_all = {}
        for vert_i in verts:
            gc_all[vert_i] = self.__gaussian_curvature(vert_i, tri_vert_data)
        return gc_all

    def __gaussian_curvature(self, vert_i, tri_vert_data):
        """Get gaussian curvature value of a vertex
        Reference: https://www.sciencedirect.com/science/article/pii/
        S0097849312001203
        Formula 1

        inputs
        ------
            vert_i : vertex entity handle
            tri_vert_data : numpy structured array that stores the
            triangle and vertex related data

        outputs
        -------
            gc : gaussian curvature value of the vertex
        """
        vert_entries = tri_vert_data[tri_vert_data['vert'] == vert_i]
        sum_alpha_angles = sum(vert_entries['angle'])
        gc = np.abs(2 * np.pi - sum_alpha_angles)
        return gc

    def __get_lri(self, vert_i, gc_all, tri_vert_data):
        """Get local roughness value of a vertex
        Reference: https://www.sciencedirect.com/science/article/pii/
        S0097849312001203
        Formula 2, 3

        inputs
        ------
            vert_i : vertex entity handle
            gc_all : dictionary in the form of vertex : gaussian curvature
                value of the vertex
            tri_vert_data : numpy structured array that stores the triangle
                and vertex related data

        outputs
        -------
            Lri : local roughness value of the vertex
        """
        DIJgc_sum = 0
        Dii_sum = 0
        vert_j_list = list(self.dagmc_file._my_moab_core.get_adjacencies(
            self.dagmc_file._my_moab_core.get_adjacencies(
                vert_i, 2, op_type=0), 0, op_type=1))
        vert_j_list.remove(vert_i)
        for vert_j in vert_j_list:
            # get tri_ij_list (the list of the two triangles connected to both
            # vert_i and vert_j)
            tri_i_list = self.dagmc_file._my_moab_core.get_adjacencies(
                vert_i, 2, op_type=0)
            tri_j_list = self.dagmc_file._my_moab_core.get_adjacencies(
                vert_j, 2, op_type=0)
            tri_ij_list = list(set(tri_i_list) & set(tri_j_list))
            # rows with tri value as tri_ij_list[0] or tri_ij_list[1]
            select_tris = (tri_vert_data['tri'] == tri_ij_list[0]) | \
                          (tri_vert_data['tri'] == tri_ij_list[1])
            # rows with vert value not equal to vert_i and not equal to vert_j
            exclude_verts = (tri_vert_data['vert'] != vert_i) & \
                            (tri_vert_data['vert'] != vert_j)
            beta_angles = tri_vert_data[select_tris & exclude_verts]['angle']
            Dij = 0.5 * (1. / np.tan(beta_angles[0]) +
                         1. / np.tan(beta_angles[1]))
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
        verts = self.get_verts()
        self.calc_area_triangle()  # get area data if not already calculated
        si_total = 0.  # sum of denominator
        lri_si_total = 0.  # sum of numerator
        for vert in verts:
            # get adjacent triangles and their areas
            tris = self.dagmc_file._my_moab_core.get_adjacencies(
                vert, 2, op_type=0)
            area_sum = self._tri_data.loc[
                self._tri_data['tri_eh'].isin(tris)]['area'].sum()

            # si = 1/3 of total area of adjacent triangles
            si = area_sum / 3.
            si_total += si

            # calculate numerator (lri*si)
            lri_si = float(self._vert_data.loc[
                self._vert_data['vert_eh'] == vert]['roughness']) * si
            lri_si_total += lri_si

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
        tri_vert_data, all_verts = self.__get_tri_vert_data()
        verts = self.get_verts()
        gc_all = self.__calc_gaussian_curvature(tri_vert_data)
        roughness_per_vert = []
        for vert in verts:
            rval = self.__get_lri(vert, gc_all, tri_vert_data)
            row_data = {'vert_eh': vert, 'roughness': rval}
            roughness_per_vert.append(row_data)
        self.__update_vert_data(roughness_per_vert)

        # calculate average for meshset list
        self.__calc_average_roughness()
