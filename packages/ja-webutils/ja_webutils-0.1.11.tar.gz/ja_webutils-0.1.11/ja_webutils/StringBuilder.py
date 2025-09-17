# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2021 Joseph Areeda <joseph.areeda@ligo.org>
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

"""Class to efficiently concatenate lots of small strings"""

import io

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__myname__ = 'StringBuilder'


class StringBuilder:
    """
    Efficient way to build long strings.

    Example:
    ========
        sb = StringBuilder()
        sb.add('foo ').add(5.2).add(' bar')
        print(sb.get_str())
    or equivalently
        sb = StringBuilder()
        sb + 'foo' + 5.2 + ' bar'
        print(str(sb))
    """
    def __init__(self):
        self._writer = io.StringIO()

    def add(self, thing):
        """
        Add string to the buffer
        :param thing: any Python construct that can be converted to a string
        :return: the StringBuilder object
        """
        self._writer.write(str(thing))
        return self

    def __add__(self, other):
        """
        Allow use of + operator to add a string to buffer
        :param other: any Python construct that can be converted to a string
        :return: this object
        """
        self._writer.write((str(other)))
        return self

    def __str__(self):
        """
        Get the buffer
        :return: srtring value of current buffer
        """
        return self._writer.getvalue()

    def get_str(self):
        """
        Get current buffer
        :return: string value of current buffer
        """
        return self._writer.getvalue()
