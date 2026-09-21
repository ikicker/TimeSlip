# TimeSlip

Local work timer for logging what you worked on, when it started, when it ended, and how many hours to bill. Export the log to Excel.

TimeSlip runs on your Mac. Sessions stay in a local SQLite file. Nothing is uploaded.

## Features

- Start and stop a live timer
- Required comment on the work being done
- Start time, end time, duration, and decimal hours to bill
- Optional hourly rate and amount
- Edit or delete saved sessions
- Excel (`.xlsx`) export with a totals row
- Installer and uninstaller
- No pip, Homebrew, Flask, or App Store account

## Requirements

- macOS (including a Late 2014 Intel Mac Mini)
- Python 3.7 or newer

If `python3` is missing, install the **macOS 64-bit** package from [python.org](https://www.python.org/downloads/). On a 2014 Mini use the Intel installer, not Apple Silicon.

## Quick start

```bash
git clone https://github.com/ikicker/TimeSlip.git
cd TimeSlip/TimeSlip-Python
python3 launch.py
```

Leave that window open. The timer opens at [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

On a Mac you can also right-click `TimeSlip-Python/Start TimeSlip.command` → **Open**.

## If macOS blocks the scripts

That is Gatekeeper, not an admin-password problem. Do not drag the folder into `/Applications`.

Right-click the `.command` file → **Open** → Open.

Or in Terminal:

```bash
xattr -cr ~/Desktop/TimeSlip/TimeSlip-Python
chmod u+x ~/Desktop/TimeSlip/TimeSlip-Python/*.command
```

Then run `Start TimeSlip.command` or `python3 launch.py`.

## Optional install

From `TimeSlip-Python`:

1. Right-click `Install TimeSlip.command` → **Open**
2. Use the launcher it puts on your Desktop

Install locations (all under your Home folder):

| Path | What it is |
| --- | --- |
| `~/TimeSlip-App/` | Program files |
| `~/Desktop/TimeSlip.app` | Launcher |
| `~/Library/Application Support/TimeSlip/timeslip.db` | Saved sessions |

## Uninstall

Right-click `TimeSlip-Python/Uninstall TimeSlip.command` → **Open**.

You can keep or delete the session database.

## Use

1. Type a short comment on the work.
2. Click **Start**, then **Stop & save**.
3. Review sessions on the **Log** tab.
4. On **Export**, set an optional rate and date range, then download the `.xlsx`.

The spreadsheet columns are work comment, date, start time, end time, duration, hours to bill, and optional rate / amount.

## Project layout

```
TimeSlip-Python/
  backend/
    server.py        local HTTP API
    storage.py       SQLite
    xlsx_export.py   Excel writer (Python standard library only)
  frontend/
    index.html
    styles.css
    app.js
  launch.py
  install.py
  uninstall.py
  Start TimeSlip.command
  Install TimeSlip.command
  Uninstall TimeSlip.command
```

## Local API

The server binds to `127.0.0.1:8765` only.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/state` | Sessions, running timer, rate |
| `POST` | `/api/sessions/start` | `{ "comment": "..." }` |
| `POST` | `/api/sessions/stop` | Stop and save |
| `PUT` | `/api/sessions/<id>` | Edit comment / start / end |
| `DELETE` | `/api/sessions/<id>` | Delete one session |
| `POST` | `/api/sessions/clear` | Delete all sessions |
| `POST` | `/api/settings` | `{ "rate": 85 }` |
| `GET` | `/api/export.xlsx` | Download the workbook |

## Privacy

- No accounts
- No analytics
- No calls to the public internet
- Uninstall can delete the database

## License

See [`LICENSE`](LICENSE).

You may use and edit TimeSlip on machines you control for your own timekeeping and billing.

- Clean-room use is prohibited.
- Use by AI systems is prohibited.
- You may not sell or rebrand this software as your own product.
