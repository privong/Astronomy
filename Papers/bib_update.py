#!/usr/bin/env python
#
# Load a bibtext file, find the arXiv entries within the past X years and
# query ADS to see if the paper has been published. If so, update the bibtex
# entry.

import pycurl
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import to_bibtex
import sys
import os
import shutil
import re
import ads  # https://github.com/andycasey/ads


def checkRef(entry):
    """
    Check ADS for an updated reference

    If a replacement entry is located, replace the following bibtex keys
        - doi
        - publication year
        - abstract
        - url
        - volume
        - page
        - year
        - pub(lication) (does not currently do abbreviations)
    """
    if 'eprint' in entry.keys():
        res = ads.query("arXiv:"+entry['eprint'])
        for i in res:
            print entry['author'],entry['title']
            print i.author[0],i.title,i.year
            sel = raw_input('Is this a match (y/n)? ')
            if sel == 'y':  # replace relevant bibtex entries
                entry['title'] = i.title[0]
                entry['year'] = i.year
                entry['journal'] = i.pub
                if 'i.doi' in globals():
                    entry['doi'] = i.doi[0]
                entry['abstract'] = i.abstract
                entry['link'] = i.url[0]
                entry['year'] = i.year
                entry['volume'] = i.volume
                entry['pages'] = i.page[0]
                entry['adsurl'] = 'http://adsabs.harvard.edu/abs/'+i.bibcode
                if not(re.search(i.year,entry['id'])):
                    sys.stderr.write("Warning: Updated year ("+i.year+") no longer matches ID: "+entry['id']+".\n")
                return entry
        return False

bibfile = sys.argv[1]

if os.path.isfile(bibfile):
    bib = open(bibfile,'r')
    bp = BibTexParser(bib.read())
    bib.close()
else:
    sys.stderr.write("Error, could not open: "+bibfile+".\n")
    sys.exit(1)

upcount = 0
match = False
j = 0
for j in range(len(bp.records)):
    thisref=bp.records[j]
    if thisref['type']=='article':  # not interested in anything else
        if 'journal' in thisref.keys():
            if re.search('arxiv',thisref['journal']) or re.search('arXiv',thisref['journal']):
                match = True
        elif 'Journal' in thisref.keys():
            if re.search('arxiv',thisref['Journal']) or re.search('arXiv',thisref['Journal']):
                match = True
        else:
            if 'arxivid' in thisref.keys():
                match = True
            else:
                sys.stdout.write(thisref['id']+' does not have a journal entry or arXiv ID.\n')

        if match:
            match = False # reset
            sys.stdout.write('Searching for update to '+thisref['id']+'...\n')
            res = checkRef(thisref)
            if res:
                upcount += 1
                bp.records[j] = res
                sys.stdout.write(thisref['id']+" updated. Please verify changes.\n")
            else:
                sys.stdout.write("No new version found for "+ref+".\n")

# back up library
shutil.copy2(bibfile,bibfile+'ads_updater.bak')
newbib = to_bibtex(bp)

# replace bibtex file
outf = open(bibfile,'w')
outf.write(newbib)
outf.close()

sys.stdout.write(str(upcount)+' reference(s) updated.\n')
