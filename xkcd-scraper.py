#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


def wikidata_query(query, props=''):
    """
    Queries WDQ and returns the result
    """
    query_url = 'https://wdq.wmflabs.org/api?q=' + query 

    if props:
        query_url += '&props=' + props

    response = urlopen(query_url)
    encoding = response.headers.get_content_charset() or 'utf-8'

    result = json.loads(response.read().decode(encoding))

    return result


def ordinal(value):
    """
    Converts zero or a *positive* integer (or its string 
    representation) to an ordinal value.
    """
    try:
        value = int(value)
    except ValueError:
        return value

    if value % 100//10 != 1:
        if value % 10 == 1:
            ordval = u"%d%s" % (value, "st")
        elif value % 10 == 2:
            ordval = u"%d%s" % (value, "nd")
        elif value % 10 == 3:
            ordval = u"%d%s" % (value, "rd")
        else:
            ordval = u"%d%s" % (value, "th")
    else:
        ordval = u"%d%s" % (value, "th")

    return ordval

# Get what is already in Wikidata to ignore it
imported_episodes = []

query = wikidata_query('claim[31:838795]%20AND%20claim[361:13915]','433')
for i in query['props']['433']:
    try:
        imported_episodes.append(int(i[2]))
    except:
        print("{} has no episode number.".format(i))

latest_imported_episode = max(imported_episodes)
#print("{} episodes already on Wikidata, the last one is {}.".format(len(imported_episodes), latest_imported_episode))

for i in range(1, latest_imported_episode):
    # There is no episode 404.
    if i not in imported_episodes and i != 404:
        print('Episode {} is missing :('.format(i))


# Get the episodes list
root_url = 'http://www.xkcd.com'
index_url = root_url + '/archive/index.html'

response = requests.get(index_url)
soup = BeautifulSoup(response.text)

header = "qid, s854|url source, Lfr, Len, Lbr, Lde, Dfr, Dde, Den, p31, p361|partie de, p433|numéro, p577|date de publication, p50|auteur, p854|url"

print(header)

episodes = soup.select('div#middleContainer a')
episodes.reverse()

for a in episodes:
    title = "\"" + a.get_text() + "\"" or ""
    urlbit = a.attrs.get('href') or ""
    episode_url = root_url + urlbit
    episodenumber = urlbit.replace("/","")

    if int(episodenumber) > latest_imported_episode:
        descriptions = "strip de xkcd n° " + episodenumber + ", Folge des Webcomics xkcd, " + ordinal(episodenumber) + " strip of the webcomic xkcd"
        #date = a.attrs.get('title') or ""
        date = "+0000000" + '-'.join(["{0:0>2}".format(v) for v in a.attrs.get('title').split("-")]) + "T00:00:00Z/11" or ""

        print("," + index_url + "," + title + "," + title + "," + title + "," + title + ","
        + descriptions + ", q838795|Comic strip , q13915|xkcd, " + episodenumber + "," + date + ", q285048|Randall," + episode_url)