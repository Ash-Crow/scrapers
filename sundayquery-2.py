#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from SPARQLWrapper import SPARQLWrapper, JSON


def getWDcontent(item):
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
    """.format(item))  # Sample query: http://tinyurl.com/hj4z2hu

    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    results = results["results"]["bindings"]

    label_langs = {}
    descriptions = []

    for res in results:
        for k, v in res.items():
            if k == "label":
                lang = v['xml:lang']
                if lang not in label_langs:
                    label = v['value']
                    label_langs[lang] = label

                if lang not in all_labels_languages:
                    all_labels_languages.append(lang)
            elif k == "description":
                lang = v['xml:lang']
                descriptions.append(lang)

    print('  - Labels found in {} language(s)'.format(len(label_langs)))
    print('  - Descriptions found in {} language(s)'.format(len(descriptions)))
    return label_langs, descriptions

# Global variables
all_labels_languages = []
all_items = []

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

# Main SPARQL query
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
  FILTER(CONTAINS(?label, "(surname)")) .
  }}
  GROUP BY ?person ?label
  HAVING ((COUNT(DISTINCT ?type) = 2) && (COUNT(DISTINCT ?sitelink) = 1))
""")  # Link to query: http://tinyurl.com/hju3gpt

sparql.setReturnFormat(JSON)

results = sparql.query().convert()

for result in results["results"]["bindings"]:
    item = result['person']['value'].rsplit('/', 1)[-1]
    label = result['label']['value'].rsplit(' (', 1)[0]
    print('\nParsing item {} ({})'.format(item, label))

    labels, descriptions = getWDcontent(item)

    out += "{}\tAen\t{} (surname)\n".format(item, label)

    # We fix descriptions first to avoid conflicts
    for lang, description in surname_descriptions.items():
        out += "{}\tD{}\t{}\n".format(item, lang, description)

    # Force empty descriptions for languages not in the previous list
    for lang in descriptions:
        if lang not in surname_descriptions.keys():
            out += "{}\tD{}\t\"\"\n".format(item, lang)

    for lang in all_langs:
        out += "{}\tL{}\t{}\n".format(item, lang, label)

    out += "\n"

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
