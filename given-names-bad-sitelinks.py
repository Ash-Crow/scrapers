from SPARQLWrapper import SPARQLWrapper, JSON
from urllib import parse

limit = 500000

endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"

sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
SELECT ?item ?itemLabel ?article WHERE {
  ?item wdt:P31 ?type .
  VALUES ?type {
    wd:Q202444
    wd:Q11879590
    wd:Q18220911
    wd:Q3409032
  } .
  ?article schema:about ?item .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

counter = 0

for result in results["results"]["bindings"]:
    item = result['item']['value'].rsplit('/', 1)[-1]
    label = result['itemLabel']['value']
    sitelink = result['article']['value']
    title = parse.unquote(sitelink).split('/')[-1].split(' (')[0]
    lang = parse.unquote(sitelink).split('/')[2].split('.')[0]
    project = parse.unquote(sitelink).split('/')[2].split('.')[1]
    if project == 'wikipedia' and label != title:
        print("* {{{{Q|{}}}}} - ({}) [{} {}]".format(
            item,
            lang,
            sitelink,
            title))
        counter += 1

    if counter >= limit:
        break
