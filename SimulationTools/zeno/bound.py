#!/usr/bin/env python2
#
# bound.py
# Plot the orbital energy of a particle versus radius
#
# Unfinished/untested concept script. use at your own risk.

import sys
import argparse
import matplotlib.pyplot as plt
import numpy as np


VERSION = '0.1.1'
VERSIONDATE = '11 October 2014'

# takes output from the following:
# cat s010-A_??00.dat | snapsift - - sieve='type!=0x41' | snapset - - auxvx='sqrt(x*x+y*y+z*z)' auxvy='0.5*(vx*vx+vy*vy+vz*vz)+phi' produce=AuxVec | snaplist - fields=AuxVec

parser = argparse.ArgumentParser(description='Plot particle energy versus \
                                              radius.')
parser.add_argument('Efile', type=str,
                    help='ASCII table with particle radii and energies to \
                          plot.')
parser.add_argument('--savefig', action='store', type=str, default=False,
                    help='Figure will be saved to this filename if given.')
parser.add_argument('--version', action='version',
                    version='%(prog)s '+VERSION+' ('+VERSIONDATE+')')
args = parser.parse_args()

data = np.loadtxt(args.snap, usecols=(0, 1))

plt.axhline(0, linestyle='-', color='gray')
plt.scatter(data[:, 0], data[:, 1], marker='.')
plt.minorticks_on()
plt.xlabel('Radius')
plt.ylabel('Energy (Potential + Kinetic)')
if args.savefig:
    plt.savefig(args.savefig)
    print("Plot saved to: " + args.savefig)
else:
    plt.show()
