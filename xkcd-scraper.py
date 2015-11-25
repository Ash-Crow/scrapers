#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
from SPARQLWrapper import SPARQLWrapper, JSON


try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def wikidata_sparql_query(query):
    """
    Queries WDQS and returns the result
    """

    sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
    sparql.setQuery(query)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

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

results = wikidata_sparql_query(
"""
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?episode ?episodeLabel ?number WHERE {
  ?episode wdt:P31 wd:Q838795 .
  ?episode wdt:P361 wd:Q13915 .
  ?episode wdt:P433 ?number .

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
} ORDER BY xsd:integer(?number)
"""
)

for r in results["results"]["bindings"]:
    try:
        imported_episodes.append(int(r["number"]["value"]))
    except:
        print("{} has no episode number.".format(r))

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
        descriptions = "strip de xkcd n°" + episodenumber + ", Folge des Webcomics xkcd, " + ordinal(episodenumber) + " strip of the webcomic xkcd"
        #date = a.attrs.get('title') or ""
        date = "+0000000" + '-'.join(["{0:0>2}".format(v) for v in a.attrs.get('title').split("-")]) + "T00:00:00Z/11" or ""

        print("," + index_url + "," + title + "," + title + "," + title + "," + title + ","
        + descriptions + ", q838795|Comic strip , q13915|xkcd, " + episodenumber + "," + date + ", q285048|Randall," + episode_url)