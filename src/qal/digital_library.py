#!/usr/bin/env python
# coding: utf-8

# This file is a part of `qal`.
#
# Copyright (c) 2021, University of Nebraska Board of Regents.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
import backoff
import traceback
import logging

from math import ceil

from .exceptions import *

from abc import ABCMeta, abstractmethod

from io import StringIO

LOGGER = logging.getLogger('qal.DigitalLibrary')

def backoff_logger(details):
    LOGGER.warning("Backing off {wait:0.1f} seconds after {tries} tries.".format(**details))

class DigitalLibrary(metaclass=ABCMeta):
    """A representation of a queryable Digital Library.

    By default, this can handle making a request, provided a query is
    given.
    """

    def __init__(self,
                 name,
                 description,
                 request_type,
                 api_key,
                 api_endpoint,
                 query_option_information,
                 page_size=10,
                 start=1):
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
        self.description = description
        self.request_type = request_type
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.page_size = page_size
        self.start = start
        self.query_option_information = query_option_information

        self.results_total = -1
        self.options = {}
        self.query_data = {}
        self.error = False

    def describe(self):
        return self.description

    def describe_options(self):
        description_output = ''
        with StringIO() as fd:
            fd.write("Known Query Options:\n")
            for key in self.query_option_information.keys():
                fd.write(
                    f" - {key} - {self.query_option_information[key][1]}\n")
            description_output = fd.getvalue()
        return description_output

    def set_option(self, name, value):
        """Set a non-query parameter NAME to VALUE."""
        self.options[name] = value

    def set_options(self, options):
        """Given a dictionary of options, automatically update the API options dictionary."""
        self.options.update(options)

    def set_query_option_non_key(self, key, value):
        """If a query option is not modified by setting a key in query_data, this is called.

        Note: If an API has an option that is defined in
        query_option_information as not being a key-to-key
        translation, this is used.  Override as needed.

        """
        raise UnknownQueryParameter(
            name, message=f"Digital Library {self.name} does not support query option {name}.")

    def set_query_option(self, name, value):
        """Set a query option NAME to VALUE.  Note, NAME should be a symbolic name, and will error if not available."""
        option_information = self.query_option_information.get(name)
        if option_information and option_information[0]:
            LOGGER.debug("Option %s is a dictionary entry.", name)
            self.query_data[option_information[2]] = value
        elif option_information and (not option_information[0]):
            LOGGER.debug("Option %s is set through delegation.")
            self.set_query_option_non_key(name, value)
        else:
            LOGGER.warning("Option %s is unknown.")
            raise UnknownQueryParameter(
                name, message=f"Digital Library {self.name} does not support query option {name}.")

    def set_query_options(self, query_options):
        for key in query_options.keys():
            self.set_query_option(key, query_options[key])

    def construct_headers(self):
        """Construct a dictionary of headers for the request.  Override if necessary."""
        return {}

    def construct_parameters(self):
        """Construct a dictionary of URL parameters for the request.  Override if necessary."""
        return {}

    def construct_body(self):
        """Construct a request body (a serializable or string).  Override if necessary."""
        return None

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries=10,
                          on_backoff=backoff_logger)
    def make_request(self):
        """Make a request."""
        headers = self.construct_headers()
        params = self.construct_parameters()
        body = self.construct_body()
        response = requests.request(method=self.request_type,
                                    url=self.api_endpoint,
                                    params=params,
                                    headers=headers,
                                    data=body)
        return response.json()

    @abstractmethod
    def process_results(self, results):
        """Process results (takes a request response object).

         - This should return a list of qal.types.Publication.
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
        """Estimate the total number of batches."""
        if self.results_total > 0:
            return ceil(self.results_total / self.page_size)
        else:
            return 1000

    def estimate_batches_left(self):
        """Estimate the number of batches that are left."""
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
