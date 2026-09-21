# -*- coding: utf-8 -*-
"""Remove TimeSlip from this Mac."""
from __future__ import print_function

import os
import shutil
import sys

HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, "Applications", "TimeSlip")
APP_BUNDLE = os.path.join(HOME, "Applications", "TimeSlip.app")
UNINSTALL_CMD = os.path.join(HOME, "Applications", "Uninstall TimeSlip.command")
SUPPORT = os.path.join(HOME, "Library", "Application Support", "TimeSlip")


def remove(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        print("Removed %s" % path)
    elif os.path.isfile(path):
        os.remove(path)
        print("Removed %s" % path)


def main():
    print("TimeSlip uninstaller")
    print("--------------------")
    keep = False
    if os.path.isdir(SUPPORT):
        try:
            answer = raw_input("Also delete saved sessions? [y/N] ")  # noqa: F821
        except NameError:
            answer = input("Also delete saved sessions? [y/N] ")
        keep = not str(answer).strip().lower().startswith("y")

    remove(APP_BUNDLE)
    remove(INSTALL_DIR)
    remove(UNINSTALL_CMD)
    if not keep:
        remove(SUPPORT)
    else:
        print("Left session database in %s" % SUPPORT)

    print("TimeSlip has been uninstalled.")


if __name__ == "__main__":
    main()
