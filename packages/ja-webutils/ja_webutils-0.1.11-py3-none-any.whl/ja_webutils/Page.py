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


import datetime
import pytz
import time
from .PageItem import (PageItem, PageItemString, PageItemBlanks)
from .StringBuilder import StringBuilder

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__myname__ = 'Page'

from .webutilerror import WebUtilError


class Page:
    """Top level class representing a html page"""

    def __init__(self):
        #: Page title
        self.title = ""
        self.docType = "<!DOCTYPE html>"
        self.contentType = "text/html"  # default
        self.charset = "UTF-8"
        self.className = ""
        self.refreshInterval = -1  # for automatic refresh, interval in seconds
        self.refreshURL = None  # for automatic refresh optional url

        self.head = list()
        self.body = list()
        self.foot = list()

        self.jsRoot = None  # directory containing our java script files
        self.cssRoot = None  # directory containing our css files
        self.jsIncludes = list()  # paths for javascript includes
        self.cssIncludes = list()  # paths for css includes
        self.styles = list()  # styles tag entries

        self.headJs = list()  # in-line javaScript routines for _head section
        self.bodyJs = list()  # in-line javaScript routines for _body section
        self.readyJs = list()  # init scripts run when jQuery(document).ready
        self.loadJs = list()  # init scripts run when page is fully loaded

        self.addStats = True  # whether or now we should add page time/queries to footer
        self.crTime = time.time()  # System time our constructor was called
        self.queryCount = None  # Set externally to the number of db queries used to create the page
        self.lastCSS = None

    @staticmethod
    def get_page_item(thing):
        """
        Return a PageItem object of the parameter. If it's not a PageItem object
        constrct a PageItemString

        :param thing: a PageItem object or any Python construct that can be converted to a string

        :return: a PageItem
        """
        if isinstance(thing, PageItem):
            ret = thing
        else:
            ret = PageItemString(thing)
        return ret

    def add(self, thing):
        """Add a PageItem object to the _body of the Page. As aconvenience if
         we are passed a non-PageItem object it will be converted first to an escaped PageItemString.

         :param thing: PageItem sub-class or Python object that can be converted to a string

         :returns: None
         """
        addend = self.get_page_item(thing)
        self.body.append(addend)

    def add_blanks(self, n=1):
        """
        Add line breaks

        :param int n: number of blank lines

        :return: None
        """
        self.add(PageItemBlanks(n))

    @staticmethod
    def add_unique(the_list, item):
        """
        Add item to the list if it is not there. A set is more efficient but
        we need the items in the order inserted and don't expect these lists to be long

        :param the_list: list to use

        :param item: item to add

        :return: the_list but original is modified in place
        """
        if item not in the_list:
            the_list.append(item)
        return the_list

    def add_body_js(self, js_script):
        """
        Add this script to the _body section of the page

        :param str js_script: javascript code the HTML tags are added by the generrator

        :return: None
        """
        self.add_unique(self.bodyJs, js_script)

    def add_foot(self, pitem):
        """
        Add the item to the page footer

        :param PageItem pitem: item to add

        :return: None
        """
        self.foot.append(Page.get_page_item(pitem))

    def add_head(self, pitem):
        """
        Add this item to the top of the page as opposed to the HTML header section

        :param PageItem pitem: Item to add

        :return: None
        """
        self.head.append(pitem)

    def add_headjs(self, script):
        """
        Add the script to header. NB: only include Javascript statements the HTML tags
        will be added by the page generator

        :param str script: javascript code, tags are added by html generator

        :return: None
        """
        self.add_unique(self.headJs, script)

    def add_loadjs(self, script):
        """
        Add a script to the javascript onload eevent of the _body tag.
        It will be executed in order when the <body> object has been fully loaded.
        Each script will be added only once

        :param script: javascript only, tags will be added by the html generator

        :return: None
        """
        self.add_unique(self.loadJs, script)

    def add_readyjs(self, script):
        """
        Add a script to the (document).ready section. This will be run as
        as early as possible so the script can add items to the page

        :param script: Javascript code to add to the function

        :return: None
        """
        self.add_unique(self.readyJs, script)

    def add_strong_string(self, thing):
        """
        A convenience function to add a string with the "strong" class for emphasis

        :param thing: a python construct that can be converted to a string

        :return: None
        """
        pi = PageItemString(thing).add_classname('strong')
        self.body.append(pi)

    def add_style(self, style_def):
        """
        Add an entry to header as part of the style tag
        eg " h1 {color:red;}"
        full entry: type[type..] { style; [style ...]}

        see https://www.w3schools.com/tags/tag_style.asp

        :param style_def:

        :return:
        """
        self.add_unique(self.styles, style_def)

    def fix_css_path(self, path):
        """
        Used to allow paths to CSS URIs to be relative to the css root if specified

        :param path:  path relative to cssroot (does not start with '/', or
            absolute are relative to the page, or full URI are anywhere

        :return: the "fixed path"
        """
        ret = path
        if not path.startswith('/') and not path.lower().startswith('http://') \
                and not path.lower().startswith('https://'):
            ret = self.cssRoot + path
        return ret

    def fix_js_path(self, path):
        """
        Used to allow paths to javascript URIs to be relative to the js root if specified

        :param path:  path relative to jsroot (does not start with '/',
            absolute are relative to the page, full URI are anywhere

        :return: the "fixed path"
        """

        ret = str(path)
        if not ret.startswith('/') and not ret.lower().startswith(
                'http://') and not ret.lower().startswith('https://') and self.jsRoot:
            ret = self.jsRoot + ret
        return ret

    def get_body(self):
        """
        Internal method.
        Process each item that goes into the _body section.
        NB:  This routine does not close the _body tag, that is left for the Footer so
        _get_footer must be called afterwards

        :returns: string containing the <body> tag
        """

        ret = StringBuilder()
        ret += '<body '
        if self.className:
            ret += 'class="' + self.className + '"'
        ret += '>\n'

        if self.readyJs:
            ret += '<script>\n' + "   jQuery(document).ready(function()\n" + "    {\n"
            for js in self.readyJs:
                ret += '    ' + js + '\n'
            ret += '    }\n' + '</script>\n\n'

        if self.loadJs:
            ret += '<script>\n' + "   window.onload=function()\n" + '    {\n'
            for js in self.loadJs:
                ret += '    ' + js + '\n'
            ret += '    }' + '</script>\n\n'

        if self.bodyJs:
            ret += '<script>\n    {\n'
            for js in self.bodyJs:
                ret += '    ' + js + '\n'
            ret += '    }n' + '</script>\n\n'

        for pi in self.body:
            pi_html = pi.get_html()
            ret += pi_html

        return str(ret)

    def add_line(self, item, pre_blank=0, post_blank=1, escape=False):
        """
        Add any item, usually tex withh plank lines before and.or after
        :param item:
        :param pre_blank:
        :param post_blank:
        :return:
        """
        if not escape and isinstance(item, str):
            it = PageItemString(item, escape=False)
        else:
            it = self.get_page_item(item)
        if pre_blank > 0:
            self.add_blanks(pre_blank)
        self.add(it)
        if post_blank > 0:
            self.add_blanks(post_blank)

    def get_footer(self):
        """
        Add the items in our footer lists to the HTML <body> tag

        :return: string of html closing the <body> tag
        """
        ret = StringBuilder()
        if self.foot or self.addStats:
            ret += '<br><br>\n'

            for pi in self.foot:
                pi.add_classname('footer')
                ret += pi.get_html()

            if self.addStats:
                elap = time.time() - self.crTime
                utc = datetime.datetime.now().astimezone(pytz.utc)
                utc_str = utc.strftime('%Y-%m-%d %H:%M:%S %Z')
                pi = PageItemString(f'Page generated in {elap:.2f}s on {utc_str}')
                pi.add_classname('footer')
                ret += pi.get_html()

        ret += '</body>\n</html>\n'
        return str(ret)

    def get_head(self):
        """
        Generate the full top level of the HTML page

        :return: str everthing befor <body> tag
        """
        ret = StringBuilder()
        ret += self.docType + '\n'
        ret += '<html dir="ltr" lang="en">\n'
        ret += '<head>\n'
        ret += f'    <meta charset="{self.charset}">\n'
        ret += f'    <title>{self.title}</title>\n\n'

        for js in self.jsIncludes:
            ret += '    <script src="' + js + '"></script>\n'

        for js in self.headJs:
            ret += '    <script>' + js + '\n    </script>\n'

        for css in self.cssIncludes:
            ret += '     <link rel="stylesheet" href="'
            ret += css + '" >\n'

        if self.styles:
            ret += '   <style>\n'
            for style in self.styles:
                ret += '        ' + style + '\n'
            ret += '    </style>\n'

        if self.refreshInterval > 2:
            ret += '    <meta http-equiv="refresh" content="{:d}'.format(self.refreshInterval)
            if self.refreshURL:
                ret += "; url='" + self.refreshURL + "'"
            ret += '">\n'

        ret += '</head>\n\n'
        return str(ret)

    def get_html(self):
        """
        Generate the HTML for the full page

        :return: str of full HTML, caller cand send to client or write to file
        """
        ret = StringBuilder()
        # give each PageItem a chance to add CSS or JS to headers
        self.update_headers()

        if self.lastCSS:
            self.cssIncludes.append(self.lastCSS)

        ret += self.get_head()
        ret += self.get_body()
        ret += self.get_footer()

        return str(ret)

    def include_css(self, css_path):
        """
        Add a link to a css file, may be relative to the cssRoot, relative to the website
        or an external link

        :param css_path: path to css file

        :return: None
        """
        self.add_unique(self.cssIncludes, self.fix_css_path(css_path))

    def include_css_cdn(self, pkg):
        """
        Add a css link to a content distribution network
        :param pkg: package name
        :return:
        """
        pkgs = {
            'theme_blue': 'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/css/theme.blue.min.css',
            'gwbootstrap': 'https://cdn.jsdelivr.net/npm/gwbootstrap@1.3.2/lib/gwbootstrap.min.css',
        }
        if pkg in pkgs.keys():
            self.include_css(pkgs[pkg])
        else:
            raise KeyError(f'Unknown css packge for CDN include: {pkg}')

    def include_js(self, js_path):
        """
        Add a link to a javascript file, may be relative to the cssRoot, relative to the website
        or an external link

        :param js_path: path to javascript

        :return: None
        """
        self.add_unique(self.jsIncludes, self.fix_js_path(js_path))

    def include_js_cdn(self, pkg):
        """
        Add a "standard" javascript package from an external content delivery network
        :param pkg: a known package name jquery, tinymce
        :return:
        """
        knowcdn = {
            'jquery': 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            'tablesorter':
                'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/jquery.tablesorter.min.js',
            'tablesorter_widgets':
            'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/jquery.tablesorter.widgets.min.js',
            'bootstrap': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js',
            'tinymce': 'https://cdn.tiny.cloud/1/850zxlg445bnhvpgnw4svhmvy46dh6eoasgyz1wg'
                       'lkxwc06t/tinymce/4/tinymce.min.js'
        }
        if pkg in knowcdn.keys():
            self.include_js(knowcdn[pkg])
        else:
            raise WebUtilError(f'No known CDN fot package: {pkg}')

    def update_headers(self):
        """
        Each PageItem is given one last chance to add javascript or css to the page

        :return: None
        """
        for pil in self.head, self.body, self.foot:
            for pi in pil:
                pi.update_header(self)
