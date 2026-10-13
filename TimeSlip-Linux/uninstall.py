# -*- coding: utf-8 -*-
"""Remove TimeSlip from this Linux system."""
from __future__ import print_function

import os
import shutil
import sys

HOME = os.path.expanduser("~")
TARGETS = [
    os.path.join(HOME, ".local", "share", "timeslip"),
    os.path.join(HOME, ".local", "share", "applications", "timeslip.desktop"),
    os.path.join(HOME, ".local", "bin", "timeslip"),
]
SUPPORT = os.path.join(HOME, ".local", "share", "TimeSlip")


def remove(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        print("Removed %s" % path)
    elif os.path.isfile(path):
        os.remove(path)
        print("Removed %s" % path)


def main():
    print("TimeSlip uninstaller (Linux)")
    print("----------------------------")
    keep = False
    if os.path.isdir(SUPPORT):
        try:
            answer = raw_input("Also delete saved sessions? [y/N] ")  # noqa: F821
        except NameError:
            answer = input("Also delete saved sessions? [y/N] ")
        keep = not str(answer).strip().lower().startswith("y")

    for path in TARGETS:
        remove(path)
    if not keep:
        remove(SUPPORT)
    else:
        print("Left session database in %s" % SUPPORT)

    print("TimeSlip has been uninstalled.")


if __name__ == "__main__":
    main()
