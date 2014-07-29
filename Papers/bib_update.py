#!/usr/bin/env python2
#
# Load a bibtext file, find the arXiv entries within the past X years and
# query ADS to see if the paper has been published. If so, update the bibtex
# entry.

from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import to_bibtex
import sys
import os
import shutil
import re
import codecs   # for unicode
import ads  # https://github.com/andycasey/ads
import argparse


def checkRef(entry,confirm=False):
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
            try:    # only want things that are published
                print i.pub
            except :
                continue
            if confirm:
                print entry['author'].split(',')[0],entry['title'],entry['year']
                print i.author[0],i.title[0],i.year
                sel = raw_input('Is this a match (y/n)? ')
            else:
                sel = 'y'
            if sel == 'y':  # replace relevant bibtex entries
                entry['author'] = '{'+entry['author']+'}'
                entry['title'] = i.title[0]
                entry['year'] = i.year
                entry['journal'] = i.pub
                try:
                    entry['doi'] = i.doi[0]
                except:
                    pass
                try: 
                    entry['abstract'] = i.abstract
                except:
                    pass
                entry['link'] = i.url[0]
                entry['year'] = i.year
                try: 
                    entry['volume'] = i.volume
                except:
                    pass
                try: 
                    entry['pages'] = i.page[0]
                except:
                    pass
                entry['adsurl'] = 'http://adsabs.harvard.edu/abs/'+i.bibcode
                if not(re.search(i.year,entry['id'])):
                    sys.stderr.write("Warning: Updating year of: "+entry['id']+" to reflect publication year ("+i.year+").\n")
                    entry['id'] = entry['id'].split('2')[0]+i.year
                return entry
        return False


parser=argparse.ArgumentParser(description="Update arXiv entries in a bibtex file with subsequently published papers.")
parser.add_argument('bibfile',action='store',type=str,default=False,help='BibTeX file')
parser.add_argument('--confirm',action='store_true',default=False,help='If passed, confirm each entry.')
args=parser.parse_args()

if os.path.isfile(args.bibfile):
    bib = codecs.open(args.bibfile,'r','utf-8')
    bp = BibTexParser(bib.read())
    bib.close()
else:
    sys.stderr.write("Error, could not open: "+args.bibfile+".\n")
    sys.exit(1)

# back up library before we start
shutil.copy2(args.bibfile,args.bibfile+'ads_updater.bak')

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
            sys.stdout.write('Searching for update to '+thisref['id']+'...')
            res = checkRef(thisref,args.confirm)
            if res:
                upcount += 1
                bp.records[j] = res
                sys.stdout.write(thisref['id']+" updated. Please verify changes.\n")
                newbib = to_bibtex(bp)
                # replace bibtex file as we go, every 10 fixes :)
                if upcount % 20 == 0:
                    outf = codecs.open(args.bibfile,'w','utf-8')
                    outf.write(newbib)
                    outf.close()

            else:
                sys.stdout.write("No new version found.\n")

outf = codecs.open(args.bibfile,'w','utf-8')
outf.write(newbib)
outf.close()

sys.stdout.write(str(upcount)+' reference(s) updated.\n')
