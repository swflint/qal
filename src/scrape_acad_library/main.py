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
                        choices = apis.keys(),
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
                        help = "set API option KEY to VALUE",
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

    parser.add_argument('--number-batches', '-b', metavar = 'N',
                        type = int,
                        dest = 'batches',
                        default = -1)
    
    args = parser.parse_args()

    key = None
    if args.api_key:
        key = args.api_key
    elif os.environ.get('LIBRARY_API_KEY'):
        key = os.environ.get('LIBRARY_API_KEY')
    else:
        print("An API key must be provided as an argument or in the LIBRARY_API_KEY environment variable.", file = sys.stderr)
        sys.exit(1)

    api = make_api(args.library, key)
    api.start = args.start
    api.page_size = args.page_size

    if args.options:
        for option in args.options:
            (key, value) = option.split('=', 1)
            api.set_option(key, value)

    for query_item in args.query:
        (key, value) = query_item.split('=', 1)
        api.set_query_option(key, value)

    results_data = {}
    if args.output and osp.exists(args.output):
        with open(args.output, 'r') as fd:
            results_data = jsonpickle.decode(fd.read())

    def do_batch():
        for results in api.batch():
            if result.identifier not in results_data.keys():
                results_data[result.identifier] = result
            results_data[result.identifier].add_search_terms(args.library, api.query_data)
            if args.output:
                with open(args.output, 'w') as fd:
                    fd.write(jsonpickle.encode(results_data))

    if args.batches > 0:
        for i in range(args.batches):
            do_batch()
    else:
        while api.has_results():
            do_batch()
