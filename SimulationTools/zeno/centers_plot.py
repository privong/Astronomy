#!/usr/bin/env python2
#
# centers_plot.py
#
# Read in the snapascii output from a snaptrak file, pull out only the
# positions, determine the 3D separation, and plot it as a function of time.

import argparse
# import matplotlib.pyplot as plt
import math

VERSION = '0.1'
VERSIONDATE = '30 August 2012'

# set up command line arguments
parser = argparse.ArgumentParser(description='Read in the snapascii output \
                                              from a snaptrak file, pull out \
                                              only the positions, determine \
                                              the 3D separation, and plot it \
                                              as a function of time.')
parser.add_argument('centers', type=str, help='ASCII file of snaptrak output.')
parser.add_argument('-noPlot', action='store_true', default=False,
                    help='Suppress plotting.')
parser.add_argument('-writeDist', action='store', default=False,
                    help='Write the nuclear separation as a function of time \
                          to the specified ASCII file.')
parser.add_argument('--version', action='version',
                    version='%(prog)s '+VERSION+' ('+VERSIONDATE+')')
args = parser.parse_args()

infile = open(args.centers, 'r')

if args.writeDist:
    outfile = open(args.writeDist, 'w')

while True:
    line = infile.readline()
    pos1 = []
    pos2 = []
    if len(line) == 0:
        break
    else:
        # first line was the nbody line. read the next batch of lines
        line = infile.readline()
        time = float(infile.readline().split()[0])  # Time, keep
        line = infile.readline()    # Mass1, discard
        line = infile.readline()    # Mass2, discard
        pos1 = [float(x) for x in infile.readline().split()]  # Position1, keep
        pos2 = [float(x) for x in infile.readline().split()]  # Position1, keep
        vel1 = [float(x) for x in infile.readline().split()]  # Velocity1, keep
        vel2 = [float(x) for x in infile.readline().split()]  # Velocity2, keep

        # now compute the geometric distance
        dist = math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 +
                         (pos1[2]-pos2[2])**2)
        dv = math.sqrt((vel1[0]-vel2[0])**2+(vel1[1]-vel2[1])**2 +
                       (vel1[2]-vel2[2])**2)
        outfile.write(str(time)+'\t' + str(dist) + '\t' + str(dv) + '\n')

outfile.close()
infile.close()
