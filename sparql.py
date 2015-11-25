from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
sparql.setQuery("""
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?l WHERE {
  wd:Q18615489 rdfs:label ?l .
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

langs = []
for result in results["results"]["bindings"]:
    langs.append(result["l"]["xml:lang"])

print(langs)