TimeSlip for Mac — Python backend + frontend
===========================================

What this is
------------
A local Python app you can install on a Mac (including a 2014 Intel Mac Mini).

Backend  (Python, standard library only)
  SQLite database of work sessions
  HTTP API on http://127.0.0.1:8765
  Excel (.xlsx) export: comment, start, end, duration, hours to bill

Frontend (served by that Python server)
  Timer, session log, edit/delete, billing export

No pip, no Homebrew, no Flask, no Xcode.

Requires
--------
Python 3.7 or newer.
If /usr/bin/python3 is missing, install the macOS 64-bit package from:
  https://www.python.org/downloads/
A 2014 Mini can use the Intel 64-bit installer (macOS 10.13+ recommended).

Install
-------
1. Copy the TimeSlip-Python folder onto the Mac.
2. Double-click "Install TimeSlip.command"
   If macOS blocks it: right-click → Open.
3. The installer copies files to:
     ~/Applications/TimeSlip
     ~/Applications/TimeSlip.app
     ~/Applications/Uninstall TimeSlip.command

Run
---
Double-click TimeSlip.app (right-click → Open the first time).
Leave that process running while you use the timer.
Safari/Chrome opens http://127.0.0.1:8765/

Sessions are stored in:
  ~/Library/Application Support/TimeSlip/timeslip.db

Uninstall
---------
Double-click "Uninstall TimeSlip.command"
or ~/Applications/Uninstall TimeSlip.command

It removes the app and, if you choose, the saved session database.

Run without installing
----------------------
From this folder:
  python3 launch.py
