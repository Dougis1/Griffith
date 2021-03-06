# -*- coding: UTF-8 -*-

__revision__ = '$Id: gutils.py 1582 2011-09-04 21:08:14Z piotrek $'
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

import gzip
import html.entities
import logging
import os
import re
import string
import sys
import webbrowser
from io import StringIO
import platform
import config

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GdkPixbuf
    import db
except:
    Gtk = None
    pass

mac = False

if os.name in ('mac') or \
    (hasattr(os, 'uname') and os.uname()[0] == 'Darwin'):
        import macutils
        mac = True

log = logging.getLogger("Griffith")

ENTITY = re.compile(r'\&.\w*?\;')


def remove_accents(txt, encoding='iso-8859-1'):
#    d = {192: u'A', 193: u'A', 194: u'A', 195: u'A', 196: u'A', 197: u'A',
#         199: u'C', 200: u'E', 201: u'E', 202: u'E', 203: u'E', 204: u'I',
#         205: u'I', 206: u'I', 207: u'I', 209: u'N', 210: u'O', 211: u'O',
#         212: u'O', 213: u'O', 214: u'O', 216: u'O', 217: u'U', 218: u'U',
#         219: u'U', 220: u'U', 221: u'Y', 224: u'a', 225: u'a', 226: u'a',
#         227: u'a', 228: u'a', 229: u'a', 231: u'c', 232: u'e', 233: u'e',
#         234: u'e', 235: u'e', 236: u'i', 237: u'i', 238: u'i', 239: u'i',
#         241: u'n', 242: u'o', 243: u'o', 244: u'o', 245: u'o', 246: u'o',
#         248: u'o', 249: u'u', 250: u'u', 251: u'u', 252: u'u', 253: u'y',
#         255: u'y'}
#    return unicode(txt, encoding).translate(d)
        return txt


def is_number(x):
    return isinstance(x, int)


def find_next_available(gsql):
    """
    finds next available movie number.
    This is the first empty position.
    If none is empty then increments the last position.
    """
    first = 0

    movies = gsql.session.query(db.Movie.number).order_by(db.Movie.number.asc()).all()
    for movie in movies:
        second = int(movie.number)
        if second is None:
            second = 0
        if second > first + 1:
            break
        first = second

    if first is None:
        return 1
    else:
        number = first + 1
        return number


def trim(text, key1, key2):
    p1 = string.find(text, key1)
    if p1 == -1:
        return ''
    else:
        p1 = p1 + len(key1)

    p2 = string.find(text[p1:], key2)
    if p2 == -1:
        return ""
    else:
        p2 = p1 + p2

    return text[p1:p2]

def rtrim(text, key1, key2):
    p1 = string.rfind(text, key2)
    if p1 == -1:
        return ''

    p2 = string.rfind(text[:p1], key1)
    if p2 == -1:
        return ""
    else:
        p2 = p2 + len(key1)

    return text[p2:p1]

def regextrim(text, key1, key2):
    obj = re.search(key1, text)
    if obj is None:
        return ''
    else:
        p1 = obj.end()

    obj = re.search(key2, text[p1:])
    if obj is None:
        return ''
    else:
        p2 = p1 + obj.start()

    return text[p1:p2]


def after(text, key):
    p1 = string.find(text, key)
    return text[p1 + len(key):]


def before(text, key):
    p1 = string.find(text, key)
    return text[:p1]


def gescape(text):
##    text = string.replace(text, "'", "''")
##    text = string.replace(text, "--", "-")
    text.replace("'", "''")
    text.replace("--", "-")
    return text


def progress(blocks, size_block, size):
    transfered = blocks * size_block
    if size > 0 and transfered > size:
        transfered = size
    elif size < 0:
        size = "?"

    print(transfered, '/', size, 'bytes')

# functions to handle comboboxentry stuff

def set_model_from_list(cb, items):
    """Setup a ComboBox or ComboBoxEntry based on a list of strings."""
    model = Gtk.ListStore(str)
    for i in items:
        model.append([i])

    cb.set_model(model)
    if type(cb) == Gtk.ComboBoxEntry:
        cb.set_text_column(0)
    elif type(cb) == Gtk.ComboBox:
        cell = Gtk.CellRendererText()
        cb.pack_start(cell, True, True, 0)
        cb.add_attribute(cell, 'text', 0)


def on_combo_box_entry_changed(widget):
    model = widget.get_model()
    m_iter = widget.get_active_iter()
    if m_iter:
        value = model.get_value(m_iter, 0)
        if type(value) is str:
            value = value

        return value
    else:
        return 0


def on_combo_box_entry_changed_name(widget):
    return widget.get_active_text()


def convert_entities(text):

    def conv(ents):
        entities = html.entities.entitydefs
        ents = ents.group(0)
        ent_code = entities.get(ents[1:-1], None)
        if ent_code:
            try:
                ents = str(ent_code, 'UTF-8')
            except UnicodeDecodeError:
                ents = str(ent_code, 'latin-1')
            except Exception as ex:
                print(_("error occurred while converting entity %s: %s" % (ents, ex)))

            # check if it still needs conversion
            if not ENTITY.search(ents):
                return ents

        if ents[1] == '#':
            code = ents[2:-1]
            base = 10
            if code[0] == 'x':
                code = code[1:]
                base = 16

            return chr(int(code, base))
        else:
            return

    in_entity = ENTITY.search(text)
    if not in_entity:
        return text
    else:
        ctext = in_entity.re.sub(conv, text)
        return ctext


def strip_tags(text):
    if text is None:
        return ''

    finished = 0
    while not finished:
        finished = 1
        # check if there is an open tag left
        start = text.find('<')
        if start >= 0:
            # if there is, check if the tag gets closed
            stop = text[start:].find(">")
            if stop >= 0:
                # if it does, strip it, and continue loop
                text = text[:start] + text[start + stop + 1:]
                finished = 0

    return text


def clean(text):
    t = strip_tags(text)
    t.replace('&nbsp;', ' ')
    t.replace('&#34;', '')   # replace quotes
    t.replace('&#160;', ' ') # replace nbsp
    return t.strip()


def gdecode(txt, encode):
    return txt


# Messages


def error(msg, parent=None):
    dialog = Gtk.MessageDialog(parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, msg)
    dialog.set_skip_taskbar_hint(False)
    dialog.run()
    dialog.destroy()


def urllib_error(msg, parent=None):
    dialog = Gtk.MessageDialog(parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, msg)
    dialog.set_skip_taskbar_hint(False)
    dialog.run()
    dialog.destroy()


def warning(msg, parent=None):
    if mac:
        macutils.createAlert(msg)
    else:
        dialog = Gtk.MessageDialog(parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, msg)
        dialog.set_skip_taskbar_hint(False)
        dialog.run()
        dialog.destroy()


def info(msg, parent=None):
    if mac:
        macutils.createAlert(msg)
    else:
        dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO, Gtk.ButtonsType.OK, msg)
        dialog.set_skip_taskbar_hint(False)
        dialog.run()
        dialog.destroy()


def question(msg, window=None):
    if mac:
        response = macutils.question(msg)
        return response
    else:
        dialog = Gtk.MessageDialog(window, Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION, Gtk.ButtonsType.NONE, msg)
        dialog.add_buttons(Gtk.STOCK_YES, Gtk.ResponseType.YES, Gtk.STOCK_NO, Gtk.ResponseType.NO)
        dialog.set_default_response(Gtk.ResponseType.NO)
        dialog.set_skip_taskbar_hint(False)
        response = dialog.run()
        dialog.destroy()
        return response in (Gtk.ResponseType.OK, Gtk.ResponseType.YES)


def popup_message(message):
    """shows popup message while executing decorated function"""

    def wrap(f):

        def wrapped_f(*args, **kwargs):
            if Gtk:
                window = Gtk.Window()
                window.set_title('Griffith info')
                window.set_position(Gtk.WIN_POS_CENTER)
                window.set_keep_above(True)
                window.stick()
                window.set_default_size(200, 50)
                label = Gtk.Label()
                label.set_markup("""<big><b>Griffith:</b>
%s</big>""" % message)
                window.add(label)
                window.set_modal(True)
                window.set_type_hint(Gdk.WINDOW_TYPE_HINT_DIALOG)
                window.show_all()
                while Gtk.events_pending():    # give GTK some time for updates
                    Gtk.main_iteration()
            else:
                print(message, end=' ')
            res = f(*args, **kwargs)
            if Gtk:
                window.destroy()
            else:
                print(' [done]')

            return res
        return wrapped_f
    return wrap


def file_chooser(self, title, action=None, buttons=None, name='', folder='', picture=False, backup=False):
    if mac:
        if "SAVE" in str(action):
            if backup:
                status, filename, path = macutils.saveDialog(['zip'])
            else:
                status, filename, path = macutils.saveDialog()
        else:
            status, filename, path = macutils.openDialog(['zip'])

        if status:
            if filename.lower().endswith('.zip'):
                pass
            else:
                filename = filename+".zip"
            return filename, path
        else:
            return False
    else:
        dialog = Gtk.FileChooserDialog(title=title, action=action, buttons=buttons)
        dialog.set_default_response(Gtk.ResponseType.OK)
        if name:
            dialog.set_current_name(name)

        if folder:
            dialog.set_current_folder(folder)

        mfilter = Gtk.FileFilter()
        if picture:
            preview = Gtk.Image()
            dialog.set_preview_widget(preview)
            dialog.connect("update-preview", update_preview_cb, preview)
            mfilter.set_name(_("Images"))
            mfilter.add_mime_type("image/png")
            mfilter.add_mime_type("image/jpeg")
            mfilter.add_mime_type("image/gif")
            mfilter.add_pattern("*.[pP][nN][gG]")
            mfilter.add_pattern("*.[jJ][pP][eE]?[gG]")
            mfilter.add_pattern("*.[gG][iI][fF]")
            mfilter.add_pattern("*.[tT][iI][fF]{1,2}")
            mfilter.add_pattern("*.[xX][pP][mM]")
            dialog.add_filter(mfilter)
        elif backup:
            mfilter.set_name(_('backups'))
            mfilter.add_pattern('*.[zZ][iI][pP]')
            mfilter.add_pattern('*.[gG][rR][iI]')
            mfilter.add_pattern('*.[dD][bB]')
            dialog.add_filter(mfilter)

        mfilter = Gtk.FileFilter()
        mfilter.set_name(_("All files"))
        mfilter.add_pattern("*")
        dialog.add_filter(mfilter)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            filename = None
        else:
            return False

        path = dialog.get_current_folder()
        self.widgets['preferences']['backup_dir'] = path
        dialog.destroy()
        return filename, path


def update_preview_cb(file_chooser, preview):
    filename = file_chooser.get_preview_filename()
    try:
        pixbuf = Gtk.Gdk.pixbuf_new_from_file_at_size(filename, 128, 128)
        preview.set_from_pixbuf(pixbuf)
        have_preview = True
    except:
        have_preview = False
    file_chooser.set_preview_widget_active(have_preview)
    return


def run_browser(url):
    webbrowser.register('open', webbrowser.GenericBrowser("open '%s'"))
    webbrowser._tryorder.append('open')
    webbrowser.open(url)


def read_plugins(prefix, directory):
    """returns available plugins"""

    import glob
    return glob.glob("%s/%s*.py" % (directory, prefix))


def findKey(val, dict):
    for key, value in list(dict.items()):
        if value == val:
            return key
    return None


def garbage(handler):
    pass


def clean_posters_dir(self):
    posters_dir = self.locations['posters']
    counter = 0

    for dirpath, dirnames, filenames in os.walk(posters_dir):
        for name in filenames:
            filepath = os.path.join(dirpath, name)
            if name.endswith('_m.jpg') or name.endswith('_s.jpg'):
                # it's safe to remove all thumbs, they'll be regenerated later
                os.unlink(filepath)
            else:
                poster_md5 = md5sum(open(filepath, 'rb'))
                # lets check if this poster is orphan
                used = self.db.session.query(db.Poster).filter(db.Poster.md5sum == poster_md5).count()
                if not used:
                    counter += 1
                    os.unlink(filepath)

    if counter:
        print("%d orphan files cleaned." % counter)
    else:
        print("No orphan files found.")


def decompress(data):
    try:
        compressedStream = StringIO(data)
        gzipper = gzip.GzipFile(fileobj=compressedStream)
        data = gzipper.read()
    except Exception as e:
        log.debug("Cannot decompress data: ", e)
        pass
    return data


def get_dependencies():
    depend = []

    # Python version
    if sys.version_info[:2] < (3, 9):
        depend.append({'module': 'python',
            'version': '-' + '.'.join(map(str, sys.version_info)),
            'module_req': '3.9',
            'url': 'http://www.python.org/'})
            # TODO: 'suse', etc.

    if Gtk is None:
        version = False
        depend.append({'module': 'gtk',
            'version': version,
            'module_req': '3.0',
            'url': 'http://www.pyGtk.org/'})
            # TODO: 'fedora', 'suse', etc.

#    try:
#        import Gtk.glade
#        # (version == Gtk.pygtk_version)
#    except:
#        version = False
#    depend.append({'module': 'Gtk.glade',
#        'version': version,
#        'module_req': '2.6',
#        'url': 'http://www.pyGtk.org/',
#        'debian': 'python-glade2',
#        'debian_req': '2.8.6-1'})

    try:
        import sqlalchemy
        if list(map(int, sqlalchemy.__version__[:3].split('.'))) < [1, 3]:
            version = "-%s" % sqlalchemy.__version__
        else:
            version = sqlalchemy.__version__
    except:
        version = False

    depend.append({'module': 'sqlalchemy',
        'version': version,
        'module_req': '1.3',
        'url': 'http://www.sqlalchemy.org/'})

    try:
        import sqlite3
        version = sqlite3.version
        sqliteversion = sqlite3.sqlite_version
    except ImportError:
        version = False
        depend.append({'module': 'sqlite3',
            'version': version + ' (sqlite-lib ' + sqliteversion + ')',
            'url': 'http://www.python.org'})

    try:
        import reportlab
        version = reportlab.Version
    except:
        version = False
    depend.append({'module': 'reportlab',
        'version': version,
        'url': 'http://www.reportlab.org/'})

    try:
        import PIL
        version = True
    except:
        version = False
    depend.append({'module': 'PIL',
        'version': version,
        'url': 'http://www.pythonware.com/products/pil/'})

    # extra dependencies:
    optional = []

    try:
        import psycopg2
        version = psycopg2.__version__
    except:
        version = False
    optional.append({'module': 'psycopg2',
        'version': version,
        'url': 'http://initd.org/psycopg/'})

    try:
        import MySQLdb
        version = '.'.join([str(i) for i in MySQLdb.version_info])
    except:
        version = False
    optional.append({'module': 'MySQLdb',
        'version': version,
        'url': 'http://sourceforge.net/projects/mysql-python'})

    try:
        import chardet
        version = chardet.__version__
    except:
        version = False
    optional.append({'module': 'chardet',
        'version': version,
        'url': 'http://chardet.feedparser.org/'})

    try:
        import sqlite
        version = sqlite.version
    except:
        version = False
    optional.append({'module': 'sqlite',
        'version': version,
        'url': 'http://initd.org/tracker/pysqlite'})

    try:
        import lxml
        version = True
    except ImportError:
        version = False
    optional.append({'module': 'lxml',
        'version': version,
        'url': 'http://lxml.de/'})

    return depend, optional


def html_encode(s):
    if not isinstance(s, str):
        s = str(s)
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('"', '&quot;')
    return s


def digits_only(s, maximum=None):
    if s is None:
        return 0
    match = re.compile(r"\d+")
    a = match.findall(str(s))
    if len(a):
        s = int(a[0])
    else:
        s = 0
    if maximum is None:
        return s
    else:
        if s > maximum:
            return maximum
        else:
            return s


def copytree(src, dst, symlinks=False):
    """Recursively copy a directory tree using copy2().

    This is shutil's copytree modified version
    """
    from shutil import copy2
    names = os.listdir(src)
    if not os.path.isdir(dst):
        os.mkdir(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                copy2(srcname, dstname)
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, why))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except EnvironmentError as err:
            errors.extend(err.args[0])
    if errors:
        raise EnvironmentError(errors)


def is_windows_system():
    if os.name == 'nt' or os.name.startswith('win'): # win32, win64
        return True
    return False


def md5sum(fobj):
    """Returns an md5 hash for an object with read() method."""
    try:
        import hashlib
        m = hashlib.md5()
    except ImportError:
        import md5
        m = md5.new()
    if hasattr(fobj, 'read'):
        while True:
            d = fobj.read(8096)
            if not d:
                break
            m.update(d)
    else:
        m.update(fobj)

    return str(m.hexdigest())


def create_image_cache(md5sum, gsql):
    poster = gsql.session.query(db.Poster).filter_by(md5sum=md5sum).first()
    if not poster:
        log.warn("poster not available: %s", md5sum)
        return False

    if not poster.data:
        log.warn("poster data not available: %s", md5sum)
        return False

    fn_big = os.path.join(gsql.data_dir, 'posters', md5sum + '.jpg')
    fn_medium = os.path.join(gsql.data_dir, 'posters', md5sum + '_m.jpg')
    fn_small = os.path.join(gsql.data_dir, 'posters', md5sum + '_s.jpg')

    if not os.path.isfile(fn_big):
        f = open(fn_big, 'wb')
        f.write(poster.data)
        f.close()

    image = Gtk.Image()
    image.set_from_file(fn_big)

    if not os.path.isfile(fn_medium):
        pixbuf = image.get_pixbuf()
        pixbuf = pixbuf.scale_simple(100, 140, GdkPixbuf.InterpType.BILINEAR)
        pixbuf.savev(fn_medium, 'jpeg', ['quality'], ['70'])

    if not os.path.isfile(fn_small):
        pixbuf = image.get_pixbuf()
        pixbuf = pixbuf.scale_simple(30, 40, GdkPixbuf.InterpType.BILINEAR)
        pixbuf.savev(fn_small, 'jpeg', ['quality'], ['70'])

    return True


def create_imagefile(destdir, md5sum, gsql, destfilename=None):
    poster = gsql.session.query(db.Poster).filter_by(md5sum=md5sum).first()
    if not poster:
        log.warn("poster not available: %s", md5sum)
        return False

    if not poster.data:
        log.warn("poster data not available: %s", md5sum)
        return False

    if destfilename:
        fulldestpath = os.path.join(destdir, destfilename + '.jpg')
    else:
        fulldestpath = os.path.join(destdir, md5sum + '.jpg')

    f = open(fulldestpath, 'wb')
    try:
        f.write(poster.data)
    finally:
        f.close()

    return True


def get_image_fname(md5sum, gsql, size=None):
    """size: s - small; m - medium, b or None - big"""
    if size not in (None, 's', 'm', 'b'):
        raise TypeError("wrong size: %s" % size)
    if not md5sum:
        raise TypeError("md5sum not set")

    if not size or size == 'b':
        size = ''
    else:
        size = "_%s" % size

    file_name = os.path.join(gsql.data_dir, 'posters', md5sum + size + '.jpg')

    if not os.path.isfile(file_name) and not create_image_cache(md5sum, gsql):
        log.warn("Can't create image file %s for md5sum %s" % (file_name, md5sum))
        return False

    return file_name


def get_defaultimage_fname(self):
    return os.path.join(self.locations['images'], 'default.png')


def get_defaultthumbnail_fname(self):
    return os.path.join(self.locations['images'], 'default_thumbnail.png')


def get_filesystem_pagesize(path):
    pagesize = 1024
    # retrieve filesystem page size for optimizing filesystem based database systems like sqlite
    try:
        if is_windows_system():
            pagesize = 4096 # almost the best for standard windows systems

            # try to find the perfect value from the filesystem
            import ctypes

            drive = os.path.splitdrive(path)
            sectorsPerCluster = ctypes.c_ulonglong(0)
            bytesPerSector = ctypes.c_ulonglong(0)
            rootPathName = ctypes.c_wchar_p(str(drive[0]))

            ctypes.windll.kernel32.GetDiskFreeSpaceW(rootPathName, ctypes.pointer(sectorsPerCluster),
                ctypes.pointer(bytesPerSector), None, None)
            pagesize = sectorsPerCluster.value * bytesPerSector.value
        else:
            # I could not try it out on non-windows platforms
            # if it doesn't work the default page size is returned
            from os import statvfs
            stats = statvfs(path)
            pagesize = stats.f_bsize
    except:
        log.error('')

    # adjust page size
    if pagesize > 32768:
        pagesize = 32768

    if pagesize < 1024:
        pagesize = 1024

    return pagesize


# Python program to convert a list to string
def listToString(s, joiner=' '):
    # traverse in the string
    try:
        listToStr = joiner.join([str(elem) for elem in s])
        return listToStr
    except:
        return ''
