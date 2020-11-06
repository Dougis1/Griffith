# -*- coding: UTF-8 -*-

__revision__ = '$Id: gdebug.py 1326 2009-12-01 21:06:05Z mikej06 $'
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
from gi.repository import Gtk
import sys
import string
import os
import logging
log = logging.getLogger("Griffith")

#
# some special classes for better debugging support on windows platforms
# py2exe redirects stdout to /dev/null and writes stderr in a file in the
# installation directory which is a bad idea since windows vista.
#
# the argument --debug now shows a debug window on windows so that the debug
# output is not written to the (black hole windows) console.
#
class GriffithDebug:
    def __init__(self, mode = False):
        self.debugWindow = None
        self.windowredirector = None
        self.blackholebuffer = None
        self.set_debug(mode)

    def set_debug(self, mode = True, logdir = None):
        self.initialize_debug_mode(mode, logdir)
        if self.debugWindow:
            if mode:
                self.debugWindow.show()
            else:
                self.debugWindow.hide()

    def set_logdir(self, logdir):
        if self.windowredirector:
            self.windowredirector.set_logdir(logdir)
        if self.blackholebuffer:
            self.blackholebuffer.set_logdir(logdir)

    def initialize_debug_mode(self, mode, logdir = None):
        # on windows systems all output to stdout goes to a black hole
        # if py2exe is used.
        # so we use a normal window and redirect output from sys.stderr
        # and sys.stdout. it is easier to use for windows users.
        #
        # but we have to do a second trick to get the output from the logging
        # module WITHOUT (!) writing the output twice, one in the window, one
        # to stderr/console/py2exe:
        # removing the handlers from the root logger and reinitialized via
        # logging.basicConfig
        # there is no other way to prevent py2exe showing a error message and
        # generating the .log file in the installation directory
        try:
            if os.name == 'nt' or os.name.startswith('win'): # win32, win64
                if mode:
                    if self.debugWindow is None:
                        self.debugWindow = DebugWindow(None)
                    if not self.windowredirector:
                        self.windowredirector = DebugWindowRedirector(self.debugWindow, logdir)
                    else:
                        self.windowredirector.set_logdir(logdir)
                    sys.stderr = sys.stdout = self.windowredirector
                    # resetting default logging configuration
                    logging.getLogger().handlers = []
                    logging.basicConfig(stream = sys.stderr, format='%(asctime)s: %(levelname)s: %(name)s(%(module)s:%(lineno)d): %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
                elif hasattr(sys, 'frozen') and sys.frozen == 'windows_exe':
                    # if a windows exe is build via py2exe, redirect all output
                    if not self.blackholebuffer:
                        self.blackholebuffer = DebugBlackholeBufferRedirector(sys.stderr, logdir)
                    else:
                        self.blackholebuffer.set_logdir(logdir)
                    sys.stderr = sys.stdout = self.blackholebuffer
                    # resetting default logging configuration
                    logging.getLogger().handlers = []
                    logging.basicConfig(stream = sys.stderr, format='%(asctime)s: %(levelname)s: %(name)s(%(module)s:%(lineno)d): %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
        except:
            log.exception('')

#
# used on windows systems
# shows a windows with a text view which displays the
# debug output provided by DebugWindowRedirector
#
class DebugWindow:
    def __init__(self, window):
        self.dialog = Gtk.Dialog('Debug Window', window, Gtk.DIALOG_MODAL, ())
        self.dialog.set_destroy_with_parent(True)
        self.dialog.set_transient_for(window)
        self.dialog.set_modal(False)
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WRAP_WORD_CHAR)
        self.textview.set_scroll_adjustments(Gtk.Adjustment(1.0, 1.0, 100.0, 1.0, 10.0, 10.0), Gtk.Adjustment(1.0, 1.0, 100.0, 1.0, 10.0, 10.0))
        self.scrolledwindow = Gtk.ScrolledWindow(None, None)
        self.scrolledwindow.add(self.textview)
        self.dialog.vbox.pack_start(self.scrolledwindow)
        self.dialog.set_default_size(640, 480)
    def show(self):
        self.dialog.show_all()
    def hide(self):
        self.dialog.hide_all()
    def close(self):
        self.dialog.destroy()
    def add(self, txt):
        if txt is not None:
            buffer = self.textview.get_buffer()
            buffer.insert(buffer.get_end_iter(), txt, -1)

#
# used on windows system
# redirects sys.stderr and sys.stdout to a debug window and
# a program-defined log-file (py2exe independent)
#
class DebugWindowRedirector(object):
    softspace = 0
    def __init__(self, debugWindow, logdir = None):
        self.debugWindow = debugWindow
        self.set_logdir(logdir)
    def set_logdir(self, logdir):
        #
        # redirected output to a debug file in the log dir/home dir because
        # users with restricted system rights can't write to the installation directory
        # which is the default if py2exe is used
        #
        if logdir:
            from locale import getdefaultlocale
            defaultLang, defaultEnc = getdefaultlocale()
            if defaultEnc is None:
                defaultEnc = 'UTF-8'
            self.debugFileName = os.path.join(logdir, 'griffith.log')
            try:
                # create the file to show that debug is running
                f = open(self.debugFileName, 'w')
                f.close()
            except:
                self.debugFileName = None
        else:
            self.debugFileName = None
    def write(self, text):
        self.debugWindow.add(text)
        if self.debugFileName:
            try:
                f = open(self.debugFileName, 'at')
                try:
                    f.write(text)
                finally:
                    f.close()
            except:
                pass
    def flush(self):
        pass

#
# a sys.stderr and sys.stdout replacement stream to collect all
# outputs in a local buffer. That prevents the generation of
# a log file and message box when py2exe is used
# the buffer is flushed to a program-defined log file (py2exe independent)
#
class DebugBlackholeBufferRedirector(object):
    softspace = 0
    buffer = ''
    def __init__(self, oldstream, logdir = None):
        self.oldstream = oldstream
        self.set_logdir(logdir)
    def set_logdir(self, logdir):
        #
        # redirected output to a debug file in the log dir/home dir because
        # users with restricted system rights can't write to the installation directory
        # which is the default if py2exe is used
        #
        if logdir:
            from locale import getdefaultlocale
            defaultLang, defaultEnc = getdefaultlocale()
            if defaultEnc is None:
                defaultEnc = 'UTF-8'
            self.debugFileName = os.path.join(logdir, 'griffith.log')
        else:
            self.debugFileName = None
    def write(self, text):
        try:
            log.info(text)
            self.buffer = string.join([self.buffer, text])
        except Exception as e:
            # resetting to old output streams as last hope
            sys.stdout = sys.stderr = self.oldstream
            print(str(e))
    def flush(self):
        if self.debugFileName and self.buffer:
            logfile = open(self.debugFileName, 'at')
            try:
                logfile.write(self.buffer)
                self.buffer = ''
            finally:
                logfile.close()

GriffithDebug = GriffithDebug()
