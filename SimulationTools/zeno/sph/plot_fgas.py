#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import argparse,sys

# to generate the required input files, do something like this:
#cat i002.dat c_umax/iso002-D_????.dat | snapsift - - sieve='type!=0x41' | snapset - - auxvx='type!=0x66 ? m : 0' auxvy='type==0x66 ? m : 0' produce=AuxVec | snapstat - value=auxvx options=time,sum > c_umax/iso002-D_gas_frac_x.txt
#cat i002.dat c_umax/iso002-D_????.dat | snapsift - - sieve='type!=0x41' | snapset - - auxvx='type!=0x66 ? m : 0' auxvy='type==0x66 ? m : 0' produce=AuxVec | snapstat - value=auxvy options=time,sum > c_umax/iso002-D_gas_frac_y.txt
#paste c_umax/iso002-D_gas_frac_x.txt c_umax/iso002-D_gas_frac_y.txt > c_umax/iso002-D_gas_frac.txt


parser=argparse.ArgumentParser(description="Read in information on the gas fractions and plot the gas fraction as a function of time. Optionally takes arguments for mass and time scaling if you want to plot it in physical units.")
parser.add_argument('gasfile',type=str,nargs='*',help='List of 1 or more files with information on gas logs (Col 1: time, Col 2: total # particles, Col 3: number of star particles.')
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

spec=zip(args.gasfile,args.labels)

sys.stderr.write('Found '+str(len(args.gasfile))+' input files.\n')

data=[(np.loadtxt(filename,usecols=(0,2,8)),label) for filename,label in spec]

# set the axis labels and make adjustments to the data
if args.tscl!=1:
  plt.xlabel('t (Myr)')
else:
  plt.xlabel('t (sim units)')

plt.ylabel('f$_{gas}$')

for inst,label in data:
    # plot the SFR with scalings
  if args.tscl==1:
    plt.plot(inst[:,0],inst[:,2]/(inst[:,1]+inst[:,2]),label=label)
  else:
    plt.plot(args.tscl*(inst[:,0]-2.0),inst[:,2]/(inst[:,1]+inst[:,2]),label=label)
    
plt.legend(fontsize='x-small',frameon=False)
plt.title(args.title)
plt.minorticks_on()
if args.savefig:
  plt.savefig(args.savefig)
  print "Plot saved to "+args.savefig+".\n"
else:
  plt.show()
