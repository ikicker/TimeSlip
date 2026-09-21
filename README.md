# TimeSlip

Local work timer with a comment on the work being done, start time, end time, hours to bill, and an Excel export.

TimeSlip is meant to stay on your machine. Sessions are not uploaded anywhere.

## Features

- Start / stop a live timer
- Required work comment on each session
- Start time, end time, duration, and decimal hours to bill
- Optional hourly rate and amount
- Edit or delete saved sessions
- Excel (`.xlsx`) report with a totals row
- Runs without an App Store account

## Which package to use

| Package | Use when |
| --- | --- |
| [`TimeSlip-Python/`](TimeSlip-Python/) | You want a Mac app with a Python backend, installer, and uninstaller (including a 2014 Intel Mac Mini) |
| [`work-timer/`](work-timer/) | You want a browser / iPhone home-screen timer (PWA) |
| [`TimeSlip-iPhone.html`](TimeSlip-iPhone.html) | You want a single file to AirDrop and Add to Home Screen on iPhone |
| [`TimeSlip-iOS/`](TimeSlip-iOS/) | You have Xcode and want to sign a native iPhone wrapper |
| [`TimeSlip-MacMini/`](TimeSlip-MacMini/) | You only want to double-click a file that opens Safari on an old Mac |

The Python package is the one with a real backend, SQLite storage, installer, and uninstaller.

## Python app (Mac)

### Requirements

- Python 3.7 or newer
- No pip, Homebrew, Flask, or Xcode

If `python3` is missing, install the macOS 64-bit package from [python.org](https://www.python.org/downloads/). A Late 2014 Mac Mini should use the **Intel 64-bit** installer.

### Install

1. Clone or unzip this repository.
2. Open the `TimeSlip-Python` folder.
3. If macOS says you do not have access privileges, right-click `Fix Permissions.command` → **Open**.
4. Right-click `Install TimeSlip.command` → **Open**, *or* skip install and use `Start TimeSlip.command`.

Do not copy the app into `/Applications`. The installer only writes under your Home folder:

- `~/TimeSlip-App/` — program files
- `~/Desktop/TimeSlip.app` — launcher (after install)
- `~/Library/Application Support/TimeSlip/timeslip.db` — sessions

### Run without installing

```bash
cd TimeSlip-Python
python3 launch.py
```

Or double-click `Start TimeSlip.command`.

Leave that window open. The UI opens at [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

### Uninstall

Double-click `Uninstall TimeSlip.command`. You can keep or delete the session database.

### Backend API

Local only (`127.0.0.1:8765`).

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/state` | Sessions, running timer, rate |
| `POST` | `/api/sessions/start` | `{ "comment": "..." }` |
| `POST` | `/api/sessions/stop` | Stop and save |
| `PUT` | `/api/sessions/<id>` | Edit comment / start / end |
| `DELETE` | `/api/sessions/<id>` | Delete one session |
| `POST` | `/api/sessions/clear` | Delete all sessions |
| `POST` | `/api/settings` | `{ "rate": 85 }` |
| `GET` | `/api/export.xlsx` | Download the billing workbook |

Excel columns: work comment, date, start time, end time, duration, hours to bill, optional rate and amount.

### Layout

```
TimeSlip-Python/
  backend/
    server.py        HTTP server
    storage.py       SQLite
    xlsx_export.py   .xlsx writer (stdlib only)
  frontend/
    index.html
    styles.css
    app.js
  launch.py
  install.py
  uninstall.py
  Fix Permissions.command
  Start TimeSlip.command
  Install TimeSlip.command
  Uninstall TimeSlip.command
```

## Browser / iPhone timer

`work-timer/` is a static PWA. Open `index.html` in Safari on iPhone → Share → **Add to Home Screen**.

`TimeSlip-iPhone.html` is the same app inlined into one file for AirDrop.

Sessions in this variant live in the browser’s local storage, not SQLite.

## Signed iPhone app (Xcode)

`TimeSlip-iOS/` wraps the timer in a WKWebView project.

1. Open `TimeSlip.xcodeproj` on a Mac that can run a current Xcode.
2. Signing & Capabilities → Automatically manage signing → your Apple ID.
3. Change the bundle identifier to something unique.
4. Plug in the iPhone, enable Developer Mode, press Run.

A free Apple ID build expires after 7 days. The Apple Developer Program lasts about a year. A 2014 Mac Mini cannot run modern Xcode.

See `TimeSlip-iOS/SIGNING-ON-MAC-MINI.txt`.

## Privacy

- No accounts
- No analytics
- No network calls except the local Python server to itself
- Uninstall can delete the database

## License

See License file.
