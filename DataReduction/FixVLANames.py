# FixVLANames.py
#
# Prefix antenna NAME column with "VA"

import os
import string

def FixVLANames(vis):

  print "Changing antenna NAME column to modified name column for %s." % (vis)
  newname=[]
  # open the table of antenna names
  tb.open(vis+'/ANTENNA',nomodify=False)
  antenna=tb.getcol("NAME")
  for ant in antenna:
    ant="VA"+ant
    newname.append(ant)
  tb.putcol("NAME",newname)
  tb.close

  return 0
