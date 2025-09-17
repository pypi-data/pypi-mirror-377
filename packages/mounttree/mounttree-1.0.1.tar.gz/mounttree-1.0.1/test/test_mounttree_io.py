from unittest import TestCase
import unittest
import numpy.testing as npt
import mounttree as mio
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class TestMountTree(TestCase):
    def setUp(self):
        self.universe = mio.load_mounttree(os.path.join(basedir,
                                                        'testmounttree.yaml'))

    def test_updates(self):
        self.universe.update(lat=0, lon=0, height=10, roll=0, pitch=0, yaw=0)
        earth = self.universe.get_frame('EARTH')
        npt.assert_almost_equal(self.universe.get_frame('HALO').pos,
                                [0, 0, 10])
        tr1 = self.universe.get_transformation('HALO', 'EARTH')
        self.universe.update(height=20)
        tr2 = self.universe.get_transformation('HALO', 'EARTH')
        npt.assert_almost_equal(earth.toNatural(tr1.apply_point(0, 0, 0)),
                                [0, 0, 10])
        npt.assert_almost_equal(earth.toNatural(tr2.apply_point(0, 0, 0)),
                                [0, 0, 20])

    def test_updates2(self):
        self.universe.set_variables(lat=0, lon=0, roll=0, pitch=0, yaw=0)
        earth = self.universe.get_frame('EARTH')

        # height not set internally
        with self.assertRaises(KeyError):
            self.universe.get_transformation('HALO', 'EARTH')

        # height set externally
        tr1 = self.universe.get_transformation('HALO', 'EARTH', height=10)

        with self.assertRaises(KeyError):
            self.universe.get_transformation('HALO', 'EARTH')

        # height set internally
        self.universe.update(height=20)
        tr2 = self.universe.get_transformation('HALO', 'EARTH')

        # height temporarily overwritten externally
        tr3 = self.universe.get_transformation('HALO', 'EARTH', height=30)
        npt.assert_almost_equal(earth.toNatural(tr1.apply_point(0, 0, 0)),
                                [0, 0, 10])
        npt.assert_almost_equal(earth.toNatural(tr2.apply_point(0, 0, 0)),
                                [0, 0, 20])
        npt.assert_almost_equal(earth.toNatural(tr3.apply_point(0, 0, 0)),
                                [0, 0, 30])

    def test_updates3(self):
        # Update mounttree with two HALO positions
        self.universe.update(lat=[0, 0], lon=[0, 0], height=[10, 50],
                             roll=[0, 0], pitch=[0, 0], yaw=[0, 0])
        earth = self.universe.get_frame('EARTH')
        npt.assert_almost_equal(self.universe.get_frame('HALO').pos,
                                [[0, 0], [0, 0], [10, 50]])
        tr1 = self.universe.get_transformation('HALO', 'EARTH')
        self.universe.update(height=[20, 20])
        tr2 = self.universe.get_transformation('HALO', 'EARTH')
        npt.assert_almost_equal(earth.toNatural(tr1.apply_point(0, 0, 0)),
                                [[0, 0], [0, 0], [10, 50]])
        npt.assert_almost_equal(earth.toNatural(tr2.apply_point(0, 0, 0)),
                                [[0, 0], [0, 0], [20, 20]])


if __name__ == '__main__':
    unittest.main()
