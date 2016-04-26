#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib as mpl
import prettyplotlib as ppl
import seaborn 
import numpy as np
import sys,re,glob,collections,os

'''One-off script for extracting information from latex files for
open source modeling paper and turning them into graphs.'''

licenses = []
develops = []
usages = []

for tex in glob.glob('*.tex'):
    for line in open(tex):
        m = re.search(r'^.*&.*&(.*)&(.*)&.*\\\\', line)
        if m and m.group(1).strip() != 'License':
            activity = m.group(2).strip()
            lic = m.group(1).strip()
            licenses.append(lic)
            if len(activity) == 2:
                develops.append(activity[0])
                usages.append(activity[1])
            else:
                print "Missing activity code:",line
            if len(lic) == 0:
                print "Missing license:",line
            

lcnt = collections.Counter(licenses)
dcnt = collections.Counter(develops)
ucnt = collections.Counter(usages)



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

print "Number:",len(licenses)

makepie(lcnt,"licenses.pdf",6)
makepie(ucnt,"usage.pdf")
makepie(dcnt,"develop.pdf")

