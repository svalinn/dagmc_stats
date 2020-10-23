# set the path to find the current installation of pyMOAB
from pymoab import core, types
from pymoab.rng import Range

# import the new module that defines each of the functions
import dagmc_stats.dagmc_stats as ds
import numpy as np
import unittest

entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]
test_env = [ { 'input_file' : 'tests/3vols.h5m'}, {'input_file' : 'tests/single-cube.h5m'}, {'input_file' : 'tests/pyramid.h5m'}]

for env in test_env:
     env['core'] = core.Core()
     env['core'].load_file(env['input_file'])
     env['root_set'] = env['core'].get_root_set()
     env['native_ranges'] = ds.get_native_ranges(env['core'], env['root_set'], entity_types)
     env['dagmc_tags'] = ds.get_dagmc_tags(env['core'])

class TestDagmcStats(unittest.TestCase):


    def test_get_tags(self):
        """
        Tests different aspects of the get_dagmc_tags function
        """
        dagmc_tags = ds.get_dagmc_tags(test_env[0]['core'])
        assert(len(dagmc_tags) == 3)
        assert(dagmc_tags['category'])
        assert(dagmc_tags['geom_dim'])
        assert(dagmc_tags['global_id'])


    def test_get_native_ranges(self):
        """
        Tests different aspects of the get_native_ranges function
        """
        my_core = test_env[0]['core']
        root_set = test_env[0]['root_set']
        native_ranges = test_env[0]['native_ranges']
        
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
        my_core = test_env[0]['core']
        root_set = test_env[0]['root_set']
        dagmc_tags = test_env[0]['dagmc_tags']
        
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
        my_core = test_env[0]['core']
        root_set = test_env[0]['root_set']
        native_ranges = test_env[0]['native_ranges']
        
        t_p_v_data = ds.get_triangles_per_vertex(my_core, native_ranges)
        vertices = my_core.get_entities_by_type(root_set, types.MBVERTEX).size()
        assert(len(t_p_v_data) == vertices)


    def test_get_triangles_per_surface(self):
        """
        Tests some parts of the get_triangles_per_surface function
        """
        my_core = test_env[1]['core']
        root_set = test_env[1]['root_set']
        dagmc_tags = test_env[1]['dagmc_tags']
        
        dagmc_tags = ds.get_dagmc_tags(my_core)
        entityset_ranges = ds.get_entityset_ranges(
            my_core, root_set, dagmc_tags['geom_dim'])
        t_p_s_data = ds.get_triangles_per_surface(
            my_core, entityset_ranges)
            
        assert(len(t_p_s_data) == 6)
        
        assert(sum(t_p_s_data.values()) == 12)
        
        exp = [2,2,2,2,2,2]
        obs = list(t_p_s_data.values())
        np.testing.assert_array_equal(exp, obs)


    def test_get_surfaces_per_volume(self):
        """
        Tests different aspects of the get_surfaces_per_volume function
        """
        my_core = test_env[0]['core']
        root_set = test_env[0]['root_set']
        dagmc_tags = test_env[0]['dagmc_tags']
        
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
        my_core = test_env[1]['core']
        root_set = test_env[1]['root_set']
        dagmc_tags = test_env[1]['dagmc_tags']
        
        exp = (10*10*10*np.sqrt(2))/(8*5*np.sqrt(2)*5*np.sqrt(2)*(10-5*np.sqrt(2)))
        obs = ds.get_triangle_aspect_ratio(my_core, root_set, dagmc_tags['geom_dim'])[0]
        self.assertAlmostEqual(exp, obs)
        
        exp = my_core.get_entities_by_type(root_set, types.MBTRI).size()
        obs = len(ds.get_triangle_aspect_ratio(my_core, root_set, dagmc_tags['geom_dim']))
        self.assertEqual(exp, obs)


    def test_get_area_triangle(self):
        """
        Tests part of the get__area_triangle function
        """
        my_core = test_env[1]['core']
        root_set = test_env[1]['root_set']
        dagmc_tags = test_env[1]['dagmc_tags']
        
        exp = 50
        obs = ds.get_area_triangle(my_core, root_set, dagmc_tags['geom_dim'])[0]
        self.assertAlmostEqual(exp, obs)
        
        exp = my_core.get_entities_by_type(root_set, types.MBTRI).size()
        obs = len(ds.get_area_triangle(my_core, root_set, dagmc_tags['geom_dim']))
        self.assertEqual(exp, obs)


    def test_get_tri_vert_data(self):
        """Tests part of the get_tri_vert_data function
        """
        my_core = test_env[1]['core']
        native_ranges = test_env[1]['native_ranges']
        
        tri_vert_data, all_verts = ds.get_tri_vert_data(my_core, native_ranges[types.MBTRI])
        
        exp = 2*6*3
        obs = len(tri_vert_data)
        self.assertEqual(exp, obs)
        
        exp = 8
        obs = len(all_verts)
        self.assertEqual(exp, obs)
        
        exp = [4, 5, 5, 4, 5, 4, 5, 4]
        for i in range(8):
            obs = len(tri_vert_data[tri_vert_data['vert'] == all_verts[i]])
            self.assertTrue(obs == exp[i])
        
        
    def test_get_gaussian_curvature(self):
        """Tests part of the get_gaussian_curvature function
        """
        my_core = test_env[1]['core']
        native_ranges = test_env[1]['native_ranges']
        
        tri_vert_data, all_verts = ds.get_tri_vert_data(my_core, native_ranges[types.MBTRI])
        gc_all = ds.get_gaussian_curvature(my_core, all_verts, tri_vert_data)
        
        exp = 8
        obs = len(gc_all)
        self.assertEqual(exp, obs)
        
        exp = 0.5*np.pi
        for i in range(8):
            obs = gc_all[all_verts[i]]
            self.assertAlmostEqual(exp, obs)

    
    def test_get_lri(self):
        """Tests part of the get_lri function
        """
        my_core = test_env[1]['core']
        native_ranges = test_env[1]['native_ranges']
        
        tri_vert_data, all_verts = ds.get_tri_vert_data(my_core, native_ranges[types.MBTRI])
        gc_all = ds.get_gaussian_curvature(my_core, all_verts, tri_vert_data)
        
        exp = 0
        for i in range(8):
            vert_i = all_verts[i]
            obs = ds.get_lri(vert_i, gc_all, tri_vert_data, my_core)
            self.assertAlmostEqual(exp, obs)
    
    
    def test_get_roughness(self):
        """Tests part of the get_roughness function
        """
        my_core = test_env[1]['core']
        native_ranges = test_env[1]['native_ranges']
        
        roughness = ds.get_roughness(my_core, native_ranges).values()
        exp = 8
        obs = len(roughness)
        self.assertEqual(exp, obs)
        
        exp = [0,0,0,0,0,0,0,0]
        np.testing.assert_allclose(roughness, exp, atol = 1e-04)
        
        
    def test_get_avg_roughness(self):
        """Tests part of the avg_roughness function
        """
        # pyramid
        my_core = test_env[2]['core']
        native_ranges = test_env[2]['native_ranges']
        roughness = ds.get_roughness(my_core, native_ranges)
        geom_dim = test_env[2]['dagmc_tags']['geom_dim']
        
        gc_top = 2.0/3*np.pi
        gc_bottom = 5.0/6*np.pi
        d_bottom = [1/np.tan(np.pi/3),
                    0.5*(1/np.tan(np.pi/3)+1/np.tan(np.pi/4)), 0]
        lr_bottom = []
        lr_top = np.abs(gc_top - gc_bottom)
        lr_bottom.append(np.abs(gc_bottom - \
                    (d_bottom[0]*gc_top+2*d_bottom[1]*gc_bottom) \
                    /(d_bottom[0]+2*d_bottom[1])))
        lr_bottom.append(np.abs(gc_bottom - \
                    (d_bottom[0]*gc_top+2*d_bottom[1]*gc_bottom+d_bottom[2]*gc_bottom) \
                    /(d_bottom[0]+2*d_bottom[1]+d_bottom[2])))
        s_top = 4*25/4*np.sqrt(3)
        s_bottom = [12.5+2*25/4*np.sqrt(3), 25+2*25/4*np.sqrt(3)]
        # sum of vert * 1/3 total area of the incident facets of vert
        num = lr_top*s_top/3 + \
                    2*lr_bottom[0]*s_bottom[0]/3 + \
                    2*lr_bottom[1]*s_bottom[1]/3
        # the total surface area
        denom = 4*25/4*np.sqrt(3)+25
        
        exp = num/denom
        obs = ds.avg_roughness(my_core, roughness, geom_dim)
        self.assertAlmostEqual(exp, obs, 2)
