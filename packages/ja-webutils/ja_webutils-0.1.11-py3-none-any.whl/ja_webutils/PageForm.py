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

"""
Packages for html forms and input fields

A class representing the HTML form it is a container for elements of the
form which are defined in their own classes. Other items such as tables,
labels, images or links can be added.

The basic parts to a form are:

* Head - defines the form and submit action
* Hidden - hidden variables are passed back as is but not displayed to the user in any way
* Display - pageItems some may be entry some tables or text or images with no returned data
* End - Adds submit and cancel buttons (maybe) and closes the form tag

The head section Defines the encoding and the submitted action

You can add as many hidden variables as you wish. They are returned with
the form but the user is not shown these variables. Note that they are easily
seen and modified by a motivated user, so they should not contain anything secret.

The display section may contain any PageItem you wish. It is common to arrange
the input items in the table with label column, input item, helpful comment
on each row.
"""

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__myname__ = 'PageForm'

from abc import ABC

from ja_webutils.PageItem import PageItem, PageItemArray, \
    PageItemString, PageItemBlanks
from ja_webutils.StringBuilder import StringBuilder
from ja_webutils.webutilerror import WebUtilError


class PageFormItem(PageItem, ABC):
    """
    Abstract base class representing html input tags
    Attributes:
    """
    size = None
    __doc__ += """size - Limit length of value eg: text field"""
    prompt = None
    __doc__ = """prompt - convenience to put string before actual item"""

    def __init__(self, prompt=None, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompt

    def add_event(self, evt_name, call):
        super(PageFormItem, self).add_event(evt_name, call)

    def get_html(self):
        if self.prompt:
            html = PageItemString(self.prompt).get_html()
        else:
            html = ''
        return html


class PageFormSubmit(PageFormItem):
    """
    Represents the html input submit tag. A button to submit or cancel a form

    """
    def __init__(self, name, value):
        """
        Standard submit button. See PafeFormButton for alternatives
        :param str name: PageItem name
        :param str value: text to show in the button
        """
        super().__init__(name=name)
        self.value = value

    def get_html(self):
        """
        Get the html tag for a stadard submit button
        :return str: html
        """
        ret = super().get_html()
        ret += f'<input type="submit" name="{self.name}" value="{self.value}" '
        if self.id:
            ret += f' id="{self.id}" '
        if self.class_names:
            ret += f' class="{self.class_names}" '
        ret += '/>\n'
        return ret


class PageFormButton(PageFormItem):
    """
    Represens a button element, depending on type it may be similar to
    the input type submit but is more flexible in content

    Attributes:

    """
    contents = ''
    __doc__ += """text - what is shown in the button"""
    value = ''
    __doc__ += """value - what is returned on submit"""
    icon = None
    __doc__ += """icon - PageItemImage used as the button's icon"""
    enabled = True
    __doc__ += """enabled - buttons can be disabled"""
    target = None
    __doc__ += """target - where to display response _self is default, _blank for new tab/window"""
    type = 'submit'
    __doc__ += """ type - button type can be submit, button, reset"""
    types = ['submit', 'button', 'reset']

    def __init__(self, name=None, contents='', value='', type='submit', enabled=True, target=None, **kwargs):
        """
        :param str name: tag name
        :param str | PageItem contents: text to put inside the button
        :param str value: value returned
        :param str type: button type one of submit, button, or reset
        :param bool enabled: allow disabling this button
        :param str target: _blank, _self, _parent, _top
        :param kwargs: passed to PageFormItem, and PageItem
        """
        super().__init__(name=name, **kwargs)
        self.value = value
        self.contents = contents if isinstance(contents, PageItem) else PageItemString(contents)
        self.type = type
        self.enabled = enabled
        self.target = target

    def set_type(self, new_type):
        """
        Set tye button type attri ute with validity check
        :param str new_type: new button type maybe submit, button, or reset
        :return: None
        """
        if new_type not in self.types:
            raise WebUtilError(f'Invalid button type {new_type}')
        self.type = new_type

    def get_html(self):
        ret = super().get_html()
        ret += f'<button name="{self.name}" type="{self.type}" '
        if not self.enabled:
            ret += ' disabled '
        if self.value:
            ret += f' value="{self.value}" '
        ret += self.get_attributes()
        if self.target:
            ret += f' formtarget="{self.target}" '
        ret += '>'
        if self.icon:
            ret += self.icon.get_html()
        if self.contents:
            ret += self.contents.get_html()
        ret += '</button>\n'
        return ret


class PageFormCheckBox(PageFormItem):
    """
    A boolean object that appears as a checkbox
    """

    def __init__(self, txt='', checked=False, **kwargs):
        """

        :param str name: tag name
        :param txt: Text to appear beside checkbox
        :param boolean checked: Default checked status
        """
        super().__init__(**kwargs)
        self.txt = txt
        self.checked = checked

    def get_html(self):
        """
        Get html for this tag
        :return str: html
        """
        ret = super().get_html()
        ret += f'<input type="checkbox" name="{self.name}"  value="{self.txt}" '
        ret += ' checked ' if self.checked else ''
        ret += self.get_attributes()
        ret += '/>\n'
        return ret


class PageFormFileUpload(PageFormItem):
    """
    Sets up the upload
    """

    def __init__(self, name='', allow_multiple=False, accept=None):
        """
        input tye file
        :param str name: tag name
        :param allow_multiple: whether we allow more than one file to be selected
        :param list accept: list of mime types to accept
        """
        super().__init__(name)
        self.accept = accept
        self.allow_multiple = allow_multiple

    def get_html(self):
        """
        Get the tag
        :return str: the html
        """
        ret = super().get_html()
        ret += '<input type="file" '
        ret += self.get_attributes()
        ret += ' multiple="true" ' if self.allow_multiple else ''
        if self.accept:
            aclist = ', '.join(self.accept)
            ret += f' accept=""{aclist}'
        ret += '/>\n'
        return ret


class PageFormRadio(PageFormItem):
    """
    Radio Button class
    Attributes:

    """
    options = set()
    __doc__ += """options - list of tuples defining the radio options"""
    multi_allowed = False
    __doc__ += """multi_allowed - allow more than one selection"""
    radio_events = dict()

    def add(self, name=None, value=None, selected=False):
        """
        Add an option to the radio group
        :param str name: option name
        :param str value: value returned if selected
        :param boolean selected: initial selection state
        :return: None
        """
        if name is None and value is None:
            raise WebUtilError('Radio button options must specify name or value')
        n = name if name else value
        v = value if value else name
        self.options.add((n, v, selected))

    def get_html(self):
        """Return the html tags"""
        ret = StringBuilder()
        ret += super().get_html()

        for name, val, sel in self.options:
            ret += f'<input type="radio" name="{name}" '
            ret += f' value="{val}" ' if val else ''
            ret += ' checked ' if sel else ''
            for ev, call in self.events.items():
                ret += f' {ev} = "{call}" '

            ret += f'/>{val}<br>\n'

        return str(ret)


class PageFormSelect(PageFormItem):
    """
    Represents an HTML drop down menu
    Attributes:

    """
    options = list()
    __doc__ += """options - list of tuples of name, value, selected"""
    mult_allowed = False
    __doc__ += """mult_allowed - True -> user may select more than one option"""

    def __init__(self, name=None, opts=None, mult_allowed=False, **kwargs):
        """
        HTML drop down menu <select> tag
        @param str name: html element name
        @param multiple opts: string or list of strings that make up the menu
        @param bool mult_allowed: Allow multiple selections
        @param kwargs: passed to PageFirmItem then to PageItem
        """
        super().__init__(name=name, **kwargs)
        self.add(opts)
        self.mult_allowed = mult_allowed

    def add(self, opts):
        """
        Add one or more options to the menu

        :param multiple opts: string or list of strings that make up the menu
        :return: None
        """
        if isinstance(opts, list):
            for opt in opts:
                self._add(opt)
        else:
            self._add(opts)

    def _add(self, opt):
        """
        Add a single option to our list
        :param opt: string, or tuple(name, val, selected)
        :return: None
        """
        if isinstance(opt, tuple):
            if len(opt) == 3:
                self.options.append(opt)
            elif len(opt) == 2:
                self.options.append((opt[0], opt[1], False))
            else:
                raise WebUtilError(f'Unknown tuple for PageFormSelect option [{opt}')
        else:
            it = str(opt)
            self.options.append((it, it, False))

    def get_html(self):
        """
        return html for ths menu
        :return str:
        """
        ret = StringBuilder()
        ret += super().get_html()

        ret += f'<select name="{self.name}" '
        ret += ' multiple ' if self.mult_allowed else ''
        ret += f' size="{self.size:d} ' if self.size else ''
        ret += self.get_attributes()
        ret += '/>\n'
        for name, value, selected in self.options:
            ret += '<option '
            ret += f'value="{value}" ' if value else ''
            ret += ' selected ' if selected else ''
            ret += f'>{name}</option>\n'
        ret += '</selected>'
        return str(ret)


class PageFormText(PageFormItem):
    """
    Text input
    """
    maxlen = 0
    __doc__ += """maxleen: limit on how mlarge of a string may be entered"""
    default_value = None
    __doc__ += """default_value - prefilled text"""
    password = False
    __doc__ += """password - obfuscate entry if true"""
    nlines = 1
    __doc__ += """nlines - how many lines to prsent"""
    place_holder = ''
    __doc__ += """place_holder - text that does not return, like 'put uour name here'"""
    use_editor = False
    __doc__ += """use_editor - enable jquery's text editor"""

    def __init__(self, name=None, default_value='', place_holder='', maxlen=0, size=0, **kwargs):
        super().__init__(name=name, **kwargs)
        self.default_value = default_value
        self.place_holder = place_holder
        self.maxlen = maxlen
        self.size = size

    def get_html(self):
        html = super().get_html()
        closer = ''
        if self.password:
            html += '<input type="password" '
        elif self.nlines > 1:
            html += '<textarea '
            closer = '</textarea>'
        else:
            html = '<input type="text" '

        html += f' name="{self.name}" '
        if self.size > 0 and self.nlines > 1:
            html += f' cols="{self.size}" '
        elif self.size > 0:
            html += f' size="{self.size}" '
        elif self.maxlen > 0:
            size = self.size if 60 >= self.size > 0 else 60
            html += f' size="{size:d}" '

        html += f' maxlength="{self.maxlen:d}" ' if self.maxlen > 0 else ''
        html += f' rows="{self.nlines:d}" ' if self.nlines > 1 else ''
        if self.default_value != '':
            html += f' value="{self.default_value}"'
        elif self.place_holder != '':
            html += f' placeholder="{self.place_holder}" '
        html += self.get_attributes()
        html += '>\n '
        html += f'{closer}\n'

        return html

    def update_header(self, page):
        """
        If etidable add js editor to header
        :param Page page:
        :return:
        """
        if self.use_editor:
            page.include_js_cdn('tinymce')
            page.add_headjs('tinymce.init({selector:"textarea.editable"});')
            if self.default_value:
                edcontent = self.default_value
                edcontent = edcontent.replace("'", '&#39').replace('\n', '').replace('\r', '')
                if not self.id and edcontent:
                    raise WebUtilError('Default content in an editable area requires the tag id be set. {self.name}')
                script = f'tinyMCE.get("#{self.id}").setContent("{edcontent}");'
                page.add_headjs(script)


class PageForm(PageItem):
    """
    PageForm is a container that has input items and html formatting tags

    Attribtes:

    """

    def __init__(self, action=None, method='post', nosubmit=False, **kwargs):
        """
        The form contains html items and form items for returning info
        @param url action: where to go on submit
        @param str method: GET | POST - how info is returned
        @param bool nosubmit: don't ad  submit button
        @param kwargs: Passed to PageItem
        """
        super().__init__(**kwargs)
        self.action = action
        self.method = method
        self.nosubmit = nosubmit
        self.__doc__ = ''
        self.__doc__ += """action - url that handles form submission"""
        self.method = 'post'
        self.__doc__ += """method - get, parameters part of url, post = no limit on size"""
        self.encoding = "multipart/form-data"
        self.__doc__ += """encoding - default is almost always the best otion"""
        self.target = ''
        self.__doc__ += """target - where to display response _self is default, _blank for new tab/window"""
        self.items = PageItemArray()
        self.__doc__ += """items - list of PageItems and FormItems that make up the form"""
        self.hidden = dict()
        self.__doc__ += """hidden - dictionay of hidden variables. Returned but not shown"""
        self.submit = None
        self.__doc__ += """submit - text for submit button"""
        self.cancel = None
        self.__doc__ += """cancel - text for cancel button"""
        self.nosubmit = False
        self.__doc__ = """nosubmit - True means do not add a sbmit button"""

    def add(self, it):
        """
        Add any acceptable PageItem or python basic data type to form

        :param: it - any PageItem capable thing
        """
        self.items.add(it)

    def __add__(self, other):
        """ + operator s an alias for add"""
        self.add(other)

    def add_line(self, it, n=1):
        """
        Aa the item and a line break as a convenience
        :param int n: number of blank lines
        :param it:  any PageItem capable thing
        :return:
        """
        self.add(it)
        self.add(PageItemBlanks(n))

    def add_hidden(self, name, value):
        """
        Hidden values are sent with the forms but not displayed
        :param str name: parameter name can not be None
        :param str|None value: string value to return
        :return: None
        """
        self.hidden[name] = value

    def update_header(self, page):
        """
        Some items in our list may need to add javascript, or css to the Page
        :param Page page: paage we are part of
        :return: None
        """
        self.items.update_header(page)

    def get_html(self):
        """
        Produce the html for the form
        :return str: html
        """
        html_bldr = StringBuilder()
        html_bldr += super().get_html()

        self.get_form_start(html_bldr)
        self.get_form_hidden(html_bldr)
        html_bldr += self.items.get_html()
        self.get_form_end(html_bldr)
        return str(html_bldr)

    def get_form_start(self, bldr):
        """
        Get the opening html for the form
        :param StringBuilder bldr: buffer to wich to add our html
        :return: None but bldr is updated
        """
        if self.action is None:
            raise WebUtilError('PageForm must have an action defined')
        bldr += f'<form enctype="{self.encoding}" '
        if self.name:
            bldr += f' name="{self.name}" '
        if self.id:
            bldr += f' id="{self.id}" '
        if self.target:
            bldr += f' target="{self.target}" '

        bldr += f'action="{self.action}" method="{self.method}">\n'

    def get_form_hidden(self, bldr):
        """
        Add hidden variables
        :param StringBuilder bldr: where to add html
        :return: None but bldr is updated
        """
        for key, val in self.hidden.items():
            value = str(val) if val else ''
            bldr += f'<input type="hidden" name="{key}" class="{key}" value="{value}">\n'

    def get_form_end(self, bldr):
        """
        Close the form definition
        :param StringBuilder bldr: where to add html
        :return: None but bldr is updated
        """
        if not self.nosubmit:
            submit = self.submit if self.submit else 'Submit'
            pfs = PageFormSubmit("submit", submit)
            bldr += pfs.get_html()

            if self.cancel:
                pfc = PageFormSubmit('cancel', self.cancel)
                bldr += pfc.get_html()

        bldr += '</form>\n'
