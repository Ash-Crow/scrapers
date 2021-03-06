from SPARQLWrapper import SPARQLWrapper, JSON


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
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT DISTINCT ?item ?label WHERE {{
    ?item wdt:P31 wd:Q202444, wd:Q19803443 .
  ?item rdfs:label ?label .
}}""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

used_langs = {}
labels = {}
for result in results["results"]["bindings"]:
    item = result['item']['value'].rsplit('/', 1)[-1]
    if item not in used_langs:
        used_langs[item] = []
    lang = result["label"]["xml:lang"]
    label = result["label"]['value']
    if lang == 'en':
        labels[item] = label
    used_langs[item].append(lang)

for item, values in used_langs.items():
    missing_langs = set(all_langs) - set(values)

    for m in missing_langs:
        label = labels[item]
        print("\t".join((item, 'L' + m, label)))
