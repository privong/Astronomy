#!/sw/bin/python2.7

import pylab
import argparse,sys

parser=argparse.ArgumentParser(description="Read in the starlog files, bin them and plot the star formation rate as a function of time. Optionally takes arguments for mass and time scaling if you want to plot it in physical units.")
parser.add_argument('starlog',type=str,nargs='*',help='List of 1 or more starlog files in the zeno format.')
parser.add_argument('--savefig',action='store',type=str,default=False,help='Figure will be saved to this filename if given.')
parser.add_argument('--pmass',action='store',type=float,default=9.53674e-07,help='Mass of new star clusters in simulation units. Defaults to 9.53674e-07.')
parser.add_argument('--tscl',action='store',type=float,default=1,help='Time Scaling (Myr')
parser.add_argument('--Mscl',action='store',type=float,default=1,help='Mass Scaling (GM_sun')
parser.add_argument('--nbin',default='80',action='store',help='Number of bins to use')
parser.add_argument('--title',default='Star Formation Rates',action='store',type=str,help='Plot title, must be enclosed in quotes.')
args=parser.parse_args()

if len(args.starlog)<1:
  sys.stderr.write('Error, you must specify at least 1 starlog file\n\n')
  sys.exit(-1)

sys.stderr.write('Found '+str(len(args.starlog))+' star log files.\n')

if args.tscl!=1:
  pylab.xlabel('t (Myr)')
else:
  pylab.xlabel('t')

if args.Mscl!=1:
  pylab.ylabel('dM$_*$/dt (M$_{\odot}$ yr$^{-1}$)')
else:
  pylab.ylabel('dM$_*$/dt')

# import the time for each cluster and the local SFR
data=[(pylab.loadtxt(filename,usecols=(2,3)),filename) for filename in args.starlog]

# base the bin size on the first file
junk,mybins=pylab.histogram(data[0][0][:,0],bins=int(args.nbin))

# histogram the data
binned=[(pylab.histogram(dat[:,0],bins=mybins),label) for dat,label in data]

# convert data to dN/dt
SFR=[((clusters[0].astype(float)/(clusters[1][1]-clusters[1][0])),clusters[1]+(clusters[1][1]-clusters[1][0])/2.,label) for clusters,label in binned]

for pl1,pl2,label in SFR:
    # plot the SFR with scalings
    pylab.semilogy(args.tscl*pl2[:-1],args.pmass*args.Mscl*pl1,label=label)
    #pylab.plot(args.tscl*pl2[:-1],args.pmass*args.Mscl*pl1,label=label)
pylab.legend()
pylab.title(args.title)
pylab.minorticks_on()
if args.savefig:
  pylab.savefig(args.savefig)
  print "Plot saved to "+args.savefig+".\n"
else:
  pylab.show()
