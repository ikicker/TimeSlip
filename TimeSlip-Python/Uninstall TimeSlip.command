#!/bin/bash
cd "$(dirname "$0")" || exit 1
PY=""
for c in python3 /usr/local/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /usr/bin/python3; do
  if command -v "$c" >/dev/null 2>&1; then PY="$(command -v "$c")"; break; fi
  if [ -x "$c" ]; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "Python 3 was not found."
  exit 1
fi
"$PY" "./uninstall.py"
echo ""
echo "Press Return to close this window."
read -r _
