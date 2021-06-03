#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary

class SpringerNature(DigitalLibrary):
    def __init__(self, api_key, max_results = 50, start_result = 1):
        super().__init__(name = 'springer_nature',
                         request_type = 'GET',
                         api_key_name = 'api_key',
                         api_key = api_key,
                         query_url = "http://api.springernature.com/meta/v2/json",
                         start_key = 's',
                         num_results_key = 'p',
                         default_num_results = max_results,
                         default_start = start_result,
                         query_option_information = { 'query_text': 'q' })

    def process_results(self, data):
        self.results_total = int(data['result'][0]['total'])
        self.start += int(data['result'][0]['recordsDisplayed'])
        return data['records']
