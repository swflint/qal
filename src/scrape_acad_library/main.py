#!/usr/bin/env python
# coding: utf-8

import os
import sys

import os.path as osp

from argparse import ArgumentParser

from . import *
from .exceptions import *

import jsonpickle

def main():
    parser = ArgumentParser(description = "Scrape & Mine various academic digital libraries.")

    parser.add_argument('--library', '-l', metavar = 'DIGITAL_LIBRARY',
                        help = "select which digital library is used",
                        type = str,
                        choices = ['springer', 'ieee-xplore', 'science-direct'],
                        dest = 'library',
                        required = True)
    
    parser.add_argument('--api-key', '-k', metavar = "KEY",
                        help = "the API key used for making requests",
                        type = str,
                        dest = 'api_key')

    parser.add_argument('--option', '-o', metavar="KEY=VALUE",
                        help = "set non-query option KEY to VALUE",
                        type = str,
                        dest = 'options',
                        action = 'append')

    parser.add_argument('--query', '-q', metavar = "KEY=VALUE",
                        help = "set query parameter KEY to VALUE",
                        type = str,
                        dest = 'query',
                        action = 'append')

    parser.add_argument('--results', '-r', metavar = 'RESULTS.JSON',
                        help = "name of file in which to store results",
                        type = str,
                        required = True,
                        dest = 'output')

    parser.add_argument('--start', '-s', metavar = 'N',
                        help = "start result",
                        type = int,
                        dest = 'start',
                        default = 1)

    parser.add_argument('--page-size', '-p', metavar = 'N',
                        help = "size of page, or batch",
                        type = int,
                        dest = 'page_size',
                        default = 10)
    
    args = parser.parse_args()

    key = None
    if args.library == 'springer':
        if args.api_key or os.environ.get('SPRINGER_LINK_API_KEY'):
            if args.api_key:
                key = args.api_key
            else:
                key = os.environ.get('SPRINGER_LINK_API_KEY')
        else:
            print("An API key must be provided as either an argument or in the SPRINGER_LINK_API_KEY variable.", file = sys.stderr)
            sys.exit(1)
    elif args.library == 'ieee-xplore':
        if args.api_key or os.environ.get('IEEE_XPLORE_API_KEY'):
            if args.api_key:
                key = args.api_key
            else:
                key = os.environ.get('IEEE_XPLORE_API_KEY')
        else:
            print("An API key must be provided as either an argument or in the IEEE_XPLORE_API_KEY variable.", file = sys.stderr)
            sys.exit(1)
    else:
        if args.api_key or os.environ.get('SCIENCE_DIRECT_API_KEY'):
            if args.api_key:
                key = args.api_key
            else:
                key = os.environ.get('SCIENCE_DIRECT_API_KEY')
        else:
            print("An API key must be provided as either an argument or in the SCIENCE_DIRECT_API_KEY variable.", file = sys.stderr)
            sys.exit(1)

    api = None
    if args.library == 'springer':
        api = SpringerLink(api_key = key,
                           max_results = args.page_size,
                           start_result = args.start)
    elif args.library == 'ieee-xplore':
        api = IEEEXplore(api_key = key,
                         max_results = args.page_size,
                         start_result = args.start)
    else:
        api = ScienceDirect(api_key = key,
                            max_results = args.page_size,
                            start_result = args.start)

    if args.options:
        for option in args.options:
            (key, value) = option.split('=', 1)
            api.set_non_query_parameter(key, value)

    for query_item in args.query:
        (key, value) = query_item.split('=', 1)
        api.set_query_option(key, value)

    results_data = {}
    if args.output and osp.exists(args.output):
        with open(args.output, 'r') as fd:
            results_data = jsonpickle.decode(fd.read())

    for result in  api.run():
        if result.identifier not in results_data.keys():
            results_data[result.identifier] = result
        results_data[result.identifier].add_search_terms(args.library, args.query)
        if args.output:
            with open(args.output, 'w') as fd:
                fd.write(jsonpickle.encode(results_data))
