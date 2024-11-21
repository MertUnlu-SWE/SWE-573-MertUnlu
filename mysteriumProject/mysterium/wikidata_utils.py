import requests
from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_wikidata_info(tag):
    try:
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

        results = sparql.query().convert()
        if not results["results"]["bindings"]:
            return None, tag
        item_uri = results["results"]["bindings"][0]["item"]["value"]
        q_number = item_uri.split("/")[-1]
        return q_number, tag
    except Exception as e:
        raise Exception(f"Error fetching Wikidata info for '{tag}': {str(e)}")

def fetch_wikidata_tags(query):
    try:
        url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={query}&language=en&format=json"
        headers = {'User-Agent': 'MyApp/1.0 (mailto:mertunlu10@gmail.com)'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses

        data = response.json()
        if not data.get("search"):
            return []

        return [[f"https://www.wikidata.org/wiki/{entity['id']}", entity["label"]]
                for entity in data.get("search", [])]
    except requests.RequestException as e:
        raise Exception(f"Network error while fetching tags: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error fetching tags: {str(e)}")
