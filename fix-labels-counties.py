#!/usr/bin/env python3

from SPARQLWrapper import SPARQLWrapper, JSON


endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparqlba"

sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
SELECT ?county ?countyLabelFr
WHERE {
  ?county wdt:P31/wdt:P279* wd:Q47168 .
  ?county wdt:P31 ?type .
  ?county rdfs:label ?countyLabelFr . FILTER (LANG(?countyLabelFr) = "fr") .
  FILTER ( STRSTARTS(?countyLabelFr, "Comté d" ) ) .
} GROUP BY ?county ?countyLabelEn ?countyLabelFr HAVING(COUNT(?type) = 1)
""")  # Link to query: http://tinyurl.com/h83bqbr

sparql.setReturnFormat(JSON)

results = sparql.query().convert()

out = ""

for result in results["results"]["bindings"]:
    item = result['county']['value'].rsplit('/', 1)[-1]
    label = result['countyLabelFr']['value']

    label = label[:1].lower() + label[1:]

    out += "{}\tLfr\t\"{}\"\n".format(item, label)


f = open('temp.txt', 'w')
f.write(out)
f.close()

qs_url = "https://tools.wmflabs.org/wikidata-todo/quick_statements.php"

print("Operation complete!")
print("- Please paste the content of temp.txt to {}".format(qs_url))
