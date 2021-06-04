#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

setup(name = "scrape_acad_library",
      version = "0.0.1",
      description = "A tool for systematically querying various academic publishing databases.",
      author = "Samuel W. Flint",
      author_email = "swflint@flintfam.org",
      license = "MIT",
      packages = find_packages(where = "src"),
      package_dir = {"": "src"},
      scripts = [ 'bin/query-acad-library' ],
      install_requires = [
          "requests",
          "backoff",
          "urllib3",
          "jsonpickle"
      ])
