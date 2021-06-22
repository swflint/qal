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

from .digital_library import DigitalLibrary
from .types import Article

import json
import logging

from time import sleep

LOGGER = logging.getLogger('qal.scienc_direct')


class ScienceDirect(DigitalLibrary):

    def __init__(self, api_key, max_results=25, start_result=1):
        super().__init__(name="science_direct",
                         description="Elsevier Science Direct",
                         request_type="PUT",
                         api_key=api_key,
                         api_endpoint="https://api.elsevier.com/content/search/sciencedirect",
                         page_size=max_results,
                         start=start_result,
                         query_option_information={'query_text': (True, "Boolean match expression", 'qs'),
                                                   'year': (True, "Match year", 'date'),
                                                   'issue': (True, "Match issue.", 'issue'),
                                                   'publication_title': (True, "Match parent title.", 'pub'),
                                                   'title': (True, "Match title.", 'title'),
                                                   'volume': (True, "Match volume.", 'volume')})

    def process_results(self, data):
        if 'error-response' in data.keys():
            if data['error-response']['error_code'] == 'RATE_LIMIT_EXCEEDED':
                LOGGER.error("Rate limit has been exceeded, pausing.")
                sleep(60)
                return []
            else:
                LOGGER.critical("An unknown error has occured: %s.", data['error-response'])
                self.error = True
                return []
        LOGGER.debug("There are %s results for the query, %d in the batch.", data['resultsFound'], len(data['results']))
        self.results_total = int(data['resultsFound'])
        self.start += len(data['results'])
        results = []
        for result in data['results']:
            identifier = result['doi']
            title = result['title']
            authors = []
            if result['authors'] == None:
                continue
            for author in result['authors']:
                authors.append(author['name'])
            year = result['publicationDate'][:4]
            result_item = Article(identifier, title, authors, year,
                                  journal=result['sourceTitle'],
                                  volume=None,
                                  issue=None,
                                  abstract=None,
                                  pages=None)
            results.append(result_item)
        return results

    def construct_headers(self):
        LOGGER.debug("Constructing headers.")
        return {'Accept': 'application/json',
                'X-ELS-APIKey': self.api_key}

    def construct_body(self):
        LOGGER.debug("Constructing request body.")
        body_data = {'offset': self.start,
                     'show': self.page_size}
        body_data.update(self.query_data)
        return json.dumps(body_data)
