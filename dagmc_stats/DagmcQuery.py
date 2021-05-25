class DagmcQuery:
    def __init__(self):
        pass
    
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
