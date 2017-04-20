#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from SPARQLWrapper import SPARQLWrapper, JSON

languages = ['fr', 'en', 'br', 'de']


def wikidata_sparql_query(query):
    """
    Queries WDQS and returns the result
    """
    endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
    sparql = SPARQLWrapper(endpoint)
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

    if value % 100 // 10 != 1:
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


def statement(prop, value, source):
    """
    Returns a statement in the QuickStatements experted format
    """
    return "LAST\t{}\t{}\tS854\t\"{}\"".format(prop, value, source)


# Get what is already in Wikidata to ignore it
imported_episodes = []

results = wikidata_sparql_query("""
SELECT DISTINCT ?episode ?episodeLabel ?number WHERE {
  ?episode wdt:P31 wd:Q838795 .
  ?episode wdt:P361 wd:Q13915 .
  ?episode wdt:P433 ?number .

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
} ORDER BY xsd:integer(?number)
""")

for r in results["results"]["bindings"]:
    try:
        imported_episodes.append(int(r["number"]["value"]))
    except:
        print("{} has no episode number.".format(r))

latest_imported_episode = max(imported_episodes)

for i in range(1, latest_imported_episode):
    # There is no episode 404.
    if i not in imported_episodes and i != 404:
        print('Episode {} is missing :('.format(i))


# Get the episodes list
root_url = 'http://www.xkcd.com'
index_url = root_url + '/archive/index.html'

response = requests.get(index_url)
soup = BeautifulSoup(response.text, "lxml")

episodes = soup.select('div#middleContainer a')
episodes.reverse()

for e in episodes:
    title = "\"" + e.get_text() + "\"" or ""
    urlbit = e.attrs.get('href') or ""
    episode_url = root_url + urlbit
    episodenumber = urlbit.replace("/", "")

    if int(episodenumber) > latest_imported_episode:

        date = "+0000000" + '-'.join([
            "{0:0>2}".format(v) for v in e.attrs.get('title').split("-")]) + \
            "T00:00:00Z/11" or ""

        print("CREATE")
        for l in languages:
            print("LAST\tL{}\t{}".format(l, title))
            print("LAST\tA{}\t\"xkcd {}\"".format(l, episodenumber))

        print("LAST\tDfr\t\"strip de xkcd n°{}\"".format(episodenumber))
        print("LAST\tDde\t\"Folge des Webcomics xkcd\"")
        print("LAST\tDen\t\"{} strip of the webcomic xkcd\"".format(
            ordinal(episodenumber)))

        print(statement("P31", "Q838795", episode_url))  # instance of
        print(statement("P31", title, episode_url))  # instance of
        print(statement("P361", "Q13915", episode_url))  # part of
        print(statement("P433", '"' + episodenumber + '"', episode_url))  # nb
        print(statement("P577", date, episode_url))  # date
        print(statement("P50", "Q285048", episode_url))  # Author: R. Munroe
        print(statement("P2699", '"' + episode_url + '"', episode_url))  # URL
        print(statement("P364", "Q1860", episode_url))  # Language: English
        print(statement("P275", "Q6936496", episode_url))  # Licence: CC-BY-NC
        print("")
