#!/usr/bin/python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# copyright 2011 Mario Frasca

import os, os.path
import codecs
import zipfile
import tempfile
from docutils.core import publish_string
import re
from shutil import copyfile


def encode_entities(text):
    return text.replace(
        "&", "&amp;").replace(
        ">", "&gt;").replace(
        "<", "&lt;").replace(
        r"\_", "&#95;")


class translate_markup_functor(object):
    def __init__(self):
        self.superscript = re.compile(r'^(.*)^{(.*?)}(.*)$', re.DOTALL)
        self.subscript = re.compile(r'^(.*)_{(.*?)}(.*)$', re.DOTALL)
        self.bold = re.compile(r'^(.*)__(.*?)__(.*)$', re.DOTALL)
        self.italics = re.compile(r'^(.*)_(.*?)_(.*)$', re.DOTALL)

    def __call__(self, text):
        """
        """

        text = text.replace("---", "&#8212;")
        text = text.replace("...", "&#8230;")
        text = text.replace("\014", '<br style="page-break-after:always"/>')
        text = text.replace("\n  ", '\n<br/>')

        for name, rule in [("sup", self.superscript),
                           ("sub", self.subscript),
                           ("bold", self.bold),
                           ("em", self.italics),
                           ]:
            match = rule.match(text)
            while match:
                text = ("%s<" + name + ">%s</" + name + ">%s") % match.groups()
                match = rule.match(text)

        return text

translate_markup = translate_markup_functor()

def main(destination, sources, **options):
    """translate the files to epub
    """

    suggested_options = ['title', 'creator', 'identifier']
    missing_suggested = [k for k in suggested_options if options.get(k) is None]
    if missing_suggested:
        print 'missing suggested options: ', ', '.join(missing_suggested)

    fullnames = [os.path.basename(i).replace(" ", "_") 
                 for i in sources]
    sources = [{'name': ".".join(l.split('.')[:-1]),
                'type': l.split('.')[-1].lower(),
                'orig': orig,
                'full': l,
                }
                for l, orig in zip(fullnames, sources)]
    options['files'] = sources
    options['spine'] = []

    tempdir = tempfile.mkdtemp()
    ## create directory structure
    os.mkdir(tempdir + "/META-INF")
    os.mkdir(tempdir + "/content")

    ## create hard coded files
    out = open(tempdir + "/mimetype", "w")
    out.write("application/epub+zip")
    out.close()

    out = open(tempdir + "/META-INF/container.xml", "w")
    out.write("""<?xml version='1.0' encoding='utf-8'?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile media-type="application/oebps-package+xml" full-path="content/00_content.opf"/>
  </rootfiles>
</container>
""")
    out.close()

    ## use templates to produce rest of output
    from jinja2 import Environment, PackageLoader
    env = Environment(loader=PackageLoader(__name__, "templates"))

    ## first we must convert each of the files and compute the resulting
    ## full name, to be used everywhere else
    if options['keep_line_breaks']:
        template = env.get_template("item-br.html")
        split_on = '\n'
    else:
        template = env.get_template("item.html")
        split_on = '\n\n'
    included = []
    for item in sources:
        if item['type'] in ["png", "jpg"]:
            copyfile(item['orig'], tempdir + "/content/" + item['full'])
            included.append(item['full'])
            item['media_type'] = 'image/' + item['type']
            continue

        item['media_type'] = 'application/xhtml+xml'
        info = {'title': item['name']}
        content = codecs.open(item['orig'], encoding='utf-8').read()
        item['full'] = item['name'] + ".html"
        if item['type'] == "rst":
            overrides = {'input_encoding': 'utf-8',
                         'output_encoding': 'utf-8'}
            text = publish_string(content, writer_name="html", settings_overrides=overrides)
            pattern = re.compile('^(<html .*?) lang=".."(.*?>)$')
            text_lines = text.split("\n")
            matches = [pattern.match(l) for l in text_lines]
            try:
                (l, r) = [(l, r) for (l, r) in enumerate(matches) if r is not None][0]
                text_lines[l] = u''.join(r.groups())
                text = u'\n'.join(text_lines)
            except:
                pass
            with file(tempdir + "/content/" + item['full'], "w") as out:
                out.write(text)
        else:
            content = encode_entities(content)
            content = translate_markup(content)
            lines = content.split(split_on)
            info['lines'] = lines
            text = template.render(info)
            with codecs.open(tempdir + "/content/" + item['full'], 
                             "w", 'utf-8') as out:
                out.write(text)
        options['spine'].append(item)
        included.append(item['full'])

    for item in options['images']:
        content = open(item).read()
        shortname = os.path.basename(item)
        with file(tempdir + "/content/" + shortname, "w") as out:
            out.write(content)
        included.append(shortname)

    ## now we can write the content/00_content.opf
    template = env.get_template("00_content.opf")
    with file(tempdir + "/content/00_content.opf", "w") as out:
        out.write(template.render(options))

    ## then content/00_toc.ncx
    template = env.get_template("00_toc.ncx")
    with file(tempdir + "/content/00_toc.ncx", "w") as out:
        out.write(template.render(options))

    ## and the style
    template = env.get_template("00_stylesheet.css")
    with file(tempdir + "/content/00_stylesheet.css", "w") as out:
        out.write(template.render(options))

    ## finally zip everything into the destination
    out = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
    out.write(tempdir + "/mimetype", "mimetype", zipfile.ZIP_STORED)
    out.write(tempdir + "/META-INF/container.xml", "META-INF/container.xml", zipfile.ZIP_DEFLATED)
    for name in ["00_content.opf", "00_stylesheet.css"] + included + ["00_toc.ncx"]:
        out.write(tempdir + "/content/" + name, "content/" + name, zipfile.ZIP_DEFLATED)
        
    out.close()
