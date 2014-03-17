#!/usr/bin/env python
#
# Process NED data

import sys,re

fin=open(sys.argv[1],'r')
out=open('NED-reformat.dat','w')
go=0

out.write('#Source\t12\t25\t60\t100')

for line in fin:
  if go:
    # do stuff
    if re.search('PHOTO',line):
      # extract the source name
      out.write('\n')
      out.write(''.join(str(line.split()[1:])))
      out.write('\t')
    if re.search('IRAS',line):
      if not(re.search('targeted',line)) and not(re.search('Qualifiers',line)) and not(re.search('refcode',line)):
        out.write(line.split()[4])
        out.write('\t')
  elif re.search('SEARCH RESULTS',line):
    go=1

fin.close()
out.close()
