# -*- coding: UTF-8 -*-

__revision__ = '$Id: loan.py 1522 2011-02-05 19:59:38Z iznogoud $'
#               Updated to Gtk 3 2020 by Doug Lindquist

# Copyright © 2005-2010 Vasco Nunes, Piotr Ożarowski
# Copyright 2020 Doug Lindquist doug.lindquist@protonmail.com

# Permission is hereby granted, free of charge, to any person obtaining
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import db
import gutils

log = logging.getLogger("Griffith")

def loan_movie(self):
    people = self.db.session.query(db.Person.name).order_by(db.Person.name.asc()).all()
    model = Gtk.ListStore(str)
    if len(people)>0:
        for person in people:
            model.append([person.name])
        self.widgets['movie']['loan_to'].set_model(model)
        self.widgets['movie']['loan_to'].set_text_column(0)
        self.widgets['movie']['loan_to'].set_active(0)
        self.widgets['w_loan_to'].show()
    else:
        gutils.info(_("No person is defined yet."), self.widgets['window'])

def cancel_loan(self):
    self.widgets['w_loan_to'].hide()

def commit(self):
    person_name = gutils.on_combo_box_entry_changed(self.widgets['movie']['loan_to'])
    if not person_name:
        return False
    self.widgets['w_loan_to'].hide()

    session = self.db.Session()

    person = session.query(db.Person.person_id).filter_by(name=person_name).first()
    if not person:
        log.warn("loan_commit: person doesn't exist")
        return False
    if self._movie_id:
        movie = session.query(db.Movie).filter_by(movie_id=self._movie_id).first()
        if not movie:
            log.warn("loan_commit: movie doesn't exist")
            return False
    else:
        log.warn("loan_commit: movie not selected")
        return False

    # ask if user wants to loan whole collection
    loan_whole_collection = False
    if movie.collection_id > 0:
        if gutils.question(_('Do you want to loan the whole collection?'), window=self.widgets['window']):
            loan_whole_collection = True

    try:
        if movie.loan_to(person, whole_collection=loan_whole_collection):
            session.commit()
    except Exception as e:
        session.rollback()
        if e.message == 'loaned movies in the collection already':
            gutils.warning(_("Collection contains loaned movie.\nLoan aborted!"))
            return False
        else:
            raise e

    self.update_statusbar(_("Movie loaned"))
    self.treeview_clicked()

def return_loan(self):
    if not self._movie_id:
        log.warn('return_loan: movie not selected')
        return False

    session = self.db.Session()

    movie = session.query(db.Movie).filter_by(movie_id=self._movie_id).first()
    if not movie or not movie.loan_details:
        log.warn("return_loan: movie or loan doesn't exist (id=%s)", self._movie_id)
        return False
    movie.loan_details.returned_on() # current date will be used be default
    session.commit()
    self.treeview_clicked()
    self.populate_treeview()
