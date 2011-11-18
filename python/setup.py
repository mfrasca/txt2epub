#!/usr/bin/env python

from distutils.core import setup

setup(name='txt2epub',
      version='0.1',
      description='script producing epub from text files',
      author='Mario Frasca',
      author_email='mariotomo@gmail.com',
      url='https://github.com/mfrasca/txt2epub',
      scripts=['scripts/txt2epub'],
      packages=['txt2epublib'],
      package_data={'txt2epublib': ['templates/*.html',
                                    'templates/*.css',
                                    'templates/*.opf',
                                    'templates/*.ncx',
                                    ]},
     )
