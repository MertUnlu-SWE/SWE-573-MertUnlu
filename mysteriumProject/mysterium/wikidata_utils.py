from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_wikidata_info(tag):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?item ?itemLabel
    WHERE {{
        ?item ?label "{tag}"@en.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        return result["item"]["value"], result["itemLabel"]["value"]
    return None, None
