# -*- coding: utf-8 -*-
"""Install TimeSlip on Linux (Linux Mint / Ubuntu / Debian). No sudo required."""
from __future__ import print_function

import os
import shutil
import stat
import sys

APP_NAME = "TimeSlip"
SRC = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")

# Install under user home — no root needed
INSTALL_ROOT = os.path.join(HOME, ".local", "share", "timeslip")
DESKTOP_DIR = os.path.join(HOME, ".local", "share", "applications")
BIN_DIR = os.path.join(HOME, ".local", "bin")
DESKTOP_FILE = os.path.join(DESKTOP_DIR, "timeslip.desktop")
LAUNCHER = os.path.join(BIN_DIR, "timeslip")


def find_python():
    candidates = [
        sys.executable,
        "/usr/bin/python3",
        "/usr/local/bin/python3",
    ]
    for path in candidates:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def copy_tree(src, dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    ignore = shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".DS_Store", "*.zip", "install.py", "uninstall.py"
    )
    shutil.copytree(src, dst, ignore=ignore)


def write_desktop_file(python_path):
    if not os.path.isdir(DESKTOP_DIR):
        os.makedirs(DESKTOP_DIR, exist_ok=True)

    content = """[Desktop Entry]
Version=1.0
Type=Application
Name=TimeSlip
Comment=Local work timer with Excel export
Exec=%s %s/launch.py
Icon=utilities-system-monitor
Terminal=false
Categories=Utility;Office;
StartupNotify=true
""" % (python_path, INSTALL_ROOT)

    with open(DESKTOP_FILE, "w") as f:
        f.write(content)
    os.chmod(DESKTOP_FILE, 0o644)


def write_launcher(python_path):
    if not os.path.isdir(BIN_DIR):
        os.makedirs(BIN_DIR, exist_ok=True)

    script = """#!/bin/bash
# TimeSlip launcher
cd "%s" || exit 1
exec "%s" "%s/launch.py" "$@"
""" % (INSTALL_ROOT, python_path, INSTALL_ROOT)

    with open(LAUNCHER, "w") as f:
        f.write(script)
    os.chmod(LAUNCHER, os.stat(LAUNCHER).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def main():
    print("TimeSlip installer for Linux")
    print("----------------------------")
    py = find_python()
    if not py:
        print("Python 3 was not found.")
        print("On Linux Mint install it with: sudo apt update && sudo apt install python3")
        sys.exit(1)
    print("Using Python: %s" % py)
    print("Installing to: %s" % INSTALL_ROOT)

    try:
        os.makedirs(os.path.dirname(INSTALL_ROOT), exist_ok=True)
        copy_tree(SRC, INSTALL_ROOT)
        # Copy launch.py and uninstall.py into the install dir
        for name in ("launch.py", "uninstall.py"):
            src = os.path.join(SRC, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(INSTALL_ROOT, name))
        write_desktop_file(py)
        write_launcher(py)
    except OSError as exc:
        print("Could not write files: %s" % exc)
        print("Check that ~/.local is writable.")
        sys.exit(1)

    print("")
    print("Installed.")
    print("  App files:  %s" % INSTALL_ROOT)
    print("  Menu entry: %s" % DESKTOP_FILE)
    print("  Command:    timeslip   (if ~/.local/bin is on your PATH)")
    print("")
    print("You can start TimeSlip from the application menu, or run:")
    print("  %s" % LAUNCHER)
    print("")
    print("Sessions are stored in ~/.local/share/TimeSlip/timeslip.db")
    print("")
    print("To uninstall later, run:")
    print("  python3 %s/uninstall.py" % INSTALL_ROOT)


if __name__ == "__main__":
    main()
