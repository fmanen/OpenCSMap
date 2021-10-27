from django.shortcuts import render, redirect

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from .utils import (
    create_advanced_query_body,
    create_simple_query_body,
    create_advanced_query_papers_body,
    simple_search_papers_results_body,
    create_all_research_query_body,
    simple_search_papers_all_results_body
)
from .models import Search as SearchModel


def advanced_search(request):
    years = range(1900, 2021)
    return render(request, 'advanced_search.html', {'years': years})


def search_index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def all_research(request):
    n_affiliations = 0
    n_papers = 0
    client = Elasticsearch()
    body = create_all_research_query_body()
    s = Search(using=client, index='papers').update_from_dict(body)

    t = s.execute()
    aggs = t.aggregations.my_buckets.buckets
    affiliations = [aggs]

    for aff in aggs:
        n_papers += aff.doc_count
    n_affiliations += len(aggs)

    after = t.aggregations.my_buckets.after_key
    while True:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index='papers').update_from_dict(body)
        t = s.execute()

        aggs = t.aggregations.my_buckets.buckets
        for aff in aggs:
            n_papers += aff.doc_count
        affiliations.append(aggs)
        n_affiliations += len(aggs)

        try:
            after = t.aggregations.my_buckets.after_key

        except:
            break

    return render(
        request,
        'results.html',
        {
            'affiliations': affiliations,
            'all': True,
            'n_affiliations': format(n_affiliations, ',d'),
            'n_papers': format(n_papers, ',d')
        }
    )


def simple_aggregations_search_view_get(request, topic):
    n_affiliations = 0
    n_papers = 0
    client = Elasticsearch()
    body = create_simple_query_body(topic)
    s = Search(using=client, index='papers').update_from_dict(body)

    t = s.execute()
    aggs = t.aggregations.my_buckets.buckets
    affiliations = [aggs]

    for aff in aggs:
        n_papers += aff.doc_count
    n_affiliations += len(aggs)

    try:
        after = t.aggregations.my_buckets.after_key

    except:
        after = ""

    while after:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index='papers').update_from_dict(body)
        t = s.execute()

        aggs = t.aggregations.my_buckets.buckets
        affiliations.append(aggs)
        for aff in aggs:
            n_papers += aff.doc_count
        n_affiliations += len(aggs)

        try:
            after = t.aggregations.my_buckets.after_key
        except:
            break

    search = SearchModel.objects.create(
                topic=topic
            )

    search.save()

    return render(
        request,
        'results.html',
        {
            'affiliations': affiliations,
            'topic': topic,
            'n_affiliations': format(n_affiliations, ',d'),
            'n_papers': format(n_papers, ',d')
        }
    )


def simple_aggregations_search_view(request):
    if request.POST:
        topic = request.POST.get('topic')

    else:
        return redirect('search:search')

    if not topic:
        return redirect('search:search')

    n_affiliations = 0
    n_papers = 0
    client = Elasticsearch()
    body = create_simple_query_body(topic)
    s = Search(using=client, index='papers').update_from_dict(body)

    t = s.execute()
    aggs = t.aggregations.my_buckets.buckets
    affiliations = [aggs]

    for aff in aggs:
        n_papers += aff.doc_count
    n_affiliations += len(aggs)

    try:
        after = t.aggregations.my_buckets.after_key

    except:
        after = ""

    while after:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index='papers').update_from_dict(body)
        t = s.execute()

        aggs = t.aggregations.my_buckets.buckets
        affiliations.append(aggs)
        for aff in aggs:
            n_papers += aff.doc_count
        n_affiliations += len(aggs)

        try:
            after = t.aggregations.my_buckets.after_key
        except:
            break

    search = SearchModel.objects.create(
        topic=topic
    )

    search.save()

    return render(
        request,
        'results.html',
        {
            'affiliations': affiliations,
            'topic': topic,
            'n_affiliations': format(n_affiliations, ',d'),
            'n_papers': format(n_papers, ',d')
        }
    )


def aggregations_for_advanced_search_view(request):
    if request.POST:
        topic = request.POST.get('topic')
        authors = request.POST.get('authors')
        results_by = request.POST.get('results-by')
        type_of_pub = request.POST.get('type-of-pub')
        from_date = int(request.POST.get('from-date'))
        to_date = int(request.POST.get('to-date'))

    else:
        return redirect('search:advanced_search')

    n_affiliations = 0
    n_papers = 0
    body = create_advanced_query_body(
        topic,
        authors,
        results_by,
        type_of_pub,
        from_date,
        to_date
    )

    print(body)
    client = Elasticsearch()

    s = Search(using=client, index="papers").update_from_dict(body)

    t = s.execute()

    aggs = t.aggregations.my_buckets.buckets
    affiliations = [aggs]

    for aff in aggs:
        n_papers += aff.doc_count
    n_affiliations += len(aggs)

    try:
        after = t.aggregations.my_buckets.after_key
    except:
        after = ""

    while after:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index='papers').update_from_dict(body)
        t = s.execute()

        aggs = t.aggregations.my_buckets.buckets
        affiliations.append(aggs)
        for aff in aggs:
            n_papers += aff.doc_count
        n_affiliations += len(aggs)

        try:
            after = t.aggregations.my_buckets.after_key

        except:
            break

    search = SearchModel.objects.create(
        topic=topic,
        author=authors,
        results_by=results_by,
        type_of_pub=type_of_pub,
        from_date=from_date,
        to_date=to_date
    )

    search.save()

    return render(request, 'advanced_search_results.html', {
            'affiliations': affiliations,
            'topic': topic,
            'results_by': results_by,
            'authors': authors if authors else None,
            'type_of_pub': type_of_pub,
            'to_date': to_date,
            'from_date': from_date,
            'n_affiliations': format(n_affiliations, ',d'),
            'n_papers': format(n_papers, ',d')
        }
    )


def aggregations_for_advanced_search_view_get(
    request,
    topic,
    type_of_pub,
    results_by,
    from_date,
    to_date
):
    authors = ''

    n_affiliations = 0
    n_papers = 0
    body = create_advanced_query_body(
        topic,
        authors,
        results_by,
        type_of_pub,
        from_date,
        to_date
    )
    body = eval(body)

    client = Elasticsearch()

    s = Search(using=client, index='papers').update_from_dict(body)

    t = s.execute()

    aggs = t.aggregations.my_buckets.buckets
    affiliations = [aggs]

    for aff in aggs:
        n_papers += aff.doc_count
    n_affiliations += len(aggs)

    try:
        after = t.aggregations.my_buckets.after_key

    except:
        after = ''

    while after:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index='papers').update_from_dict(body)
        t = s.execute()

        aggs = t.aggregations.my_buckets.buckets
        affiliations.append(aggs)
        for aff in aggs:
            n_papers += aff.doc_count
        n_affiliations += len(aggs)

        try:
            after = t.aggregations.my_buckets.after_key

        except:
            break

    search = SearchModel.objects.create(
        topic=topic,
        author=authors,
        results_by=results_by,
        type_of_pub=type_of_pub,
        from_date=from_date,
        to_date=to_date
    )

    search.save()

    return render(request, 'advanced_search_results.html', {
        'affiliations': affiliations,
        'topic': topic,
        'results_by': results_by,
        'authors': authors if authors else None,
        'type_of_pub': type_of_pub,
        'to_date': to_date,
        'from_date': from_date,
        'n_affiliations': format(n_affiliations, ',d'),
        'n_papers': format(n_papers, ',d')
        }
    )


def simple_search_papers_results_view(request, topic, affiliation):
    client = Elasticsearch()
    body = simple_search_papers_results_body(topic, affiliation)
    s = Search(using=client, index='papers').update_from_dict(body)

    t = s.execute()

    all_hits = t.hits.hits
    results = []
    for hit in all_hits:
        results.append(hit['_source'])

    top_author = t.aggregations.Authors.buckets[0].key

    # TODO: top_author can be more than one

    return render(request, 'papers_results.html', {
            'results': results,
            'affiliation': affiliation,
            'topic': topic,
            'results_by': 'affiliation',
            'top_author': top_author,
            'number_of_hits': len(all_hits)
        }
    )


def simple_search_papers_all_results_view(request, affiliation):
    client = Elasticsearch()
    body = simple_search_papers_all_results_body(affiliation)
    s = Search(using=client, index='papers').update_from_dict(body)

    t = s.execute()

    all_hits = t.hits.hits
    results = []
    for hit in all_hits:
        results.append(hit["_source"])

    top_author = t.aggregations.Authors.buckets[0].key

    return render(request, 'papers_results.html', {
        'results': results,
        'affiliation': affiliation,
        'results_by': 'affiliation',
        'top_author': top_author,
        'number_of_hits': len(all_hits)
        }
    )


def advanced_search_papers_results_view(
    request,
    topic,
    authors,
    affiliation,
    results_by,
    type_of_pub,
    from_date,
    to_date
):
    client = Elasticsearch()
    authors_val = '' if authors == 'None' else authors
    body = create_advanced_query_papers_body(
        topic,
        authors_val,
        results_by,
        type_of_pub,
        affiliation,
        None,
        from_date,
        to_date
    )
    s = Search(using=client, index='papers').update_from_dict(body)
    print(type(body))
    t = s.execute()

    all_hits = t.hits.hits
    results = []
    for hit in all_hits:
        results.append(hit["_source"])
    top_author = t.aggregations.Authors.buckets[0].key
    return render(request, 'papers_results.html', {
        'results': results,
        'results_by': results_by,
        'type_of_pub': type_of_pub,
        'affiliation': affiliation,
        'topic': topic,
        'authors': authors_val,
        'top_author': top_author,
        'number_of_hits': len(all_hits),
        'from_date': from_date,
        'to_date': to_date
        }
    )


def advanced_search_papers_results_city_view(
    request,
    topic,
    authors,
    affiliation,
    results_by,
    type_of_pub,
    city,
    from_date,
    to_date
):
    client = Elasticsearch()
    authors_val = '' if authors == 'None' else authors
    body = create_advanced_query_papers_body(
        topic,
        authors_val,
        results_by,
        type_of_pub,
        affiliation,
        city,
        from_date,
        to_date
    )
    s = Search(using=client, index='papers').update_from_dict(body)
    t = s.execute()

    all_hits = t.hits.hits
    results = []
    for hit in all_hits:
        results.append(hit['_source'])

    top_author = t.aggregations.Authors.buckets[0].key
    return render(request, 'papers_results.html', {
            'results': results,
            'results_by': results_by,
            'type_of_pub': type_of_pub,
            'affiliation': affiliation,
            'topic': topic,
            'authors': authors_val,
            'city': city,
            'top_author': top_author,
            'number_of_hits': len(all_hits),
            'from_date': from_date,
            'to_date': to_date
        }
    )