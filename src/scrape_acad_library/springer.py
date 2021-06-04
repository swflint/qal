#!/usr/bin/env python
# coding: utf-8

from .digital_library import DigitalLibrary
from .types import Article, Conference

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
                results.append(Article(identifier,
                                       title,
                                       authors,
                                       year,
                                       journal = result['publicationName'],
                                       volume = result['volume'],
                                       issue = result['number'],
                                       abstract = result.get('abstract'),
                                       pages = None))
            elif result_type == 'Chapter ConferencePaper':
                results.append(Conference(identifier,
                                          title,
                                          authors,
                                          year,
                                          book_title = result['publicationName'],
                                          conference = result['conferenceInfo'][0]['confSeriesName'],
                                          abstract = result.get('abstract'),
                                          pages = None))
        return data['records']
