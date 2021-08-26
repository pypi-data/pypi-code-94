"""compas_mobile_robot_reloc"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from os import path
from distutils.version import LooseVersion

import compas
import compas.plugins

from .measurement_point import *  # noqa: F401, F403
from .three_pts_localization import *  # noqa: F401, F403

if not compas.IPY:
    from .arbitrary_pts_localization import *  # noqa: F401, F403

PKG_ROOT = path.dirname(__file__)
REPO_ROOT = path.abspath(path.join(PKG_ROOT, ".."))

compas.PRECISION = "12f"


def _get_version():  # type: () -> str
    # from https://smarie.github.io/python-getversion/#package-versioning-best-practices
    # and setuptools_scm docs
    try:
        # import from _version.py generated by setuptools_scm during release
        from ._version import version

        return version
    except ImportError:
        try:
            from importlib.metadata import version  # type: ignore [no-redef]

            return version("rapid-clay-formations-fab")  # type: ignore [operator]
        except ImportError:
            try:
                from importlib_metadata import version  # type: ignore [no-redef]

                return version("rapid-clay-formations-fab")  # type: ignore [operator]
            except ImportError:
                pass

    return "src"


@compas.plugins.plugin(category="install")
def installable_rhino_packages():
    return ["compas_mobile_robot_reloc"]


__author__ = "Gramazio Kohler Research"
__copyright__ = "2020 Gramazio Kohler Research"
__license__ = "MIT License"
__email__ = "anton@tetov.se"
__version__ = _get_version()


__all_plugins__ = ["compas_mobile_robot_reloc.rhino_install"]

# Backport for path related bug with compas.rpc.Proxy
# See https://github.com/compas-dev/compas/issues/701
# & https://github.com/compas-dev/compas/pull/720


def _fixed_prepare_environment(env=None):
    """Prepares an environment context to run Python on.

    Copied from https://github.com/compas-dev/compas/blob/v0.19.2/src/compas/_os.py

    If Python is being used from a conda environment, this is roughly equivalent
    to activating the conda environment by setting up the correct environment
    variables.

    Parameters
    ----------
    env : dict, optional
        Dictionary of environment variables to modify. If ``None`` is passed, then
        this will create a copy of the current ``os.environ``.

    Returns
    -------
    dict
        Updated environment variable dictionary.
    """
    from compas import WINDOWS
    from compas._os import PYTHON_DIRECTORY
    from compas._os import CONDA_EXE

    if env is None:
        env = os.environ.copy()

    if PYTHON_DIRECTORY:
        if WINDOWS:
            lib_bin = os.path.join(PYTHON_DIRECTORY, "Library", "bin")
        else:
            lib_bin = os.path.join(PYTHON_DIRECTORY, "bin")

        if os.path.exists(lib_bin) and lib_bin not in env["PATH"]:
            env["PATH"] = lib_bin + os.pathsep + env["PATH"]

    if CONDA_EXE:
        env["CONDA_EXE"] = CONDA_EXE

    return env


if LooseVersion(compas.__version__) < LooseVersion("0.19.2"):
    import compas._os

    compas._os.prepare_environment = _fixed_prepare_environment
