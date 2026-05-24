#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Build frontend
cd ../frontend
npm install
npm run build
cd ../backend

# Collect static files (includes frontend dist/)
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Seed initial data
python seed_data.py
