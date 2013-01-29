#!/usr/bin/python

import pylab
import argparse,sys

parser=argparse.ArgumentParser(description="Read in the starlog files, bin them and plot the star formation rate as a function of time. Optionally takes arguments for mass and time scaling if you want to plot it in physical units.")
parser.add_argument('starlog',type=str,nargs='*',help='List of 1 or more starlog files in the zeno format.')
parser.add_argument('--split',action='store',type=int,default='0',help='Separate the starlog into two galaxies. This value is the upper particle ID number for the first galaxy. NOT YET IMPLEMENTED')
parser.add_argument('--savefig',action='store',type=str,default=False,help='Figure will be saved to this filename if given.')
parser.add_argument('--pmass',action='store',type=float,default=1,help='Mass of new star clusters in simulation units. Defaults to 1.')
parser.add_argument('--tscl',action='store',type=float,default=1,help='Time Scaling (Myr)')
parser.add_argument('--Mscl',action='store',type=float,default=1,help='Mass Scaling (GM_sun)')
parser.add_argument('--nbin',default='100',action='store',help='Number of bins to use')
parser.add_argument('--labels',default='',action='store',help='Comma separated labels for the plot items. Must be as many labels as files added.')
parser.add_argument('--title',default='Star Formation Rates',action='store',type=str,help='Plot title, must be enclosed in quotes.')
args=parser.parse_args()

if len(args.starlog)<1:
  sys.stderr.write('Error, you must specify at least 1 starlog file\n\n')
  sys.exit(-1)

if args.labels=='':
  args.labels=args.starlog
else:
  if len(args.labels.split(','))!=len(args.starlog):
    sys.stderr.write('Error, you must provide a number of labels equal to the number of starlog files.\n')
    sys.exit(-1)
  else:
    args.labels=args.labels.split(', ')

spec=zip(args.starlog,args.labels)

sys.stderr.write('Found '+str(len(args.starlog))+' star log files.\n')

# import the time for each cluster and the local SFR
data=[(pylab.loadtxt(filename,usecols=(2,3)),label) for filename,label in spec]

# base the bin size on the first file
junk,mybins=pylab.histogram(data[0][0][:,0],bins=int(args.nbin))

# histogram the data
binned=[(pylab.histogram(dat[:,0],bins=mybins,density=False),label) for dat,label in data]

# set the axis labels and make adjustments to the data
if args.tscl!=1:
  pylab.xlabel('t (Myr)')
  # convert the times to have 0 be pericenter passage (t=2 in sim units)
  SFR=[((clusters[0].astype(float)/(clusters[1][1]-clusters[1][0])),clusters[1]-2.0+(clusters[1][1]-clusters[1][0])/2.,label) for clusters,label in binned]
else:
  pylab.xlabel('t (sim units)')
  # convert data to dN/dt
  SFR=[((clusters[0].astype(float)/(clusters[1][1]-clusters[1][0])),clusters[1]+(clusters[1][1]-clusters[1][0])/2.,label) for clusters,label in binned]

if args.Mscl!=1:
  if args.pmass!=1:
    pylab.ylabel('dM$_*$/dt (M$_{\odot}$ yr$^{-1}$)')
  else:
    sys.stderr.write("Surely your gas particles don't all have masses of 1 in sim units??\n")
    sys.exit()
else:
  if args.pmass==1:
    pylab.ylabel('dN$_*$/dt (Particles time$^{-1}$)')
  else:
    pylab.ylabel('dM$_*$/dat (Mass time$^{-1}$, sim units)')

for pl1,pl2,label in SFR:
    # plot the SFR with scalings
    pylab.semilogy(args.tscl*pl2[:-1],args.pmass*(args.Mscl*1.e9)*pl1/(args.tscl*1.e6),label=label)
pylab.legend(fontsize='x-small',frameon=False)
pylab.title(args.title)
pylab.minorticks_on()
if args.savefig:
  pylab.savefig(args.savefig)
  print "Plot saved to "+args.savefig+".\n"
else:
  pylab.show()
