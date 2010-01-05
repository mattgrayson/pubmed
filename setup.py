#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pubmed',
    author='Matt Grayson',
    author_email='mattgrayson@uthsc.edu',
    url='http://library.uthsc.edu',
    description='Simple wrapper around Bio.Entrez for searching '
                'and retrieving articles from PubMed via the Entrez '
                'Programming Utilities.',
    long_description="""\
pubmed.py
-----
Simple wrapper around Bio.Entrez for searching and retrieving 
articles from PubMed via the Entrez Programming Utilities 
<http://eutils.ncbi.nlm.nih.gov/>.

Required: Python 2.5 or later
Required: biopython <http://biopython.org/>
-----

To install:
$ python setup.py install
""",
    version='1.0',
    py_modules=['pubmed'],
)