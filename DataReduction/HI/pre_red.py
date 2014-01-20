# Pre-reduction script to make general plots prior to reducing data
# 
# Version 0.0.1   - 24 June 2010
# George Privon gcp8y@virginia.edu

# Required arguments:
# msfile	string, enter the ms file containing the observations
# primcal	tuple, Field ID of the primary calibrator
# scals		tuple, Field IDs of the seconday calibrators (must be input as a tuple)
# sources	tuple, Field IDs of the target sources (must be input as a tuple)
# flag		Flag data? (defaults to no)

# Optional Arguments
# quacklen	int, duration (in seconds) of quack flagging for scan starts (if flag=1)
# badants	tuple, antennas which need to be flagged for the whole 
#		observation (determine from observing log)

def pre_red(msfile,primcal,scals,sources,flag=0,quacklen=10,badants=-1):

  # flag consistently bad antennas
  if badants != -1:
    flagdata(vis=msfile,mode='manualflag',selectdata=True,antenna=badants)

  # list observation information
#  listobs(vis=msfile,verbose=True)

  # plot antenna locations
  figure=msfile+'-ant_loc.png'
#  plotants(vis=msfile,figfile=figure)

  # plot uv coverage for the calibrators, and the source(s)
  for i in primcal:
    figure=msfile+'-field'+str(primcal)+'-uvcov.png'
#    plotxy(vis=msfile,xaxis='u',yaxis='v',field=str(primcal),averagemode='vector',timebin='10',width='all',figfile=figure)

  for i in scals:
    figure=msfile+'-field'+str(i)+'-uvcov.png'
#    plotxy(vis=msfile,xaxis='u',yaxis='v',field=str(i),averagemode='vector',timebin='10',width='all',figfile=figure)

  for i in sources:
    figure=msfile+'-field'+str(i)+'-uvcov.png'
#    plotxy(vis=msfile,xaxis='u',yaxis='v',field=str(i),averagemode='vector',timebin='10',width='all',figfile=figure)

#  if flag:
    # Flag autocorrelations, shadowing, and quack
#    flagautocorr(vis=msfile)	# autocorrelations
#    flagdata(vis=msfile,mode='shadow')	# flag for shadowed antennas
#    flagdata(vis=msfile,mode='quack',quackinterval=quacklen) # quack flagging

  return 0



# TODO
#
# - Can we use the CASA toolkit to search a MS and determine which fields are the calibrators and which are the sources, then iterate over them so the user doesn't have to specify it when calling?
