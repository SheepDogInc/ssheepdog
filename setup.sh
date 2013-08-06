#!/bin/bash

# This script can be used to onboard new developers to the project or ensure
# project dependencies are up to date.

PROJECT=ssheepdog

function echo_exit {
    echo ABORTING: $*
    exit 1
}

if [ -n "$VIRTUALENV" ]; then
    echo_exit "Deactivate your virtualenv by typing 'deactivate' and run this script again."
fi

# Make sure we are in the root directory where the setup executable lives
if [ "`echo $0 | cut -c1`" = "/" ]; then
  cd `dirname $0`
else
  cd `pwd`/`echo $0 | sed -e s/setup.sh//`
fi

# Check for required executables
for ex in python2.7 virtualenv virtualenvwrapper.sh
do
    command -v $ex >/dev/null 2>&1 || { echo >&2 echo_exit "Executable '$ex' is required but not installed.  Aborting."; }
done

# Check for normal files we expect
for f in manage.py requirements.txt $PROJECT/settings/base.py
do
    if [ ! -e $f ]; then
        echo_exit "File $f not found"
    fi
done

# Create virtualenv if necessary
source `which virtualenvwrapper.sh`
if [ -d "$WORKON_HOME/$PROJECT" ]; then
    workon $PROJECT
else
    mkvirtualenv --python=python2.7 --no-site-packages $PROJECT
fi

# Install all dependencies
pip install -r requirements.txt
npm install

# Add node_modules to path if necessary
if ! grep -Fq "/node_modules/.bin" $VIRTUAL_ENV/bin/postactivate; then
    printf 'export PATH=%s/node_modules/.bin:$PATH\n' `pwd` >> $VIRTUAL_ENV/bin/postactivate
    workon $PROJECT
fi

bower install

echo "============================"
echo "TO PROCEED:"
echo "(1) => Create database $PROJECT"
echo "(2) workon $PROJECT"
echo "(3) ./manage.py syncdb"
echo "(4) ./manage.py migrate"
