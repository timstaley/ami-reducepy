from unittest import TestCase
import os
import shutil
import driveami
import driveami.tests.resources as resources
import driveami.keys as keys
import logging
logging.basicConfig()

#@unittest.skip
class TestStandardReduction(TestCase):
    def setUp(self):
        env_extras = resources.setup_testdata_symlink()
        self.reduce = driveami.Reduce(ami_rootdir=resources.ami_rootdir,
                                      additional_env_variables=env_extras)

    def tearDown(self):
       # shutil.rmtree(resources.driveami_testdir)
        pass

    def test_standard_reduction_j1753(self):
        file_info = driveami.process_rawfile(resources.j1753_basename,
                                 output_dir=resources.driveami_testdir,
                                 reduce=self.reduce)
        output_fits = file_info[keys.target_uvfits]
        self.assertTrue(os.path.isfile(output_fits))


class TestCalInterParsing(TestCase):
    def setUp(self):
        env_extras = resources.setup_testdata_symlink()
        self.reduce = driveami.Reduce(ami_rootdir=resources.ami_rootdir,
                                      additional_env_variables=env_extras)
        self.rawfile_basename = resources.SWIFT_590206_basename

    def tearDown(self):
#        shutil.rmtree(resources.driveami_testdir)
        pass

    def test_reduction(self):
        file_info = driveami.process_rawfile(self.rawfile_basename,
                                 output_dir=resources.driveami_testdir,
                                 reduce=self.reduce)
        output_fits = file_info[keys.target_uvfits]
        self.assertTrue(os.path.isfile(output_fits))
