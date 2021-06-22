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


from setuptools import setup, find_packages

setup(name="qal",
      version="1.0.0",
      description="A tool for systematically querying various academic publishing databases.",
      author="Samuel W. Flint",
      author_email="swflint@flintfam.org",
      license="MIT",
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      scripts=['bin/qal-query',
               'bin/qal-auto'],
      install_requires=[
          "requests",
          "backoff",
          "urllib3",
          "jsonpickle",
          "tqdm"
      ])
