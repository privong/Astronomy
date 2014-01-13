# mysci.py
#
# George's python module of useful scientific things.

import sys as _sys
import os as _os
import re as _re
import string as _string
import numpy as _numpy
from astropy.io import fits as _pyfits
import astropy.units as _u
import astropy.io.votable as _votable

# Solar System Measurements, given as a dictionary
# mass - g, radius - cm, period - yr, semi-major axis - cm, eccentrcity
ssys={'sun'	:{'mass':1.99e33*_u.g, 'radius':6.96e10*_u.cm, 'period':0*_u.year,'sma':0*_u.cm,'e':0},
	'mercury'	:{'mass': 3.303e26*_u.g,'radius': 2.439e8*_u.cm,'period': 2.4085e-1*_u.year,'sma': 5.7909e12*_u.cm,'e': 0.205622},
	'venus'		:{'mass': 4.870e27*_u.g,'radius': 6.050e8*_u.cm,'period': 6.1521e-1*_u.year,'sma': 1.0821e13*_u.cm,'e': 0.006783},
	'earth'		:{'mass': 5.976e27*_u.g,'radius': 6.378e8*_u.cm,'period': 1.00004e0*_u.year,'sma': 1.4959e13*_u.cm,'e': 0.016684},
	'mars'		:{'mass': 6.418e26*_u.g,'radius': 3.397e8*_u.cm,'period': 1.88089e0*_u.year,'sma': 2.2794e13*_u.cm,'e': 0.093404},
	'jupiter'	:{'mass': 1.899e30*_u.g,'radius': 7.140e9*_u.cm,'period': 1.18622e1*_u.year,'sma': 7.7859e13*_u.cm,'e': 0.047826},
	'saturn'	:{'mass': 5.686e29*_u.g,'radius': 6.000e9*_u.cm,'period': 2.94577e1*_u.year,'sma': 1.4324e14*_u.cm,'e': 0.052754},
	'uranus'	:{'mass': 8.66e28*_u.g, 'radius': 2.615e9*_u.cm,'period': 8.40139e1*_u.year,'sma': 2.8878e14*_u.cm,'e': 0.050363},
	'neptune'	:{'mass': 1.030e29*_u.g,'radius': 2.43e9*_u.cm, 'period': 1.64793e2*_u.year,'sma': 4.5188e14*_u.cm,'e': 0.004014}}
# interesting stars (distances in cm)
stars={'proximacentauri'	:{'distance':4.0143e18*_u.cm},	# wikipedia
	'barnardsstar'		:{'distance':5.6428e18*_u.cm},	# wikipedia
	'siriusA'		:{'distance':8.1219e18*_u.cm}}	# wikipedia

# Galaxy values (from https://secure.wikimedia.org/wikipedia/en/wiki/Milky_Way 16 Oct 2011)
R_MW	= 4.62e22*_u.cm		# cm		Milky Way Radius
M_MW	= 1.4e45*_u.g		# g		Milky Way Mass

# Rest frequencies of astrophysically interesting (to me) lines
restfreq={'HI'		:1420405751.77*_u.Hz,
	'CO(1-0)'	:115271201800.*_u.Hz,
	'13CO(1-0)'	:110201.35400e6*_u.Hz,
	'C18O(1-0)'	:109782.17600e6*_u.Hz,
	'HCN(1-0)'	:88631.60100e6*_u.Hz,
	'HCO+(1-0)'	:89188.52600e6*_u.Hz,
	'HNC(1-0)'	:90.66356e9*_u.Hz,
	'CCH'		:87.325e9*_u.Hz}
# End Astronomical Constants/Values
###############################################################################

###############################################################################
# Useful functions

# Wishlist:
# - Blackbody (Planck in both F_lam and F_nu; Wein's Law, Stefan-Boltzmann Law)
# - Jy/beam <-> K
# - Velocity system conversions (LSR, Bary/heliocentric)
# - Velocity definitions (optical, radio, relativistic)
# - pyfits import, transpose the data to RA,Dec,Spectral,[Stokes] (see http://www.cv.nrao.edu/~aleroy/pytut/topic2/intro_fits_files.py)

def SegtoDecimal(seg,RA=False):
  """
  Input a segidecimal angle (can't be hours!), return a decimal value
  
  seg is a string, with the values separated by a colon
  RA=False if it's an angle, RA=True if it's hours,mins,seconds

  """
  # split the string
  if _re.search(":",seg):
    seg=seg.split(":")
  elif _re.search("h",seg):
    temp=seg.split("h")
    seg=[]
    seg[0]=temp[0]
    temp=temp.split('m')
    seg[1]=temp[0]
    temp=temp.split('s')
    seg[2]=temp[0]
  else: 
    seg=seg.split()
  sign=np.sign(float(seg[0]))
  if sign<0 and RA:
    _sys.stderr.write("Uh, RA has a negative value. That's weird. Returning nan.n")
    return _numpy.nan
  if RA and seg[0]>24.:
    _sys.stderr.write("RA is greater than 24 hours. Sure you're passing the correct arguments?\n")
    return _numpy.nan
  deci=float(seg[0])+sign*(float(seg[1])/60.+float(seg[2])/60.)  
  if RA:
    deci*=15

  return deci

def DecimaltoSeg(deci,RA=False):
  """

  Convert deci to a segidecimal string. If RA=True, then it's also converted to
  hours:min:seconds. Otherwise it is left as degrees:arcminutes:arcseconds.

  """
  sign=int(np.sign(deci))
  deci=deci/sign
  if RA:
    deci=deci/15.
  T1=int(np.floor(deci))
  T2=int(np.floor(60.*(deci-T1)))
  T3=60*(60.*(deci-T1)-T2)
  seg=_string.join([str(sign*T1),str(T2),str(T3)],":")
  
  return seg

def RedshiftLine(z,restlam=None,restnu=None):
  """

  Computes the wavelength and/or frequency of a redshifted line.
  Requires the redshift (z) and one of restlam or restnu. Returns redshifted
  value.

  If neither are defined, the function returns nan.
  """
  if restlam:
    return restlam*(1.+z)
  if restnu:
    return restnu/(1.+z)
  else:
    _sys.stderr.write("Error: frequency not specified. Returning nan.\n")
    return nan

def fitsopen(file,mode='readonly',ext=0,trim=0,quiet=True):
  """

  Opens a fits file using pyfits (with an optional specification of the mode).
  This transposes the image to match sky convention.

  Returns a numpy array.

  ext specifies the FITS extension to use
  trim=0 won't trim the image according to the TRIMSEC keyword, 1 will.

  If quiet=True, no output is printed. If quiet is False, status messages are written
  to stdout.
  """

  # make sure the file exists
  if _os.path.isfile(file):
    frame=_pyfits.open(file,mode=mode)
    # we should really make sure we have enough extensions to open the one we
    # want, but i'll leave that for later. :)
    idata=frame[ext].data.transpose()
    if trim:
      trimsec=frame[ext].header['TRIMSEC'] #should really check this exists...
      # split it
      range=[int(s) for s in _re.findall(r'\d+',trimsec)]
      idata=idata[range[0]-1:range[1],range[2]-1:range[3]]
    frame.close()
  else:
    _sys.stderr.write('Error: '+file+' not found.')
    return -1

  if not(quiet):
    print file+" HDU("+str(ext)+") opened successfully with dimensions "+str(idata.shape)

  return idata
# End Useful functions
###############################################################################

###############################################################################
# Wrapper Functions
#
# Wrappers for various things. May require functions listed above

def Telload(file,Tel='none',mode='readonly',quiet=True):
  """

  Wrapper function for fitsopen(). Will load and appropriately arrange a fits
  file based on the specific telescope.

  Currently supported (Tel=)
    VATT (VATT 4k CCD)
  """

  if Tel=='none':
    _sys.stderr.write('No telescope specified, running fitsopen()\n')
    ff=fitsopen(file,mode=mode,quiet=quiet)
    return ff
  elif Tel=='VATT':
    if not(quiet):
      print "Loading FITS file for the VATT"
    # load both fits extensions (and re-transpose to put them in the orig format)
    # 2nd one needs to be flipped since it's reading out the other way
    ext1=fitsopen(file,mode=mode,quiet=quiet,ext=1,trim=1).transpose()
    ext2=np.fliplr(fitsopen(file,mode=mode,quiet=quiet,ext=2,trim=1).transpose())

    # concatenate the two halves of the image
    ff=np.concatenate((ext1,ext2),axis=1)

    return ff
  elif Tel=="90Prime":
    if not(quiet):
      print "Loading FITS file for the Bok 90Prime imager."
    # Bok 90Prime images have 17 HDU objects. 1 for the overall file and 1 for
    # each amplifier
    # stack these into a 3D array and return it? handle the calibration files
    # in the same way?

    # first, figure out how many HDUs there are...
    frame=_pyfits.open(file)
    nHDU=len(frame)-1 # ditch the overall HDU
    frame.close()
    # load the first frame to get us started
    ext1=fitsopen(file,mode=mode,quiet=quiet,ext=1,trim=0)
    shape=ext1.shape
    ext1=ext1.reshape((1,shape[0],shape[1]))
    ext2=fitsopen(file,mode=mode,quiet=quiet,ext=2,trim=0)
    shape=ext2.shape
    ext2=ext2.reshape((1,shape[0],shape[1]))
    ff=np.concatenate((ext1,ext2),axis=0)
    for hdu in range(3,nHDU+1,1):
      extt=fitsopen(file,mode=mode,quiet=quiet,ext=hdu,trim=0)
      shape=extt.shape
      extt=extt.reshape((1,shape[0],shape[1]))
      ff=np.concatenate((ff,extt),axis=0)
    return ff

# End Wrapper Functions
###############################################################################

################################################################################# VOTable functions

def VOtoDict(votab,printstruc=False):
  """

  When passed a votab object, return a dictionary with the votab.

  Arguments:
    - votab: parsed VOTable item
    - printstruc: if True, will print the structure of the resulting dictionary
	to stdout

  """

  dump={}
  i=j=0
  for resource in votab.resources:
    dump[j]={}
    for table in resource.tables:
      # parse away, me hearties!
      if table.name:
        dkey=table.name
      else:
        dkey=i
      i+=1
      dump[j][dkey]={}
      for entry in table.array:
        dump[j][dkey][entry[0]]={}
        for l in range(1,len(entry)):
          dump[j][dkey][entry[0]][table.fields[l].name]=entry[l]
          if table.fields[l].unit:
            dump[j][dkey][entry[0]][table.fields[l].name]*=table.fields[l].unit
    j+=1
  while len(dump.keys())==1:
    dump=dump[dump.keys()[0]]

  if printstruc:
    DictStruct(dump)

  return dump

# End VOTable parsing
################################################################################

################################################################################
# Specific VOTable tasks

def WriteSpecVOTMeas(outdict=None,outfile=None):
  """
  Take a dictionary and write it to a VOTable.

  Output VOTable will have a 'Source Information' table with top-level
  information, plus additional tables for each entry in the (required) 
  'measlines' sub-directory.

  This function uses any astropy.units information from the first entry it
  comes across to set up units in the VOTable.

  Arguments:
    - outdict: dictionary to write
    - outfile: file to which to write

  """

  if not(outdict) or not(outfile):
    _sys.stderr.write("WriteSpecVOTMeas Error: need to provide both the dictionary and the desired output file.\n")
    _sys.exit(-1)

  votable=_votable.tree.VOTableFile()
  resource=_votable.tree.Resource()

  # add in stuff from the custom-written script converting the IRAM measured
  # results.

# End Specific VOTable tasks
################################################################################


################################################################################
# Convenience functions

def DictStruct(d,depth=0,Print=True):
  """

  Print the structure of a dictionary.

  Arguments:
    - d:	dictionary in question
    - depth:	don't touch this :)
    - Print:	If True, structure will be printed via stdout. If False, nothing
		happens, so why did you bother to run this? :)

  """

  if type(d)==dict:
    if depth==0:
      if Print: _sys.stdout.write("Dictionary has the following key structure:\n")
    for key in d.keys():
      for i in range(depth):
        if depth>0 and i==depth-1:
          if Print: _sys.stdout.write("|")
        else:
          if Print: _sys.stdout.write(" ")
      if Print: _sys.stdout.write(str(key)+"\n")
      DictStruct(d[key],depth=depth+1,Print=Print)

# End Convenience functions
################################################################################
