# -*- coding: utf-8 -*-

from unittest import TestCase
import unittest
import numpy.testing as npt
import numpy as np
import mounttree.mounttree as mnt


class BasicTests(TestCase):
    def test_forward_rotation(self):
        halo = mnt.CartesianCoordinateFrame()
        halo.name = 'HALO'
        vnir = mnt.CartesianCoordinateFrame()
        vnir.name = 'VNIR'
        vnir.rotation = mnt.Rotation.fromAngle(np.pi/2, 'z', 1)
        halo.add_child(vnir)
        universe = mnt.CoordinateUniverse('universe', halo)
        child_transform = halo.get_transform_child(vnir)
        transform = universe.get_transformation('VNIR', 'HALO')
        npt.assert_almost_equal(child_transform.apply_direction(1, 0, 0),
                                [0, 1, 0])
        npt.assert_almost_equal(transform.apply_direction(1, 0, 0),
                                [0, 1, 0])

    def test_find_path_to_frame(self):
        halo = mnt.CartesianCoordinateFrame()
        halo.name = 'HALO'
        vnir = mnt.CartesianCoordinateFrame()
        vnir.name = 'VNIR'
        halo.add_child(vnir)
        universe = mnt.CoordinateUniverse('universe', halo)
        path = universe.find_path_to_frame('VNIR')
        self.assertIs(vnir, path[0])
        self.assertEqual(len(path), 1)

    def test_find_path_to_frame_deep(self):
        halo = mnt.CartesianCoordinateFrame()
        halo.name = 'HALO'
        vnir = mnt.CartesianCoordinateFrame()
        vnir.name = 'VNIR'
        swir = mnt.CartesianCoordinateFrame()
        swir.name = 'SWIR'
        containment = mnt.CartesianCoordinateFrame()
        containment.name = 'CONTAINMENT'
        containment.add_child(vnir)
        containment.add_child(swir)
        halo.add_child(containment)
        universe = mnt.CoordinateUniverse('universe', halo)
        path = universe.find_path_to_frame('SWIR')
        path2 = universe.find_path_to_frame('VNIR')
        self.assertIs(swir, path[1])
        self.assertIs(vnir, path2[1])
        self.assertIs(containment, path[0])
        self.assertEqual(len(path), 2)

    def test_backward_rotation(self):
        halo = mnt.CartesianCoordinateFrame()
        halo.name = 'HALO'
        vnir = mnt.CartesianCoordinateFrame()
        vnir.name = 'VNIR'
        vnir.rotation = mnt.Rotation.fromAngle(np.pi/2, 'z', 1)
        halo.add_child(vnir)
        universe = mnt.CoordinateUniverse('universe', halo)
        transform = universe.get_transformation('HALO', 'VNIR')
        npt.assert_almost_equal(transform.apply_direction(0, 1, 0), [1, 0, 0])

    def test_zig_zag_transform(self):
        halo = mnt.CartesianCoordinateFrame()
        halo.name = 'HALO'
        vnir = mnt.CartesianCoordinateFrame()
        vnir.name = 'VNIR'
        vnir.rotation = mnt.Rotation.fromAngle(np.pi/2, 'z', 1)
        swir = mnt.CartesianCoordinateFrame()
        swir.name = 'SWIR'
        swir.rotation = mnt.Rotation.fromAngle(-np.pi/2, 'z', 1)
        halo.add_child(vnir)
        halo.add_child(swir)
        universe = mnt.CoordinateUniverse('universe', halo)
        transform = universe.get_transformation('SWIR', 'VNIR')
        npt.assert_almost_equal(transform.apply_direction(0, 1, 0), [0, -1, 0])

    def test_double_transform(self):
        halo = mnt.CartesianCoordinateFrame()
        halo.name = 'HALO'
        intermediate = mnt.CartesianCoordinateFrame()
        intermediate.name = 'INTER'
        intermediate.rotation = mnt.Rotation.fromAngle(np.pi/2, 'z', 1)
        swir = mnt.CartesianCoordinateFrame()
        swir.name = 'SWIR'
        swir.rotation = mnt.Rotation.fromAngle(np.pi/2, 'z', 1)
        intermediate.add_child(swir)
        halo.add_child(intermediate)
        universe = mnt.CoordinateUniverse('uni', halo)
        transform = universe.get_transformation('HALO', 'SWIR')
        npt.assert_almost_equal(transform.apply_direction(0, 1, 0), [0, -1, 0])

    def test_forward_shift(self):
        a = mnt.CartesianCoordinateFrame()
        b = mnt.CartesianCoordinateFrame()
        a.name = 'a'
        b.name = 'b'
        b.pos = [1, 2, 0]
        a.add_child(b)
        universe = mnt.CoordinateUniverse('uni', a)
        transform = universe.get_transformation('b', 'a')
        npt.assert_almost_equal(transform.apply_point(1, 0, 0), [2, 2, 0])

    def test_backward_shift(self):
        a = mnt.CartesianCoordinateFrame()
        b = mnt.CartesianCoordinateFrame()
        a.name = 'a'
        b.name = 'b'
        b.pos = [1, 2, 0]
        a.add_child(b)
        universe = mnt.CoordinateUniverse('uni', a)
        transform = universe.get_transformation('a', 'b')
        npt.assert_almost_equal(transform.apply_point(2, 0, 0), [1, -2, 0])


class TransformTest(TestCase):
    def test_rotation_inverse(self):
        rot = mnt.Rotation.fromAngle(np.deg2rad(77), 'x', 1)
        rot = mnt.Rotation.fromAngle(np.deg2rad(48), 'z', 1) * rot
        assert (isinstance(rot, mnt.Rotation))
        roti = rot.invert()
        ident = rot * roti
        npt.assert_almost_equal(ident.M[..., 0], np.eye(4))

    def test_translation_inverse(self):
        trans = mnt.Translation.fromPoint([2, 5, 77.8], 1)
        assert (isinstance(trans, mnt.Translation))
        transi = trans.invert()
        ident = trans*transi
        npt.assert_almost_equal(ident.M, np.eye(4).reshape(4, 4, 1))

    def test_transform_inverse(self):
        trans = mnt.Translation.fromPoint([2, 5, 77.8], 1)
        rot = mnt.Rotation.fromAngle(np.deg2rad(77), 'x', 1)
        rot = mnt.Rotation.fromAngle(np.deg2rad(48), 'z', 1) * rot
        transform = rot * trans * rot
        assert (type(transform) is mnt.Transform)
        transformi = transform.invert()
        ident = transform*transformi
        npt.assert_almost_equal(ident.M, np.eye(4).reshape(4, 4, 1))


class EarthTest(TestCase):
    def test_simple_positions(self):
        earth = mnt.coordinate_lib['WGS-84']()
        npt.assert_almost_equal(earth.toCartesian([90, 0, 0]),
                                [0, 0, 6356752.314245])
        npt.assert_almost_equal(earth.toCartesian([0, 0, 0]),
                                [6378137.0, 0, 0])
        npt.assert_almost_equal(earth.toCartesian([0, 270, 0]),
                                [0, -6378137.0, 0])

    def test_direction(self):
        ned2enu = (mnt.Rotation.fromAngle(np.pi/2, 'z', 1) *
                   mnt.Rotation.fromAngle(np.pi, 'x', 1))
        earth = mnt.coordinate_lib['WGS-84']()
        earth.name = 'earth'
        local = mnt.CartesianCoordinateFrame()
        local.name = 'local'
        local.pos = [45, 45, 0]
        local.rotation = ned2enu
        earth.add_child(local)
        check_result = [-0.5, -0.5, np.sqrt(0.5)]
        universe = mnt.CoordinateUniverse('uni', earth)
        transform = universe.get_transformation('local', 'earth')
        npt.assert_almost_equal(transform.apply_direction(0, 1, 0),
                                check_result)

    def test_natural_coordinates(self):
        earth = mnt.coordinate_lib['WGS-84']()
        positions = [[90, 0, 0],
                     [0, 90, 0],
                     [23.45, 17.41, 15.7],
                     [-65.1, 0.5, 20000.8],
                     [5.3, -165.2, 0]]
        for p in positions:
            res = earth.toNatural(earth.toCartesian(p))
            npt.assert_almost_equal(res, p)

    def test_natural_downwards(self):
        earth = mnt.coordinate_lib['WGS-84']()
        ref = np.array([0, 0, 9000])
        cart = earth.toCartesian(ref)
        res = earth.toNatural(cart-np.array([1100, 0, 0]))
        npt.assert_almost_equal(res, np.array([0, 0, 7900]))

    def test_natural_downwards2(self):
        earth = mnt.coordinate_lib['WGS-84']()
        ref = np.array([0, 90, 9000])
        cart = earth.toCartesian(ref)
        res = earth.toNatural(cart-np.array([0, 1100, 0]))
        npt.assert_almost_equal(res, np.array([0, 90, 7900]))

    def test_get_origin_of_subframes(self):
        earth = mnt.coordinate_lib['WGS-84']()
        earth.name = 'earth'
        local = mnt.CartesianCoordinateFrame()
        local.name = 'local'
        local.pos = [45, 45, 0]
        earth.add_child(local)
        universe = mnt.CoordinateUniverse('uni', earth)
        transform = universe.get_transformation('local', 'earth')
        res = transform.apply_point(0, 0, 0)
        npt.assert_almost_equal(
            res,
            universe.get_frame('earth').toCartesian([45, 45, 0]))


class StabilizationTest(TestCase):
    def setUp(self):
        earth = mnt.coordinate_lib['WGS-84']()
        earth.name = 'earth'
        stabilized = mnt.CartesianCoordinateFrame()
        stabilized.name = 'stabilized'
        self.lat = 10.
        self.lon = 15.
        self.height = 7000.
        self.roll = np.pi/6.
        self.pitch = 0  # np.pi/9.
        self.yaw = -np.pi
        stabilized.pos = [self.lat, self.lon, self.height]
        stabilized.euler = [0, 0, np.rad2deg(self.yaw)]
        halo = mnt.CartesianCoordinateFrame()
        halo.name = 'HALO'
        halo.euler = [np.rad2deg(self.roll), np.rad2deg(self.pitch), 0]
        stabilized.add_child(halo)
        earth.add_child(stabilized)
        self.universe = mnt.CoordinateUniverse('uni', earth)

    def test_roll_correction(self):
        transform = self.universe.get_transformation('HALO', 'stabilized')
        res = transform.apply_direction(0, 1, 0)
        npt.assert_almost_equal(res, [0, np.cos(self.roll), np.sin(self.roll)])

    def test_plane2plane(self):
        plane2 = mnt.CartesianCoordinateFrame()
        plane2.name = 'plane2'
        plane2.pos = [10.1, 15.2, 7500.]
        plane2.euler = [0, 0.1, 0.2]
        self.universe.get_frame('earth').add_child(plane2)
        tr1 = self.universe.get_transformation("HALO", 'plane2')
        tr2 = self.universe.get_transformation("plane2", "HALO")
        res1 = tr1.apply_point(0, 0, 0)
        res2 = tr2.apply_point(0, 0, 0)
        res3 = tr2.apply_point(100, 0, 0)
        res4 = tr2.apply_point(*tr1.apply_point(24, 745., 812))
        res2 = np.array(res2)
        res3 = np.array(res3)
        res4 = np.array(res4)

        npt.assert_almost_equal(np.linalg.norm(res1), np.linalg.norm(res2))
        npt.assert_almost_equal(np.linalg.norm(res3 - res2), 100)
        npt.assert_almost_equal(np.linalg.norm(res4 -
                                               np.array([24, 745., 812])),
                                0)


class StabilizationTestMultipleLocations(TestCase):
    def setUp(self):
        earth = mnt.coordinate_lib['WGS-84']()
        earth.loc_count = 2
        earth.name = 'earth'
        stabilized = mnt.CartesianCoordinateFrame()
        stabilized.name = 'stabilized'
        stabilized.loc_count = 2
        self.lat = [10., 10.]
        self.lon = [15., 15.]
        self.height = [7000., 7000.]
        self.roll = [np.pi/6., np.pi/6.]
        self.pitch = [0, 0]  # np.pi/9.
        self.yaw = [-np.pi, -np.pi]
        self.loc_count = 2
        stabilized.pos = [self.lat, self.lon, self.height]
        stabilized.euler = [[0, 0], [0, 0], np.rad2deg(self.yaw)]
        halo = mnt.CartesianCoordinateFrame()
        halo.name = 'HALO'
        halo.euler = [np.rad2deg(self.roll), np.rad2deg(self.pitch), [0, 0]]
        halo.loc_count = 2
        stabilized.add_child(halo)
        earth.add_child(stabilized)
        self.universe = mnt.CoordinateUniverse('uni', earth, loc_count=2)

    def test_roll_correction_multiple_locations(self):
        transform = self.universe.get_transformation('HALO', 'stabilized')
        res = transform.apply_direction(0, 1, 0)
        npt.assert_almost_equal(res, [[0, 0], np.cos(self.roll),
                                      np.sin(self.roll)])

    def test_plane2plane_multiple_locations(self):
        plane2 = mnt.CartesianCoordinateFrame()
        plane2.name = 'plane2'
        plane2.pos = [[10.1, 10.1], [15.2, 15.2], [7500., 7500.]]
        plane2.euler = [[0, 0], [0.1, 0.1], [0.2, 0.2]]
        plane2.loc_count = 2
        self.universe.get_frame('earth').add_child(plane2)
        tr1 = self.universe.get_transformation("HALO", 'plane2')
        tr2 = self.universe.get_transformation("plane2", "HALO")
        res1 = tr1.apply_point(0, 0, 0)
        res2 = tr2.apply_point(0, 0, 0)
        res3 = tr2.apply_point(100, 0, 0)
        res4 = tr2.apply_point(*tr1.apply_point(24, 745., 812))
        res2 = np.array(res2)
        res3 = np.array(res3)
        res4 = np.array(res4)

        npt.assert_almost_equal(np.linalg.norm(res1), np.linalg.norm(res2))
        npt.assert_almost_equal(np.linalg.norm((res3 - res2)[..., 0]), 100)
        npt.assert_almost_equal(np.linalg.norm((res3 - res2)[..., 1]), 100)
        npt.assert_almost_equal(np.linalg.norm(res4 -
                                               np.array([[24, 24],
                                                         [745., 745.],
                                                         [812, 812]])), 0)


class Ball(TestCase):
    def setUp(self):
        ball = mnt.OblateEllipsoidFrame(1, 1)
        ball.name = 'ball'
        local = mnt.CartesianCoordinateFrame()
        local.name = 'local'
        ball.add_child(local)
        self.universe = mnt.CoordinateUniverse('uni', ball)
        self.tr1 = self.universe.get_transformation('local', 'ball')

    def test_position_transformation(self):
        res1 = self.tr1.apply_point(0., 0., 0.)
        npt.assert_almost_equal(res1, [1., 0., 0.])
        res2 = self.tr1.apply_point(0., 1., 0.)
        npt.assert_almost_equal(res2, [1., 1., 0.])
        res3 = self.tr1.apply_point(0., 1., 0.)
        npt.assert_almost_equal(res3, [1., 1., 0.])
        res4 = self.tr1.apply_point(0., 0., 1.)
        npt.assert_almost_equal(np.linalg.norm(res4), 1e-9)
        res5 = self.tr1.apply_point(1., 0., 1.)
        npt.assert_almost_equal(res5, [0., 0., 1.])

    def test_position_transformation_pointArray(self):
        x = np.array([[0, 0, 0], [0, 1, 1]])
        y = np.array([[0, 1, 1], [0, 0, 0]])
        z = np.array([[0, 0, 0], [1, 1, 1]])
        resx, resy, resz = self.tr1.apply_point(x, y, z)
        npt.assert_equal(resx.shape, x.shape)
        npt.assert_equal(resy.shape, y.shape)
        npt.assert_equal(resz.shape, z.shape)
        npt.assert_almost_equal([resx[0, 0], resy[0, 0], resz[0, 0]],
                                [1., 0., 0.])
        npt.assert_almost_equal([resx[0, 1], resy[0, 1], resz[0, 1]],
                                [1., 1., 0.])
        npt.assert_almost_equal([resx[0, 2], resy[0, 2], resz[0, 2]],
                                [1., 1., 0.])
        npt.assert_almost_equal(np.linalg.norm([resx[1, 0],
                                                resy[1, 0],
                                                resz[1, 0]]),
                                1e-9)
        npt.assert_almost_equal([resx[1, 1], resy[1, 1], resz[1, 1]],
                                [0., 0., 1.])
        npt.assert_almost_equal([resx[1, 2], resy[1, 2], resz[1, 2]],
                                [0., 0., 1.])

    def test_transform_at_height(self):
        self.universe.get_frame('local').pos = [0., 0., 10.]
        self.tr1 = self.universe.get_transformation('local', 'ball')
        res1 = self.tr1.apply_point(0., 0., 0.)
        npt.assert_almost_equal(res1, [11, 0, 0])
        res2 = self.tr1.apply_point(1., 0., 0.)
        npt.assert_almost_equal(res2, [11., 0., 1.])
        res3 = self.tr1.apply_point(0., 1., 0.)
        npt.assert_almost_equal(res3, [11., 1., 0.])
        res4 = self.tr1.apply_point(0., 0., 11.)
        npt.assert_almost_equal(np.linalg.norm(res4), 1e-9)

    def test_position_transform_on_north_pole(self):
        self.universe.get_frame('local').pos = [90., 0., 0.]
        self.tr1 = self.universe.get_transformation('local', 'ball')
        res1 = self.tr1.apply_point(0., 0., 0.)
        npt.assert_almost_equal(res1, [0., 0., 1.])
        res2 = self.tr1.apply_point(1., 0., 0.)
        npt.assert_almost_equal(res2, [-1., 0., 1.])
        res3 = self.tr1.apply_point(0., 1., 0.)
        npt.assert_almost_equal(res3, [0., 1., 1.])
        res4 = self.tr1.apply_point(0., 0., 1.)
        npt.assert_almost_equal(np.linalg.norm(res4), 1e-9)

    def test_position_transform_45_west(self):
        self.universe.get_frame('local').pos = [0., -45., 0.]
        self.tr1 = self.universe.get_transformation('local', 'ball')
        res1 = self.tr1.apply_point(0., 0., 0.)
        npt.assert_almost_equal(res1,
                                [np.sin(np.pi / 4), -np.sin(np.pi / 4), 0])
        res2 = self.tr1.apply_point(1., 0., 0.)
        npt.assert_almost_equal(res2,
                                [np.sin(np.pi / 4), -np.sin(np.pi / 4), 1])
        res3 = self.tr1.apply_point(0., 1., 0.)
        npt.assert_almost_equal(res3,
                                [np.sqrt(2), 0., 0.])
        res4 = self.tr1.apply_point(0., 0., 1.)
        npt.assert_almost_equal(np.linalg.norm(res4), 1e-9)

    def test_position_transform_nested_on_north_pole(self):
        ball = mnt.OblateEllipsoidFrame(1, 1)
        ball.name = 'ball'
        intermediate = mnt.CartesianCoordinateFrame()
        intermediate.name = 'intermediate'
        local = mnt.CartesianCoordinateFrame()
        local.name = 'local'
        local.pos = [1, 0, 1]
        intermediate.add_child(local)
        ball.add_child(intermediate)
        universe = mnt.CoordinateUniverse('uni', ball)
        tr1 = universe.get_transformation('local', 'ball')
        res1 = tr1.apply_point(0., 0., 0.)
        npt.assert_almost_equal(res1, [0, 0, 1])
        res2 = tr1.apply_point(1., 0., 0.)
        npt.assert_almost_equal(res2, [0, 0, 2])
        res3 = tr1.apply_point(0., 1., 0.)
        npt.assert_almost_equal(res3, [0, 1, 1])
        res4 = tr1.apply_point(-1, 0, 0)
        npt.assert_almost_equal(np.linalg.norm(res4), 1e-9)


if __name__ == '__main__':
    unittest.main()
