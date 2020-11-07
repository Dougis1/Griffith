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
from urllib3 import *
from bs4 import BeautifulSoup
import certifi
#from cStringIO import StringIO
from PIL import Image
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
import gutils

log = logging.getLogger("Griffith2")


class Movie(object):
    cast = None
    classification = None
    country = None
    director = None
    genre = None
    image = None
    notes = None
    number = None
    o_site = None
    o_title = None
    plot = None
    rating = None
    runtime = None
    site = None
    studio = None
    title = None
    trailer = None
    year = None
    screenplay = None
    cameraman = None
    resolution = None
    barcode = None

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
    encode = 'iso-8859-1'
    fields_to_fetch = []
    progress = None
    useurllib2 = False

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

    def get_country(self):
        pass

    def get_director(self):
        pass

    def get_genre(self):
        pass

    def get_image(self):
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

    def get_studio(self):
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
        try:
            # check for internet connection
            r = http.request('GET', 'http://www.google.com')
#            urllib.request.urlopen("http://www.google.com")
            #
            # initialize the progress dialog once for the following loading process
            #
            if self.progress is None:
                self.progress = Progress(parent_window)

            self.progress.set_data(parent_window, _("Fetching data"), _("Wait a moment"), True)
            #
            # get the page
            #
            if not self.open_page(parent_window):
                return None

            return True

        except:
            self.progress.hide()
            gutils.error(_("Connection failed."))
            return False

    def open_page(self, parent_window=None, url=None):
        if url is None:
            url_to_fetch = self.url
        else:
            url_to_fetch = url

        if parent_window is not None:
            self.parent_window = parent_window

        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        data = None
#        f = urllib3.urlopen(url_to_fetch)
        f = self.http.request('GET', url_to_fetch, preload_content=False)
#        data = BeautifulSoup(f)
        while True:
            z = resp.read(8192)
            if not z:
                break

            data += str(z)

        f.release_conn()
#        soup = BeautifulSoup(data, "html.parser")

        if url is None:
            self.page = data

        urlcleanup()
        return data

    def fetch_picture(self):
        if self.image_url:
            tmp_dest = tempfile.mktemp(prefix='poster_', dir=self.locations['temp'])
            self.image = tmp_dest.split('poster_', 1)[1]
            dest = "%s.jpg" % tmp_dest
            try:
                http = urllib3.PoolManager()
                r = http.request('GET', self.image_url)
                data = r.data
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

            if 'year' in fields:
                self.get_year()
                self.year = gutils.digits_only(self.year, 2100)
                fields.pop(fields.index('year'))
            if 'runtime' in fields:
                self.get_runtime()
                self.runtime = gutils.digits_only(self.runtime)
                fields.pop(fields.index('runtime'))
            if 'rating' in fields:
                self.get_rating()
                self.rating = gutils.digits_only(self.rating, 10)
                fields.pop(fields.index('rating'))
            if 'cast' in fields:
                self.get_cast()
                self.cast = gutils.clean(self.cast)
                if not isinstance(self.cast, str):
                    self.cast = gutils.gdecode(self.cast, self.encode)
                fields.pop(fields.index('cast'))
            if 'plot' in fields:
                self.get_plot()
                self.plot = gutils.clean(self.plot)
                if not isinstance(self.plot, str):
                    self.plot = gutils.gdecode(self.plot, self.encode)
                fields.pop(fields.index('plot'))
            if 'notes' in fields:
                self.get_notes()
                self.notes = gutils.clean(self.notes)
                if not isinstance(self.notes, str):
                    self.notes = gutils.gdecode(self.notes, self.encode)
                fields.pop(fields.index('notes'))
            if 'image' in fields:
                self.get_image()
                self.fetch_picture()
                fields.pop(fields.index('image'))

            for i in fields:
                getattr(self, "get_%s" % i)()
                self[i] = gutils.clean(self[i])
                if not isinstance(self[i], str):
                    self[i] = gutils.gdecode(self[i], self.encode)

            if 'o_title' in self.fields_to_fetch and self.o_title is not None:
                if self.o_title[:4] == 'The ':
                    self.o_title = self.o_title[4:] + ', The'

            if 'title' in self.fields_to_fetch and self.title is not None:
                if self.title[:4] == 'The ':
                    self.title = self.title[4:] + ', The'
        except:
            log.exception('')
        finally:
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
    useurllib2 = False
    usepostrequest = False

    def __init__(self):
        pass

    def search_movies(self, parent_window):
        try:
            #
            # initialize the progress dialog once for the following search process
            #
            if self.progress is None:
                self.progress = Progress(parent_window)

            self.progress.set_data(parent_window, _("Searching"), _("Wait a moment"), True)
            #
            # call the plugin specific search method
            #
            return self.search(parent_window)
        finally:
            # dont forget to hide the progress dialog
            self.progress.hide()

    def open_search(self, parent_window, destination=None):
        self.titles = [""]
        self.ids = [""]
        if self.url.find('%s') > 0:
            self.url = self.url % self.title
            self.url = string.replace(self.url, ' ', '%20')
        else:
            if not self.usepostrequest:
                self.url = string.replace(self.url + self.title, ' ', '%20')

        try:
            url = self.url.encode(self.encode)
        except UnicodeEncodeError:
            url = self.url.encode('utf-8')

        self.progress.set_data(parent_window, _("Searching"), _("Wait a moment"), True)
        if self.usepostrequest:
            postdata = self.get_postdata()
            retriever = Retriever(url, parent_window, self.progress, destination, useurllib2=self.useurllib2, postdata=postdata)
        else:
            retriever = Retriever(url, parent_window, self.progress, destination, useurllib2=self.useurllib2)

        retriever.start()
        while retriever.isAlive():
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
                    self.page = self.page    ##.decode(self.encode, 'replace')
                else:
                    return False
            else:
                self.progress.hide()
                gutils.urllib_error(_("Connection error"), parent_window)
                return False
        except IOError:
            log.exception('')
        finally:
            urlcleanup()

        return True

    def get_postdata(self):
        # sample, depends on target site
        #return {'title' : self.Title, 'category' : 'movieTitel' }
        return {}


class Retriever(threading.Thread):

    def __init__(self, URL, parent_window, progress, destination=None, useurllib3=False, postdata=None):
        self.URL = URL
        self.html = None
        self.exception = None
        self.destination = destination
        self.useurllib3 = useurllib3
        self.progress = progress
        self._stopevent = threading.Event()
        self._sleepperiod = 1.0
        self.postdata = postdata
        threading.Thread.__init__(self, name="Retriever")

    def run(self):
        try:
            if self.useurllib3:
                if self.postdata:
                    encodedpostdata = urlencode(self.postdata)
                    self.html = urlretrieve2(self.URL, self.destination, self.hook, encodedpostdata)
                else:
                    self.html = urlretrieve2(self.URL, self.destination, self.hook)
            else:
                if self.postdata:
                    encodedpostdata = urlencode(self.postdata)
                    self.html = urlretrieve(self.URL, self.destination, self.hook, encodedpostdata)
                else:
                    self.html = urlretrieve(self.URL, self.destination, self.hook)
            if self.progress.status:
                self.html = []
        except Exception as e:
            log.exception('')
            self.exception = e

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


def urlretrieve(url, filename=None, reporthook=None, data=None):
    global _uaurlopener
    if not _uaurlopener:
        _uaurlopener = UAFancyURLopener()

    return _uaurlopener.retrieve(url, filename, reporthook, data)


def urlretrieve2(url, filename=None, reporthook=None, data=None):
    global _tempfilecleanup
    headers = {
        #'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MSAppHost/1.0)',
        #'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.2.2; Nexus 4 Build/JDQ39E)'
        'User-Agent': 'Dalvik/1.2.0 (Linux; U; Android 2.2.2; Huawei U8800-51 Build/HWU8800B635)',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip'}
    req = urllib.request.Request(url, data, headers)
    response = urllib.request.urlopen(req)
    if not filename:
        import tempfile
        (fd, filename) = tempfile.mkstemp()
        if not _tempfilecleanup:
            _tempfilecleanup = TempFileCleanup()
        _tempfilecleanup._tempfiles.append(filename)
        tfp = os.fdopen(fd, 'wb')
    else:
        tfp = file(filename, 'wb')

    while 1:
        block = response.read(4096)
        if block == "":
            break
        tfp.write(block)

    tfp.close()
    return [filename, response.info()]


#class UAFancyURLopener(FancyURLopener):
#    # use Firefox 3.0 User-Agent string from Windows XP
#    version = 'Mozilla/5.0 (X11; Fedora; Linux x64; rv:66.0) Gecko/20190501 Firefox/66.0'

#    def __init__(self, *args, **kwargs):
#        FancyURLopener.__init__(self, *args, **kwargs)
        # additional HTTP headers to work around the html file compression which
        # is used by UMTS connections. compression breaks the movie import plugins sometimes
#       self.addheaders.append(('Cache-Control', 'no-cache'))
#        self.addheaders.append(('Pragma', 'no-cache'))

#    def open(self, fullurl, data=None):
        # prevent blocking calls which doesn't come back
#        import socket
#        socket.setdefaulttimeout(20)
#        return FancyURLopener.open(self, fullurl, data)


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
        self.dialog = Gtk.Dialog(title, window, Gtk.DIALOG_MODAL, ())
        self.dialog.set_urgency_hint(False)
        self.label = Gtk.Label()
        self.label.set_markup(message)
        self.dialog.vbox.pack_start(self.label)
        self.progress = Gtk.ProgressBar()
        self.progress.set_pulse_step(0.01)
        self.dialog.vbox.pack_start(self.progress, False, False)
        self.button = Gtk.Button(_("Cancel"), Gtk.STOCK_CANCEL)
        self.button.connect("clicked", self.callback)
        self.dialog.vbox.pack_start(self.button, False, False)
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
