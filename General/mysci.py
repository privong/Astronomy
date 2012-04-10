# mysci.py
#
# George's python module of useful scientific things.
#
# Last Modified: 08 February 2012 by George C. Privon
# gcp8y@virginia.edu
#

import sys,pyfits,numpy,os,re

###############################################################################
# CGS constants
# from http://www.astro.wisc.edu/~dolan/constants.html
# Retreived: 16 October 2011
c	= 2.99792458e10		# cm s^-1		Speed of Light
h	= 6.6260755e-27		# erg s			Planck Constant
hbar	= 1.05457266e-27	# erg s			/2pi
G	= 6.67259e-8		# cm^3 g^-1 s^-2	Grav constant
e	= 4.8032068e-10		# esu			electron charge
eV	= 1.6021772e-12		# erg			Electron Volt
m_e	= 9.1093897e-28		# g			electron mass
m_p	= 1.6726231e-24		# g			proton mass
m_n	= 1.6749286e-24		# g			neutron mass
amu	= 1.6605402e-24		# g			atomic mass unit
N_A	= 6.0221367e23		# -			Avagadro's Number
k	= 1.380658e-16		# erg K^-1		Boltzmann Constant
a	= 7.5646e-15		# erg cm^-3 K^-4	Radiation density const
sigma	= 5.67051e-5		# erg cm^-2 K^-4 s^-1	Stefan-Boltzmann const
alpha	= 7.29735308e-3		# -			Fine Structure const
rhyd	= 2.1798741e-11		# erg			Rhydberg const

# End CGS constants
###############################################################################

###############################################################################
# Astronomical Constants
# from http://www.astro.wisc.edu/~dolan/constants.html
# Retreived: 16 October 2011
AU	= 1.496e13		# cm			Astronomical Unit
pc	= 3.086e18		# cm			Parsec
ly	= 9.463e17		# cm			Light-year
M_sun	= 1.99e33		# g			Solar Mass
R_sun   = 6.96e10		# cm			Solar Radius
L_sun	= 3.9e33		# erg s^-1		Solar Luminosity
T_sun	= 5.789e3		# K			Solar Temperature (surf)
# Solar System Measurements, given as a dictionary
# mass - g, radius - cm, period - yr, semi-major axis - cm, eccentrcity
ssys={'sun'	:{'mass':1.99e33, 'radius':6.96e10, 'period':0,'sma':0,'e':0},
	'mercury'	:{'mass': 3.303e26,'radius': 2.439e8,'period': 2.4085e-1,'sma': 5.7909e12,'e': 0.205622},
	'venus'		:{'mass': 4.870e27,'radius': 6.050e8,'period': 6.1521e-1,'sma': 1.0821e13,'e': 0.006783},
	'earth'		:{'mass': 5.976e27,'radius': 6.378e8,'period': 1.00004e0,'sma': 1.4959e13,'e': 0.016684},
	'mars'		:{'mass': 6.418e26,'radius': 3.397e8,'period': 1.88089e0,'sma': 2.2794e13,'e': 0.093404},
	'jupiter'	:{'mass': 1.899e30,'radius': 7.140e9,'period': 1.18622e1,'sma': 7.7859e13,'e': 0.047826},
	'saturn'	:{'mass': 5.686e29,'radius': 6.000e9,'period': 2.94577e1,'sma': 1.4324e14,'e': 0.052754},
	'uranus'	:{'mass': 8.66e28, 'radius': 2.615e9,'period': 8.40139e1,'sma': 2.8878e14,'e': 0.050363},
	'neptune'	:{'mass': 1.030e29,'radius': 2.43e9, 'period': 1.64793e2,'sma': 4.5188e14,'e': 0.004014}}
# interesting stars (distances in cm)
stars={'proximacentauri'	:{'distance':4.0143e18},	# wikipedia
	'barnardsstar'		:{'distance':5.6428e18},	# wikipedia
	'siriusA'		:{'distance':8.1219e18}}	# wikipedia

# Galaxy values (from https://secure.wikimedia.org/wikipedia/en/wiki/Milky_Way 16 Oct 2011)
R_MW	= 4.62e22		# cm		Milky Way Radius
M_MW	= 1.4e45		# g		Milky Way Mass

# Universe Values
t_U	= 4.342e17		# s		Age of the Universe (13.76 Gyr)
T_CMB	= 2.73			# K		CMB temperature at z=0

# Rest frequencies of astrophysically interesting lines (in Hz)
restfreq={'HI'	:1420405751.77,
	'CO'	:115271201800.,
	'13CO'	:110201.35400e6,
	'C18O'	:109782.17600e6,
	'HCN'	:88631.60100e6,
	'HCO+'	:89188.52600e6}
# End Astronomical Constants/Values
###############################################################################

###############################################################################
# Useful functions

# Wishlist:
# - Blackbody (Planck in both F_lam and F_nu; Wein's Law, Stefan-Boltzmann Law)
# - angle conversions (arcsec to degrees to radians, H:M:S to decimal degrees and the reverse)
# - Jy/beam <-> K
# - Velocity system conversions (LSR, Bary/heliocentric)
# - Velocity definitions (optical, radio, relativistic)
# - pyfits import, transpose the data to RA,Dec,Spectral,[Stokes] (see http://www.cv.nrao.edu/~aleroy/pytut/topic2/intro_fits_files.py)

def segtodecimal(seg,RA=0):
  """
  Input a segidecimal angle (can't be hours!), return a decimal value
  
  seg is a string, with the values separated by a colon
  RA is 0 if it's an angle, RA=1 if it's hours,mins,seconds
  """
  print "Coming soon...."
  # split the string

  # compute the angle
  return dec 

def decimaltoseg(deci,RA=0):
  """

  Convert deci to a segidecimal string. If RA=1, then it's also converted to
  hours:min:seconds. Otherwise it is left as degrees:arcminutes:arcseconds.
  """
  
  return seg

def redshift_line(z,restlam=-1,restnu=-1):
  """

  Computes the wavelength and/or frequency of a redshifted line.
  Requires the redshift (z) and one of restlam or restnu. Returns redshifted
  value.

  If neither are defined, the function returns -1.
  """
  if restlam>0:
    return restlam*(1.+z)
  if restnu>0:
    return restnu/(1.+z)
  else:
    return -1

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
  if os.path.isfile(file):
    frame=pyfits.open(file,mode=mode)
    # we should really make sure we have enough extensions to open the one we
    # want, but i'll leave that for later. :)
    idata=frame[ext].data.transpose()
    if trim:
      trimsec=frame[ext].header['TRIMSEC'] #should really check this exists...
      # split it
      range=[int(s) for s in re.findall(r'\d+',trimsec)]
      idata=idata[range[0]-1:range[1],range[2]-1:range[3]]
    frame.close()
  else:
    sys.stderr.write('Error: '+file+' not found.')
    return -1

  if not(quiet):
    print file+" opened successfully with dimensions "+str(idata.shape)

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
    sys.stderr.write('No telescope specified, running fitsopen()\n')
    ff=fitsopen(file,mode=mode,quiet=quiet)
    return ff
  elif Tel=='VATT':
    if not(quiet):
      print "Loading FITS file for the VATT"
    # load both fits extensions (and re-transpose to put them in the orig format)
    # 2nd one needs to be flipped since it's reading out the other way
    ext1=fitsopen(file,mode=mode,quiet=quiet,ext=1,trim=1).transpose()
    ext2=numpy.fliplr(fitsopen(file,mode=mode,quiet=quiet,ext=2,trim=1).transpose())

    # concatenate the two halves of the image
    ff=numpy.concatenate((ext1,ext2),axis=1)

    return ff


# End Wrapper Functions
###############################################################################
