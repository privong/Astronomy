#!/usr/bin/python

# hicomp.py
#
# generate a comparison set of histograms for original data with calibrated data
# or a comparison file

import numpy,pyfits,glob
import matplotlib.pyplot as plt

def hicomp(files,compfile=False,hrange=(0,65000),corrfac=1):

  # get the flie list
  files=glob.glob(files)
  if compfile:
    # load the compfile, compare *everything* to this
    frame=pyfits.open(compfile)
    comp=True
  else:
    comp=False
  # continue comparing stufffff
  j=0
  for file in files:
    plt.figure(j)
    plt.xlabel('Counts')
    plt.ylabel('Number')
    frame2=pyfits.open(file)
    if not(comp):
      frame=pyfits.open(file.split('.fits')[0]+'-bsub_flat.fits')
      plt.title(file+'-'+file.split('.fits')[0]+'-bsub_flat.fits')
    else:
      plt.title(file+'-'+compfile)
    for i in range(1,17):
      # uncorrected data
      (a,b,c)=plt.hist(numpy.ravel(frame2[i].data),100,range=hrange,alpha=0.3,color='red')
      # corrected data
      (a,b,c)=plt.hist(numpy.ravel(frame[i].data*corrfac),100,range=hrange,alpha=0.3,color='blue')
    frame2.close()
    if not(comp):
      frame.close()
    print "Saving figure "+str(j)
    plt.savefig(file.split('.fits')[0]+'.png',format='png')
    j=j+1
    #if i>2:
    #  break

  if comp:
    frame.close()
  #plt.show()
