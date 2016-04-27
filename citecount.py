#!/usr/bin/env python


import numpy as np
import sys,re,glob,collections,os
import bibtexparser
import scholar
import time

cites = set()

for tex in glob.glob('*.tex'):
    for line in open(tex):
        m = re.search(r'^.*&.*&(.*)&(.*)& \\cite\{(.*)\}.*\\\\', line)
        if m and m.group(1).strip() != 'License':
            cites.add(m.group(3))

seen = set()
dois = []
with open('bibliography/biblio.bib') as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)
    for e in bib_database.entries:
        if 'ID' in e and e['ID'] in cites and 'doi' in e:
            seen.add(e['ID'])
            dois.append(e['doi'])

notseen = cites - seen

querier = scholar.ScholarQuerier()

citecnts = []

for doi in dois:
    query = scholar.SearchScholarQuery()
    query.set_words(doi)
    querier.send_query(query)
    
    if len(querier.articles) > 0 :
        art = querier.articles[0]
        txt = art.as_txt()
        if doi in txt:
            #print art['num_citations'],doi
            citecnts.append((doi,art['num_citations']))
        else:
            print "NOTFOUND",doi
    else:
        print "REALLYNOTFOUND",doi
    time.sleep(1)
        
with open('citecnts.txt','w') as out:
    for (doi,num) in citecnts:
        out.write('%s %d\n' % (doi,num))
    
