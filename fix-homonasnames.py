#!/usr/bin/env python3
import pprint
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"

sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
SELECT DISTINCT
?item
?itemLabel
?familyname
?familynameLabel
WHERE {
  {
    SELECT DISTINCT
    ?item 
    (SAMPLE(?familyname) AS ?familyname)
    WHERE {
      ?item wdt:P734 ?name .

      ?name wdt:P31 wd:Q4167410 ;
            wdt:P1889 ?familyname .
      
      ?familyname wdt:P31 wd:Q101352 .
    } GROUP BY ?item HAVING (COUNT(?name) = 1 && COUNT(?familyname) = 1) ORDER BY ?item_label
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en,es,pl,it,ru" }
} ORDER BY ?familynameLabel
""")  # Link to query: http://tinyurl.com/hmk5x3o

sparql.setReturnFormat(JSON)

results = sparql.query().convert()

pprint.pprint(results)

out = ""
all_items = []

for result in results["results"]["bindings"]:
    item = result['item']['value'].rsplit('/', 1)[-1]
    familyname = result['familyname']['value'].rsplit('/', 1)[-1]

    out += "{}\tP734\t{}\n".format(item, familyname)

    all_items.append(item)

f = open('temp-qs.txt', 'w')
f.write(out)
f.close()

f = open('temp-ps.txt', 'w')
f.write(('\n').join(all_items))
f.close()

qs_url = "https://tools.wmflabs.org/wikidata-todo/quick_statements.php"
ps_url = "https://petscan.wmflabs.org/#tab_other_sources"
print("\n=============")
print("Operation complete!")
print("- Please paste the content of temp-qs.txt to {}".format(qs_url))
ps_txt = "- Please paste the content of temp-ps.txt to {} ".format(ps_url)
ps_txt += "and run the command '-P31:Q4167410'"
print(ps_txt)
