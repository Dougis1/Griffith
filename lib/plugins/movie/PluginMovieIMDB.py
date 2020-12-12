# -*- coding: UTF-8 -*-

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

plugin_name         = 'IMDb'
plugin_description  = 'Internet Movie Database'
plugin_url          = 'www.imdb.com'
plugin_language     = _('English')
plugin_author       = 'Doug Lindquist'
plugin_author_email = 'doug.lindquist@protonmail.com'
plugin_version      = '1.20'

class Plugin(movie.Movie):
    from imdb import IMDb
    ia = None
    movie = None

    def __init__(self, id):
        self.encode   = 'utf-8'
        self.movie_id = id
        self.url      = "http://imdb.com/title/tt%s" % self.movie_id
        if not ia:
            ia = IMDb()

    def initialize(self):
        movie = ia.get_movie(self.movie_id)
        company = ia.get_company(self.movie_id)

    def get_image(self):
        try:
            self.image_url = movie['cover url']
            if not self.image_url:
                self.image_url = movie['full-size cover url']
        except:
            self.image_url = ''

    def get_o_title(self):
        self.title = movie['original title']

    def get_title(self):
        self.title = self.movie['title']

    def get_director(self):
        self.director = gutils.listToString(movie['directors'], joiner=', ')

    def get_plot(self):
        self.plot = movie['plot']
        self.plot.replace('\\', '')
        self.plot = self.plot.split('::')[0]

    def get_year(self):
        self.year = movie['year']

    def get_runtime(self):
        self.runtime = movie['runtimes']

    def get_genre(self):
        self.genre = gutils.listToString(movie['genre'], joiner=' | ')

    def get_cast(self):
        self.cast = gutils.listToString(movie['cast'], joiner='\n')

    def get_classification(self):
        # until we can find a way to locate the user, we have to use the US-classification
        self.classification = gutils.trim(self.page, '<meta itemprop="contentRating" content="', '"')
        if not self.classification:
            classificationList = gutils.regextrim(self.cert_page,'id="certifications-list"','<\/ul>')
            if classificationList:
                self.classification = gutils.regextrim(classificationList,'>United States:','<')
            else: # the old way
                self.classification = gutils.trim(self.cert_page, '>Certification:<', '</div>')
                self.classification = gutils.trim(self.classification, '>USA:', '<')

    def get_studio(self):
        self.studio = ''
        tmp = gutils.regextrim(self.comp_page, 'name="production"', '</ul>')
        tmp = string.split(tmp, 'href="')
        if len(tmp)>1:
            for entry in tmp[1:]:
                entry = string.strip(string.replace(gutils.trim(entry, '>', '<'), '\n', ''))
                if entry:
                    self.studio = self.studio + entry + ', '

            if self.studio:
                self.studio = self.studio[:-2]

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = "http://www.imdb.com/title/tt%s" % self.movie_id

    def get_trailer(self):
        self.trailer = "http://www.imdb.com/title/tt%s/trailers" % self.movie_id

    def get_country(self):
        self.country = gutils.listToString(movie['countries'], joiner=', ')

    def get_rating(self):
        self.rating = movie['rating']
        if self.rating:
            try:
                self.rating = math.trunc(float(self.rating) + 0.5)
            except Exception as e:
                self.rating = 0
        else:
            self.rating = 0

    def get_notes(self):
        self.notes = ''
        language = get_language()
        color = movie['color']
        sound = movie['sound mix']

#        tagline = gutils.regextrim(self.tagl_page, '>Taglines', '>See also')
#        taglines = re.split('<div[^>]+class="soda[^>]*>', tagline)
#        tagline = ''
#        if len(taglines)>1:
#            for entry in taglines[1:]:
#                entry = gutils.clean(gutils.before(entry, '</div>'))
#                if entry:
#                    tagline = tagline + entry + '\n'

        if len(language) > 0:
            self.notes = "%s: %s\n" %(_('Language'), language)

        if len(sound) > 0:
            self.notes += "%s: %s\n" %(gutils.strip_tags(_('<b>Audio</b>')), sound)

        if len(color) > 0:
            self.notes += "%s: %s\n" %(_('Color'), color)

#        if len(tagline) > 0:
#            self.notes += "%s: %s\n" %('Tagline', tagline)

    def get_screenplay(self):
        self.screenplay = movie['writer']

    def get_cameraman(self):
        self.cameraman = ''
        tmp = gutils.regextrim(self.cast_page, '>Cinematography by', '</table>')
        tmp = string.split(tmp, 'href="')
        if len(tmp) > 1:
            for entry in tmp[1:]:
                entry = string.strip(string.replace(gutils.trim(entry, '>', '<'), '\n', ''))
                if entry:
                    self.cameraman = self.cameraman + entry + ', '
            if self.cameraman:
                self.cameraman = self.cameraman[:-2]

    def __before_more(self, data):
        for element in ['>See more<', '>more<', '>Full summary<', '>Full synopsis<']:
            tmp = string.find(data, element)
            if tmp>0:
                data = data[:tmp] + '>'
        return data

class SearchPlugin(movie.SearchMovie):
    PATTERN = re.compile(r"""<a href=['"]/title/tt([0-9]+)/[^>]+[>](.*?)</td>""")
    PATTERN_DIRECT = re.compile(r"""value="/title/tt([0-9]+)""")
    movies = [""]

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

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None

        movies = ia.search_movie(self.title)
        print("2 %d" % len(movies))
        return len(movies)

    def get_searches(self):
        print("1 %s" % self.title)
        movies = ia.search_movie(self.title)
        print("5 %d" % len(movies))
        for m in movies:
            ids.append(m.movieID)
            titles.append(m['title'])
        print("6 %d" % len(ids))

        if len(ids) < 2:
            # try to find a direct result
            match = self.PATTERN_DIRECT.findall(self.page)
            if len(match) > 0:
                ids.append(match[0])
            else:
                # try to look for IMDb id directly
                if len(self.title) == 7 and re.match('[0-9]+', self.title):
                    ids.append(self.title)

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
