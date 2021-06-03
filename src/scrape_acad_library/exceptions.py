#!/usr/bin/env python
# coding: utf-8

class UnknownQueryParameter(Exception):
    def __init__(self, query_parameter, message = "The provided query parameter is not known."):
        self.query_parameter = query_parameter
        self.message = message
        super().__init__(self.message)
