import json
from SPARQLWrapper import SPARQLWrapper, JSON


def getWDcontent(item):
    print(item)
    sparql.setQuery("""
    SELECT DISTINCT ?lang ?label ?description WHERE {{
      {{
        SELECT ?lang ?label WHERE {{
          wd:{0} rdfs:label ?label .
          BIND(LANG(?label) AS ?lang) .
        }}
      }} UNION {{
          SELECT ?lang ?description WHERE {{
            wd:{0} schema:description ?description .
            BIND(LANG(?description) AS ?lang) .
          }}
      }}
    }} ORDER BY ?lang
    """.format(item))

    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    results = results["results"]["bindings"][0]
    print(results)
    for k, v in results.items():
        print(k, v)

    return "a", "b"

# Global variables

all_labels_languages = []

# Languages and descriptions

with open("resources/surname.json") as file:
    surname_descriptions = json.load(file)
    file.close()

out = ""

all_langs = ['af', 'an', 'ast', 'bar', 'bm', 'br', 'ca', 'co', 'cs', 'cy',
             'da', 'de', 'de-at', 'de-ch', 'en', 'en-ca', 'en-gb', 'eo', 'es',
             'et', 'eu', 'fi', 'fr', 'frc', 'frp', 'fur', 'ga', 'gd', 'gl',
             'gsw', 'hr', 'hu', 'ia', 'id', 'ie', 'io', 'it', 'jam', 'kab',
             'kg', 'lb', 'li', 'lij', 'lt', 'lv', 'mg', 'min', 'ms', 'nap',
             'nb', 'nds', 'nds-nl', 'nl', 'nn', 'nrm', 'oc', 'pap', 'pcd',
             'pl', 'pms', 'prg', 'pt', 'pt-br', 'rgn', 'rm', 'ro', 'sc', 'scn',
             'sco', 'sk', 'sr-el', 'sv', 'sw', 'tr', 'vec', 'vi', 'vls', 'vmf',
             'vo', 'wa', 'wo', 'zu', 'fo', 'is', 'kl']

endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"

sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
SELECT DISTINCT ?person ?label WHERE {{
  ?person wdt:P31 wd:Q101352 ;
          wdt:P31 wd:Q4167410 ;
          wdt:P31 ?type ;
          rdfs:label ?label .
  ?sitelink schema:about ?person .
  ?article schema:about ?person ;
           schema:inLanguage "en" ;
           schema:isPartOf <https://en.wikipedia.org/> .
  FILTER(LANG(?label) IN ("en")) .
  FILTER(CONTAINS(?label, "(")) .
  }}
  GROUP BY ?person ?label
  HAVING ((COUNT(DISTINCT ?type) = 2) && (COUNT(DISTINCT ?sitelink) = 1))
""")

sparql.setReturnFormat(JSON)

results = sparql.query().convert()

for result in results["results"]["bindings"]:
    item = result['person']['value'].rsplit('/', 1)[-1]

    if item:labels, descriptions = getWDcontent(item)

    label = result['label']['value'].rsplit(' (', 1)[0]

    out += "{}\tAen\t{} (surname)\n".format(item, label)

    for lang in all_langs:
        out += "{}\tL{}\t{}\n".format(item, lang, label)

    for lang, description in surname_descriptions.items():
        out += "{}\tD{}\t{}\n".format(item, lang, description)

    out += "\n"

# print(out)
"""
    item = result['item']['value'].rsplit('/', 1)[-1]

    labelFR = result["labelFR"]['value']
    labelEN = result["labelEN"]['value']
    labelDE = result["labelDE"]['value']

    if labelFR == labelEN == labelDE and '(' not in labelFR:
        for l in all_langs:
            print("\t".join((item, 'L' + l, labelFR)))
"""

f = open('temp.txt', 'w')
f.write(out)
f.close()
