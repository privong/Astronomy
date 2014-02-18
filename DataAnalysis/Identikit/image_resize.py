#!/usr/bin/env python
#
# Pad (optical) images to be paddedsizexpaddedsize so they don't limit the 
# extent of the XY HI data cube projections
#
# Should be run from within CASA, since it needs access to CASA image formats

import pyfits,numpy,sys

def image_match(img,refimg=None,oimg=None):
  """
  Pad and/or crop an image to match the angular coverage of a reference image.

  Arguments:
    img		- Image to be modified
    refimg	- Reference image to match
    oimg	- Output image

  Notes:
    - Script assumes input and reference images have the same orientation and
	that they have no rotation.
  """
  if not(refimg):
    sys.stdout.write("No reference image specified. Can't do much with this.\n")
    return -1

