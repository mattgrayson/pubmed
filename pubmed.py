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
__copyright__ = "Copyright 2009-2010, Matt Grayson"
__license__ = "MIT"
__version__ = "0.2"

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
        results = {
            'total_found': int(xml_tree.findtext('Count')) if xml_tree.find('Count') is not None else 0,
            'query_key': xml_tree.findtext('QueryKey') if xml_tree.find('QueryKey') is not None else '',
            'web_env': xml_tree.findtext('WebEnv') if xml_tree.find('WebEnv') is not None else '',
        }
        
        if autofetch:
            results['articles'] = self.fetch_query_results(
                results['query_key'], 
                results['web_env'], 
                results['total_found']
            )
        else:
            results['pmids'] = [e.text for e in xml_tree.findall('IdList/Id')]
            
        return results
    
    def fetch_query_results(self, query_key, web_env, total_found):
        results = []
        args = {
            'WebEnv': web_env,
            'query_key': query_key,
            'retstart': 0,
            'retmax': 500
        }

        while args['retstart'] < total_found:
            print 'Fetching results %s - %s ...' % (args['retstart'], args['retstart']+args['retmax'])                
            raw = self._get(self.fetch_uri, args)            
            results += self.parse_fetch_result(raw)            
            args['retstart'] += args['retmax']
            
        return results
        
    
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
            art_dict['affiliation'] = article.findtext('.//Article/Affiliation') if article.find('.//Article/Affiliation') is not None else ''  
            
            art_dict['abstract'] = article.findtext('.//Article/Abstract/AbstractText') if article.find('.//Article/Abstract/AbstractText') is not None else ''  
            art_dict['abstract_copyright'] = article.findtext('.//Article/Abstract/CopyrightInformation') if article.find('.//Article/Abstract/CopyrightInformation') is not None else ''  
            
            art_dict['medline_status'] = article.find('MedlineCitation').get('Status') if article.find('MedlineCitation').get('Status') is not None else ''
            art_dict['pubmed_status'] = article.findtext('.//PubmedData/PublicationStatus') if article.find('.//PubmedData/PublicationStatus') is not None else ''
            #for entrez_date in article.findall('.//PubmedData/History/PubMedPubDate[@PubStatus="entrez"]'):
            # art_dict['entrez_date'] = '...'
            
            # Journal details
            journal = {}
            journal['name'] = article.findtext('.//Article/Journal/Title') if article.find('.//Article/Journal/Title') is not None else ''  
            journal['name_abbrv'] = article.findtext('.//MedlineJournalInfo/MedlineTA') if article.find('.//MedlineJournalInfo/MedlineTA') is not None else ''  
            journal['issn_online'] = article.findtext('.//Article/Journal/ISSN[@IssnType="Electronic"]') if article.find('.//Article/Journal/ISSN[@IssnType="Electronic"]') is not None else ''  
            journal['issn_print'] = article.findtext('.//Article/Journal/ISSN[@IssnType="Print"]') if article.find('.//Article/Journal/ISSN[@IssnType="Print"]') is not None else ''                          
            art_dict['journal'] = journal
            
            # Citation
            # -- basic details
            citation = {}
            citation['pages'] = article.findtext('.//Article/Pagination/MedlinePgn') if article.find('.//Article/Pagination/MedlinePgn') is not None else ''  
            citation['volume'] = article.findtext('.//Article/Journal/JournalIssue/Volume') if article.find('.//Article/Journal/JournalIssue/Volume') is not None else ''  
            citation['issue'] = article.findtext('.//Article/Journal/JournalIssue/Issue') if article.find('.//Article/Journal/JournalIssue/Issue') is not None else ''  
            # -- pub date
            citation['date'] = article.findtext('.//Article/Journal/JournalIssue/PubDate/Year') if article.find('.//Article/Journal/JournalIssue/PubDate/Year') is not None else ''
            citation['date'] = "%s %s" % (citation['date'], article.findtext('.//Article/Journal/JournalIssue/PubDate/Month')) if article.find('.//Article/Journal/JournalIssue/PubDate/Month') is not None else citation['date']
            citation['date'] = "%s %s" % (citation['date'], article.findtext('.//Article/Journal/JournalIssue/PubDate/Day')) if article.find('.//Article/Journal/JournalIssue/PubDate/Day') is not None else citation['date']
            art_dict['citation'] = citation
            
            # MeSH headings
            art_dict['subjects'] = []
            for subj in article.findall('.//MeshHeadingList/MeshHeading'):
                desc_name = subj.findtext('DescriptorName') if subj.find('DescriptorName') is not None else ''
                desc_is_major = True if article.find('DescriptorName[@MajorTopicYN="Y"]') is not None else False
                art_dict['subjects'].append({'name': desc_name, 'is_major': desc_is_major})
                
                for qual in subj.findall('QualifierName'):
                    qual_name = qual.text
                    qual_is_major = True if qual.get('MajorTopicYN') == 'Y' else False
                    art_dict['subjects'].append({'name': "%s/%s" % (desc_name,qual_name), 'is_major': qual_is_major})
            
            # Cache raw XML string
            art_dict['raw'] = etree.tostring(article)
            
            articles_list.append(art_dict)
            
        return articles_list
    