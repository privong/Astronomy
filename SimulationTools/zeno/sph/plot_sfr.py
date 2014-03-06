#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import argparse,sys

parser=argparse.ArgumentParser(description="Read in the starlog files, bin them and plot the star formation rate as a function of time. Optionally takes arguments for mass and time scaling if you want to plot it in physical units.")
parser.add_argument('starlog',type=str,nargs='*',help='List of 1 or more starlog files in the zeno format.')
#parser.add_argument('--split',action='store',type=int,default='0',help='Separate the starlog into two galaxies. This value is the upper particle ID number for the first galaxy. NOT YET IMPLEMENTED')
parser.add_argument('--savefig',action='store',type=str,default=False,help='Figure will be saved to this filename if given.')
parser.add_argument('--pmass',action='store',type=str,default='0',help='Mass of new star clusters in simulation units. Defaults to 1. Comma separated if there\'s more than one value.')
parser.add_argument('--nucsep',action='store',type=str,default=False,help='Centers file of the nuclear separation to overplot on the y2 axis.')
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
    sys.stderr.write('LABELS Error: you must provide a number of labels equal to the number of starlog files.\n')
    sys.exit(-1)
  else:
    args.labels=args.labels.split(',')

if args.pmass=='0':
  pmass=np.ones(len(args.starlog))
else:
  if (len(args.pmass.split(','))!=len(args.starlog) or len(args.pmass.split(','))==1):
    sys.stderr.write('PMASS Error: you must provide a single number or a number of particle masses equal to the number of starlog files.\n')
    sys.exit(-1)
  else:
    pmass=args.pmass.split(',')
 
spec=zip(args.starlog,args.labels,pmass)

sys.stderr.write('Found '+str(len(args.starlog))+' star log files.\n')

# import the time for each cluster and the local SFR
data=[(np.loadtxt(filename,usecols=(2,3)),label,pmass) for filename,label,pmass in spec]

# base the bin size on the first file
junk,mybins=np.histogram(data[0][0][:,0],bins=int(args.nbin))

# histogram the data
binned=[(np.histogram(dat[:,0],bins=mybins,density=False),label,pmass) for dat,label,pmass in data]

fig=plt.figure()
ax1=plt.subplot(111)
# set the axis labels and make adjustments to the data
if args.tscl!=1:
  ax1.set_xlabel('t (Myr)',fontsize='x-large')
  # convert the times to have 0 be pericenter passage (t=2 in sim units)
  SFR=[((clusters[0].astype(float)/(clusters[1][1]-clusters[1][0])),clusters[1]-2.0+(clusters[1][1]-clusters[1][0])/2.,label,pmass) for clusters,label,pmass in binned]
else:
  ax1.set_xlabel('t (sim units)',fontsize='x-large')
  # convert data to dN/dt
  SFR=[((clusters[0].astype(float)/(clusters[1][1]-clusters[1][0])),clusters[1]+(clusters[1][1]-clusters[1][0])/2.,label,pmass) for clusters,label,pmass in binned]

if args.Mscl!=1:
  args.Mscl=args.Mscl*1.e9	# convert it to M_sun from GM_sun
  if args.pmass!=1:
    ax1.set_ylabel('dM$_*$/dt (M$_{\odot}$ yr$^{-1}$)',fontsize='x-large')
  else:
    sys.stderr.write("Surely your gas particles don't all have masses of 1 in sim units??\n")
    sys.exit()
else:
  if args.pmass=='0':
    ax1.set_ylabel('dN$_*$/dt (Particles)',fontsize='x-large')
  else:
    ax1.set_ylabel('dM$_*$/dt (sim units)',fontsize='x-large')

for pl1,pl2,label,pm in SFR:
    # plot the SFR with scalings
    ax1.semilogy(args.tscl*pl2[:-1],float(pm)*args.Mscl*pl1/(args.tscl*1.e6),label=label)
ax1.legend(fontsize='x-small',frameon=False,loc='upper left')
plt.title(args.title)
ax1.minorticks_on()
if args.nucsep:
  ax2=ax1.twinx()
  ax2.minorticks_on()
  ax2.set_ylabel('Nuclear Separation',fontsize='x-large')
  data=np.loadtxt(args.nucsep)
  sep=((data[:,1]-data[:,4])**2+(data[:,2]-data[:,5])**2+(data[:,3]-data[:,6])**2)**0.5
  time=(data[:,0]-2.0)*args.tscl
  ax2.set_ylim([0,3.5])
  ax2.plot(time,sep,ls='--',color='gray')

if args.savefig:
  plt.savefig(args.savefig)
  sys.stdout.write("Plot saved to "+args.savefig+".\n")
else:
  plt.show()
