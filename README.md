# dagmc_stats
Tool for calculating and reporting statistics about DAGMC models

Dependencies
============

[PyMOAB](https://press3.mcs.anl.gov/sigma/moab-library/)

[NumPy](https://www.numpy.org/)

[MatPlotLib](https://matplotlib.org/)

[Argparse](https://docs.python.org/3/library/argparse.html)


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


## 9. Triangles per Surface:

Triangles per Surface is the number of triangles that represent each surface in a mesh.

A triangle is a mesh entity, and make up larger surfaces within a mesh.

Minimum, Maximum, Median, and Mean (average) are returned for this statistic, as well as a distribution.


## 10. Triangles per Vertex:

Triangles per Vertex is the number of triangles that connect each vertex.

Each triangle connects to three vertices, but there can be many triangles on a given vertex.

Minimum, Maximum, Median, and Mean (average) are returned for this statistic, as well as a distribution.


## 11. Triangle Aspect Ratio:

This is a ratio that describes a certain triangle, and can be calculated using the equation:

abc/(8*(s-a)(s-b)(s-c)) where s = .5(a+b+c) and a, b, and c are the side lengths of the triangle. 

Minimum, Maximum, Median, and Mean (average) are returned for this statistic, as well as a distribution.

There is an option for this statistic to specify a Surface or Volume to analyze.
