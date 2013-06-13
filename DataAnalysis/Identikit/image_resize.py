#!/usr/bin/python
#
# Pad (optical) images to be paddedsizexpaddedsize so they don't limit the extent of the XY
# HI data cube projections

import pyfits,numpy,sys

frame=pyfits.open(sys.argv[1],ignore_missing_end=True)

(xsize,ysize)=frame[0].data.shape

paddedsize=(xsize+ysize)

nimg=numpy.zeros((paddedsize,paddedsize),dtype=frame[0].data.dtype)

nimg[paddedsize/2.-numpy.ceil(xsize/2.):paddedsize/2.+numpy.ceil(xsize/2.),paddedsize/2.-numpy.ceil(ysize/2.):paddedsize/2.+numpy.ceil(ysize/2.)]=frame[0].data

frame[0].data=nimg*1.

frame[0].header['CRPIX1']=paddedsize/2.-(ysize/2.-frame[0].header['CRPIX1'])
frame[0].header['CRPIX2']=paddedsize/2.-(xsize/2.-frame[0].header['CRPIX2'])

frame.writeto(sys.argv[1].split('.fits')[0]+'-padded.fits')

frame.close()
