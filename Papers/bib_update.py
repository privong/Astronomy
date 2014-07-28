#!/usr/bin/env python
#
# Load a bibtext file, find the arXiv entries within the past X years and 
# query ADS to see if the paper has been published. If so, update the bibtex
# entry.

import pycurl
from bibtexparser.bparser import BibTexParser
import sys
import os
import re
import ads  # https://github.com/andycasey/ads


def checkRef(entry):
    """
    Check ADS for an updated reference 
    """
    if 'eprint' in entry.keys():
        res = ads.query(entry['year']+"arXiv"+entry['eprint'])
        for i in res:
            print entry['author'],entry['title']
            print i.author[0],i.title,i.year
            sel = raw_input('Is this a match (y/n)? ')
            if sel == 'y':
                print entry
                print 'would be replaced with '
                print i.author,i.year,i.title

    return 0

bibfile = sys.argv[1]

if os.path.isfile(bibfile):
    bib = open(bibfile,'r')
    bp = BibTexParser(bib.read()).get_entry_dict()
    bib.close()
else:
    sys.stderr.write("Error, could not open: "+bibfile+".\n")
    sys.exit(1)

upcount = 0
match = False
for ref in bp.keys():
    if bp[ref]['type']=='article':
        if 'journal' in bp[ref].keys():
            if re.search('arxiv',bp[ref]['journal']) or re.search('arXiv',bp[ref]['journal']):
                match = True
        elif 'Journal' in bp[ref].keys():
            if re.search('arxiv',bp[ref]['Journal']) or re.search('arXiv',bp[ref]['Journal']):
                match = True
        else:
            if 'arxivid' in bp[ref].keys():
                match = True
            else:
                sys.stdout.write(ref+' does not have a journal entry or arXiv ID.\n')

        if match:
            match = False # reset
            res = checkRef(bp[ref])
            if res:
                upcount += 1
                bp[ref] = res

sys.stdout.write(str(upcount)+' references updated.\n')
