#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re               # Regular expressions
import sys

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def to_minutes(datestring):
    datestring = re.sub('\+','', datestring)
    date_chunks = datestring.split()

    minutes = 0
    for c in date_chunks:
        if 'd' in c:
            minutes += int(c[:-1]) * 24 * 60
        elif 'h' in c:
            minutes += int(c[:-1]) * 60
        elif 'min' in c:
            minutes += int(c[:-3])

    return minutes

def resultatliste(r_id):

    results_url = root_url + '/race/results/results.jsp?rid=' + r_id
    response = requests.get(results_url)
    soup = BeautifulSoup(response.text)

    header = soup.select('#rshead')[0].find_all('span')
    raw_label = header[0].text
    print('Parsing race #{} - {}'.format(r_id, raw_label))

    results_list = soup.select('table tr')
    results_list.pop(0)

    winner_time = 0

    for row in results_list:
        columns = row('td')
        current_row = {}

        rank = columns[0].text
        number = columns[1].text
        name = columns[2].text
        time = columns[5].text

        minutes = to_minutes(time)

        if not winner_time:
            winner_time = minutes
        else:
            minutes += winner_time

        print('{:>3}\t{:>4}\t{:<25}\t{}\t{}'.format(rank, number, name, time, minutes))

# variables
root_url = 'http://www.finnmarkslopet.no'

# Main part
if len(sys.argv) == 2:
    if sys.argv[1].isdigit():
        resultatliste(sys.argv[1])
    else:
        raise ValueError("Invalid argument")
else:
    raise ValueError("Please indicate the race number")
