#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pubmed',
    author='Matt Grayson',
    author_email='mattgrayson@uthsc.edu',
    url='http://library.uthsc.edu',
    description='Simple utility for searching and retrieving articles from '
                'PubMed via the Entrez Programming Utilities.',
    long_description="""\
pubmed.py
-----
Simple utility for searching and retrieving articles from PubMed via the 
Entrez Programming Utilities <http://eutils.ncbi.nlm.nih.gov/>.

Required: Python 2.5 or later
Required: httplib2
Required: lxml
Required: dateutil
-----

To install:
$ python setup.py install
""",
    version='0.3.2',
    py_modules=['pubmed'],
)
