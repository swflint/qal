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
from .types import Article, Conference

import re
import logging

LOGGER = logging.getLogger('qal.springer')


def sanitize_venue(string):
    string = re.sub(r'proceedings of the', '', string, flags=re.IGNORECASE)
    string = re.sub(r"[0-9]{1,2}(nd|th|rd|st)", "", string)
    string = re.sub(r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeeth|eighteenth|ninteenth|twentieth|twenty|thirtieth|thirty|fourthieth|fourty|fiftieth|fifty|sixtieth|sixty)-?", "", string, flags=re.IGNORECASE)
    string = re.sub(r'\u2014', '', string)
    string = re.sub(r'\u2013', '', string)
    string = re.sub(r'\'\d{2}', '', string)
    string = re.sub(r'\u2019[0-9]+', '', string)
    string = re.sub(r'[0-9]{4}', '', string)
    string = re.sub(r'Part (v|iv|iii|ii|i)', '', string, flags=re.IGNORECASE)
    string = re.sub(r'proceedings of', '', string, flags=re.IGNORECASE)
    string = re.sub(r'volume \d+', '', string, flags=re.IGNORECASE)
    string = re.sub(r'\s[,:]\s', '', string)
    string = re.sub(r'\s+\)', '\)', string)
    string = re.sub(r' - ', ' ', string)
    string = re.sub(r'\s+', ' ', string).strip()
    return string


class SpringerNature(DigitalLibrary):
    def __init__(self, api_key, max_results=50, start_result=1):
        super().__init__(name='springer_nature',
                         description='Springer Link',
                         request_type='GET',
                         api_key=api_key,
                         api_endpoint="http://api.springernature.com/meta/v2/json",
                         page_size=max_results,
                         start=start_result,
                         query_option_information={'query_text': (True, 'Boolean match expression.', 'q')})

    def construct_parameters(self):
        LOGGER.debug("Constructing URL parameters.")
        params = {'s': self.start,
                  'p': self.page_size,
                  'api_key': self.api_key}
        params.update(self.query_data)
        return params

    def process_results(self, data):
        LOGGER.debug("There are %s results for the query, %s in the batch.", data['result'][0]['total'], data['result'][0]['recordsDisplayed'])
        self.results_total = int(data['result'][0]['total'])
        self.start += int(data['result'][0]['recordsDisplayed'])
        results = []
        for result in data['records']:
            result_type = result['contentType']
            identifier = result['doi']
            title = result['title']
            authors = []
            for author in result['creators']:
                authors.append(author['creator'])
            year = result['publicationDate'][:4]
            if result_type == 'Article':
                result_item = Article(identifier,
                                      title,
                                      authors,
                                      year,
                                      journal=result['publicationName'],
                                      volume=result['volume'],
                                      issue=result['number'],
                                      abstract=result.get('abstract'),
                                      pages=None)
                results.append()
            elif result_type == 'Chapter ConferencePaper':
                result_item = Conference(identifier,
                                         title,
                                         authors,
                                         year,
                                         book_title=result['publicationName'],
                                         conference=sanitize_venue(
                                             result['publicationName']),
                                         abstract=result.get('abstract'),
                                         pages=None)
                results.append(result_item)
        return data['records']
