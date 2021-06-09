#!/usr/bin/env python
# coding: utf-8

import requests
import backoff
import traceback

from math import ceil

from .exceptions import *

from abc import ABCMeta, abstractmethod

class DigitalLibrary(metaclass=ABCMeta):
    """A representation of a queryable Digital Library.
    
    By default, this can handle making a request, provided a query is
    given.
    """

    def __init__(self,
                 name,
                 request_type,
                 api_key,
                 api_endpoint,
                 query_option_information,
                 page_size = 10,
                 start = 1):
        """Initialize a Digital Library.
        
        Parameters:
        name (string): The name of the Digital library
        request_type (string): The HTTP request type used by the Digital Library
        api_key (string): The API Key used in making queries
        api_endpoint (string): API Endpoint
        query_option_information (dict, symbolic name -> query parameter name): Dictionary describing how to map symbolic query names to parameter names
        page_size (int): How many results to grab at a time, by default
        start (int): Where to start grabbing results, by default
        """
        self.name = name
        self.request_type = request_type
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.page_size = page_size
        self.start = start
        self.query_option_information = query_option_information
        
        self.results_total = -1
        self.non_query_parameters = {}
        self.query_data = {}
        self.error = False

    def set_non_query_parameter(self, name, value):
        """Set a non-query parameter NAME to VALUE."""
        self.non_query_parameters[name] = value

    def set_non_query_parameters(self, non_query_parameters):
        for key in non_query_parameters.keys():
            self.non_query_parameters[key] = non_query_parameters[key]
        
    def set_query_option(self, name, value):
        """Set a query option NAME to VALUE.  Note, NAME should be a symbolic name, and will error if not available."""
        try:
            self.query_data[self.query_option_information[name]] = value
        except KeyError:
            raise UnknownQueryParameter(name, message = f"Digital Library {self.name} does not support query option {name}.")

    def set_query_options(self, query_options):
        for key in query_options.keys():
            self.set_query_option(key, query_options[key])

    def construct_headers(self):
        return { }

    def construct_parameters(self):
        return { }

    def construct_body(self):
        return None

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries = 10)
    def make_request(self):
        """Make a request."""
        headers = self.construct_headers()
        params = self.construct_parameters()
        body = self.construct_body()
        response = requests.request(method = self.request_type,
                                    url = self.api_endpoint,
                                    params = params,
                                    headers = headers,
                                    data = body)
        return response.json()

    @abstractmethod
    def process_results(self, results):
        """Process results (takes a request response object).

         - This should return a list of scrape_acad_library.types.Publication.
         - If an un-recoverable error occurs, set self.error to true, otherwise, try to recover it."""
        raise NotImplementedError("Must define result processing logic.")

    def has_results(self):
        """Do we expect to have more results?"""
        if self.error:
            return False
        elif self.results_total == -1:
            return True
        else:
            return self.start < self.results_total

    def batch(self):
        """Query batch by batch."""
        try:
            if self.has_results():
                data = self.make_request()
                results = self.process_results(data)
                for result in results:
                    yield result
                else:
                    return []
        except:
            print(traceback.format_exc())
            self.error = True

    def estimate_batches(self):
        if self.results_total > 0:
            return ceil(self.results_total / self.page_size)
        else:
            return 1000

    def estimate_batches_left(self):
        return self.estimate_batches() - ceil(self.start / self.page_size)
        
    def run(self):
        """Run a query, as long as possible."""
        try:
            while self.has_results():
                for result in self.batch():
                    yield result
        except:
            print(traceback.format_exc())
            self.error = True
