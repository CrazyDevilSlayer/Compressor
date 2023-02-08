#!/bin/bash
gunicorn app:app --workers 1 --threads 1 --bind 0.0.0.0:5000 --timeout 86400 & python3 main.py