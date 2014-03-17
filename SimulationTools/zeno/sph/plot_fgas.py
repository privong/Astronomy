#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import argparse,sys

# to generate the required input files, do something like this:
#cat i002.dat c_umax/iso002-D_????.dat | snapsift - - sieve='type!=0x41' | snapset - - auxvx='type!=0x66 ? m : 0' auxvy='type==0x66 ? m : 0' produce=AuxVec | snapstat - value=auxvx options=time,sum > c_umax/iso002-D_gas_frac_x.txt
#cat i002.dat c_umax/iso002-D_????.dat | snapsift - - sieve='type!=0x41' | snapset - - auxvx='type!=0x66 ? m : 0' auxvy='type==0x66 ? m : 0' produce=AuxVec | snapstat - value=auxvy options=time,sum > c_umax/iso002-D_gas_frac_y.txt
#paste c_umax/iso002-D_gas_frac_x.txt c_umax/iso002-D_gas_frac_y.txt > c_umax/iso002-D_gas_frac.txt


parser=argparse.ArgumentParser(description="Read in information on the gas fractions and plot the gas fraction as a function of time. Optionally takes arguments for mass and time scaling if you want to plot it in physical units.")
parser.add_argument('gasfile',type=str,nargs='*',help='List of 1 or more files with information on gas logs (Col 1: time, Col 2: total # particles, Col 3: number of star particles.')
parser.add_argument('-mgas',action='store_true',default=False,help='Plot the gas mass as a function of time.')
parser.add_argument('-fgas',action='store_true',default=False,help='Plot the gas fraction as a function of time (DEFAULT)?')
parser.add_argument('--Mscl',action='store',type=float,default=1,help='Mass Scaling (GM_sun), only useed if -mgas is flagged.')
parser.add_argument('--savefig',action='store',type=str,default=False,help='Figure will be saved to this filename if given.')
parser.add_argument('--tscl',action='store',type=float,default=1,help='Time Scaling (Myr)')
parser.add_argument('--labels',default='',action='store',help='Comma separated labels for the plot items. Must be as many labels as files added.')
parser.add_argument('--title',default='f$_{gas}$',action='store',type=str,help='Plot title, must be enclosed in quotes.')
args=parser.parse_args()

if len(args.gasfile)<1:
  sys.stderr.write('Error, you must specify at least 1 input file\n\n')
  sys.exit(-1)

if args.labels=='':
  args.labels=args.gasfile
else:
  if len(args.labels.split(','))!=len(args.gasfile):
    sys.stderr.write('Error, you must provide a number of labels equal to the number of input files.\n')
    sys.exit(-1)
  else:
    args.labels=args.labels.split(', ')

if not(args.mgas) and not(args.fgas):
  # default to fgas
  args.fgas=True

spec=zip(args.gasfile,args.labels)

sys.stderr.write('Found '+str(len(args.gasfile))+' input files.\n')


if args.Mscl!=1:
  # put it in M_sun
  args.Mscl=args.Mscl*1.e9

# set the axis labels and make adjustments to the data
if args.tscl!=1:
  plt.xlabel('t (Myr)')
else:
  plt.xlabel('t (sim units)')

if args.fgas:
  plt.ylabel('f$_{gas}$')
  data=[(np.loadtxt(filename,usecols=(0,2,8)),label) for filename,label in spec]
elif args.mgas:
  plt.ylabel('M$_{gas}$')
  data=[(np.loadtxt(filename,usecols=(0,8)),label) for filename,label in spec]

for inst,label in data:
    # plot the SFR with scalings
  if args.fgas:
    yax=inst[:,2]/(inst[:,1]+inst[:,2])
  elif args.mgas:
    yax=inst[:,1]*args.Mscl
  if args.tscl==1:
    plt.plot(inst[:,0],yax,label=label)
  else:
    plt.plot(args.tscl*(inst[:,0]-2.0),yax,label=label)
plt.legend(fontsize='x-small',frameon=False)

plt.title(args.title)
plt.minorticks_on()
if args.savefig:
  plt.savefig(args.savefig)
  print "Plot saved to "+args.savefig+".\n"
else:
  plt.show()
