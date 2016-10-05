#!/usr/bin/env python3
import pprint
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"

sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
SELECT DISTINCT
?item
?itemLabel
?familynameLabel
?familyname
WHERE {
  {
    SELECT DISTINCT
    ?item
    (SAMPLE(?familyname) AS ?familyname)
    WHERE {
      ?item wdt:P734 ?allnames, ?name .

      ?name wdt:P31 wd:Q4167410 ;
            wdt:P1889 ?familyname .

      ?familyname wdt:P31 wd:Q101352 .

      FILTER(?familyname NOT IN (
        wd:Q21488047,
        wd:Q21502319,
        wd:Q21488251,
        wd:Q21488880,
        wd:Q21507956,
        wd:Q21494599
      ))
    } GROUP BY ?item
      HAVING (COUNT(?allnames) = 1 && COUNT(?familyname) = 1)
      ORDER BY ?item_label
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en,es,pl,it" }
} ORDER BY ?familynameLabel
""")  # Link to query: <>

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
ps_txt += "and run the command '-P734'"
print(ps_txt)
