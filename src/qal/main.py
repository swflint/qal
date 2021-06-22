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

import os
import sys
import logging

import os.path as osp

from argparse import ArgumentParser

from . import *
from .exceptions import *
from .results_store import ResultsStore

import jsonpickle

LOGGER = logging.getLogger('qal.main')


def main():
    parser = ArgumentParser(
        description="Scrape & Mine various academic digital libraries.")

    parser.add_argument('--list-libraries', '-L',
                        help="list known libraries",
                        dest='list_libraries',
                        action='store_true',
                        default=False)

    parser.add_argument('--library', '-l', metavar='DIGITAL_LIBRARY',
                        help="select which digital library is used",
                        type=str,
                        choices=apis.keys(),
                        dest='library')

    parser.add_argument('--describe', '-d',
                        help="desribe query options for a specific library",
                        dest='describe_library',
                        action='store_true',
                        default=False)

    parser.add_argument('--api-key', '-k', metavar="KEY",
                        help="the API key used for making requests",
                        type=str,
                        dest='api_key')

    parser.add_argument('--option', '-o', metavar="KEY=VALUE",
                        help="set non-query option KEY to VALUE",
                        type=str,
                        dest='options',
                        action='append')

    parser.add_argument('--query', '-q', metavar="KEY=VALUE",
                        help="set API option KEY to VALUE",
                        type=str,
                        dest='query',
                        action='append')

    parser.add_argument('--results', '-r', metavar='RESULTS.JSON',
                        help="name of file in which to store results",
                        type=str,
                        dest='output')

    parser.add_argument('--start', '-s', metavar='N',
                        help="start result",
                        type=int,
                        dest='start',
                        default=1)

    parser.add_argument('--page-size', '-p', metavar='N',
                        help="size of page, or batch",
                        type=int,
                        dest='page_size',
                        default=10)

    parser.add_argument('--number-batches', '-b', metavar='N',
                        type=int,
                        dest='batches',
                        default=-1)

    parser.add_argument('--verbose', '-v',
                        help="provide verbose logging",
                        default=0,
                        action='count',
                        dest='verbose')

    args = parser.parse_args()

    logging.getLogger('qal').setLevel((6 - args.verbose)*10)

    if args.list_libraries:
        print("Known Libraries:")
        for key in apis.keys():
            api = make_api(key, 'x')
            print(f" - {key}: {api.describe()}")
        sys.exit(0)

    if args.library is None:
        parser.error("A library is required.")

    if args.describe_library:
        api = make_api(args.library, 'x')
        print(api.describe_options())
        sys.exit(0)

    key = get_env_var(args.library, args.api_key)
    if key is None:
        parser.error(
            f"An API key must be provided as an argument or in the {get_env_var_name(args.library)} or LIBRARY_API_KEY environment variables.")

    if not args.output:
        parser.error("A results storage file must be provided.")

    api = make_api(args.library, key)
    api.start = args.start
    api.page_size = args.page_size

    if args.options:
        for option in args.options:
            (key, value) = option.split('=', 1)
            api.set_option(key, value)

    query = {}
    for query_item in args.query:
        (key, value) = query_item.split('=', 1)
        query[key] = value
        api.set_query_option(key, value)

    results_store = ResultsStore(args.output, saviness=1)

    def do_batch():
        for result in api.batch():
            print("Processing {result.identifier}")
            results_store.add_item(result, args.library, query)

    if args.batches > 0:
        for i in range(args.batches):
            do_batch()
    else:
        while api.has_results():
            do_batch()
