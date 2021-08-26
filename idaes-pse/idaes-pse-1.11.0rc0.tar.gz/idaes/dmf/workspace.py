#################################################################################
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES), and is copyright (c) 2018-2021
# by the software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia University
# Research Corporation, et al.  All rights reserved.
#
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and
# license information.
#################################################################################
"""
Workspace classes and functions.
"""
# stdlib
import logging
import os
import re
from typing import List
from urllib.parse import urlparse
import uuid

# third-party
import jsonschema
import yaml

# local
from .errors import (
    ParseError,
    WorkspaceError,
    WorkspaceNotFoundError,
    WorkspaceConfNotFoundError,
    WorkspaceConfMissingField,
    WorkspaceCannotCreateError,
)
from .util import yaml_load

__author__ = "Dan Gunter <dkgunter@lbl.gov>"

_log = logging.getLogger(__name__)

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "http://idaes.org/dmf/workspace-config",
    "type": "object",
    "properties": {
        "_id": {"description": "Unique workspace identifier", "type": "string"},
        "htmldocs": {
            "description": "HTML documentation paths",
            "type": "array",
            "items": {
                "type": "string",
                "description": "directory containing Sphinx HTML docs",
            },
            "default": "https://idaes-pse.readthedocs.io/en/stable,{dmf_root}/docs/build/html"
        },
        "description": {
            "description": "A human-readable description of the workspace",
            "type": "string",
        },
        "name": {"description": "A short name for the workspace", "type": "string"},
    },
}


class Fields(object):
    """Workspace configuration fields.
    """

    DOC_HTML_PATH = "htmldocs"  # path to documentation html dir
    LOG_CONF = "logging"  # logging config


class Workspace(object):
    """DMF Workspace.

    In essence, a workspace is some information at the root of a directory
    tree, a database (currently file-based, so also in the directory tree)
    of *Resources*, and a set of files associated with these resources.

    **Workspace Configuration**

    When the DMF is initialized, the workspace is given as a path to a
    directory. In that directory is a special file named ``config.yaml``,
    that contains metadata about the workspace. The very existence of a
    file by that name is taken by the DMF code as an indication that the
    containing directory is a DMF workspace::

        /path/to/dmf: Root DMF directory
         |
         +- config.yaml: Configuration file
         +- resourcedb.json: Resource metadata "database" (uses TinyDB)
         +- files: Data files for all resources

    The configuration file is a `YAML`_ formatted file

    .. _YAML: http://www.yaml.org/

    The configuration file defines the following key/value pairs:

        _id
            Unique identifier for the workspace. This is auto-generated by
            the library, of course.
        name
            Short name for the workspace.
        description
            Possibly longer text describing the workspace.
        created
            Date at which the workspace was created, as string in the
            ISO8601 format.
        modified
            Date at which the workspace was last modified, as string in the
            ISO8601 format.
        htmldocs
            Full path to the location of the built (not source) Sphinx HTML
            documentation for the `idaes_dmf` package. See
            DMF Help Configuration for more details.

    There are many different possible "styles" of formatting a list of values
    in YAML, but we prefer the simple block-indented style, where the key is
    on its own line and the values are each indented with a dash:

    .. code-block:: YAML

        _id: fe5372a7e51d498fb377da49704874eb
        created: '2018-07-16 11:10:44'
        description: A bottomless trashcan
        modified: '2018-07-16 11:10:44'
        name: Oscar the Grouch's Home
        htmldocs:
        - '{dmf_root}/doc/build/html/dmf'
        - '{dmf_root}/doc/build/html/models'


    Any paths in the workspace configuration, e.g., for the "htmldocs",
    can use two special variables that will take on values relative to the
    workspace location. This avoids hardcoded paths and makes the workspace
    more portable across environments. ``{ws_root}`` will be replaces with
    the path to the workspace directory, and ``{dmf_root}`` will be replaced
    with the path to the (installed) DMF package.

    The `config.yaml` file will allow keys and values it does not know
    about. These will be accessible, loaded into a Python dictionary,
    via the ``meta`` attribute on the :class:`Workspace` instance.
    This may be useful for
    passing additional user-defined information into the DMF at startup.
    """

    #: Name of configuration file placed in WORKSPACE_DIR
    WORKSPACE_CONFIG = "config.yaml"
    #: Name of ID field
    ID_FIELD = "_id"

    CONF_NAME = "name"  #: Configuration field for name
    CONF_DESC = "description"  #: Configuration field for description
    CONF_CREATED = "created"  #: Configuration field for created date
    CONF_MODIFIED = "modified"  #: Configuration field for modified date

    def __init__(
        self, path, create=False, existing_ok=True, add_defaults=False, html_paths=None
    ):
        """Load or create a workspace rooted at `path`

        Args:
            (str) path: Path for root of workspace
            (bool) create: Create the workspace if it does not exist.
            (bool) existing_ok: If create is True, and the workspace exists, just continue
            (bool) add_defaults: Add default values to new configuration.
                    These values are found in the JSON Schema that is stored in the module variable
                    `CONFIG_SCHEMA`, and substituted by logic in :meth:`WorkspaceConfiguration.get_fields`.
            html_paths: One or more paths to HTML docs (or None)
        Raises:
            WorkspaceNotFoundError: if ws is not found (and create is false)
            WorkspaceConfNotFoundError: if ws config is not found (& ~create)
            WorkspaceConfMissingField: if there is no ID field.
            DMFError: Anything else
        """
        path = os.path.abspath(path)
        self._wsdir = path
        self._conf = os.path.join(self._wsdir, self.WORKSPACE_CONFIG)
        self._cached_conf = None
        if create:
            skip_config = False
            # note: these raise OSError on failure
            try:
                os.mkdir(self._wsdir, 0o770)
            except OSError:
                if not os.path.exists(self._wsdir):
                    raise WorkspaceCannotCreateError(self._wsdir)
                if os.path.exists(self._conf):
                    if existing_ok:
                        _log.info(f"Using existing DMF workspace: {self._conf}")
                        skip_config = True
                    else:
                        raise WorkspaceError(
                            "existing configuration would be "
                            "overwritten: {}".format(self._conf)
                        )
                _log.info(
                    "Using existing path for new DMF workspace: {}".format(self._wsdir)
                )
            if not skip_config:
                try:
                    self._create_new_config(add_defaults)
                except OSError as err:
                    raise WorkspaceError(
                        "while creating new workspace " "configuration: {}".format(err)
                    )
        else:
            # assert that the workspace exists
            try:
                assert os.path.isdir(self._wsdir)
            except AssertionError:
                raise WorkspaceNotFoundError(self._wsdir)
            try:
                assert os.path.isfile(self._conf)
            except AssertionError:
                raise WorkspaceConfNotFoundError(self._conf)
        self._install_dir = self._get_install_dir()
        try:
            self._id = self.meta[self.ID_FIELD]
        except KeyError:
            raise WorkspaceConfMissingField(path, self.ID_FIELD, "ID field")
        if html_paths:
            self.set_doc_paths(html_paths)

    def _create_new_config(self, add_defaults):
        _log.info(f"Create new configuration at '{self._conf}'")
        conf = open(self._conf, 'w')  # create the file
        new_id = uuid.uuid4().hex  # create new unique ID
        conf.write("{}: {}\n".format(self.ID_FIELD, new_id))  # write ID
        conf.close()  # flush and close
        if add_defaults:
            self._configure_defaults()

    def _configure_defaults(self):
        """Add default values to the workspace configuration.

        The default values are provided by the w

        Note: this will *overwrite* any existing values!
        """
        values = {
            key: val
            for key, (desc, val) in WorkspaceConfiguration()
            .get_fields(only_defaults=True)
            .items()
        }
        self.set_meta(values)

    @property
    def wsid(self):
        """Get workspace identifier (from config file).

        Returns:
            str: Unique identifier.
        """
        return self._id

    @staticmethod
    def _get_install_dir():
        fpath = os.path.realpath(__file__)
        fdir = os.path.dirname(fpath)
        idir = os.path.join(fdir, "..", "..")
        return os.path.abspath(idir)

    def set_meta(self, values, remove=None):
        # type: (dict, list) -> None
        """Update metadata with new values.
        
        Args:
            values (dict): Values to add or change
            remove (list): Keys of values to remove.
        """
        d = self._read_conf()
        if remove:
            for key in remove:
                if key in d:
                    del d[key]
                else:
                    _log.warning('Cannot remove "{}": no such key'.format(key))
        d.update(values)
        self._write_conf(d)
        self._cached_conf = d

    @property
    def meta(self):
        # type: () -> dict
        """Get metadata.

        This reads and parses the configuration.
        Therefore, one way to force a config refresh is to
        simply refer to this property, e.g.::

             dmf = DMF(path='my-workspace')
             #  ... do stuff that alters the config ...
             dmf.meta  # re-read/parse the config

        Returns:
            (dict) Metadata for this workspace.
        """
        # Re-read configuration from file
        d = self._read_conf()
        # In sections that contain paths,
        # substitute special variables in the values with
        # the paths for this workspace.
        if Fields.DOC_HTML_PATH in d:
            p = d[Fields.DOC_HTML_PATH]
            if isinstance(p, str):
                p = [p]
            d[Fields.DOC_HTML_PATH] = list(map(self._expand_path, p))
        if Fields.LOG_CONF in d:
            # Look through logging configuration tree, and
            # replace paths in any value whose key is 'output'.
            stack = [(k, d) for k in d]
            while stack:
                key, p = stack.pop()
                if key == "output":
                    p[key] = self._expand_path(p[key])
                elif isinstance(p[key], dict):
                    for key2 in p[key].keys():
                        stack.append((key2, p[key]))
        # Return modified configuration metadata
        return d

    def get_doc_paths(self):
        """Get paths to generated HTML Sphinx docs.

        Returns:
            (list) Paths or empty list if not found.
        """
        paths = self.meta.get(Fields.DOC_HTML_PATH, [])
        if len(paths) and hasattr(paths, "lower"):
            paths = [paths]  # make a str into a list
        return paths

    def set_doc_paths(self, paths: List[str], replace: bool = False):
        """Set paths to generated HTML Sphinx docs.

        Args:
            paths: New paths to add.
            replace: If True, replace any existing paths. Otherwise merge
                     new paths with existing ones.
        """
        existing_paths = self.get_doc_paths()
        if replace:
            new_paths = list(set(existing_paths + paths))
        else:
            new_paths = paths
        if new_paths != existing_paths:
            self.set_meta({Fields.DOC_HTML_PATH: new_paths})

    def _read_conf(self):
        #: type (None) -> dict
        if self._cached_conf is None:
            _log.debug('Load workspace configuration from "{}"'.format(self._conf))
            conf = open(self._conf, "r")
            try:
                contents = yaml_load(conf)
            except Exception as err:
                raise ParseError(
                    'Cannot load config file "{f}": {e}'.format(f=self._conf, e=err)
                )
            if contents is None:  # empty file
                contents = {}
            self._cached_conf = contents
        else:
            contents = self._cached_conf
        if isinstance(contents, str):
            raise ParseError("File contents cannot be simple str ({})".format(contents))
        else:
            return contents.copy()

    def _expand_path(self, path):
        # leave paths bracketed by _underscores_ as-is
        if re.match(r"^_.*_$", path):
            pass
        else:
            # See if this is a file or web URL.
            # Do substitution on file paths, but leave web URLs alone.
            parsed = urlparse(path)
            if (not parsed.netloc) and parsed.path:
                # Do substitution of '{ws_root}' and '{dmf_root}' in the path
                path = os.path.realpath(
                    path.format(ws_root=self.root, dmf_root=self._install_dir)
                )
        return path

    def _write_conf(self, contents):
        #: type (dict) -> None
        conf = open(self._conf, "w")
        yaml.dump(contents, conf, default_flow_style=False)
        conf.close()

    @property
    def root(self):
        """Root path for this workspace.
        This is the path containing the configuration file.
        """
        return self._wsdir

    @property
    def configuration_file(self):
        """Configuration file path.
        """
        return self._conf

    @property
    def name(self):
        return self.meta.get(self.CONF_NAME, "none")

    @property
    def description(self):
        return self.meta.get(self.CONF_DESC, "none")


class WorkspaceConfiguration(object):
    """Interface to the :data:`CONFIG_SCHEMA` JSON Schema that specifies the fields in the
       workspace configuration.
    """
    DEFAULTS = {"string": "", "number": 0, "boolean": False, "array": []}

    def __init__(self):
        self._schema = jsonschema.Draft4Validator(CONFIG_SCHEMA)

    def get_fields(self, only_defaults=False) -> dict:
        """Get the metadata fields that are in a workspace config[uration], with default values
        provided for each field.

        The default values come out of the configuration schema in :data:`CONFIG_SCHEMA`.
        Keys starting with a leading underscore, like '_id', are skipped.

        Args:
            only_defaults: Do not return fields that are not given a default value in the schema.

        Returns:
            Keys are field name, values are (field description, value). The 'value' is the default value.
            Its type is either a list, a number, boolean, or a string.
        """
        result = {}  # return value

        # Loop over all properties in the schema
        for key, item in CONFIG_SCHEMA["properties"].items():
            # Skip properties whose name starts with a leading underscore
            if key.startswith("_"):
                continue
            desc, type_ = item["description"], item["type"]
            # Coerce unknown types to string (but print a warning, as this is not expected)
            if type_ not in self.DEFAULTS:
                _log.warning(
                    'Unknown schema type "{}".' 'Using "string" instead'.format(type_)
                )
                type_ = "string"
            # Based on value type, extract default value
            default_value = None
            if type_ == "array":
                # Arrays need special processing
                item_type, item_desc = item["items"]["type"], item["items"]["description"]
                desc = "{}. Each item is a {}".format(desc, item_desc)
                type_ = item_type
                # Use default either (1) inside the list of items, or (2) outside for the whole property
                if "default" in item["items"]:
                    default_value = [item["items"]["default"]]
                elif "default" in item:
                    # default is comma-separated list
                    default_value = item["default"].split(",")
            elif "default" in item:
                # For everything else, simply get the "default" key
                default_value = item["default"]
            # Set result, except if we are in 'only_defaults' mode and there is no default value
            if only_defaults:
                if default_value is None:
                    _log.debug(f"(only_defaults mode) NOT setting default value for {key}: no value provided")
                else:
                    # Set the value
                    result[key] = (desc, default_value)
                    _log.debug(f"(only_defaults mode) setting default value for {key} to: {default_value}")
            else:
                # If not in only_defaults mode, use an internal default value based on the type when there
                # is no default value in the schema.
                if default_value is None:
                    default_value = self.DEFAULTS[type_]
                # Set the value
                result[key] = (desc, default_value)
                _log.debug(f"setting default value for {key} to: {default_value}")

        return result


def find_workspaces(root):
    """Find workspaces at or below 'root'.

    Args:
        root (str): Path to start at

    Returns:
        List[str]: paths, which are all workspace roots.
    """
    w = []
    # try all subdirectories of root
    for (dirpath, dirnames, filenames) in os.walk(root):
        for dmfdir in dirnames:
            dmfpath = os.path.join(dirpath, dmfdir)
            conf_file = os.path.join(dmfpath, Workspace.WORKSPACE_CONFIG)
            if os.path.exists(conf_file):
                w.append(dmfpath)
    # also try root itself
    if os.path.exists(os.path.join(root, Workspace.WORKSPACE_CONFIG)):
        w.insert(0, root)
    return w
