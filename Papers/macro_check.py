#!/usr/bin/env python2
#
# Compare privon_astro.sty entries with entries in a latex file to decide which
# macros to copy into a file for submission to journals.

import re
import sys
import os

# extract list of macros to search for
macros = {}
if os.path.isfile(os.environ['HOME'] +
                  '/astro/software/Astronomy/Papers/privon_astro.sty'):
    sty = open(os.environ['HOME'] +
               '/astro/software/Astronomy/Papers/privon_astro.sty', 'r')
    for line in sty:
        if re.search('newcommand', line):
            macros[line.split('{')[1].split('}')[0]] = line
    sty.close()

texfile = sys.argv[1]

if os.path.isfile(texfile):
    inf = open(texfile, 'r')
else:
    sys.stderr.write('Error opening: ' + texfile + '. Not found.\n')

keeplist = {}
for line in inf:
    for macro in macros.keys():
        if re.search(macro, line):
            keeplist[macro] = macros[macro]
            macros.pop(macro)
inf.close()

sys.stdout.write('Finished searching ' + texfile +
                 '. Please copy the following macros into your manuscript: \
                 \n\n')
for macro in keeplist.keys():
    sys.stdout.write(keeplist[macro])
