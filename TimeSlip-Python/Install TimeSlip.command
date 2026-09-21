#!/bin/bash
cd "$(dirname "$0")" || exit 1
PY=""
for c in python3 /usr/local/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /usr/bin/python3; do
  if command -v "$c" >/dev/null 2>&1; then PY="$(command -v "$c")"; break; fi
  if [ -x "$c" ]; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  osascript -e 'display alert "TimeSlip installer" message "Python 3 was not found. Install the macOS 64-bit Python 3 package from python.org, then run this installer again." as critical'
  exit 1
fi
"$PY" "./install.py"
echo ""
echo "Press Return to close this window."
read -r _
