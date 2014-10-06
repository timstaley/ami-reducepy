import unittest
from unittest import TestCase
import os
import driveami
import driveami.tests.resources as resources
import driveami.keys as keys

import pickle


class TestGrouping(TestCase):
    def setUp(self):
        env_extras = resources.setup_testdata_symlink()
        self.reduce = driveami.Reduce(ami_rootdir=resources.ami_rootdir,
                                      additional_env_variables=env_extras)
        with open(resources.file_info_dump) as f:
            file_info_data = pickle.load(f)
        self.reduce.files = file_info_data


    def test_grouping_by_target_id(self):
        groups = self.reduce.group_obs_by_target_id()
        #Regression test, assuming fixed data dump
        self.assertEqual(len(groups), 178)

    def test_grouping_by_pointing(self):
        id_groups = self.reduce.group_obs_by_target_id()
        pointing_groups = self.reduce.group_target_ids_by_pointing(id_groups)
        #Regression test, assuming fixed data dump
        self.assertEqual(len(pointing_groups.keys()),130)
        


