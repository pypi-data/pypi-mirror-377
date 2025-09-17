import yaml
import mounttree.mounttree as mnt
import numpy as np
import re


def load_mounttree(filename):
    with open(filename) as f:
        tree = yaml.safe_load(f)
    name = tree['description']['name']
    tree = tree['mounttree']
    root_frame = create_from_yaml(tree)
    universe = mnt.CoordinateUniverse(name, root_frame)
    return universe


def create_from_yaml(mounttree):
    try:
        rhs = mnt.coordinate_lib[mounttree['framespec']]()
    except KeyError:
        rhs = mnt.CartesianCoordinateFrame()
    rhs.name = mounttree['framename']
    if 'position' in mounttree:
        rhs.pos = mounttree['position']
    if 'rotation' in mounttree:
        rot_input = mounttree['rotation']
        if isinstance(rot_input, list):
            assert (len(rot_input) == 3)
            rhs.euler = rot_input
        if isinstance(rot_input, str):
            rhs.rotation = convert_rot_string(rot_input)
    if 'subframes' in mounttree:
        for subframe in mounttree['subframes']:
            rhs.add_child(create_from_yaml(subframe))
    return rhs


def convert_rot_string(rot_string):
    reRotPrimitive = re.compile(
            '^R([xyz])\\((-?[0-9]+(?:\\.[0-9]*)?)((?:deg|rad)?)\\)$')
    rsplit = rot_string.split("*")
    loc_count = 1  # define number of positions that mounttree is updated with
    rot = mnt.Rotation.Identity(loc_count)
    for s in rsplit:
        m = reRotPrimitive.match(s)
        assert (m is not None)
        axis, angle, unit = m.groups()
        angle = float(angle)
        if unit == 'deg':
            angle = np.deg2rad(angle)
        rot = mnt.Rotation.fromAngle(angle, axis, loc_count)*rot
    return rot
