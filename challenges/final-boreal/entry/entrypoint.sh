#!/bin/sh
set -e

ssh-keygen -A
mkdir -p /run/sshd
/usr/sbin/sshd

exec python3 /opt/web/app.py
