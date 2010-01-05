#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pubmed.py

Simple wrapper around Bio.Entrez for searching and retrieving 
articles from PubMed via the Entrez Programming Utilities 
<http://eutils.ncbi.nlm.nih.gov/>.

Required: Python 2.5 or later
Required: biopython <http://biopython.org/>
"""

__author__ = "Matt Grayson (mattgrayson@uthsc.edu)"
__copyright__ = "Copyright 2009, Matt Grayson"
__license__ = "MIT"
__version__ = "1.0"

import httplib2
import urllib
from lxml import etree

class PubMedEntrez(object):
    """
    """    
    ENTREZ_BASE_URI = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

    def __init__(self, email):        
        self.search_results = ''
        self.last_query = ''
        self.email_address = email
        self.search_uri = '%s/esearch.fcgi?db=pubmed&retmode=xml&usehistory=y&email=%s' % (self.ENTREZ_BASE_URI, email)
        self.fetch_uri = '%s/efetch.fcgi?db=pubmed&retmode=xml&rettype=full&email=%s' % (self.ENTREZ_BASE_URI, email)
        self.conn = httplib2.Http()        
        
    def _get(self, url, params=None):    
        if params:
            encoded_params = urllib.urlencode(params)
            if '?' in url:
                url = "%s&%s" % (url, encoded_params)
            else:
                url = "%s?%s" % (url, encoded_params)
        
        resp, content = self.conn.request(url)
        if resp.status < 400:
            return content
        else:
            return None
              
    def search(self, query, autofetch=True, **kwargs):
        args = {'term': query}
        args.update(kwargs)
        raw = self._get(self.search_uri, args)
        xml_tree = etree.XML(raw)
        if autofetch:
            count = xml_tree.findtext('Count') if xml_tree.find('Count') is not None else 0
            query_key = xml_tree.findtext('QueryKey') if xml_tree.find('QueryKey') is not None else ''
            web_env = xml_tree.findtext('WebEnv') if xml_tree.find('WebEnv') is not None else ''
            return self.fetch_batch(query_key, web_env, count)
        else:
            return {            
                'count': xml_tree.findtext('Count') if xml_tree.find('Count') is not None else 0,
                'ids': [e.text for e in xml_tree.findall('IdList/Id')]
            }
    
    def fetch_batch(self, query_key, web_env, total):
        ret_position = 0
        ret_max = 500
        results = []
        args = {
            'WebEnv': web_env,
            'query_key': query_key,
            'retstart': ret_position,
            'retmax': ret_max
        }

        while ret_position < total:
            raw = self._get(self.fetch_uri, args)
            print raw
            #results.append(Entrez.read(query_handle))
            ret_position += ret_max

        return results
    
    def parse_fetch_result(self, raw):
        xml_tree = etree.XML(raw)
        articles_list = []
        for article in xml_tree.findall('PubmedArticle'):
            art_dict = {}
            art_dict['title'] = article.findtext('.//Article/ArticleTitle') if article.find('.//Article/ArticleTitle') is not None else ''
            art_dict['authors'] = []
            for auth in article.findall('.//Author[@ValidYN="Y"]'):
                auth_str = auth.findtext('LastName') if auth.find('LastName') is not None else ''
                if auth.find('Inititals') is not None:
                    auth_str = "%s %s" % (auth_str, auth.findtext('Inititals'))
                    print 'initials ...                    '
                elif auth.find('ForeName') is not None:
                    auth_str = "%s %s" % (auth_str, auth.findtext('ForeName'))
                art_dict['authors'].append(auth_str)
            articles_list.append(art_dict)
        return articles_list
            
        
# from Bio import Entrez
# 
# class PubMedSearch(object):
#     
#     def __init__(self, email_address):
#         self.email_address = email_address
#         self.search_results = ''
#         self.last_query = ''
#     
#     def search(self, query, max_records=50, autofetch=True):
#         self.last_query = query
#         query_handle = Entrez.esearch(
#             db='pubmed', 
#             term=query,
#             email=self.email_address,
#             usehistory='y',            
#         )
#         self.search_results = Entrez.read(query_handle)
#         
#         if autofetch:
#             count = self.search_results['Count']
#             query_key = self.search_results['QueryKey']
#             web_env = self.search_results['WebEnv']
#             return self.fetch_batch(query_key, web_env, count)
#         else:
#             return {
#                 'total': self.search_results['Count'],
#                 'pmid_list': self.search_results['IdList'],
#             }
#     
#     def fetch(self, pmid):
#         """docstring for fetch"""
#         pass
#     
#     def fetch_batch(self, query_key, web_env, total):
#         ret_position = 0
#         ret_max = 500
#         results = []
#         
#         while ret_position < total:
#             query_handle = Entrez.efetch(
#                 db='pubmed', 
#                 email=self.email_address,
#                 WebEnv=web_env,
#                 query_key=query_key,
#                 retstart=ret_position,
#                 retmax=ret_max,
#                 retmode='xml'
#             )
#             results.append(Entrez.read(query_handle))
#             ret_position += ret_max
#         
#         return results
# 
# class PubMedRecord(object):
#     """docstring for PubMedRecord"""
#     def __init__(self, arg):
#         super(PubMedRecord, self).__init__()
#         self.arg = arg
# 
# 
# if  __name__ == '__main__':
#     q = '"ut memphis"[Affiliation] OR "university of Tennessee Memphis"[Affiliation] ' \
#         'OR "university of Tennessee health science center"[Affiliation] OR ' \
#         '"uthsc"[Affiliation] OR "University of Tennessee College of Medicine"[Affiliation]'
#     p = PubMedSearch('test')
#     p.search(q)
    