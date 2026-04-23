#!/usr/bin/env python3
# Copyright (C) 2025 B9Software
# This file is forked from Cuckoo Sandbox - hxxp://www.cuckoosandbox.org
# Additional code from B9Software


import argparse
import json
import os
import io
import socket
import sys
import tarfile
import subprocess
from datetime import datetime
#from StringIO import StringIO
from zipfile import ZipFile, ZIP_STORED

try:
    from bottle import route, run, request, hook, response, HTTPError
    from bottle import default_app, BaseRequest
except ImportError:
    sys.exit("ERROR: Bottle.py library is missing")

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

# Increase request size limit
BaseRequest.MEMFILE_MAX = 1024 * 1024 * 4

def jsonize(data):
    """Converts data dict to JSON.
    @param data: data dict
    @return: JSON formatted data
    """
    response.content_type = "application/json; charset=UTF-8"
    return json.dumps(data, sort_keys=False, indent=4)

@hook("after_request")
def custom_headers():
    """Set some custom headers across all HTTP responses."""
    response.headers["Server"] = "Machete Server"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Pragma"] = "no-cache"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Expires"] = "0"

    
@route("/logon", method="Get")
def logon():
    try:
      os.system("qemu-system-x86_64 -enable-kvm \
    -machine q35 -cpu host -smp sockets=1,cores=1,threads=2 -m 2048 \
    -usb -device usb-kbd -device usb-tablet -rtc base=localtime \
    -net nic,model=virtio -net user,hostfwd=tcp::8008-:8008 \
    -drive file=/snapshot2.img,media=disk,if=virtio \
    -display vnc=:0,websocket=5700 &")
    except Exception as ex:
      status = " Exception: " + str(ex)
      return jsonize(status)

    return jsonize("VM is starting with logon..." )
        

@route("/startVM", method="Get")
def startVM():
    try:
      os.system("qemu-system-x86_64 -enable-kvm \
    -machine q35 -cpu host -smp sockets=1,cores=1,threads=2 -m 2048 \
    -usb -device usb-kbd -device usb-tablet -rtc base=localtime \
    -net nic,model=virtio -net user,hostfwd=tcp::8008-:8008 \
    -drive file=/snapshot.img,media=disk,if=virtio \
    -display vnc=:0,websocket=5700 \
    -loadvm windows &")
    except Exception as ex:
      status = " Exception: " + str(ex)
      return jsonize(status)

    return jsonize("VM is starting..." )
    

@route("/killVM", method="Get")
def killVM():
    try:
      os.system("pkill -9 qemu")
    except Exception as ex:
      status = " Exception: " + str(ex)
      return jsonize(status)
    return jsonize("VM is being killed..." )
    
@route("/addUSB", method="Get")
def addUSB():
	try:
		output = subprocess.check_output(["lsusb | grep -i SanDisk | awk '{print $2}'"], shell=True).decode('utf-8')		
		x = output
		cleaned = x.replace('\n', '').replace('\r', '')
		x = cleaned.lstrip('0')
		print(f"USB hostbus: {x}")

		output = subprocess.check_output(["lsusb | grep -i SanDisk | awk '{print $4}' | sed 's/.$//'"], shell=True).decode('utf-8')
		y = output
		cleaned = y.replace('\n', '').replace('\r', '')
		y = cleaned.lstrip('0')			
		print(f"USB hostaddr: {y}")	
		
		output = "qemu-system-x86_64 -enable-kvm -machine q35 -cpu host -smp sockets=1,cores=1,threads=2 -m 2048 -usb -device usb-kbd -device usb-tablet -rtc base=localtime -device qemu-xhci -device usb-host,hostbus={},hostaddr={} -net nic,model=virtio -net user,hostfwd=tcp::8008-:8008 -drive file=/snapshot.img,media=disk,if=virtio -display vnc=:0,websocket=5700".format(x,y) 
		cleaned = output.replace('\n', '')
		print(cleaned)
			
		os.system(cleaned +" &")
		
	except Exception as ex:
		status = " Exception: " + str(ex)
		return jsonize(status)
			
	return jsonize("VM with usb is starting..." )
    
@route("/ps", method="Get")
def ps():
    try:
      return jsonize(os.system("ps -eaf | grep -i qemu"))
    except Exception as ex:
      status = " Exception: " + str(ex)
      return jsonize(status)
    return jsonize("ps ..." )

@route("/revertVM", method="Get")
def revertVM():
    try:
      killVM()
      startVM()
    except Exception as ex:
      status = " Exception: " + str(ex)
      return jsonize(status)
    return jsonize("VM is reverting ...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", help="Host to bind the API server on", default="0.0.0.0", action="store", required=False)
    parser.add_argument("-p", "--port", help="Port to bind the API server on", default=8090, action="store", required=False)
    args = parser.parse_args()
    #revertVM()
    run(host=args.host, port=args.port)

