from unittest import TestCase
import driveami
import json

from StringIO import StringIO

import logging
logging.basicConfig(level=logging.DEBUG)


class TestListingSerialization(TestCase):
    def setUp(self):
        self.testdata = {'foo1':{'bar':'baz1'},
                         'foo2':{'bar':'baz2'},
                         }

    def test_check_for_magic_key(self):
        s = StringIO()
        json.dump(self.testdata, s)
        with self.assertRaises(ValueError):
            driveami.load_listing(s)

    def test_rawfiles_roundtrip(self):
        s = StringIO()
        driveami.save_rawfile_listing(self.testdata, s)

        listing, datatype = driveami.load_listing(StringIO(s.getvalue()))
        self.assertEqual(datatype, driveami.Datatype.ami_la_raw)
        self.assertEqual(listing, self.testdata)

    def test_calfiles_roundtrip(self):
        s = StringIO()
        driveami.save_calfile_listing(self.testdata, s)
        listing, datatype = driveami.load_listing(StringIO(s.getvalue()))
        self.assertEqual(datatype, driveami.Datatype.ami_la_calibrated)
        self.assertEqual(listing, self.testdata)

    def test_expected_raw(self):
        s = StringIO()
        driveami.save_calfile_listing(self.testdata, s)
        with self.assertRaises(ValueError):
            listing, datatype = driveami.load_listing(StringIO(s.getvalue()),
                              expected_datatype=driveami.Datatype.ami_la_raw)

    def test_expected_cal(self):
        s = StringIO()
        driveami.save_rawfile_listing(self.testdata, s)
        with self.assertRaises(ValueError):
            listing, datatype = driveami.load_listing(StringIO(s.getvalue()),
                              expected_datatype=driveami.Datatype.ami_la_calibrated)