# -*- coding: UTF-8 -*-

__revision__ = '$Id: preferences.py 1597 2011-10-04 18:41:24Z piotrek $'
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
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import db
import gutils
import initialize
import plugins.extensions

try:
    import gtkspell
    spell_support = 1
except:
    spell_support = 0

log = logging.getLogger("Griffith")


def show_preferences(self, page=None):
    w = self.widgets['preferences']
    # number
    if self.config.get('number', True, section='mainlist') == False:
        w['view_number'].set_active(False)
    else:
        w['view_number'].set_active(True)
    # image
    if self.config.get('image', True, section='mainlist') == False:
        w['view_image'].set_active(False)
    else:
        w['view_image'].set_active(True)
    # original title
    if self.config.get('otitle', True, section='mainlist') == False:
        w['view_o_title'].set_active(False)
    else:
        w['view_o_title'].set_active(True)
    # title
    if self.config.get('title', True, section='mainlist') == False:
        w['view_title'].set_active(False)
    else:
        w['view_title'].set_active(True)
    # director
    if self.config.get('director', True, 'mainlist') == False:
        w['view_director'].set_active(False)
    else:
        w['view_director'].set_active(True)
    # genre
    if self.config.get('genre', True, 'mainlist') == False:
        w['view_genre'].set_active(False)
    else:
        w['view_genre'].set_active(True)
    # seen
    if self.config.get('seen', True, 'mainlist') == False:
        w['view_seen'].set_active(False)
    else:
        w['view_seen'].set_active(True)
    # year
    if self.config.get('year', True, 'mainlist') == False:
        w['view_year'].set_active(False)
    else:
        w['view_year'].set_active(True)
    # runtime
    if self.config.get('runtime', True, 'mainlist') == False:
        w['view_runtime'].set_active(False)
    else:
        w['view_runtime'].set_active(True)
    # rating
    if self.config.get('rating', True, 'mainlist') == False:
        w['view_rating'].set_active(False)
    else:
        w['view_rating'].set_active(True)
    # created
    if self.config.get('created', True, 'mainlist') == False:
        w['view_created'].set_active(False)
    else:
        w['view_created'].set_active(True)
    # updated
    if self.config.get('updated', True, 'mainlist') == False:
        w['view_updated'].set_active(False)
    else:
        w['view_updated'].set_active(True)

    # email reminder
    if self.config.get('use_auth', False, section='mail') == False:
        w['mail_use_auth'].set_active(False)
    else:
        w['mail_use_auth'].set_active(True)

    if self.config.get('mail_use_tls', False, section='mail') == False:
        w['mail_use_tls'].set_active(False)
    else:
        w['mail_use_tls'].set_active(True)

    w['mail_smtp_server'].set_text(self.config.get('smtp_server', 'localhost', section='mail'))
    w['mail_smtp_port'].set_text(self.config.get('mail_smtp_port', '25', section='mail'))
    w['mail_username'].set_text(self.config.get('username', '', section='mail'))
    w['mail_password'].set_text(self.config.get('password', '', section='mail'))
    w['mail_email'].set_text(self.config.get('email', 'griffith@localhost', section='mail'))

    # pdf reader
    w['epdf_reader'].set_text(self.pdf_reader)

    # pdf font
    if self.config.get('font'):
        w['font'].set_filename(self.config.get('font'))
    if self.config.get('font_size'):
        try:
            w['font_size'].set_value(float(self.config.get('font_size')))
        except:
            w['font_size'].set_value(18.0)

    # pdf elements
    pdf_elements = self.config.get('pdf_elements', 'image,director,genre,cast')
    for pdf_element in pdf_elements.split(','):
        if 'pdf_' + pdf_element.strip() in w:
            w['pdf_' + pdf_element.strip()].set_active(True)

    # defaults (for static data only)
    w['condition'].set_active( gutils.digits_only(self.config.get('condition', 0, section='defaults'), 5) )
    w['region'].set_active( gutils.digits_only(self.config.get('region', 0, section='defaults'), 8) )
    w['layers'].set_active( gutils.digits_only(self.config.get('layers', 0, section='defaults'), 4) )
    w['color'].set_active( gutils.digits_only(self.config.get('color', 0, section='defaults'), 3 ))
    tmp = self.config.get('media', 0, section='defaults')
    if tmp is not None and int(tmp) in self.media_ids:
        if int(self.config.get('media', 0, section='defaults')) > 0:
            w['media'].set_active( gutils.findKey(int(self.config.get('media', 0, section='defaults')), self.media_ids) )
        else:
            w['media'].set_active(0)
    tmp = self.config.get('vcodec', 0, section='defaults')
    if tmp is not None and int(tmp) in self.vcodecs_ids:
        if int(self.config.get('vcodec', 0, section='defaults')) > 0:
            w['vcodec'].set_active(    int(gutils.findKey(int(self.config.get('vcodec', 0, section='defaults')), self.vcodecs_ids)) )
        else:
            w['vcodec'].set_active(0)
    w['seen'].set_active(bool(self.config.get('seen', True, section='defaults')))

    # search for:
    w['s_classification'].set_active(bool(self.config.get('s_classification', True, section='add')))
    w['s_country'].set_active(bool(self.config.get('s_country', True, section='add')))
    w['s_director'].set_active(bool(self.config.get('s_director', True, section='add')))
    w['s_genre'].set_active(bool(self.config.get('s_genre', True, section='add')))
    w['s_image'].set_active(bool(self.config.get('s_image', True, section='add')))
    w['s_notes'].set_active(bool(self.config.get('s_notes', True, section='add')))
    w['s_o_site'].set_active(bool(self.config.get('s_o_site', True, section='add')))
    w['s_o_title'].set_active(bool(self.config.get('s_o_title', True, section='add')))
    w['s_plot'].set_active(bool(self.config.get('s_plot', True, section='add')))
    w['s_rating'].set_active(bool(self.config.get('s_rating', True, section='add')))
    w['s_runtime'].set_active(bool(self.config.get('s_runtime', True, section='add')))
    w['s_site'].set_active(bool(self.config.get('s_site', True, section='add')))
    w['s_studio'].set_active(bool(self.config.get('s_studio', True, section='add')))
    w['s_title'].set_active(bool(self.config.get('s_title', True, section='add')))
    w['s_trailer'].set_active(bool(self.config.get('s_trailer', True, section='add')))
    w['s_cast'].set_active(bool(self.config.get('s_cast', True, section='add')))
    w['s_year'].set_active(bool(self.config.get('s_year', True, section='add')))
    w['s_screenplay'].set_active(bool(self.config.get('s_screenplay', True, section='add')))
    w['s_cameraman'].set_active(bool(self.config.get('s_cameraman', True, section='add')))
    w['s_resolution'].set_active(bool(self.config.get('s_resolution', True, section='add')))
    w['s_barcode'].set_active(bool(self.config.get('s_barcode', True, section='add')))

    if self.config.get('sortby', section='mainlist'):
        tmp = self.sort_criteria.index(self.config.get('sortby', section='mainlist'))
        w['sortby'].set_active(tmp)
    w['sortby_reverse'].set_active(bool(self.config.get('sortby_reverse', False, section='mainlist')))

    w['s_limit'].set_value(gutils.digits_only(self.config.get('limit', 0, section='mainlist')))

    plugins = gutils.read_plugins('PluginMovie', \
        self.locations['movie_plugins'])
    plugins.sort()
    mcounter = 0
    default_movie_plugin = self.config.get('default_movie_plugin')
    for p in plugins:
        plugin_module = os.path.basename(p).replace('.py','')
        plugin_name = plugin_module.replace('PluginMovie','')
        if plugin_name == default_movie_plugin:
            w['default_plugin'].set_active(mcounter)

        mcounter = mcounter + 1

    # rating image
    try:
        rimage = int(self.config.get('rating_image', 0))
    except:
        rimage = 0

    w['rating_image'].set_active(rimage)

    # spellchecker
    if self.config.get('gtkspell', False, section='spell') == False:
        w['spellchecker'].set_active(False)
    else:
        w['spellchecker'].set_active(True)

    self.on_cb_spellchecker_pref_toggled(w['spellchecker'])

    if self.config.get('notes', True, section='spell') == False:
        w['spell_notes'].set_active(False)
    else:
        w['spell_notes'].set_active(True)

    if self.config.get('plot', True, section='spell') == False:
        w['spell_plot'].set_active(False)
    else:
        w['spell_plot'].set_active(True)

    w['spell_lang'].set_text(str(self.config.get('lang', 'en', section='spell')))

    if page is not None:
        w['notebook'].set_current_page(page)

    w['window'].show()

def save_preferences(self):
    w = self.widgets['preferences']
    c = self.config
    global spell_support

    was_false = notes_was_false = plot_was_false = 1

    if c.get('gtkspell', False, section='spell') == True:
        was_false = 0

    if c.get('notes', False, section='spell') == True:
        notes_was_false = 0

    if c.get('plot', False, section='spell') == True:
        plot_was_false = 0

    # number
    if w['view_number'].get_active():
        c.set('number', 'True', section='mainlist')
    else:
        c.set('number', 'False', section='mainlist')
    # image
    if w['view_image'].get_active():
        c.set('image', 'True', section='mainlist')
    else:
        c.set('image', 'False', section='mainlist')
    # original title
    if w['view_o_title'].get_active():
        c.set('otitle', 'True', section='mainlist')
    else:
        c.set('otitle', 'False', section='mainlist')
    # title
    if w['view_title'].get_active():
        c.set('title', 'True', section='mainlist')
    else:
        c.set('title', 'False', section='mainlist')
    # director
    if w['view_director'].get_active():
        c.set('director', 'True', section='mainlist')
    else:
        c.set('director', 'False', section='mainlist')
    # genre
    if w['view_genre'].get_active():
        c.set('genre', 'True', section='mainlist')
    else:
        c.set('genre', 'False', section='mainlist')
    # seen
    if w['view_seen'].get_active():
        c.set('seen', 'True', section='mainlist')
    else:
        c.set('seen', 'False', section='mainlist')
    # year
    if w['view_year'].get_active():
        c.set('year', 'True', section='mainlist')
    else:
        c.set('year', 'False', section='mainlist')
    # runtime
    if w['view_runtime'].get_active():
        c.set('runtime', 'True', section='mainlist')
    else:
        c.set('runtime', 'False', section='mainlist')
    # rating
    if w['view_rating'].get_active():
        c.set('rating', 'True', section='mainlist')
    else:
        c.set('rating', 'False', section='mainlist')
    # created
    if w['view_created'].get_active():
        c.set('created', 'True', section='mainlist')
    else:
        c.set('created', 'False', section='mainlist')
    # updated
    if w['view_updated'].get_active():
        c.set('updated', 'True', section='mainlist')
    else:
        c.set('updated', 'False', section='mainlist')

    # sortby
    if w['sortby'].get_active():
        field = self.sort_criteria[w['sortby'].get_active()]
        if field:
            c.set('sortby', field, section='mainlist')
    else:
        c.set('sortby', 'number', section='mainlist')
    c.set('sortby_reverse', w['sortby_reverse'].get_active(), section='mainlist')

    c.set('limit', str(int(w['s_limit'].get_value())), section='mainlist')


    # pdf font
    if w['font'].get_filename():
        c['font'] = w['font'].get_filename()
    c['font_size'] = int(w['font_size'].get_value())

    # pdf elements
    pdf_elements = ''
    for child in w['pdf_elements_table']:
        if child.get_active():
            pdf_elements = pdf_elements + child.get_name()[4:] + ','
    if pdf_elements:
        c.set('pdf_elements', pdf_elements[:-1])
    else:
        c.set('pdf_elements', pdf_elements)

    # spellchecker
    if w['spellchecker'].get_active():
        c.set('gtkspell', True, section='spell')
    else:
        c.set('gtkspell', False, section='spell')
    if w['spell_notes'].get_active():
        c.set('notes', True, section='spell')
    else:
        c.set('notes', False, section='spell')
    if w['spell_plot'].get_active():
        c.set('plot', True, section='spell')
    else:
        c.set('plot', False, section='spell')

    # rating image
    c['rating_image'] = str(w['rating_image'].get_active())

    #defaults
    media_id = self.media_ids[w['media'].get_active()]
    if media_id is None:
        media_id = 0
    c.set('media', media_id, section='defaults')
    vcodec_id = self.vcodecs_ids[w['vcodec'].get_active()]
    if vcodec_id is None:
        vcodec_id = 0
    c.set('vcodec', vcodec_id, section='defaults')
    c.set('condition', str(w['condition'].get_active()), section='defaults')
    c.set('region', str(w['region'].get_active()), section='defaults')
    c.set('layers', str(w['layers'].get_active()), section='defaults')
    c.set('color', str(w['color'].get_active()), section='defaults')
    c.set('seen', str(w['seen'].get_active()), section='defaults')

    # email reminder
    if w['mail_use_auth'].get_active():
        c.set('use_auth', True, section='mail')
    else:
        c.set('use_auth', False, section='mail')

    if w['mail_use_tls'].get_active():
        c.set('mail_use_tls', True, section='mail')
    else:
        c.set('mail_use_tls', False, section='mail')

    c.set('smtp_server', w['mail_smtp_server'].get_text(), section='mail')
    c.set('mail_smtp_port', w['mail_smtp_port'].get_text(), section='mail')

    c.set('username', w['mail_username'].get_text(), section='mail')
    c.set('password', w['mail_password'].get_text(), section='mail')
    c.set('email', w['mail_email'].get_text(), section='mail')

    # default movie plugin
    if w['default_plugin'].get_active():
        c['default_movie_plugin'] = \
            gutils.on_combo_box_entry_changed(w['default_plugin'])
    # search for:
    c.set('s_classification', w['s_classification'].get_active(), section='add')
    c.set('s_country', w['s_country'].get_active(), section='add')
    c.set('s_director', w['s_director'].get_active(), section='add')
    c.set('s_genre', w['s_genre'].get_active(), section='add')
    c.set('s_image', w['s_image'].get_active(), section='add')
    c.set('s_notes', w['s_notes'].get_active(), section='add')
    c.set('s_o_site', w['s_o_site'].get_active(), section='add')
    c.set('s_o_title', w['s_o_title'].get_active(), section='add')
    c.set('s_plot', w['s_plot'].get_active(), section='add')
    c.set('s_rating', w['s_rating'].get_active(), section='add')
    c.set('s_runtime', w['s_runtime'].get_active(), section='add')
    c.set('s_site', w['s_site'].get_active(), section='add')
    c.set('s_studio', w['s_studio'].get_active(), section='add')
    c.set('s_title', w['s_title'].get_active(), section='add')
    c.set('s_trailer', w['s_trailer'].get_active(), section='add')
    c.set('s_cast', w['s_cast'].get_active(), section='add')
    c.set('s_year', w['s_year'].get_active(), section='add')
    c.set('s_screenplay', w['s_screenplay'].get_active(), section='add')
    c.set('s_cameraman', w['s_cameraman'].get_active(), section='add')
    c.set('s_resolution', w['s_resolution'].get_active(), section='add')
    c.set('s_barcode', w['s_barcode'].get_active(), section='add')

    mcounter = 0
    for p in self.plugins:
        plugin_module = os.path.basename(p).replace('.py','')
        plugin_name = plugin_module.replace('PluginMovie','')
        if gutils.on_combo_box_entry_changed(w['default_plugin']) == plugin_name:
            break
        mcounter = mcounter + 1
    self.widgets['add']['source'].set_active(mcounter)

    save_reader = w['epdf_reader'].get_text()

    c.set('lang', w['spell_lang'].get_text(), section='spell')
    c['pdf_reader'] = save_reader

    if spell_support:
        if c.get('gtkspell', False, section='spell') == False and not was_false:
            self.notes_spell.detach()
            self.plot_spell.detach()
        elif c.get('gtkspell', False, section='spell') == True and was_false:
            initialize.spellcheck(self)
        else:
            pass

        if c.get('gtkspell', False, section='spell') == True:
            if c.get('plot', True, section='spell') == False and not plot_was_false:
                self.plot_spell.detach()
            elif c.get('plot', True, section='spell') == True and plot_was_false:
                self.plot_spell = gtkspell.Spell(self.widgets['add']['plot'])
                self.plot_spell.set_language(c.get('lang', 'en', section='spell'))
            else:
                pass

            if c.get('notes', True, section='spell') == False and not notes_was_false:
                self.notes_spell.detach()
            elif c.get('notes', True, section='spell') == True and notes_was_false:
                self.notes_spell = gtkspell.Spell(self.widgets['add']['notes'])
                self.notes_spell.set_language(c.get('lang', 'en', section='spell'))
            else:
                pass
    self.pdf_reader = save_reader

    # extensions settings
    for ext_name in plugins.extensions.by_name:
        preferenceswidgets = plugins.extensions.by_name[ext_name].preferenceswidgets
        for prefname in preferenceswidgets:
            widget = preferenceswidgets[prefname]
            if isinstance(widget, Gtk.CheckButton):
                value = widget.get_active()
            elif isinstance(widget, Gtk.Entry):
                value = widget.get_text()
            elif isinstance(widget, Gtk.ComboBox):
                iter = widget.get_active_iter()
                if iter:
                    value = widget.get_model().get_value(iter, 1)
            else:
                log.error('widget type not supported %s', type(widget))
                continue
            c.set("%s_%s" % (ext_name, prefname), value, section='extensions')

    # database
    old = c.to_dict(section='database')

    c.set('host', w['db_host'].get_text(), section='database')
    c.set('port', int(w['db_port'].get_value()), section='database')
    c.set('name', w['db_name'].get_text(), section='database')
    c.set('user', w['db_user'].get_text(), section='database')
    c.set('passwd', w['db_passwd'].get_text(), section='database')
    db_type = int(w['db_type'].get_active())
    if db_type == 1:
        c.set('type', 'postgres', section='database')
    elif db_type == 2:
        c.set('type', 'mysql', section='database')
    elif db_type == 3:
        c.set('type', 'mssql', section='database')
    else:
        c.set('type', 'sqlite', section='database')

    if old['type'] != c.get('type', section='database') or (old['type']!='sqlite' and (\
            old['host'] != c.get('host', section='database') or \
            old['port'] != c.get('port', section='database') or \
            old['user'] != c.get('user', section='database') or \
            old['passwd'] != c.get('passwd', section='database'))) or \
            old['name'] != c.get('name', section='database'):
        log.info('DATABASE: connecting to new db server...')
        import sql
        from sqlalchemy.exc import InvalidRequestError
        from initialize import dictionaries, people_treeview

        # new database connection
        self.initialized = False
        if 'posters' in c:
            c['posters'] = None # force update
        try:
            self.db.dispose()
            self.db = sql.GriffithSQL(c, self.locations['home'], fallback=True)
        except InvalidRequestError as e:
            log.exception('')
            c.set('type', 'sqlite', section='database')
            w['db_type'].set_active(0)
            self.db = sql.GriffithSQL(c, self.locations['home'])

        log.info("New database Engine: %s" % self.db.session.bind.engine.name)

        # initialize new database
        self.total = int(self.db.session.query(db.Movie).count())
        self.count_statusbar()
        dictionaries(self)
        people_treeview(self, False)
        self.initialized = True
    self.clear_details()
    self.filter_txt_forced()
    c.save()

    # reload extensions
    initialize.extensions(self)
