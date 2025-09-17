Overview
========

ja_webutils is a collection of classes that are used to programmatically
create html pages. These classes can be considered medium level abstractions.

The overriding design philosophy is to record in a class, method or attribute anything
we had to search the Web to learn how to do.  This doesn't preclude including
raw html directives.

The canonical hello application could look like:

.. code-block:: python

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


The resulting html file looks like:

.. code-block:: html

    <!DOCTYPE html>
    <html dir="ltr" lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hello</title>

    </head>

    <body >
    Hello world<br><br>
    <p  class="footer" > Page generated in 0.00s on 2023-09-06 16:31:27 UTC</p>
    </body>
    </html>

Which produces:

.. figure:: _static/example_01.jpg
    :width: 640
    :alt: Example 1 in browser

    Browser (Chrome) rendition of the above example

The overall organization of the package:

The ``Page`` class is a container that will produce complete HTML with a <head> and <body> section.
It allows style and javascript to be added as strings or loaded from content delivery sites,
including your own. This allows our ``PageTable`` class to include appropriate jQuery code and
styles when a sortable table is requested. The ``head``, ``body``, and ``foot`` containers
maintain the order items are added, other containers such as styles, CSS fles, javascript,
javascript files are check for duplicates but do not in general maintain the order in
which they were added.

The ``PageItem`` class is an abstract base class for all items added to the body and footer
sections. Children are loosely divided into ``PageItems`` and ``FormItems`` where the
``FormItems`` are used to pass input fields.

The ``Form`` class is a container for HTML forms, it may contain both ``PageItems`` and
``FormItems``.


