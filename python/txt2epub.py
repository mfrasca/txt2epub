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

import os
import codecs
import zipfile
import tempfile


def main(source, destination, **options):
    """translate the files to epub
    """

    names = [".".join(i.split('.')[:-1]) 
             for i in os.listdir(source)]
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
    template = env.get_template("item.html")
    for n in names:
        info = {'title': n}
        content = codecs.open(source + "/" + n + ".txt", encoding='utf-8').read()
        lines = content.split("\n\n")
        info['lines'] = lines
        out = codecs.open(tempdir + "/content/" + n + ".html", "w", encoding='utf-8')
        out.write(template.render(info))
        out.close()

    ## finally zip everything into the destination
    out = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
    out.write(tempdir + "/mimetype", "mimetype", zipfile.ZIP_STORED)
    out.write(tempdir + "/META-INF/container.xml", "META-INF/container.xml", zipfile.ZIP_DEFLATED)
    for name in ["00_content.opf", "00_stylesheet.css"] + [i + ".html" for i in names] + ["00_toc.ncx"]:
        out.write(tempdir + "/content/" + name, "content/" + name, zipfile.ZIP_DEFLATED)
        
    out.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='convert text files to epub document.')
    parser.add_argument('source', type=str,
                        help='the directory that holds the text files')
    parser.add_argument('destination', type=str,
                        help='the name of the epub document')
    parser.add_argument('--type')
    parser.add_argument('--title')
    parser.add_argument('--creator')
    parser.add_argument('--description')
    parser.add_argument('--publisher')
    parser.add_argument('--date')
    parser.add_argument('--language')
    parser.add_argument('--identifier')

    args = parser.parse_args()

    main(**vars(args))
