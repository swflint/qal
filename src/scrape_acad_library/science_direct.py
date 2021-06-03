#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary

class ScienceDirect(DigitalLibrary):

    def __init__(self, api_key):
        super().__init__(name = "science_direct",
                         request_type = "GET",
                         api_key_name = 'apiKey',
                         api_key = api_key,
                         query_url = "https://api.elsevier.com/content/metadata/article",
                         start_key = 'start',
                         num_results_key = 'count',
                         query_option_information = { 'query_text': 'query' },
                         additional_query_parameters = { 'httpAccept': 'application/json',
                                                         'view': 'COMPLETE' })

    def process_results(self, results):
        self.results_total = int(results['search-results']['opensearch:totalResults'])
        self.start += len(results['entry'])
        return results['entry']
