#!/usr/bin/env python

import numpy as np
import astropy.io.fits as pyfits
import astropy.coordinates as coords
import argparse,sys,os

parser=argparse.ArgumentParser(description="Load a fits image and a reference image. Resize the image to match the angular extent of the reference image.")
parser.add_argument('refimg',action='store',type=str,default=False,help='Reference figure.')
arser.add_argument('img',action='store',type=str,default=False,help='Figure to be modified.')
args=parser.parse_args()

if not(args.refimg and args.img):
  sys.stderr.write("Error, you must specify a reference image and an image to be processed.\n")
  sys.exit(-1)

if os.path.isfile(args.refimg):
  ref=pyfits.open(args.refimg)
else:
  sys.stderr.write(args.refimg+" doesn't seem to be a file. Exiting.\n")
  sys.exit(-2)
if os.path.isfile(args.img):
  img=pyfits.open(args.img)
else:
  sys.stderr.write(args.img+" doesn't seem to be a file. Exiting.\n")
  sys.exit(-2)

# under the assumption that the reference image is the one to be matched,
# modify the second image (by padding and/or cropping) to match the angular
# size
