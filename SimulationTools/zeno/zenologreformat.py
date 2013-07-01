#!/usr/bin/python
#
# zenoLogReformat.py
#
# Read in a zeno logfile and reformat it for plotting.

import sys,re,argparse

parser=argparse.ArgumentParser(description='Reformat zeno treecode logs into a single-line format.')
parser.add_argument('logfile',type=str,help='name of the zeno treecode log')
args=parser.parse_args()

infile=open(args.logfile,'r')
ofname=args.logfile.split('.log')[0]+'-reformat.log'
ofile=open(ofname,'w')
ofile.write('#       time   |T+U|       T      -U    -T/U  |Vcom|  |Jtot|  CPUtot\n')

writenext=False
for line in infile:
  if writenext:
    ofile.write(line)
    writenext=False
  if re.search('T\+U',line):
    writenext=True

ofile.close()
infile.close()
