#!/usr/bin/env python3

import requests
from SPARQLWrapper import SPARQLWrapper, JSON


endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparqlba"

sparql = SPARQLWrapper(endpoint)
sparql.setQuery("""
SELECT DISTINCT ?floss ?label ?repo WHERE {
  {
   ?floss p:P31/ps:P31/wdt:P279* wd:Q506883.
  } Union {
   ?floss p:P31/ps:P31/wdt:P279* wd:Q341.
  } Union {
   ?floss p:P31/ps:P31/wdt:P279* wd:Q1130645.
  } Union {
   ?floss p:P31/ps:P31/wdt:P279* wd:Q19652.
   ?floss p:P31/ps:P31/wdt:P279* wd:Q7397.
  }
  ?floss wdt:P1324 ?repo .

  FILTER NOT EXISTS { ?floss p:P275 ?license }
  OPTIONAL { ?floss rdfs:label ?label filter (lang(?label) = "en") .}
 }
""")  # Link to query: http://tinyurl.com/h83bqbr

sparql.setReturnFormat(JSON)

results = sparql.query().convert()

count = 0

for result in results["results"]["bindings"]:
    entity = result['floss']['value']
    qid = entity.rsplit('/', 1)[-1]

    if 'label' in result:
        label = result['label']['value']
    else:
        label = ""

    repo = result['repo']['value']
    protocol = repo.split('://')[0]

    if protocol in ['http', 'https']:
        if 'github' in repo:
            if repo[-1] == '/':
                repo = repo[:-1]

            if repo.endswith('.git'):
                repo = repo[:-4]

            license = repo + "/blob/master/LICENSE"
            response = requests.get(license)

            if response.status_code == 200:
                print("* [[{}]], {} {}".format(qid, repo, license))
                count += 1

print(count)
