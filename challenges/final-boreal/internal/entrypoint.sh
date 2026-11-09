#!/bin/sh
set -e

ssh-keygen -A
mkdir -p /run/sshd /var/backups
/usr/sbin/sshd

exec cron -f
