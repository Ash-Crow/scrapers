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
SELECT DISTINCT ?item ?labelFR ?labelEN ?labelDE WHERE {{
       ?item wdt:P31 wd:Q5 .
    ?item wdt:P27 wd:Q142 .

    ?item rdfs:label ?labelFR filter (lang(?labelFR) = "fr") .
    ?item rdfs:label ?labelEN filter (lang(?labelEN) = "en") .
    ?item rdfs:label ?labelDE filter (lang(?labelDE) = "de") .

    FILTER NOT EXISTS {{ ?item rdfs:label ?itemLabelBR filter (lang(?itemLabelBR) = "br") . }}
}} LIMIT 1000""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()


for result in results["results"]["bindings"]:
    item = result['item']['value'].rsplit('/', 1)[-1]

    labelFR = result["labelFR"]['value']
    labelEN = result["labelEN"]['value']
    labelDE = result["labelDE"]['value']

    if labelFR == labelEN == labelDE and '(' not in labelFR:
        for l in all_langs:
            print("\t".join((item, 'L' + l, labelFR)))
