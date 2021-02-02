import pandas as pd
import numpy as np
from pymoab.rng import Range
from pymoab import core, types

class DagmcStats:

    tri_vert_struct = np.dtype({'names': ['tri', 'vert', 'angle',
    'side_length'], 'formats': [np.uint64, np.uint64, np.float64, np.float64]})


    def __init__(self, filename, populate=False):
        # read file
        self._my_moab_core = moab.load_file(...)
        my_core = core.Core()
        root_set = my_core.get_root_set()
        entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
        
        # some metadata
        self._native_ranges = get_native_ranges(my_core, root_set, entity_types) # TODO: is this still necessary?
        self.dagmc_tags = get_dagmc_tags(my_core)
        self.entityset_ranges = get_entityset_ranges(my_core, root_set,
                                                    dagmc_tags['geom_dim'])

        # initialize data frames
        self._vert_data = pd.DataFrame(columns = ['vert_eh', 'roughness','t_p_v'])
        self._tri_data = pd.DataFrame(columns = ['tri_eh', 't_a_r', 'tri_area'])
        self._surface_data = pd.DataFrame(columns = ['surf_eh', 't_p_s', 'coarseness'])
        self._volume_data = pd.DataFrame(columns = ['volume', 's_p_v', 'coarseness'])
        
        self._vert_data = df_vert.set_index('vert_eh')
        self._tri_data = df_tri.set_index('tri_eh')
        self._surface_data = df_surf.set_index('surf_eh')
        self._volume_data = df_volume.set_index('volume')
        
        # TODO: args
        tar_meshset = args.tar_meshset
        if tar_meshset == None:
            tar_meshset = root_set
        
        # TODO: default data to populate data frames??
        if populate:
            #  xxx
        return


    def get_native_ranges(my_core, meshset, entity_types):
        """
        Get a dictionary with MOAB ranges for each of the requested entity types

        inputs
        ------
        my_core : a MOAB Core instance
        meshset : a MOAB meshset to query for the ranges of entities
        entity_types : a list of valid pyMOAB types to be retrieved

        outputs
        -------
        native_ranges : a dictionary with one entry for each entity type that is a
                        Range of handles to that type
        """

        native_ranges = {}
        for entity_type in entity_types:
            native_ranges[entity_type] = my_core.get_entities_by_type(
                meshset, entity_type)
        return native_ranges


    def get_dagmc_tags:
        """
        Get a dictionary with the important tags for DAGMC geometries

        inputs
        ------
        my_core : a MOAB Core instance

        outputs
        -------
        dagmc_tags : a dictionary of relevant tags
        """

        dagmc_tags = {}
        # geometric dimension
        dagmc_tags['geom_dim'] = \
            my_core.tag_get_handle('GEOM_DIMENSION',
                                   size=1, tag_type=types.MB_TYPE_INTEGER,
                                   storage_type=types.MB_TAG_SPARSE,
                                   create_if_missing=True)
        # the category
        dagmc_tags['category'] = \
            my_core.tag_get_handle('CATEGORY',
                                   size=32,
                                   tag_type=types.MB_TYPE_OPAQUE,
                                   storage_type=types.MB_TAG_SPARSE,
                                   create_if_missing=True)
        # id
        dagmc_tags['global_id'] = \
            my_core.tag_get_handle('GLOBAL_ID',
                                   size=1,
                                   tag_type=types.MB_TYPE_INTEGER,
                                   storage_type=types.MB_TAG_SPARSE,
                                   create_if_missing=True)
        return dagmc_tags
    
    
    def populate_triangle_area(self, tris=[]):
        """
        populate the triangle areas
        """
        # TODO: my_core, tar_meshset, dagmc_tags['geom_dim']
        area = []
        if not tris:
            tris = get_tris(my_core, meshset, geom_dim)
        for tri in tris:
            side_lengths = list(get_tri_side_length(my_core, tri).values())
            # sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2
            s = sum(side_lengths)/2
            s = np.sqrt(s * np.prod(s - side_lengths))
            area.append(s)
        df_tri['tri_area'] = area
        return


    # overload this somehow: either optional parameters, or different names
    def query_triangle_area(self, tris):
        """
        query triangle areas given triangle entity handles
        """
        return self._tri_data.query('tri_eh == tris')


    def query_triangle_area_from_surf(self, surface):
        """
        query triangle areas given surface entity handles
        """
        # gets the areas of the triangles that make up a single surface
        return self._tri_data.query('surf_eh == surface')
        

    def get_tris(my_core, meshset, geom_dim):
        """
        Get triangles of a volume if geom_dim is 3
        Get triangles of a surface if geom_dim is 2
        Else get all the triangles

        inputs
        ------
        my_core : a MOAB core instance
        meshset : the root meshset for the file
        geom_dim : a MOAB Tag that holds the dimension of an entity.

        outputs
        -------
        tris : a list of triangle entities
        """

        # get triangles of a volume
        if my_core.tag_get_data(geom_dim, meshset)[0][0] == 3:
            entities = my_core.create_meshset()
            for surface in my_core.get_child_meshsets(meshset):
                my_core.add_entities(
                    entities, my_core.get_entities_by_type(surface, types.MBTRI))
            tris = my_core.get_entities_by_type(entities, types.MBTRI)
        # get triangles of a surface
        elif my_core.tag_get_data(geom_dim, meshset)[0][0] == 2:
            entities = my_core.create_meshset()
            my_core.add_entities(
                entities, my_core.get_entities_by_type(meshset, types.MBTRI))
            tris = my_core.get_entities_by_type(entities, types.MBTRI)
        else:
            # get all the triangles
            tris = my_core.get_entities_by_type(meshset, types.MBTRI)
        return tris
    
    
    def populate_triangle_aspect_ratio(self):
        """
        populate triangle aspect ratio
        """
        tris = get_tris(my_core, tar_meshset, dagmc_tags['geom_dim'])
        t_a_r = []

        for tri in tris:
            side_lengths = list(get_tri_side_length(my_core, tri).values())
            s = .5*(sum(side_lengths))
            top = np.prod(side_lengths)
            bottom = 8*np.prod(s-side_lengths)
            t_a_r.append(top/bottom)

        df_tri['t_a_r'] = t_a_r
        return


    def populate_vert_roughness(self):
        """
        populate roughness
        """
        tri_vert_data, all_verts = get_tri_vert_data(my_core,
                                                    native_ranges[types.MBTRI])
        if verts is None: # Todo: argument
            verts = all_verts
        gc_all = get_gaussian_curvature(my_core, all_verts, tri_vert_data)
        roughness = {}
        for vert_i in verts:
            roughness[vert_i] = get_lri(vert_i, gc_all, tri_vert_data, my_core)
        df_vert['roughness'] = roughness.values()
        # Todo: maybe roughness is better to be a list
        return
        
        
    def populate_triangle_per_vertex(self):
        """
        popoulate triangle per vertex
        """
        t_p_v_data = []
        tri_dimension = 2
        for vertex in native_ranges[types.MBVERTEX]:
            tpv_val = my_core.get_adjacencies(vertex, tri_dimension).size()
            if ignore_zero and tpv_val == 0:
                continue
            t_p_v_data.append(tpv_val)
        df_vert['t_p_v'] = np.array(t_p_v_data)
        return


    def populate_triangle_per_surface(self):
        """
        populate triangle per surface
        """
        t_p_s = {}
        for surface in entity_ranges['Surfaces']:
            t_p_s[surface] = my_core.get_entities_by_type(
                surface, types.MBTRI).size()
        df_surf['t_p_s'] = t_p_s.values()
        return
        
    
    def populate_surface_coarseness(self):
        """
        populate surface coarseness
        """
        coarseness = []
        for surface in entity_ranges['Surfaces']:
            surf_area = get_area_triangle(my_core, surface, dagmc_tags['geom_dim'])
            coarseness.append(len(surf_area)/sum(surf_area))
        df_surf['coarseness'] = coarseness
        return
    
    
    def populate_triangle_per_volume(self):
        """
        populate triangle per volume
        """
        s_p_v = {}
        for volumeset in entityset_ranges['Volumes']:
            s_p_v[volumeset] = my_core.get_child_meshsets(volumeset).size()
        df_vert['t_p_v'] = s_p_v
        return
        
    def populate_volume_coarseness(self):
        # TODO
        return
        
#my_stats = DagmcStats(‘test_file.h5m’)

#my_stats.populate_triangle_area()
#some_areas = my_stats.query_triangle_area(self, [some_tris])

