import requests
from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_wikidata_info(tag):
    """Fetches the Wikidata Q-number for a given tag."""
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?item ?itemLabel
    WHERE {{
        ?item rdfs:label "{tag}"@en.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        if not results["results"]["bindings"]:
            print("No results found for the given tag.")
            return None, tag
        item_uri = results["results"]["bindings"][0]["item"]["value"]
        q_number = item_uri.split("/")[-1]
        return q_number, tag
    except Exception as e:
        print(f"Error fetching Wikidata info: {e}")
        return None, tag

import requests

def fetch_wikidata_tags(query):
    print('fetch_wikidata_tags çağrıldı')
    """Fetches possible matching tags from Wikidata."""
    url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={query}&language=en&format=json"
    headers = {
        'User-Agent': 'MyApp/1.0 (mailto:mertunlu10@gmail.com)'  # Add a real email
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching tags: HTTP {response.status_code}")
        return []
    
    data = response.json()
    if not data.get("search"):
        print("No matching tags found for the query.")
        return []
    
    results = [
        [f"https://www.wikidata.org/wiki/{entity['id']}", entity["label"]]
        for entity in data.get("search", [])
    ]
    print("Fetched Results:", results)
    return results


