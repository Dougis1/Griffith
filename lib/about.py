# -*- coding: UTF-8 -*-

__revision__ = '$Id: about.py 1519 2011-02-05 15:32:36Z iznogoud $'
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import version
import os
import sys

class AboutDialog:
    """Shows a Gtk about dialog"""
    def __init__(self, locations):
        TRANSLATORS_FILE = os.path.join(locations['share'], 'TRANSLATORS') # remember to encode this file in UTF-8
        IMAGES_DIR = locations['images']

        def _open_url(dialog, link):
            import gutils
            gutils.run_browser(link)
##        Gtk.about_dialog_set_url_hook(_open_url)   no longer valid

        dialog = Gtk.AboutDialog()
        dialog.set_name(version.pname)
        dialog.set_version(version.pversion)
        dialog.set_copyright("Copyright © 2005-2011 Vasco Nunes. Piotr Ożarowski")
        dialog.set_website(version.pwebsite)
        dialog.set_authors([
            _("Main Authors") + ':',
            version.pauthor.replace(', ', '\n') + "\n",
            _("Programmers") + ':',
            'Doug Lindquist <doug.lindquist@protonmail.com>',
            'Jessica Katharina Parth <Jessica.K.P@women-at-work.org>',
            'Michael Jahn <mikej06@hotmail.com>',
            'Ivo Nunes <netherblood@gmail.com>\n',
            _('Contributors') + ':',
            'Christian Sagmueller <christian@sagmueller.net>\n' \
            'Arjen Schwarz <arjen.schwarz@gmail.com>'
        ])
        dialog.set_artists([_("Logo, icon and general artwork " + \
            "by Peek <peekpt@gmail.com>." + \
            "\nPlease visit http://www.peekmambo.com/\n"),
            'seen / unseen icons by dragonskulle <dragonskulle@gmail.com>'
        ])
        data = None
        if os.path.isfile(TRANSLATORS_FILE):
            data = open(TRANSLATORS_FILE).read()
        elif os.path.isfile(TRANSLATORS_FILE+'.gz'):
            from gutils import decompress
            data = decompress(open(TRANSLATORS_FILE + '.gz').read())
        elif os.name == 'posix':
            if os.path.isfile('/usr/share/doc/griffith/TRANSLATORS'):
                data = open('/usr/share/doc/griffith/TRANSLATORS').read()
            elif os.path.isfile('/usr/share/doc/griffith/TRANSLATORS.gz'):
                from gutils import decompress
                data = decompress(open('/usr/share/doc/griffith/TRANSLATORS.gz').read())
        translator_credits = ''
        if data:
            for line in data.split('\n'):
                if line.startswith('* '):
                    lang = line[2:]
                    if _(lang) != lang:
                        line = "* %s:" % _(lang)
                translator_credits += "%s\n" % line
        else:
            translator_credits = _("See TRANSLATORS file")
        dialog.set_translator_credits(translator_credits)
        logo_file = os.path.abspath(os.path.join(IMAGES_DIR, 'griffith.png'))
        logo = GdkPixbuf.Pixbuf.new_from_file(logo_file)
        dialog.set_logo(logo)
        dialog.set_license(_("This program is released under the GNU" + \
                "General Public License.\n" + \
                "Please visit http://www.gnu.org/copyleft/gpl.html for details."))
        dialog.set_comments(version.pdescription)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()
