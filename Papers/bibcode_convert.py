#!/usr/bin/env python2
#
# Convert long-form Journal names to the appropriate ApJ bibcode.

import re
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import to_bibtex
import sys
import os


# get ibliographic codes from: http://adsabs.harvard.edu/abs_doc/refereed.html
journals = {'monthly notices of the royal astronomical society': '\mnras',
            'astrophysical journal letters': '\apjl',
            'astrophysical journal supplement': '\apjs',
            'astrophysical journal': '\apj'}
