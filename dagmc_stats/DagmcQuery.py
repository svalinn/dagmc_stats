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
        if self._vert_data.empty:
            self._vert_data = self._vert_data.append(t_p_v_data)
        else:
            self._vert_data.set_index('vert_eh').join(
                self._vert_data.append(t_p_v_data).set_index('vert_eh'))
