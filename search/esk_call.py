from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A
from collections import defaultdict

def simple_search(topic=""):
    client = Elasticsearch()
    q = Q(
            "match", title__english=topic
        )
    s = Search(using=client, index="papers").query(q)[0:20]
    response = s.execute()
    search = get_results(response)
    return search

def get_results(response):
    results = defaultdict(dict)
    nf = 0
    for hit in response:
        try:
            if not 'papers' in results[hit.affiliation_name]:
                results[hit.affiliation_name]['papers'] = [{'title':hit.title, 'authors':hit.authors}]
            else:
                results[hit.affiliation_name]['papers'].append({'title':hit.title, 'authors':hit.authors})
            results[hit.affiliation_name]['coord'] = hit.coord
        except:
            nf += 1
            continue

    print(len(results))
    print(nf)
    return dict(results)

def aggregations():
    """
    body = {
        "size":0,
        "aggs": {
            "my_buckets": {
                "composite": {
                    "sources": [
                        {
                            "Country": {
                                "terms": {
                                    "field": "country.normalized"
                                }
                            },
                            "City": {
                                "terms": {
                                    "field": "city.normalized"
                                }
                            }
                        }
                    ]
                }
            }
        }
    }"""

    
    body =   \
    {
        "size":0,
        "query": {
            "bool": {
            "must": [
                {"match":{ "title": {"query":"semantic web", "operator": "and"}}}
            ]
            }
        },
        "aggs": {
            "my_buckets": {
            "composite": {
                "size":1000,
                "sources": [
                {
                    "Country": {
                    "terms": {
                        "field": "affiliation_name.raw"
                    }
                    }
                },
                {
                    "Lat": {
                    "terms": {
                        "field": "affLat"
                    }
                    }
                },
                {
                    "Long": {
                    "terms": {
                        "field": "affLong"
                    }
                    }
                }
            ]
            }
            }
        }
        }
    client = Elasticsearch()
    s = Search(using=client, index="papers_def").update_from_dict(body)

    t = s.execute()

    results = t.aggregations.my_buckets.buckets

    after = t.aggregations.my_buckets.after_key

    while after:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index="papers_def").update_from_dict(body)
        t = s.execute()
        for item in t.aggregations.my_buckets.buckets:
            print(item.key['Country'], item.key['Lat'], item.doc_count)

        try:
            after = t.aggregations.my_buckets.after_key
        except:
            break

def create_advanced_query_body(topic, authors, results_by, type_of_pub, from_date, to_date):

    
    must_topic = """"must": [{"match":{ "title": {"query":"%s", "operator": "and"}}}],""" % (topic)

    if not authors:
        should_author = ""
    elif type_of_pub in ['inproceedings', 'article'] or from_date or to_date:
        should_author = """ "should": [{"match":{ "authors": {"query":"%s", "operator": "and"}}}],"minimum_should_match": 1, """ % (authors)
    else:
        should_author = """ "should": [{"match":{ "authors": {"query":"%s", "operator": "and"}}}],"minimum_should_match": 1 """ % (authors)


    if not type_of_pub in ['inproceedings', 'article']:
        term_filter = ""
    elif from_date or to_date:
        term_filter = """{ "term":  { "type": "%s" }},""" % (type_of_pub)
    else:
        term_filter = """{ "term":  { "type": "%s" }}""" % (type_of_pub)

    if from_date and to_date:
        range_filter = """{ "range": { "year": { "gte": %s, "lte":%s }}}""" % (from_date, to_date)
    elif from_date and not to_date:
        range_filter = """{ "range": { "year": { "gte": %s }}}""" % (from_date)
    elif not from_date and to_date:
        range_filter = """{ "range": { "year": { lte":%s }}}""" % (to_date)
    else:
        range_filter = ""

    place_agg = """ {"Country": {"terms": {"field": "country.raw"}} },"""

    if results_by == 'country':
        lat = """{"Lat": {"terms": {"field": "countryLat"}}},"""
        long = """{"Long": {"terms": {"field": "countryLong"}}}"""
    elif results_by == 'city':
        place_agg += """{"City": {"terms": {"field": "city.raw"}} },"""
        lat = """{"Lat": {"terms": {"field": "cityLat"}}},"""
        long = """{"Long": {"terms": {"field": "cityLong"}}}"""
    else:
        place_agg += """{"City": {"terms": {"field": "city.raw"}} },"""
        place_agg += """{"Affiliation": {"terms": {"field": "affiliation_name.raw"}} },"""
        lat = """{"Lat": {"terms": {"field": "affLat"}}},"""
        long = """{"Long": {"terms": {"field": "affLong"}}}"""

    filter
    query_part = """"query": {"bool": {%s%s"filter": [%s%s]}},""" % (must_topic, should_author, term_filter, range_filter)
    aggs_part = """"aggs": {"my_buckets": {"composite": {"size":1000,"sources": [%s%s%s]}}}""" % (place_agg, lat, long)

    body = """{"size":0,%s%s}""" % (query_part, aggs_part)

    return body


if __name__ == '__main__':
    print("Query hits:\n", (dict(create_advanced_query_body("semantic web", "", "","", "", ""))))