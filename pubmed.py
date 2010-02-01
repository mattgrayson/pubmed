#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pubmed.py

Simple utility for searching and retrieving articles from PubMed via the 
Entrez Programming Utilities <http://eutils.ncbi.nlm.nih.gov/>.

Required: Python 2.5 or later
Required: httplib2
Required: lxml
"""

__author__ = "Matt Grayson (mattgrayson@uthsc.edu)"
__copyright__ = "Copyright 2009, Matt Grayson"
__license__ = "MIT"
__version__ = "0.1"

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
        """Convenience method for retrieving the resulting contents of a request 
        to a given URL. If the params arg is a dict, it will be urlencoded and 
        appended to the given URL.
        """
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

        while args['retstart'] < total:
            raw = self._get(self.fetch_uri, args)
            #results += self.parse_fetch_results(raw)
            
            print 'tmp/%s_%s.xml' % (web_env, args['retstart'])
            f = open('tmp/%s_%s.xml' % (web_env, args['retstart']), 'w')
            f.write(raw)
            f.close()
            
            args['retstart'] += ret_max

        #return results
    
    def parse_fetch_result(self, raw):
        xml_tree = etree.XML(raw)
        articles_list = []
        for article in xml_tree.findall('PubmedArticle'):
            art_dict = {}
            art_dict['pmid'] = article.findtext('.//PMID') if article.find('.//PMID') is not None else ''
            art_dict['title'] = article.findtext('.//Article/ArticleTitle') if article.find('.//Article/ArticleTitle') is not None else ''
            art_dict['authors'] = []
            for auth in article.findall('.//Author[@ValidYN="Y"]'):
                auth_str = auth.findtext('LastName') if auth.find('LastName') is not None else ''
                if auth.find('Initials') is not None:
                    auth_str = "%s %s" % (auth_str, auth.findtext('Initials'))
                elif auth.find('ForeName') is not None:
                    auth_str = "%s %s" % (auth_str, auth.findtext('ForeName'))
                art_dict['authors'].append(auth_str)
            art_dict['affiliations'] = article.findtext('.//Article/Affiliation') if article.find('.//Article/Affiliation') is not None else ''  
            art_dict['abstract'] = article.findtext('.//Article/Abstract/AbstractText') if article.find('.//Article/Abstract/AbstractText') is not None else ''  
            art_dict['medline_status'] = article.find('MedlineCitation').get('Status') if article.find('MedlineCitation').get('Status') is not None else ''
            art_dict['pubmed_status'] = article.findtext('.//PubmedData/PublicationStatus') if article.find('.//PubmedData/PublicationStatus') is not None else ''
            
            # Journal details
            journal = {}
            journal['name'] = article.findtext('.//Article/Journal/Title') if article.find('.//Article/Journal/Title') is not None else ''  
            journal['name_abbrv'] = article.findtext('.//MedlineJournalInfo/MedlineTA') if article.find('.//MedlineJournalInfo/MedlineTA') is not None else ''  
            journal['issn_online'] = article.findtext('.//Article/Journal/ISSN[@IssnType="Electronic"]') if article.find('.//Article/Journal/ISSN[@IssnType="Electronic"]') is not None else ''  
            journal['issn_print'] = article.findtext('.//Article/Journal/ISSN[@IssnType="Print"]') if article.find('.//Article/Journal/ISSN[@IssnType="Print"]') is not None else ''                          
            art_dict['journal'] = journal
            
            # Citation details
            citation = {}
            citation['pages'] = article.findtext('.//Article/Pagination/MedlinePgn') if article.find('.//Article/Pagination/MedlinePgn') is not None else ''  
            citation['volume'] = article.findtext('.//Article/Journal/JournalIssue/Volume') if article.find('.//Article/Journal/JournalIssue/Volume') is not None else ''  
            citation['issue'] = article.findtext('.//Article/Journal/JournalIssue/Issue') if article.find('.//Article/Journal/JournalIssue/Issue') is not None else ''  
            # Citation pub date
            citation['date'] = article.findtext('.//Article/Journal/JournalIssue/PubDate/Year') if article.find('.//Article/Journal/JournalIssue/PubDate/Year') is not None else ''
            citation['date'] = "%s %s" % (citation['date'], article.findtext('.//Article/Journal/JournalIssue/PubDate/Month')) if article.find('.//Article/Journal/JournalIssue/PubDate/Month') is not None else citation['date']
            citation['date'] = "%s %s" % (citation['date'], article.findtext('.//Article/Journal/JournalIssue/PubDate/Day')) if article.find('.//Article/Journal/JournalIssue/PubDate/Day') is not None else citation['date']
            art_dict['citation'] = citation
            
            # Mesh headings
            art_dict['subjects'] = []
            for subj in article.findall('.//MeshHeadingList/MeshHeading'):
                desc_name = subj.findtext('DescriptorName') if subj.find('DescriptorName') is not None else ''
                desc_is_major = True if article.find('DescriptorName[@MajorTopicYN="Y"]') is not None else False
                art_dict['subjects'].append({'name': desc_name, 'is_major': desc_is_major})
                
                for qual in subj.findall('QualifierName'):
                    qual_name = qual.text
                    qual_is_major = True if qual.get('MajorTopicYN') == 'Y' else False
                    art_dict['subjects'].append({'name': "%s/%s" % (desc_name,qual_name), 'is_major': qual_is_major})
            
            articles_list.append(art_dict)
        return articles_list
    