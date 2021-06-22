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

from abc import ABCMeta, abstractmethod


class Publication(metaclass=ABCMeta):
    def __init__(self, identifier, title, authors, year):
        self.search_terms = {}
        self.identifier = identifier
        self.title = title
        self.authors = authors
        self.year = year

    def add_search_terms(self, source, search_terms):
        if source in self.search_terms.keys():
            self.search_terms[source].append(search_terms)
        else:
            self.search_terms[source] = [search_terms]

    def asdict(self):
        return {'identifier': self.identifier,
                'title': self.title,
                'authors': self.authors,
                'year': self.year,
                'search_terms': self.search_terms}

    @abstractmethod
    def venue(self):
        raise NotImplementedError("Must define venue getter.")


class Article(Publication):
    def __init__(self, identifier, title, authors, year, journal, volume, issue, abstract=None, pages=None):
        super().__init__(identifier, title, authors, year)
        self.journal = journal
        self.volume = volume
        self.issue = issue
        self.abstract = abstract
        self.pages = pages

    def venue(self):
        return self.journal

    def asdict(self):
        d = super().asdict()
        d['journal'] = self.journal
        d['volume'] = self.volume
        d['issue'] = self.issue
        d['abstract'] = self.abstract
        d['pages'] = self.pages
        return d


class Conference(Publication):
    def __init__(self, identifier, title, authors, year, book_title, conference, abstract=None, pages=None):
        super().__init__(identifier, title, authors, year)
        self.book_title = book_title
        self.conference = conference
        self.abstract = abstract
        self.pages = pages

    def venue(self):
        if self.conference:
            return self.conference
        else:
            return self.book_title

    def asdict(self):
        d = super().asdict()
        d['book_title'] = self.book_title
        d['conference'] = self.conference
        d['abstract'] = self.abstract
        d['pages'] = self.pages
        return d


class Book(Publication):
    def __init__(self, identifier, title, authors, year, abstract=None):
        super().__init__(identifier, title, authors, year)
        self.abstract = abstract

    def venue(self):
        return self.title

    def asdict(self):
        d = super().asdict()
        d['abstract'] = self.abstract


class BookChapter(Publication):
    def __init__(self, identifier, title, authors, year, book_title, abstract=None, pages=None):
        super().__init__(identifier, title, authors, year)
        self.book_title = book_title
        self.abstract = abstract
        self.pages = pages

    def venue(self):
        return self.book_title

    def asdict(self):
        d = super().asdict()
        d['book_title'] = self.book_title
        d['abstract'] = self.abstract
        d['pages'] = self.pages
        return d
