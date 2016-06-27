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

for i in range(1, 1698):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery("""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT DISTINCT ?episode ?title WHERE {{
      ?episode wdt:P31 wd:Q838795 .
      ?episode wdt:P361 wd:Q13915 .
      ?episode wdt:P433 '{}' .
      ?episode rdfs:label ?title .
    }}""".format(i))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    used_langs = []
    for result in results["results"]["bindings"]:
        episode = result['episode']['value'].rsplit('/', 1)[-1]
        lang = result["title"]["xml:lang"]
        title = result["title"]['value']
        used_langs.append(lang)

    missing_langs = set(all_langs) - set(used_langs)

    for m in missing_langs:
        print("\t".join((episode, 'L' + m, title)))
