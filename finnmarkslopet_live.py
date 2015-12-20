#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import os               # Files and folder manipulations
import re               # Regular expressions
import csv              # CSV file manipulations 
from collections import Counter
from termcolor import colored

verbose = 1

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

class WikidataItem(object):
    def __init__(self):
        self.label = ''
        self.qid = ''

    def set_qid(self):
        if self.label in self.qids_list:
            self.qid = self.qids_list[self.label]
        elif verbose:
            print('Unknown {}: {}'.format(self.type, self.label))
            if self.type == 'race':
                unknown_races_qids.append(self.label)
            else:
                unknown_mushers_qids.append(self.label)
        
class Musher(WikidataItem):
    def __init__(self, m_id):
        super().__init__()
        self.type = "musher"
        self.id = m_id
        self.number = ''
        self.country = ''
        self.country_qid = ''
        self.residence = ''
        self.final_rank = 0 # 0: didn't finish (no explanation) | -1: disqualified
        self.last_checkpoint = ''
        self.last_checkpoint_qid = ''
        self.dogs_number_start = 0
        self.dogs_number_end = 0
        self.qids_list = musher_qids

class Race(WikidataItem):
    """An edition of the Finnmarkslopet."""

    # Faire un CSV par course
    #colonnes : numéro de dossard, nom du musher, classement final, lieu d'abandon le cas échéant, source
    def __init__(self, r_id):
        super().__init__()
        self.type = "race"
        self.id = r_id
        self.raw_checkpoints = []
        self.raw_start = ''
        self.mushers=[]
        self.qids_list = race_qids

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
        status_url = self.statusUrl()
        response = requests.get(status_url)
        soup = BeautifulSoup(response.text)


        # Header is in the form "<race> <year>", we need "<year> <race>"
        header = soup.select('#rshead')[0].find_all('span')
        raw_label = header[0].string.split()
        for i in raw_label:
            if i.isdigit():
                self.year = i
                raw_label.remove(i)
        self.label = "{} {}".format(self.year, ' '.join(raw_label))
        self.raw_start = header[2].string

        self.set_qid()

        if verbose:
            print(colored('Race: {} ({}) - startdate: {}'.format(self.label, self.qid, self.raw_start), 'green'))
 
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

        musher_results_url = self.musherResultsUrl(m_id)
        response = requests.get(musher_results_url)
        soup = BeautifulSoup(response.text)

        # Another tables mess to sort manually
        tables = soup.select('table')
        
        header = tables[1]('td')
        
        # The first <td> contains the number and the name with a '.' in between
        # The name of the musher can also have a '.', though...

        raw_header = header[0].string.split('.')
        raw_header = [item.strip() for item in raw_header]
        musher.number = raw_header.pop(0)
        musher.label = re.sub(' +',' ', '. '.join(raw_header))
        musher.country = header[2]('img')[0].get('title')
        musher.country_qid = country_qids[musher.country]
        musher.residence = header[4].string

        musher.set_qid()

        all_mushers.append(musher.label)
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


        #Manually manage the most crappy entries.
        if self.qid=='Q18645361' and musher.qid=='Q18674757':
            #Torgeir Øren in 1992 FL Open 
            musher.last_checkpoint = 'Strand Camping'
            musher.dogs_number_end = 0
        elif self.qid=='Q21585426' and musher.qid=='Q19361431':
            # Andreas Tømmervik (Q19361431) in the 2015 FL500 (Q21585426)
            musher.last_checkpoint = 'Jotka'
            musher.dogs_number_end = 7
        elif self.qid=='Q21585426' and musher.qid=='Q21585655':
            # Radek Havrda (Q21585655) in the 2015 FL500 (Q21585426)            
            musher.last_checkpoint = 'Jotka'
            musher.dogs_number_end = 6
        elif self.qid=='Q18645138' and musher.qid=='Q21455487':
            # Johanne Sundby (Q21455487) in the 2008 FL500 (Q18645138)
            musher.last_checkpoint = 'Jotka'
            musher.dogs_number_end = 6
        elif self.qid=='Q18645147' and musher.qid=='Q21467516':
            # Mathias Jenssen (Q21467516) in the 2011 FL500 (Q18645147)
            musher.last_checkpoint = 'Jotka'
            musher.dogs_number_end = 5
        elif self.qid=='Q18645150' and musher.qid=='Q21467762':
            # Øyvind Skogen (Q21467762) in the 2012 FL500 (Q18645150)            
            musher.last_checkpoint = 'Jotka'
            musher.dogs_number_end = 7
        else:
            for row in checkpoints:
                columns = row('td')

                if columns[1].string and not columns[2].string :
                    dogs = columns[3].string.strip()
                    if columns[3].string.strip():
                        musher.dogs_number_end = int(columns[3].string.strip())
                    musher.last_checkpoint = columns[0].string
                    break
                elif columns[3].strong:
                    musher.dogs_number_end = int(columns[3].strong.contents[0])
                    musher.last_checkpoint = columns[0].strong.string
                else:
                    dogs = columns[3].string.strip()
                    if dogs:
                        musher.dogs_number_end = int(dogs)
                    col_mess = '' # '| {} || {} || {} || {} |'.format(columns[0], columns[1], columns[2], columns[3])
                    musher.last_checkpoint = ('No last checkpoint found for {} ({}) in the {} ({}) -- {}'.format(musher.label, musher.qid, self.label, self.qid, col_mess))

        #manually force the number of dogs for those who abandoned before the first checkpoint
        quick_abandons = ['Q21570604', 'Q21462927']
        if musher.qid in quick_abandons:
            musher.dogs_number_end = musher.dogs_number_start

        if musher.last_checkpoint in checkpoints_qids:
            musher.last_checkpoint_qid = checkpoints_qids[musher.last_checkpoint]
        else:
            if verbose:
                print(colored("Unknown checkpoint: {}".format(musher.last_checkpoint), 'yellow'))
            unknown_checkpoints_qids.append(musher.last_checkpoint)

        if musher.dogs_number_start <=0:
            if verbose:
                print(colored("Musher with no dogs at start: {} ({}) in the {} ({})".format(musher.label, musher.qid, self.label, self.qid), 'yellow'))
            no_dogs_at_start.append("{} ({}) in the {} ({})".format(musher.label, musher.qid, self.label, self.qid))
        
        if musher.dogs_number_end <=0:
            if verbose:
                print(colored("Musher with no dogs at the end: {} ({}) in the {} ({}) -- Final rank: {}".format(musher.label, musher.qid, self.label, self.qid, musher.final_rank), 'yellow'))
            no_dogs_at_end.append("{} ({}) in the {} ({}) -- Final rank: {}".format(musher.label, musher.qid, self.label, self.qid, musher.final_rank))

        if verbose:
            print(musher.label, musher.qid, musher.number, musher.country, musher.country_qid, str(musher.final_rank), str(musher.dogs_number_start), str(musher.dogs_number_end), musher.last_checkpoint, musher.last_checkpoint_qid)


def import_ids():
    """
    Import the qids of the mushers, checkpoints and races on Wikidata
    """
    with open(races_dir + 'finnmarkslopet/' + 'finnmarkslopet-qid.csv', 'r') as csv_race_ids:
        reader = csv.DictReader(csv_race_ids)
        for row in reader:
            race_qids.update({row['race']: row['qid'] })
    csv_race_ids.closed

    with open(races_dir + 'finnmarkslopet/' + 'checkpoint-id.csv', 'r') as csv_checkpoints_ids:
        reader = csv.DictReader(csv_checkpoints_ids)
        for row in reader:
            checkpoints_qids.update({row['Checkpoint']: row['qid'] })
    csv_checkpoints_ids.closed

    with open(races_dir + 'mushers-qid.csv', 'r') as csv_musher_ids:
        reader = csv.DictReader(csv_musher_ids)
        for row in reader:
            if verbose and row['label'] in musher_qids.keys():
                print('Duplicate Musher: {}'.format(row['label']))
            musher_qids.update({row['label']: row['qid'] })
            if row['alias']:
                aliases = row['alias'].split('|')
                for alias in aliases:
                    alias = alias.strip()
                    if verbose and alias in musher_qids.keys():
                        print('Duplicate Musher: {}'.format(alias))
                    musher_qids.update({alias: row['qid'] })
    csv_musher_ids.closed

"""
Presets
"""
country_qids = {
    'Aragon': 'Q29', #Spain
    'Austria': 'Q40',
    'Basque country': 'Q47588',
    'Belgia': 'Q31',
    'Catalonia': 'Q29', #Spain
    'Czech Republic': 'Q213',
    'Denmark': 'Q35',
    'England': 'Q145', #UK
    'Faroe Islands': 'Q4628',
    'Finland': 'Q33',
    'France': 'Q142',
    'Germany': 'Q183',
    'Great Britain': 'Q145', #UK
    'Hungary': 'Q28',
    'Iceland': 'Q189',
    'Italy': 'Q38',
    'Nederland': 'Q55',
    'Norway': 'Q20',
    'Poland': 'Q36',
    'Russia': 'Q159',
    'Scotland': 'Q145', #UK
    'Slovakia': 'Q214',
    'Spain': 'Q29',
    'Sweden': 'Q34',
    'Swiss': 'Q39',
    'USA': 'Q30',
    'Uruguay': 'Q77',
    'Wales': 'Q145' #UK
}

dropbox_dir = os.environ['HOME'] + "/Dropbox/"
races_dir = dropbox_dir + 'finnmarkslopet/'
race_qids = {}
checkpoints_qids = {}
musher_qids = {}
unknown_races_qids = []
unknown_checkpoints_qids = []
unknown_mushers_qids = []
no_dogs_at_start = []
no_dogs_at_end = []

import_ids()

"""
The main part of the script
"""

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

#"""
for r in races:
    r_id = int(re.findall(r'\b\d+\b', r.get('href'))[0])
    races_ids.append(r_id)

# Cycle trough the races
def parse_single_race(r_id):
    r = Race(r_id)
    r.getStatus()
    for m in r.mushers:
        r.getMusherResults(m)

def parse_all_races():
    for r_id in races_ids:
        parse_single_race(r_id)

#parse_single_race(52)
parse_all_races()

print("\n\n=========")
print("Checkpoints:\n")
print(sorted(all_checkpoints))

print("\n\n=========")
print("Countries:\n")
print(sorted(all_countries))
print("\n\n=========")
#print("Cities:\n")
#print(all_cities)
#print("\n\n=========")
print("Mushers:\n")
print(sorted(all_mushers))
print("\n\n=========")
print("Unknown qIDs:\n")
print("races:")
print(sorted(unknown_races_qids))
print("checkpoints")
print(sorted(unknown_checkpoints_qids))
print("mushers")
print(sorted(unknown_mushers_qids))

print("\n\n=========")
print("No dogs at start:")
print(sorted(no_dogs_at_start))

print("No dogs in the end:")
for n in no_dogs_at_end:
    print(n)
#"""
