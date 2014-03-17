#!/usr/bin/env python
#
# VATT_headerfix.py
#
# Fix headers of FITS files for VATT observations.

import pyfits,sys,os,re,glob,getopt,datetime

def usage():
  sys.stderr.write('Usage:\n')
  sys.stderr.write(sys.argv[0]+' [OPTIONS] filelist\n\n')
  sys.stderr.write('Acceptable options are:\n')
  sys.stderr.write('\t--observer=\tobserverstring\n')
  sys.stderr.write('\t--filter=\tFilter String\t\t(only applied to object and flat files)\n')

################################################################################
# Start script
################################################################################
# get arguments
if len(sys.argv)<2:
  sys.stderr.write('\nERROR: insufficient command line arguments.\n\n')
  usage()
  sys.exit(-1)

# get the command line arguments
try:
  optlist=getopt.getopt(sys.argv[1:],'x',['observer=','filter='])
except getopt.GetoptError, err:
  sys.stderr.write(str(err))
  usage()
  sys.exit(-1)

# start parsing through the list of arguments
optlist=list(optlist)
files=optlist.pop()
optlist.append([('foo','null')])        # need it to be at least 2 elements long

args={}
for o,a in optlist[0]:
  if o=='--observer':
    args['OBSERVER']=a
  elif o=='--filter':
    args['FILTER']=a
  else:
    assert False, "unhandled option"

# get the current date and time (for the purposes of the history keywords)
datenow=datetime.datetime.today().isoformat()

# now crunch through the files and change the header keywords
for file1 in files:
  file1=glob.glob(file1)
  for file in file1:
    if os.path.isfile(file):
      frame=pyfits.open(file,mode='update')
      sys.stderr.write('Opened '+frame.filename()+'\t- ')
      if 'OBSERVER' in args.keys():
	# replace the observer keyword
        sys.stderr.write('Fixing OBSERVER keyword...\t')
	frame[0].header.update('OBSERVER',args['OBSERVER'])
	frame[0].header.add_history(datenow+' - Corrected OBSERVER keyword.')
      # only replace the filter for object or flat frames
      if 'FILTER' in args.keys() and (re.match('object',frame[0].header['IMAGETYP']) or re.match('flat',frame[0].header['IMAGETYP'])):
	oldfilt=0
	# replace the filter keyword
	if 'FILTER' in frame[0].header.keys():
	  oldfilt=frame[0].header['FILTER']
	frame[0].header.update('FILTER',args['FILTER'])
        if oldfilt:
          frame[0].header.add_history(datenow+' - Changed FILTER keyword from '+oldfilt+' to '+args['FILTER'])
	  sys.stderr.write('FILTER keyword updated...\t')
	else:
	  frame[0].header.add_history(datenow+' - FILTER keyword added.')
	  sys.stderr.write('FILTER keyword added...\t')
      # our work here is done, close the frame.
      frame.close()
      sys.stderr.write('File closed.\n')

