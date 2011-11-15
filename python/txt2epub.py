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


def encode_entities(text):
    return text.replace(
        "&", "&amp;").replace(
        ">", "&gt;").replace(
        "<", "&lt;").replace(
        "\014", "")


def main(destination, sources, **options):
    """translate the files to epub
    """

    names = [os.path.basename(".".join(i.split('.')[:-1])).replace(" ", "_")
             for i in sources]
    types = [i.split('.')[-1].lower()
             for i in sources]
    options['names'] = names

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
    env = Environment(loader=PackageLoader('__main__', "templates"))

    ## start with content/00_content.opf
    template = env.get_template("00_content.opf")
    out = file(tempdir + "/content/00_content.opf", "w")
    out.write(template.render(options))
    out.close()

    ## then content/00_toc.ncx
    template = env.get_template("00_toc.ncx")
    out = file(tempdir + "/content/00_toc.ncx", "w")
    out.write(template.render(options))
    out.close()

    ## and the style
    template = env.get_template("00_stylesheet.css")
    out = file(tempdir + "/content/00_stylesheet.css", "w")
    out.write(template.render(options))
    out.close()

    ## then convert each of the files
    if options['keep_line_breaks']:
        template = env.get_template("item-br.html")
        split_on = '\n'
    else:
        template = env.get_template("item.html")
        split_on = '\n\n'
    for short, full, this_type in zip(names, sources, types):
        info = {'title': short}
        content = codecs.open(full, encoding='utf-8').read()
        if this_type == "rst":
            text = publish_string(content, writer_name="html")
        else:
            content = encode_entities(content)
            lines = content.split(split_on)
            info['lines'] = lines
            text = template.render(info)
        out = codecs.open(tempdir + "/content/" + short + ".html", "w", encoding='utf-8')
        out.write(text)
        out.close()

    ## finally zip everything into the destination
    out = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
    out.write(tempdir + "/mimetype", "mimetype", zipfile.ZIP_STORED)
    out.write(tempdir + "/META-INF/container.xml", "META-INF/container.xml", zipfile.ZIP_DEFLATED)
    for name in ["00_content.opf", "00_stylesheet.css"] + [i + ".html" for i in names] + ["00_toc.ncx"]:
        out.write(tempdir + "/content/" + name, "content/" + name, zipfile.ZIP_DEFLATED)
        
    out.close()


if __name__ == '__main__':
    import argparse, datetime, uuid

    parser = argparse.ArgumentParser(description='convert text files to epub document.')
    parser.add_argument('destination', type=str,
                        help='the name of the epub document')
    parser.add_argument('sources', type=str, nargs='+',
                        help='the text files to include in the epub')
    parser.add_argument('--keep-line-breaks', action='store_true')
    parser.add_argument('--type')
    parser.add_argument('--title')
    parser.add_argument('--creator')
    parser.add_argument('--description')
    parser.add_argument('--publisher')
    parser.add_argument('--date', default=datetime.datetime.today())
    parser.add_argument('--language')
    parser.add_argument('--identifier', default=str(uuid.uuid4()))

    args = parser.parse_args()

    main(**vars(args))
