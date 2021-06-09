#!/usr/bin/env python
# coding: utf-8

import os
import sys

import os.path as osp
import os

from argparse import ArgumentParser

from . import *
from .exceptions import *

from tqdm import trange, tqdm

import json
import jsonpickle

VERBOSE = 0
OUT_FILE = ''
STATUS_FILE = ''

def vprint(level, message, stream_like = sys.stderr):
    if level <= VERBOSE:
        if type(stream_like) is tqdm:
            stream_like.display(message)
        else:
            stream_like.write(message)
            if stream_like is sys.stderr:
                stream_like.write("\n")

def make_api_object(site):
    name = site['name']
    if name == 'springer':
        api = SpringerLink(api_key = site['key'])
    elif name == 'ieee-xplore':
        api = IEEEXplore(api_key = site['key'])
    elif name == 'science-direct':
        api = ScienceDirect(api_key = site['key'])
    
    if 'start' in site.keys():
        api.start = site['start']

    if 'page_size' in site.keys():
        api.page_size = site['page_size']

    if 'options' in site.keys():
        api.set_non_query_parameters(site['options'])
    return api

def write_status(status):
    vprint(2, "Saving status file.")
    vprint(3, "Retaining backup copy of status file.")
    if osp.exists(STATUS_FILE):
        os.replace(STATUS_FILE, f"{STATUS_FILE}.bak")
    with open(STATUS_FILE, 'w') as fd:
        json.dump(status, fd, indent = True)
    vprint(2, "Saved status file.")

def write_data(results):
    vprint(2, "Saving results data file.")
    vprint(3, "Retaining backup copy of results file.")
    if osp.exists(OUT_FILE):
        os.replace(OUT_FILE, f"{OUT_FILE}.bak")
    with open(OUT_FILE, 'w') as fd:
        fd.write(jsonpickle.encode(results))
    vprint(2, "Saved status file.")

def restore_query_status(status, api, site_id, query_id):
    status_item = status['statuses'][site_id][query_id]
    if len(status_item.keys()) != 0:
        api.start = status_item['start']
        api.page_size = status_item['page_size']
        api.results_total = status_item['total']

def max_runs(batches):
    max(map(max, batches))
        
def main():
    parser = ArgumentParser(description = "Automatically query several academic libraries as defined by a control file.")

    parser.add_argument('--verbose', '-v',
                        help = "provide verbose logging",
                        default = 0,
                        action = 'count',
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

    parser.add_argument('--number-batches', '-b', metavar = "N",
                        type = int,
                        dest = 'batches',
                        default = -1)

    args = parser.parse_args()

    global VERBOSE
    global STATUS_FILE
    global OUT_FILE
    VERBOSE = args.verbose
    STATUS_FILE = args.status_file
    OUT_FILE = args.out_file

    plan = {}
    vprint(2, "Loading plan")
    with open(args.plan_file, 'r') as fd:
        plan = json.load(fd)


    status = {}
    if osp.exists(args.status_file):
        vprint(2, "Restoring status.")
        with open(args.status_file, 'r') as fd:
            status = json.load(fd)
        vprint(1, "Restored status.")

    results = {}
    if osp.exists(args.out_file):
        vprint(2, f"Opening {args.out_file} for restoration.")
        with open(args.out_file, 'r') as fd:
            results = jsonpickle.decode(fd.read())
        vprint(1, f"Restored data.")
            
    num_sites = len(plan['sites'])
    num_queries = len(plan['queries'])

    vprint(2, "Seeding status structure.")
    if len(status.keys()) == 0:
        status['statuses'] = []
        status['has_results'] = []
        status['incomplete'] = num_sites * num_queries
        status['batches'] = []
        status['max_batches'] = 10
        for i in range(num_sites):
            row = []
            has_results = []
            batches = []
            for i in range(num_queries):
                row.append({})
                has_results.append(True)
                batches.append(10)
            status['statuses'].append(row)
            status['has_results'].append(has_results)
            status['batches'].append(batches)
    vprint(1, "Seeded status structure.")
            
    write_status(status)

    def batch_across():
        sites_tqdm = tqdm(enumerate(plan['sites']), desc = "Sites", total = num_sites, position = 1)
        for site_id, site in sites_tqdm:
            vprint(2, f"Starting for site {site['name']}.")
            query_tqdm = tqdm(enumerate(plan['queries']), desc = "Query", total = num_queries, position = 2)
            if not site['enabled']:
                continue
            for query_id, query in query_tqdm:
                vprint(2, f"Starting for query number {query_id}")
                if status['has_results'][site_id][query_id]:
                    vprint(4, f"Building API object.")
                    api = make_api_object(site)
                    vprint(4, "Setting query parameters.")
                    api.set_query_options(query)
                    vprint(4, "Restoring query status.")
                    restore_query_status(status, api, site_id, query_id)
                    results_tqdm = tqdm(api.batch(), desc = f"Results ({site['name']})", total = api.page_size, position = 3)
                    for result in results_tqdm:
                        vprint(1, f"Processing {result.identifier}.", results_tqdm)
                        if result.identifier not in results.keys():
                            results[result.identifier] = result
                        results[result.identifier].add_search_terms(site['name'], query)
                        write_data(results)
                    vprint(1, "Updating status matrix.")
                    status['statuses'][site_id][query_id]['total'] = api.results_total
                    status['statuses'][site_id][query_id]['start'] = api.start
                    status['statuses'][site_id][query_id]['page_size'] = api.page_size
                    status['has_results'][site_id][query_id] = api.has_results()
                    vprint(1, "Estimating remaining batch size.")
                    status['batches'][site_id][query_id] = api.estimate_batches_left()
                    status['max_batches'] = max_runs(status['batches'])
                    if not status['has_results'][site_id][query_id]:
                        status['incomplete'] -= 1
                    write_status(status)
    
    if args.batches > 0:
        for k in trange(args.batches, desc = "Batch", position = 0):
            vprint(1, f"Starting Batch {k + 1}.")
            batch_across()
            vprint(1, f"Completed Batch {k + 1}.")
    else:
        with tqdm(total = status['max_batches'], desc = "Batch", position = 0) as progress:
            k = 0
            while status['incomplete'] > 0:
                vprint(1, f"Starting Batch {k + 1}.")
                batch_across()
                vprint(1, f"Completed Batch {k + 1}.")
                progress.update(1)
                vprint(2, "Updated progress.")
                progress.total = status['max_batches']
                vprint(2, f"Updated estimated batches.")
                progress.refresh()
                vprint(2, f"Refreshed.")
                k += 1
