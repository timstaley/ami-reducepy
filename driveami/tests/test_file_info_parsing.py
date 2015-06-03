from __future__ import print_function

from unittest import TestCase
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
import driveami
import driveami.tests.resources as resources
import driveami.keys as keys
import StringIO

class TestFileListing(TestCase):
    def setUp(self):
        env_extras = resources.setup_testdata_symlink()
        self.reduce = driveami.Reduce(ami_rootdir=resources.ami_rootdir,
                                      additional_env_variables=env_extras)

    def test_list_files(self):
        self.assertEqual(len(self.reduce.files), 3)
        self.assertEqual(self.reduce.files.values()[0], {})

        self.reduce.load_obs_info()
        self.assertNotEqual(self.reduce.files.values()[0], {})

        s = StringIO.StringIO()
        rawfile_dict = { fname:driveami.make_serializable(info) for fname, info
                         in self.reduce.files.iteritems()}
        driveami.save_rawfile_listing(rawfile_dict, s)
        print(s.getvalue())


class TestRegularFileInfo(TestCase):
    @classmethod
    def setUpClass(cls):
        env_extras = resources.setup_testdata_symlink()
        cls.reduce = driveami.Reduce(ami_rootdir=resources.ami_rootdir,
                                      additional_env_variables=env_extras)
        cls.reduce.load_obs_info()
        # print("Files:")
        # for f in self.reduce.files:
        #     # print(f, self.reduce.files[f])
        #     # print(self.reduce.files[f][keys.raw_obs_text])
        #     d = self.reduce.files[f][keys.duration]
        #     print(d, type(d))
        #     if keys.warnings in self.reduce.files[f]:
        #         print(self.reduce.files[f][keys.warnings])
        #     print()

    def test_regular_file_timestamps(self):
        obs = "SWIFT_590206-140305.raw"
        info = self.reduce.files[obs]
        self.assertAlmostEqual(info[keys.duration], 1.08361, places=5)
        self.assertEqual(info[keys.time_ut],
                (datetime(2014, 3, 5, 13, 55, 49), datetime(2014, 3, 5, 15, 0, 50)))

    def test_incomplete_file_timestamps(self):
        obs = "SWIFT_636005-150326.raw"
        info = self.reduce.files[obs]
        # print(info[keys.raw_obs_text])
        # print(info[keys.warnings])
        self.assertAlmostEqual(info[keys.duration], 0.08583, places=5)
        self.assertEqual(info[keys.time_ut],
            (datetime(2015, 3, 26, 0, 21, 13), datetime(2015, 3, 26, 0, 26, 22)))

