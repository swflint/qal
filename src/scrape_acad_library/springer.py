#!/usr/bin/env python
# coding: utf-8

import urllib.request
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse

import requests
import backoff

import json
import simplejson

class SpringerNature:

    def __init__(self, api_key, max_results = 100, start_result = 1):
        self.api_key = api_key
        self.query = ""
        self.max_results = max_results
        self.start_result = start_result
        self.total_results = -1
        self.error = False
        self.o_max_results = max_results
        self.o_start_result = start_result
        self.request_number = 0
        self.batch = 0

    def set_query(self, query):
        self.query = query
        self.max_results = self.o_max_results
        self.start_result = self.o_start_result
        self.total_results = -1
        self.error = False
        self.request_number = 0
        self.batch = 0

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.RequestException,
                           simplejson.errors.JSONDecodeError),
                          max_tries = 10)
    def make_request(self):
        self.request_number += 1
        print(f"Batch {self.batch}, Request {self.request_number}")
        response = requests.get(url = "http://api.springernature.com/meta/v2/json",
                                params = { 'api_key': self.api_key,
                                           'q': self.query,
                                           'p': self.max_results,
                                           's': self.start_result })
        return response.json()
        
    def run_query(self):
        self.request_number = 0
        self.batch += 1
        try:
            data = self.make_request()
            self.request_number = 0
            self.total_results = int(data['result'][0]['total'])
            self.start_result += int(data['result'][0]['recordsDisplayed'])
            return data['records']
        except simplejson.errors.JSONDecodeError:
            self.error = True
            return []

    def has_results(self):
        if self.error:
            return False
        elif self.total_results == -1:
            return True
        else:
            return self.start_result < self.total_results
