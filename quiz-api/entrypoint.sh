#!/bin/sh
# Script de démarrage

echo "Starting seed script..."
python seed.py

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers=3 app:app
