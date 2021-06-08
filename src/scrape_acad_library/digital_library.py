#!/usr/bin/env python
# coding: utf-8

import requests
import backoff
import traceback

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
                 api_key_name,
                 api_key,
                 query_url,
                 num_results_name,
                 start_name,
                 query_option_information,
                 non_query_parameters = {},
                 default_num_results = 10,
                 default_start = 1):
        """Initialize a Digital Library.
        
        Parameters:
        name (string): The name of the Digital library
        request_type (string): The HTTP request type used by the Digital Library
        api_key_name (string): What parameter the API Key should be
        api_key (string): The API Key used in making queries
        query_url (string): API Endpoint
        number_results_name (string): The name of the query parameter for the number of results to select
        start_name (string): The name of the query parameter for the start result
        query_option_information (dict, symbolic name -> query parameter name): Dictionary describing how to map symbolic query names to parameter names
        non_query_parameters (dict): Dictionary of parameters not related to the query proper (i.e., what to return, additional authentication information, etc.)
        default_num_results (int): How many results to grab at a time, by default
        default_start (int): Where to start grabbing results, by default
        """
        self.name = name
        self.request_type = request_type
        self.api_key_name = api_key_name
        self.api_key = api_key
        self.query_url = query_url
        self.number_results_name = num_results_name
        self.num_results = default_num_results
        self.start_name = start_name
        self.start = default_start
        self.results_total = -1
        self.query_option_information = query_option_information
        self.non_query_parameters = non_query_parameters
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
        if name == "start":
            self.start = value
        elif name == "num_results":
            self.num_results = value
        else:
            try:
                self.query_data[self.query_option_information[name]] = value
            except KeyError:
                raise UnknownQueryParameter(name, message = f"Digital Library {self.name} does not support query option {name}.")

    def set_query_options(self, query_options):
        for key in query_options.keys():
            self.set_query_option(key, query_options[key])

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries = 10)
    def make_request(self):
        """Make a request."""
        request_data = {
            self.api_key_name: self.api_key,
            self.start_name: self.start,
            self.number_results_name: self.num_results
        }
        for key in self.non_query_parameters.keys():
            request_data[key] = self.non_query_parameters[key]
        for key in self.query_data.keys():
            request_data[key] = self.query_data[key]
        response = requests.request(method = self.request_type,
                                    url = self.query_url,
                                    params = request_data)
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
        
    def run(self):
        """Run a query, as long as possible."""
        try:
            while self.has_results():
                for result in self.batch():
                    yield result
        except:
            print(traceback.format_exc())
            self.error = True
