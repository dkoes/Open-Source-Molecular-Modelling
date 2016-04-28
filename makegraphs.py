#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib as mpl
import prettyplotlib as ppl
import seaborn 
import bibtexparser
import numpy as np
import sys,re,glob,collections,os

'''One-off script for extracting information from latex files for
open source modeling paper and turning them into graphs.'''

licenses = []
develops = []
usages = []
activities = []
citationcnt = 0
cites = set()

for tex in glob.glob('*.tex'):
    for line in open(tex):
        m = re.search(r'^.*&.*&(.*)&(.*)&(.*)\\\\', line)
        if m and m.group(1).strip() != 'License':
            c = re.search(r'\\cite\{(.*)\}',m.group(3))
            if c:
                cites.add(c.group(1))
            activity = m.group(2).strip()
            lic = m.group(1).strip()
            licenses.append(lic)
            activities.append(activity)
            if len(activity) == 2:
                develops.append(activity[0])
                usages.append(activity[1])
            else:
                print "Missing activity code:",line
            if len(lic) == 0:
                print "Missing license:",line
            if len(m.group(3).strip()) > 0:
                citationcnt += 1

lcnt = collections.Counter(licenses)
dcnt = collections.Counter(develops)
ucnt = collections.Counter(usages)
acnt = collections.Counter(activities)

seen = set()
dois = []
years = dict()
with open('bibliography/biblio.bib') as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)
    for e in bib_database.entries:
        if 'ID' in e and e['ID'] in cites and 'doi' in e:
            seen.add(e['ID'])
            dois.append(e['doi'])
            years[e['doi']] = int(e['year'])
            
citeddois = set()
citations = []
normcitations = []
with open('cites') as cite_file:
    for line in cite_file:
        (doi,cnt) = line.split()
        citations.append(int(cnt))
        citeddois.add(doi)
        year = years[doi]
        normc = float(cnt)/(2016-year+1)
        normcitations.append(normc)

for doi in dois:
    if doi not in citeddois:
        print "Not cited:",doi

def makepie(cnt,name,num=-1):
    labels = []
    x = []
    for (l,val) in sorted(cnt.iteritems(), key=lambda (l,val): val, reverse=True):
        labels.append(l)
        x.append(val)
        
    if num > 0 and num < len(x):
        extra = np.sum(x[num:])
        x = x[:num]
        labels = labels[:num]
        labels.append('Other')
        x.append(extra)
    plt.figure(figsize=(6,6))
    plt.axis('equal')
    if num > 3: #license colors
        colors = [(0.2980392156862745, 0.4470588235294118, 0.6901960784313725),
                (0.39215686274509803, 0.7098039215686275, 0.803921568627451),
                 (0.3333333333333333, 0.6588235294117647, 0.40784313725490196),
                  (0.7686274509803922, 0.3058823529411765, 0.3215686274509804),
                   (0.5058823529411764, 0.4470588235294118, 0.6980392156862745),
                    (0.8, 0.7254901960784313, 0.4549019607843137),
                    (0.2, 0.2, 0.2)]
    else:
        colors = seaborn.color_palette()
    patches, texts = plt.pie(x,labels=labels,colors=colors)
    for text in texts:
        text.set_fontsize(24)
    for patch in patches:
        patch.set_edgecolor('white')

    plt.savefig(name,bbox_inches='tight',pad_inches=0)
    plt.clf()

print acnt
print "Citable: %d (%.2f)" % (citationcnt,citationcnt/float(len(licenses)))
print "Total:",len(licenses)

makepie(lcnt,"licenses.pdf",5)
makepie(ucnt,"usage.pdf")
makepie(dcnt,"develop.pdf")

plt.style.use('classic')

plt.style.use('seaborn-colorblind')

plt.figure(figsize=(10,6))

plt.gca().set_yscale('log')
plt.xlabel("Publication Citation Rank",fontsize=16)
plt.ylabel("Number of Citations per Year",fontsize=16)
plt.plot(sorted(normcitations),linewidth=3)
#plt.plot(sorted(citations),linewidth=3)
plt.ylim(0.1,1000)
plt.savefig('citedist.pdf',bbox_inches='tight')
