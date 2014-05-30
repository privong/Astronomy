#!/usr/bin/env python
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
parser.add_argument('--minorder',action='store',type=int,default=10,help='Number of points on either side of minima for it to be considered valid. (Default:10)')
parser.add_argument('--tscl',action='store',type=float,default=1.0,help='Time scaling factor (Myr)')
parser.add_argument('--Lscl',action='store',type=float,default=1.0,help='Length scaling factor (kpc)')
parser.add_argument('--savefig',action='store',type=str,default=False,help='Save figure of the nuclear separation for diagnostics.')
args=parser.parse_args()

if len(args.center)<1:
  sys.stderr.write('Error, you must specify centers file\n\n')
  sys.exit(-1)


data=np.loadtxt(args.center)

#sep=((data[:,1]-data[:,4])**2+(data[:,2]-data[:,5])**2+(data[:,3]-data[:,6])**2)**0.5
sep=np.array(data[:,1])
time=np.array(data[:,0])

fig=plt.figure(1,figsize=(5.5,3.5),tight_layout=True)
ax1=plt.subplot(111)
ax1.minorticks_on()
ax1.set_xlabel('t')
ax1.set_ylabel('Nuclear separation')
ax1.set_xlim([0,8])
ax1.set_ylim([0,3.5])
if args.tscl!=1.0:
  ax1.set_xlabel('T (Myr)')
  time=(time-2.0)*args.tscl
  ax1.set_xlim([-2*args.tscl,6*args.tscl])
  args.tnow-=2
  args.tnow*=args.tscl
if args.Lscl!=1.0:
  ax1.set_ylabel('Nuclear separation (kpc)')
  sep=sep*args.Lscl
  args.eps*=args.Lscl
  ax1.set_ylim([0,3.5*args.Lscl])

ax1.plot(time,sep)

# get local minima
minima=argrelextrema(sep, np.less,order=args.minorder)[0]
if args.eps:
  sys.stderr.write('Ignoring "passes" below the smoothing limit.\n')
  minima=np.delete(minima,np.nonzero((sep[minima]<args.eps)*sep[minima]))
plt.scatter(time[minima],sep[minima])
if args.tnow:
  plt.vlines(args.tnow,0,8*args.Lscl)

# get the merger point
if args.eps:
  mtime=time[(sep<=args.eps).nonzero()[0][0]]

# re-scale this to a merger stage defined by the time between sucessive passages
iprev=0
npass=0
ntime=time*1
for i in minima:
  ntime[iprev:i]=npass+(time[iprev:i]-time[iprev])/(time[i+1]-time[iprev])
  if args.tnow and args.tnow < time[i+1] and args.tnow > time[iprev]:
    tnowscl=npass+(args.tnow-time[iprev])/(time[i+1]-time[iprev])
    print("Merger stage of this object: %f" % (tnowscl))
  iprev=i
  npass+=1

ax2=ax1.twiny()
if args.Lscl!=1.0: ax2.set_ylim([0,3.5*args.Lscl])
else: ax2.set_ylim([0,3.5])
# put tick marks at the minima
ax2.xaxis.set_ticks(np.concatenate([time[minima][:4],[mtime]],axis=0))
labels=[str(i) for i in np.arange(1,4)]
labels.append('0m')
ax2.xaxis.set_ticklabels(labels,rotation=90)
ax2.minorticks_on()
#for (loc,label) in (ax2.xaxis.get_ticklines(),ax2.xaxis.get_ticklabels()):
  
ax2.set_xlabel('Merger Stage')
ax2.plot(time,sep)

if args.savefig:
  plt.savefig(args.savefig)
else:
  plt.show()

