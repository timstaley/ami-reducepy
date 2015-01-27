"""Defines various shell environments for use with subprocess.

We generally grab the current shell env, then update paths with package specific
directories.

This is a nice way to ensure everything happens in its own sandbox,
without confusing interaction between conflicting variables.

Note the utility functions are overkill for the AMI package, but
are handy when defining multiple environments.
"""
import os

default_ami_dir = os.environ.get('AMI_DIR',os.path.expanduser("~/ami"))
default_output_dir = os.environ.get('AMI_RESULTS',
                                   os.path.expanduser("~/ami_results"))

def _append_to_path(env, path, extra_dir):
    """Deal nicely with empty path, minimise boilerplating."""
    env_dirs = env.get(path, '').split(':')
    env_dirs.append(extra_dir)
    env[path] = ':'.join(env_dirs)

def _add_bin_lib_python(env, package_group_dir, include_python=True):
    """Add the bin, lib, (and optionally python-packages) subdirs of
    `package_group_dir` to the relevant environment paths."""
    _append_to_path(env, "PATH", os.path.join(package_group_dir, 'bin'))
    _append_to_path(env, 'LD_LIBRARY_PATH',
                    os.path.join(package_group_dir, 'lib'))
    if include_python:
        _append_to_path(env, 'PYTHONPATH',
                        os.path.join(package_group_dir, 'python-packages'))

def init_ami_env(ami_topdir):
    """Returns an environment dictionary configured for AMI-reduce execution.
        
    `ami_topdir` should be the top directory of the AMI-reduce installation.
    
    """
    ami_env = {}
    ami_env["AMI_DIR"] = ami_topdir
    _add_bin_lib_python(ami_env, ami_topdir, include_python=False)
    ami_env["PGPLOT_DIR"] = os.path.join(ami_topdir , "lib/pgplot")
    ami_env["PGPLOT_FONT"] = os.path.join(ami_topdir , "lib/pgplot/grfont.dat")
    ami_env["PGPLOT_RGB"] = os.path.join(ami_topdir , "lib/pgplot/rgb.txt")
    ami_env["PGPLOT_DEV"] = "/xwin"
    return ami_env
