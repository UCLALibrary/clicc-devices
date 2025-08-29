#!/bin/bash

# Write python output in real time without buffering
export PYTHONUNBUFFERED=1

# Pick up any local changes to requirements.txt, which do *not* automatically get re-installed when starting the container.
# Do this only in dev environment!
if [ "$DJANGO_RUN_ENV" = "dev" ]; then
  pip install --no-cache-dir -r requirements.txt --user --no-warn-script-location
fi

# Check when database is ready for connections
echo "Checking database connectivity..."
until python -c 'import os, psycopg ; conn = psycopg.connect(host=os.environ.get("DJANGO_DB_HOST"),port=os.environ.get("DJANGO_DB_PORT"),user=os.environ.get("DJANGO_DB_USER"),password=os.environ.get("DJANGO_DB_PASSWORD"),dbname=os.environ.get("DJANGO_DB_NAME"))' ; do
  echo "Database connection not ready - waiting"
  sleep 5
done

# Run database migrations
python manage.py migrate

# Start cron (via sudo).
# sudo access was set up in Dockerfile and is limited to this one command.
sudo /usr/sbin/service cron start

# Capture environment to file, for cron to use;
# otherwise, cron's env is sparse, and values are set at startup by
# external sources: docker compose (local) or kubernetes (production),
# so not otherwise available within the container for cron to use.
env | sort > /home/django/full_env_for_cron.env

# The cron jobs themselves are created and managed via the Django UI.
# However, when the container starts, there's no crontab - it must be
# (re)created.
python manage.py update_crontab

if [ "$DJANGO_RUN_ENV" = "dev" ]; then
  # Create default superuser for dev environment, using django env vars.
  # Logs will show error if this exists, which is OK.
  python manage.py createsuperuser --no-input

  ##### FIXTURES: Enable and add as needed. #####
  # Load fixtures, only in dev environment.
  python manage.py loaddata item_types.json sets.json
  ##### END FIXTURES #####
fi

if [ "$DJANGO_RUN_ENV" = "dev" ]; then
  python manage.py runserver 0.0.0.0:8000
else
  # Build static files directory, starting fresh each time - do we really need this?
  python manage.py collectstatic --no-input

  # Start the Gunicorn web server
  # Gunicorn cmd line flags:
  # -w number of gunicorn worker processes
  # -b IPADDR:PORT binding
  # -t timeout in seconds; allow 180 seconds, for long-running Excel exports.
  # --access-logfile where to send HTTP access logs (- is stdout)
  export GUNICORN_CMD_ARGS="-w 3 -b 0.0.0.0:8000 -t 180 --access-logfile -"
  gunicorn project.wsgi:application
fi
