#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary
from .types import Conference, Article

import re

def sanitize_venue(string):
    # string = re.sub(r"(ACM/)?IEEE(/ACM)?", "", string)
    string = re.sub(r"[0-9]{4}", "", string)
    string = re.sub(r"[0-9]{1,2}(nd|th|rd|st)", "", string)
    string = re.sub(r"Proceedings?\.?( of)?( the)?", "", string)
    string = re.sub(r"\bs ", "", string)
    string = re.sub(r"[\[\]]", "", string)
    string = re.sub(r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeeth|eighteenth|ninteenth|twentieth|twenty|thirtieth|thirty|fourthieth|fourty|fiftieth|fifty|sixtieth|sixty)-?", "", string, flags = re.IGNORECASE)
    string = re.sub(r"\(.*\)$", "", string)
    string = re.sub(r"^Annual", "", string)
    string = re.sub(r"(ACM/IEEE|IEEE/ACM|IEEE|ACM)", "", string)
    string = re.sub(r"^The ", "", string, flags = re.IGNORECASE)
    string = re.sub(r"\s+", " ", string).strip()
    string = string.strip()
    return string

class IEEEXplore(DigitalLibrary):
    def __init__(self, api_key, max_results = 50, start_result = 1):
        super().__init__(name = 'ieee_explore',
                         request_type = 'GET',
                         api_key = api_key,
                         api_endpoint = 'http://ieeexploreapi.ieee.org/api/v1/search/articles',
                         page_size = max_results,
                         start = start_result,
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
                                                      'thesaurus_terms': 'thesaurus_terms' })

    def construct_parameters(self):
        params = { 'start_record': self.start,
                   'max_results': self.page_size,
                   'format': 'json',
                   'apikey': self.api_key }
        params.update(self.query_data)
        return params

    def process_results(self, data):
        self.results_total = data['total_records']
        self.start += len(data['articles'])
        results = []
        for result in data['articles']:
            item_type = result['content_type']
            if 'doi' in result.keys():
                identifier = result['doi']
            else:
                identifier = result['article_number']
            if item_type == 'Conferences':
                authors = []
                for author in result['authors']['authors']:
                    authors.append(author['full_name'])
                    result_item = Conference(identifier,
                                             result['title'],
                                             authors,
                                             result['publication_year'],
                                             conference = sanitize_venue(result['publication_title']),
                                             book_title = result['publication_title'],
                                             abstract = result.get('abstract'),
                                             pages = None)
                    results.append(result_item)
            elif item_type == 'Journals':
                authors = []
                for author in result['authors']['authors']:
                    authors.append(author['full_name'])
                result_item = Article(identifier,
                                      result['title'],
                                      authors,
                                      result['publication_year'],
                                      journal = result['publication_title'],
                                      abstract = result.get('abstract'),
                                      volume = result['volume'],
                                      issue = None,
                                      pages = None)
                results.append(result_item)
        return results
