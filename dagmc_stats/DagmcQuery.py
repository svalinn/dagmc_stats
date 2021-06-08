from pymoab.rng import Range
from pymoab import core, types
import warnings

class DagmcQuery:
    def __init__(self, dagmc_file, meshset=None):
        self.dagmc_file = dagmc_file
        self.meshset = meshset
    
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
