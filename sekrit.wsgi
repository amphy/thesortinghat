#!/usr/bin/python

import os
# os.environ['PYTHON_EGG_CACHE'] = '/var/www/LeagueAPIChallenge/python-eggs' 

activate_this = '/var/www/sekrit/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/var/www/sekrit')
sys.path.append('/var/www/sekrit')

from hello import app as application
