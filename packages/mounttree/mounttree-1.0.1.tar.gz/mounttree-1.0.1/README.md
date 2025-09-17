# Python package for coordinate conversions
<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Python package for coordinate conversions](#python-package-for-coordinate-conversions)
  - [Usage](#usage)
  - [Mounttree](#mounttree)
    - [Coordinate frames](#coordinate-frames)
    - [Mounttree structure](#mounttree-structure)
    - [Open variables](#open-variables)

<!-- /code_chunk_output -->

This package allows to convert position and direction vectors between different coordinate frames.
These frames must be arranged in a so called "mounttree", a tree-like structure which defines their relative orientation.

## Usage
Load a mounttree in yaml format to get a CoordinateUniverse object
```python
import mounttree as mnt
universe=mnt.load_mounttree('test/testmounttree.yaml')
```
If there are open variables in the tree, specify them before use:
```python
universe.update(lat=0, lon=0, height=10, roll=0, pitch=0, yaw=0)
```

Now, we can get a transformation from 'HALO' to 'EARTH' coordinates
```python
transform=universe.get_transformation('HALO','EARTH')
```
Use the transformation to convert positional or direction vectors
```python
p1=transform.apply_point(0, 0, 0)
p2=transform.apply_direction(0, 1, 0)
```
We can also convert multiple points at once, if we provide numpy arrays of coordinates.
```python
import numpy as np
x=np.array([[0,0,0],[0,1,1]])
y=np.array([[0,1,1],[0,0,0]])
z=np.array([[0,0,0],[1,1,1]])
px, py, pz=transform.apply_point(x,y,z)
```

We can also update the mounttree with multiple locations which differ, e.g., in the height coordinate as shown here:
```python
universe.update(lat=[0, 0], lon=[0, 0], height=[10, 100], roll=[0, 0], pitch=[0, 0], yaw=[0, 0])
```

Note: With `universe.variables`, you can have a look at the variables of the mounttree.

We specify the transformation:
```python
transform_multiple_locations = universe.get_transformation('HALO','EARTH')
```
and apply the transformation as before. In this case, the point `(0, 0, 0)` and the direction `(0, 1, 0)` are transformed from 'HALO' to 'EARTH' for the two HALO positions defined above.
```python
p1 = transform_multiple_locations.apply_point(0,0,0)
p2 = transform_multiple_locations.apply_direction(0,1,0)
print(p1)
(array([6378147., 6378237.]), array([0., 0.]), array([0., 0.]))
print(p2)
(array([0., 0.]), array([1., 1.]), array([0., 0.]))
```

For the transformation of the same but multiple points/directions to different HALO positions, repeat the array according to the number of positions. For example, the transformation of the different viewing angles of a polarization camera of specMACS (`view_dirs_HALO_coords` with shape `(2040, 2440, 3)`) from 'HALO' to 'EARTH' coordinates for the two different positions would look like this: 
```python
vx, vy, vz = transform_multiple_locations.apply_direction(*np.array([view_dirs_HALO_coords, view_dirs_HALO_coords]).transpose(3,1,2,0))
view_dirs_EARTH_coords = np.stack([xv, vy, vz])
print(view_dirs_EARTH_coords.shape)
(2, 2040, 2440, 3)
```

In the next example, we will apply the transformation to two different points which correspond to the two different HALO positions:
```python
import numpy as np
x = np.array([0, 0])
y = np.array([0, 0])
z = np.array([0, 333])
px, py, pz = transform_multiple_locations.apply_point(x,y,z)
```

Again, we see the difference in the `px` element:
```python
print(px)
array([6378147., 6377904.])
```

Note: So far, the combination (= transform N vectors at M different mounttree positions, which would result in N x M transformed vectors) is not possible. In this case, just loop over the smaller number of N or M.

## Mounttree
### Coordinate frames
Coordinate frames are objects to relate tuples of numbers (coordinates) to points in space. A point can be expressed in natural coordinates and cartesian coordinates. Each coordinate frame must provide functions to convert between natural and cartesian coordinates. 
Additionally, there must be a function to provide a natural orientation at each point in space.
In `mounttree_py`, there are some predefined coordinate frames which are specified by the `framespec` keyword. Examples are 'WGS-84' and 'GRS-80' geospatial coordinate frames, where natural coordinates are latitude, longitude and height and natural orientation lets the x-axis of subframes point northward. If `framespec` is not given, a CartesianCoordinateFrame is assumed, where natural and cartesian coordinates are similar.
```yaml
#Example how to specify a coordinate frame
framename: EARTH
framespec: WGS-84
position: [0,0,0]
rotation: [0,0,0]
```

### Mounttree structure
A mounttree is a tree-like datastructure containing different coordinate frames with their relative orientation (see https://nbn-resolving.org/urn:nbn:de:bvb:19-261616, sec. 3.3.2). 
There must be exactly one root coordinate frame in the tree. Each coordinate frame can have any number of child frames, specified by the `subframes` keyword.
A child frame in the tree needs a position and rotation relative to the parent.

Positions must be given as three floating point numbers in natural coordinates of the parent frame.

Rotations are assumed to be three floating point numbers, interpreted as euler angles relative to the local frame orientation of the parent frame at the childframe's position. 
Euler angles are in the "roll, pitch, yaw" convention, i.e. as sequence of rotations around 'x', 'y' and 'z' axis. Alternatively, a single string of a form similar to `Ry(-85deg)*Rz(-90deg)` can be provided at initialization, defining the rotation as a product of rotation matrices.
```yaml
framename: EARTH
framespec: WGS-84
subframes:
    - framename: HALO
        position: [10.2,20.7,6000]
        rotation: [0,0,90]
        subframes:
            - framename: VNIR
            position: [0, 0, 0]
            rotation: Ry(-85deg)*Rz(-90deg)
```

### Open variables
Instead of defining position and rotation of frames as three floating point numbers, some of the numbers can also be replaced by arbitrary strings.
In this case, the strings are interpreted as open variables and must be associated to numbers with the "universe.update()" method before they can be used for transformations. If a transformation is requested and open variables without associated numbers are found to be necessary for this transformation, an error is thrown.
```yaml
#Examples for open variables
framename: HALO
position: [lat, lon, height]
rotation: [roll, pitch, yaw]
```
