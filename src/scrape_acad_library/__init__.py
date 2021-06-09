#!/usr/bin/env python
# coding: utf-8

apis = {}

def register_api(names, api):
    global apis
    for name in names:
        apis[name] = api

def make_api(name, api_key):
    global apis
    try:
        api = apis[name]
        return api(api_key = api_key)
    except KeyError:
        return None
        
from .springer import SpringerNature
register_api([ 'springer',
               'springer_link',
               'springer-link',
               'springer_nature',
               'springer-nature' ],
             SpringerNature)

from .ieeexplore import IEEEXplore
register_api([ 'ieee',
               'ieeexplore',
               'ieee_xplore',
               'ieee-xplore',
               'xplore' ],
             IEEEXplore)

from .science_direct import ScienceDirect
register_api([ 'science-direct',
               'sciencedirect',
               'elsevier' ],
             ScienceDirect)
