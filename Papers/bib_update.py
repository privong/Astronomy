#!/usr/bin/env python
#
# Load a bibtext file, find the arXiv entries within the past X years and 
# query ADS to see if the paper has been published. If so, update the bibtex
# entry.

import pycurl,bibtexparser

# get ADSABS dev key
of=open('ADS_Key','r')
key='dev_key='+of.readline().rstrip()
of.close()

urlbase='http://adslabs.org/adsabs/api/search/?fmt=json&'+key
recordbase='http://adslabs.org/adsabs/api/record/'
