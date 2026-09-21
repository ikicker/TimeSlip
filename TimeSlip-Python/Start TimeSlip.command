#!/bin/bash
cd "$(dirname "$0")" || exit 1
PY=""
for c in python3 /usr/local/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /usr/bin/python3; do
  if command -v "$c" >/dev/null 2>&1; then PY="$(command -v "$c")"; break; fi
  if [ -x "$c" ]; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  osascript -e 'display alert "TimeSlip" message "Python 3 was not found. Install it from python.org first." as critical'
  exit 1
fi
exec "$PY" "./launch.py"
