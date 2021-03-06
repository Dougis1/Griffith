# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieIMDB.py 1660 2014-03-13 20:48:05Z mikej06 $'

__revision__ = '$Id: PluginMovieIMDB.py 1660 2020-12-13 dougl $'
#               Updated to Gtk 3 2020 by Doug Lindquist

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

import gutils, movie
import string, re, math
import urllib3
from bs4 import BeautifulSoup
from imdb import IMDb
import locale
import pycountry

plugin_name         = 'IMDb'
plugin_description  = 'Internet Movie Database'
plugin_url          = 'www.imdb.com'
plugin_language     = _('English')
plugin_author       = 'Doug Lindquist'
plugin_author_email = 'doug.lindquist@protonmail.com'
plugin_version      = '1.20'

ul3 = urllib3.PoolManager()

class Plugin(movie.Movie):
    mvie = None
    company = None

    def __init__(self, id):
        self.encode   = 'utf-8'
        self.movie_id = id
        self.url      = "http://imdb.com/title/tt%s" % self.movie_id

    def initialize(self):
#        self.cast_page = self.open_page(url=self.url + '/fullcredits')
#        self.plot_page = self.open_page(url=self.url + '/plotsummary')
#        self.comp_page = self.open_page(url=self.url + '/companycredits')
#        self.tagl_page = self.open_page(url=self.url + '/taglines')
#        self.cert_page = self.open_page(url=self.url + '/parentalguide')
#        self.release_page = self.open_page(url=self.url + '/releaseinfo')
        ia = IMDb()
        self.mvie = ia.get_movie(self.movie_id)
#        company = ia.get_company(self.movie_id)

    def get_barcode(self):
        try:
            if 'barcode' in self.mvie:
                self.barcode = self.mvie.get('barcode')
            else:
                self.barcode = str('')
        except:
            self.barcode = str('')

    def get_cameraman(self):
        if 'cinematographers' in self.mvie:
            self.cameraman = gutils.listToString(self.mvie['cinematographers'], joiner=', ')
        else:
            self.cameraman = str('')

    def get_cast(self):
        if 'cast' in self.mvie:
            self.cast = ''
            actors = self.mvie['cast']
            for actor in actors:
#                try:
                role = actor.currentRole
                if role is None or role == '' or len(role) == 0:
                    line = actor['name'] + '\n'
                else:
                    line = ("%s as %s\n" % (actor['name'], role))

#                except:
#                    line = '\n'

                self.cast += line
        else:
            self.cast = str('')

    def get_classification(self):
        if 'rating' in self.mvie:
            try:
                self.classification = self.mvie['rating']
                loc = locale.getlocale()[0][3:]
                res = pycountry.countries.search_fuzzy(loc)
                cntry = res[0].name
                cert = ''
                c = self.mvie['certificates']
                if c is not None:
                    for a in c:
                        if a.startswith(cntry):
                            a,b = a.split(':')
                            cert = b
                            break
                else:
                    cert = str('')
            except:
                cert = str('')

            self.classification = cert
        else:
            self.classification = str('')

    def get_color(self):
        if 'color info' in self.mvie:
            try:
                c = self.mvie['color info']
                self.color = ''
                if not c:
                    self.color = gutils.listToString(c, joiner=', ')
            except:
                self.color = str('')
        else:
            self.color = str('')

    def get_country(self):
        if 'countries' in self.mvie:
            self.country = gutils.listToString(self.mvie['countries'], joiner=', ')
        else:
            self.country = str('')

    def get_director(self):
        if 'directors' in self.mvie:
            try:
                if self.mvie['directors']:
                    self.director = gutils.listToString(self.mvie['directors'], joiner=', ')
                else:
                    self.director = str('')
            except:
                self.director = str('')
        else:
            self.director = str('')

    def get_genre(self):
        if 'genres' in self.mvie:
            self.genre = gutils.listToString(self.mvie['genres'], joiner=' | ')
        else:
            self.genre = str('')

    def get_image(self):
        if 'cover url' in self.mvie and self.mvie['cover url']:
            self.image_url = self.mvie['cover url']
        elif 'full-size cover url' in self.mvie and self.mvie['full-size cover url']:
            self.image_url = self.mvie['full-size cover url']
        else:
            self.image_url = str('')

    def get_language(self):
        if 'languages' in self.mvie:
            try:
                languages = self.mvie['languages']
                self.language = ''
                f = False
                for l in languages:
                    if f:
                        self.language += ', ' + l
                    else:
                        self.language += l
                        f = True
            except:
                self.language = str('')
        else:
            self.language = str('')

    def get_notes(self):
        self.notes = ''
        self.get_color()
        self.get_sound()
        self.get_language()
        self.get_tagline()

        if self.language and len(self.language) > 0:
            self.notes = "%s: %s\n" %(_('Language'), self.language)

        if self.sound and len(self.sound) > 0:
            self.notes += "%s: %s\n" %(gutils.strip_tags(_('<b>Audio</b>')), self.sound)

        if self.color and len(self.color) > 0:
            self.notes += "%s: %s\n" %(_('Color'), self.color)

        if self.tagline and len(self.tagline) > 0:
            self.notes += "%s: %s\n" %(_('Tagline'), self.tagline)

    def get_o_site(self):
        self.o_site = str('')

    def get_o_title(self):
        try:
            self.o_title = self.mvie['original title']
        except:
            self.o_title = str('')

    def get_plot(self):
        if 'plot' in self.mvie:
            try:
                a = self.mvie['plot']
                b = a[0]
                if '::' in b:
                    self.plot = b.split('::')[0]
                else:
                    self.plot = b
            except:
                self.plot = str('')
        else:
            self.plot = str('')

    def get_rating(self):
        if 'rating' in self.mvie:
            try:
                self.rating = self.mvie['rating']
                if self.rating:
                    try:
                        self.rating = math.trunc(float(self.rating) + 0.5)
                    except Exception as e:
                        self.rating = 0
                else:
                    self.rating = 0
            except:
                self.rating = 0
        else:
            self.ratinf = 0

#    def get_resolution(self):
#        self.resolution = mvie

    def get_runtime(self):
        if 'runtimes' in self.mvie:
            self.runtime = self.mvie['runtimes'][0]
        else:
            self.runtime = '0'

    def get_screenplay(self):
        if 'writer' in self.mvie:
            try:
                w = self.mvie['writer']
                self.screenplay = gutils.listToString(w, joiner=', ')
            except:
                self.screenplay = str('')
        else:
            self.screenplay = str('')

    def get_site(self):
        self.site = "http://www.imdb.com/title/tt%s" % self.movie_id

    def get_sound(self):
        if 'sound mix' in self.mvie:
            try:
                sm = self.mvie['sound mix']
                self.sound = gutils.listToString(sm, ', ')
            except:
                self.sound = str('')
        else:
            self.sound = str('')

    def get_studio(self):
        if 'studio' in self.mvie:
            self.studio = self.mvie.get('studio')
        else:
            self.studio = str('')

    def get_tagline(self):
        if 'taglines' in self.mvie:
            self.tagline = self.mvie.get('taglines')
        else:
            self.tagline =str('')

    def get_title(self):
        if 'title' in self.mvie:
            self.title = self.mvie['title']
        else:
            self.title = str('')

    def get_trailer(self):
        self.trailer = "http://www.imdb.com/title/tt%s/trailers" % self.movie_id

    def get_year(self):
        if 'year' in self.mvie:
            self.year = str(self.mvie['year'])
        else:
            self.year = '1900'


#https://www.imdb.com/find?s=tt&q=matrix
#https://www.imdb.com/find?q=matrix&s=tt&exact=true&ref_=fn_tt_ex
#https://www.imdb.com/find?q=matrix&s=tt&ref_=fn_tt_pop
class SearchPlugin(movie.SearchMovie):
#    PATTERN = re.compile(r"""<a href=['"]/title/tt([0-9]+)/[^>]+[>](.*?)</td>""")
#    PATTERN_DIRECT = re.compile(r"""value="/title/tt([0-9]+)""")

    def __init__(self):
        # http://www.imdb.com/List?words=
        # finds every title sorted alphabetically, first results are with a quote at
        # the beginning (episodes from tv series), no popular results at first
        # http://www.imdb.com/find?more=tt;q=
        # finds a whole bunch of results. if you look for "Rocky" you will get 903 results.
        # http://www.imdb.com/find?s=tt;q=
        # seems to give the best results. 88 results for "Rocky", popular titles first.
        self.original_url_search   = 'http://www.imdb.com/find?s=tt&q='
        self.translated_url_search = 'http://www.imdb.com/find?s=tt&q='
        self.encode                = 'utf8'

    def search(self, parent_window):
        url = self.original_url_search + self.title
        try:
            r = ul3.request('GET', url)
            self.page = r.data
            return True
        except:
            print("search failed for %s" % url)
            self.page = ''
            return None

    def get_searches(self):
        self.ids.clear()
        self.titles.clear()
        soup = BeautifulSoup(self.page, 'html.parser')
        for i in soup.find_all('td', class_='result_text'):
            link = i.find('a')['href']
            link1 = link.split('/')[2][2:]
            name = i.text
            self.ids.append(link1)
            self.titles.append(name)

#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa'         : [ 10, 10 ],
        'Ein glückliches Jahr' : [ 3, 3 ]
    }

class PluginTest:
    #
    # Configuration for automated tests:
    # dict { movie_id -> dict { arribute -> value } }
    #
    # value: * True/False if attribute only should be tested for any value
    #        * or the expected value
    #
    test_configuration = {
        '0138097' : {
            'title'             : 'Shakespeare in Love',
            'o_title'           : 'Shakespeare in Love',
            'director'          : 'John Madden',
            'plot'              : True,
            'cast'              : 'Geoffrey Rush' + _(' as ') + 'Philip Henslowe\n\
Tom Wilkinson' + _(' as ') + 'Hugh Fennyman\n\
Steven O\'Donnell' + _(' as ') + 'Lambert\n\
Tim McMullan' + _(' as ') + 'Frees (as Tim McMullen)\n\
Joseph Fiennes' + _(' as ') + 'Will Shakespeare\n\
Steven Beard' + _(' as ') + 'Makepeace - the Preacher\n\
Antony Sher' + _(' as ') + 'Dr. Moth\n\
Patrick Barlow' + _(' as ') + 'Will Kempe\n\
Martin Clunes' + _(' as ') + 'Richard Burbage\n\
Sandra Reinton' + _(' as ') + 'Rosaline\n\
Simon Callow' + _(' as ') + 'Tilney - Master of the Revels\n\
Judi Dench' + _(' as ') + 'Queen Elizabeth\n\
Bridget McConnell' + _(' as ') + 'Lady in Waiting (as Bridget McConnel)\n\
Georgie Glen' + _(' as ') + 'Lady in Waiting\n\
Nicholas Boulton' + _(' as ') + 'Henry Condell\n\
Gwyneth Paltrow' + _(' as ') + 'Viola De Lesseps\n\
Imelda Staunton' + _(' as ') + 'Nurse\n\
Colin Firth' + _(' as ') + 'Lord Wessex\n\
Desmond McNamara' + _(' as ') + 'Crier\n\
Barnaby Kay' + _(' as ') + 'Nol\n\
Jim Carter' + _(' as ') + 'Ralph Bashford\n\
Paul Bigley' + _(' as ') + 'Peter - the Stage Manager\n\
Jason Round' + _(' as ') + 'Actor in Tavern\n\
Rupert Farley' + _(' as ') + 'Barman\n\
Adam Barker' + _(' as ') + 'First Auditionee\n\
Joe Roberts' + _(' as ') + 'John Webster\n\
Harry Gostelow' + _(' as ') + 'Second Auditionee\n\
Alan Cody' + _(' as ') + 'Third Auditionee\n\
Mark Williams' + _(' as ') + 'Wabash\n\
David Curtiz' + _(' as ') + 'John Hemmings\n\
Gregor Truter' + _(' as ') + 'James Hemmings\n\
Simon Day' + _(' as ') + 'First Boatman\n\
Jill Baker' + _(' as ') + 'Lady De Lesseps\n\
Amber Glossop' + _(' as ') + 'Scullery Maid\n\
Robin Davies' + _(' as ') + 'Master Plum\n\
Hywel Simons' + _(' as ') + 'Servant\n\
Nicholas Le Prevost' + _(' as ') + 'Sir Robert De Lesseps\n\
Ben Affleck' + _(' as ') + 'Ned Alleyn\n\
Timothy Kightley' + _(' as ') + 'Edward Pope\n\
Mark Saban' + _(' as ') + 'Augustine Philips\n\
Bob Barrett' + _(' as ') + 'George Bryan\n\
Roger Morlidge' + _(' as ') + 'James Armitage\n\
Daniel Brocklebank' + _(' as ') + 'Sam Gosse\n\
Roger Frost' + _(' as ') + 'Second Boatman\n\
Rebecca Charles' + _(' as ') + 'Chambermaid\n\
Richard Gold' + _(' as ') + 'Lord in Waiting\n\
Rachel Clarke' + _(' as ') + 'First Whore\n\
Lucy Speed' + _(' as ') + 'Second Whore\n\
Patricia Potter' + _(' as ') + 'Third Whore\n\
John Ramm' + _(' as ') + 'Makepeace\'s Neighbor\n\
Martin Neely' + _(' as ') + 'Paris / Lady Montague (as Martin Neeley)\n\
The Choir of St. George\'s School in Windsor' + _(' as ') + 'Choir (as The Choir of St. George\'s School Windsor) rest of cast listed alphabetically:\n\
Jason Canning' + _(' as ') + 'Nobleman (uncredited)\n\
Kelley Costigan' + _(' as ') + 'Theatregoer (uncredited)\n\
Rupert Everett' + _(' as ') + 'Christopher Marlowe (uncredited)\n\
John Inman' + _(' as ') + 'Character Player (uncredited)',
            'country'           : 'USA',
            'genre'             : 'Comedy | Drama | Romance',
            'classification'    : False,
            'studio'            : 'Universal Pictures, Miramax Films, Bedford Falls Productions',
            'o_site'            : False,
            'site'              : 'http://www.imdb.com/title/tt0138097',
            'trailer'           : 'http://www.imdb.com/title/tt0138097/trailers',
            'year'              : 1998,
            'notes'             : _('Language') + ': English\n'\
+ _('Audio') + ': Dolby Digital\n'\
+ _('Color') + ': Color\n\
Tagline: ...A Comedy About the Greatest Love Story Almost Never Told...\n\
Love is the only inspiration',
            'runtime'           : 123,
            'image'             : True,
            'rating'            : 7,
            'screenplay'        : 'Marc Norman, Tom Stoppard',
            'cameraman'         : 'Richard Greatrex',
            'barcode'           : False
        },
    }
