from qwikidata.sparql  import return_sparql_query_results

WIKIDATA_ENDPOINT = 'https://query.wikidata.org/sparql'

WD = 'wd:Q13371'

def do_wikidata_query_aff(id=WD):
    query = (
        'SELECT ?label ?wikidata ?article '
        '(SAMPLE(?cityLabel) as ?sCity) (SAMPLE(?headqLabel) as ?sHeadqCity) '
        '(SAMPLE(?countryLabel) as ?sCountryLabel) (SAMPLE(?coord) as ?sCoord) '
        '(SAMPLE(?countryCoord) as ?sCountryCoord) (SAMPLE(?cityCoord) as ?sCityCoord) '
        '(SAMPLE(?headqCoord) as ?sHeadqCoord) '
        'WHERE { '
        '?wikidata rdfs:label ?label . '
        'OPTIONAL{ '
        '?article schema:about ?wikidata . '
        'FILTER regex(str(?article), "https://en.wikipedia.org/wiki/") } '
        'OPTIONAL{ '
        '?wikidata wdt:P625 ?coord . } '
        'OPTIONAL{ '
        '?wikidata wdt:P131 ?city . '
        '?city rdfs:label ?cityLabel .'
        '?city wdt:P625 ?cityCoord . '
        'FILTER (lang(?cityLabel) = "en") } '
        'OPTIONAL{ '
        '?wikidata wdt:P17 ?country . '
        '?country rdfs:label ?countryLabel . '
        '?country wdt:P625 ?countryCoord . '
        'FILTER (lang(?countryLabel) = "en") } '
        'OPTIONAL{ '
        '?wikidata wdt:P159 ?headq . '
        '?headq rdfs:label ?headqLabel . '
        '?headq wdt:P625 ?headqCoord . '
        'FILTER (lang(?headqLabel) = "en") } '
        'VALUES ?wikidata {%s} '
        'FILTER (lang(?label) = "en") } '
        'GROUP BY ?wikidata ?label ?article '
    ) % WD
    res = return_sparql_query_results(query)
    return res['results']['bindings']


if __name__ == "__main__":
    try:
        print(do_wikidata_query_aff(sys.argv[1]))

    except:
        print(do_wikidata_query_aff())
