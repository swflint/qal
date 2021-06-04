#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary
from .types import Article, Conference

import re

def sanitize_venue(string):
    string = re.sub(r'proceedings of the', '', string, flags = re.IGNORECASE)
    string = re.sub(r"[0-9]{1,2}(nd|th|rd|st)", "", string)
    string = re.sub(r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeeth|eighteenth|ninteenth|twentieth|twenty|thirtieth|thirty|fourthieth|fourty|fiftieth|fifty|sixtieth|sixty)-?", "", string, flags = re.IGNORECASE)
    string = re.sub(r'\u2014', '', string)
    string = re.sub(r'\u2013', '', string)
    string = re.sub(r'\'\d{2}', '', string)
    string = re.sub(r'\u2019[0-9]+', '', string)
    string = re.sub(r'[0-9]{4}', '', string)
    string = re.sub(r'Part (v|iv|iii|ii|i)', '', string, flags = re.IGNORECASE)
    string = re.sub(r'proceedings of', '', string, flags = re.IGNORECASE)
    string = re.sub(r'volume \d+', '', string, flags=re.IGNORECASE)
    string = re.sub(r'\s[,:]\s', '', string)
    string = re.sub(r'\s+\)', '\)', string)
    string = re.sub(r' - ', ' ', string)
    string = re.sub(r'\s+', ' ', string).strip()
    return string

class SpringerNature(DigitalLibrary):
    def __init__(self, api_key, max_results = 50, start_result = 1):
        super().__init__(name = 'springer_nature',
                         request_type = 'GET',
                         api_key_name = 'api_key',
                         api_key = api_key,
                         query_url = "http://api.springernature.com/meta/v2/json",
                         start_key = 's',
                         num_results_key = 'p',
                         default_num_results = max_results,
                         default_start = start_result,
                         query_option_information = { 'query_text': 'q' })

    def process_results(self, data):
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
                                      journal = result['publicationName'],
                                      volume = result['volume'],
                                      issue = result['number'],
                                      abstract = result.get('abstract'),
                                      pages = None)
                results.append()
            elif result_type == 'Chapter ConferencePaper':
                result_item = Conference(identifier,
                                         title,
                                         authors,
                                         year,
                                         book_title = result['publicationName'],
                                         conference = sanitize_venue(result['publicationName']),
                                         abstract = result.get('abstract'),
                                         pages = None)
                results.append(result_item)
        return data['records']
