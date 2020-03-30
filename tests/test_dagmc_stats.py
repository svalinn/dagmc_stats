# set the path to find the current installation of pyMOAB
from pymoab import core, types
from pymoab.rng import Range

# import the new module that defines each of the functions
import dagmc_stats
import numpy as np
import unittest

test_input = "3vols.h5m"

my_core = core.Core()
my_core.load_file(test_input)

root_set = my_core.get_root_set()
entity_types = [types.MBVERTEX, types.MBTRI, types.MBENTITYSET]

class TestDagmcStats(unittest.TestCase):


    def test_get_tags(self):
        """
        Tests different aspects of the get_dagmc_tags function
        """
        dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
        assert(len(dagmc_tags) == 3)
        assert(dagmc_tags['category'])
        assert(dagmc_tags['geom_dim'])
        assert(dagmc_tags['global_id'])


    def test_get_native_ranges(self):
        """
        Tests different aspects of the get_native_ranges function
        """
        native_ranges = dagmc_stats.get_native_ranges(my_core, root_set, entity_types)
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
        dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
        entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
        node_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [0])
        assert(node_range == entityset_ranges['Nodes'])
        curve_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [1])
        assert(curve_range == entityset_ranges['Curves'])
        surface_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [2])
        assert(surface_range ==entityset_ranges['Surfaces'])
        volume_range = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [3])
        assert(volume_range == entityset_ranges['Volumes'])


    def test_get_triangles_per_vertex(self):
        "Tests part of the get_triangles_per_vertex function"
        dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
        native_ranges = dagmc_stats.get_native_ranges(my_core, root_set, entity_types)
        t_p_v_data = dagmc_stats.get_triangles_per_vertex(my_core, native_ranges)
        vertices = my_core.get_entities_by_type(root_set, types.MBVERTEX).size()
        assert(len(t_p_v_data) == vertices)


    def test_get_triangles_per_surface(self):
        """
        Tests some parts of the get_triangles_per_surface function
        """
        dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
        entityset_ranges = dagmc_stats.get_entityset_ranges(
            my_core, root_set, dagmc_tags['geom_dim'])
        t_p_s_data = dagmc_stats.get_triangles_per_surface(
            my_core, entityset_ranges)
        surfaces = my_core.get_entities_by_type_and_tag(
            root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [2]).size()
        assert(len(t_p_s_data) == surfaces)
        triangles = my_core.get_entities_by_type(root_set, types.MBTRI).size()
        assert(sum(t_p_s_data) == triangles)


    def test_get_surfaces_per_volume(self):
        """
        Tests different aspects of the get_surfaces_per_volume function
        """
        dagmc_tags = dagmc_stats.get_dagmc_tags(my_core)
        entityset_ranges = dagmc_stats.get_entityset_ranges(my_core, root_set, dagmc_tags['geom_dim'])
        s_p_v_data = dagmc_stats.get_surfaces_per_volume(my_core, entityset_ranges)
        known_volumes = my_core.get_entities_by_type_and_tag(root_set, types.MBENTITYSET, dagmc_tags['geom_dim'], [3])
        for eh in range(known_volumes.size()):
            surfs = my_core.get_child_meshsets(known_volumes[eh]).size()
            assert(surfs == s_p_v_data[eh])


    def test_get_triangle_aspect_ratio(self):
        """
        Tests part of the get_triangle_aspect_ratio function
        """
        test_input2 = "single-cube.h5m"
        my_core = core.Core()
        my_core.load_file(test_input2)
        root_set = my_core.get_root_set()

        exp = (10*10*10*np.sqrt(2))/(8*5*np.sqrt(2)*5*np.sqrt(2)*(10-5*np.sqrt(2)))
        obs = dagmc_stats.get_triangle_aspect_ratio(my_core, root_set)[0]
        assertAlmostEqual(exp,obs)

        exp = my_core.get_entities_by_type(root_set, types.MBTRI).size()
        obs = len(dagmc_stats.get_triangle_aspect_ratio(my_core, root_set))
        assertEqual(exp,obs)


    def test_get_area_triangle(self):
        """
        Tests part of the get__area_triangle function
        """
        test_input2 = "single-cube.h5m"
        my_core = core.Core()
        my_core.load_file(test_input2)
        root_set = my_core.get_root_set()

        exp = 50
        obs = get_area_triangle(my_core, root_set)[0]
        assertEqual(exp,obs)

        exp = my_core.get_entities_by_type(root_set, types.MBTRI).size()
        obs = len(dagmc_stats.get_area_triangle(my_core, root_set))
        assertEqual(exp,obs)
