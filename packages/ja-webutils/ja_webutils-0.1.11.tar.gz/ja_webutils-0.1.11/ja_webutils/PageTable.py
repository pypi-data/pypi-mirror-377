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
import itertools

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__myname__ = 'PageTable'

from enum import Enum

from ja_webutils.PageItem import PageItem
from ja_webutils.StringBuilder import StringBuilder


class PageTable(PageItem):
    """
    Represents an HTML table with jQuery support for sorting
    Attributes:
    """
    hdr_rows = list()
    __doc__ += """hdr_rows: Header body_rows are not sorted and are different CSS objects"""
    body_rows = list()
    __doc__ += """body_rows: body pf the table"""
    footer_rows = list()
    __doc__ += """footer_rows: footers are not sorted"""
    sorted = False
    __doc__ += """sorted: True -> use jQuery's table sorter"""
    zebra = False
    __doc__ += """zebra: True -> alternating background for body body_rows"""
    width = 0
    __doc__ += """width: table width usually as % of page"""
    width_pct = False
    __doc__ += """width_pct: if width is specified is it % of page or pixels"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hdr_rows = list()
        self.body_rows = list()
        self.footer_rows = list()
        self.sorted = False
        self.zebra = False
        self.width = 0
        self.width_pct = False

    def get_row_count(self):
        """

        :return int: number of body_rows in table
        """
        ret = len(self.hdr_rows) + len(self.body_rows) + len(self.footer_rows)
        return ret

    def add_row(self, row, **kwargs):
        """
        Add a row (header, footer, body) or somthing that can be coerced into a PageItem to table

        :param row: object to add
        :param kwargs: if object is not a PageTableRow it is passed to row created
        :return PageTable: self so adds may be chained
        """
        it = row
        if not isinstance(row, PageTableRow):
            it = PageTableRow()
            it.add(row, **kwargs)
        if it.row_type is RowType.HEAD:
            self.hdr_rows.append(it)
        elif it.row_type is RowType.BODY:
            self.body_rows.append(it)
        elif it.row_type is RowType.FOOT:
            self.footer_rows.append(it)
        else:
            raise TypeError(f'Unknown row type in table {self.name}: {it.row_type}')

    def set_sorted(self, sorted=True, zebra=True):
        """
        Add appropriate javascript to sort this table
        :param bool sorted: set or clear sorted flag
        :param bool zebra: whether backgrounds alternat for even/odd rows
        :return PageTable: self pointer to allow chaining
        """
        self.sorted = sorted
        self.zebra = zebra

    def set_zebra(self, zebra=True):
        self.zebra = zebra

    def update_header(self, page):
        for row in itertools.chain(self.hdr_rows, self.body_rows, self.footer_rows):
            row.update_header(page)
        if self.sorted:
            self.add_classname('tablesorter')
            page.include_js_cdn('jquery')
            page.include_js_cdn('tablesorter')
            page.include_css_cdn('theme_blue')
            page.add_headjs('$(function() '
                            '{'
                            '    $("table").tablesorter({'
                            '      theme: "blue",'
                            '      widgets: ["zebra"],'
                            '      widgetOptions : {'
                            '        zebra : [ "odd", "even" ]'
                            '      }'
                            '     });'
                            '});')
        if self.zebra:
            page.add_style('tr.odd td.odd {background-color:#cbd1dc;padding-right: 12px;border-color: darkblue}'
                           'tr.even td.even {background-color:#fff;padding-right: 12px;border-color: darkblue}')
            odd = True
            for row in self.body_rows:
                row.set_class_all('odd' if odd else 'even')
                odd = not odd

    def set_class_all(self, cls_name):
        for row in itertools.chain(self.hdr_rows, self.body_rows, self.footer_rows):
            row.set_class_all(cls_name)

    def get_html(self):
        ret = StringBuilder()
        ret += f'<table {self.get_attributes()} '
        if self.width > 0:
            ret += f' style="width={self.width:d}' + '% ' if self.width_pct else 'px '
        ret += '>\n'

        if self.hdr_rows:
            ret += '  <thead>\n'
            for row in self.hdr_rows:
                ret += f'    {row.get_html()}'
            ret += '  </thead>'

        ret += ' <tbody>\n'
        for row in self.body_rows:
            ret += f'    {row.get_html()}'
        ret += '  </tbody>\n'

        if self.footer_rows:
            ret += '  <tfoot>\n'
            for row in self.footer_rows:
                ret += f'    {row.get_html()}'
            ret += '  </tfoot>\n'

        ret += '</table>\n'
        return str(ret)


class RowType(Enum):
    """
    Row types specify html tags
    see: https://www.w3schools.com/tags/tag_table.asp
    """
    HEAD = '<thead>'
    BODY = '<tbody>'
    FOOT = '<tfoot>'


class PageTableRow(PageItem):
    """
    Represents a row in an html table
    Attributes:
    """
    row_type = RowType.BODY
    __doc__ += """row_type: Where in the table to put this row, and whether to include in sorting"""
    cells = list()
    __doc__ += """cells: make up the colums in this row"""

    def __init__(self, thing=None, row_type=RowType.BODY, **kwargs):
        """
        Create a new row
        :param RowType row_type: header, body or footet
        :param thing: a single or array of things that can be coerced a PageTableCell
        :param kwargs: passed to PageTableCell
        """
        super().__init__(**kwargs)
        self.cells = list()
        self.row_type = row_type
        if thing:
            self.add(thing, **kwargs)

    def add(self, thing, **kwargs):
        """
        Add one or more cells to this row
        :param thing: anything that can be coerced to a PageTableCell
        :param kwargs: passed to PageTableCell
        :return:
        """
        it = None
        if isinstance(thing, PageTableCell):
            self.cells.append(thing)
        elif isinstance(thing, list):
            for it in thing:
                self.add(it, **kwargs)
        else:
            it = PageTableCell(thing, **kwargs)
            self.cells.append(it)

    def column_count(self):
        """

        :return int: Number of columns in this row
        """
        return len(self.cells)

    def set_row_type(self, rt):
        """
        Define where this row will be in the table, head, body or foot
        :param RowType rt: type of row or string
        :return:  None
        """
        if isinstance(rt, RowType):
            self.row_type = rt
        else:
            self.row_type = RowType[rt]

    def set_class_all(self, cls_name):
        """
        Set the CSS class of the row and all cells in the row. Commonly use to remove borders or
        set background color
        :param str cls_name: the name of the class
        :return:
        """
        self.add_classname(cls_name)
        for cell in self.cells:
            cell.add_classname(cls_name)

    def get_html(self):
        """get the html for this row"""
        ret = StringBuilder()
        tag = 'tr' if self.row_type is RowType.HEAD else 'tr'
        ret += f'  <{tag} {self.get_attributes()}>\n'
        for cell in self.cells:
            cell.row_type = self.row_type
            ret += f'    {cell.get_html()}\n'
        ret += f'  </{tag}>\n'
        return str(ret)

    def update_header(self, page):
        """
        Give  our cells a chance to add CSS, javascript ... to page header
        :param Page page:  our page
        :return:
        """
        cell: PageTableCell
        for cell in self.cells:
            if cell.contents is not None:
                cell.update_header(page)


class PageTableCell(PageItem):
    """
    Representing a cell in an HTML table
    Attributes:
    """
    contents = None
    __doc__ += """contents: May be any PageItem including an Array or another Table"""
    col_span = 1
    __doc__ += """col_span: how many columns does this cell use"""
    row_span = 1
    __doc__ += """row_span: how many body_rows does this cell use"""
    row_type = RowType.BODY
    __doc__ += """row_type: tag depends on where the row is in the table"""

    def __init__(self, thing=None, col_span=0, row_span=0, row_type=RowType.BODY, **kwargs):
        super().__init__(*kwargs)
        self.contents = PageItem.get_page_item(thing)
        self.col_span = col_span
        self.row_span = row_span
        self.row_type = row_type

    def get_html(self):
        ret = StringBuilder()
        tag = 'th' if self.row_type is RowType.HEAD else 'td'
        ret += f'<{tag} {self.get_attributes()} '
        ret += f' colspan="{self.col_span:d}" ' if self.col_span > 1 else ''
        ret += f' rowspan="{self.row_span:d}" ' if self.row_span > 1 else ''
        ret += '>\n    '
        if self.contents is not None:
            ret += self.contents.get_html()
        else:
            ret += 'None'
        ret += f'\n     </{tag}>\n'

        return str(ret)

    def update_header(self, page):
        self.contents.update_header(page)
