#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Exemple d'une course bien remplie : https://www.wikidata.org/wiki/Q19455277

import requests
from bs4 import BeautifulSoup, NavigableString
import datetime
import json
import os               # Files and folder manipulations
import re               # Regular expressions
import csv              # CSV file manipulations 
import sys
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
        self.finish_time = 0
        self.total_time = 0

class Race(WikidataItem):
    """An edition of the Finnmarkslopet."""

    # Faire un CSV par course
    #colonnes : numéro de dossard, nom du musher, classement final, lieu d'abandon le cas échéant, source
    def __init__(self, r_id):
        super().__init__()
        self.type = "race"
        self.id = r_id
        self.raw_checkpoints = []
        self.checkpoints = []
        self.raw_start = ''
        self.mushers=[]
        self.qids_list = race_qids
        self.winner = ""
        self.distance = 0

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
        """Get all data that can be scrapped from the status page"""

        if verbose:
            print('Parsing race #{}'.format(self.id))

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
        if verbose:
                print("Checkpoints:")
        for c in checkpoints_data:
            checkpoint = c('img')[0].get('title').split(':')[0].strip()

            self.raw_checkpoints.append(checkpoint)
            if checkpoint not in all_checkpoints:
                all_checkpoints.append(checkpoint)

            if checkpoint in checkpoints_qids:
                self.checkpoints.append(checkpoints_qids[checkpoint])
                if verbose:
                        print(checkpoint, checkpoints_qids[checkpoint])
            else:
                if verbose:
                    print(colored("Unknown checkpoint: '{}'".format(checkpoint), 'yellow'))
                unknown_checkpoints_qids.append("{} (race: {})".format(checkpoint, self.qid))

        self.distance = int(checkpoints_data[-1]('img')[0].get('title').split(':')[1].split()[0])

        if verbose:
            print("\n")
            print("Total distance: {}".format(self.distance))
            print("\n")

        ###### MUSHER IDS ######
        # List of registered mushers that didn't even start the race
        did_not_start = [133]
        for s in status:
            if len(s.contents) > 1:
                url = s.find_all('a')

                if len(url):
                    m_id = int(re.findall(r'\d+$', url[0].get('href'))[0])
                    if m_id not in did_not_start:
                        self.mushers.append(m_id)

        if verbose >=1:
            print("{} mushers in the race".format(len(self.mushers)))
            print(self.mushers)

    def getMusherResults(self, m_id):
        global quick_statements
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
        musher.label = re.sub(' +',' ', '. '.join(raw_header)).strip()
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
                if musher.final_rank == 1:
                    self.winner = musher.qid
        
        raw_checkpoints = tables[3]('tr')[1::]
        cleaned_checkpoints = []

        for row in raw_checkpoints:
            columns = row('td')
            current_row = {}

            current_row['checkpoint'] = strip_tags(columns[0])
            current_row['time_in'] = strip_tags(columns[1])
            current_row['time_out'] = strip_tags(columns[2])
            if len(columns) > 3:
                dogs = strip_tags(columns[3])
                if dogs:
                    if not dogs.isdigit():
                        dogs = re.sub('<s></s>', '', dogs) #empty <s> tag on some lines...
                    dogs = int(dogs)

                current_row['dogs'] = dogs

            cleaned_checkpoints.append(current_row)

        #check if the musher did start the race at all
        if not cleaned_checkpoints[0]['time_out']:
            self.mushers.remove(m_id)
        else:
            musher.dogs_number_start = cleaned_checkpoints[0]['dogs'] 
            for i in cleaned_checkpoints:
                if i['dogs']:
                    musher.dogs_number_end = i['dogs']

                if i['time_in']:
                    musher.last_checkpoint = i['checkpoint']
                    start_time = convert_time(self.year, cleaned_checkpoints[0]['time_out'])
                    musher.finish_time =  convert_time(self.year,i['time_in'])

                    musher.total_time = int((musher.finish_time - start_time).total_seconds()/60)

            # if the musher didn't even manage to the first checkpoint
            if not musher.last_checkpoint:
                musher.last_checkpoint = cleaned_checkpoints[0]['checkpoint']
                musher.finish_time = convert_time(self.year, cleaned_checkpoints[0]['time_out'])

            #manually force the number of dogs where the table is wrong
            dog_number_error = [312, 314]

            if musher.id in dog_number_error:
                musher.dogs_number_end = 0
                musher.dogs_number_start = 0

            if musher.last_checkpoint in checkpoints_qids:
                musher.last_checkpoint_qid = checkpoints_qids[musher.last_checkpoint]
            else:
                if verbose:
                    print(colored("Unknown checkpoint: {}".format(musher.last_checkpoint), 'yellow'))
                unknown_checkpoints_qids.append("{} ({} in the {})".format(musher.last_checkpoint, musher.qid, self.qid))

            if musher.dogs_number_start <=0:
                if verbose:
                    print(colored("Musher with no dogs at start: {} ({}) in the {} ({})".format(musher.label, musher.id, self.label, self.qid), 'yellow'))
                no_dogs_at_start.append("{} ({}) in the {} ({})".format(musher.label, musher.id, self.label, self.qid))
            
            if musher.dogs_number_end <=0:
                if verbose:
                    print(colored("Musher with no dogs at the end: {} ({}) in the {} ({}) -- Final rank: {}".format(musher.label, musher.id, self.label, self.qid, musher.final_rank), 'yellow'))
                no_dogs_at_end.append("{} ({}) in the {} ({}) -- Final rank: {}".format(musher.label, musher.id, self.label, self.qid, musher.final_rank))

            if verbose:
                print(musher.label, musher.id, musher.qid, musher.number, musher.country, musher.country_qid, str(musher.total_time), str(musher.final_rank), str(musher.dogs_number_start), str(musher.dogs_number_end), musher.last_checkpoint, musher.last_checkpoint_qid)

            #quick_statements += self.participant_quick_statements(musher) + "\n"

    def race_quick_statements(self):
        reference = "\tS854\t\"{}\"".format(self.statusUrl())
        
        #winner
        statement = "{}\tP1346\t{}".format(self.qid, self.winner) + reference + "\n"

        # entrants
        statement += "{}\tP1132\t{}".format(self.qid, len(self.mushers)) + reference + "\n"

        # Starting point
        statement += "{}\tP1427\t{}".format(self.qid, self.checkpoints[0]) + reference + "\n"

        # Destination
        statement += "{}\tP1444\t{}".format(self.qid, self.checkpoints[-1]) + reference + "\n"

        # Checkpoints
        for k, v in enumerate(self.checkpoints):
            rank = k + 1
            statement += "{}\tP276\t{}\tP1545\t\"{}\"".format(self.qid, v, rank)
            if rank not in [1, len(self.checkpoints)]:
                statement += "\tP31\tQ19162210" 
            statement += reference + "\n"

        # Total distance
        statement += "{}\tP2043\t{}".format(self.qid, self.distance) + reference + "\n"

        return statement

    def participant_quick_statements(self, musher):
        # qualifiers in reverse order because QS starts by the end
        # Doc de QS : https://tools.wmflabs.org/wikidata-todo/quick_statements.php
        statement = "{}\tP710\t{}".format(self.qid, musher.qid)

        if musher.final_rank > 0 and musher.dogs_number_end > 0:
            statement += "\tP2105\t{}".format(musher.dogs_number_end)

        if musher.dogs_number_start > 0:
            statement += "\tP2103\t{}".format(musher.dogs_number_start)

        if musher.number:
            statement += "\tP1618\t\"{}\"".format(musher.number)

        if musher.finish_time:
            statement += "\tP585\t+0000000{0:%Y}-{0:%m}-{0:%d}T00:00:00Z/11".format(musher.finish_time)


        if musher.final_rank > 0:
            statement += "\tP2047\t{}".format(musher.total_time)
            statement += "\tP1352\t{}".format(musher.final_rank)

        else:
            if musher.last_checkpoint_qid:
                statement += "\tP276\t{}".format(musher.last_checkpoint_qid)

            if musher.final_rank == -1:
                # disqualification
                statement += "\tP793\tQ1229261"
            else:
                # abandon
                statement += "\tP793\tQ18595374"
        
        reference = "\tS854\t\"{}\"".format(self.musherResultsUrl(musher.id))
        return statement + reference

def strip_tags(string):
    if isinstance(string, str):
        soup = BeautifulSoup(string)
    else:
        soup = string

    for tag in soup.findAll(True):
        s = ""

        for c in tag.contents:
            if not isinstance(c, NavigableString):
                c = strip_tags(c)
            s += str(c).strip()

        tag.replaceWith(s)

    return soup.text.strip()

def convert_time(year, date_string):
    # base format is "D/M H:M" 
    date_chunks = date_string.split()
    
    day_month = date_chunks[0].split('/')
    day = int(day_month[0])
    month = int(day_month[1])

    hour_min =  date_chunks[1].split(':')
    hour = int(hour_min[0])
    minute = int(hour_min[1])

    return datetime.datetime(int(year), month, day, hour, minute)

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


def parse_single_race(r_id, m_id = 0):
    global quick_statements

    r = Race(r_id)
    r.getStatus()

    if m_id:
        r.getMusherResults(m_id)
    else:
        for m in r.mushers:
            r.getMusherResults(m)

    quick_statements += r.race_quick_statements() + "\n"


def parse_all_races():
    for r_id in races_ids:
        parse_single_race(r_id)

def save_quick_statements(text):
    if len(text):
        file = 'qs.txt'
        with open(file,"w") as f:
            f.write(text)
            f.close()

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
quick_statements = ""

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
if len(sys.argv) > 1:
    if all(arg.isdigit() for arg in sys.argv[1:]):
        if len(sys.argv) == 3:
            parse_single_race(sys.argv[1], sys.argv[2]) #parse a single musher in a single race
        else:
            parse_single_race(sys.argv[1]) #parse all mushers in a single race
    else:
        raise ValueError("Invalid arguments")
else:
    parse_all_races()

save_quick_statements(quick_statements)

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
