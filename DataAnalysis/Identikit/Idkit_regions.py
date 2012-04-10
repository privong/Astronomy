# Idkit_regions.py

def Idkit_regions(imagelist,poslist):
  """
  Take an input data file of positions and velocities, generate CASA region
  XML files to overlay on the moment maps in the casa viewer

  Inputs:
    - imagelist	- list/tuple with the images listed in order (XY, XV, VY)
    - poslist	- file with tabulation of positions and velocities for 
		dynamical tracers

  poslist is of the form (tab-separated):
  RA    Dec     code    vcenter [voff1] [voff2]
   - code designates what type of marker it is, and what color will be used:
        g1      - center of galaxy 1 (cyan)
        g2      - center of galaxy 2 (magenta)
        s       - star cluster (yellow)
   - voff1 is a symmetric range in the velocity if no voff2 (total range/2)
   - voff1&2 are lower and upper velocity values (respectively)
  (all velocities are assumed to be in the optical defn)

  Outputs
   _XY.xml      - regions for XY projection
   _XV.xml      - regions for XV projection
   _VY.xml      - regions for VY projection
  """
  # read in the coordinate information from the position list
  posfile=open(poslist,'r')
  pos=[]	# list of dictionaries
  for obj in posfile:
    # remove newlines
    obj=obj.split('\n')[0]
    objs=obj.split('\t')
    if len(objs)==5:
      # symmetric velocity constraints
      pos.append({"RA":objs[0],"Dec":objs[1],"code":objs[2],"vel":1,"vcen":float(objs[3]),"vlow":(float(objs[3])-float(objs[4])),"vhigh":(float(objs[3])+float(objs[4]))})
    elif len(objs)==3:
      # no velocity constraints, plot positions only
      pos.append({"RA":objs[0],"Dec":objs[1],"code":objs[2],"vel":0})
    elif len(objs)==6:
      # have asymmetric velocity constraints
      pos.append({"RA":objs[0],"Dec":objs[1],"code":objs[2],"vel":1,"vcen":float(objs[3]),"vlow":float(objs[4]),"vhigh":float(objs[5])})
    else:
      # what were they thinking?
      print "Skipping invalid line: "
      print obj
  posfile.close()

  print pos

  # read in the list of projections we have and make region files for all
  # (this doesn't assume images are the same size, scale, etc)
  for proj in imagelist:
    proot=proj.rsplit('.',1)[0]
    # open the projection and get the coordinate system
    ia.open(proj)
    coords=ia.coordsys()
    # figure out which projection we're looking at
    if re.search("XY",proj):
      # sky plane projection, XML file of RA and Dec
      print "Found sky plane projection (XY)"
      outfile=open(proot+'.xml','w')
      Idkit_XMLheader(outfile)
      for obj in pos:
	# loop over objects in memory, write to an xml file
        Idkit_XMLobj(coords,outfile,'XY',obj)
      Idkit_XMLfooter(outfile)
      outfile.close()
    elif re.search("XV",proj):
      # velocity vs RA
      print "Found PV diagram (XV)"
      outfile=open(proot+'.xml','w')
      Idkit_XMLheader(outfile)
      for obj in pos:
        # loop over objects in memory, write to an xml file
	if obj['vel']!=0:
          Idkit_XMLobj(coords,outfile,'XV',obj)
      Idkit_XMLfooter(outfile)
      outfile.close()
    elif re.search("VY",proj):
      # Dec vs velocity
      print "Found PV diagram (VY)"
      outfile=open(proot+'.xml','w')
      Idkit_XMLheader(outfile)
      for obj in pos:
        # loop over objects in memory, write to an xml file
	if obj['vel']!=0:
          Idkit_XMLobj(coords,outfile,'VY',obj)
      Idkit_XMLfooter(outfile)
      outfile.close()
    else:
      print "ERROR: unknown projection type for file "+proj+". Ignoring and moving to next file."
    ia.close()
  

  return 0

# Convert to decimal RA
def decRA(RA):
  RAs=RA.split(':')
  return 15.*(float(RAs[0])+float(RAs[1])/60.+float(RAs[2])/3600.)

# Convert to decimal Dec
def decDec(Dec):
  Decs=Dec.split(':')
  if re.search('-',Decs[0]):
    # we're at negative Dec
    return float(Decs[0])-float(Decs[1])/60.-float(Decs[2])/3600.
  else:
    # positive Dec
    return float(Decs[0])+float(Decs[1])/60.+float(Decs[2])/3600.

# write XML file header
def Idkit_XMLheader(outfile):
  outfile.write('<casaviewer-shapes version="1.0" >\n <shape-options>\n')
  return 0

# write the XML for a specific region
def Idkit_XMLobj(coords,outfile,proj,obj):
  outfile.write('  <shape>\n')

  # select the appropriate color and label for this object
  label=obj['code']
  if obj['code']=='g1':
    color='cyan'
  elif obj['code']=='g2':
    color='magenta'
  elif obj['code']=='s':
    color='yellow'
  else:
    sys.stderr.write('ERROR: unknown object code. Coloring this object red.\n')
    color='red'

  # these lines are common to all projections
  outfile.write('   <field type="string" name="line_color" >'+color+'</field>\n')
  outfile.write('   <field type="double" name="line_width" >1</field>\n')
  outfile.write('   <field type="string" name="line_style" >solid</field>\n')
#  outfile.write('   <field type="string" name="text" >'+label+'</field>\n')
  outfile.write('   <field type="string" name="text_color" >'+color+'</field>\n')
  outfile.write('   <field type="string" name="text_font" >Nimbus Roman No9 L</field>\n')
  outfile.write('   <field type="int" name="text_size" >11</field>\n')
  outfile.write('   <field type="bool" name="text_italic" >0</field>\n')
  outfile.write('   <field type="bool" name="text_bold" >0</field>\n')
  outfile.write('   <field type="bool" name="linethrough" >0</field>\n')
  outfile.write('   <field type="string" name="ltcolor" >red</field>\n')
  outfile.write('   <field type="double" name="ltwidth" >1</field>\n')
  outfile.write('   <field type="string" name="ltstyle" >solid</field>\n')

  if proj=='XY':
    # we can write out coordinates in RA/Dec
    outfile.write('   <field type="bool" name="isworld" >1</field>\n')
    outfile.write('   <field type="string" name="worldsys" >J2000</field>\n')
    outfile.write('   <field type="doubleArray" name="coordinates" >\n')
    outfile.write('    <array shape="3" >\n')
    outfile.write('     <val>'+str(decRA(obj['RA']))+'</val>\n')
    outfile.write('     <val>'+str(decDec(obj['Dec']))+'</val>\n')
    outfile.write('     <val>10</val>\n')
    outfile.write('    </array>\n')
    outfile.write('   </field>\n')
    outfile.write('   <field type="record" name="options" >\n')
    outfile.write('    <field type="stringArray" name="0" >\n')
    outfile.write('     <array shape="1" >\n')
    outfile.write('      <val>cross</val>\n')
    outfile.write('     </array>\n')
    outfile.write('    </field>\n')
    outfile.write('   </field>\n')
    outfile.write('   <field type="string" name="type" >type_marker</field>\n')
  elif proj=='XV':
    # get the RA and velocity coordinates
    (pRA,pDec,pVel1,pStokes)=coords.topixel([obj['RA'],'.'.join(obj['Dec'].split(':')),coords.velocitytofrequency(value=obj['vlow'],doppler='optical',velunit='km/s'),'I'])['numeric']
    pVel2=coords.topixel([obj['RA'],'.'.join(obj['Dec'].split(':')),coords.velocitytofrequency(value=obj['vhigh'],doppler='optical',velunit='km/s'),'I'])['numeric'][2]
    outfile.write('   <field type="bool" name="isworld" >0</field>\n')
    outfile.write('   <field type="doubleArray" name="coordinates" >\n')
    outfile.write('    <array shape="5" >\n')
    # write out the (X,V) pixel coordinates for each end of the bar
    outfile.write('     <val>'+str(pRA)+'</val>\n')
    outfile.write('     <val>'+str(pVel1)+'</val>\n')
    outfile.write('     <val>'+str(pRA)+'</val>\n')
    outfile.write('     <val>'+str(pVel2)+'</val>\n')
    outfile.write('     <val>0</val>\n')
    outfile.write('    </array>\n')
    outfile.write('  </field>')
    outfile.write('   <field type="record" name="options" >\n')
    outfile.write('    <field type="bool" name="0" >0</field>\n')
    outfile.write('    <field type="bool" name="1" >0</field>\n')
    outfile.write('    <field type="string" name="2" >filled double v</field>\n')
    outfile.write('    <field type="string" name="3" >filled double v</field>\n')
    outfile.write('   </field>\n')
    outfile.write('   <field type="string" name="type" >type_line</field>\n')
  elif proj=='VY':
    # drop the RA coordinate
    (pRA,pDec,pVel1,pStokes)=coords.topixel([obj['RA'],'.'.join(obj['Dec'].split(':')),coords.velocitytofrequency(value=obj['vlow'],doppler='optical',velunit='km/s'),'I'])['numeric']
    pVel2=coords.topixel([obj['RA'],'.'.join(obj['Dec'].split(':')),coords.velocitytofrequency(value=obj['vhigh'],doppler='optical',velunit='km/s'),'I'])['numeric'][2]
    print (pVel1,pVel2)
    outfile.write('   <field type="bool" name="isworld" >0</field>\n')
    outfile.write('   <field type="doubleArray" name="coordinates" >\n')
    outfile.write('    <array shape="5" >\n')
    # write out the (X,V) pixel coordinates for each end of the bar
    outfile.write('     <val>'+str(pVel1)+'</val>\n')
    outfile.write('     <val>'+str(pDec)+'</val>\n')
    outfile.write('     <val>'+str(pVel2)+'</val>\n')
    outfile.write('     <val>'+str(pDec)+'</val>\n')
    outfile.write('     <val>0</val>\n')
    outfile.write('    </array>\n')
    outfile.write('  </field>')
    outfile.write('   <field type="record" name="options" >\n')
    outfile.write('    <field type="bool" name="0" >0</field>\n')
    outfile.write('    <field type="bool" name="1" >0</field>\n')
    outfile.write('    <field type="string" name="2" >filled double v</field>\n')
    outfile.write('    <field type="string" name="3" >filled double v</field>\n')
    outfile.write('   </field>\n')
    outfile.write('   <field type="string" name="type" >type_line</field>\n')
  outfile.write('  </shape>\n')
  
  return 0


# write XML file footer
def Idkit_XMLfooter(outfile):
  outfile.write(' </shape-options>\n</casaviewer-shapes>\n')
  return 0
