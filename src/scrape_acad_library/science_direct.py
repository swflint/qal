#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary
from .types import Article

import json

from time import sleep

class ScienceDirect(DigitalLibrary):

    def __init__(self, api_key, max_results = 25, start_result = 1):
        super().__init__(name = "science_direct",
                         description = "Elsevier Science Direct",
                         request_type = "PUT",
                         api_key = api_key,
                         api_endpoint = "https://api.elsevier.com/content/search/sciencedirect",
                         page_size = max_results,
                         start = start_result,
                         query_option_information = { 'query_text': (True, "Boolean match expression", 'qs'),
                                                      'year': (True, "Match year", 'date'),
                                                      'issue': (True, "Match issue.", 'issue'),
                                                      'publication_title': (True, "Match parent title.", 'pub'),
                                                      'title': (True, "Match title.", 'title'),
                                                      'volume': (True, "Match volume.", 'volume') })

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
        self.results_total = int(data['resultsFound'])
        self.start += len(data['results'])
        results = []
        for result in data['results']:
            identifier = result['doi']
            title = result['title']
            authors = []
            if result['authors'] == None:
                continue
            for author in result['authors']:
                authors.append(author['name'])
            year = result['publicationDate'][:4]
            result_item = Article(identifier, title, authors, year,
                                  journal = result['sourceTitle'],
                                  volume = None,
                                  issue = None,
                                  abstract = None,
                                  pages = None)
            results.append(result_item)
        return results

    def construct_headers(self):
        return { 'Accept': 'application/json',
                 'X-ELS-APIKey': self.api_key }

    def construct_body(self):
        body_data = { 'offset': self.start,
                      'show': self.page_size }
        body_data.update(self.query_data)
        return json.dumps(body_data)
