#!/usr/bin/python
#
# zenoLogplot.py
#
# Read in a zeno logfile and plot the energies.

import sys,re,argparse,os
import matplotlib.pyplot as plt
import numpy

VERSION='0.1'
VERSIONDATE='25 April 2012'

# set up command line arguments
parser=argparse.ArgumentParser(description='Process zeno sphcode logs and make plots of interesting quantities.')
parser.add_argument('logfile',type=str,help='name of the zeno sphcode log')
parser.add_argument('-allE',action='store_true',default=False,help='Plot all energy quantites (overrides other options)')
parser.add_argument('-Etot',action='store_true',default=False,help='Plot Etot (on 2nd y-axis)')
parser.add_argument('-Ekin',action='store_true',default=False,help='Plot Ekin')
parser.add_argument('-Epot',action='store_true',default=False,help='Plot Epot')
parser.add_argument('-Eint',action='store_true',default=False,help='Plot Eint (normalized to the max value with time)')
parser.add_argument('-Erad',action='store_true',default=False,help='Plot Erad')
#parser.add_argument('-allDot',action='store_true',default=False,help='Plot all energetic time derivatives (overrides other options)')
#parser.add_argument('-Udot',action='store_true',default=False,help='Plot Udot internal')
parser.add_argument('-fixErad',action='store_true',default=False,help='Fix the Erad and Etot budgeting due to a sign error (only needed for sphcode-1.3a runs)')
parser.add_argument('--density',action='store',help='Overplot density vs time from this file (normalized to the maximum density)')
parser.add_argument('--output',action='store',default=False,help='Specify the name of the output file (default is to change the log file suffix to .pdf)')
parser.add_argument('--savefig',action='store',type=str,default=False,help='Figure will be saved to this filename if given.')
parser.add_argument('--version',action='version',version='%(prog)s '+VERSION+' ('+VERSIONDATE+')')
args=parser.parse_args()

if args.allE:
  args.Etot=args.Ekin=args.Epot=args.Eint=args.Erad=True
elif not(args.Etot) and not(args.Ekin) and not(args.Epot) and not(args.Eint) and not(args.Erad):
  sys.stderr.write('uhhh, you didn\'t request anything to plot... try:\n')
  sys.stderr.write(sys.argv[0]+' --help\n')
  sys.stderr.write('to see your options.\n\n')
  sys.exit(-1)

infile=open(args.logfile,'r')

lhead=0
# read the meat of the data and write it out, continuing until the end
# this records: time, Nstep, freqmax, freqavg, Etot, Eint, Ekin, Epot, Erad,
#    |Jtot|, |Vcom|, and CPUtot
time=numpy.array([])
Nstep=numpy.array([])
freqmax=numpy.array([])
freqavg=numpy.array([])
Etot=numpy.array([])
Eint=numpy.array([])
Ekin=numpy.array([])
Epot=numpy.array([])
Erad=numpy.array([])
Jtot=numpy.array([])
Vcom=numpy.array([])
Cputot=numpy.array([])
while 1:
  tline=infile.readline()
  if not tline:
    break
  if re.search('time:',tline):
    # extract the exact time
    tline=tline.split()
    time=numpy.append(time,float(tline[1]))
    Nstep=numpy.append(Nstep,int(tline[3]))
  elif re.search('Etot',tline):
    # get the next line and add other information to the stack
    tline=infile.readline().split()
    Etot=numpy.append(Etot,float(tline[1]))
    Eint=numpy.append(Eint,float(tline[2]))
    Ekin=numpy.append(Ekin,float(tline[3]))
    Epot=numpy.append(Epot,float(tline[4]))
    Erad=numpy.append(Erad,float(tline[5]))
    Jtot=numpy.append(Jtot,float(tline[6]))
    Vcom=numpy.append(Vcom,float(tline[7]))

infile.close()

if args.density:
  rhoavg=numpy.array([])
  t=numpy.array([])
  if not(os.path.exists(args.density)):
    sys.stderr.write('ERROR: density file "'+args.density+'" does not exist. skipping.\n')
    args.density=False
  else: 
    infile=open(args.density,'r')
    for line in infile:
      if not(re.match("#",line)):
        t=numpy.append(t,float(line.split()[0]))
        rhoavg=numpy.append(rhoavg,float(line.split()[2]))
    infile.close()
    # normalize the density to the max value
    rhoavg=rhoavg/rhoavg.max()

# plot the energy quantities
if args.Ekin:
  plt.plot(time,Ekin,'--',label='E$_{kin}$')
if args.Eint:
  plt.plot(time,Eint/Eint.max(),'--',label='E$_{int}$/(E$_{int}$)$_{max}$')
if args.Epot:
  plt.plot(time,Epot,'-.',label='E$_{pot}$')
if args.fixErad:
  Etot=Etot-2*Erad
  Erad=-1*Erad
if args.Erad:
  plt.plot(time,Erad,':',label='E$_{rad}$')
if args.density:
  plt.plot(t,rhoavg,"-",label='mean(rho) / mean(rho)$_{max}$',color='green')
plt.minorticks_on()
plt.xlim(xmax=8)
plt.ylabel('Energy (Components) [simulation units]')
plt.xlabel('Time [simulation units]')
plt.legend(loc='upper left',frameon=False,fontsize='small')
if args.Etot:
  plt.twinx()
  plt.minorticks_on()
  plt.ylim(ymin=-1.45)
  plt.ylim(ymax=-1.3)
  plt.xlim(xmax=8)
  plt.plot(time,Etot,'-',color='red',label='E$_{tot}$')
  plt.ylabel('E$_{tot}$ [simulation units]')
  plt.legend(loc='upper right',frameon=False,fontsize='small')
plt.title(args.logfile+' - Energy')
if args.savefig:
  plt.savefig(args.savefig)
  print "Plot saved to: "+args.savefig
else:
  plt.show()
