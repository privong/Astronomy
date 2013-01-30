# Idkit_moms.py
#


def Idkit_moms(cube,moms=[0],exclude=[0],chrange=[0],center=[0],pixrange=0):
  """
  Take an input data cube, calculate XY, XV, and VY images using ia.immoment
 
  Inputs:
    cube	- input data cube
    moms	- [optional] which moments to compute
    exclude	- [optional] range of pixel values to exclude
    chrange	- [optional] requested channel range 
    center	- [optional] XY center position of the image
    pixrange	- [optional] pixel range on either side of the center to use
 
  Outputs CASA images using the cube root name, with moment number and
 	projection appended to the image.
        e.g.: cube_XV-mom0.image	- XV moment 0 CASA image
  """

  # list of projections we want
  projs=('spectral','ra','dec')
  suffix=('_XY','_VY','_XV')

  # delete any '.fits' or '.image' from the cube name
  croot=cube.rsplit('.',1)[0]

  # check to see if we're limited in X and Y coordinates
  sbox=''
  schrange=''
  se=[]
  if (len(center)==2 and pixrange):
    # create a box (with the center pixel at the center of the resulting image
    sbox="%i,%i,%i,%i" % (center[0]-pixrange,center[1]-pixrange,center[0]+pixrange,center[1]+pixrange)
  # check to see if we have limits on the channel ranges too
  if len(chrange)==2:
    schrange="%i~%i" % (chrange[0],chrange[1])
  # are we excluding pixels?
  if len(exclude)==2:
    se=exclude
  elif exclude[0]:
    se=[-1*exclude[0],exclude[0]]

  # now compute the image moments for all projections
  for i in range(len(projs)):
    for j in range(len(moms)):
      imname=croot+suffix[i]+'_mom'+str(moms[j])+'.image'
      if moms[j]:
        immoments(imagename=cube,moments=moms[j],axis=projs[i],box=sbox,chans=schrange,outfile=imname)
      else:
        immoments(imagename=cube,moments=moms[j],axis=projs[i],box=sbox,chans=schrange,excludepix=se,outfile=imname)
      # uncomment the following line to export FITS files
      # exportfits(imagename=imname,fitsimage=croot+suffix[i]+'_mom'+str(moms[j])+'.fits',optical=True,dropstokes=True,velocity=True)

  return 0
