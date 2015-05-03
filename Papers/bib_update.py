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


def checkRef(entry, confirm=False):
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
        res = ads.query("arXiv:" + entry['eprint'])
        try:
            for i in res:
                try:    # only want things that are published
                    print i.pub
                    if re.search('arxiv', i.pub, re.IGNORECASE):
                        continue
                except:
                    continue
                if confirm:
                    print entry['author'].split(',')[0], entry['title'], \
                          entry['year']
                    print i.author[0], i.title[0], i.year
                    sel = raw_input('Is this a match (y/n)? ')
                else:
                    sel = 'y'
                if sel == 'y':  # replace relevant bibtex entries
                    entry['author'] = '{' + entry['author'] + '}'
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
                    entry['adsurl'] = 'http://adsabs.harvard.edu/abs/' + i.bibcode
                    if not(re.search(i.year, entry['id'])):
                        sys.stderr.write("Warning: Updating year of: " +
                                         entry['id'] +
                                         " to reflect publication year (" +
                                         i.year + ").\n")
                        entry['id'] = entry['id'].split('2')[0] + i.year
                    return entry
        except:
            sys.stderr.write("API issue")
        return False

def aref(entry, confirm=False):
    """
    Check ADS for a preprint associated with a published article.
    """
    if 'doi' in entry.keys():
        res = ads.query('doi:' + entry['doi'])
        try:
            for i in res:
                try:
                    for j in i.identifier:
                        if re.search('arXiv:', j):
                            ID = j.split(':')[1]
                            entry['arxivid'] = ID
                            entry['Eprint'] = ID
                            entry['archiveprefix'] = 'arXiv'
                            return entry
                        elif re.search('astro-ph/', j):
                            ID = j
                            entry['arxivid'] = ID
                            entry['Eprint'] = ID
                            entry['archiveprefix'] = 'arXiv'
                            return entry
                except:
                    pass
        except:
            entry['arxivsearched'] = 'True'
            return entry
    entry['arxivsearched'] = 'True'
    return entry

parser = argparse.ArgumentParser(description="Update arXiv entries in a bibtex \
                                 file with subsequently published papers.")
parser.add_argument('bibfile', action='store', type=str, default=False,
                    help='BibTeX file')
parser.add_argument('--confirm', '-c', action='store_true', default=False,
                    help='If passed, confirm each entry.')
parser.add_argument('--arXiv', '-a', action='store_true', default=False,
                    help='For published entries, Search ADS for an arXiv \
                          entries if not present.')
args = parser.parse_args()

if os.path.isfile(args.bibfile):
    bib = codecs.open(args.bibfile, 'r', 'utf-8')
    bp = BibTexParser(bib.read())
    bib.close()
else:
    sys.stderr.write("Error, could not open: " + args.bibfile + ".\n")
    sys.exit(1)

# back up library before we start
shutil.copy2(args.bibfile, args.bibfile + 'ads_updater.bak')

upcount = 0
acount = 0
match = False
aphsearch = False
j = 0
for j in range(len(bp.entries)):
    thisref = bp.entries[j]
    if thisref['type'] == 'article':  # not interested in anything else
        if 'journal' in thisref.keys():
            if re.search('arxiv', thisref['journal'], re.IGNORECASE):
                match = True
            elif 'eprint' not in thisref.keys() and args.arXiv:
                aphsearch = True
        elif 'Journal' in thisref.keys():
            if re.search('arxiv', thisref['Journal'], re.IGNORECASE):
                match = True
            elif 'eprint' not in thisref.keys() and args.arXiv:
                aphsearch = True
        else:
            if 'arxivid' in thisref.keys():
                match = True
            else:
                sys.stdout.write(thisref['id'] + \
                                 ' does not have a journal entry or arXiv ID.\n')

        if match:
            match = False   # reset
            sys.stdout.write('Searching for update to ' + thisref['id'] +
                             '...')
            res = checkRef(thisref, args.confirm)
            if res:
                upcount += 1
                bp.entries[j] = res
                sys.stdout.write(thisref['id'] +
                                 " updated. Please verify changes.\n")
                newbib = to_bibtex(bp)
                if upcount + acount % 20 == 0:
                    outf = codecs.open(args.bibfile, 'w', 'utf-8')
                    outf.write(newbib)
                    outf.close()

            else:
                sys.stdout.write("No new version found.\n")

        if aphsearch and \
           not('arxivsearched' in thisref.keys()) and \
           thisref['year'] >= '1991':
            aphsearch = False
            sys.stdout.write('No preprint associated with ' + thisref['id'] +
                             ', checking...\n')
            res = aref(thisref, args.confirm)
            if res and not('arxivsearched' in thisref.keys()):
                acount += 1
                bp.entries[j] = res
                sys.stdout.write(thisref['id'] +
                                 " updated with a preprint. Please verify changes.\n")
                newbib = to_bibtex(bp)
                if upcount + acount % 20 == 0:
                    outf = codecs.open(args.bibfile, 'w', 'utf-8')
                    outf.write(newbib)
                    outf.close()
            elif 'arxivsearched' in thisref.keys():
                sys.stdout.write("No preprint found. Will not search again.\n")
            else:
                sys.stdout.write("No preprint found.\n")

outf = codecs.open(args.bibfile, 'w', 'utf-8')
try:
    outf.write(newbib)
except:
    outf.write(to_bibtex(bp))
outf.close()

sys.stdout.write(str(upcount) + ' reference(s) updated with journal articles.\n')
sys.stdout.write(str(acount) + ' reference(s) updated with preprints.\n')
