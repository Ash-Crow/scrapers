#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from SPARQLWrapper import SPARQLWrapper, JSON

unmatched_wikipedia = []
unmatched_imdb = []
unmatched_other = []
matched = []

# Get what is already in Wikidata
endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
SELECT ?item ?itemLabel ?imdb ?source ?sitelink WHERE {
  ?item wdt:P31 wd:Q5 .
  ?item p:P69 ?statement .
  ?statement ps:P69 wd:Q981195 .

  OPTIONAL {
    ?statement prov:wasDerivedFrom ?ref .
    ?ref (pr:P854|pr:P143) ?source .
  }

  OPTIONAL { ?sitelink schema:about ?item ;
                       schema:isPartOf <https://en.wikipedia.org/> . }

  OPTIONAL { ?item wdt:P345 ?imdb . }


  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
results = results['results']['bindings']

# Get content from the CSSD website
alumni_url = "http://www.cssd.ac.uk/content/high-profile-alumni"
response = requests.get(alumni_url)
soup = BeautifulSoup(response.text, "lxml")

alumni = soup.select("p")

for alumnus in alumni:
    if alumnus.strong in alumnus:
        urls = alumnus.select("a")
        name = alumnus.strong.text[:-3]
        for url in urls:
            url = url['href']
            if "wikipedia" in url:
                wikipedia = url.replace("_", "%20")
                wikipedia = wikipedia.replace("(", "%28")
                wikipedia = wikipedia.replace(")", "%29")
                wikipedia = wikipedia.replace("http:", "https:")
                # print(wikipedia)
            else:
                wikipedia = ""
            if "imdb.com" in url:
                imdb = url.split('/')[-2]
            else:
                imdb = ""

            qid = ""
            for r in results:
                if wikipedia and 'sitelink' in r:
                    if wikipedia == r['sitelink']['value']:
                        qid = r['item']['value'].split('/')[-1]

                if imdb and 'imdb' in r:
                    if imdb == r['imdb']['value']:
                        qid = r['item']['value'].split('/')[-1]
            if qid:
                matched.append(qid)
            else:
                if wikipedia:
                    unmatched_wikipedia.append(name)
                if imdb:
                    unmatched_imdb.append(imdb)
                if not wikipedia and not imdb:
                    unmatched_other.append(name)

print("Matched")
print(matched)

print("Unmatched Wikipedia")
print(unmatched_wikipedia)

print("Unmatched IMDb")
print(unmatched_imdb)

print("Unmatched Other")
print(unmatched_other)

print('QS')
for m in matched:
    print('\t'.join([m,
                     'P69',
                     'Q981195',
                     'S854',
                     '"http://www.cssd.ac.uk/content/high-profile-alumni"']))
