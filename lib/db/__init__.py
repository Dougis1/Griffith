# -*- coding: UTF-8 -*-
# vim: fdm=marker
__revision__ = '$Id: __init__.py 1449 2010-09-29 21:03:04Z mikej06 $'
__version__ = 6 # XXX: database format version, remember to increase after changing data structures

# Copyright © 2009 Piotr Ożarowski
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from sqlalchemy import MetaData, func, select, and_
from sqlalchemy.orm import mapper, relation, deferred, column_property, synonym

metadata = MetaData()
import tables # *after* metadata initialization
from _objects import *


mapper(Configuration, tables.configuration)
mapper(Volume, tables.volumes, order_by=tables.volumes.c.name, properties={
    'loaned': synonym('_loaned', map_column=True),
    'movies': relation(Movie, backref='volume')})
mapper(Collection, tables.collections, order_by=tables.collections.c.name, properties={
    'loaned': synonym('_loaned', map_column=True),
    'movies': relation(Movie, backref='collection')})
mapper(Medium, tables.media, properties={
    'movies': relation(Movie, backref='medium')})
mapper(Ratio, tables.ratios, properties={
    'movies': relation(Movie, backref='ratio')})
mapper(VCodec, tables.vcodecs, properties={
    'movies': relation(Movie, backref='vcodec')})
mapper(Person, tables.people, properties={
    'loans': relation(Loan, backref='person', cascade='all, delete-orphan'),
    'loaned_movies_count': column_property(select(
        [func.count(tables.loans.c.loan_id)],
        and_(tables.people.c.person_id == tables.loans.c.person_id,
             tables.loans.c.return_date == None))\
        .label('loaned_movies_count'), deferred=True),
    'returned_movies_count': column_property(select( # AKA loan history
        [func.count(tables.loans.c.loan_id)],
        and_(tables.people.c.person_id == tables.loans.c.person_id,
             tables.loans.c.return_date != None))\
        .label('returned_movies_count'), deferred=True)})
mapper(MovieLang, tables.movie_lang, primary_key=[tables.movie_lang.c.ml_id], properties={
    'movie': relation(Movie),
    'language': relation(Lang),
    'achannel': relation(AChannel),
    'acodec': relation(ACodec),
    'subformat': relation(SubFormat)})
mapper(ACodec, tables.acodecs, properties={
    'movielangs': relation(MovieLang)})
mapper(AChannel, tables.achannels, properties={
    'movielangs': relation(MovieLang)})
mapper(SubFormat, tables.subformats, properties={
    'movielangs': relation(MovieLang)})
mapper(Lang, tables.languages, properties={
    'movielangs': relation(MovieLang)})
mapper(MovieTag, tables.movie_tag)
mapper(Tag, tables.tags, properties={'movietags': relation(MovieTag, backref='tag')})
mapper(Loan, tables.loans, properties={
    'volume': relation(Volume),
    'collection': relation(Collection)})
mapper(Movie, tables.movies, order_by=tables.movies.c.number, properties={
    'loans': relation(Loan, backref='movie', cascade='all, delete-orphan'),
    #'tags': relation(Tag, cascade='all, delete-orphan', secondary=movie_tag,
    'tags': relation(Tag, secondary=tables.movie_tag,
                     primaryjoin=tables.movies.c.movie_id == tables.movie_tag.c.movie_id,
                     secondaryjoin=tables.movie_tag.c.tag_id == tables.tags.c.tag_id),
    'languages': relation(MovieLang, cascade='all, delete-orphan')})
mapper(Poster, tables.posters, properties={
    'movies': relation(Movie),
    'data': deferred(tables.posters.c.data)})
mapper(Filter, tables.filters)
