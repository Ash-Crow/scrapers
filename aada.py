#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup, Tag
from SPARQLWrapper import SPARQLWrapper, JSON

# Get content from the AADA website
soup = BeautifulSoup(open("temp.html"), 'lxml')

alumni = soup.select(".alumni_casting_listing figcaption")

# print(alumni)

imdb_ids = []
ibdb_ids = []
imdb_years = {}
qid_years = {}

for alumnus in alumni:
    last_name = alumnus.span.text
    year = alumnus.em.span.text

    if isinstance(alumnus.a, Tag):
        url = alumnus.a['href']
        if 'imdb'in url:
            imdb = url.split('/')[4]
            imdb_ids.append(imdb)
            imdb_years[imdb] = year
        if 'ibdb' in url:
            ibdb = url.split('=')[1]
            ibdb_ids.append(ibdb)

imdb_ids_list = ('" "').join(imdb_ids)

query = """
SELECT ?item ?imdb WHERE {{
  VALUES ?imdb {{ "{ids}" }}
  OPTIONAL {{ ?item wdt:P345 ?imdb . }}
}}
""".format(ids=imdb_ids_list)

print(query)
# Get what is already in Wikidata
endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
sparql = SPARQLWrapper(endpoint)
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
results = results['results']['bindings']


print(results)

matched = []
unmatched = []
for imdb in imdb_ids:
    for r in results:
        print(r)
        if 'item' in r and imdb == r['imdb']['value']:
            qid = r['item']['value'].split('/')[-1]

    if qid:
        matched.append(qid)
        qid_years[qid] = imdb_years[imdb]
    else:
        unmatched.append(imdb)

print('Matched')
print(matched)

print('Unmatched')
print(unmatched)

for m in matched:
    print('\t'.join([m,
                     'P69',
                     'Q389336',
                     'P582',
                     "+{}-01-01T00:00:00Z/09".format(qid_years[m]),
                     'S854',
                     '"https://www.aada.edu/alumni/notable-alumni#decade:all/orderby:all/display:panel/perpage:All"']))
