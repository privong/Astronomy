#!/usr/bin/env python2
#
# Sort and classify MUSE files.

import astropy.io.fits as fits
import sys
import re
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-p','--processed', type=bool, default=False,
                    help='Invoke if using pre-processed calibrations.')
parser.add_argument('fitsfiles', type=str, nargs='+',
                    help='FITS files to sort.')
args = parser.parse_args()

sys.stdout.write('Sorting ' + str(len(args.fitsfiles)) + ' FITS files.\n')

if args.processed:
    sys.stdout.write('Assuming files contain processed calibrations.\n')
    # frames needed for science post-processing
    files = [
#             'ASTROMETRY_REFERENCE',
             'ASTROMETRY_WCS',
             'BADPIX_TABLE',
             'EXTINCT_TABLE',
             'FILTER_LIST',
             'GEOMETRY_TABLE',
             'LSF_PROFILE',
             'MASTER_BIAS',
             'MASTER_FLAT',
             'STD_RESPONSE',
             'STD_TELLURIC',
             'STD_FLUX_TABLE',
             'STD_RESPONSE',
             'STD_TELLURIC',
             'TRACE_TABLE',
             'TWILIGHT_CUBE',
             'WAVECAL_TABLE']
    # frames needed for preprocessing
    preproc = ['GEOMETRY_TABLE',
               'BADPIX_TABLE',
               'MASTER_BIAS',
               'MASTER_FLAT',
               'TRACE_TABLE',
               'WAVECAL_TABLE']
    # frames needed to create a sky frame
    skyf = ['EXTINCT_TABLE',
            'STD_RESPONSE',
            'SKY_LINES',
            'LSF_PROFILE',
            'STD_TELLURIC']

    objp = open('object-pre.sof', 'w')
    spost = open('scipost.sof', 'w')
    sky = open('sky.sof', 'w')
    skyp = open('sky-pre.sof', 'w')

    for entry in args.fitsfiles:
        myfits = fits.open(entry)
        try:
            curr = myfits[0].header['HIERARCH ESO PRO CATG']
            if curr in skyf:
                sky.write(entry + ' ' + curr + '\n')
            elif curr in preproc:
                skyp.write(entry + ' ' + curr + '\n')
                objp.write(entry + ' ' + curr + '\n')
            elif curr in files:
                spost.write(entry + ' ' + curr + '\n')
        except:
            sys.stdout.write('Trying non-processed type.\n')
            try:
    
                curr = myfits[0].header['ESO DPR TYPE']
                if curr == 'SCIENCE':
                    if myfits[0].header['ESO DPR TYPE'] == 'SKY':
                        sky.write(entry + ' SKY\n')
                    elif myfits[0].header['ESO DPR TYPE'] == 'OBJECT':
                        spost.write(entry + ' OBJECT\n')
            except:
                sys.stdout.write('Unknown file type.\n')
    objp.close()
    spost.close()
    sky.close()
    skyp.close()

    sys.stdout.write('Finished writing files. Now, pre-process sky \
and object frames with the following commands:\n\n')
    sys.stdout.write('OMP_NUM_THREADS=4 esorex --log-file=sky-pre.log muse_scibasic --nifu=-1 --merge sky-pre.sof\n\n')
    sys.stdout.write('OMP_NUM_THREADS=4 esorex --log-file=object-pre.log muse_scibasic --nifu=-1 --merge object-pre.sof\n\n')
    sys.stdout.write('Then add the PIXTABLE_SKY files to the sky.sof file and run:\n\n')
    sys.stdout.write('OMP_NUM_THREADS=4 esorex --log-file=makesky.log muse_create_sky sky.osf\n\n')
    sys.stdout.write('Finally add the PIXTABLE_OBJECT files to scipost.sof and run:\n\n')
    sys.stdout.write('OMP_NUM_THREADS=4 --log=scipost.log muse_scipost scipost.sof\n\n')

else:
    sys.stdout.write('Cataloging files using raw calibration frames.\n')

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
        if 'ESO DPR CATG' in list(myfits[0].header.keys()) and \
           'ESO DPR TYPE' in list(myfits[0].header.keys()):
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
