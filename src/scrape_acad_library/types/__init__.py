#!/usr/bin/env python
# coding: utf-8

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
            self.search_terms.append(search_terms)
        else:
            self.search_terms[source] = [search_terms]

    @abstractmethod
    def venue(self):
        raise NotImplementedError("Must define venue getter.")
            
class Article(Publication):
    def __init__(self, identifier, title, authors, year, journal, volume, issue, abstract = None, pages = None):
        super().__init__(identifier, title, authors, year)
        self.journal = journal
        self.volume = volume
        self.issue = issue
        self.abstract = abstract
        self.pages = pages

    def venue(self):
        return self.journal

class Conference(Publication):
    def __init__(self, identifier, title, authors, year, book_title, conference, abstract = None, pages = None):
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

class Book(Publication):
    def __init__(self, identifier, title, authors, year, abstract = None):
        super().__init__(identifier, title, authors, year)
        self.abstract = abstract

    def venue(self):
        return self.title
        
class BookChapter(Publication):
    def __init__(self, identifier, title, authors, year, book_title, abstract = None, pages = None):
        super().__init__(identifier, title, authors, year)
        self.book_title = book_title
        self.abstract = abstract
        self.pages = pages

    def venue(self):
        return self.book_title
