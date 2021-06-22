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

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(name="qal-swflint",
      version="1.0.0",
      description="A tool for systematically querying various academic publishing databases.",
      long_description = long_description,
      long_description_content_type="text/markdown",
      author="Samuel W. Flint",
      author_email="swflint@flintfam.org",
      license="MIT",
      url="https://github.com/swflint/qal",
      download_url='https://github.com/swflint/qal/archive/v1.0.0.tar.gz',
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
      ],
      keywords=['LITERATURE REVIEW', 'ACADEMIC', 'BIBLIOGRAPHY'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9'
      ])
