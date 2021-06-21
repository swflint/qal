#!/usr/bin/env python
# coding: utf-8

# This file is a part of `scrape_acad_library`.
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

import jsonpickle
import os.path as osp
import os


class ResultsStore:
    def __init__(self, file_name, saviness=0):
        self.file_name = file_name
        self.saviness = saviness
        if osp.exists(self.file_name):
            with open(self.file_name, 'r') as fd:
                self.data = jsonpickle.decode(fd.read())
        else:
            self.data = {}
        self.num = 0

    def save(self):
        if osp.exists(self.filename):
            os.replace(self.filename, f"{self.filename}.bak")
        with open(self.filename, 'w') as fd:
            fd.write(jsonpickle.encode(self.data))

    def add_item(self, item, source=None, query=None):
        if item.identifier in self.data.keys():
            self.data[item.identifier] = item
        if (source != None) and (query != None):
            self.data[item].add_search_terms(source, query)
        if self.saviness > 0:
            self.num += 1
            if (self.num % self.saviness) == 0:
                self.save()
