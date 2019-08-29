# dagmc_stats
Tool for calculating and reporting statistics about DAGMC models

Dependencies
============

[PyMOAB](https://press3.mcs.anl.gov/sigma/moab-library/)
(PyMOAB.Core, PyMOAB.Range)

[NumPy](https://www.numpy.org/)

[MatPlotLib](https://matplotlib.org/)
(Matplotlib.pyplot)

[Argparse](https://docs.python.org/3/library/argparse.html)

Usage
=====

`generate_stats.py` can be used to return statistics about certain parts of a mesh file, such as `.h5m` or `.vtk` files. Running `generate_stats.py` will print these statistics when it is run. There are a variety of options that can be implemented in order to individualize the statistics returned.

  `python generate_stats.py [filename]`
  
This base option will return all statistics that might be relevant to the file
  
  `python generate_stats.py [filename] -v`

The `-v` controls the verbosity of the output

  `python generate_stats.py [filename] --nr --er --spv --tps --tpv --tar`
  
Each of the previous options controls whether a different statistical area is printed:
  
    `--nr` : Native Ranges
  
    `--er` : EntitySet Ranges

    `--spv` : Surfaces per Volume

    `--tps` : Triangles per Surface

    `--tpv` : Triangles per Vertex

    `--tar` : Triangle Aspect Ratio
  
The default setting is that all statistics will be printed, so if one or more of these options are specified, the unspecified options will not be printed.
  
  `python generate_stats.py [filename] --tar_meshset TAR_MESHSET`

`--tar_meshset` controls what meshset (or EntitySet) is used to compute the statistics for the Triangle Aspect Ratio. Default is the root set for the file. This can be a surface, volume, or the root_set.

  `python generate_stats.py [filename] --spv_data, --tps_data`
  
These two options control whether the actual data for Surfaces per Volume and Triangles per Surface is printed, with each entity being paired with its corrosponding value (see example below)

Example Output from `generate_stats.py`
=======================================

#### `python generate_stats.py 3vols.h5m`
  
    Type 0 : 74130

    Type 2 : 148248

    Type 11 : 58

    Nodes : 16

    Curves : 24

    Surfaces : 13

    Volumes : 3

    Triangles per Surface:

    minimum : 2

    maximum : 148224

    median : 2.0

    mean : 11403.692307692309

    Surfaces per Volume:

    minimum : 1

    maximum : 6

    median : 6.0

    mean : 4.333333333333333

    Triangles per Vertex:

    minimum : 4

    maximum : 386

    median : 6.0

    mean : 5.999514366653177

    Triangle Aspect Ratio:

    minimum : 1.205763046406058

    maximum : 61.534011819479794

    median : 1.2691552474001135

    mean : 2.2629211298630483


#### `python generate_stats.py 3vols.h5m --spv -v`

    The minimum number of Surfaces per Volume in this model is 1.

    The maximum number of Surfaces per Volume in this model is 6.

    The median number of Surfaces per Volume in this model is 6.0.

    The mean number of Surfaces per Volume in this model is 4.333333333333333.


#### `python generate_stats.py 3vols.h5m --spv_data`

    Volume                          Surfaces

    12682136550675316791 (1)        6

    12682136550675316792 (2)        6

    12682136550675316793 (3)        1


#### `python generate_stats.py 3vols.h5m --tar --tar_meshset 12682136550675316791`

    Triangle Aspect Ratio:

    minimum : 1.2071067811865475

    maximum : 1.2071067811865477

    median : 1.2071067811865475

    mean : 1.2071067811865477

  
Explanation of Statistics Returned
==================================
## 1. Vertices (Type 0):

Vertices are mesh elements that connect triangles to one another. 

The number of Vertices is returned


## 2. Triangles (Type 2):

Triangles are mesh elements that are bound by vertices. 

Triangles make up surfaces. 

The number of Triangles is returned.


## 3. EntitySets (Type 11):

EntitySets are mesh entities that represent a geometric entity, such as a node, curve, surface, or volume. 

The number of EntitySets is returned. 


## 4. Nodes:

Nodes are 0-D points, similar to vertices, but are geometric entities, rather than mesh. 

Nodes bind Curves. 

The number of Nodes is returned. 


## 5. Curves:

Curves are 1-D geometric elements. 

Curves bind Surfaces and are bound by Nodes. 

The number of Curves is returned. 


## 6. Surfaces:

Surfaces are 2-D geometric entities that are made fundamentally up by triangles. 

Surfaces bind Volumes and are bound by Curves. 

The number of Surfaces is returned. 


## 7. Volumes:

Volumes are 3-D geometric entities. 

Volumes are bound by Surfaces. 

The number of Volumes is returned. 


## 8. Surfaces per Volume:

Surfaces per Volume is the number of surfaces each volume in the mesh contains.

Minimum, Maximum, Median, and Mean (average) are returned for this statistic, as well as a distribution.

There is an option to return the EntityHandle of each Volume and its corrosponding number of Surfaces

## 9. Triangles per Surface:

Triangles per Surface is the number of triangles that represent each surface in a mesh.

A triangle is a mesh entity, and make up larger surfaces within a mesh.

Minimum, Maximum, Median, and Mean (average) are returned for this statistic, as well as a distribution.

There is an option to display the EntityHandle of each Surface and its corrosponding number of Triangles

## 10. Triangles per Vertex:

Triangles per Vertex is the number of triangles that connect each vertex.

Each triangle connects to three vertices, but there can be many triangles on a given vertex.

Minimum, Maximum, Median, and Mean (average) are returned for this statistic, as well as a distribution.


## 11. Triangle Aspect Ratio:

This is a ratio that describes a certain triangle, and can be calculated using the equation:

abc/(8*(s-a)(s-b)(s-c)) where s = .5(a+b+c) and a, b, and c are the side lengths of the triangle. 

Minimum, Maximum, Median, and Mean (average) are returned for this statistic, as well as a distribution.

There is an option for this statistic to specify a Surface or Volume to analyze.
