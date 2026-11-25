#!/bin/sh
# Headless Aseprite for the cloud session, with a throw-away profile (no user settings are read or written).
# The binary is not in the repository (EULA): build it per tools/aseprite/README.md or set ASEPRITE_BIN.
BIN="${ASEPRITE_BIN:-/home/user/aseprite-build/src/build/bin/aseprite}"
if [ ! -x "$BIN" ]; then echo "ase_headless.sh: no Aseprite binary at $BIN (set ASEPRITE_BIN)" >&2; exit 127; fi
T="${TMPDIR:-/tmp}/ase-headless-profile"
mkdir -p "$T/c" "$T/a"
export HOME="$T" XDG_CONFIG_HOME="$T/c" ASEPRITE_USER_FOLDER="$T/a"
unset DISPLAY WAYLAND_DISPLAY
exec "$BIN" "$@"
