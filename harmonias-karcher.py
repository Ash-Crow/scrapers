#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Harmonia's Kärcher
# Fixes surnäme items in ä mässive wäy.

import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from bs4 import BeautifulSoup


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

# endpoint
endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
sparql = SPARQLWrapper(endpoint)

# Main query
rest_base = "https://www.wikidata.org/api/rest_v1/"
rest_request = "page/html/User%3AHarmonia_Amanda%2FNames"

response = requests.get(rest_base + rest_request)

soup = BeautifulSoup(response.text, "lxml")

all_items = soup.p.text.split()

for item in all_items:
    print('\nParsing item {}'.format(item))
    labels, descriptions = getWDcontent(item)
    label = labels['en']

    out += "{}\tAen\t{} (surname)\n".format(item, label)

    # We fix descriptions first to avoid conflicts
    for lang, description in surname_descriptions.items():
        out += "{}\tD{}\t{}\n".format(item, lang, description)

    # Force empty descriptions for languages not in the previous list
    for lang in descriptions:
        if lang not in surname_descriptions.keys():
            out += "{}\tD{}\t\"\"\n".format(item, lang)

    print(labels, descriptions, label)

    for lang in all_langs:
        out += "{}\tL{}\t{}\n".format(item, lang, label)

    out += "\n"

f = open('temp-qs.txt', 'w')
f.write(out)
f.close()

f = open('temp-ps.txt', 'w')
f.write(('\n').join(all_items))
f.close()

qs_url = "https://tools.wmflabs.org/wikidata-todo/quick_statements.php"
ps_url = "https://petscan.wmflabs.org/#tab_other_sources"

print("\n=============")
print("Operation complete! {} items parsed.".format(len(all_items)))

print("- Please paste the content of temp-qs.txt to {}".format(qs_url))
ps_txt = "- Please paste the content of temp-ps.txt to {} ".format(ps_url)
ps_txt += "and run the command '-P31:Q4167410'"
print(ps_txt)

print("Note: during the execution of the script,")
print(" labels were found in the following languages:")
print(', '.join(all_labels_languages))
