#!/usr/bin/env python3

from SPARQLWrapper import SPARQLWrapper, JSON

endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"

sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
SELECT ?item ?label WHERE {{
  ?item wdt:P31/wdt:P279* wd:Q178561 .
  ?item rdfs:label ?label . FILTER(LANG(?label) = "fr") .
  FILTER(STRSTARTS(?label, "Bataille ")) .
}}
""")  # Link to query: http://tinyurl.com/hju3gpt

sparql.setReturnFormat(JSON)

results = sparql.query().convert()

out = ""

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
