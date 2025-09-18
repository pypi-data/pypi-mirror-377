GmCapsule is an extensible server for [Gemini](https://gemini.circumlunar.space/) and [Titan](https://transjovian.org/titan/).

See the [User manual](https://geminispace.org/gmcapsule/gmcapsule.html) for configuration and usage instructions.

## Installation

Install "gmcapsule" via `pip`:

    pip install gmcapsule

Then run the server daemon:

    gmcapsuled

## Running via systemd

Create the following service file and save it as _~/.config/systemd/user/gmcapsule.service_:

    [Unit]
    Description=GmCapsule: extensible Gemini/Titan server
    After=network.target
    
    [Service]
    Type=simple
    ExecStart=<YOUR-INSTALL-PATH>/gmcapsuled
    ExecReload=/bin/kill -HUP $MAINPID
    Restart=always
    Environment="PYTHONUNBUFFERED=1"
    StandardOutput=syslog
    StandardError=syslog
    SyslogIdentifier=gmcapsule
    
    [Install]
    WantedBy=default.target

Replace `<YOUR-INSTALL-PATH>` with the actual path of `gmcapsuled`. `pip` will install it in a directory on your PATH.

Then you can do the usual:

    systemctl --user daemon-reload
    systemctl --user enable gmcapsule
    systemctl --user start gmcapsule

The log can be viewed via journalctl (or syslog):

    journalctl -xe --user-unit=gmcapsule

## Change log

### v0.9

* Misfin: Added extension for receiving Misfin(B) and Misfin(C) messages and forwarding them to the configured email address(es).

v0.9.1:

* Certificates for virtual hosts are first checked under subdirectories in the certificate directory. The subdirectory name must match the virtual host domain name; the certificate files must be named "cert.pem" and "key.pem" in each subdirectory. As a fallback, every virtual host still uses the common certificate as before.

v0.9.2:

* Cleanup and minor fixes.

v0.9.3:

* Titan: Fixed parsing parameters when request contains a query string.

v0.9.4:

* Misfin: Fixed issue parsing sender certificate.

v0.9.5:

* Misfin: Updated URI format.
* Documented more settings.

v0.9.6:

* GitView: Fixed commit history parsing error when it contains CR characters. (Thanks Aelspire!)

v0.9.7:

* CGI: Added the `TITAN_EDIT` environment variable. It gets the value "1" when a Titan edit request is being processed.

v0.9.8:

* Misfin: Added `uriformat` config variable to choose format of "mailto"-like Misfin links.

### v0.8

* Added support for the Titan "edit" parameter. The `Request` class has a new `is_titan_edit` flag to indicate when a request is being processed as an edit.
* Fixed handling of invalid Titan requests (unrecognized parameters or no size specified).
* Fixed issue handling SIGHUP (patch by noirscape).

### v0.7

* CGI: Fixed contents of `PATH_INFO`: it is now URL-decoded and the script path is removed so only the part following the script path is included in the environment variable (RFC 3875, section 4.1.5).
* CGI: `bin_root` applies a wildcard to all found CGI executables so `PATH_INFO` can be used.
* CGI: `bin_root` looks for executable "index.gmi" files in requested directories to provide the directory index.
* Skip the TLS SNI check when request hostname has a literal IP address. (SNI is not supposed to be used with literal addresses.)
* Respond with status 53 if an unknown hostname is requested. This helps reveal configuration errors where the correct hostnames are not specified.

### v0.6

* Added `stream` to the `[cgi.*]` section to enable streaming output mode where the output of the CGI child process is immediately sent to the client without any buffering. Streaming is not supported if the server is using multiple processes.
* Markdown: Fixed handling of alt text in preformatted blocks (patch by Mike Cifelli).

v0.6.1:

* Static: Fixed unquoting URL paths when looking up files.
* Added example of printing Gemini meta line in CGI documentation.

### v0.5

* Added `processes` to the `[server]` section to configure how many request handler processes are started.
* Extension modules can register new protocols in addition to the built-in Gemini and Titan.
* SIGHUP causes the configuration file to be reloaded and workers to be restarted. The listening socket remains open, so the socket and TLS parameters cannot be changed.
* API change: Extension modules get initialized separately in each worker thread. Instead of a `Capsule`, the extension module `init` method is passed a `Context`. `Capsule` is no longer available as global state.
* API change: `Identity` no longer contains OpenSSL objects for the certificate and public key. Instead, they are provided as serialized in DER format.

v0.5.1:

* `Identity` class is available when importing the `gmcapsule` module.

v0.5.2:

* Fixed error in the "rewrite" module (Codeberg PR #1).

v0.5.3:

* Enable address reuse on the server socket for unimpeded restarting (Codeberg PR #3).

### v0.4

* Added built-in module "rewrite" that matches regular expressions against the request path and can rewrite the path or return a custom status for redirection, "Gone" messages, or other exceptional situations.
* Extension module load order is determined after locating all modules from all directories. Previously, the order was local to each directory.
* Added a new configuration section `[priority]` for overriding default module priorities determined from file names. This is useful for changing the priority of the built-in modules.

v0.4.1:

* Rewrite: Request query string can be included in a `status` using the `${QUERY_STRING}` variable.

### v0.3

* Added a shutdown event for custom background workers.
* `Request.query` is None if there is no query string present. Previously, the query string was an empty string in this case. This allows making a distinction between empty and absent query strings.

v0.3.1:

* CGI: Fixed handling of a missing query string.

v0.3.2:

* GitView: Fixed processing of Git commit history when a message contains backslashes.

### v0.2

* Added `[cgi] bin_root` configuration option for automatically and dynamically mapping all executables in a directory tree to URL entry points.
* Minor documentation updates.
* Published on PyPi as "gmcapsule".

v0.2.1:

* Fixed error handling. Exceptions are now caught and the error message is printed.

v0.2.2:

* Reduced required Python version to 3.6 (f-strings).
* Added systemd instructions.

v0.2.3:

* Requests exceeding 1024 bytes should result in an error code and not just be ignored.
* Respond with an error code to malformed UTF-8 in the request.
* Verify that the port number in the request URI matches the server's port.

v0.2.4:

* Fixed an error in the Markdown parser.

v0.2.5:

* Fixed handling of exceptions from request handler, and print a traceback.
* Fixed `importlib` error with Python 3.11.

### v0.1

* Initial public release.