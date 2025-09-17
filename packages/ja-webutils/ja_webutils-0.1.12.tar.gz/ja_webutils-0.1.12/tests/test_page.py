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
from pathlib import Path
from ja_webutils.Page import Page

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__name__ = 'test_page'

from ja_webutils.PageForm import PageForm, PageFormText, PageFormButton, \
    PageFormCheckBox

from ja_webutils.PageItem import PageItemString, PageItemHeader, \
    PageItemHorizRule, PageItemUList, PageItemOList
from ja_webutils.PageTable import PageTable, PageTableRow, RowType


class TestPage:
    OUTDIR = Path('/tmp/webutilstest')
    OUTDIR.mkdir(exist_ok=True)

    def test_min(self):
        page = Page()
        self.check_save(page, 'min')

    def check_save(self, page, name):
        html = page.get_html()

        assert len(html) > 0

        with open(self.OUTDIR / (name + '_page.html'), 'w') as out:
            print(html, file=out)

    def get_page(self, title):
        page = Page()
        my_styles = [
            'body{background-color: #CFF3FC;}',
            '.bold{font-weight: bold;font-size: 1.2em;}',
            'th{background-color: lightgreen;}',
            '.center {text-align: center; border: 3px solid green;}',
            'tr.odd td.odd {background-color:#cbd1dc;padding-right: 12px;border-color: darkblue}',
            'tr.even td.even {background-color:#fff;padding-right: 12px;border-color: darkblue}',
        ]
        for style in my_styles:
            page.add_style(style)
        page.title = title
        h1 = PageItemHeader(title, 1, class_name='center')
        page.add(h1)
        page.add_blanks(2)
        return page

    def test_small(self):
        page = Page()
        page.title = 'Small page'
        page.add('Hello world')
        self.check_save(page, 'small')

    def test_big(self):
        page = self.get_page('Big page')
        s1 = PageItemString('bold test')
        s1.add_classname('bold')
        page.add(s1)
        page.add_blanks(1)
        page.add('Normal text no line break')
        page.add(PageItemString(' more text<br>', escape=False))
        page.add_blanks(1)
        page.add_line('Indented text:')
        page.add_style('.indent{ margin-left: 5em; }')
        paragraph = PageItemString('Instead, you can take all your CSS code and '
                                   'place it a separate file, with the extension '
                                   '.css. Then, you can link to this one file '
                                   'from any HTML document, and that document can '
                                   'use those CSS properties. Using an external CSS '
                                   'file make it easier to change the CSS later,'
                                   ' because all the CSS is defined in one place.')
        paragraph.add_classname('indent')
        page.add(paragraph)
        page.add_blanks(2)

        page.add(PageItemHeader('header level 1', 1))
        page.add(PageItemHeader('header level 2', 2))
        page.add(PageItemHeader('header level 3', 3))
        page.add(PageItemHeader('header level 4', 4))

        page.add(PageItemHorizRule())
        page.add('Unordered list')
        page.add_blanks()
        ul = PageItemUList()
        ul.add('Apple')
        ul.add('Orange')
        ul.add('Banana')
        page.add(ul)
        page.add_blanks(2)

        page.add('Unordered list 2')
        page.add_blanks()
        ul = PageItemUList(marker='square')
        ul.add('Dog')
        ul.add('Cat')
        ul.add('Hamster')
        page.add(ul)

        page.add(PageItemHorizRule())
        page.add('Ordered list')
        page.add_blanks()
        ul = PageItemOList()
        ul.add('Apple')
        ul.add('Orange')
        ul.add('Banana')
        page.add(ul)
        page.add_blanks(2)

        page.add('Ordered list 2')
        page.add_blanks()
        ul = PageItemOList(type='I')
        ul.add('Dog')
        ul.add('Cat')
        ul.add('Hamster')
        page.add(ul)

        page.add(PageItemHorizRule())
        page.add(PageItemHeader('Forms', 3))
        form = PageForm(name='form1', id='form1', action='form_proc.html', method='get')

        form.add('Text area:')
        form.add_line(PageFormText(id='ta1'))
        form.add('Text w/default')
        form.add_line(PageFormText(id='ta2', default_value='my default'))
        form.add('Text w/place holder')
        form.add_line(PageFormText(id='ta2', place_holder='my place holder'), 2)
        form.add('multi-line editable: ')
        pft = PageFormText(name='ta4', id='ta4', default_value="Large text area")
        pft.add_classname('editable')
        pft.nlines = 4
        pft.use_editor = True
        form.add_line(pft, 2)

        form.add('Checkbox: ')
        form.add_line(PageFormCheckBox(name='chkbox', id='cbox', txt='Single'))
        form.add('Checkbox: ')
        form.add_line(PageFormCheckBox(name='chkbox2', id='cbox2', checked=True, txt='Happy'))

        form.add(PageItemHeader('Bunch-o-buttons', 3))
        button = PageFormButton(name='but1', contents='My 1st button', value='b1')
        button.type = 'submit'
        form.add_line(button)

        button = PageFormButton(name='but2', contents='button type button', type='button')
        form.add_line(button)

        button = PageFormButton(name='but3', contents='button type reset',
                                type='reset')
        form.add_line(button)

        # add the form and validate
        page.add(form)
        self.check_save(page, 'big')

    def test_table(self):
        page = self.get_page('Test tables')
        page.add_style('.border {padding:3px;border:1px solid black;'
                       'border-collapse: collapse;text-align:center;vertical-align:bottom;}')
        rows = [
            [1, 1.0, 'first row'],
            [2, 2.0, 'second row'],
            [3, 3.0, 'third row'],
        ]
        t1 = PageTable(id='t1')
        for row in rows:
            t1.add_row(row)
        t1.set_class_all('border')
        page.add(t1)
        page.add_blanks(2)

        hdr = ['int', 'flt', 'str']
        t2 = PageTable(id='t2')
        t2.set_zebra()
        for row in rows:
            t2.add_row(row)
        hdr_row = PageTableRow(hdr, RowType.HEAD)
        t2.add_row(hdr_row)
        t2.set_class_all('border')
        page.add(t2)

        page.add_blanks(2)
        t3 = PageTable(id='t3')
        t3.set_sorted()
        for row in rows:
            t3.add_row(row)
        hdr_row = PageTableRow(hdr, RowType.HEAD)
        t3.add_row(hdr_row)
        t3.set_class_all('border')
        page.add(t3)

        self.check_save(page, 'tables')
