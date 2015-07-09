#!/usr/bin/env python2

# hicomp.py
#
# generate a comparison set of histograms for original data with calibrated
# data or a comparison file

import glob
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits as pyfits


def hicomp(files, compfile=False, hrange=(0, 65000), corrfac=1):

    # get the flie list
    files = glob.glob(files)
    # sort it
    files.sort()
    if compfile:
        # load the compfile, compare *everything* to this
        frame = pyfits.open(compfile)
        comp = True
    else:
        comp = False
    # continue comparing stuff
    j = 0   # keep track of how many comparisons we've made
    for file in files:
        plt.figure(j)
        plt.xlabel('Counts')
        plt.ylabel('Number')
        frame2 = pyfits.open(file)
        if not(comp):
            frame = pyfits.open(file.split('.fits')[0] + '-bsub_flat.fits')
            plt.title(file + '-' + file.split('.fits')[0] + '-bsub_flat.fits')
        else:
            plt.title(file+' and ' + compfile)
        for i in range(1, len(frame)):  # frames must have the same number of
                    # extensions for this to work!
            # uncorrected data
            (a, b, c) = plt.hist(np.ravel(frame2[i].data), 100, range=hrange,
                                 alpha=0.3, color='red')
            # corrected data
            (a, b, c) = plt.hist(np.ravel(frame[i].data*corrfac), 100,
                                 range=hrange, alpha=0.3, color='blue')
        frame2.close()
        if not(comp):
            frame.close()
        print("Saving figure #" + str(j) + ", " + file.split('.fits')[0] + \
              '.png')
        plt.savefig(file.split('.fits')[0] + '.png', format='png')
        j = j+1

    if comp:
        frame.close()

    # delete unused variables
    del a, b, c
    del frame, frame2

    return 0
