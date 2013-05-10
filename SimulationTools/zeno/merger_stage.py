#!/usr/bin/python2
#
# Determine a numerical merger stage based on a model.

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import argrelextrema
import argparse,sys
parser=argparse.ArgumentParser(description="Determine a numerical merger stage based on an input nuclear separation curve.")
parser.add_argument('center',type=str,help='Centers file')
parser.add_argument('-tstage',action='store_true',default=True,help='Compute the merger stage between successive passes linear in time.')
#parser.add_argument('-rstage',action='store_true',efault=False,help='Compute the merger stage between successive passes, linear in nuclear separation.') 
parser.add_argument('--eps',action='store',type=float,default=0.,help='Smoothing length for the simulation (if given, will clip minima below that)')
parser.add_argument('--tnow',action='store',type=float,default=0.,help='Viewing time.')
parser.add_argument('--savefig',action='store',type=str,default=False,help='Save figure of the nuclear separation for diagnostics.')
args=parser.parse_args()

if len(args.center)<1:
  sys.stderr.write('Error, you must specify centers file\n\n')
  sys.exit(-1)


data=np.loadtxt(args.center)

sep=((data[:,1]-data[:,4])**2+(data[:,2]-data[:,5])**2+(data[:,3]-data[:,6])**2)**0.5
time=data[:,0]

fig=plt.figure()
ax1=plt.subplot(111)
ax1.minorticks_on()
ax1.set_xlabel('t')
ax1.set_ylabel('Nuclear separation')
ax1.set_xlim([0,8])
ax1.set_ylim([0,3.5])
ax1.plot(time,sep)
# get local minima
minima=argrelextrema(sep, np.less,order=50)
plt.scatter(time[minima],sep[minima])
if args.tnow:
  plt.vlines(args.tnow,0,8)

# re-scale this to a merger stage defined by the time between sucessive passages
iprev=0
npass=0
ntime=time*1
for i in minima[0]:
  ntime[iprev:i]=npass+(time[iprev:i]-time[iprev])/(time[i+1]-time[iprev])
  if args.tnow and args.tnow < time[i+1] and args.tnow > time[iprev]:
    tnowscl=npass+(args.tnow-time[iprev])/(time[i+1]-time[iprev])
    print "Merger stage of this object: %f" % (tnowscl)
  iprev=i
  npass+=1

ax2=ax1.twiny()
ax2.set_ylim([0,3.5])
# put tick marks at the minima
ax2.xaxis.set_ticks(time[minima][:4])
ax2.xaxis.set_ticklabels(np.arange(4)+1)
ax2.minorticks_on()
#for (loc,label) in (ax2.xaxis.get_ticklines(),ax2.xaxis.get_ticklabels()):
  
ax2.set_xlabel('Merger Stage')
ax2.plot(time,sep)

if args.savefig:
  plt.savefig(args.savefig)
else:
  plt.show()

