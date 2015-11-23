from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
sparql.setQuery("""
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?episode ?episodeLabel ?number ?date WHERE {
  ?episode wdt:P31 wd:Q838795 .
  ?episode wdt:P361 wd:Q13915 .
  ?episode wdt:P433 ?number .
  ?episode wdt:P577 ?date

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
 } ORDER BY xsd:integer(?number)
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(result["episode"]["value"], result["episodeLabel"]["value"])

