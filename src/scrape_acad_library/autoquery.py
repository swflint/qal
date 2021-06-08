#!/usr/bin/env python
# coding: utf-8

import os
import sys

import os.path as osp

from argparse import ArgumentParser

from . import *
from .exceptions import *

from tqdm import trange, tqdm

import json
import jsonpickle

def main():
    parser = ArgumentParser(description = "Automatically query several academic libraries as defined by a control file.")

    parser.add_argument('--verbose', '-v',
                        help = "provide verbose logging",
                        default = False,
                        action = 'store_true',
                        dest = 'verbose')

    parser.add_argument('--plan-file', '-p', metavar = "PLAN",
                        type = str,
                        required = True,
                        dest = 'plan_file')

    parser.add_argument('--status-file', '-s', metavar = "STATUS",
                        type = str,
                        required = True,
                        dest = 'status_file')

    parser.add_argument('--output-file', '-o', metavar = "OUT",
                        type = str,
                        required = True,
                        dest = 'out_file')

    args = parser.parse_args()

    def vprint(message, stream_like = sys.stderr):
        if args.verbose:
            stream_like.write(message)
            if stream_like is sys.stderr:
                stream_like.write("\n")

    def write_status(status):
        vprint("Saving status file.")
        with open(args.status_file, 'w') as fd:
            json.dump(status, fd, indent = True)

    def write_data(results):
        vprint("Saving results data file.")
        with open(args.out_file, 'w') as fd:
            fd.write(jsonpickle.encode(results))

    plan = {}
    vprint("Loading plan")
    with open(args.plan_file, 'r') as fd:
        plan = json.load(fd)

    status = []
    if osp.exists(args.status_file):
        vprint("Restoring status.")
        with open(args.status_file, 'r') as fd:
            status = json.load(fd)

    results = {}
    if osp.exists(args.out_file):
        vprint(f"Opening {args.out_file} for restoration.")
        with open(args.out_file, 'r') as fd:
            results = jsonpickle.decode(fd.read())
        vprint(f"Restored data.")

    def make_api_object(site):
        name = site['name']
        if name == 'springer':
            api = SpringerLink(api_key = site['key'])
        elif name == 'ieee-xplore':
            api = IEEEXplore(api_key = site['key'])
        elif args.library == 'science-direct':
            api = ScienceDirect(api_key = site['key'])

        if 'start' in site.keys():
            api.set_query_option('start', site['start'])

        if 'num_results' in site.keys():
            api.set_query_option('num_results', site['num_results'])

        if 'options' in site.keys():
            for key in site['options'].keys():
                api.set_non_query_parameter(key, site['options'][key])
            
        return api

    def set_query_parameters(api, query):
        for key in query.keys():
            api.set_query_option(key, query[key])

    def restore_query_status(api, site_id, query_id):
        status_item = status[site_id][query_id]
        if len(status_item.keys()) != 0:
            api.set_query_option('start', status_item['start'])
            api.set_query_option('num_results', status_item['number_results'])
            api.results_total = status_item['total']
            
    num_sites = len(plan['sites'])
    num_queries = len(plan['queries'])

    if len(status) == 0:
        for i in range(num_sites):
            row = []
            for i in range(num_queries):
                row.append({})
            status.append(row)

    write_status(status)

    sites_tqdm = tqdm(enumerate(plan['sites']))
    for site_id, site in sites_tqdm:
        query_tqdm = tqdm(enumerate(plan['queries']))
        for query_id, query in query_tqdm:
            vprint("Building API Object.", stream_like = query_tqdm)
            api = make_api_object(site)
            vprint("Setting Query Parameters", stream_like = query_tqdm)
            set_query_parameters(api, query)
            vprint("Restoring Query Status", stream_like = query_tqdm)
            restore_query_status(api, site_id, query_id)
            for result in api.run():
                query_tqdm.write(f"Processing result {result.identifier}.")
                if result.identifier not in results.keys():
                    results[result.identifier] = results
                # results[result.identifier].add_search_terms(site['name'], query)
                write_data(results)
                status[site_id][query_id]['total'] = api.results_total
                status[site_id][query_id]['start'] = api.start
                status[site_id][query_id]['number_results'] = api.num_results
                write_status(status)
