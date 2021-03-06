# -*- coding: UTF-8 -*-

__revision__ = '$Id: movie.py 1655 2019-05-12 21:52:22Z DougL $'
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
import os
import string
import sys
import tempfile
import threading
import time
#from urllib import *
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import gutils
import requests
import urllib3
from bs4 import BeautifulSoup
#import certifi
#from PIL import Image

log = logging.getLogger("Griffith")
ul3 = None


class Movie(object):
    barcode = None
    cameraman = None
    cast = None
    classification = None
    color = None
    country = None
    director = None
    genre = None
    image = None
    languages = None
    notes = None
    number = None
    o_site = None
    o_title = None
    plot = None
    rating = None
    resolution = None
    runtime = None
    screenplay = None
    site = None
    sound = None
    studio = None
    tagline = None
    title = None
    trailer = None
    year = None

    movie_id = None
    debug = False
    locations = None
    engine_author = None
    engine_description = None
    engine_language = None
    engine_name = None
    engine_version = None
    page = None
    url = None
    image_url = None
    encode = 'utf-8'
    fields_to_fetch = []
    progress = None
    useurllib3 = False

    # functions that plugin should implement: {{{
    def initialize(self):
        pass

    def get_barcode(self):
        pass

    def get_cameraman(self):
        pass

    def get_cast(self):
        pass

    def get_classification(self):
        pass

    def get_color(self):
        pass

    def get_country(self):
        pass

    def get_director(self):
        pass

    def get_genre(self):
        pass

    def get_image(self):
        pass

    def get_language(self):
        pass

    def get_notes(self):
        pass

    def get_o_site(self):
        pass

    def get_o_title(self):
        pass

    def get_plot(self):
        pass

    def get_rating(self):
        pass

    def get_resolution(self):
        pass

    def get_runtime(self):
        pass

    def get_screenplay(self):
        pass

    def get_site(self):
        pass

    def get_sound(self):
        pass

    def get_studio(self):
        pass

    def get_tagline(self):
        pass

    def get_title(self):
        pass

    def get_trailer(self):
        pass

    def get_year(self):
        pass
    #}}}

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get_movie(self, parent_window=None):
#        try:
            # check for internet connection
#            ul3.urlopen("http://www.google.com")
#        except:
#            gutils.error(_("Connection failed."))
#            return False

        try:
            # initialize the progress dialog once for the following loading process
            if self.progress is None:
                self.progress = Progress(parent_window)

            self.progress.set_data(parent_window, _("Fetching data"), _("Wait a moment"), True)

            # get the page
            if not self.open_page(parent_window):
                return None

            return True

        except:
            self.progress.hide()
            gutils.error(_("Connection failed."))
            return False

    def open_page(self, parent_window=None, url=None):
        global ul3

        if url is None:
            url_to_fetch = self.url
        else:
            url_to_fetch = url

        if parent_window is not None:
            self.parent_window = parent_window

#        if ul3 is None:
#            ul3 = urllib3.PoolManager()

        data = None
#        r = ul3.request('GET', url_to_fetch)
#        self.page = BeautifulSoup(r.data)
#        r.release_conn()
        self.progress.set_data(parent_window, _("Fetching data"), _("Wait a moment"), False)
        retriever = Retriever(url_to_fetch, self.parent_window, self.progress)
        retriever.start()
        while retriever.isAlive():
            self.progress.pulse()
            if self.progress.status:
                retriever.join()

            while Gtk.events_pending():
                Gtk.main_iteration()

#        data = None
        self.progress.hide()
        return True

    def fetch_picture(self):
        if self.image_url:
            tmp_dest = tempfile.mktemp(prefix='poster_', dir=self.locations['temp'])
            self.image = tmp_dest.split('poster_', 1)[1]
            dest = "%s.jpg" % tmp_dest
            try:
                self.progress.set_data(self.parent_window, _("Fetching poster"), _("Wait a moment"), False)
                retriever = Retriever(self.image_url, self.parent_window, self.progress, dest)
                retriever.start()
                while retriever.isAlive():
                    self.progress.pulse()
                    if self.progress.status:
                        retriever.join()

                    while Gtk.events_pending():
                        Gtk.main_iteration()
#                urlcleanup()
            except:
                log.exception('')
                self.image = ""
                try:
                    os.remove("%s.jpg" % tmp_dest)
                except:
                    log.info("Can't remove %s file" % tmp_dest)
        else:
            self.image = ""

    def parse_movie(self):
        try:
            fields = list(self.fields_to_fetch)  # make a copy
            self.initialize()

            if 'barcode' in fields:
                self.get_barcode()
                fields.pop(fields.index('barcode'))

            if 'cameraman' in fields:
                self.get_cameraman()
                fields.pop(fields.index('cameraman'))

            if 'cast' in fields:
                self.get_cast()
                self.cast = gutils.clean(self.cast)
                fields.pop(fields.index('cast'))

            if 'color' in fields:
                self.get_color()
                fields.pop(fields.index('color'))

            if 'classification' in fields:
                self.get_classification()
                fields.pop(fields.index('classification'))

            if 'country' in fields:
                self.get_country()
                fields.pop(fields.index('country'))

            if 'director' in fields:
                self.get_director()
                fields.pop(fields.index('director'))

            if 'genre' in fields:
                self.get_genre()
                fields.pop(fields.index('genre'))

            if 'image' in fields:
                self.get_image()
                self.fetch_picture()
                fields.pop(fields.index('image'))

            if 'language' in fields:
                self.get_language()
                fields.pop(fields.index('language'))

            if 'notes' in fields:
                self.get_notes()
                self.notes = gutils.clean(self.notes)
                fields.pop(fields.index('notes'))

            if 'o_site' in fields:
                self.get_o_site()
                fields.pop(fields.index('o_site'))

            if 'o_title' in self.fields_to_fetch:
                self.get_o_title()
                if self.o_title is not None:
                    if self.o_title[:4] == u'The ':
                        self.o_title = self.o_title[4:] + u', The'

            if 'plot' in fields:
                self.get_plot()
                self.plot = gutils.clean(self.plot)
#                if not isinstance(self.plot, unicode):
#                    self.plot = gutils.gdecode(self.plot, self.encode)
                fields.pop(fields.index('plot'))

            if 'rating' in fields:
                self.get_rating()
                self.rating = gutils.digits_only(self.rating, 10)
                fields.pop(fields.index('rating'))

            if 'resolution' in fields:
                self.get_resolution()
                fields.pop(fields.index('resolution'))

            if 'runtime' in fields:
                self.get_runtime()
                self.runtime = gutils.digits_only(self.runtime)
                fields.pop(fields.index('runtime'))

            if 'screenplay' in fields:
                self.get_screenplay()
                fields.pop(fields.index('screenplay'))

            if 'site' in fields:
                self.get_site()
                fields.pop(fields.index('site'))

            if 'sound' in fields:
                self.get_sound()
                fields.pop(fields.index('sound'))

            if 'studio' in fields:
                self.get_studio()
                fields.pop(fields.index('studio'))

            if 'tagline' in fields:
                self.get_tagline()
                fields.pop(fields.index('tagline'))

            if 'title' in self.fields_to_fetch:
                self.get_title()
                if self.title is not None:
                    if self.title[:4] == u'The ':
                        self.title = self.title[4:] + u', The'

            if 'trailer' in fields:
                self.get_trailer()
                fields.pop(fields.index('trailer'))

            if 'year' in fields:
                self.get_year()
                self.year = gutils.digits_only(self.year, 2100)
                fields.pop(fields.index('year'))

#            for i in fields:
#                getattr(self, "get_%s" % i)()
#                self[i] = gutils.clean(self[i])
#                if not isinstance(self[i], unicode):
#                    self[i] = gutils.gdecode(self[i], self.encode)
        except:
            log.exception('')
            # close the progress dialog which was opened in get_movie
            self.progress.hide()


class SearchMovie(object):
    page = None
    number_results = None
    titles = []
    ids = []
    url = None
    encode = 'utf-8'
    original_url_search = None
    translated_url_search = None
    elements = None
    title = None
    remove_accents = True
    progress = None
    useurllib3 = False
    usepostrequest = False

    def __init__(self):
        pass

    def search_movies(self, parent_window):
       ans = self.search(parent_window)
       return ans

    def open_search(self, parent_window, destination=None):
        self.titles = [""]
        self.ids = [""]

        try:
            url = self.url.encode(self.encode)
        except UnicodeEncodeError:
            url = self.url.encode('utf-8')

        if self.url.find('%s') > 0:
            self.url = self.url % self.title
            self.url.replace(self.url, ' ', '%20')
        else:
            self.url = self.url + self.title
            self.url.replace(' ', '%20')

        self.progress.set_data(parent_window, _("Searching"), _("Wait a moment"), True)
        retriever = Retriever(url, parent_window, self.progress, destination)

        retriever.start()
        while threading.isAlive():
            self.progress.pulse()
            if self.progress.status:
                retriever.join()

        while Gtk.events_pending():
            Gtk.main_iteration()

        try:
            if retriever.exception is None:
                if destination:
                    # caller gave an explicit destination file
                    # don't care about the content
                    return True
                if retriever.html:
                    ifile = file(retriever.html[0], 'rb')
                    try:
                        self.page = ifile.read()
                    finally:
                        ifile.close()
                    # check for gzip compressed pages before decoding to unicode
                    if len(self.page) > 2 and self.page[0:2] == '\037\213':
                        self.page = gutils.decompress(self.page)
                    self.page = self.page.decode(self.encode, 'replace')
                else:
                    return False
            else:
                self.progress.hide()
                gutils.urllib_error(_("Connection error"), parent_window)
                return False
        except IOError:
            log.exception('')
#        finally:
#            urlcleanup()
        return True


class Retriever(threading.Thread):
    is_alive=False

    def __init__(self, URL, parent_window, progress, destination=None):
        self.URL = URL
        self.html = None
        self.exception = None
        self.destination = destination
        self.progress = progress
        self._stopevent = threading.Event()
        self._sleepperiod = 1.0
        threading.Thread.__init__(self, name="Retriever")

    def isAlive(self):
        global is_alive
        return is_alive

    def run(self):
        global is_alive

        is_alive = True
        try:
            self.html = urlretrieve2(self.URL, self.destination, self.hook)
            if self.progress.status:
                self.html = []
        except Exception as e:
            log.exception('')
            self.exception = e

        is_alive = False
        self.progress.hide()

    def hook(self, count, blockSize, totalSize):
        if totalSize == -1:
            pass
        else:
            try:
                downloaded_percentage = min((count * blockSize * 100) / totalSize, 100)
            except:
                downloaded_percentage = 100

            if count != 0:
                downloaded_kbyte = int(count * blockSize / 1024.0)
                filesize_kbyte = int(totalSize / 1024.0)

#
# use own derived URLopener class because we need to set a correct User-Agent
# string for some web sites. The default is 'Python-urllib/<version>'
# which not all sites accepting. (zelluloid.de for example)
#
_uaurlopener = None
_tempfilecleanup = None


def urlretrieve2(url, filename=None, reporthook=None, data=None):
    global _tempfilecleanup
    req = requests.get(url, stream=True)
    if not filename:
        import tempfile
        (fd, filename) = tempfile.mkstemp()
        if not _tempfilecleanup:
            _tempfilecleanup = TempFileCleanup()

        _tempfilecleanup._tempfiles.append(filename)
        tfp = os.fdopen(fd, 'wb')
    else:
        tfp = open(filename, 'wb')

    while 1:
        try:
            for chunk in req.iter_content(4096):
                tfp.write(chunk)
        except requests.exceptions.StreamConsumedError as e:
            break
        except requests.exceptions.Timeout as e:
            gutils.urllib_error(_("Timeout error getting data"), parent_window)
            break

    tfp.close()
    return filename

class TempFileCleanup:
    _tempfiles = []

    def __init__(self):
        self.__unlink = os.unlink

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        if self._tempfiles:
            for file in self._tempfiles:
                try:
                    self.__unlink(file)
                except OSError:
                    pass
            del self._tempfiles[:]


class Progress:

    def __init__(self, window, title='', message=''):
        self.status = False
        self.dialog = Gtk.Dialog(title, window, Gtk.DialogFlags.MODAL, ())
        self.dialog.set_urgency_hint(False)
        self.label = Gtk.Label()
        self.label.set_markup(message)
        self.dialog.vbox.pack_start(self.label, True, True, 0)
        self.progress = Gtk.ProgressBar()
        self.progress.set_pulse_step(0.01)
        self.dialog.vbox.pack_start(self.progress, False, False, 0)
        self.button = Gtk.Button(_("Cancel"), Gtk.STOCK_CANCEL)
        self.button.connect("clicked", self.callback)
        self.dialog.vbox.pack_start(self.button, False, False, 0)
        self.dialog.show_all()

    def callback(self, widget):
        self.dialog.hide()
        self.status = True

    def pulse(self):
        self.progress.pulse()
        time.sleep(0.01)

    def close(self):
        self.dialog.destroy()

    def hide(self):
        self.dialog.hide()

    def set_data(self, parent_window, title, message, showit):
        #self.dialog.set_parent(parent_window)
        self.dialog.set_title(title)
        self.label.set_markup(message)
        if showit is True:
            self.dialog.show()
