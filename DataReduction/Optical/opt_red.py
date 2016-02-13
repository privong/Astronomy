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


parser = argparse.ArgumentParser(description='Pipeline to generate master \
bias and flat frames, then apply those master calibration files to a batch \
of science observations.')
parser.add_argument('files', nargs='*', help='files to process')
parser.add_argument('-t', '--telescope', action='store', default='none',
                    help='Specify telescope type', choices=['VATT', '90Prime'])
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

# sort files by type
for file1 in args.files:
    file1 = glob.glob(file1)
    for file in file1:
        if os.path.isfile(file):
            frame = pyfits.open(file)
            thisfil = 0
            if re.match('zero', frame[0].header["IMAGETYP"]) or \
               re.match('bias', frame[0].header["IMAGETYP"]):
                bias.append(file)
            elif re.match('dark', frame[0].header["IMAGETYP"]):
                darks.append(file)
            elif re.match('object', frame[0].header["IMAGETYP"]):
                thisfil = frame[0].header["FILTER"]
                if not(thisfil in filters):
                    filters.append(thisfil)
                objects.append((file, thisfil))
            elif re.match('flat', frame[0].header["IMAGETYP"]):
                thisfil = frame[0].header["FILTER"]
                if not(thisfil in filters):
                    filters.append(thisfil)
                flats.append((file, thisfil))
            else:
                sys.stderr.write(file+' - unknown image type, ignoring.\n')
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
else:   # make a master bias
    mean = []
    median = []
    stddev = []
    bframes = np.array([0])
    sys.stderr.write('Creating a master bias file...\n')
    sys.stderr.write('Loading bias frames...\n')
    for image in bias:
        # need to un-fix this later when more telescopes are added
        idata = mysci.Telload(image, Tel=args.telescope,
                              quiet=not(args.verbose))
        # idata=idata.reshape((1,idata.shape[0],idata.shape[1],idata.shape[2]))
        if bframes.ndim < 2:
            # bframes.resize((1,idata.shape[0],idata.shape[1],idata.shape[2]))
            bframes = idata.copy()
        else:
            bframes = np.concatenate((bframes, idata), axis=0)
        stddev.append(np.std(idata))

        """
        this is wrong for large files unless the data are converted to float64
        since this isn't necessary for the other steps, we won't do it
        """
        mean.append(np.mean(idata))
        median.append(np.median(idata))
        if args.verbose:
            sys.stderr.write('\nMean: ' + str(np.mean(idata)) +
                             '\tMedian: ' + str(np.median(idata)) +
                             '\tstddev: '+str(np.std(idata)))
            sys.stderr.write('.\n')

    sys.stderr.write('\n')
    sys.stderr.write('Loaded ' + str(len(mean)) + ' bias frames.\n')
    if args.plot:
        # plot diagonstics
        fig = plt.figure()
        # plt.scatter(range(len(mean)),mean,color='red',label='Mean')
        plt.scatter(range(len(median)), median, color='blue', label='Median')
        plt.scatter(range(len(stddev)), stddev, color='green', label='Stddev')
        plt.legend()
        plt.show()
    # right now take all the frames, need to add selective frame-ignoring
    mbias = np.mean(bframes, axis=0)
    if args.verbose:
        sys.stderr.write(str(bframes.shape) + '\n')
        sys.stderr.write(str(mbias.shape) + '\n')

    datenow = datetime.datetime.today().isoformat()

    # if we're dealing with a single fits extension, create a new file
    if os.path.isfile('masterbias.fits'):
        sys.stderr.write('Deleting existing masterbias.fits\n')
        raw_input('PRESS ENTER TO CONTINUE')
        os.remove('masterbias.fits')
    if len(mbias.shape) < 3:
        # copy header from an existing bias frame, add comments saying which
        # bias frames were combined and how they were combined.
        frame = pyfits.PrimaryHDU(mbias)
        sbias = pyfits.open(image)
        # copy over the keywords we want
        for kw in kprop:
            if kw in sbias[0].header:
                frame.header.set(kw, sbias[0].header[kw])
        # add reduction info to header
        frame.header['IMAGETYP'] = 'masterbias'
        frame.header.add_history(datenow + ' - Masterbias created')
        frame.header.add_comment('Master bias created from mean of: ' +
                                 str(bias))
        frame.writeto('masterbias.fits')
    else:
        # we need to insert this new data into a copy of the old fits file
        shutil.copy(image, 'masterbias.fits')
        frame = pyfits.open('masterbias.fits', mode='update')
        frame[0].header['IMAGETYP'] = 'masterbias'
        frame[0].header.add_history(datenow + ' - Masterbias created')
        frame[0].header.add_comment('Master bias created from mean of: ' +
                                    str(bias))
        for hdu in range(1, len(frame)):
            if args.verbose:
                sys.stderr.write("Writing HDU " + str(hdu) + " with mean: " +
                                 str(np.mean(mbias[hdu-1])) + '\n')
                # sys.stderr.write(str(mbias[hdu-1,:,:].shape)+'\n')
                # sys.stderr.write(str(mbias[hdu-1,:,:].dtype)+'\n')
            frame[hdu].header['BZERO'] = 0.0    # don't rescale data
            frame[hdu].data = np.transpose(mbias[hdu-1, :, :])
        frame.close()

    sys.stderr.write('\n')
    del bframes

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
for filter in filters:
    sys.stderr.write("Making master flat field for filter: " + filter + ' ')
    fframes = np.array([0])
    stddev = []
    for image in flats:
        if re.match(filter, image[1]):
            idata = mysci.Telload(image[0], Tel=args.telescope,
                                  quiet=not(args.verbose))
            # idata.reshape((1,idata.shape[0],idata.shape[1],idata.shape[2]))
            if args.verbose:
                sys.stderr.write('\nmbias.shape=' + str(mbias.shape) +
                                 '\tidata.shape=' + str(idata.shape)+'\n\n')
            idata = idata-mbias
            # idata.resize(1,idata.shape[0],idata.shape[1],idata.shape[2])
            # add that flat field image onto the stack
            if fframes.ndim < 2:
                fframes = idata/np.median(idata)
            else:
                fframes = np.concatenate((fframes, idata/np.median(idata)),
                                         axis=0)
            stddev.append(np.std(idata/np.mean(idata)))
    sys.stderr.write('\n')
    # we've loaded all the flats for that particular filter, now make a master
    mflat = np.median(fframes, axis=0)
    if args.verbose:
        sys.stderr.write('fframes.shape: ' + str(fframes.shape) +
                         '\tmflat.shape: ' + str(mflat.shape)+'\n')
    mfname = filter + '_masterflat.fits'
    # add that master flat to the stack of master flats
    if mflats.ndim < 2:
        mflats = mflat*1.0
        # mflats.resize((1,mflat.shape[0],mflat.shape[1],mflat.shape[2]))
    else:
        mflats = np.concatenate((mflats, mflat), axis=0)
    if os.path.isfile(mfname):
        sys.stderr.write('Deleting existing ' + mfname+'\n')
        raw_input('PRESS ENTER TO CONTINUE')
        os.remove(mfname)
    datenow = datetime.datetime.today().isoformat()
    if args.verbose:
        sys.stderr.write("mflats.shape: " + str(mflats.shape) + "\n")
    # if we're dealing with a single fits extension, create a new file
    if mflat.ndim < 2:
        if args.verbose:
            sys.stderr.write('Single extension data, \
creating a new fits file.\n')
        frame = pyfits.PrimaryHDU(mflat)
        sflat = pyfits.open(image[0])
        for kw in kprop:
            if kw in sflat[0].header:
                frame.header.set(kw, sflat[0].header[kw])
        frame.header['IMAGETYP'] = 'masterflat'
        frame.header.add_history(datenow + ' - Master Flat created')
        sflat.close()
        sys.stderr.write('\tsaving master flat as: ')
        sys.stderr.write(mfname + '\n')
        frame.writeto(mfname)
    # otherwise we insert this new data into a copy of the old fits file
    else:
        if args.verbose:
            sys.stderr.write('Multiextension data, copying off an \
existing image\n')
        shutil.copy(image[0], mfname)
        frame = pyfits.open(mfname, mode='update')
        frame[0].header['IMAGETYP'] = 'masterflat'
        frame[0].header.add_history(datenow + ' - Master Flat created')
        for hdu in range(1, len(frame)):
            if args.verbose:
                sys.stderr.write("Writing HDU " + str(hdu) + " with mean: " +
                                 str(np.mean(mflat[hdu-1])) + '\t')
                sys.stderr.write(str(mflat[hdu-1, :, :].shape) + '\t')
                sys.stderr.write(str(mflat[hdu-1, :, :].dtype) + '\n')
            frame[hdu].header['BZERO'] = 0.0    # so the data isn't rescaled
            frame[hdu].data = np.transpose(mflat[hdu-1, :, :])
        frame.close()

del fframes

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
