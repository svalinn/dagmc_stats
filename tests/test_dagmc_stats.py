# set the path to find the current installation of pyMOAB
from pymoab import core, types
from pymoab.rng import Range

# import the new module that defines each of the functions
import dagmc_stats.dagmc_stats as ds
import numpy as np
import unittest

test_input = "tests/3vols.h5m"
my_core = core.Core()
my_core.load_file(test_input)
root_set = my_core.get_root_set()

entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]

test_input_2 = "tests/single-cube.h5m"
my_core_2 = core.Core()
my_core_2.load_file(test_input_2)
root_set_2 = my_core.get_root_set()
native_ranges_2 = ds.get_native_ranges(my_core_2, root_set_2, entity_types)
dagmc_tags_2 = ds.get_dagmc_tags(my_core_2)

class TestDagmcStats(unittest.TestCase):


    def test_get_tags(self):
        """
        Tests different aspects of the get_dagmc_tags function
        """
        dagmc_tags = ds.get_dagmc_tags(my_core)
        assert(len(dagmc_tags) == 3)
        assert(dagmc_tags['category'])
        assert(dagmc_tags['geom_dim'])
        assert(dagmc_tags['global_id'])


    def test_get_native_ranges(self):
        """
        Tests different aspects of the get_native_ranges function
        """
        native_ranges = ds.get_native_ranges(my_core, root_set, entity_types)
        vertex_range = my_core.get_entities_by_type(root_set, types.MBVERTEX)
        assert(vertex_range == native_ranges[0])
        triangle_range = my_core.get_entities_by_type(root_set, types.MBTRI)
        assert(triangle_range == native_ranges[2])
        entityset_range = my_core.get_entities_by_type(root_set, types.MBENTITYSET)
        assert(entityset_range == native_ranges[11])


    def test_get_entityset_ranges(self):
        """
        Tests different aspects of the get_entityset_ranges function
        """
        dagmc_tags = ds.get_dagmc_tags(my_core)
        entityset_ranges = ds.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
        node_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [0])
        assert(node_range == entityset_ranges['Nodes'])
        curve_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [1])
        assert(curve_range == entityset_ranges['Curves'])
        surface_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [2])
        assert(surface_range ==entityset_ranges['Surfaces'])
        volume_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [3])
        assert(volume_range == entityset_ranges['Volumes'])


    def test_get_triangles_per_vertex(self):
        """Tests part of the get_triangles_per_vertex function"""
        dagmc_tags = ds.get_dagmc_tags(my_core)
        native_ranges = ds.get_native_ranges(my_core, root_set, entity_types)
        t_p_v_data = ds.get_triangles_per_vertex(my_core, native_ranges)
        vertices = my_core.get_entities_by_type(root_set, types.MBVERTEX).size()
        assert(len(t_p_v_data) == vertices)


    def test_get_triangles_per_surface(self):
        """
        Tests some parts of the get_triangles_per_surface function
        """
        dagmc_tags = ds.get_dagmc_tags(my_core_2)
        entityset_ranges = ds.get_entityset_ranges(
            my_core_2, root_set_2, dagmc_tags['geom_dim'])
        t_p_s_data = ds.get_triangles_per_surface(
            my_core_2, entityset_ranges)
            
        assert(len(t_p_s_data) == 6)
        
        assert(sum(t_p_s_data.values()) == 12)
        
        for v in t_p_s_data.values():
            assert(v == 2)


    def test_get_surfaces_per_volume(self):
        """
        Tests different aspects of the get_surfaces_per_volume function
        """
        dagmc_tags = ds.get_dagmc_tags(my_core)
        entityset_ranges = ds.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
        s_p_v_data = ds.get_surfaces_per_volume(my_core, entityset_ranges)
        known_volumes = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [3])
        for vol_eh in known_volumes:
            surfs = my_core.get_child_meshsets(vol_eh)
            assert(len(surfs) == s_p_v_data[vol_eh])


    def test_get_triangle_aspect_ratio(self):
        """
        Tests part of the get_triangle_aspect_ratio function
        """
        exp = (10*10*10*np.sqrt(2))/(8*5*np.sqrt(2)*5*np.sqrt(2)*(10-5*np.sqrt(2)))
        obs = ds.get_triangle_aspect_ratio(my_core_2, root_set_2, dagmc_tags_2['geom_dim'])[0]
        self.assertAlmostEqual(exp,obs)
        
        exp = my_core_2.get_entities_by_type(root_set_2, types.MBTRI).size()
        obs = len(ds.get_triangle_aspect_ratio(my_core_2, root_set_2, dagmc_tags_2['geom_dim']))
        self.assertEqual(exp,obs)


    def test_get_area_triangle(self):
        """
        Tests part of the get__area_triangle function
        """
        exp = 50
        obs = ds.get_area_triangle(my_core_2, root_set_2, dagmc_tags_2['geom_dim'])[0]
        self.assertAlmostEqual(exp,obs)
        
        exp = my_core_2.get_entities_by_type(root_set_2, types.MBTRI).size()
        obs = len(ds.get_area_triangle(my_core_2, root_set_2, dagmc_tags_2['geom_dim']))
        self.assertEqual(exp,obs)


    def test_get_tri_vert_data(self):
        """
        Test part of the get_tri_vert_data function
        """
        tri_vert_data, all_verts = ds.get_tri_vert_data(my_core_2, native_ranges_2)
        
        exp = 2*6*3
        obs = len(tri_vert_data)
        self.assertEqual(exp,obs)
        
        exp = 8
        obs = len(all_verts)
        self.assertEqual(exp,obs)
        
        for i in range(8):
            obs = len(tri_vert_data[tri_vert_data['vert'] == all_verts[i]])
            self.assertTrue(obs == 4 or obs == 5)
        
        
    def test_get_gaussian_curvature(self):
        """
        Test part of the get_gaussian_curvature function
        """
        tri_vert_data, all_verts = ds.get_tri_vert_data(my_core_2, native_ranges_2)
        gc_all = ds.get_gaussian_curvature(my_core_2, native_ranges_2,all_verts, tri_vert_data)
        
        exp = 8
        obs = len(gc_all)
        self.assertEqual(exp,obs)
        
        exp = 0.5*np.pi
        for i in range(8):
            obs = gc_all[all_verts[i]]
            self.assertAlmostEqual(exp,obs)

    
    def test_get_roughness(self):
        """
        Test part of the get_roughness function
        """
        roughness = ds.get_roughness(my_core_2, native_ranges_2)
        exp = 8
        obs = len(roughness)
        self.assertEqual(exp,obs)
        
        exp = 0
        for i in range(8):
            obs = roughness[i]
            self.assertAlmostEqual(exp,obs)
