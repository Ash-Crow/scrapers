from SPARQLWrapper import SPARQLWrapper, JSON
import argparse


parser = argparse.ArgumentParser(
    description='Fixes labels for French communes.')
parser.add_argument("departement", help="The number of a departement")
args = parser.parse_args()
if args.departement.isdigit():
    dept = '"{}"'.format(args.departement)
    f = open('temp-lastdept.txt', 'w')
    f.write(dept)
    f.close()

else:
    dept = "?dept"

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
SELECT DISTINCT ?item ?label WHERE {{
  ?item wdt:P31/wdt:P279* wd:Q484170 .
  ?item wdt:P131 ?dept .
  ?dept wdt:P2586 ?deptnum .
  FILTER(STRSTARTS(?deptnum, {})) .
  ?item rdfs:label ?label .
}}""".format(dept))
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

out = ""
label_counter = 0
item_counter = 0

used_langs = {}
labels = {}
for result in results["results"]["bindings"]:
    item = result['item']['value'].rsplit('/', 1)[-1]
    if item not in used_langs:
        used_langs[item] = []
    lang = result["label"]["xml:lang"]
    label = result["label"]['value']
    if lang == 'fr':
        labels[item] = label
    used_langs[item].append(lang)

for item, values in used_langs.items():
    missing_langs = set(all_langs) - set(values)
    missing_langs = sorted(missing_langs)

    modified_item_counter = 0
    for m in missing_langs:
        label = labels[item]
        out += "{}\tL{}\t{}\n".format(item, m, label)
        label_counter += 1
        modified_item_counter += 1

    if modified_item_counter:
        out += "\n"
        item_counter += 1

f = open('temp.txt', 'w')
f.write(out)
f.close()

qs_url = "https://tools.wmflabs.org/wikidata-todo/quick_statements.php"

print("Operation complete! {} labels added on {}/{} items.".format(
    label_counter,
    item_counter,
    len(used_langs)))
print("- Please paste the content of temp.txt to {}".format(qs_url))
