#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary
from .types import Article

from time import sleep

class ScienceDirect(DigitalLibrary):

    def __init__(self, api_key, max_results = 25, start_result = 1):
        super().__init__(name = "science_direct",
                         request_type = "GET",
                         api_key_name = 'apiKey',
                         api_key = api_key,
                         query_url = "https://api.elsevier.com/content/search/sciencedirect",
                         start_key = 'start',
                         num_results_key = 'count',
                         default_num_results = max_results,
                         default_start = start_result,
                         query_option_information = { 'query_text': 'query' },
                         non_query_parameters = { 'httpAccept': 'application/json' })

    def process_results(self, data):
        if 'error-response' in data.keys():
            if data['error-response']['error_code'] == 'RATE_LIMIT_EXCEEDED':
                print("Rate Limit Exceeded: Pausing.")
                sleep(60)
                return []
            else:
                print(f"An error has occured: {data['error-response']}")
                self.error = True
                return []
        self.results_total = int(data['search-results']['opensearch:totalResults'])
        self.start += len(data['search-results']['entry'])
        results = []
        for result in data['search-results']['entry']:
            identifier = result['prism:doi']
            title = result['dc:title']
            authors = []
            if result['authors'] == None:
                continue
            for author in result['authors']:
                authors.append(author)
            year = result['prism:coverDate'][:4]
            result_item = Article(identifier, title, authors, year,
                                  journal = result['prism:publicationName'],
                                  volume = None,
                                  issue = None,
                                  abstract = None,
                                  pages = None)
            results.append(result_item)
        return results
