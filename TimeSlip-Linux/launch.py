# -*- coding: utf-8 -*-
"""Start the TimeSlip backend and open the frontend in a browser."""
from __future__ import print_function

import os
import socket
import sys
import threading
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from server import HOST, PORT, make_server  # noqa: E402


def port_open(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.3)
    try:
        return sock.connect_ex((host, port)) == 0
    finally:
        sock.close()


def main():
    url = "http://%s:%s/" % (HOST, PORT)
    if port_open(HOST, PORT):
        print("TimeSlip is already running at %s" % url)
        webbrowser.open(url)
        return

    httpd = make_server()

    def serve():
        httpd.serve_forever()

    thread = threading.Thread(target=serve)
    thread.daemon = True
    thread.start()

    for _ in range(30):
        if port_open(HOST, PORT):
            break
        time.sleep(0.1)

    print("TimeSlip running at %s" % url)
    print("Leave this window open while you use the timer.")
    print("Press Control-C to quit.")
    webbrowser.open(url)
    try:
        while thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping TimeSlip")
        httpd.shutdown()


if __name__ == "__main__":
    main()
