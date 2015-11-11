#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import re

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

class Race(object):
    """An edition of the Finnmarkslopet."""

    # Faire un CSV par course
    #colonnes : numéro de dossard, nom du musher, classement final, lieu d'abandon le cas échéant, source
    def __init__(self, r_id):
        self.mushers = {}
        self.id = r_id

    def status_url(self):
        """Returns the URL of the status page for this race"""
        return root_url + '/race/results/status.jsp?lang=en&rid=' + str(self.id)

    def results_url(self):
        """Returns the URL of the results page for this race"""
        return root_url + '/race/results/results.jsp?lang=en&rid=' + str(self.id)

# Get the races list
last_race = 0

root_url = 'http://www.finnmarkslopet.no'
index_url = root_url + '/rhist/results.jsp?lang=en'

response = requests.get(index_url)
soup = BeautifulSoup(response.text)

races = soup.select('table.winners a')

for r in races:
    r_id = int(re.findall(r'\b\d+\b', r.get('href'))[0])
    if r_id > last_race:
        last_race = r_id

# Cycle trough the races
for r_id in range(1, last_race + 1):
    r = Race(r_id)
    status_url = status_url(r)
    results_url = result_url(r)
