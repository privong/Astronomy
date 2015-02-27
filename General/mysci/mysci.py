# mysci.py
#
# Python module with some useful constants, values, and functions for data
# processing and import/export.
#
# George Privon

import sys as _sys
import os as _os
import re as _re
import string as _string
import numpy as _np
from astropy.io import fits as _pyfits
import astropy.units as _u
import astropy.io.votable as _vot
import cStringIO as _cStringIO
import pycurl as _pycurl

# Solar System Measurements, given as a dictionary
# mass - g, radius - cm, period - yr, semi-major axis - cm, eccentrcity
ssys = {'sun':   {'mass':1.99e33*_u.g,
                  'radius':6.96e10*_u.cm,
                  'period':0*_u.year,
                  'sma':0*_u.cm,
                  'e':0},
	'mercury':   {'mass': 3.303e26*_u.g,
                  'radius': 2.439e8*_u.cm,
                  'period': 2.4085e-1*_u.year,
                  'sma': 5.7909e12*_u.cm,
                  'e': 0.205622},
	'venus':     {'mass': 4.870e27*_u.g,
                  'radius': 6.050e8*_u.cm,
                  'period': 6.1521e-1*_u.year,
                  'sma': 1.0821e13*_u.cm,
                  'e': 0.006783},
	'earth':     {'mass': 5.976e27*_u.g,
                  'radius': 6.378e8*_u.cm,
                  'period': 1.00004e0*_u.year,
                  'sma': 1.4959e13*_u.cm,
                  'e': 0.016684},
	'mars':      {'mass': 6.418e26*_u.g,
                  'radius': 3.397e8*_u.cm,
                  'period': 1.88089e0*_u.year,
                  'sma': 2.2794e13*_u.cm,
                  'e': 0.093404},
	'jupiter':   {'mass': 1.899e30*_u.g,
                  'radius': 7.140e9*_u.cm,
                  'period': 1.18622e1*_u.year,
                  'sma': 7.7859e13*_u.cm,
                  'e': 0.047826},
	'saturn':    {'mass': 5.686e29*_u.g,
                  'radius': 6.000e9*_u.cm,
                  'period': 2.94577e1*_u.year,
                  'sma': 1.4324e14*_u.cm,
                  'e': 0.052754},
	'uranus':    {'mass': 8.66e28*_u.g,
                  'radius': 2.615e9*_u.cm,
                  'period': 8.40139e1*_u.year,
                  'sma': 2.8878e14*_u.cm,
                  'e': 0.050363},
	'neptune':   {'mass': 1.030e29*_u.g,
                  'radius': 2.43e9*_u.cm,
                  'period': 1.64793e2*_u.year,
                  'sma': 4.5188e14*_u.cm,
                  'e': 0.004014}}
# interesting stars (distances in cm)
stars = {'proximacentauri':  {'distance': 4.0143e18*_u.cm},	# wikipedia
         'barnardsstar':     {'distance': 5.6428e18*_u.cm},	# wikipedia
         'siriusA':          {'distance': 8.1219e18*_u.cm}}	# wikipedia

# Galaxy values (from https://secure.wikimedia.org/wikipedia/en/wiki/Milky_Way 16 Oct 2011)
R_MW = 4.62e22*_u.cm		# cm		Milky Way Radius
M_MW = 1.4e45*_u.g		# g		Milky Way Mass
# galcenter coordinates in (RA and Dec in J2000)
galcenter={'RA': 282.749599*_u.deg,
           'Dec': 27.46024*_u.deg,
           'galLon': 0.57596*_u.rad}

# Attractor locations (from Mould+ 2000 ApJ, 529, 786)
# Converted from B1950 to J2000
# parameters: RA-right ascencion
#       Dec - declination
#       vlgcl - attractor velocity corrected to local group
#       vfid - infall velocity to attractor, at local group position
#       radius - cluster angular radius
#       vmax - maximum heliocentric velocity of cluster core
#       vmin - minimum heliocentric velocity of cluster core
VirgoCluster = {'RA': 187.71186*_u.deg,
                'Dec': 12.39060*_u.deg,
                'vlgcl': 957.*_u.km/_u.s,
                'vfid': 200.*_u.km/_u.s,
                'radius': 0.17453*_u.rad,
                'vmin': 600*_u.km/_u.s,
                'vmax': 2300*_u.km/_u.s}
GreatAttractor={'RA': 200.73470*_u.deg,
                'Dec': -44.26105*_u.deg,
                'vlgcl': 4380*_u.km/_u.s,
                'vfid': 400.*_u.km/_u.s,
                'radius': 0.17453*_u.rad,
                'vmin': 2600*_u.km/_u.s,
                'vmax': 6600*_u.km/_u.s}
ShapleySupercluster={'RA': 203.20597*_u.deg,
                     'Dec': -31.25658*_u.deg,
                     'vlgcl': 13600*_u.km/_u.s,
                     'vfid': 85.*_u.km/_u.s,
                     'radius': 0.20944*_u.rad,
                     'vmin': 10000*_u.km/_u.s,
                     'vmax': 16000*_u.km/_u.s}

# Rest frequencies of astrophysically interesting (to me) lines
restfreq={'HI':1420405751.77*_u.Hz,
          'CO(1-0)':115271201800.*_u.Hz,
          '13CO(1-0)':110201.35400e6*_u.Hz,
          'C18O(1-0)':109782.17600e6*_u.Hz,
          'HCN(1-0)':88631.60100e6*_u.Hz,
          'HCO+(1-0)':89188.52600e6*_u.Hz,
          'HNC(1-0)':90.66356e9*_u.Hz,
          'CCH':87.325e9*_u.Hz}
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
        seg = seg.split(":")
    elif _re.search("h",seg):
        temp = seg.split("h")
        seg = []
        seg.append(temp[0])
        temp = temp[1].split('m')
        seg.append(temp[0])
        temp = temp[1].split('s')[0]
        seg.append(temp)
    elif _re.search("d",seg):
        temp = seg.split("d")
        seg = []
        seg.append(temp[0])
        temp = temp[1].split('m')
        seg.append(temp[0])
        temp = temp[1].split('s')[0]
        seg.append(temp)
    else:			# to cover whitespace separated values
        seg = seg.split()
    if float(seg[0]) == 0:
        if seg[0][0] == '-':
            sign = -1.0
        else:
            sign = 1.0
    else:
        sign = _np.sign(float(seg[0]))
    if sign < 0 and RA:
        _sys.stderr.write("Uh, RA has a negative value. That's weird. Returning nan.\n")
        return _np.nan
    if RA and float(seg[0]) > 24.:
        _sys.stderr.write("RA is greater than 24 hours. Are you sure you're passing the correct arguments?\n")
        return _np.nan
    deci = float(seg[0])+sign*(float(seg[1])/60.+float(seg[2])/3600.)    
    if RA:
        deci *= 15

    return deci*_u.deg

def DecimaltoSeg(deci,RA=False):
    """

    Convert deci to a segidecimal string. If RA=True, then it's also converted to
    hours:min:seconds. Otherwise it is left as degrees:arcminutes:arcseconds.

    """
    sign=int(_np.sign(deci))
    deci=deci/sign
    if RA:
        deci=deci/15.
    T1=int(_np.floor(deci))
    T2=int(_np.floor(60.*(deci-T1)))
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

def quadsum(values):
    """
    Take a list and return the quadrature sum of the elements.
    """
    tot=0.*values[0]**2
    for item in values:
        tot+=item**2
    return _np.sqrt(tot)

def angDist(pos1,pos2):
    """
    Calculate the angular distance between two points. Require decimal positions
    """
    numer=_np.sqrt((_np.cos(pos2[0])*_np.sin(_np.abs(pos1[1]-pos2[1])))**2+(_np.cos(pos1[0])*_np.sin(pos2[0])-_np.sin(pos1[0])*_np.cos(pos2[0])*_np.cos(_np.abs(pos1[1]-pos2[1])))**2)
    denom=_np.sin(pos1[0])*_np.sin(pos2[0])+_np.cos(pos1[0])*_np.cos(pos2[0])*_np.cos(_np.abs(pos1[1]-pos2[1]))
    return _np.arctan2(numer,denom)

def HImass(flux,DL):
    """
    HImass(flux,DL)

    Returns HI mass (in units of solar mass) with an input flux (Jy km/s) and a
    luminosity distance (Mpc). Units encouraged.
    """

    return (2.36e5*(DL/_u.Mpc)**2*flux/(_u.Jy*_u.km/_u.s)).decompose()*_u.MsolMass

# End Useful functions
###############################################################################

###############################################################################
# Scaper Functions

def simbadQuery(name):
    """
    simbadQuery(): Return information on a galaxy from a simbad query
    
    Arguments
    name: galaxy name
    
    Returns:
    dictionary with:
        - IRCS coordinates (J2000)
        - redshift
        - angular size
    """
    
    urlbase = "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=ASCII&Ident="
    out = {'RA': _np.nan*_u.deg,
           'Dec': _np.nan*_u.deg,
           'z': _np.nan,
           'angsize': {'major': _np.nan*_u.arcmin,
                       'minor': _np.nan*_u.arcmin,
                       'PA': _np.nan*_u.deg}}

    buf = _cStringIO.StringIO()
    c = _pycurl.Curl()
    c.setopt(c.URL, urlbase + name)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()
    results = buf.getvalue().split('\n')
    if _re.search('Identifier not found', results[0]):
        _sys.stderr.write(source + " not found in SIMBAD.")
    elif _re.search('No known catalog', results[0]):
        _sys.stderr.write(source + " catalog error.")
    else:
        for line in results:
            if _re.search('Identifiers', line):
                break
            elif _re.search('ICRS', line):
                line = line.split(':')[1].split(' (')[0].split()
                out['RA'] = line[0] + ':' + line[1] + ':' + line[2]
                out['Dec'] = line[3] + ':' + line[4] + ':' + line[5]
            elif _re.search('Redshift', line):
                out['z'] = _np.float(line.split(':')[1].split(' [')[0])
            elif _re.search('Angular size', line):
                pos = [float(x) for x in line.split(':')[1].split(' (')[0].split()]
                out['angsize']['major'] = pos[0] * _u.arcmin
                out['angsize']['minor'] = pos[1] * _u.arcmin
                out['angsize']['PA'] = pos[2] * _u.deg

    return out

# End scraper functions
###############################################################################

###############################################################################
# Catalog Functions

def PosMatch(pos1,pos2,name1=None,name2=None,posTol=60.*_u.arcsec):
    """
    Position matching function for catalogs. 

    Parameters:
        - pos1,pos2: positions, 2 element, Seg or decimal
        - name1,name2: tagged names (optional)
        - posTol: position tolerance (in arcsec if no units defined; default 60")

    Returns True if they match, False if not.
    """

    # homogenize positions
    if type(pos1[0]) is str or type(pos1[0]) is _np.string_:
        pos1[0]=SegtoDecimal(pos1[0],RA=True)
    elif not(type(pos1[0]) is _u.quantity.Quantity):
        pos1[0] *= _u.deg
    if type(pos1[1]) is str or type(pos1[1]) is _np.string_:
        pos1[1]=SegtoDecimal(pos1[1],RA=False)
    elif not(type(pos1[1]) is _u.quantity.Quantity):
        pos1[1] *= _u.deg
    if type(pos2[0]) is str or type(pos2[0]) is _np.string_:
        pos2[0]=SegtoDecimal(pos2[0],RA=True)
    elif not(type(pos2[0]) is _u.quantity.Quantity):
        pos2[0] *= _u.deg
    if type(pos2[1]) is str or type(pos2[1]) is _np.string_:
        pos2[1]=SegtoDecimal(pos2[1],RA=False)
    elif not(type(pos2[1]) is _u.quantity.Quantity):
        pos2[1] *= _u.deg

    # determine posTol character and homogenize
    if not(type(posTol) is _u.quantity.Quantity):
        _sys.stderr.write("WARNING: No units given for posTol, assuming arcsec.\n")
        posTol *= _u.arcsec

    if angDist(pos1,pos2) < posTol:
        return True
    else:
        return False    

    return -1

# End Catalog Functions
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
        ff=_np.concatenate((ext1,ext2),axis=1)

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
        ff=_np.concatenate((ext1,ext2),axis=0)
        for hdu in range(3,nHDU+1,1):
            extt=fitsopen(file,mode=mode,quiet=quiet,ext=hdu,trim=0)
            shape=extt.shape
            extt=extt.reshape((1,shape[0],shape[1]))
            ff=_np.concatenate((ff,extt),axis=0)
        return ff

# End Wrapper Functions
###############################################################################

################################################################################
# CSV functions

def CSVtoDict(infile,usecols=None,delimiter=',',haveunits=False, dtype=None,
              keycol=False):
    """
    Opens infile and converts it to a dictionary.

    Assumes the first non-skipped line has column titles. If haveunits is True,
    the second non-skipped line is assumed to have units.

    If keycol is not false, that column number is used as the key for the
    returned dictionary.

    """
    vals=_np.genfromtxt(infile, usecols=usecols, delimiter=delimiter,
                        dtype=dtype)
    key = []
    cols = []
    units = []
    infile = open(infile, 'r')
    count = 0
    for line in infile:
        if count == 0 and line[0] == '#':
            sline = line.split(delimiter)
            for a in usecols:
                cols.append(sline[a])
            count = 1
        elif haveunits and count == 1:
            sline = line.split(delimiter)
            for a in usecols:
                units.append(sline[a])
            count = 2
        elif (haveunits and count > 1) or (count > 0 and not(haveunits)) and \
             not(line[0] == '#'):
            line = line.split(delimiter)
            key.append(line[0])
    infile.close()
    out={}
    if keycol is False:     # first column of CSV file becomes the dict keys
        for i in range(len(key)):
            out[key[i]] = {}
            for j in range(len(cols)):
                out[key[i]][cols[j]] = vals[i][j]
    else:                   # use specified column as the dict key
        for i in range(len(key)):
            out[vals[i][keycol]] = {}
            for j in range(len(cols)):
                if j != keycol:
                    out[vals[i][keycol]][cols[j]] = vals[i][j]

    return out

# End CSV functions
################################################################################



################################################################################
# VOTable functions

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

def WriteSpecVOTMeas(outdict=None,outfile=None,**kwargs):
    """
    Take a dictionary and write it to a VOTable.

    Output VOTable will have a 'Source Information' table with top-level
    information, plus additional tables for each entry in the (required) 
    'measline' sub-dictionary.

    This function uses any astropy.units information from the first entry it
    comes across to set up units in the VOTable.

    Required Arguments:
        - outdict: dictionary to write
        - outfile: file to which to write

    Optional Arguments (via **kwargs):
        - author: Author Name
        - email: Author email
        - reference: Paper reference

    """

    if not(outdict) or not(outfile):
        _sys.stderr.write("WriteSpecVOTMeas Error: need to provide both the dictionary and the desired output file.\n")
        _sys.exit(-1)

    if not 'measline' in outdict[outdict.keys()[0]].keys():
        _sys.stderr.write("WriteSpecVOTMeas Warning: no 'measline' dictionary entry. Will be writing a single table.\n")
        havemeasline=False
    else:
        havemeasline=True

    newtable=_vot.tree.VOTableFile()
    resource=_vot.tree.Resource()
    newtable.resources.append(resource)

    if kwargs is None:
        # put in some generic header inforation
        kwargs['author']='privong/mysci.py'
        kwargs['email']='None'
        kwargs['reference']='None'

    #info=_vot.tree.Info()
    #newtable.infos.append(info)
    #for key in kwargs.keys():
    #    newtable.infos.extend([_vot.tree.Info(newtable,name=key,datatype='char',arraysize='*',value=(kwargs[key]))])

    # create a 'Source Information' table
    srcTab=_vot.tree.Table(newtable)
    srcTab.ID='Src'
    srcTab.name='Source Information'
    resource.tables.append(srcTab)
    srcTab.fields.extend([_vot.tree.Field(newtable,name="Source",datatype='char',arraysize='*',ID="Source")])
    srcTab.fields.extend([_vot.tree.Field(newtable,name="srcID",datatype="int")])
    for i in sorted(outdict[outdict.keys()[0]].keys()):
        if i!='measline':
            if type(outdict[outdict.keys()[0]][i]) is _u.quantity.Quantity:
                srcTab.fields.extend([_vot.tree.Field(newtable,name=i,
		datatype="float",
		unit=outdict[outdict.keys()[0]][i].unit)])
            elif type(outdict[outdict.keys()[0]][i]) is float:
                srcTab.fields.extend([_vot.tree.Field(newtable,name=i,
		datatype="float")])
            else:
                srcTab.fields.extend([_vot.tree.Field(newtable,name=i,
		datatype='char',
		arraysize='*')]) #ype(outdict[outdict.keys()[0]][i])))])
    srcTab.create_arrays(len(outdict.keys()))
    # create tables for the measurements
    measTab={}
    for i in sorted(outdict[outdict.keys()[0]]['measline'].keys()):
        measTab[i]=_vot.tree.Table(newtable)
        measTab[i].ID='line'+str(i)
        measTab[i].name=outdict[outdict.keys()[0]]['measline'][i]['lineID']
        resource.tables.append(measTab[i])
        measTab[i].fields.extend([_vot.tree.Field(newtable,name='srcID',datatype='int',ID='srcID')])
        for j in sorted(outdict[outdict.keys()[0]]['measline'][i].keys()):
            if type(outdict[outdict.keys()[0]]['measline'][i][j]) is _u.quantity.Quantity:
                measTab[i].fields.extend([_vot.tree.Field(newtable,name=j,
		datatype="float",
		unit=(outdict[outdict.keys()[0]]['measline'][i][j]).unit)])
            elif type(outdict[outdict.keys()[0]]['measline'][i][j]) is float:
                measTab[i].fields.extend([_vot.tree.Field(newtable,name=j,
		datatype="float")])
            else:
                measTab[i].fields.extend([_vot.tree.Field(newtable,name=j,
		datatype='char',
		arraysize='*')])
        measTab[i].create_arrays(len(outdict.keys()))

    srcID=0
    for src in sorted(outdict.keys()):
        srcinfo=(src,srcID)
        for key in sorted(outdict[src].keys()):
            if key=='measline':
                for line in sorted(measTab.keys()):
                    lineinfo=(srcID,)
                    for key2 in sorted(outdict[src]['measline'][line].keys()):
                        if type(outdict[src]['measline'][line][key2]) is _u.quantity.Quantity:
                            lineinfo=lineinfo+(outdict[src]['measline'][line][key2].value,)
                        else:
                            lineinfo=lineinfo+(outdict[src]['measline'][line][key2],)
                    measTab[line].array[srcID]=lineinfo
            else:
                if type(outdict[src][key]) is _u.quantity.Quantity:
                    srcinfo=srcinfo+(outdict[src][key].value,)
                else:
                    srcinfo=srcinfo+(outdict[src][key],)
        srcTab.array[srcID]=srcinfo
        srcID+=1

    newtable.to_xml(outfile)


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
