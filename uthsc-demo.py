#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pubmed import PubMedEntrez

QUERY = '"ut memphis"[Affiliation] \
OR ("ut"[Affiliation] AND "memphis"[Affiliation]) \
OR ("ut health science center"[Affiliation] AND "tennessee"[Affiliation]) \
OR ("ut health science center"[Affiliation] AND "memphis"[Affiliation]) \
OR ("ut health sciences center"[Affiliation] AND "tennessee"[Affiliation]) \
OR ("ut health sciences center"[Affiliation] AND "memphis"[Affiliation]) \
OR (ut health sci*[Affiliation] AND "memphis"[Affiliation]) \
OR (university of tennessee health sci*[Affiliation] AND "memphis"[Affiliation]) \
OR "university of tennessee memphis"[Affiliation] \
OR ("university of tennessee"[Affiliation] AND "memphis"[Affiliation]) \
OR "university of tennessee health science center"[Affiliation] \
OR "university of tennessee health sciences center"[Affiliation] \
OR "university of tennessee college of medicine"[Affiliation] \
OR ("ut college of medicine"[Affiliation] AND "memphis"[Affiliation]) \
OR ("ut college of medicine"[Affiliation] AND "tennessee"[Affiliation]) \
OR ("utmem"[Affiliation] AND "tennessee"[Affiliation]) \
OR ("uthsc"[Affiliation] AND "tennessee"[Affiliation])'

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    pme = PubMedEntrez('test@test.edu')

    if len(args) == 1:
        results = pme.search("%s[uid]" % (args[0],), True, **{'retmax': 1})
    else:
        results = pme.search(QUERY, True, **{'retmax': 5}) 
 
    for a in results['articles']:
        #print a
        print a['pmid']
        print a['affiliation']
        print a['title']
        print a['journal']['name']
        print a['citation']
        print a['pubdate']
        print a['authors']
        print '-'*100
