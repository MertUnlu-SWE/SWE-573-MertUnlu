from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_wikidata_info(tags):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    tag = tags[0]
    query = f"""
    SELECT ?item ?itemLabel
    WHERE {{
        ?item rdfs:label "{tag}"@en.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            item_uri = result["item"]["value"]
            if "Q" in item_uri:
                q_number = item_uri.split("/")[-1]
                return q_number, tag
        return None, tag
    except Exception as e:
        print(f"Error fetching Wikidata info: {e}")
        return None, tag
