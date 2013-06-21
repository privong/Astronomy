#!/usr/bin/python
#
# Make a list of unique images files in a tex file, get list of images in 
# that directory, and print out which aren't being used in that tex file.

import re,sys,os

suffix=['jpg','png','gif','pdf']

try: 
  texfile=open(sys.argv[1])
except:
  sys.stderr.write("Error, couldn't open "+sys.argv[1]+" for reading.\n")

imglist=[]
rmlist=[]

for line in texfile:
  if re.search('includegraphics',line):
    sline=line.split('\\includegraphics')
    n=len(sline)-1
    for i in range(1,n+1):
      img=sline[i].split(']{')[1].split('}')[0]
      if not(img in imglist): imglist.append(img)

for filename in os.listdir('.'):
  nomatch=True
  i=0
  while nomatch:
    if re.search(suffix[i],filename):
      nomatch=False
      if not(filename.split('\/')[-1] in imglist):
        if not(re.search(sys.argv[1].split('.tex')[0],filename.split('\/')[-1])):
          rmlist.append(filename.split('\/')[-1])
    i+=1
    if i>=len(suffix): break

if imglist:
  imglist.sort()
  sys.stderr.write(str(len(imglist))+" images found.\n")
  sys.stdout.write("Found images: ")
  for img in imglist:
    sys.stdout.write(img+", ")
  sys.stdout.write("\n\n")
else:
  sys.stderr.write("Found no images to be included in TeX file.\n")
if rmlist:
  sys.stdout.write("The unused images can be removed with this command:\n")
  sys.stdout.write("rm ")
  for img in rmlist:
    sys.stdout.write(img+' ')
  sys.stdout.write("\n\n")
else:
  sys.stderr.write("No unused images found.\n\n")
