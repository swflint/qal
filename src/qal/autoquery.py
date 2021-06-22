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

from tqdm import trange, tqdm

import json
import jsonpickle

VERBOSE = 0
STATUS_FILE = ''

LOGGER = logging.getLogger('qal.autoquery')

def make_api_object(site):
    name = site['name']
    api = make_api(name, get_env_var(site['name'], site.get('key')))
    if 'start' in site.keys():
        api.start = site['start']
    if 'page_size' in site.keys():
        api.page_size = site['page_size']
    if 'options' in site.keys():
        api.set_options(site['options'])
    return api


def write_status(status):
    LOGGER.info("Saving status file %s.", STATUS_FILE)
    if osp.exists(STATUS_FILE):
        LOGGER.debug("Retaining backup copy of status file")
        os.replace(STATUS_FILE, f"{STATUS_FILE}.bak")
    with open(STATUS_FILE, 'w') as fd:
        json.dump(status, fd, indent=True)
    LOGGER.debug("Saved status file.")


def restore_query_status(status, api, site_id, query_id):
    status_item = status['statuses'][site_id][query_id]
    if len(status_item.keys()) != 0:
        api.start = status_item['start']
        api.page_size = status_item['page_size']
        api.results_total = status_item['total']


def max_runs(batches):
    max(map(max, batches))


def main():
    parser = ArgumentParser(
        description="Automatically query several academic libraries as defined by a control file.")

    parser.add_argument('--verbose', '-v',
                        help="provide verbose logging",
                        default=0,
                        action='count',
                        dest='verbose')

    parser.add_argument('--plan-file', '-p', metavar="PLAN",
                        type=str,
                        required=True,
                        dest='plan_file')

    parser.add_argument('--status-file', '-s', metavar="STATUS",
                        type=str,
                        required=True,
                        dest='status_file')

    parser.add_argument('--output-file', '-o', metavar="OUT",
                        type=str,
                        required=True,
                        dest='out_file')

    parser.add_argument('--number-batches', '-b', metavar="N",
                        type=int,
                        dest='batches',
                        default=-1)

    args = parser.parse_args()

    logging.getLogger('qal').setLevel((6 - args.verbose)*10)
    
    global STATUS_FILE
    STATUS_FILE = args.status_file

    plan = {}
    LOGGER.info("Loading plan file %s.", args.plan_file)
    with open(args.plan_file, 'r') as fd:
        plan = json.load(fd)

    status = {}
    if osp.exists(args.status_file):
        LOGGER.info("Restoring status.")
        with open(args.status_file, 'r') as fd:
            status = json.load(fd)
        LOGGER.debug("Restored status.")

    results = ResultsStore(args.out_file, saviness=1)

    num_sites = len(plan['sites'])
    num_queries = len(plan['queries'])

    if len(status.keys()) == 0:
        LOGGER.info("Seeding status structure.")
        status['statuses'] = []
        status['has_results'] = []
        status['incomplete'] = num_sites * num_queries
        status['batches'] = []
        status['max_batches'] = 10
        for j in range(num_sites):
            row = []
            has_results = []
            batches = []
            for i in range(num_queries):
                row.append({})
                if plan['sites'][i]['enabled']:
                    has_results.append(True)
                else:
                    has_results.append(False)
                    status['incomplete'] -= 1
                batches.append(10)
            status['statuses'].append(row)
            status['has_results'].append(has_results)
            status['batches'].append(batches)
        LOGGER.debug("Seeded status structure.")

    write_status(status)

    def batch_across():
        sites_tqdm = tqdm(
            enumerate(plan['sites']), desc="Sites", total=num_sites, position=1)
        for site_id, site in sites_tqdm:
            LOGGER.info(f"Starting for site {site['name']}.")
            query_tqdm = tqdm(
                enumerate(plan['queries']), desc="Query", total=num_queries, position=2)
            if not site['enabled']:
                continue
            for query_id, query in query_tqdm:
                LOGGER.info(f"Starting for query number {query_id}")
                if status['has_results'][site_id][query_id]:
                    LOGGER.debug(f"Building API object.")
                    api = make_api_object(site)
                    LOGGER.debug("Setting query parameters.")
                    api.set_query_options(query)
                    LOGGER.debug("Restoring query status.")
                    restore_query_status(status, api, site_id, query_id)
                    results_tqdm = tqdm(
                        api.batch(), desc=f"Results ({site['name']})", total=api.page_size, position=3)
                    for result in results_tqdm:
                        LOGGER.info(f"Processing {result.identifier}.")
                        results.add_item(result, site['name'], query)
                    LOGGER.debug("Updating status matrix.")
                    status['statuses'][site_id][query_id]['total'] = api.results_total
                    status['statuses'][site_id][query_id]['start'] = api.start
                    status['statuses'][site_id][query_id]['page_size'] = api.page_size
                    status['has_results'][site_id][query_id] = api.has_results()
                    LOGGER.debug("Estimating remaining batch size.")
                    status['batches'][site_id][query_id] = api.estimate_batches_left()
                    status['max_batches'] = max_runs(status['batches'])
                    if not status['has_results'][site_id][query_id]:
                        status['incomplete'] -= 1
                    write_status(status)

    if args.batches > 0:
        for k in trange(args.batches, desc="Batch", position=0):
            LOGGER.debug(f"Starting Batch {k + 1}.")
            batch_across()
            LOGGER.debug(f"Completed Batch {k + 1}.")
    else:
        with tqdm(total=status['max_batches'], desc="Batch", position=0) as progress:
            k = 0
            while status['incomplete'] > 0:
                LOGGER.debug(f"Starting Batch {k + 1}.")
                batch_across()
                LOGGER.debug(f"Completed Batch {k + 1}.")
                progress.update(1)
                LOGGER.debug("Updated progress.")
                progress.total = status['max_batches']
                LOGGER.debug(f"Updated estimated batches.")
                progress.refresh()
                LOGGER.debug(f"Refreshed.")
                k += 1
