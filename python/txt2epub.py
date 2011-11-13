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


def main(source, destination, **options):
    """translate the files to epub
    """

    names = os.listdir(source)

    ## create directory structure
    os.mkdir(destination)
    os.mkdir(destination + "/META_INF")
    os.mkdir(destination + "/content")

    ## create hard coded files
    f = open(destination + "/mimetype", "w")
    f.write("application/epub+zip")
    f.close()

    f = open(destination + "/META_INF/container.xml", "w")
    f.write("""<?xml version='1.0' encoding='utf-8'?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile media-type="application/oebps-package+xml" full-path="content/00_content.opf"/>
  </rootfiles>
</container>
""")
    f.close()

    ## use templates to produce rest of output

    ## start with 00_content.opf

    ## then convert each of the files
    for n in names:
        pass

    ## finally zip everything into the destination.epub
    zip = zipfile.ZipFile(destination + ".epub")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='convert text files to epub document.')
    parser.add_argument('source', type=str,
                        help='the directory that holds the text files')
    parser.add_argument('destination', type=str,
                        help='the name of the epub document, excluded extension')
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
