#!/usr/bin/env python2
#
# list_file_types.py
#
# Given a list of FITS files, list the types for both processed and raw frames.

import astropy.io.fits as fits
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('fitsfiles', type=str, nargs='+',
                    help='FITS files to sort.')
args = parser.parse_args()

for entry in args.fitsfiles:
    myfits = fits.open(entry)
    try:
        curr = myfits[0].header['HIERARCH ESO PRO CATG']
        print(entry + "\tHIERARCH ESO PRO CATG: " + curr)
    except:
        curr = False

    try:
        curr = myfits[0].header['ESO DPR CATG']
        print(entry + "\tESO DPR CATG: " + curr + "\tESO DPR TYPE: " + myfits[0].header['ESO DPR TYPE'])
    except:
        curr = False

