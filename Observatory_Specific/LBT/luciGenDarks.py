#!/usr/bin/python
#
# luciGenDarks.py
# Look through a list of LUCIFER files, extract the integration settings
# and generate LUCIFER scripts to take darks at the end of the night.
#
# Version 0.1
# Last modified: 08 June 2011 by George Privon gcp8y@virginia.edu

import os,pyfits,glob,sys,re
from datetime import datetime

def usage():
  sys.stderr.write('Generates two LUCIFER dark scripts based on an input file list of images.\n')
  sys.stderr.write('Usage:\n')
  sys.stderr.write(sys.argv[0]+' filelist\n\n')
  return 0

def writedark(fileh,ro,dit,ndit,nexp):
  fileh.write('DARK\t\t=')
  if re.match('o2.double.corr.read',ro):
   fileh.write('o2dcr')
  elif re.match('multiple.endpoints',ro):
   fileh.write('mer')
  fileh.write(' '+str(dit)+' '+str(ndit)+' '+str(nexp)+'\n')
  return 0

def writefirstdark(fileh,ro,dit,ndit,nexp,savem):
 fileh.write('DIT\t\t\t='+str(dit)+'\n')
 fileh.write('NDIT\t\t\t='+str(ndit)+'\n')
 fileh.write('NEXPO\t\t\t=5\n')
 fileh.write('ROE_MODE\t\t=')
 if re.match('o2.double.corr.read',ro):
   fileh.write('o2dcr\n')
 elif re.match('multiple.endpoints',ro):
   fileh.write('mer\n')
 fileh.write('SAVE_MODE\t\t='+savem+'\n')
 fileh.write('[END_READOUT_SETUP]\n\n[START_OBSERVING_SETUP]\n')
 fileh.write('#FLUSH_DETECTOR\nDARK\n')
 return 0

################################################################################
# Start script
################################################################################
# get arguments
sys.stderr.write('luciGenDarks.py - v0.1 (08 June 2011)\n')
sys.stderr.write('Run luciGenDarks.py without arguments for a usage message.\n')
sys.stderr.write('\n\n\nIMPORTANT: This code has not yet been vetted. It would be advisable to compare the output with the data to ensure all the necessary darks have been included.\n\n\n')
if len(sys.argv)<2:
  sys.stderr.write('\nERROR: insufficient command line arguments.\n\n')
  usage()
  sys.exit(-1)

firstI=True
firstN=True

Iwritten=[]
Nwritten=[]

# get the current date
utc=datetime.utcnow()
tdate=str(utc.year).zfill(2)+str(utc.month).zfill(2)+str(utc.day).zfill(2)

# open two dark scripts
outI=open(tdate+'_darks_int.txt','w')
outI.write('[START_READOUT_SETUP]\n')
outN=open(tdate+'_darks_norm.txt','w')
outN.write('[START_READOUT_SETUP]\n')

# get our filelist
files=sys.argv[1:]
for frame in files:
  if os.path.isfile(frame):
    lucif=pyfits.open(frame)
    # make sure we only look at object frames
    #if not(re.match('NOTSPECIFIED',lucif[0].header['OBJECT'])):
    if True:
      # load up the rest of the keywords
      readmode=lucif[0].header['READMODE']
      itime=str(lucif[0].header['ITIME'])
      ncoadds=str(lucif[0].header['NCOADDS'])
      if itime==str(lucif[0].header['EXPTIME']):
	# NDIT=1 or SAVEMODE=normal
	# can't differentiate based on current header info. do normal darks
        if not(firstN) and not(readmode+itime+ncoadds+'normal' in Nwritten):
          writedark(outN,readmode,itime,ncoadds,5)
          Nwritten.append(readmode+itime+ncoadds+'normal')
        elif firstN:
          firstN=False
          writefirstdark(outN,readmode,itime,ncoadds,5,'normal')
          Nwritten.append(readmode+itime+ncoadds+'normal')
      else:
        # NDIT!=1 and SAVEMODE=integrated
        if not(firstI) and not(readmode+itime+ncoadds+'integrated' in Iwritten):
          writedark(outI,readmode,itime,ncoadds,5)
          Iwritten.append(readmode+itime+ncoadds+'integrated')
        elif firstI:
          firstI=False
          writefirstdark(outI,readmode,itime,ncoadds,5,'integrated')
          Iwritten.append(readmode+itime+ncoadds+'integrated')
  else:
    sys.stderr.write('File not found: '+frame+'. Continuing with next file\n')

master=open(tdate+'_DoDarks.txt','w')

# finished with all files
outN.write('#FLUSH_DETECTOR\n#FLUSH_DETECTOR\n[END_OBSERVING_SETUP]\n')
outN.close()
if len(Nwritten):
  master.write('executeLUCIScript.sh '+tdate+'_darks_int.txt\n')
  sys.stderr.write(tdate+'_darks_int.txt\twritten.\n')
else:
  os.remove(tdate+'_darks_int.txt')
outI.write('#FLUSH_DETECTOR\nFLUSH_DETECTOR\n[END_OBSERVING_SETUP]\n')
outI.close()
if len(Iwritten):
  master.write('executeLUCIScript.sh '+tdate+'_darks_norm.txt\n')
  sys.stderr.write(tdate+'_darks_norm.txt\twritten.\n')
else:
  os.remove(tdate+'_darks_norm.txt')

master.close()

sys.stderr.write('Finished. Please inspect files, then run darks via:\n')
sys.stderr.write('sh '+tdate+'_DoDarks.txt\n\n')
