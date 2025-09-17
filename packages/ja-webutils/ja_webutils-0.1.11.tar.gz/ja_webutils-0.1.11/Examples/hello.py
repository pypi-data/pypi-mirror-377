#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2023 Joseph Areeda <joseph.areeda@ligo.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Simple hello world app"""
import webbrowser
from pathlib import Path

from ja_webutils.Page import Page

page = Page()
page.title = 'Hello'

page.add('Hello world')

html = page.get_html()

ofile = Path('/tmp/ja_webutils_example_1.html')
with ofile.open('w') as ofp:
    print(html, file=ofp)

webbrowser.open_new_tab(f'file://{ofile.absolute()}')
