#!/usr/bin/python
#
# luci_select.py
# Given an selection criteria, print a list of matching FITS files.
#
# Last modified: 06 June 2011 by George Privon gcp8y@virginia.edu
#
# Arguments (all optional except the filelist)
# --itime	integration time
# --object	desired object
# --readmode	readout mode (searches a substring)
# --filter	desired filter (searches FILTER1 and FILTER2)
# filelist	list of FITS files to search
#
# Usage:
# luci_select.py [OPTIONS] filelist

import pyfits,sys,getopt,os,re,glob

def usage():
  sys.stderr.write('Usage:\n')
  sys.stderr.write(sys.argv[0]+' [OPTIONS] filelist\n\n')
  sys.stderr.write('Acceptable options are:\n')
  sys.stderr.write('\t--itime=\tintegration time\n')
  sys.stderr.write('\t--object=\tObject name\n')
  sys.stderr.write('\t--readmode=\treadout mode (searches a substring)\n')
  sys.stderr.write('\t--filter=\tdesired filter (searches FILTER 1 and FILTER2 keywords. EXACT mach needed)\n\n')


################################################################################
# Start script
################################################################################
# get arguments
if len(sys.argv)<2:
  sys.stderr.write('\nERROR: insufficient command line arguments.\n\n')
  usage()
  sys.exit(-1)

if re.match('--help',sys.argv[1]) or re.match('-h',sys.argv[1]):
  sys.stderr.write(sys.argv[0].split('/').pop()+' - Create lists of LUCIFER files according to selection criteria.\n')
  usage()
  sys.exit(0)

# get the command line arguments
try:
  optlist=getopt.getopt(sys.argv[1:],'x',['itime=','object=','readmode=','filter='])
except getopt.GetoptError, err:
  sys.stderr.write(str(err))
  usage()
  sys.exit(-1)

# start parsing through the list of arguments
optlist=list(optlist)
files=optlist.pop()
optlist.append([('foo','null')])	# need it to be at least 2 elements long

args={}
for o,a in optlist[0]:
  if o=='--itime':
    args['ITIME']=a
  elif o=='--object':
    args['OBJECT']=a
  elif o=='--readmode':
    args['READMODE']=a
  elif o=='--filter':
    args['FILTER']=a
  else:
    assert False, "unhandled option"

# now crunch through the files
for file1 in files:
  file1=glob.glob(file1)
  for file in file1:
    match=1
    if os.path.isfile(file):
      lucif=pyfits.open(file)
      for kw in args.keys():
        if re.match("FILTER",kw):
          # need to search both filter keywords
          if re.match(args[kw],str(lucif[0].header['FILTER1'])) or re.match(args[kw],str(lucif[0].header['FILTER2'])):
            match=match*1
          else:
            match=match*0
        else:
          if re.search(args[kw],str(lucif[0].header[kw])):
            # we've found the keyword
            match=match*1
          else:
            match=match*0
      lucif.close()
    else:
      sys.stderr.write('ERROR: '+file+' not located, skipping.\n')
      match=0

    if match:
      print file

