# Copyright (c) 2022 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

"""

User manual
===========

GmCapsule is an extensible Gemini/Titan server.

Extensibility is achieved with Python modules that get loaded at launch
from the configured directories. A set of built-in extension modules is
provided for common functionality like CGI and for serving static files.

The supported protocols are `Gemini <https://geminiprotocol.net>`_ and
`Titan <https://transjovian.org/titan>`_. Both are accepted via the same
TCP port.

GmCapsule can be used in a few different ways:

- You can run it as-is for serving static files.
- You can use CGI programs to generate dynamic content and/or process
  queries and uploads. As an extreme example, you could attach a CGI
  program to the path ``/*`` and generate the entire capsule procedurally
  with it.
- You can use the included extension module `gitview` to make local Git
  repositories viewable via Gemini.
- You can write new extension modules that run as part of the server
  process for advanced use cases. For example, this enables the use
  of additional worker threads and caching state in memory.

``gmcapsuled`` is a simple command line utility for loading a configuration
and running the server. Use the ``--help`` option to see usage instructions.

One can also run the server manually in Python::

    from gmcapsule import *
    cfg = Config("myconfig.ini")
    capsule = Capsule(cfg)
    capsule.run()


Getting started
***************

1. Acquire or generate a server certificate.
2. Prepare a configuration file. A configuration file is required for
   running GmCapsule. For more details, see :ref:`Configuration` and
   :ref:`example.ini`.
3. Run ``gmcapsuled``.


Configuration
*************

The GmCapsule configuration file is in `INI format
<https://en.wikipedia.org/wiki/INI_file>`_. The following sections are
defined:

- :ref:`server` — server settings
- :ref:`titan` — Titan upload settings
- :ref:`static` — serving static files
- :ref:`rewrite.*` — URL rewriting rules
- :ref:`cgi` — General CGI settings
- :ref:`cgi.*` — CGI programs
- :ref:`gitview` — Git repository viewer settings
- :ref:`gitview.*` — Git repository settings
- :ref:`misfin` — Misfin settings
- :ref:`misfin.*` — Misfin mailbox settings

Example of a minimal configuration file for serving static files from
`/var/gemini/example.com/`:

.. code-block:: ini

    [server]
    host  = example.com
    certs = /home/username/.certs

    [static]
    root = /var/gemini


server
------

host : string [string...]
    One or more hostnames for the server. Defaults to ``localhost``.

    When multiple hostnames are specified, each becomes a virtual host.
    The certs directory (see below) may contain separate certificate
    files for each virtual host.

address : string
    IP address of the network interface where the server is listening.
    Defaults to ``0.0.0.0`` (all interfaces).

port : int
    IP port on which the server is listening.

certs : path
    Directory where server certificates are stored. The directory must
    contain the PEM-formatted files `cert.pem` and `key.pem`. Defaults
    to `.certs`.

    If virtual hosts are in use (multiple hostnames configured), this
    directory can have subdirectories matching each hostname. These
    host-specific subdirectories are also expected to contain the
    PEM-formatted files `cert.pem` and `key.pem`. As a fallback, the
    common certificate at the top level of the certs directory is used.

modules : path [path...]
    One or more directories to load extension modules from.

threads : int
    Number of worker threads. At least 1 is required. Defaults to 5.
    Determines how many clients can be responded to at the same time.

processes : int
    Number of request handler processes. Defaults to 2. Request handler
    processes run independently of the main process, allowing multiple
    long-running requests to be handled concurrently. If zero, the worker
    threads handle requests synchronously and are able to only do I/O
    operations concurrently.


titan
-----

Settings for Titan requests.

upload_limit : int
    Maximum size of content accepted in an upload, in bytes. Defaults to
    ``10485760`` (i.e., 10 MiB). Requests that attempt to upload larger
    content will be rejected with an error status.

require_identity : bool
    Require a client certificate when receiving uploads. Defaults to
    ``true``.


static
------

Settings for the `static` module that serves files from a directory. Omitting
this section from the configuration disables the module.

root : path [path...]
    Content directory. Defaults to `.` (current directory). The hostname
    is appended as a subdirectory, so for example if this is set to:

    .. code-block:: ini

        [static]
        root = /home/user/gemini

    files will be served from `/home/user/gemini/example.com/`.


rewrite.*
---------

Settings for the `rewrite` module that checks regular expressions against
the request path and can rewrite the path or return a custom status. You can
use this for internal remapping of directories and files, redirections,
"Gone" statuses, or other exceptional situations.

Each rewriting rule is a section that begins with ``rewrite.``.

.. code-block:: ini

    [rewrite.rename]
    path    = ^/old-path/
    repl    = /new-location/

    [rewrite.elsewhere]
    path    = .*\\.gmi$
    status  = 31 gemini://mygemlog.space/\\1.gmi

protocol : string
    Protocol for the rewrite rule. If omitted, the rule applies to both
    ``gemini`` and ``titan``.

host : string
    Hostname for the rewrite rule. If omitted, defaults to the first
    hostname defined in the :ref:`server` section.

path : string
    Regular expression that is matched against the request path. You may use
    capture groups and refer to them in the replacement text. Note that the
    request path always begins with a slash.

repl : string
    Replacement path. The part of the request path that matches the "path"
    pattern is replaced with this. You can use backslashes to refer to
    capture groups (``\\1``).

status : string
    Custom status to respond with. Must begin with the status code followed
    by the meta line. You can use backslashes to refer to capture groups
    (``\\1``).


cgi
---

General settings for CGI programs.

bin_root : path
    CGI root directory. If set, all executables under the root are made
    available at corresponding URL entry points. The entire directory tree is
    checked for executables. This mapping of executables to entry points is
    dynamic, so you can add, modify, and remove executables inside the
    directory tree without restarting the server.

    The hostname is appended as a subdirectory, like with the static root
    content directory. For example:

    .. code-block:: ini

        [cgi]
        bin_root = /home/user/gemini/cgi-bin

    An executable at `/home/user/gemini/cgi-bin/example.com/action` would then
    be visible at gemini://example.com/action. If the executable name ends
    with ``,titan`` (note: a comma), the entrypoint will use the Titan
    protocol instead of Gemini. The ``,titan`` suffix is omitted from the URL.

    Executable files named `index.gmi` are assumed to be directory indices, so
    a request for the directory `DIR` will check for `DIR/index.gmi` and use
    it for generating the index page.


cgi.*
-----

Each section whose name begins with ``cgi.`` is used for setting up CGI entry
points for the `cgi` module. For example, this registers
``gemini://example.com/listing`` to show the output of ``/bin/ls -l``:

.. code-block:: ini

    [cgi.listfiles]
    path    = /listing
    cwd     = /home/username/testdir
    command = /bin/ls -l

protocol : string
    Protocol for the CGI entry point. Defaults to ``gemini``.

host : string
    Hostname for the CGI entry point. If omitted, defaults to the first
    hostname defined in the :ref:`server` section.

path : string [string...]
    URL path for CGI entry point. An asterisk ``*`` in the end is considered
    a wildcard, matching any path that begins with the specified path.
    Multiple paths can be specified.

cwd : path
    Working directory for executing the CGI command. If omitted, the CGI
    command is executed in the directory where the server was started from.

command : string [string...]
    Command to execute when a request is received matching the CGI entry
    point. The specified strings are interpreted like a shell command, i.e.,
    values that contain spaces need to be quoted.

    See :ref:`CGI Programs` for details about executing CGI programs.

stream : bool
    Execute the command in streaming mode. The output from the command is
    sent immediately to the client without waiting for the command to
    finish. Defaults to ``false``. If enabled, the server must not use
    multiple processes to handle requests.


gitview
-------

Settings for the `gitview` module that enables viewing local Git
repositories via Gemini. If this section is missing, `gitview` is disabled.

host : string
    Hostname where is `gitview` running. If omitted, defaults to the first
    hostname defined in the :ref:`server` section. `gitview` is limited to a
    single hostname.

    This version of `gitview` assumes that the host is reserved just
    for viewing Git repositories. Therefore, using a dedicated virtual host
    is recommended, for example `git.example.com`. The hostname must be
    one of the hostnames in the :ref:`server` section.

git : path
    Path of the Git executable to use. Defaults to `/usr/bin/git`.

cache_path : path
    Directory where cached pages are stored. If omitted, caching is disabled.


gitview.*
---------

Configuration of a Git repository that is visible via `gitview`. For example:

.. code-block:: ini

    [gitview.lagrange]
    title          = Lagrange
    brief          = A Beautiful Gemini Client
    clone_url      = https://git.skyjake.fi/gemini/lagrange.git
    tag_url        = https://git.skyjake.fi/gemini/lagrange/releases/tag/{tag}
    path           = /Users/jaakko/src/lagrange
    url_root       = lagrange
    default_branch = release

title : string
    Name of the repository.

brief : string
    Short description of the repository. Shown on the root page.

clone_url : url
    Git clone URL.

tag_url : url
    Git tag URL for viewing tags in a web browser. This is useful for showing
    release notes and downloads attached to the tag. The placeholder ``{tag}``
    is replaced with the tag to view.

path : path
    Local file path of the Git repository. Git will be run in this directory.

url_root : string
    URL root path where the Git repository can be viewed via Gemini.

default_branch : string
    The default branch of the repository. This is used if no branch is
    specified in the URL.


misfin
------


misfin.*
--------


Static files
************

Static files are served from the configured content directory. There must be
a separate subdirectory for each configured hostname inside the content
directory. For example, if the content directory is `/var/gemini`::

    var
    └── gemini
        ├── example.com
        └── sub.example.com

If the requested path is a directory that contains an `index.gmi` file, that
file is automatically sent as a response.

If the requested path is a directory but the URL path does not end with
a slash, a redirect is sent as a response with the slash added.

The MIME types of files are autodetected using Python's ``mimetypes`` and the
system ``file`` utility, if that is available. A few common file extensions
like ``.txt`` are directly mapped to the corresponding MIME types.


.meta files
-----------

A `.meta` file can be placed in any directory inside the content directory
tree, containing additional directives for handling static files.

Each `.meta` file affects the directory it's in and also all its
subdirectories. For example, placing a `.meta` in `/var/gemini` would affect
all directories inside all virtual hosts.

The `.meta` file has a simple format. Each line has the following structure:

.. code-block:: rst

    pattern: directive

``pattern``
    Shell globbing expression. For example: ``*.zip``
``directive``
    MIME type, or the full Gemini header that will be sent when serving
    the file.

If only a MIME type is specified, that will be used instead of the
autodetected type. If the full header is specified with a non-20 status code,
the response body will be empty and only the header is sent.


CGI programs
************

CGI programs inherit the environment of the server process. Additionally, the
following CGI-specific environment variables are set, providing input and
contextual information:

- ``REMOTE_ADDR``
- ``QUERY_STRING``
- ``PATH_INFO``
- ``SCRIPT_NAME``
- ``SERVER_PROTOCOL``
- ``SERVER_NAME``
- ``SERVER_PORT``
- ``AUTH_TYPE``
- ``TLS_CLIENT_HASH`` (when client certificate provided)
- ``REMOTE_IDENT`` (fingerprints of client certificate and public key)
- ``REMOTE_USER`` (when client certificate provided)
- ``CONTENT_LENGTH`` (Titan only)
- ``CONTENT_TYPE`` (Titan only)
- ``TITAN_TOKEN`` (Titan only)
- ``TITAN_EDIT`` (handling a Titan edit request; protocol is "GEMINI")

The CGI programs's stdout is used as the response to the request.
The response is expected to begin with a valid meta line (status code and
meta text). For example, the following code prints the most commonly used
status:

.. code-block:: python

    print("20 text/gemini\\r")

If the meta line is missing from the CGI program's output, the following
header is prepended if the ouput is valid UTF-8 text:

.. code-block:: rst

    20 text/plain; charset=utf-8

Or, if the output is binary, the prepended header will be:

.. code-block:: rst

    20 application/octet-stream

The response is sent to the client after the program finishes running.

With Titan requests, the uploaded content is passed in via stdin. Note that
the CGI program is only executed after the full contents have already been
successfully received, so the program does not need to worry about interrupted
uploads.


Extensions
**********

All Python modules in the configured extension module directories (see
:ref:`server` configuration) are loaded at launch in alphabetical order, as
long as they use the following naming convention:

    `NN_extmod.py`

That is, the name of the extension ("extmod") is prefixed with two numbers
`NN` and an underscore. This naming gives more control over the order in
which modules are loaded. The ones loaded first have precedence over
registered URL entry points.

If the server has been configured to use multiple processes, each process
loads the extensions separately. This may require synchronizing access to
external resources accessed by extensions.


Initialization
--------------

Each extension module is required to have an initialization function:

.. py:function:: extmod.init(context)

    Initialize the extension module.

    This is called once immediately after the extension has been loaded.

    :param context: Worker context. The extension can use this to access
        configuration parameters, install caches, and register entry
        points and custom scheme handlers.
    :type context: gmcapsule.Context


Requests
--------

An extension module is responsible for handling requests arriving at its
registered entry points. A :class:`~gmcapsule.gemini.Request` object is
given as an argument when the registered entry point callback or handler
object gets called.

The return value from the handler determines what gets sent as a response
to the client:

- Returning ``bytes`` or ``str`` means that the response is UTF-8 encoded
  "text/gemini", and the status code is 20.
- Returning a two-element tuple is interpreted as (status code, meta).
  The response body will be empty. This is useful for error messages and
  redirects.
- Returning a three-element tuple is interpreted as (status, meta, body).
  If the body type is ``str``, it will be UTF-8 encoded before sending.
  If the body type is ``pathlib.Path``, the referenced file is opened and
  its contents are streamed to the client without reading the entire file
  to memory. Otherwise, the body type must be ``bytes`` or ``bytearray``.


Future improvements
*******************

The following limitations could/should be lifted in the future:

- Enable value interpolation in the `configparser`, allowing access to
  defined values and environment variables.
- `gitview` should have a URL path prefix.
- Caches should be informed of identities and queries; content might still
  be cacheable.

"""

import configparser
import importlib
import importlib.machinery
import importlib.util
import mimetypes
import os
import re
import shlex
import subprocess
from pathlib import Path

from .gemini import Server, Cache, Context, Identity, GeminiError
from .markdown import to_gemtext as markdown_to_gemtext


__version__ = '0.9.8'
__all__ = [
    'Config', 'Cache', 'Context', 'GeminiError', 'Identity',
    'get_mime_type', 'markdown_to_gemtext'
]


class Config:
    """
    Server configuration.

    Args:
        config_path (str): Path of a config INI file to load.

    Attributes:
        ini(configparser.ConfigParser): Contents of the config INI file.
            Extension modules can use this to access additional custom
            config parameters. See `configparser
            <https://docs.python.org/3/library/configparser.html>`_
            for details.
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.reload()

    def reload(self):
        self.ini = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            print('Configuration:', self.config_path)
            self.ini.read(self.config_path)
        else:
            print(self.config_path, 'not found -- using defaults')

    def hostnames(self):
        """
        Returns:
            list(str): All the configured hostnames. The first listed hostname
            is considered the default to be used when a hostname is not
            otherwise specified.
        """
        return self.ini.get('server', 'host', fallback='localhost').split()

    def address(self):
        return self.ini.get('server', 'address', fallback='0.0.0.0')

    def port(self):
        """
        Returns:
            int: Listening IP port of the server.
        """
        return self.ini.getint('server', 'port', fallback=1965)

    def certs_dir(self):
        return Path(self.ini.get('server', 'certs', fallback='.certs'))

    def root_dir(self):
        """
        Returns:
            pathlib.Path: Content root directory for serving static files.
            The hostname is always automatically appended to this as a
            subdirectory.
        """
        return Path(self.ini.get('static', 'root')).resolve()

    def mod_dirs(self):
        return [Path(p).resolve() for p in shlex.split(
            self.ini.get('server', 'modules', fallback='.'))]

    def num_threads(self):
        return self.ini.getint('server', 'threads', fallback=5)

    def num_processes(self):
        return self.ini.getint('server', 'processes', fallback=2)

    def max_upload_size(self):
        return self.ini.getint('titan', 'upload_limit', fallback=10 * 1024 * 1024)

    def require_upload_identity(self):
        return self.ini.getboolean('titan', 'require_identity', fallback=True)

    def section(self, name):
        """
        Find a section in the config INI file.

        Args:
            name (str): Name of the section.

        Returns:
            configparser.SectionProxy: INI section.

        Raises:
            KeyError: The section was not found.
        """
        return self.ini[name]

    def prefixed_sections(self, prefix):
        """
        Find all sections in the config INI file whose name begins with
        the given prefix.

        Args:
            prefix (str): Name prefix, e.g., ``cgi.``.

        Returns:
            dict: Mapping of section names (with the prefix removed) to the
            corresponding INI sections (configparser.SectionProxy). An
            empty dictionary is returned if there are no sections matching
            the prefix.
        """
        sects = {}
        for name in self.ini.sections():
            if not name.startswith(prefix): continue
            sects[name[len(prefix):]] = self.ini[name]
        return sects


class Capsule:
    """
    Server instance.

    The server is initialized as specified in the configuration.
    Extension modules are loaded and initialized.

    After constructing and setting up Capsule, call the
    :func:`~gmcapsule.Capsule.run` method to begin accepting incoming
    connections.

    Args:
        cfg (Config): Server configuration.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.sv = Server(cfg)

    def run(self):
        """
        Start worker threads and begin accepting incoming connections. The
        server will run until stopped with a KeyboardInterrupt (^C).
        """
        self.sv.run()


def get_mime_type(path):
    """
    Determine the MIME type of a file. A handful of common file extensions
    are detected as special cases, such as ".gmi" and ".txt". Other files
    are detected with Python's ``mimetypes`` standard library module, and as
    a final fallback, the ``file`` command line utility.

    Args:
        path (str): File path.

    Returns:
        str: Detected MIME type, for example, "image/jpeg". Returns
        "application/octet-stream" if the correct type could not be
        determined.
    """
    p = str(path)
    lp = p.lower()
    if lp.endswith('.txt'):
        return 'text/plain'
    if lp.endswith('.gmi') or lp.endswith('.gemini'):
        return 'text/gemini'
    if lp.endswith('.md') or lp.endswith('.markdown') or lp.endswith('.mdown'):
        return 'text/markdown'

    if not Path(p).exists():
        return None

    mt = mimetypes.guess_type(p)[0]
    if mt is not None:
       return mt

    try:
        return subprocess.check_output([
            '/usr/bin/env', 'file', '--mime-type', '-b', p
            ]).decode('utf-8').strip()
    except:
        return 'application/octet-stream'


def run_server():
    print(f"GmCapsule v{__version__}")

    import argparse
    argp = argparse.ArgumentParser(
        description='GmCapsule is an extensible server for Gemini and Titan.')
    argp.add_argument('-c', '--config',
                      dest='config_file',
                      default=Path.home() / '.gmcapsulerc',
                      help='Configuration file to load at startup')
    argp.add_argument('--trace-malloc',
                      action='store_true',
                      help='Enable memory allocation tracing (for debugging)')
    args = argp.parse_args()

    cfg = Config(args.config_file)
    try:
        capsule = Capsule(cfg)
        capsule.run()
        return 0
    except Exception as er:
        print('ERROR:', er)
        return -1
