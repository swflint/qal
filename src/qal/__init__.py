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

import logging
import os
from .springer import SpringerNature
from .science_direct import ScienceDirect
from .ieeexplore import IEEEXplore
__version__ = "1.0.0"

apis = {}

env_var_names = {}

LOGGER = logging.getLogger('qal')

def register_api(names, env_var, api):
    global apis
    global env_var_names
    LOGGER.info("Registering API: %s", api)
    for name in names:
        apis[name] = api
        env_var_names[name] = env_var

def get_env_var(name, key_maybe):
    global env_var_names
    if key_maybe:
        return key_maybe
    elif env_var_names.get(name):
        return os.environ.get(env_var_names.get(name))
    else:
        return os.environ.get('LIBRARY_API_KEY')


def get_env_var_name(name):
    global env_var_names
    return env_var_names.get(name)


def make_api(name, api_key):
    global apis
    global env_var_names
    try:
        api = apis[name]
        return api(api_key=api_key)
    except KeyError:
        return None


register_api(['springer',
              'springer_link',
              'springer-link',
              'springer_nature',
              'springer-nature'],
             'SPRINGER_LINK_API_KEY',
             SpringerNature)

register_api(['ieee',
              'ieeexplore',
              'ieee_xplore',
              'ieee-xplore',
              'xplore'],
             'IEEE_XPLORE_API_KEY',
             IEEEXplore)

register_api(['science-direct',
              'sciencedirect',
              'elsevier'],
             'SCIENCE_DIRECT_API_KEY',
             ScienceDirect)
