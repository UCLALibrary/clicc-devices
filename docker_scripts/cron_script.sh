#!/bin/bash

shopt -s nocasematch

cd /home/django/django_app

# Enable export of KEY=VALUE variables to environment
set -o allexport
# Read env variables from file created in entrypoint.sh on startup,
# escaping punctuation which has meaning in bash.
# Via https://stackoverflow.com/questions/19331497
source <(cat /home/django/full_env_for_cron.env | \
    sed -e '/^#/d;/^\s*$/d' -e "s/'/'\\\''/g" -e "s/=\(.*\)/='\1'/g")
# Turn off export beyond here, though probably doesn't matter in this case.
set +o allexport

# Retrieve data for all registered Alma sets - no parameters needed.
/usr/local/bin/python /home/django/django_app/manage.py retrieve_sets
