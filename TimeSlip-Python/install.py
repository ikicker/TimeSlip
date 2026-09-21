# -*- coding: utf-8 -*-
"""Install TimeSlip on this Mac (no sudo, no Homebrew)."""
from __future__ import print_function

import os
import shutil
import stat
import sys

APP_NAME = "TimeSlip"
SRC = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, "Applications", APP_NAME)
APP_BUNDLE = os.path.join(HOME, "Applications", APP_NAME + ".app")
UNINSTALL_CMD = os.path.join(HOME, "Applications", "Uninstall TimeSlip.command")


def find_python():
    candidates = [
        sys.executable,
        "/usr/local/bin/python3",
        "/opt/homebrew/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/Current/bin/python3",
        "/usr/bin/python3",
    ]
    for path in candidates:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def copy_tree(src, dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    ignore = shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".DS_Store", "*.zip"
    )
    shutil.copytree(src, dst, ignore=ignore)


def write_app_bundle(python_path):
    macos = os.path.join(APP_BUNDLE, "Contents", "MacOS")
    resources = os.path.join(APP_BUNDLE, "Contents", "Resources")
    if os.path.isdir(APP_BUNDLE):
        shutil.rmtree(APP_BUNDLE)
    os.makedirs(macos)
    os.makedirs(resources)

    plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>TimeSlip</string>
    <key>CFBundleDisplayName</key><string>TimeSlip</string>
    <key>CFBundleIdentifier</key><string>com.timeslip.python</string>
    <key>CFBundleVersion</key><string>1.0</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleExecutable</key><string>TimeSlip</string>
    <key>LSMinimumSystemVersion</key><string>10.10</string>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
"""
    with open(os.path.join(APP_BUNDLE, "Contents", "Info.plist"), "w") as handle:
        handle.write(plist)

    launcher = """#!/bin/bash
DIR="%s"
PY="%s"
cd "$DIR" || exit 1
exec "$PY" "$DIR/launch.py"
""" % (INSTALL_DIR, python_path)
    exe = os.path.join(macos, "TimeSlip")
    with open(exe, "w") as handle:
        handle.write(launcher)
    os.chmod(exe, os.stat(exe).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def write_uninstaller(python_path):
    body = """#!/bin/bash
DIR="%s"
PY="%s"
exec "$PY" "$DIR/uninstall.py"
""" % (INSTALL_DIR, python_path)
    with open(UNINSTALL_CMD, "w") as handle:
        handle.write(body)
    os.chmod(
        UNINSTALL_CMD,
        os.stat(UNINSTALL_CMD).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH,
    )
    # Also keep a copy next to the installed app.
    installed = os.path.join(INSTALL_DIR, "Uninstall TimeSlip.command")
    shutil.copy2(UNINSTALL_CMD, installed)
    os.chmod(
        installed,
        os.stat(installed).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH,
    )


def main():
    print("TimeSlip installer")
    print("------------------")
    py = find_python()
    if not py:
        print("Python 3 was not found.")
        print("Install the Intel 64-bit Python 3 package from https://www.python.org/downloads/")
        print("then run this installer again.")
        sys.exit(1)
    print("Using Python: %s" % py)
    print("Installing to: %s" % INSTALL_DIR)

    os.makedirs(os.path.join(HOME, "Applications"), exist_ok=True)
    copy_tree(SRC, INSTALL_DIR)
    write_app_bundle(py)
    write_uninstaller(py)

    print("")
    print("Installed.")
    print("  App:        %s" % APP_BUNDLE)
    print("  Files:      %s" % INSTALL_DIR)
    print("  Uninstall:  %s" % UNINSTALL_CMD)
    print("")
    print("Right-click TimeSlip.app and choose Open the first time.")
    print("Leave the terminal/app running while you use the timer.")


if __name__ == "__main__":
    main()
