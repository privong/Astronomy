#!/sw/bin/python2.7
#
# Make RGB frames using 2 input images
# DM+stars (red channel), stars (green), and stars (blue)

import argparse,os

parser=argparse.ArgumentParser()
parser.add_argument('pgms',type=str,nargs='+')
parser.add_argument('--overlay',type=str,action='store',default=False,help='Specify an overlay image to be added to the movie.')
parser.add_argument('--nframes',type=int,action='store',default=2,help='Number of frames to combine into a color image (default: 2)')
parser.add_argument('--overlayframes',type=int,action='store',default=150,help='Number of frames to display the overlay. (default=150)')
args=parser.parse_args()

for i in range(len(args.pgms)/2):
  if args.nframes==2:
    os.system('convert %s %s %s -combine %s' % (args.pgms[i*2],args.pgms[i*2+1],args.pgms[i*2+1],str(i).zfill(5)+'.ppm'))
  elif args.nframes==3:
    os.system('convert %s %s %s -combine %s' % (args.pgms[i*3],args.pgms[i*3+1],args.pgms[i*3+2],str(i).zfill(5)+'.ppm'))
  if args.overlay:
    if i<args.overlayframes:
      os.system('convert %s %s -layers flatten %s' % (str(i).zfill(5)+'.ppm',args.overlay,str(i).zfill(5)+'.ppm'))
    if (i>args.overlayframes) and (i<(args.overlayframes+20)):
      os.system('composite '+str(i).zfill(5)+'.ppm -dissolve '+str(100-(i-args.overlayframes)/20.)+'% '+args.overlay+' '+str(i).zfill(5)+'.ppm')
