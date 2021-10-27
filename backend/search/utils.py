def create_simple_query_body(topic):
    body = {
        'size': 0,
        'query': {
            'bool': {
                'should': [
                    {
                        'match': {
                            'title': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    },
                    {
                        'match': {
                            'proceedingsName': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    },
                    {
                        'match': {
                            'journal': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    }
                ],
                'minimum_should_match': 1
            }
        },
        'aggs': {
            'my_buckets': {
                'composite': {
                    'size': 1000,
                    'sources': [
                        {
                            'Affiliation': {
                                'terms': {
                                    'field': 'affiliation_name.raw'
                                }
                            }
                        },
                        {
                            'Lat': {
                                'terms': {
                                    'field': 'affLat'
                                }
                            }
                        },
                        {
                            'Long': {
                                'terms': {
                                    'field': 'affLong'
                                }
                            }
                        },
                        {
                            'Country': {
                                'terms': {
                                    'field': 'country.raw'
                                }
                            }
                        },
                        {
                            'City': {
                                'terms': {
                                    'field': 'city.raw'
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    return body


def create_advanced_query_body(
    topic,
    authors,
    results_by,
    type_of_pub,
    from_date, to_date
):
    must_topic = {
        'should': [
            {
                'match': {
                    'title': {
                        'query': topic,
                        'operator': 'and'
                    }
                }
            },
            {
                'match': {
                    'proceedingsName': {
                        'query': topic,
                        'operator': 'and'
                    }
                }
            },
            {
                'match': {
                    'journal': {
                        'query': topic,
                        'operator': 'and'
                    }
                }
            }
        ],
        'minimum_should_match': 1,
    }

    if not authors:
        should_author = dict()

    else:
        should_author = {
            'must': [
                {
                    'match': {
                        'authors': {
                            'query': authors,
                            'operator': 'and'
                        }
                    }
                }
            ],
        }

    if type_of_pub not in ['inproceedings', 'article']:
        term_filter = dict()

    elif from_date or to_date:
        term_filter = {
            'term': {
                'type': type_of_pub
            }
        }

    else:
        term_filter = {
            'term': {
                'type': type_of_pub
            }
        }

    if from_date and to_date:
        range_filter = {
            'range': {
                'year': {
                    'gte': from_date,
                    'lte': to_date
                }
            }
        }

    elif from_date and not to_date:
        range_filter = {
            'range': {
                'year': {
                    'gte': from_date
                }
            }
        }

    elif not from_date and to_date:
        range_filter = {
            'range': {
                'year': {
                    'lte': to_date
                }
            }
        }

    else:
        range_filter = dict()

    place_agg = {
        'Country': {
            'terms': {
                'field': 'country.raw'
            }
        }
    }

    if results_by == 'country':
        lat = {
            'Lat': {
                'terms': {
                    'field': 'countryLat'
                }
            }
        }

        long = {
            'Long': {
                'terms': {
                    'field': 'countryLong'
                }
            }
        }

    elif results_by == 'city':
        place_agg = {
            **place_agg,
            **{
                'City': {
                    'terms': {
                        'field': 'city.raw'
                    }
                }
            }
        }

        lat = {
            'Lat': {
                'terms': {
                    'field': 'cityLat'
                }
            }
        }

        long = {
            'Long': {
                'terms': {
                    'field': 'cityLong'
                }
            }
        }

    else:
        place_agg = {
            **place_agg,
            **{
                'City': {
                    'terms': {
                        'field': 'city.raw'
                    }
                }
            },
            **{
                'Affiliation': {
                    'terms': {
                        'field': 'affiliation_name.raw'
                    }
                }
            }
        }
        lat = {
            'Lat': {
                'terms': {
                    'field': 'cityLat'
                }
            }
        }

        long = {
            'Long': {
                'terms': {
                    'field': 'cityLong'
                }
            }
        }

    query_part = {
        'query': {
            'bool': {
                **must_topic,
                **should_author,
                **{
                    'filter':
                        [
                            x for x in [term_filter, range_filter] if x
                        ]
                }
            }
        }
    }
    aggs_part = {
        'aggs': {
            'my_buckets': {
                'composite': {
                    'size': 1000,
                    'sources': [
                        {k: v} for k, v in place_agg.items()
                    ] +
                    [lat, long]
                }
            }
        }
    }

    body = {
        'size': 0,
        'query': query_part['query'],
        'aggs': aggs_part['aggs']
    }

    return body


def simple_search_papers_results_body(topic, affiliation):
    body = {
        'size': 1000,
        'query': {
            'bool': {
                'should': [
                    {
                        'match': {
                            'title': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    },
                    {
                        'match': {
                            'proceedingsName': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    },
                    {
                        'match': {
                            'journal': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    }
                ],
                'minimum_should_match': 1,
                'filter': [
                    {
                        'term':  {
                            'affiliation_name.raw': affiliation
                        }
                    }
                ]
            }
        },
        'aggs': {
            'Authors': {
                'terms': {
                    'field': 'authors.raw'
                }
            }
        },
        '_source': {
            'includes': [
                'title',
                'authors',
                'type',
                'year',
                'journal',
                'proceedingsName',
                'city',
                'country',
                'affiliation_name',
                'doi'
            ]
        }
    }

    return body


def simple_search_papers_all_results_body(affiliation):
    body = {
        'size': 10000,
        'query': {
            'bool': {
                'filter': [
                    {
                        'term':  {
                            'affiliation_name.raw': affiliation
                        }
                    }
                ]
            }
        },
        'aggs': {
            'Authors': {
                'terms': {
                    'field': 'authors.raw'
                }
            }
        },
        '_source': {
            'includes': [
                'title',
                'authors',
                'type',
                'year',
                'journal',
                'proceedingsName',
                'city',
                'country',
                'affiliation_name',
                'doi'
            ]
        }
    }

    return body


def create_advanced_query_papers_body(
    topic,
    authors,
    results_by,
    type_of_pub,
    affiliation,
    city,
    from_date,
    to_date
):
    body = {
        'size': 1000,
        'query': {
            'bool': {
                'should': [
                    {
                        'match': {
                            'title': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    },
                    {
                        'match': {
                            'proceedingsName': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    },
                    {
                        'match': {
                            'journal': {
                                'query': topic,
                                'operator': 'and'
                            }
                        }
                    }
                ],
                'minimum_should_match': 1,
                'must': [
                    {
                        'match': {
                            'authors': {
                                'query': authors,
                                'operator': 'and'
                            }
                        }
                    }
                ],
                'filter': [
                ]
            }
        },
        'aggs': {
            'Authors': {
                'terms': {
                    'field': 'authors.raw'
                }
            }
        },
        '_source': {
            'includes': [
                'title',
                'authors',
                'type',
                'year',
                'journal',
                'proceedingsName',
                'city',
                'country',
                'affiliation_name',
                'doi']
        }
    }

    if results_by == 'affiliation':
        aff_dict = {
            'term': {
                'affiliation_name.raw': affiliation
            }
        }

    elif results_by == 'country':
        aff_dict = {
            'term': {
                'country.raw': affiliation
            }
        }

    else:
        aff_dict = {
            'term': {
                'country.raw': affiliation
            }
        }

    body['query']['bool']['filter'].append(aff_dict)

    if from_date and to_date:
        range_filter = {
            'range': {
                'year': {
                    'gte': from_date,
                    'lte': to_date
                }
            }
        }

    elif from_date and not to_date:
        range_filter = {
            'range': {
                'year': {
                    'gte': from_date
                }
            }
        }

    elif not from_date and to_date:
        range_filter = {
            'range': {
                'year': {
                    'lte': to_date
                }
            }
        }

    else:
        range_filter = None

    if range_filter:
        body['query']['bool']['filter'].append(range_filter)

    if results_by == 'city':
        city_dict = {
            'term':  {
                'city.raw': city
            }
        }
        body['query']['bool']['filter'].append(city_dict)

    if not authors:
        body['query']['bool'].pop('must')

    if type_of_pub in ['inproceedings', 'article']:
        type_dict = {
            'term': {
                'type': type_of_pub
            }
        }
        body['query']['bool']['filter'].append(type_dict)

    return body


def create_all_research_query_body():
    body = {
        'size': 0,
        'query': {
            'match_all': {}
        },
        'aggs': {
            'my_buckets': {
                'composite': {
                    'size': 1000,
                    'sources': [
                        {
                            'Affiliation': {
                                'terms': {
                                    'field': 'affiliation_name.raw'
                                }
                            }
                        },
                        {
                            'Lat': {
                                'terms': {
                                    'field': 'affLat'
                                }
                            }
                        },
                        {
                            'Long': {
                                'terms': {
                                    'field': 'affLong'
                                }
                            }
                        },
                        {
                            'Country': {
                                'terms': {
                                    'field': 'country.raw'
                                }
                            }
                        },
                        {
                            'City': {
                                'terms': {
                                    'field': 'city.raw'
                                }
                            }
                        }
                    ]
                }
            }
        }
    }

    return body
