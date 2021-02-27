Griffith 1.13.0 README
======================

This document was last updated on Feb 27 2021.
Please see the file COPYING for licensing and warranty information.


Table of Contents
=================

* Introduction
* System Requirements
* Installation
* Reporting Bugs
* TODO list
* About the Authors

Updates
=======
Finished IMDB plugin.
Languages are now sorted before lising in Add mode.
Imdb plugin now uses Imdb library instead of parsing web site.
Added extra options in Technical tab of Add movie.
Added extra languages and other options when creating a new database.

Introduction
============

Griffith is a film collection manager, released under the MIT License.


Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


System Requirements
===================

  Name			Minimum version		URL						NOTE
  ----			---------------		---						----
  * Python		3.6 or higher		http://www.python.org/
  * GTK+		tested on 2.8.6		http://www.gtk.org/
  * PyGTK (with glade3)	2.6.8		http://www.pygtk.org/
  * SQLAlchemy		0.5			http://www.sqlalchemy.org/
  * pysqlite2		2			http://initd.org/tracker/pysqlite		Python 2.5's sqlite3 module will be used if available
  * ReportLab		1.19			http://www.reportlab.org

Other (optional) dependencies:
------------------------------

  PostgreSQL support:
  * Psycopg2		2			http://initd.org/tracker/psycopg/wiki/PsycopgTwo
  MySQL support:
  * MySQLDb					http://sourceforge.net/projects/mysql-python
  Upgrading from Griffith <=0.6.2 (only if pysqlite 1.0 was used before, 1.1 is not needed)
  * pysqlite		1.0 			http://initd.org/tracker/pysqlite
  Encoding detection of imported CSV file support:
  * chardet					http://chardet.feedparser.org/
  Gtkspell:
  * python-gnome-extras
  Covers and reports support:
  * PDF reader

To check dependencies:
----------------------
  $ ./griffith --check-dep

To show detected Python modules versions:
-----------------------------------------
  $ ./griffith --show-dep

Windows installer includes all the needed requirements.
A GTK+ runtime is not necessary when using this installer.


External databases
==================

You need to prepare a new database and a new user by yourself

PostgreSQL
----------

	CREATE USER griffith UNENCRYPTED PASSWORD 'gRiFiTh' NOCREATEDB NOCREATEUSER;
	CREATE DATABASE griffith WITH OWNER = griffith ENCODING = 'UNICODE';
	GRANT ALL ON DATABASE griffith TO griffith;

MySQL
-----

	CREATE DATABASE `griffith` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
	CREATE USER 'griffith'@'localhost' IDENTIFIED BY 'gRiFiTh';
	CREATE USER 'griffith'@'%' IDENTIFIED BY 'gRiFiTh';
	GRANT ALL ON `griffith` . * TO 'griffith'@'localhost';
	GRANT ALL ON `griffith` . * TO 'griffith'@'%';

Microsoft SQL Server
--------------------
	CREATE DATABASE griffith
	EXEC sp_addlogin @loginame='griffith', @passwd='gRiFiTh', @defdb='griffith'
	GO
	USE griffith
	EXEC sp_changedbowner @loginame='griffith'


Installation
============

See INSTALL file


Reporting Bugs
==============

If you want to help or report any bugs founded please visit:
  http://www.griffith.cc/
or
  https://bugs.launchpad.net/griffith/


TODO
====

See TODO file


About the Authors
=================

See AUTHORS file
