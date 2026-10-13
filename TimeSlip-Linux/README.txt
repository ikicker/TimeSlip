TimeSlip for Linux (Linux Mint / Ubuntu / Debian)
=================================================

Local work timer with start/end times, comments, hours to bill, and Excel export.
Uses only the Python standard library — no pip packages required.

Requires
--------
Python 3.7 or newer. On Linux Mint:

    sudo apt update
    sudo apt install python3

Quick start (no install)
------------------------
1. Extract this folder anywhere (e.g. your home directory or Desktop).
2. Open a terminal in the folder and run:

    python3 launch.py

The browser opens to http://127.0.0.1:8765/
Leave the terminal window open while you use the timer.
Press Ctrl-C to stop.

Install (recommended)
---------------------
From the TimeSlip-Linux folder:

    python3 install.py

This installs to:
  - App files:     ~/.local/share/timeslip/
  - Menu entry:    ~/.local/share/applications/timeslip.desktop
  - Command:       ~/.local/bin/timeslip

After install you can:
  - Launch from the application menu (search for “TimeSlip”)
  - Or run `timeslip` from a terminal (make sure ~/.local/bin is on your PATH)

Sessions are stored in:
  ~/.local/share/TimeSlip/timeslip.db

Uninstall
---------
    python3 ~/.local/share/timeslip/uninstall.py

Or, if you have not installed yet, run uninstall.py from this folder.

Notes
-----
- No root/sudo is required for install or running.
- The app binds only to 127.0.0.1 — it is local only.
- Excel export is generated on the fly with no external libraries.
- Works on Linux Mint, Ubuntu, Debian, and most other modern Linux distributions that have Python 3.

License
-------
See the LICENSE file in the original TimeSlip package.
