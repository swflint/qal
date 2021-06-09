#!/usr/bin/env python
# coding: utf-8

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
            
