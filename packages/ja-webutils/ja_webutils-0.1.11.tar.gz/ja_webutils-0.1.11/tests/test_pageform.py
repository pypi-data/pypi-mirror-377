# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2022 Joseph Areeda <joseph.areeda@ligo.org>
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

"""[doc string]"""

from ja_webutils.PageForm import (PageFormRadio, PageFormSelect)

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__name__ = 'test_pageform'


class TestPageForm:

    def test_pageform_radio(self):
        radio = PageFormRadio()
        radio.add('rad1', 'apple')
        radio.add('rad1', 'orange', True)
        radio.add('rad1', 'banana')
        html = radio.get_html()
        assert len(html) > 0

    def test_pageform_select(self):
        select = PageFormSelect(name='tstsel', prompt='drop menu', id='menu1', opts=['dog', 'cat', 'gerbil'])
        select.add('parrot')
        select.add(('spider', 'arachnid', True))
        html = select.get_html()
        assert len(html) > 0
