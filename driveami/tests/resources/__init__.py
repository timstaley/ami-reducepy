import os
from driveami.reduce import ensure_dir


ami_rootdir = '/data2/ami'
driveami_testdir = '/tmp/driveami-test'
_test_data_dir = os.path.dirname(__file__)
_symlink_target = '/tmp/driveami-test/LA'


def setup_testdata_symlink(test_data_dir=_test_data_dir,
                           symlink_target=_symlink_target):
    ensure_dir(os.path.dirname(symlink_target))
    if not os.path.islink(symlink_target):
        os.symlink(test_data_dir, symlink_target)

    la_data_dir = os.path.join(symlink_target,'data')
    la_gains_data_dir = os.path.join(symlink_target,'gains')
    data_dict = {'AMILA_DATA':la_data_dir,
                 'AMILA_GAINS':la_gains_data_dir,}
    return data_dict


j1753_basename = 'J1753-140330.raw'
SWIFT_590206_basename =  'SWIFT_590206-140314.raw'
file_info_dump =  os.path.join(_test_data_dir, 'filedump.pck')
