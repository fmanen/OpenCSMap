from django.shortcuts import render, redirect

from django.http import HttpResponse


from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A
from collections import defaultdict

from .forms import AdvancedSearchForm
from .utils import create_advanced_query_body, create_simple_query_body, create_advanced_query_papers_body, simple_search_papers_results_body

def simple_search(topic="", results_by=0):
    client = Elasticsearch()
    q = Q(
            "match", title__english=topic
        )
    s = Search(using=client, index="papers_def").query(q)[0:10000]
    response = s.execute()
    search = get_results(response, results_by)
    return search

def advanced_search(request):
    form = AdvancedSearchForm()
    years = range(1900,2021)
    return render(request, 'advanced_search.html', {'form':form, 'years':years})

def get_results(response, results_by):
    results = defaultdict(dict)
    for hit in response:
        try:
            if results_by == 0:
                coord = hit.coord
                name = hit.affiliation_name
            elif results_by == 1:
                coord = hit.cityCoord
                name = hit.city
            else:
                coord = hit.countryCoord
                name = hit.country
            if not coord:
                continue
            results[name]['coord'] = coord
            if not 'papers' in results[name]:
                results[name]['papers'] = [{'title':hit.title, 'authors':hit.authors}]
            else:
                results[name]['papers'].append({'title':hit.title, 'authors':hit.authors})
        except:
            continue
    return dict(results)

def search_index(request):
    return render(request, 'index.html')

def advanced_results(request):
    if request.POST:
        topic = request.POST.get('topic')
        authors = request.POST.get('authors')
        results_by = int(request.POST.get('results-by'))
        print(results_by)

    aggregations = simple_search(topic, results_by)

    return render(request, 'advanced_search_results.html', {'aggregations':aggregations, 'topic':topic, 'results':results_by})


def results(request):
    if request.POST:
        topic = request.POST.get('topic')

    if not topic:
        return redirect('search:search')

    affiliations = simple_search(topic)
    return render(request, 'results.html', {'affiliations':affiliations, 'topic':topic})


def simple_aggregations_search_view(request):
    if request.POST:
        topic = request.POST.get('topic')

    client = Elasticsearch()
    body = create_simple_query_body(topic)
    s = Search(using=client, index="papers_def").update_from_dict(body)

    t = s.execute()
    affiliations = [t.aggregations.my_buckets.buckets]

    after = t.aggregations.my_buckets.after_key
    while True:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index="papers_def").update_from_dict(body)
        t = s.execute()

        affiliations.append(t.aggregations.my_buckets.buckets)

        try:
            after = t.aggregations.my_buckets.after_key
        except:
            break

    return render(request, 'results.html', {'affiliations':affiliations, 'topic':topic})



def aggregations_for_advanced_search_view(request):
    if request.POST:
        topic = request.POST.get('topic')
        authors = request.POST.get('authors')
        results_by = request.POST.get('results-by')
        type_of_pub = request.POST.get('type-of-pub')
        from_date = int(request.POST.get('from-date'))
        to_date = int(request.POST.get('to-date'))


    body = create_advanced_query_body(topic, authors, results_by, type_of_pub, from_date, to_date)
    body = eval(body)

    client = Elasticsearch()

    s = Search(using=client, index="papers_def").update_from_dict(body)

    t = s.execute()
    affiliations = [t.aggregations.my_buckets.buckets]
    
    try:
        after = t.aggregations.my_buckets.after_key
    except:
        after = ""
    while after:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index="papers_def").update_from_dict(body)
        t = s.execute()

        affiliations.append(t.aggregations.my_buckets.buckets)

        try:
            after = t.aggregations.my_buckets.after_key
        except:
            break

    return render(request, 'advanced_search_results.html', {
        'affiliations':affiliations,
        'topic':topic,
        'results_by':results_by,
        'authors':authors if authors else None,
        'type_of_pub':type_of_pub,
        'to_date':to_date,
        'from_date':from_date
        })



def simple_search_papers_results_view(request, topic, affiliation):
    client = Elasticsearch()
    body = simple_search_papers_results_body(topic,affiliation)
    s = Search(using=client, index="papers_def").update_from_dict(body)

    t = s.execute()

    all_hits = t.hits.hits
    results = []
    for hit in all_hits:
        results.append(hit["_source"])

    top_author = t.aggregations.Authors.buckets[0].key

    return render(request, 'papers_results.html', {
        'results':results,
        'affiliation':affiliation,
        'topic':topic,
        'results_by':"affiliation",
        'top_author':top_author,
        'number_of_hits':len(all_hits)
        })

def advanced_search_papers_results_view(request, topic, authors, affiliation, results_by, type_of_pub, from_date, to_date):
    client = Elasticsearch()
    authors_val = "" if authors == "None" else authors
    body = create_advanced_query_papers_body(topic, authors_val, results_by, type_of_pub, affiliation, None, from_date, to_date)
    s = Search(using=client, index="papers_def").update_from_dict(body)
    print(type(body))
    t = s.execute()

    all_hits = t.hits.hits
    results = []
    for hit in all_hits:
        results.append(hit["_source"])
    top_author = t.aggregations.Authors.buckets[0].key
    return render(request, 'papers_results.html', {
        'results':results,
        'results_by':results_by,
        'type_of_pub':type_of_pub,
        'affiliation':affiliation,
        'topic':topic,
        'authors':authors_val,
        'top_author':top_author,
        'number_of_hits':len(all_hits),
        'from_date':from_date,
        'to_date':to_date
        })

def advanced_search_papers_results_city_view(request, topic, authors, affiliation, results_by, type_of_pub, city, from_date, to_date):
    client = Elasticsearch()
    authors_val = "" if authors == "None" else authors
    body = create_advanced_query_papers_body(topic, authors_val, results_by, type_of_pub, affiliation, city, from_date, to_date)
    print(body)
    s = Search(using=client, index="papers_def").update_from_dict(body)
    t = s.execute()

    all_hits = t.hits.hits
    results = []
    for hit in all_hits:
        results.append(hit["_source"])

    top_author = t.aggregations.Authors.buckets[0].key
    return render(request, 'papers_results.html', {
        'results':results,
        'results_by':results_by,
        'type_of_pub':type_of_pub,
        'affiliation':affiliation,
        'topic':topic,
        'authors':authors_val,
        'city':city,
        'top_author':top_author,
        'number_of_hits':len(all_hits),
        'from_date':from_date,
        'to_date':to_date
        })