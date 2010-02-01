#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pubmed import PubMedEntrez

QUERY = '"ut memphis"[Affiliation] OR ("university of Tennessee Memphis"[Affiliation] \
OR "university of Tennessee health science center"[Affiliation]) OR \
"uthsc"[Affiliation] OR University of Tennessee College of Medicine[Affiliation] \
OR (*utmem*[Affiliation] AND *edu*[Affiliation])'

pme = PubMedEntrez('test@test.edu')
#raw = open('efetch.xml','rU').read()
#print pme.parse_fetch_result(raw)[0]
pme.search(QUERY)