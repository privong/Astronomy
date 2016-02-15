#!/usr/bin/env python2
#
# opt_red.py
#
# Batch optical reduction for a single night of data
#
# To do:
# - allow user to specify telescope on the command line
# - Enable selection of which flat fields be used to make the master flat

from astropy.io import fits as pyfits
import numpy as np
import sys
import os
import re
import glob
import shutil
import datetime
import matplotlib.pyplot as plt
import mysci
import argparse


def imageCombine(imgnames, frametype, verbose=False):
    """
    Take a list of images, perform a specified combination operation and
    return the final image. Optionally provide diagnostic feedback.
    """
    
    mean = []
    median = []
    stddev = []
    cframes = np.array([0])
    for image in imgnames:
        idata = mysci.Telload(image, Tel=args.telescope,
                              quiet=not(args.verbose))
        if cframes.ndim < 2:
            cframes = idata.copy()
        else:
            cframes = np.dstack((cframes, idata))
        stddev.append(np.std(idata))

        mean.append(np.mean(idata))
        median.append(np.median(idata))
        if args.verbose:
            sys.stderr.write('\nMean: ' + str(np.mean(idata)) +
                             '\tMedian: ' + str(np.median(idata)) +
                             '\tstddev: '+str(np.std(idata)))
            sys.stderr.write('.\n')

    sys.stderr.write('\n')
    sys.stderr.write('Loaded ' + str(len(mean)) + ' ' + frametype + ' frames.\n')
    if verbose:
        # plot diagonstics
        fig = plt.figure()
        # plt.scatter(range(len(mean)),mean,color='red',label='Mean')
        plt.scatter(range(len(median)), median, color='blue', label='Median')
        plt.scatter(range(len(stddev)), stddev, color='green', label='Stddev')
        plt.legend()
        plt.show()
    # right now take all the frames, need to add selective frame-ignoring
    mframe = np.mean(cframes, axis=2)
    if args.verbose:
        sys.stderr.write(str(cframes.shape) + '\n')
        sys.stderr.write(str(mframe.shape) + '\n')

    datenow = datetime.datetime.today().isoformat()

    # if we're dealing with a single fits extension, create a new file
    fname = 'master' + frametype + '.fits'
    if os.path.isfile(fname):
        sys.stderr.write('Deleting existing ' + fname + '\n')
        raw_input('PRESS ENTER TO CONTINUE')
        os.remove(fname)
    if len(mframe.shape) < 3:
        # copy header from an existing frame, add comments saying which
        # frames were combined and how they were combined.
        frame = pyfits.PrimaryHDU(np.transpose(mframe))
        sframe = pyfits.open(image)
        # copy over the keywords we want
        for kw in kprop:
            if kw in sframe[0].header:
                frame.header.set(kw, sframe[0].header[kw])
        # add reduction info to header
        frame.header['IMAGETYP'] = fname.split('.fits')[0]
        frame.header.add_history(datenow + ' - master ' + frametype + ' created')
        frame.header.add_comment('Master ' + frametype + ' created from mean of: ' +
                                 str(imgnames))
        frame.writeto(fname)
    else:
        # we need to insert this new data into a copy of the old fits file
        shutil.copy(image, fname)
        frame = pyfits.open(fname, mode='update')
        frame[0].header['IMAGETYP'] = fname.split('.fits')[0]
        frame[0].header.add_history(datenow + ' - master ' + frametype + ' created')
        frame[0].header.add_comment('Master ' + frametype + ' created from mean of: ' +
                                    str(imgnames))
        for hdu in range(1, len(frame)):
            if verbose:
                sys.stderr.write("Writing HDU " + str(hdu) + " with mean: " +
                                 str(np.mean(mframe[hdu-1])) + '\n')
            frame[hdu].header['BZERO'] = 0.0    # don't rescale data
            frame[hdu].data = np.transpose(mframe[hdu-1, :, :])
        frame.close()

    sys.stderr.write('\n')
    del cframes 


parser = argparse.ArgumentParser(description='Pipeline to generate master \
bias and flat frames, then apply those master calibration files to a batch \
of science observations.')
parser.add_argument('files', nargs='*', help='files to process')
parser.add_argument('-t', '--telescope', action='store', default='none',
                    help='Specify telescope type',
                    choices=['VATT', '90Prime', 'Swope'])
parser.add_argument('-p', '--plot', action='store_true',
                    help='Plot diagnostics to the screen and pause before \
continuing?')
parser.add_argument('--masterbias', action='store',
                    help='Use this master bias file instead of generating a \
new one')
parser.add_argument('--masterflat', action='store',
                    help='Use this master flat file instead of generating a \
new one')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Provide additional output. Mostly useful for \
debugging.')
args = parser.parse_args()

# keywords to move from original files to the derived calibration files
kprop = ['DETSIZE', 'CCDSUM', 'TIMESYS', 'OBJECT', 'DATE-OBS', 'DARKTIME',
         'TIMEZONE', 'IMAGETYP', 'INSTRUME', 'DEWTEMP', 'LST-OBS', 'OBSERVER',
         'JULIAN', 'OBSERVAT', 'EPOCH', 'CAMTEMP', 'UT', 'TIME-OBS', 'ST',
         'EXPTIME']

darks = []    # list of dark frames
bias = []        # list of bias frames
filters = []    # list of filters used
flats = []    # flat frames (will be a 2D array, file ID and filter ID)
objects = []    # object frames (2D array, as above)

if args.telescope == 'Swope':
    IMGKEY = 'EXPTYPE'
else:
    IMGKEY = 'IMAGETYP'

# sort files by type
for file1 in args.files:
    file1 = glob.glob(file1)
    for cfile in file1:
        if os.path.isfile(cfile):
            frame = pyfits.open(cfile)
            thisfil = 0
            if re.match('zero', frame[0].header[IMGKEY], re.IGNORECASE) or \
               re.match('bias', frame[0].header[IMGKEY], re.IGNORECASE):
                bias.append(cfile)
            elif re.match('dark', frame[0].header[IMGKEY], re.IGNORECASE):
                darks.append(cfile)
            elif re.match('object', frame[0].header[IMGKEY], re.IGNORECASE):
                thisfil = frame[0].header["FILTER"]
                if not(thisfil in filters):
                    filters.append(thisfil)
                objects.append((cfile, thisfil))
            elif re.match('flat', frame[0].header[IMGKEY], re.IGNORECASE):
                thisfil = frame[0].header["FILTER"]
                if not(thisfil in filters):
                    filters.append(thisfil)
                flats.append((cfile, thisfil))
            else:
                sys.stderr.write(cfile+' - unknown image type ("' + 
                                 frame[0].header[IMGKEY] + '"), ignoring.\n')
            frame.close()

sys.stderr.write(str(len(args.files)) + ' files inspected.\n')
sys.stderr.write(str(len(darks)) + ' dark frames found. ')
sys.stderr.write(str(len(bias)) + ' bias frames found. ')
sys.stderr.write(str(len(flats)) + ' flat frames found.\n')
sys.stderr.write(str(len(objects)) + ' object frames with ' +
                 str(len(filters)) + ' filters identified (')
for i in filters:
    sys.stderr.write(i + ' ')
sys.stderr.write(')\n\n')

if args.masterbias:
    if not(os.path.isfile(args.masterbias)):
        sys.stderr.write('ERROR: specified master bias file does not exist. \
Exiting.\n\n')
        sys.exit(-1)
    else:
        sys.stderr.write('Using user-specified master bias: ' +
                         args.masterbias+'\n\n')
        mbias = mysci.Telload(args.masterbias, Tel=args.telescope,
                              quiet=not(args.verbose))
else:   # make a master bias and load it
    imageCombine(bias, 'bias', verbose=args.verbose)
    mbias = mysci.Telload('masterbias.fits', Tel=args.telescope,
                          quiet=not(args.verbose))

sys.stderr.write('\n\n\nNOTE: We are ignoring dark frames at the \
moment!!!!!\n\n\n')

# See if there are any dark frames, make a master dark.
"""
if len(darks) > 0:
    # we have darks!
    mean = []
    median = []
    stddev = []
    dframes = np.array([0])
    sys.stderr.write('Creating a master dark frame\n')
    sys.stderr.write('Loading dark frames')
    for image in darks:
        if bframes.ndim < 2:
            bframes.resize(idata.shape)
            bframes = idata-mbias
        else:
            # bias subtraction included
            bframes = np.dstack((bframes,idata-mbias))

        # get the exposure time for the dark frame, add it to a list
        # use this to make sure we're only combining appropriate dark frames
        # (not yet implemented)


        stddev.append(np.std(idata))
        mean.append(np.mean(idata))
        median.append(np.median(idata))
        sys.stderr.write('.')

    sys.stderr.write('\n')
    sys.stderr.write('Loaded ' + str(len(mean)) + ' dark frames.\n')



else:
    sys.stderr.write('No dark frames found.. not creating a master dark.\n\n')
"""

mflats = np.array([0])
# Create a master flat
# first load all the flat files (and normalize them), then loop over filters
sys.stderr.write('Creating master flats.\n')
for filtername in filters:
    sys.stderr.write("Making master flat field for filter: " + filtername + ' ')
    fframes = np.array([0])
    stddev = []
    thisfiltfiles = []
    for image in flats:
        if re.match(filtername, image[1]):
            thisfiltfiles.append(image[0])
    imageCombine(thisfiltfiles, "flat_"+filtername, verbose=args.verbose)

# now process the individual object frames, going by filter
sys.stderr.write('\n\nProcessing object frames (bias and flat correction)\n')
i = 0
for filter in filters:
    sys.stderr.write('Filter: ' + filter+'.\n')
    # locate the flat we want to use
    flatnum = filters.index(filter)
    for image in objects:
        if re.match(filter, image[1]):
            # filter for object matches what we're trying
            idata = mysci.Telload(image[0], Tel=args.telescope,
                                  quiet=not(args.verbose))
            datenow = datetime.datetime.today().isoformat()

            idata = idata-mbias

            idata = idata/mflats[flatnum]
            rootn = re.split('.fits', image[0])[0]
            fname = rootn + '-bsub_flat.fits'
            if os.path.isfile(fname):
                sys.stderr.write('Deleting existing ' + fname+'\n')
                raw_input('PRESS ENTER TO CONTINUE')
                os.remove(fname)
            sys.stderr.write('\t' + image[0] + '. Writing as ' + fname+'.\t')
            shutil.copy(image[0], fname)
            frame = pyfits.open(fname, mode='update')
            frame[0].header.add_history(datenow +
                                        ' - Bias and flat field corrected')
            for hdu in range(1, len(frame)):
                if args.verbose:
                    sys.stderr.write("Writing HDU " + str(hdu) +
                                     " with mean: " +
                                     str(np.mean(data[hdu-1])) + '\t')
                    sys.stderr.write(str(idata[hdu-1, :, :].shape) + '\t')
                    sys.stderr.write(str(idata[hdu-1, :, :].dtype) + '\n')
                frame[hdu].header['BZERO'] = 0.0    # don't rescale data
                frame[hdu].data = np.transpose(idata[hdu-1, :, :])
            frame.close()
            sys.stderr.write('Success.\n')
    i = i+1

sys.stderr.write('Finished processing ' + str(i) + ' filters.\n\n')
