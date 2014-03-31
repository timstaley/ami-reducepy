import unittest
from unittest import TestCase
import os
import shutil
import driveami
import driveami.tests.resources as resources
import driveami.keys as keys

@unittest.skip
class TestStandardReduction(TestCase):
    def setUp(self):
        env_extras = resources.setup_testdata_symlink()
        self.reduce = driveami.Reduce(ami_rootdir=resources.ami_rootdir,
                                      additional_env_variables=env_extras)
        self.rawfile_basename = resources.rawfile_basenames[0]

    def tearDown(self):
#        shutil.rmtree(resources.driveami_testdir)
        pass

    def test_reduction(self):
        file_info = driveami.process_rawfile(self.rawfile_basename,
                                 output_dir=resources.driveami_testdir,
                                 reduce=self.reduce)
        output_fits = file_info[keys.target_uvfits]
        self.assertTrue(os.path.isfile(output_fits))
