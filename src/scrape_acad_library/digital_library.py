#!/usr/bin/env python
# coding: utf-8

import requests
import backoff

from .exceptions import *

class DigitalLibrary:

    def __init__(self,
                 name,
                 request_type,
                 api_key_name,
                 api_key,
                 query_url,
                 num_results_key,
                 start_key,
                 query_option_information,
                 additional_query_parameters = {},
                 default_num_results = 10,
                 default_start = 1):
        self.name = name
        self.request_type = request_type
        self.api_key_name = api_key_name
        self.api_key = api_key
        self.query_url = query_url
        self.number_results_key = num_results_key
        self.num_results = default_num_results
        self.start_key = start_key
        self.start = default_start
        self.results_total = -1
        self.query_option_information = query_option_information
        self.additional_query_parameters = additional_query_parameters
        self.query_data = {}
        self.error = False
        
    def set_query_option(self, name, value):
        if name == "start":
            self.start = value
        elif name == "num_results":
            self.num_results = value
        else:
            try:
                self.query_data[self.query_option_information[name]] = value
            except KeyError:
                raise UnknownQueryParameter(name, message = f"Digital Library {self.name} does not support query option {name}.u")

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries = 10)
    def make_request(self):
        request_data = {
            self.api_key_name: self.api_key,
            self.start_key: self.start,
            self.number_results_key: self.num_results
        }
        for key in self.additional_query_parameters.keys():
            request_data[key] = self.additional_query_parameters[key]
        for key in self.query_data.keys():
            request_data[key] = self.query_data[key]
        response = requests.get(url = self.query_url,
                                params = request_data)
        return response.json()

    def process_results(self, results):
        pass

    def has_results(self):
        if self.error:
            return False
        elif self.results_total == -1:
            return True
        else:
            return self.start < self.results_total
    
    def run(self):
        try:
            while self.has_results():
                data = self.make_request()
                results = self.process_results(data)
                for result in results:
                    yield result
        except:
            self.error = True
