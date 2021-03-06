# set the path to find the current installation of pyMOAB
import numpy as np

from pymoab.rng import Range
from pymoab import core, types

tri_vert_struct = np.dtype({'names': ['tri', 'vert', 'angle',
'side_length'], 'formats': [np.uint64, np.uint64, np.float64, np.float64]})

def get_dagmc_tags(my_core):
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


def get_entityset_ranges(my_core, meshset, geom_dim):
    """
    Get a dictionary with MOAB Ranges that are specific to the
    types.MBENTITYSET type

    inputs
    ------
    my_core : a MOAB Core instance
    meshset : the root meshset for the file
    geom_dim : the tag that specifically denotes the dimesion of the entity

    outputs
    -------
    entityset_ranges : a dictionary with one entry for each entityset type,
                       and the value is the range of entities that corrospond
                       to each type
    """

    entityset_ranges = {}
    entityset_types = ['Nodes', 'Curves', 'Surfaces', 'Volumes']
    for dimension, set_type in enumerate(entityset_types):
        entityset_ranges[set_type] = \
            my_core.get_entities_by_type_and_tag(meshset, types.MBENTITYSET,
                                                 geom_dim, [dimension])
    return entityset_ranges


def get_triangles_per_vertex(my_core, native_ranges, ignore_zero=True):
    """
    This function will return data about the number of triangles on each
    vertex in a file

    inputs
    ------
    my_core : a MOAB Core instance
    native_ranges : a dictionary containing ranges for each native type in the
                    file (VERTEX, TRIANGLE, ENTITYSET)
    ignore_zero : a boolean value that indicates whether to ignore the 
                  vertices that are not connected to any triangles.

    outputs
    -------
    t_p_v_data : a list of the number of triangles each vertex touches
    """

    t_p_v_data = []
    tri_dimension = 2
    for vertex in native_ranges[types.MBVERTEX]:
        tpv_val = my_core.get_adjacencies(vertex, tri_dimension).size()
        if ignore_zero and tpv_val == 0:
            continue
        t_p_v_data.append(tpv_val)
    return np.array(t_p_v_data)


def get_triangles_per_surface(my_core, entity_ranges):
    """
    This function will return data about the number of triangles on each
    surface in a file

    inputs
    ------
    my_core : a MOAB Core instance
    entity_ranges : a dictionary containing ranges for each type in the file
                    (VOLUME, SURFACE, CURVE, VERTEX, TRIANGLE, ENTITYSET)

    outputs
    -------
    t_p_s : a dictionary containing the entityhandle of the surface,
            and the number of triangles each surface contains.
            i.e {surface entityhandle : triangles it contains}
    """

    t_p_s = {}
    for surface in entity_ranges['Surfaces']:
        t_p_s[surface] = my_core.get_entities_by_type(
            surface, types.MBTRI).size()
    return t_p_s


def get_surfaces_per_volume(my_core, entityset_ranges):
    """
    Get the number of surfaces that each volume in a given file contains

    inputs
    ------
    my_core : a MOAB core instance
    entity_ranges : a dictionary of the entityset ranges of each tag in a file

    outputs
    -------
    s_p_v : a dictionary containing the volume entityhandle
            and the number of surfaces each volume in the file contains
            i.e. {volume entityhandle:surfaces it contains}
    """

    s_p_v = {}
    for volumeset in entityset_ranges['Volumes']:
        s_p_v[volumeset] = my_core.get_child_meshsets(volumeset).size()
    return s_p_v


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


def get_tri_side_length(my_core, tri):
    """
    Get side lengths of triangle

    inputs
    ------
    my_core : a MOAB Core instance
    tri : triangle entity

    outputs
    -------
    side_lengths : a dictionary that stores vert : the opposite side length of
    the vert as key-value pair
    """

    side_lengths = {}
    s = 0
    coord_list = []

    verts = list(my_core.get_adjacencies(tri, 0))

    for vert in verts:
        coords = my_core.get_coords(vert)
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


def get_triangle_aspect_ratio(my_core, meshset, geom_dim):
    """
    Get the triangle aspect ratio (according to the equation:
    (abc)/(8(s-a)(s-b)(s-c)), where s = .5(a+b+c).)

    inputs
    ------
    my_core : a MOAB Core instance
    meshset : a meshset containing a certain part of the mesh
    geom_dim : a MOAB Tag that holds the dimension of an entity.

    outputs
    -------
    t_a_r : (list) the triangle aspect ratios for triangles in the meshset
    """

    tris = get_tris(my_core, meshset, geom_dim)
    t_a_r = []

    for tri in tris:
        side_lengths = list(get_tri_side_length(my_core, tri).values())
        s = .5*(sum(side_lengths))
        top = np.prod(side_lengths)
        bottom = 8*np.prod(s-side_lengths)
        t_a_r.append(top/bottom)

    return t_a_r


def get_area_triangle(my_core, meshset, geom_dim, tris=[]):
    """
    Get the triangle area (according to the Heron's formula:
    sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2)

    inputs
    ------
    my_core : a MOAB Core instance
    meshset : a meshset containing a certain part of the mesh
    geom_dim : a MOAB Tag that holds the dimension of an entity.
    tris : (list) triangles whose area will be calculated. The default value is
    an empty list and will lead to calculation of all triangle areas in the
    geometry

    outputs
    -------
    area : (list) the triangle areas in the meshset
    """

    area = []
    if not tris:
        tris = get_tris(my_core, meshset, geom_dim)
    for tri in tris:
        side_lengths = list(get_tri_side_length(my_core, tri).values())
        # sqrt(s(s - a)(s - b)(s - c)), where s = (a + b + c)/2
        s = sum(side_lengths)/2
        s = np.sqrt(s * np.prod(s - side_lengths))
        area.append(s)

    return area


def get_coarseness(my_core, meshset, entity_ranges, geom_dim):
    """
    Get the coarseness of area. Coarseness is calculated by dividing
    surface area of a surface by number of triangles in that surface.

    inputs
    ------
    my_core : a MOAB Core instance
    meshset : a meshset containing a certain part of the mesh
    entity_ranges : the surface entities
    geom_dim : a MOAB Tag that holds the dimension of an entity.

    outputs
    -------
    coarseness : (list) the coarseness for surfaces in the meshset.
    """

    coarseness = []

    for surface in entity_ranges:
        surf_area = get_area_triangle(my_core, surface, geom_dim)
        coarseness.append(len(surf_area)/sum(surf_area))

    return coarseness


def get_tri_vert_data(my_core, all_tris):
    """Build a numpy strcutured array to store triangle and vertex related
    data in the form of triangle entity handle | vertex entity handle
    | angle connected to the vertex | side length of side opposite to
    vertex in the triangle

    inputs
    ------
    my_core : a MOAB Core instance
    all_tris : a dictionary containing range for TRIANGLE native type
    in the file

    outputs
    -------
    tri_vert_data : a numpy structured array that stores the triangle
    and vertex related data
    all_verts : (list) all the vertices that are connected to
    triangle in the geometry
    """
    all_verts =set()
    tri_vert_data = np.zeros(len(all_tris)*3, dtype=tri_vert_struct)
    tri_vert_index = 0

    for tri in all_tris:
        side_lengths = get_tri_side_length(
            my_core, tri)   # {vert : side_length}
        side_length_sum_sq_half = sum(map
                                    (lambda i: i**2, side_lengths.values()))/2
        side_length_prod = np.prod(list(side_lengths.values()))
        verts = list(my_core.get_adjacencies(tri, 0, op_type=1))
        for vert_i in verts:
            all_verts.add(vert_i)
            side_i = side_lengths[vert_i]
            d_i = np.arccos((side_length_sum_sq_half - (side_i**2)) * side_i /
                            side_length_prod)
            bar = np.array((tri, vert_i, d_i, side_i), dtype=tri_vert_struct)
            tri_vert_data[tri_vert_index] = bar
            tri_vert_index += 1
    return tri_vert_data, list(all_verts)


def get_gaussian_curvature(my_core, all_verts, tri_vert_data):
    """Get gaussian curvature values of all non-isolated vertices

    inputs
    ------
    my_core : a MOAB Core instance
    all_verts : all the vertices that are connected to triangle in the
    geometry
    tri_vert_data : numpy structured array that stores the triangle and
    vertex related data

    outputs
    -------
    gc_all : dictionary in the form of vertex : gaussian curvature value
    of the vertex
    """
    gc_all = {}
    for vert_i in all_verts:
        gc_all[vert_i] = gaussian_curvature(vert_i, tri_vert_data)
    return gc_all


def gaussian_curvature(vert_i, tri_vert_data):
    """Get gaussian curvature value of a vertex
    Reference: https://www.sciencedirect.com/science/article/pii/
    S0097849312001203
    Formula 1

    inputs
    ------
    vert_i : vertex entity handle
    tri_vert_data : numpy structured array that stores the triangle and
    vertex related data

    outputs
    -------
    gc : gaussian curvature value of the vertex
    """
    vert_entries = tri_vert_data[tri_vert_data['vert'] == vert_i]
    sum_alpha_angles = sum(vert_entries['angle'])
    gc = np.abs(2 * np.pi - sum_alpha_angles)
    return gc


def get_lri(vert_i, gc_all, tri_vert_data, my_core):
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
    my_core : a MOAB Core instance

    outputs
    -------
    Lri : local roughness value of the vertex
    """
    DIJgc_sum = 0
    Dii_sum = 0
    vert_j_list = list(my_core.get_adjacencies(my_core.get_adjacencies(
        vert_i, 2, op_type=0), 0, op_type=1))
    vert_j_list.remove(vert_i)
    for vert_j in vert_j_list:
        # get tri_ij_list (the list of the two triangles connected to both
        # vert_i and vert_j)
        tri_i_list = my_core.get_adjacencies(vert_i, 2, op_type=0)
        tri_j_list = my_core.get_adjacencies(vert_j, 2, op_type=0)
        tri_ij_list = list(set(tri_i_list) & set(tri_j_list))
        # rows with tri value as tri_ij_list[0] or tri_ij_list[1]
        select_tris = (tri_vert_data['tri'] == tri_ij_list[0]) | \
                                    (tri_vert_data['tri'] == tri_ij_list[1])
        # rows with vert value not equal to vert_i and not equal to vert_j
        exclude_verts = (tri_vert_data['vert'] != vert_i) & \
                                            (tri_vert_data['vert'] != vert_j)
        beta_angles = tri_vert_data[select_tris & exclude_verts]['angle']

        Dij = 0.5 * (1/np.tan(beta_angles[0]) + 1/np.tan(beta_angles[1]))
        DIJgc_sum += (Dij * gc_all[vert_j])
        Dii_sum += Dij
    Lri = abs(gc_all[vert_i] - DIJgc_sum/Dii_sum)
    return Lri


def get_roughness(my_core, native_ranges, verts=None):
    """Get local roughness values of all the non-isolated vertices

    inputs
    ------
    my_core : a MOAB Core instance
    native_ranges : a dictionary containing ranges for each native type
    in the file (VERTEX, TRIANGLE, ENTITYSET)
    verts : the list of vertices whose roughness values are to be calculated.
    By default its value is None and the roughness values for all the vertices
    in the geometry will be calculated

    outputs
    -------
    roughness : (dictionary) the roughness for all vertices in the meshset
    stored in the form of vert : local roughness value
    """
    tri_vert_data, all_verts = get_tri_vert_data(my_core,
                                                    native_ranges[types.MBTRI])
    if verts is None:
        verts = all_verts
    gc_all = get_gaussian_curvature(my_core, all_verts, tri_vert_data)
    roughness = {}
    for vert_i in verts:
        roughness[vert_i] = get_lri(vert_i, gc_all, tri_vert_data, my_core)
    return roughness
    

def get_tri_roughness(my_core, native_ranges, roughness):
    """Get triangle average roughness

    inputs
    ------
    my_core : a MOAB Core instance
    native_ranges : a dictionary containing ranges for each native type
    in the file (VERTEX, TRIANGLE, ENTITYSET)
    roughness : (dictionary) the roughness for all vertices in the meshset
    stored in the form of vert : local roughness value

    outputs
    -------
    tri_roughness : (dictionary) the average roughness values for all triangles
    in the meshset stored in the form of tri : average roughness value
    """
    tri_roughness = {}
    for tri in native_ranges[types.MBTRI]:
        three_verts = list(my_core.get_adjacencies(tri, 0, op_type=1))
        sum_lr = 0
        for vert in three_verts:
            sum_lr += roughness[vert]
        tri_roughness[tri] = sum_lr/3
    return tri_roughness
    
    
def add_tag(my_core, tag_name, tag_dic, tag_type):
    """Add tag according to given tag information

    inputs
    ------
    my_core : a MOAB Core instance
    tag_name : tag name
    tag_dic : a dictionary containing eh:data
    tag_type : tag type
    """
    # create the tag handle
    tag_eh = \
        my_core.tag_get_handle(tag_name, size=1,
                                tag_type=tag_type,
                                storage_type=types.MB_TAG_SPARSE,
                                create_if_missing=True)
    for eh, data in tag_dic.items():
        # assign data to the tag:
        my_core.tag_set_data(tag_eh, eh, data)


def avg_roughness(my_core, roughness, geom_dim):
    """Get the average roughness value for the geometry
    Reference: https://www.sciencedirect.com/science/article/pii/
    S0097849312001203
    Formula 5

    inputs
    ------
    my_core : a MOAB Core instance
    roughness : (dictionary) the roughness for all vertices in the meshset
    geom_dim : the tag that specifically denotes the dimesion of the entity
    
    outputs
    -------
    avg_roughness : the average roughness value for the geometry
    """
    root_set = my_core.get_root_set()
    area_sum = sum(get_area_triangle(my_core, root_set, geom_dim))
    num = 0
    for vert in roughness:
        adj_tris = my_core.get_adjacencies(vert, 2, op_type=0)
        s_i = get_area_triangle(my_core, root_set, geom_dim, tris=adj_tris)
        num += roughness[vert] * sum(s_i) / 3
    avg_roughness = num/area_sum
    return avg_roughness
