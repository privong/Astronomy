#!/usr/bin/python

# merge rgb images into single frames and write them out sequentially so 
# they can be combined into a movie

import argparse,os

parser=argparse.ArgumentParser()
parser.add_argument('pgms',type=str,nargs='+')
parser.add_argument('--overlay',type=str,action='store',default=False,help='Specify an overlay image to be added to the movie.')
parser.add_argument('--overlayframes',type=int,action='store',default=150,help='Number of frames to display the overlay. (default=150)')
args=parser.parse_args()

for i in range(len(args.pgms)/3):
  os.system('convert %s %s %s -combine %s' % (args.pgms[i*3+2],args.pgms[i*3+1],args.pgms[i*3],str(i).zfill(5)+'.ppm'))
  if args.overlay:
    if i<args.overlayframes:
      os.system('convert -page %s -page %s -layers flatten %s' % (str(i).zfill(5)+'.ppm',args.overlay,str(i).zfill(5)+'.ppm'))
