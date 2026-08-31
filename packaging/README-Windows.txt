TLServer for Windows
====================

1. Extract every file from this ZIP into the same directory.
2. Copy config.sample.toml to config.toml and edit it for your translators.
3. Run tlserver.exe from a terminal so that startup errors remain visible.

Python is not required to run this packaged executable.

Offline translation models are not included. If you enable the Offline
translator, download the models separately and set its model paths in
config.toml. Relative paths are resolved from the directory in which you
launch TLServer.

This executable is not code-signed. Windows SmartScreen or antivirus software
may display a warning when it is first downloaded or launched.
