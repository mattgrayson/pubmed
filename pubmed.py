#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pubmed.py

Simple interface for searching and retrieving articles from PubMed via the 
Entrez Programming Utilities <http://eutils.ncbi.nlm.nih.gov/>. It does not 
provide access to all of the Entrez utilities and only parses a subset of the 
elements included in PubmedArticle. There's probably a better way to do this ...

Required: Python 2.5 or later
Required: httplib2
Required: lxml
Required: dateutil
"""

__author__ = "Matt Grayson (mattgrayson@uthsc.edu)"
__copyright__ = "Copyright 2009-2010, Matt Grayson"
__license__ = "MIT"
__version__ = "0.3.3"


import httplib2
import re
import urllib
from datetime import datetime
from lxml import etree
from dateutil import parser as dateparser

class PubMedEntrez(object):
    """
    """    
    ENTREZ_BASE_URI = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    DEFAULT_DATE = datetime(datetime.now().year,1,1)
    MEDLINEDATE_YEAR_MONTH = re.compile(r'^(?P<year>\d{4}) (?P<month>\w{3})[\s-]')
    MEDLINEDATE_YEAR_SEASON = re.compile(r'^(?P<year>\d{4}) (?P<season>\w+)[\s-]')
    MEDLINEDATE_YEAR = re.compile(r'^\d{4}')
    
    def __init__(self, email):
        self.search_results = ''
        self.last_query = ''
        self.email_address = email
        self.search_uri = '%s/esearch.fcgi?db=pubmed&retmode=xml&usehistory=y&tool=pubmedpy&email=%s' % (self.ENTREZ_BASE_URI, email)
        self.fetch_uri = '%s/efetch.fcgi?db=pubmed&retmode=xml&rettype=full&tool=pubmedpy&email=%s' % (self.ENTREZ_BASE_URI, email)
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
            if args.has_key('retmax'):
                total = args['retmax']
            else:
                total = results['total_found']
            results['articles'] = self.fetch_query_results(
                results['query_key'], 
                results['web_env'], 
                total
            )
        else:
            results['pmids'] = [e.text for e in xml_tree.findall('IdList/Id')]
            
        return results
    
    def fetch_query_results(self, query_key, web_env, total_to_retrieve):
        results = []
        args = {
            'WebEnv': web_env,
            'query_key': query_key,
            'retstart': 0,
            'retmax': total_to_retrieve if total_to_retrieve < 500 else 500
        }

        while args['retstart'] < total_to_retrieve:
            print 'Fetching results %s - %s ...' % (args['retstart'], args['retstart']+args['retmax'])                
            raw = self._get(self.fetch_uri, args)            
            results += self.parse_fetch_result(raw)            
            args['retstart'] += args['retmax']
            
        return results
        
    
    def parse_fetch_result(self, raw):
        xml_tree = etree.XML(raw)
        articles_list = []
        for article in xml_tree.findall('PubmedArticle'):
            a = {'raw_xml': etree.tostring(article)}            
            a['pmid'] = article.findtext('MedlineCitation/PMID') if article.findtext('MedlineCitation/PMID') is not None else ''
            a['title'] = article.findtext('MedlineCitation/Article/ArticleTitle') if article.findtext('MedlineCitation/Article/ArticleTitle') is not None else ''
            a['authors'] = []
            for auth in article.findall('MedlineCitation/Article/AuthorList/Author'):
                if auth.find('LastName') is not None:
                    auth_str = auth.findtext('LastName')
                else:
                    continue
                
                if auth.find('Initials') is not None:
                    auth_str = "%s %s" % (auth_str, auth.findtext('Initials'))
                elif auth.find('ForeName') is not None:
                    auth_str = "%s %s" % (auth_str, auth.findtext('ForeName'))
                a['authors'].append(auth_str)
            a['affiliation'] = article.findtext('MedlineCitation/Article/Affiliation') if article.findtext('MedlineCitation/Article/Affiliation') is not None else ''  
            
            a['abstract'] = article.findtext('MedlineCitation/Article/Abstract/AbstractText') if article.findtext('MedlineCitation/Article/Abstract/AbstractText') is not None else ''  
            a['abstract_copyright'] = article.findtext('MedlineCitation/Article/Abstract/CopyrightInformation') if article.findtext('MedlineCitation/Article/Abstract/CopyrightInformation') is not None else ''  
            
            a['medline_status'] = article.find('MedlineCitation').get('Status') if article.find('MedlineCitation').get('Status') is not None else ''
            a['pubmed_status'] = article.findtext('PubmedData/PublicationStatus') if article.findtext('PubmedData/PublicationStatus') is not None else ''
            #for entrez_date in article.findall('.//PubmedData/History/PubMedPubDate[@PubStatus="entrez"]'):
            # art_dict['entrez_date'] = '...'
            
            # Journal details
            a['journal'] = {}
            a['journal']['name'] = article.findtext('MedlineCitation/Article/Journal/Title') if article.findtext('MedlineCitation/Article/Journal/Title') is not None else ''              
            a['journal']['name_abbreviated'] = article.findtext('MedlineCitation/MedlineJournalInfo/MedlineTA') if article.findtext('MedlineCitation/MedlineJournalInfo/MedlineTA') is not None else ''  
            a['journal']['issn_online'] = article.findtext('MedlineCitation/Article/Journal/ISSN[@IssnType="Electronic"]') if article.findtext('MedlineCitation/Article/Journal/ISSN[@IssnType="Electronic"]') is not None else ''  
            a['journal']['issn_print'] = article.findtext('MedlineCitation/Article/Journal/ISSN[@IssnType="Print"]') if article.findtext('MedlineCitation/Article/Journal/ISSN[@IssnType="Print"]') is not None else ''                          
            a['journal']['nlm_unique_id'] = article.findtext('MedlineCitation/MedlineJournalInfo/NlmUniqueID') if article.findtext('MedlineCitation/MedlineJournalInfo/NlmUniqueID') is not None else ''              
            
            # Citation
            # -- basic details
            a['pages'] = article.findtext('MedlineCitation/Article/Pagination/MedlinePgn') if article.findtext('MedlineCitation/Article/Pagination/MedlinePgn') is not None else ''
            a['volume'] = article.findtext('MedlineCitation/Article/Journal/JournalIssue/Volume') if article.findtext('MedlineCitation/Article/Journal/JournalIssue/Volume') is not None else ''  
            a['issue'] = article.findtext('MedlineCitation/Article/Journal/JournalIssue/Issue') if article.findtext('MedlineCitation/Article/Journal/JournalIssue/Issue') is not None else ''
            a['volume_issue'] = "%s(%s)" % (a['volume'],a['issue']) if a['issue'] != '' else a['volume']
            # -- publicate date
            a['pubdate_year'] = article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Year') if article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Year') is not None else ''
            a['pubdate_month'] = article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Month') if article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Month') is not None else ''
            a['pubdate_day'] = article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Day') if article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Day') is not None else ''
            a['pubdate_season'] = article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Season') if article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/Season') is not None else ''                        
            # -- medline date            
            a['medline_date'] = article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate') if article.findtext('MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate') is not None else ''

            # Create date string
            def season_to_month(season):
                season = season.lower()
                if season == 'spring':
                    month = 'Mar'
                elif season == 'summer':
                    month = 'Jun'
                elif season == 'fall':
                    month = 'Sep'
                elif season == 'winter':
                    month = 'Dec'
                else:
                    month = 'Jan'
                return month
            
            if a['pubdate_month'] != '':
                a['pubdate_str'] = ("%s %s %s" % (a['pubdate_year'], a['pubdate_month'], a['pubdate_day'])).strip()
            elif a['pubdate_season'] != '':
                a['pubdate_month'] = season_to_month(a['pubdate_season'])
                a['pubdate_day'] = 1
                a['pubdate_str'] = ("%s %s %s" % (a['pubdate_year'], a['pubdate_month'], a['pubdate_day'])).strip()
            else:
                medline_year_month = self.MEDLINEDATE_YEAR_MONTH.search(a['medline_date'])
                medline_year_season = self.MEDLINEDATE_YEAR_SEASON.search(a['medline_date'])
                if medline_year_month != None:
                    dates = medline_year_month.groupdict()
                    a['pubdate_year'] = dates['year'] if a['pubdate_year'] == '' else a['pubdate_year']
                    a['pubdate_month'] = dates['month']
                    a['pubdate_day'] = 1
                    a['pubdate_str'] = ("%s %s %s" % (a['pubdate_year'], a['pubdate_month'], a['pubdate_day'])).strip()
                elif medline_year_season != None:
                    dates = medline_year_season.groupdict()                  
                    a['pubdate_year'] = dates['year'] if a['pubdate_year'] == '' else a['pubdate_year']
                    a['pubdate_month'] = season_to_month(dates['season'])
                    a['pubdate_day'] = 1
                    a['pubdate_str'] = ("%s %s %s" % (a['pubdate_year'], a['pubdate_month'], a['pubdate_day'])).strip()
                else:
                    # Pubmed date only used as a last resort
                    pubmed_date_year = article.findtext('PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Year') if article.findtext('PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Year') is not None else ''
                    pubmed_date_month = article.findtext('PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Month') if article.findtext('PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Month') is not None else ''
                    pubmed_date_day = article.findtext('PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Day') if article.findtext('PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]/Day') is not None else ''
                    a['pubdate_year'] = pubmed_date_year
                    a['pubdate_month'] = pubmed_date_month
                    a['pubdate_day'] = pubmed_date_day
                    a['pubdate_str'] = ("%s %s %s" % (pubmed_date_year, pubmed_date_month, pubmed_date_day))

            # Parse datetime obj from date string
            try:                
                a['pubdate'] = dateparser.parse(a['pubdate_str'], fuzzy=True, yearfirst=True, default=self.DEFAULT_DATE)
            except ValueError:
                year = self.MEDLINEDATE_YEAR.search(a['pubdate_str'])
                if year is not None:
                    a['pubdate'] = datetime(int(year.group()),1,1)
                else:
                    a['pubdate'] = self.DEFAULT_DATE
            
            
            # -- derived citation
            a['citation'] = a['medline_date'] if a['medline_date'] != '' else a['pubdate'].strftime("%Y")
            a['citation'] = "%s %s" % (a['citation'], a['pubdate_season']) if a['pubdate_season'] != '' else "%s %s" % (a['citation'], a['pubdate'].strftime("%b"))            
            a['citation'] = "%s; %s" % (a['citation'], a['volume_issue']) if a['volume_issue'] != '' else a['citation']
            a['citation'] = "%s: %s." % (a['citation'], a['pages']) if a['pages'] != ('' or None) else "%s." % (a['citation'],)
            
            # MeSH headings
            a['subjects'] = []
            for subj in article.findall('MedlineCitation/MeshHeadingList/MeshHeading'):
                for desc in subj.findall('DescriptorName'):
                    desc_name = desc.text
                    desc_is_major = True if desc.get('MajorTopicYN') == 'Y' else False
                    a['subjects'].append({'name': desc_name, 'qualifier': '', 'is_major': desc_is_major})
                
                for qual in subj.findall('QualifierName'):
                    qual_name = qual.text
                    qual_is_major = True if qual.get('MajorTopicYN') == 'Y' else False
                    a['subjects'].append({'name': desc_name, 'qualifier': qual_name, 'is_major': qual_is_major})
                        
            articles_list.append(a)
            
        return articles_list
    
