#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary

class IEEEXplore(DigitalLibrary):
    def __init__(self, api_key, max_results = 50, start_result = 1):
        super().__init__(name = 'ieee_explore',
                         request_type = 'GET',
                         api_key_name = 'apikey',
                         api_key = api_key,
                         query_url = 'http://ieeexploreapi.ieee.org/api/v1/search/articles',
                         start_key = 'start_record',
                         num_results_key = 'max_results',
                         default_num_results = max_results,
                         default_start = start_result,
                         query_option_information = { 'query_text': 'querytext',
                                                      'abstract': 'abstract',
                                                      'affiliation': 'affiliation',
                                                      'article_number': 'article_number',
                                                      'article_title': 'article_title',
                                                      'author': 'author',
                                                      'd-au': 'd-au',
                                                      'doi': 'doi',
                                                      'd-publisher': 'd-publisher',
                                                      'd-pubtype': 'd-pubtype',
                                                      'd-year': 'd-year',
                                                      'facet': 'facet',
                                                      'index_terms': 'index_terms',
                                                      'isbn': 'isbn',
                                                      'issn': 'issn',
                                                      'issue_number': 'is_number',
                                                      'meta_data': 'meta_data',
                                                      'publication_title': 'publication_title',
                                                      'publication_year': 'publication_year',
                                                      'thesaurus_terms': 'thesaurus_terms' },
                         additional_query_parameters = { 'format': 'json' })

    def process_results(self, data):
        self.results_total = data['total_records']
        self.start += len(data['articles'])
        return data['articles']
