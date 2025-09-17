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

import html
import mimetypes
from abc import (ABC, abstractmethod)

from .StringBuilder import StringBuilder
from .webutilerror import WebUtilError


__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__myname__ = 'PageItem'


class PageItem(ABC):
    """
    Base class for html tags
    """

    def __init__(self, name='unknown', id='', class_name=None, title=None):
        self.jsevents = ["onkeydown", "onkeypress", "onkeyup", "onblur", "onchange", "onfocus",
                         "onreset", "onselect", "onsubmit", "onclick", "ondblclick", "onmousedown",
                         "onmousemove", "onmouseover", "onmouseout", "onmouseup", "onabort"]
        self.name = name
        self.id = id
        self.class_names = set()
        if class_name:
            if isinstance(class_name, list) | isinstance(class_name, set):
                self.class_names.update(class_name)
            elif isinstance(class_name, str):
                self.class_names.add(class_name)
        self.styles = dict()
        self.events = dict()
        self.title = title if title else ''
        self.disabled = False   # start with it available

    @abstractmethod
    def get_html(self):
        """Each item must define this method to return a complete html tag

        :return: simple string with the html tag

        :raises: WebUtilError
        """
        return ''

    def update_header(self, page):
        """ This method is called before adding its html. If the item needs a javascript or css file
        to be added to the header it can be done here

        :param: page, the relevant Page object

        :raises: WebUtilError
        """
        pass

    def get_classname(self):
        return ' '.join(self.class_names)

    def add_classname(self, cname):
        """
        Add a class to the tag attributes for CSS

        :param str cname: class name

        :return: None
        """
        self.class_names.add(cname)

    def add_event(self, evt_name, call):
        """Add a call to a javascript routine on a specific event like click

        :param str evt_name: name of event see list in __init__

        :param str call: name of jacascript function to call

        :return: None

        :raises: WebUtilError if event is not recognized"""

        if evt_name not in self.jsevents:
            raise WebUtilError('Unknown event: {} for {}'.format(evt_name, self.name))
        if evt_name in self.events.keys() and self.events[evt_name] != call:
            raise WebUtilError('Conflicting calls for {} event on {}. "{}" vs. "{}"'.
                               format(evt_name, self.name, call, self.events[evt_name]))
        self.events[evt_name] = call

    def add_style(self, style, val):
        """Add a CSS like styles to this tag
        :param str style: name of styles as defined in the page's styles sheet
        :param str val: value for the setting
        :returns: None
        :raises: WebUtilError if styles is already set"""

        if style in self.styles and self.styles[style] != val:
            raise WebUtilError('Conflicting calls for {} event on {}. "{}" vs. "{}"'.
                               format(style, self.name, val, self.styles[style]))
        self.styles[style] = val

    def get_attributes(self):
        """Generat the common attributes fot this tag

        :returns str: common attributes
        """
        ret = ''

        if self.name and self.name != 'unknown':
            ret += f' name="{self.name}" '
        if self.id:
            ret += f' id="{self.id}" '

        if self.class_names:
            clas = ' '.join(self.class_names)
            ret += ' class="' + clas + '" '

        if self.styles:
            ret += ' style="'
            for sty, val in self.styles.items():
                ret += sty + ':' + val + ';'
            ret += '" '

        if self.title:
            ret += ' title="{self.title}" '

        for ev, call in self.events.items():
            ret += f' {ev} = "{call}" '

        if self.disabled:
            ret += ' disabled '

        return ret

    @staticmethod
    def escape(instr):
        """Escape a string for html

        :param str instr: string to escape

        :returns str: escaped string
        """
        ret = html.escape(instr)
        return ret

    @staticmethod
    def get_page_item(thing):
        """
        Many methods need a PageItem subclass. This method will verify the argument is a PageItem
        if not it creates and returns a PageItemString

        :param thing: aPageItem or any Python construct that can be converted to a string

        :return: a PageItem representng the thing

        :raises: WebUtilError if string conversion fails
        """
        try:

            if thing is None or isinstance(thing, PageItem):
                it = thing
            else:
                it = PageItemString(thing)
        except TypeError as ex:
            raise WebUtilError('Problem creating a PageItemString from a {}'.format(type(thing)), ex)
        return it


class PageItemBlanks(PageItem):
    """Class representing 1 or more blank lines"""

    def __init__(self, n=1):
        """
        :param int n: number of blank lines

        :returns: None
        """
        super().__init__()
        self.n = n

    def get_html(self):
        ret = ''
        for i in range(0, self.n):
            ret += '<br>'
        ret += '\n'
        return ret


class PageItemHeader(PageItem):
    """"HTML header is a CSS class for emphasis"""

    def __init__(self, text=None, level=1, name=None, **kwargs):
        """

        :param text: Header text (it will be escaped, no html here)

        :param level: Header level 1-6 are used by browsers
        """
        super().__init__(**kwargs)
        self.text = self.escape(text)
        self.level = max(1, min(level, 6))
        self.name = name

    def get_html(self):
        ret = f'<h{self.level:1d} {self.get_attributes()}>{self.text}</h{self.level:1d}>\n'
        return ret


class PageItemHorizRule(PageItem):
    """Class representing a hoizontl rule"""
    def get_html(self):
        return '<hr/>\n'


class PageItemImage(PageItem):
    """
    Class representing an image in the page
    """

    def __init__(self, url=None, alt_text=None, width=None, height=None, mime=None, **kwargs):
        """

        :param url: Image URI

        :param str alt_text: any alternate text

        :param int width: specify image horizontal size

        :param int height: specify image vertical size

        :param str mime: mime type of the image or pdf

        :param kwargs:
        """

        super().__init__(**kwargs)
        self.url = url
        self.mime = mime
        if url and not mime:
            mimetype = str(mimetypes.guess_type(url))
            self.mime = mimetype

        self.alt_text = alt_text
        self.width = width
        self.height = height

    def get_html(self):
        """
        Get the HTML representation

        :return: str with html of this image
        """
        ret = StringBuilder()

        if self.url and not self.mime:
            mimetype = mimetypes.guess_type(self.url)
            self.mime = mimetype
        if not self.mime or 'image' in str(self.mime).lower():
            ret += f'<img draggable="true" {self.get_attributes()} data-src="{self.url}" '
            if self.alt_text:
                ret += 'alt="{}" '.format(self.alt_text)
            if self.width:
                ret += ' width="{}" '.format(self.width)
            if self.height:
                ret += ' height="{}" '.format(self.height)
            ret += '/>\n'
        elif self.mime and 'pdf' in str(self.mime).lower():
            ret += '<object {} data="{}" type="{}" />'.format(self.get_attributes(), self.url, self.mime)
            if self.alt_text:
                ret += 'Your browser does not appear to have the ability to ' \
                       'display this pdf alt="{}" '.format(self.alt_text)
            ret += '<a href="{}">Click here</a> to download the documemt'.format(self.url)
            ret += '</object>'
        else:
            raise WebUtilError('Image object {} has unknown or missing mime type'.format(self.url))
        return str(ret)


class PageItemLink(PageItem):
    """
    Class representing a clickable image as a link
    """

    def __init__(self, url=None, contents=None, target=None, **kwargs):
        """

        :param str url: end point of the link
        :param PageItem | str contents: image to display or string
        :param target: where to open the link eg: '_blank' for new window or tab
        :param kwargs: passed to PageItem base class
        """
        super().__init__(**kwargs)
        self.url = url
        self.contents = contents if isinstance(contents, PageItem) else PageItemString(contents)
        self.target = target

    def get_html(self):
        """
        get the html for this object
        :return: str html to add to the page
        """
        if not self.url or not self.contents:
            raise WebUtilError('PageItemImageLink: missing url (link) and/or image')

        ret = StringBuilder()
        ret += '<a {} href="{}" '.format(self.get_attributes(), self.url)
        if self.target:
            ret += 'target="{}" '.format(self.target)
        ret += '>{}</a>'.format(self.contents.get_html())
        return str(ret)


class PageItemArray(PageItem):
    """
    A list of PageItems that can be used anywhere a single Item can. Array so it is not
    confused with PageItemList which is an HTML ordered or unordered list
    """

    def __init__(self, use_div=False, **kwargs):
        super().__init__(**kwargs)
        self.contents = list()
        self.use_div = use_div or kwargs

    def add(self, thing):
        """
        add an item to the list

        :param thing: A PageItem subclass or anything that can be converted to a string

        :return PageItemList: this object ref so adds can be chained
        """
        it = self.get_page_item(thing)
        self.contents.append(it)

    def update_header(self, page):
        """
        Give each item in this array a chance to add to headers

        :param Page page: the Page object we are a part of

        :return: None
        """
        for pi in self.contents:
            if isinstance(pi, PageItem):
                pi.update_header(page)

    def get_html(self):
        """
        Get html representing every PageItem in the array
        :return str: the html representation of these  items
        """
        ret = StringBuilder()
        attr = self.get_attributes()

        closer = ''
        if self.use_div or attr:
            ret += '<div {}>\n'.format(attr)
            closer = '</div>\n'
        for pi in self.contents:
            pi_html = pi.get_html()
            ret += pi_html

        ret += closer
        return ret


class PageItemList(PageItem, ABC):
    """
    A base class for HTML Ordered [number] and Unordered (bullet) list
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contents = list()
        self.use_div = True

    def add(self, thing):
        """
        Add an item to the list

        :param thing: A PageItem object or a Python construct that can be converted to a string

        :return PageItemList: reference to this object so add calls can be chained
        """
        it = PageItem.get_page_item(thing)
        self.contents.append(it)
        return self

    @abstractmethod
    def tag_open(self):
        """
        Get the tag opening eg: <ol type=I> or <ul style="list-style-type:circle";>

        :return str: opening tag
        """

    @abstractmethod
    def tag_close(self):
        """
        get list closing tag

        :return str: closing tag
        """

    def get_html(self):
        """
        Generate html for this item

        :return str: the html
        """
        ret = StringBuilder()
        ret += '<div>\n' if self.use_div else ''
        ret += self.tag_open()
        for pi in self. contents:
            ret += f'<li>{pi.get_html()}</li>\n'
        ret += self.tag_close()
        ret += '</div>\n' if self.use_div else ''

        return str(ret)


class PageItemUList(PageItemList):
    """
    Class representing an HTML unordered (bulleted) list
    """

    def __init__(self, marker='disc', **kwargs):
        """
        :param marker: one of the valid marker styles

        :see: https://www.w3schools.com/html/html_lists_unordered.asp
        """
        super().__init__(**kwargs)
        valid_markers = ['disc', 'circle', 'square', 'none']
        if marker not in valid_markers:
            raise WebUtilError('Invalid marker [{}] for Unordered list. Options are {}'.
                               format(marker, ', '.join(valid_markers)))
        self.marker = marker

    def tag_open(self):
        """
        Generate opening tag for this list

        :return str: html opening tag
        """
        return '<UL style="list-style-type:{};">'.format(self.marker)

    def tag_close(self):
        """
        close the UL tag

        :return str: closing tag
        """
        return '</UL>\n'


class PageItemOList(PageItemList):
    """
    Class representing an HTML unordered (bulleted) list
    """

    def __init__(self, type='1', reversed=False, start=None, **kwargs):
        """
        :param marker: one of the valid marker styles

        :see: https://www.w3schools.com/html/html_lists_unordered.asp
        """
        super().__init__(**kwargs)
        valid_types = ['1', 'A', 'a', 'I', 'i']
        if str(type) not in valid_types:
            raise WebUtilError(f'Invalid ordered list type. Valid types: {", ".join(valid_types)}')
        self.type = type
        self.reversed = reversed
        self.start = start

    def tag_open(self):
        """
        Generate opening tag for this list

        :return str: html opening tag
        """

        otag = f'<OL type="{self.type}" '
        otag += ' reversed ' if self.reversed else ''
        otag += f' start="{self.start}" ' if self.start else ""
        otag += '>'
        return otag

    def tag_close(self):
        """
        close the  tag

        :return str: closing tag
        """
        return '</OL>\n'


class PageItemString(PageItem):
    """Class representing a string or a paragraph"""

    def __init__(self, thing=None, escape=True, paragraph=False, **kwargs):
        """
        :param thing: Any python object that can be passed to str()

        :param escape: Set to false if html is in the string, otherwise escape all special characters
        """
        super().__init__(**kwargs)
        self.text = str(thing)
        self.escaped = escape
        self.paragraph = paragraph
        if escape:
            self.text = self.escape(self.text)

    def get_html(self):
        begin = ''
        end = ''
        attr = self.get_attributes()
        if attr:
            begin = '<p ' + attr + '> '
            end = '</p>\n'
        ret = begin + self.text + end
        return ret


class PageItemRadioButton(PageItem):
    """
    Radio buttons select one from a list
    see: https://www.w3schools.com/tags/att_input_type_radio.asp
    """

    def __init__(self, prompt=None, options=None, **kwargs):
        """
        :param str prompt: title text for rado group
        :param list options: options are tuples (<id>, <label>, <value>)
        be sure to set name if there will be more than oe radio group
        """
        super().__init__(**kwargs)
        self.prompt = prompt
        self.options = options if options else list()

    def add_option(self, id, label, value):
        """
        param str label: text user will see
        param str value: text returned if selected
        """
        self.options.append((id, label, value))

    def get_html(self):
        ret = ''
        if len(self.class_names) > 0:
            cnames = " ".join(self.class_names)
            cls_str = f' class="{cnames}" '
        else:
            cls_str = ''
        if self.prompt:
            if isinstance(self.prompt, str):
                self.prompt = PageItemString(self.prompt, paragraph=True)
                for cls_nam in self.class_names:
                    self.prompt.add_classname(cls_nam)
            ret += self.prompt.get_html()
            brk = PageItemBlanks()
            ret += brk.get_html()

        for opt in self.options:
            opt_html = f'<input type="radio" id="{opt[0]}" name="{self.name}" value="{opt[2]}" {cls_str}'
            for evnt, call in self.events.items():
                opt_html += f' {evnt} = "{call}" '

            opt_html += f'>\n<label for="{opt[0]}" {cls_str}>{opt[1]}</label><br>\n'
            ret += opt_html

        ret += '<br>\n'
        return ret


class PageItemVideo(PageItem):

    def __init__(self, src=None, autoplay=None, controls=None, height=None, loop=None, muted=None, poster=None,
                 preload=None, width=None, **kwargs):
        """
        Define video tag
        :param url src: location of video
        :param bool autoplay: Specifies that the video will start playing as soon as it is ready
        :param bool controls: Specifies that video controls should be displayed (such as a play/pause button etc)..
        :param int height: Sets the height of the video player in pixels
        :param bool loop: Specifies that the video will start over again, every time it is finished
        :param bool muted: Specifies that the audio output of the video should be muted
        :param url poster: Specifies an image to be shown while the video is downloading, or until the user
                           hits the play button
        :param str preload: Specifies if and how the author thinks the video should be loaded when the page loads
                            auto, metadata, or none
        :param int width: Sets the width of the video player
        :param kwargs: passed to :meth: ~ja_webutils.PageItem.__init__

        """
        super().__init__(**kwargs)
        self.src = src
        self.autoplay = autoplay
        self.controls = controls
        self.height = height
        self.loop = loop
        self.muted = muted
        self.poster = poster
        self.preload = preload
        self.width = width

    def get_html(self):
        ret = f'<video {self.get_attributes()} src="{self.src}" '

        if self.autoplay is not None:
            ret += f"autoplay={self.autoplay} "
        if self.controls is not None:
            ret += f"controls={self.controls} "
        if self.height is not None:
            ret += f"height={self.height} "
        if self.loop is not None:
            ret += f"loop={self.loop} "
        if self.muted is not None:
            ret += f"muted={self.muted} "
        if self.poster is not None:
            ret += f'poster="{self.poster}" '
        if self.preload is not None:
            ret += f"preload='{self.preload}' "
        if self.width is not None:
            ret += f"width={self.width} "

        ret += '>'
        return ret
