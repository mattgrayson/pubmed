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
print QUERY
#pme = PubMedEntrez('test@test.edu')
#articles = pme.search(QUERY)
 
# for a in articles:
#     print a['pmid']
#     print a['affiliations']
#     print a['title']
#     print '-'*100