#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary
from .types import Article

class ScienceDirect(DigitalLibrary):

    def __init__(self, api_key, max_results = 50, start_result = 1):
        super().__init__(name = "science_direct",
                         request_type = "GET",
                         api_key_name = 'apiKey',
                         api_key = api_key,
                         query_url = "https://api.elsevier.com/content/metadata/article",
                         start_key = 'start',
                         num_results_key = 'count',
                         default_num_results = max_results,
                         default_start = start_result,
                         query_option_information = { 'query_text': 'query' },
                         non_query_parameters = { 'httpAccept': 'application/json',
                                                  'view': 'COMPLETE' })

    def process_results(self, data):
        self.results_total = int(data['search-results']['opensearch:totalResults'])
        self.start += len(data['entry'])
        results = []
        for result in data['entry']:
            identifier = result['dc:identifier']
            title = result['dc:title']
            authors = []
            for author in result['authors']:
                authors.append(f"{author['given-name']} {author['surname']}")
            result_type = result['prism:aggregationType']
            year = result['prism:coverDate'][0]['$'][:4]
            if result_type == 'journal':
                result_item = Article(identifier, title, authors, year,
                                      journal = result['prism:publicationName'],
                                      volume = result['prism:volume'],
                                      issue = result['prism:issueIdentifier'],
                                      abstract = result['prism:teaser'],
                                      pages = None)
        return results
