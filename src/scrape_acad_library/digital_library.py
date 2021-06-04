#!/usr/bin/env python
# coding: utf-8

import requests
import backoff
import traceback

from .exceptions import *

from abc import ABCMeta, abstractmethod

class DigitalLibrary(metaclass=ABCMeta):

    def __init__(self,
                 name,
                 request_type,
                 api_key_name,
                 api_key,
                 query_url,
                 num_results_key,
                 start_key,
                 query_option_information,
                 non_query_parameters = {},
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
        self.non_query_parameters = non_query_parameters
        self.query_data = {}
        self.error = False

    def set_non_query_parameter(self, name, value):
        self.non_query_parameters[name] = value
        
    def set_query_option(self, name, value):
        if name == "start":
            self.start = value
        elif name == "num_results":
            self.num_results = value
        else:
            try:
                self.query_data[self.query_option_information[name]] = value
            except KeyError:
                raise UnknownQueryParameter(name, message = f"Digital Library {self.name} does not support query option {name}.")

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries = 10)
    def make_request(self):
        request_data = {
            self.api_key_name: self.api_key,
            self.start_key: self.start,
            self.number_results_key: self.num_results
        }
        for key in self.non_query_parameters.keys():
            request_data[key] = self.non_query_parameters[key]
        for key in self.query_data.keys():
            request_data[key] = self.query_data[key]
        response = requests.get(url = self.query_url,
                                params = request_data)
        return response.json()

    @abstractmethod
    def process_results(self, results):
        raise NotImplementedError("Must define result processing logic.")

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
            print(traceback.format_exc())
            self.error = True
