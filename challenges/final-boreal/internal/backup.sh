#!/bin/sh
# Respaldo de AuroraVault (lo ejecuta root por cron cada minuto en el laboratorio)
mkdir -p /var/backups
tar -czf "/var/backups/boreal-$(date +%s).tgz" /etc 2>/dev/null || true
