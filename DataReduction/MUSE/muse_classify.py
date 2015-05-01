#!/usr/bin/env python2
#
# Sort and classify MUSE files.

import astropy.io.fits as fits
import sys
import re
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('fitsfiles', type=str, nargs='+',
                    help='FITS files to sort.')
args = parser.parse_args()

sys.stdout.write('Sorting ' + str(len(args.fitsfiles)) + ' FITS files.\n')

bias = open('bias.sof', 'w')
dark = open('dark.sof', 'w')
flat = open('flat.sof', 'w')
skyflat = open('skyflat.sof', 'w')
wave = open('wave.sof', 'w')
lsf = open('lsf.sof', 'w')
mask = open('mask.sof', 'w')
std = open('std.sof', 'w')
astro = open('astrometry.sof', 'w')
sky = open('sky.sof', 'w')
obj = open('object.sof', 'w')
illum = open('illum.sof', 'w')

for entry in args.fitsfiles:
    myfits = fits.open(entry)
    if 'ESO DPR CATG' in myfits[0].header.keys() and \
       'ESO DPR TYPE' in myfits[0].header.keys():
        if re.search('CALIB', myfits[0].header['ESO DPR CATG']):
            if re.search('BIAS', myfits[0].header['ESO DPR TYPE']):
                bias.write(entry + ' BIAS\n')
            elif re.search('DARK', myfits[0].header['ESO DPR TYPE']):
                dark.write(entry + ' DARK\n')
            elif re.search('FLAT,LAMP',myfits[0].header['ESO DPR TYPE']):
                flat.write(entry + ' FLAT\n')
            elif re.search('FLAT,SKY', myfits[0].header['ESO DPR TYPE']):
                skyflat.write(entry + ' SKYFLAT\n')
            elif re.search('WAVE', myfits[0].header['ESO DPR TYPE']):
                wave.write(entry + ' ARC\n')
                lsf.write(entry + ' ARC\n')
            elif re.search('WAVE,MASK', myfits[0].header['ESO DPR TYPE']):
                mask.write(entry + ' WAVE,MASK\n')
            elif re.search('STD', myfits[0].header['ESO DPR TYPE']):
                std.write(entry + ' STD\n')
            elif re.search('ASTROMETRY', myfits[0].header['ESO DPR TYPE']):
                astro.write(entry + ' ASTROMETRY\n')
            elif re.search('FLAT,LAMP,ILLUM', myfits[0].header['ESO DPR TYPE']):
                illum.write(entry + ' FLAT,LAMP,ILLUM\n')
            else:
                sys.stderr.write(entry + ' not recognized as a calib file.\n')
        elif myfits[0].header['ESO DPR CATG'] == 'SCIENCE':
            if myfits[0].header['ESO DPR TYPE'] == 'SKY':
                sky.write(entry + ' SKY\n')
            elif myfits[0].header['ESO DPR TYPE'] == 'OBJECT':
                obj.write(entry + ' OBJECT\n')
            else:
                sys.stderr.write(entry + ' not recognized as a science file.\n')

bias.close()
dark.close()
flat.close()
skyflat.close()
wave.close()
lsf.close()
mask.close()
std.close()
astro.close()
sky.close()
obj.close()
illum.close()
