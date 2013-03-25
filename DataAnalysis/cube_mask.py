#!/usr/bin/python
#
# Generate a mask for a data cube

from astropy.io import fits
import sys,argparse,os
import numpy as np

parser=argparse.ArgumentParser(description='Create a mask for a data cube')
parser.add_argument('cube',type=str,default=False,help='Data cube to mask')
parser.add_argument('-rms',type=float,default=-1,help='RMS noise')
parser.add_argument('-SN',type=float,default=-1,help='SN to use for individual pixels (Default: -1, accept all pixels).')
parser.add_argument('-SNJ',type=float,default=-1,help='SN to use for pixels detected in >1 adjacent channels (Default: -1, option disabled).')
args=parser.parse_args()

if args.cube:
  print "Generating mask for "+args.cube+"."
else:
  sys.stderr.write("ERROR: You must specify a data cube.\n\n")
  sys.exit(-1)

if args.rms:
  print "Using RMS noise of "+str(args.rms)+" (in the units of the cube)."
else:
  sys.stderr.write("ERROR: You must specify a RMS noise value.\n\n")
  sys.stderr.write("Eventually I'll get around to allowing the program to compute this.\n\n")
  sys.exit(-1)

if args.SN==1:
  print "No SN specified, accepting all pixels."
if args.SNJ==-1:
  print "Not taking into account pixels adjacent in frequency space."

# let's get a move on
if os.path.isfile(args.cube):
  cube=fits.open(args.cube,mode='readonly')
else:
  sys.stderr.write("ERROR: "+args.cube+" not found.\n\n")
  sys.exit(-1)

# transpose so the definition is sensible
wdata=cube[0].data.transpose()*1

cshape=wdata.shape

if len(cshape)==4:
  # we have a velocity axis
  nchan=cshape[2]
  nstokes=cshape[3]
elif len(cshape)==3:
  # no velocity axis
  nstokes=cshape[2]
imsize=(cshape[0],cshape[1])

# simple mask for points which are above the SN threshold
masku=wdata*(wdata>args.rms*args.SN)
# do this for below the threshold too, we want to capture absorption
maskl=wdata*(wdata<-1*args.rms*args.SN)
mask=np.logical_or(masku,maskl)

adjmask=np.zeros((imsize[0],imsize[1],nchan,nstokes))

# now loop over the cube and look for adjacenent pixels
for v in range(0,nchan,2):	# double assign goodness
  for x in range(imsize[0]):
    for y in range(imsize[1]):
      if v!=(nchan-1):
        if (wdata[x,y,v,0]>args.rms*args.SNJ) and (wdata[x,y,v+1,0]>args.rms*args.SNJ):
          adjmask[x,y,v,0]=adjmask[x,y,v+1,0]=1
      else:
        # just do a left compare
        if (wdata[x,y,v,0]>args.rms*args.SNJ) and (wdata[x,y,v-1,0]>args.rms*args.SNJ):
          adjmask[x,y,v,0]=1

# combine the masks
fmask=np.ones((imsize[0],imsize[1],nchan,nstokes))*np.logical_or(mask,adjmask)

ofname=args.cube.split('.fits')[0]+'-masked.fits'
if os.path.isfile(ofname):
 os.remove(ofname)

cube[0].data=cube[0].data*fmask.transpose()
cube[0].header['comment']='Masked data cube.'
cube[0].header['comment']='SN='+str(args.SN)+' SNJ='+str(args.SNJ)+' RMS='+str(args.rms)

cube.writeto(ofname)

cube.close()
