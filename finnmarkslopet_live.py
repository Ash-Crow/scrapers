#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import re

verbose = 1

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

class Musher(object):
    def __init__(self, m_id):
        self.id = m_id
        self.number = ''
        self.name = ''
        self.country = ''
        self.residence = ''
        self.final_rank = 0 # 0: didn't finish (no explanation) | -1: disqualified
        self.last_checkpoint = ''
        self.dogs_number_start = 0
        self.dogs_number_end = 0

class Race(object):
    """An edition of the Finnmarkslopet."""

    # Faire un CSV par course
    #colonnes : numéro de dossard, nom du musher, classement final, lieu d'abandon le cas échéant, source
    def __init__(self, r_id):
        self.id = r_id
        self.raw_checkpoints = []
        self.label = ''
        self.raw_start = ''
        self.mushers=[]

    def statusUrl(self):
        """Returns the URL of the status page for this race"""
        return root_url + '/race/results/status.jsp?lang=en&rid=' + str(self.id)

    def resultsUrl(self):
        """Returns the URL of the results page for this race"""
        return root_url + '/race/results/results.jsp?lang=en&rid=' + str(self.id)

    def musherResultsUrl(self, m_id):
        """Returns the URL of the results page for a musher."""
        return root_url + '/race/results/musher.jsp?lang=en&rid=' + str(self.id) + '&entr.id=' + str(m_id)

    def getStatus(self):
        if verbose:
            print('Parsing race #{}'.format(self.id))
        """Get all data that can be scrapped from the status page"""
        status_url = r.statusUrl()
        response = requests.get(status_url)
        soup = BeautifulSoup(response.text)

        header = soup.select('#rshead')[0].find_all('span')
        self.label = header[0].string
        self.raw_start = header[2].string

        if verbose:
            print('Race: {} - startdate: {}'.format(self.label, self.raw_start))
 
        ###### STATUS GRID ######
        # The page has an awful structure with nested tables
        # so best to get down the tree manually.
        status = soup.select('#status-grid')
        status = status[0].contents[1].contents[1::2]

        del status[0] #Remove the title lign

        ###### CHECKPOINTS ######
        # Get the start point
        checkpoints_data = status.pop(0).find_all('td')

        #Remove the "→" cells
        checkpoints_data = checkpoints_data[::2]
        for c in checkpoints_data:
            checkpoint = c('img')[0].get('title').split(':')[0]

            self.raw_checkpoints.append(checkpoint)
            if checkpoint not in all_checkpoints:
                all_checkpoints.append(checkpoint)

        if verbose:
            print("Checkpoints:")
            for c in self.raw_checkpoints:
                print(c)
            print("\n")

        ###### MUSHER IDS ######
        for s in status:
            if len(s.contents) > 1:
                url = s.find_all('a')

                if len(url):
                    m_id = int(re.findall(r'\d+$', url[0].get('href'))[0])
                    self.mushers.append(m_id)

        if verbose >=1:
            print("{} mushers in the race".format(len(self.mushers)))
            print(self.mushers)


    def getMusherResults(self, m_id):
        musher = Musher(m_id)

        musher_results_url = r.musherResultsUrl(m_id)
        response = requests.get(musher_results_url)
        soup = BeautifulSoup(response.text)

        # Another tables mess to sort manually
        tables = soup.select('table')
        
        header = tables[1]('td')
        
        musher.number = header[0].string.split('.')[0].strip()
        musher.name = header[0].string.split('.')[1].strip()
        musher.country = header[2]('img')[0].get('title')
        musher.residence = header[4].string

        all_mushers.append(musher.name)
        if musher.country not in all_countries:
            all_countries.append(musher.country)

        if musher.residence not in all_cities:
            all_cities.append(musher.residence)

        if len(header) == 7:
            if header[6].string == '(Disqualified)':
                musher.final_rank = -1
            else:
                musher.final_rank = int(re.findall(r'\d+$', header[6].string)[0])
        
        checkpoints = tables[3]('tr')[1::]

        start = checkpoints.pop(0)
        musher.dogs_number_start = int(start('td')[3].strong.contents[0])

        for row in checkpoints:
            columns = row('td')

            if columns[1].string and not columns[2].string :
                if columns[3].string.strip():
                    musher.dogs_number_end = int(columns[3].string.strip())
                musher.last_checkpoint = columns[0].string
                break
            elif columns[3].strong:
                musher.dogs_number_end = int(columns[3].strong.contents[0])
                musher.last_checkpoint = columns[0].strong.string

        if verbose:
            print(musher.name, musher.number, musher.country, musher.residence, str(musher.final_rank), str(musher.dogs_number_start), str(musher.dogs_number_end), musher.last_checkpoint)

# Get the races list
races_ids = []
all_countries = []
all_cities = []
all_checkpoints = []
all_mushers = []

root_url = 'http://www.finnmarkslopet.no'
index_url = root_url + '/rhist/results.jsp?lang=en'

response = requests.get(index_url)
soup = BeautifulSoup(response.text)

races = soup.select('table.winners a')

for r in races:
    r_id = int(re.findall(r'\b\d+\b', r.get('href'))[0])
    races_ids.append(r_id)

# Cycle trough the races
#for r_id in range(1, last_race + 1):
"""
r_id = 57
r = Race(r_id)
r.getStatus()

#musher.residencer.getMusherResults(r.mushers[0])
#r.getMusherResults(2225)


for m in r.mushers:
    r.getMusherResults(m)

"""
for r_id in races_ids:
    r = Race(r_id)
    r.getStatus()
    for m in r.mushers:
        r.getMusherResults(m)
#"""
print("\n\n=========")
print("Checkpoints:\n")
print(sorted(all_checkpoints))

print("\n\n=========")
print("Countries:\n")
print(sorted(all_countries))
print("\n\n=========")
print("Cities:\n")
print(all_cities)
print("\n\n=========")
print("Mushers:\n")
print(sorted(all_mushers))