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
from .types import Conference, Article

import re
import logging

LOGGER = logging.getLogger('qal.ieeexplore')

def sanitize_venue(string):
    # string = re.sub(r"(ACM/)?IEEE(/ACM)?", "", string)
    string = re.sub(r"[0-9]{4}", "", string)
    string = re.sub(r"[0-9]{1,2}(nd|th|rd|st)", "", string)
    string = re.sub(r"Proceedings?\.?( of)?( the)?", "", string)
    string = re.sub(r"\bs ", "", string)
    string = re.sub(r"[\[\]]", "", string)
    string = re.sub(r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeeth|eighteenth|ninteenth|twentieth|twenty|thirtieth|thirty|fourthieth|fourty|fiftieth|fifty|sixtieth|sixty)-?", "", string, flags=re.IGNORECASE)
    string = re.sub(r"\(.*\)$", "", string)
    string = re.sub(r"^Annual", "", string)
    string = re.sub(r"(ACM/IEEE|IEEE/ACM|IEEE|ACM)", "", string)
    string = re.sub(r"^The ", "", string, flags=re.IGNORECASE)
    string = re.sub(r"\s+", " ", string).strip()
    string = string.strip()
    return string


class IEEEXplore(DigitalLibrary):
    def __init__(self, api_key, max_results=50, start_result=1):
        super().__init__(name='ieee_explore',
                         description="IEEEXplore Library",
                         request_type='GET',
                         api_key=api_key,
                         api_endpoint='http://ieeexploreapi.ieee.org/api/v1/search/articles',
                         page_size=max_results,
                         start=start_result,
                         query_option_information={'query_text': (True, 'Boolean match expression.', 'querytext'),
                                                   'abstract': (True, 'Match in abstract.', 'abstract'),
                                                   'affiliation': (True, 'Match affiliation.', 'affiliation'),
                                                   'title': (True, 'Match item title.', 'article_title'),
                                                   'author': (True, 'Match author.', 'author'),
                                                   'doi': (True, 'Match DOI.', 'doi'),
                                                   'index_terms': (True, 'Match index terms.', 'index_terms'),
                                                   'isbn': (True, 'Match ISBN.', 'isbn'),
                                                   'issn': (True, 'Match ISSN.', 'issn'),
                                                   'issue': (True, 'Match issue.', 'is_number'),
                                                   'publication_title': (True, 'Match parent title.', 'publication_title'),
                                                   'year': (True, 'Match publication year.', 'publication_year')})

    def construct_parameters(self):
        LOGGER.debug("Constructing URL parameters.")
        params = {'start_record': self.start,
                  'max_results': self.page_size,
                  'format': 'json',
                  'apikey': self.api_key}
        params.update(self.query_data)
        return params

    def process_results(self, data):
        LOGGER.debug("There are %d results for the query, %d in the batch.", data['total_records'], len(data['articles']))
        self.results_total = data['total_records']
        self.start += len(data['articles'])
        results = []
        for result in data['articles']:
            item_type = result['content_type']
            if 'doi' in result.keys():
                identifier = result['doi']
            else:
                identifier = result['article_number']
            if item_type == 'Conferences':
                authors = []
                for author in result['authors']['authors']:
                    authors.append(author['full_name'])
                    result_item = Conference(identifier,
                                             result['title'],
                                             authors,
                                             result['publication_year'],
                                             conference=sanitize_venue(
                                                 result['publication_title']),
                                             book_title=result['publication_title'],
                                             abstract=result.get('abstract'),
                                             pages=None)
                    results.append(result_item)
            elif item_type == 'Journals':
                authors = []
                for author in result['authors']['authors']:
                    authors.append(author['full_name'])
                result_item = Article(identifier,
                                      result['title'],
                                      authors,
                                      result['publication_year'],
                                      journal=result['publication_title'],
                                      abstract=result.get('abstract'),
                                      volume=result['volume'],
                                      issue=None,
                                      pages=None)
                results.append(result_item)
        return results
