#!/usr/bin/env python3

from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint

endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"

sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
# UnincorporatedArea
SELECT ?item
(SAMPLE(?item_label_en) AS ?item_label_en)
(SAMPLE(?item_label_fr) AS ?item_label_fr)
(SAMPLE(?item_desc_fr) AS ?item_desc_fr)
(SAMPLE(?countyLabel) AS ?countyLabel)
(SAMPLE(?stateLabel) AS ?stateLabel) WHERE {
  ?item wdt:P31 wd:Q17343829 .
  ?item rdfs:label ?item_label_en . FILTER(LANG(?item_label_en) = "en") .
  OPTIONAL { ?item rdfs:label ?item_label_fr . FILTER(LANG(?item_label_fr) = "fr") . }
  OPTIONAL { ?item schema:description ?item_desc_fr . FILTER(LANG(?item_desc_fr) = "fr") . }
  
  # county
  ?item wdt:P131* ?county .
  ?county wdt:P31/wdt:P279* wd:Q47168 .
  ?county rdfs:label ?county_label_en . FILTER(LANG(?county_label_en) = "en") .

  # State
  ?item wdt:P131* ?state .
  ?state wdt:P31/wdt:P279* wd:Q35657 .
  ?state rdfs:label ?state_label_en . FILTER(LANG(?state_label_en) = "en") .
} GROUP BY ?item LIMIT 100
""")  # Link to query: http://tinyurl.com/hju3gpt

sparql.setReturnFormat(JSON)

results = sparql.query().convert()

out = ""

pprint(results["results"]["bindings"])

"""
for result in results["results"]["bindings"]:
    item = result['item']['value'].rsplit('/', 1)[-1]
    label = result['label']['value']

    label = label[:1].lower() + label[1:]

    out += "{}\tLfr\t{}\n".format(item, label)


f = open('temp.txt', 'w')
f.write(out)
f.close()

qs_url = "https://tools.wmflabs.org/wikidata-todo/quick_statements.php"

print("Operation complete!")
print("- Please paste the content of temp.txt to {}".format(qs_url))
"""