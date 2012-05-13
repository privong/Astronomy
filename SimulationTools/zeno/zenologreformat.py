#!/usr/bin/python
#
# zenoLogReformat.py
#
# Read in a zeno logfile and reformat it for plotting.

import sys,re

if len(sys.argv) < 2:
  sys.stderr.write("Usage:\n"+sys.argv[0]+' logfile\n\n')
  exit(-1)

infile=open(sys.argv[1],'r')
ofname=sys.argv[1].split('.log')[0]+'-reformat.log'
ofile=open(ofname,'w')

lineno=0
# open the first 15 lines, prepend '#', and move to the meat.
while lineno<15:
  ofile.write('# '+infile.readline())
  lineno+=1

lhead=0
# read the meat of the data and write it out, continuing until the end
# this records: time, Nstep, freqmax, freqavg, Etot, Eint, Ekin, Epot, Erad,
#    |Jtot|, |Vcom|, and CPUtot
while infile.readline():
  tline=infile.readline().split()
  print tline
  blank=infile.readline()
  label1=infile.readline()
  label1v=infile.readline()
  blank=infile.readline()
  label2=infile.readline()
  label2v=infile.readline().split()
  blank=infile.readline()
  label3=infile.readline()
  label3v=infile.readline().split()
  blank=infile.readline()
  if not(re.search('----',infile.read(5))):
    print "we wrote an output file!"
    fline=infile.readline()
    blank=infile.readline()
  
  # now do the real work
  if not(lhead):
    # write out a header
    ofile.write('#time\tNstep\tfreqmax\tfreqavg\tEtot\t\tEint\tEkin\tEpot\t\tErad\t|Jtot|\t|Vcom|\tCPUtot\n')
    lhead=1
  # extract and write out what we want
  ofile.write(tline[1]+'\t'+tline[3]+'\t')
  ofile.write(label2v[6]+'\t'+label2v[7]+'\t')
  ofile.write(label3v[0]+'\t'+label3v[1]+'\t'+label3v[2]+'\t'+label3v[3]+'\t'+label3v[4]+'\t'+label3v[5]+'\t'+label3v[6]+'\t'+label3v[7]+'\n')

ofile.close()
infile.close()
