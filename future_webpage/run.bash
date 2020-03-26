#!/bin/bash

# CHECK ARGUMENTS
if [[ ! "$1" =~ (test|runserver|shell|makemessages) ]]
then
  echo -e "\n  Usage: $0 <test, runserver, shell, makemessages>\n"
  exit 1
fi

# VIRTUALENV + DEPENDENCIES
. env/bin/activate
pip install -r requirements.txt

# SECRETS
source secrets
if [[ "$?" -eq "1" ]]
then
  echo
  echo "You should get the secrets file from the server in order to have the needed environment variables"
  echo "WARNING! This file should not be pushed to the git repository"
  exit 1
fi

# ENV
case "$1" in

  test)
    export DJANGO_ENV="test"
    ;;
  runserver|shell|makemessages)
    export DJANGO_ENV="dev"
    ;;
esac

# DATABASE
python manage.py migrate

# COMMAND
case "$1" in

  test)
    export DJANGO_SETTINGS_MODULE="dgf_cms.settings"
    pytest --cov=dgf --cov-config=.coveragerc --ignore=env  --flakes --pep8
    ;;
  runserver)
    python manage.py runserver 0.0.0.0:8000
    ;;
  shell)
    python manage.py shell
    ;;
  makemessages)
    python manage.py makemessages -l de -i env
    ;;
esac
