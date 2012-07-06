#!/sw/bin/python2.6
#
# Generate images from zeno sph/treecode simulations for making movies
#
# George Privon, gcp8y@virginia.edu, 06 July 2012
#
# you can turn this into a movie with something like:
# ffmpeg -r 120 -i s001_00%02d-gdisk.pgm test.mp4
#
# Can also make a 4 paneled image. 3 panels for the individual components, 1
# panel for the 3 color image of the simulations. --- Need to figure out how to
# do this. maybe with ImageMagik?

import sys,re,argparse,os,glob

VERSION='0.1a'
VERSIONDATE='06 July 2012'

# set up command line arguments
parser=argparse.ArgumentParser(description='Generate pgm images of subsets of a zeno N-body snapshot. Assumes first file has BodyType information in it.')
parser.add_argument('snaps',type=str,nargs='+',help='snapshots to image')
parser.add_argument('-DM',action='store_true',default=False,help='Select dark matter particles')
parser.add_argument('-sdisk',action='store_true',default=False,help='Select stellar disk particles')
parser.add_argument('-sbulge',action='store_true',default=False,help='Select stellar bulge particles')
parser.add_argument('-gdisk',action='store_true',default=False,help='Select gas disk particles')
parser.add_argument('--viewfile=',action='store',default=False,help='Specify a view file to rotate the snapshots prior to generating the images. [NOT YET IMPLEMENTED].')
parser.add_argument('--version',action='version',version='%(prog)s '+VERSION+' ('+VERSIONDATE+')')
args=parser.parse_args()

#if args.viewfile:
#  sys.stderr.write('A viewfile was provided. Note that this is not yet implemented, so it will not be applied to the data.\n\n')

type=[]
multiple=-1	# are there multiple particles to plot in this image?
suffix=''
if args.DM:
  sys.stderr.write('Imaging the dark matter.\n')
  multiple+=1
  type.append('0x41')
  suffix=suffix+'-dm'
if args.sdisk:
  sys.stderr.write('Imaging the stellar disk.\n')
  multiple+=1
  type.append('0x44')
  suffix=suffix+'-sdisk'
if args.sbulge:
  sys.stderr.write('Imaging the stellar bulge.\n')
  multiple+=1
  type.append('0x42')
  suffix=suffix+'-sbulge'
if args.gdisk:
  sys.stderr.write('Imaging the gas disk.\n')
  multiple+=1
  type.append('0x66')
  suffix=suffix+'-gdisk'

if multiple==-1:
  sys.stderr.write('Ummmm... you need to pick at least one type of particle to make an image of...\n\n')
  sys.exit(-1)

# generate the sieve argument
sieve='type=='+type[0]
if multiple>0:
  sieve=''
  for h in type:
    if not(sieve==''):
      sieve=sieve+' || type=='+h
    else:
      sieve='type=='+h

snaps=args.snaps
# the first file is special, since it has the bodytype info!
for snap in snaps:
  # generate an output file name
  oname=snap.split('.dat')[0]+suffix+'.pgm'

  # make sure our temp files don't already exist
  if os.path.exists('tempsnap.dat'):
    os.remove('tempsnap.dat')
  if os.path.exists('tmpimg.dat'):
    os.remove('tmpimg.dat')

  # now generate the snapshots
  os.system('csf '+snaps[0]+' ./tempsnap.dat')
  os.system('csf '+snap+' ./tempsnap.dat append=t')
  os.system('snapcollect tempsnap.dat - | snapsift - - sieve="'+sieve+'" | snapset - - produce=BodyType,Uinternal,Mass type=0x60 uint=0.00001 m=0.00001 z=0 | sphcode_u - tmpimg.dat tstop=0 outputs=Position,SmoothLength')
  os.system('snapset tmpimg.dat - aux=0.0001 produce=Aux | snapsmooth - '+oname+' value=bright threedim=false')

  # delete our temp files
  os.remove('tmpimg.dat')
  os.remove('tempsnap.dat')
