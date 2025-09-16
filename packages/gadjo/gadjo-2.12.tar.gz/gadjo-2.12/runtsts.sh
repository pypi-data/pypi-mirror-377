#! /bin/sh

. ../venv/bin/activate
PYTHONPATH=tests/:$PYTHONPATH py.test $@
