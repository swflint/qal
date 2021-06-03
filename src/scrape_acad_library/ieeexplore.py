#!/usr/bin/env python
# coding: utf-8

import urllib.request
from urllib.error import HTTPError
import urllib.parse

import requests
import backoff

import json

class IEEEXplore:
    
    def __init__(self, api_key, max_results = 200, start_result = 1):
        self.api_key = api_key
        self.query_content = OrderedDict()
        self.max_results = max_results
        self.start_result = start_result
        self.total_results = -1
        self.error = False
        self.batch = 0
        self.request_number = 0

    def query_abstract(self, query):
        self.query_content['abstract'] = query

    def query_affiliation(self, query):
        self.query_content['affiliation'] = query

    def query_article_number(self, query):
        self.query_content['article_number'] = query

    def query_article_title(self, query):
        self.query_content['article_title'] = query

    def query_author(self, query):
        self.query_content['author'] = query

    def query_d_au(self, query):
        self.query_content['d-au'] = query

    def query_doi(self, query):
        self.query_content['doi'] = query

    def query_d_publisher(self, query):
        self.query_content['d-publisher'] = query

    def query_d_pubtype(self, query):
        self.query_content['d-pubtype'] = query

    def query_d_year(self, query):
        self.query_content['d_year'] = query

    def query_facet(self, query):
        self.query_content['facet'] = query
    
    def query_index_terms(self, query):
        self.query_content['index_terms'] = query
    
    def query_isbn(self, query):
        self.query_content['isbn'] = query

    def query_issn(self, query):
        self.query_content['issn'] = query
    
    def query_is_number(self, query):
        self.query_content['is_number'] = query

    def query_meta_data(self, query):
        self.query_content['meta_data'] = query
    
    def query_publication_title(self, query):
        self.query_content['publication_title'] = query
    
    def query_publication_year(self, query):
        self.query_content['publication_year'] = query
    
    def query_querytext(self, query):
        self.query_content['querytext'] = query

    def query_thesaurus_terms(self, query):
        self.query_content['thesaurus_terms'] = query

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.RequestException,
                           simplejson.errors.JSONDecoderError),
                          max_tries = 10)
    def make_request(self):
        self.request_number += 1
        print(f"Batch {self.batch}, Request: {self.request_number}")
        parameters = { 'apikey': self.api_key,
                       'format': 'json',
                       'max_results': self.max_results,
                       'start_record': self.start_result}
        for key, value in self.query_content:
            parameters[key] = value

        response = requests.get(url = 'http://ieeexploreapi.ieee.org/api/v1/search/articles',
                                params = parameters)
        return response.json()
        
    def run_query(self):
        self.request_number = 0
        self.batch += 1
        try:
            data = self.make_request()
            self.total_results = data['total_rectords']
            self.start_results += len(data['articles'])
            return data['articles']
        except:
            self.error = True
            return []

    def has_results(self):
        if self.error:
            return False
        elif self.total_results == -1:
            return True
        else:
            return self.start_result < self.total_results

