#!/usr/bin/python
#
# opt_red.py
#
# Batch optical reduction for a single night of data
#
# To do:
# - allow user to specify telescope on the command line
# - Enable selection of which flat fields you should use to make the master flat

import pyfits
import numpy
import sys,os,re,glob,getopt,datetime
import matplotlib.pyplot as plt
import mysci

# keywords to move from original files to the derived calibration files
kprop=['DETSIZE','CCDSUM','TIMESYS','OBJECT','DATE-OBS','DARKTIME','TIMEZONE','IMAGETYP','INSTRUME','DEWTEMP','LST-OBS','OBSERVER','JULIAN','OBSERVAT','EPOCH','CAMTEMP','UT','TIME-OBS','ST','EXPTIME']

def usage():
  sys.stderr.write('Usage:\n')
  sys.stderr.write(sys.argv[0]+' [OPTIONS] filelist\n\n')
  sys.stderr.write('Acceptable options are:\n')
  sys.stderr.write('== no additional options currently available==\n\n')

################################################################################
# Start script
################################################################################
# check number of arguments
if len(sys.argv)<2:
  sys.stderr.write('\nERROR: insufficient command line arguments.\n\n')
  usage()
  sys.exit(-1)

# get arguments
try:
  optlist=getopt.getopt(sys.argv[1:],'x',['itime=','object=','readmode=','filter='])
except getopt.GetoptError, err:
  sys.stderr.write(str(err))
  usage()
  sys.exit(-1)

# start parsing through the list of arguments
optlist=list(optlist)
files=optlist.pop()

# initialize some lists
darks=[]	# list of dark frames
bias=[]		# list of bias frames
filters=[]	# list of filters used
flats=[]	# flat frames (will be a 2D array, file ID and filter ID)
objects=[]	# object frames (2D array, as above)

# identify the files
for file1 in files:
  file1=glob.glob(file1)
  for file in file1:
    if os.path.isfile(file):
      frame=pyfits.open(file)
      thisfil=0
      if re.match('zero',frame[0].header["IMAGETYP"]):
        bias.append(file)
      elif re.match('dark',frame[0].header["IMAGETYP"]):
        darks.append(file)
      elif re.match('object',frame[0].header["IMAGETYP"]) and not(re.match('Focus',frame[0].header["OBJECT"])):
        # get the filter name
        thisfil=frame[0].header["FILTER"]
        if not(thisfil in filters):
          # filter isn't in our list, add it!
          filters.append(thisfil)
        objects.append((file,thisfil))
      elif re.match('flat',frame[0].header["IMAGETYP"]):
        thisfil=frame[0].header["FILTER"]
        if not(thisfil in filters):
          # filter isn't in our list, add it!
          filters.append(thisfil)
        flats.append((file,thisfil))
      else:
        sys.stderr.write(file+' - unknown image type, ignoring.\n')
      frame.close()
# print out some info
sys.stderr.write(str(len(file1))+' files inspected.\n')
sys.stderr.write(str(len(darks))+' dark frames found. ')
sys.stderr.write(str(len(bias))+' bias frames found. ')
sys.stderr.write(str(len(flats))+' flat frames found.\n')
sys.stderr.write(str(len(objects))+' object frames with '+str(len(filters))+' filters identified (')
for i in filters:
  sys.stderr.write(i+' ')
sys.stderr.write(')\n\n')

## make a master bias
mean=[]
median=[]
stddev=[]
bframes=numpy.array([0])
sys.stderr.write('Creating a master bias file\n')
sys.stderr.write('Loading bias frames')
for image in bias:
  # need to un-fix this later when more telescopes are added
  idata=mysci.Telload(image,Tel='VATT',quiet=True)
  if bframes.ndim<2:
    bframes.resize(idata.shape)
    bframes=idata.copy()
  else:
    bframes=numpy.dstack((bframes,idata))
  stddev.append(numpy.std(idata))
  mean.append(numpy.mean(idata))
  median.append(numpy.median(idata))
  sys.stderr.write('.')

sys.stderr.write('\n')
sys.stderr.write('Loaded '+str(len(mean))+' bias frames.\n')
# plot diagonstics
fig=plt.figure()
plt.scatter(range(len(mean)),mean)
plt.scatter(range(len(median)),median)
plt.scatter(range(len(stddev)),stddev)
plt.show()


# right now take all the frames, we'll deal with dropping frames later
mbias=numpy.mean(bframes,axis=2)

# get the date
datenow=datetime.datetime.today().isoformat()

# copy the header from an existing bias frame, add comments saying which
# bias frames were combined and how they were combined.
hdu=pyfits.PrimaryHDU(mbias)
sbias=pyfits.open(image)
# copy over the keywords we want
for kw in kprop:
  if sbias[0].header.has_key(kw):
    hdu.header.update(kw,sbias[0].header[kw])
# add header comments
hdu.header['IMAGETYP']='masterbias'
hdu.header.add_history(datenow+' - Masterbias created')
hdu.header.add_comment('Master bias created from mean of: '+str(bias))
if os.path.isfile('masterbias.fits'):
  sys.stderr.write('Deleting existing masterbias.fits\n')
  raw_input('PRESS ENTER TO CONTINUE')
  os.remove('masterbias.fits')
hdu.writeto('masterbias.fits')

sys.stderr.write('\n')

# delete variables we no longer need
del bframes

sys.stderr.write('\n\n\nNOTE: We are ignoring dark frames at the moment!!!!!\n\n\n')

## See if there are any dark frames, make a master dark.
"""
if len(darks)>0:
  # we have darks!
  mean=[]
  median=[]
  stddev=[]
  dframes=numpy.array([0])
  sys.stderr.write('Creating a master dark frame\n')
  sys.stderr.write('Loading dark frames')
  for image in darks:
    if bframes.ndim<2:
      bframes.resize(idata.shape)
      bframes=idata-mbias	# do bias subtraction as soon as we load the file
    else:
      bframes=numpy.dstack((bframes,idata-mbias)) # bias subtraction included

    # get the exposure time for the dark frame, add it to a list
    # we'll use this to make sure we're only combining appropriate dark frames
    # (not yet implemented)


    stddev.append(numpy.std(idata))
    mean.append(numpy.mean(idata))
    median.append(numpy.median(idata))
    sys.stderr.write('.')

  sys.stderr.write('\n')
  sys.stderr.write('Loaded '+str(len(mean))+' dark frames.\n')


  
else:
  sys.stderr.write('No dark frames found.. not creating a master dark.\n\n')
"""

mflats=numpy.array([0])
## Create a master flat
# first load all the flat files (and normalize them), then loop over filters
sys.stderr.write('Creating master flats.\n')
for filter in filters:
  sys.stderr.write(filter)
  fframes=numpy.array([0])
  stddev=[]
  # we've selected a filter, now loop over files
  for image in flats:
    if re.match(filter,image[1]):
      # yay, it's a filter we want, load it up
      sys.stderr.write('.')
      idata=mysci.Telload(image[0],Tel='VATT',quiet=True)
      if fframes.ndim<2:
        fframes.resize(idata.shape)
        fframes=idata/numpy.median(idata)
      else:
        fframes=numpy.dstack((fframes,idata/numpy.median(idata)))
      stddev.append(numpy.std(idata/numpy.mean(idata)))
  sys.stderr.write('\n')
  # we've loaded all the flats for that particular filter, now make a master
  mflat=numpy.median(fframes,axis=2)
  if mflats.ndim<2:
    mflats.resize(mflat.shape)
    mflats=mflat*1.0
  else:
    mflats=numpy.dstack(mflats,mflat)
  hdu=pyfits.PrimaryHDU(mflat)
  sflat=pyfits.open(image[0])
  # copy over the keywords we want
  for kw in kprop:
    if sflat[0].header.has_key(kw):
      hdu.header.update(kw,sflat[0].header[kw])
  # change the header keyword to masterflat
  hdu.header['IMAGETYP']='masterflat'
  # add header comments
  hdu.header.add_history(datenow+' - Master Flat created')
  sflat.close()
  sys.stderr.write('\tsaving master flat as: ')
  mfname=filter+'_masterflat.fits'
  sys.stderr.write(mfname+'\n')
  if os.path.isfile(mfname):
    sys.stderr.write('Deleting existing '+mfname+'\n')
    raw_input('PRESS ENTER TO CONTINUE')
    os.remove(mfname)
  hdu.writeto(mfname)

del fframes

## now process the individual object frames, going by filter
sys.stderr.write('\n\nProcessing object frames (bias and flat)\n')
i=0
for filter in filters:
  sys.stderr.write('Filter: '+filter)
  for image in objects:
    if re.match(filter,image[1]):
      # filter for object matches what we're trying
      idata=mysci.Telload(image[0],Tel='VATT',quiet=True)
      datenow=datetime.datetime.today().isoformat()
      # bias subtract
      idata=idata-mbias
      # flat field
      idata=idata/mflats
      rootn=re.split('.fits',image[0])[0]
      fname=rootn+'-bsub_flat.fits'
      sys.stderr.write('\tCalibrated: '+image[0]+'. Writing as '+fname+'.\n')
      hdu=pyfits.PrimaryHDU(idata)
      sobj=pyfits.open(image[0])
      for kw in kprop:
        if sobj[0].header.has_key(kw):
          hdu.header.update(kw,sobj[0].header[kw])
      hdu.header.add_history(datenow+' - Bias and flat field corrected')
      sobj.close()
      if os.path.isfile(fname):
        sys.stderr.write('Deleting existing '+fname+'\n')
        raw_input('PRESS ENTER TO CONTINUE')
        os.remove(fname)
      hdu.writeto(fname)
  i=i+1

