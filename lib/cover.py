# -*- coding: UTF-8 -*-

__revision__ = '$Id: cover.py 1154 2009-02-08 23:20:39Z piotrek $'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ożarowski
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
import pango
import string
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
import TTFont
from reportlab.platypus import Image
from reportlab.lib import colors
import db
import gutils
import version
import textwrap

exec_location = os.path.abspath(os.path.dirname(sys.argv[0]))

def cover_image(self,number):
    filename = gutils.file_chooser(_("Select image"), \
        action=gtk.FILE_CHOOSER_ACTION_OPEN, \
        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    if filename[0]:
        cover_image_process(self, filename[0], number)

def cover_image_process(self, filename, number):
    size = self.widgets['print_cover']['ci_size'].get_active()
    print_number = self.widgets['print_cover']['ci_number'].get_active()

    if self.config.get('font', '') != '':
        fontName = "custom_font"
        pdfmetrics.registerFont(TTFont(fontName,self.config.get('font', '')))
    else:
        fontName = "Helvetica"

    if size == 0:
        #standard
        cover_x=774
        cover_y=518
    elif size == 1:
        #slim
        cover_x=757;
        cover_y=518
    else:
        #double slim
        cover_x=757
        cover_y=518

    # A4 landscape definition
    pageWidth = 842
    pageHeight = 595

    # hardcoded to A4
    pos_x=(pageWidth-cover_x)/2;
    pos_y=(pageHeight-cover_y)/2;

    # make a pdf
    # using a truetype font with unicode support
    c = canvas.Canvas(os.path.join(self.griffith_dir, "cover.pdf"), \
        (pageWidth, pageHeight))
    c.setFont(fontName, 8)
    # copyright line
    c.drawString(20, 20 ,_("Cover generated by Griffith v").encode('utf-8') + \
        version.pversion+" (C) 2004-2009 Vasco Nunes/Piotr Ozarowski - "+ \
        _("Released Under the GNU/GPL License").encode('utf-8'))

    # get movie information from db
    movie = self.db.session.query(db.Movie).filter_by(number=number).first()
    if movie is not None:
        c.drawImage(filename, pos_x, pos_y, cover_x, cover_y)
        if print_number:
            c.setFillColor(colors.white)
            c.rect((pageWidth/2)-13, 520, 26, 70, fill=1, stroke=0)
            c.setFillColor(colors.black)
            c.setFont(fontName, 10)
            c.drawCentredString(pageWidth/2, 530, number)

    # draw cover area
    c.rect(pos_x, pos_y, cover_x, cover_y)

    c.showPage()
    c.save()
    self.widgets['print_cover']['window_simple'].hide()
    cover_file = os.path.join(self.griffith_dir, "cover.pdf")
    if self.windows:
        os.popen3("\"" + cover_file + "\"")
    else:
        os.popen3(self.pdf_reader + " " + cover_file)

def cover_simple(self, number):
    size = self.widgets['print_cover']['cs_size'].get_active()
    print_number = self.widgets['print_cover']['cs_include_movie_number'].get_active()
    poster = self.widgets['print_cover']['cs_include_poster'].get_active()

    if self.config.get('font', '')!='':
        fontName = "custom_font"
        pdfmetrics.registerFont(TTFont(fontName,self.config.get('font', '')))
    else:
        fontName = "Helvetica"

    if size == 0:
        #standard
        cover_x=774
        cover_y=518
    elif size == 1:
        #slim
        cover_x=757;
        cover_y=518
    else:
        #double slim
        cover_x=757
        cover_y=518

    # A4 landscape definition
    pageWidth = 842
    pageHeight = 595

    # hardcoded to A4
    pos_x=(pageWidth-cover_x)/2;
    pos_y=(pageHeight-cover_y)/2;
    # make a pdf
    c = canvas.Canvas(os.path.join(self.griffith_dir, "cover.pdf"), (pageWidth, pageHeight))
    c.setFont(fontName,8)

    # copyright line
    c.drawString(20,20,_("Cover generated by Griffith v").encode('utf-8') + \
        version.pversion+" (C) 2004-2009 Vasco Nunes/Piotr Ozarowski - "+ \
        _("Released Under the GNU/GPL License").encode('utf-8'))

    # draw cover area
    c.rect(pos_x, pos_y, cover_x, cover_y)

    # get movie information from db
    movie = self.db.session.query(db.Movie).filter_by(number=number).first()
    if movie is not None:
        if print_number:
            c.setFont(fontName, 10)
            c.drawCentredString(pageWidth/2, 530, number)

        c.setFont(fontName, 16)
        c.rotate(90)
        c.drawString(60, (-pageWidth/2)-8, movie.title.encode('utf-8'))
        c.rotate(-90)
        if movie.poster_md5:
            filename = gutils.get_image_fname(movie.poster_md5, self.db)
            if filename:
                c.drawImage(filename, x=(pageWidth-30)/2, y=470, width=30, height=50)
        # print movie info
        c.setFont(fontName, 8)
        textObject = c.beginText()
        textObject.setTextOrigin(pageWidth-cover_x, 300)
        textObject.setFont(fontName, 8)
        textObject.textLine("%s: %s" % (_('Original Title'), movie.o_title))
        textObject.textLine("%s: %s" % (_('Title'), movie.title))
        textObject.textLine('')
        textObject.textLine("%s: %s" % (_('Director'), movie.director))
        textObject.textLine('')
        textObject.textLine("%s: %s %s" % (_('Running Time'), movie.runtime, _(' min')))
        textObject.textLine("%s: %s" % (_('Country'), movie.country))
        textObject.textLine("%s: %s" % (_('Genre'), movie.genre))
        plotlines = textwrap.wrap(movie.plot, 80)
        plotlinenr = 0
        textObject.textLine("%s:" % (_('Plot')))
        for plotline in plotlines:
            textObject.textLine(plotline)
            plotlinenr = plotlinenr + 1
            if plotlinenr > 15:
                textObject.textLine('...')
                break
        textObject.textLine('')
        c.drawText(textObject)
        # draw bigger poster image
        if poster and movie.poster_md5 and filename:
            c.drawImage(filename, x=(pageWidth-(pageWidth-cover_x)-235), y=(pageHeight/2)-125, width=180, height=250)
    c.showPage()
    c.save()
    self.widgets['print_cover']['window_simple'].hide()
    cover_file = os.path.join(self.griffith_dir, 'cover.pdf')
    if self.windows:
        os.popen3("\"" + cover_file + "\"")
    elif self.mac:
        os.popen3("open -a Preview" + " " + cover_file)
    else:
        os.popen3(self.pdf_reader + " " + cover_file)
