# WSRT-HI.py
#
# George C. Privon
# gcp8y@virginia.edu

# TO DO:
# 1. intelligent concatenating. Be sure we only concatenate two parts of the same observation.. e.g., "T0" and "T1"
# 2. Self-discovery of measurement sets.
#	2b. with auto-identification of the source and purpose of that obs?

import os
import string

def WSRTHI(viz, source, refant="RT4", flagRT5=True, FLAGGING=True,
            GENCAL=True, APPLYCAL=True, MSCAT=False, IMAGE=False, FSMO=1,
            CONTSUB=False, CONTSUBIMG=False):
    """
    WSRTHI() - Pipeline HI reduction for WSRT observations.


    viz: array of .MS files to use
    source: Name of the source
    refant (OPTIONAL, default: RT4): reference antenna to use for gaincal
    flagRT5 (OPTIONAL, default: True): flag antenna RT5 (being used in apertif testing)
    FLAGGING (OPTIONAL, default: True): do the flagging portion of the script?
    GENCAL (OPTIONAL, default: True): generate calibration tables?
    APPLYCAL (OPTIONAL, default: True): apply calibration to the data?
    MSCAT (OPTIONAL, default: False): concatenate source MS?
    IMAGE (OPTIONAL, default: False): invert and clean the image?
    FSMO (OPTIONAL, default: 1): # of adjacent channels to avg together when imaging
    CONTSUB (OPTIONAL, default: False): QND UV continuum subtraction.
    CONTSUBIMG (OPTIONAL, default: False): QND imaging of continuum subtracted and continuum
		data.
    """

    # be sure we have MS inputs. If they're UVFITS, convert them
    for i in range(len(viz)):
        tvis = string.rsplit(viz[i],'.',1)
        if (tvis[1]=="UVF"):
            if not(os.path.isdir('./'+tvis[0]+'.ms')) or not(os.path.isdir('./'+tvis[0]+'.MS')):
                print "Importing UVFITS file "+viz[i]
                # MS file hasn't been imported yet, so do it
                importuvfits(fitsfile=viz[i], vis=tvis[0]+'.ms')
                # now need to edit the "ANTENNAS" table to copy the station name to the "name" column.
                print "Fixing WSRT antenna names..."
                tb.open(tvis[0]+'.ms/ANTENNA', nomodify=False)
                antenna=tb.getcol("STATION")
                tb.putcol("NAME", antenna)
                tb.close()
            viz[i]=tvis[0]+'.ms'

    print "Processing WSRT observation contained in MS files: "
    for vis in viz:
        print vis

    if (FLAGGING):
        print "---- Initial Flagging ----"

        # start by flagging autocorrelations
        print "Flagging autocorrelations..."
        for vis in viz:
            flagdata(vis=vis, mode='manual', autocorr=True)

        print "Flagging shadowed antennas..."
        for vis in viz:
            flagdata(vis=vis, mode='shadow')

        if (flagRT5):
            print "Flagging antenna RT5 (APERTIF testing)"
            for vis in viz:
                flagdata(vis=vis, flagbackup=True, mode="manual",
                            antenna="RT5")

        print "Flagging channels on the edges of the bandpass."
        for vis in viz:
            flagdata(vis=vis, flagbackup=True, mode="manual",
                        spw="0:0~5;850~1023")

    if (GENCAL):
        print "---- Generating Calibration Tables ----"


        # set the intitial flux density scale
        print "Setting flux density scale"
        setjyout = setjy(vis=viz[0], scalebychan=True, usescratch=True)
        print "Flux of "+setjyout['0']['fieldName']+" set to "
                +str(setjyout['0']['0']['fluxd'][0])
        # name our calibration tables
        calname = setjyout['0']['fieldName']
        caltable=(calname+".gcal.01", calname+".bcal.01",
                    calname+".gcal-int_p.02", calname+".gcal-inf_p.02",
                    calname+".gcal-inf_ap.03")

        # integration based phase calibration
        gaincal(vis=viz[0], caltable=caltable[0], field="", spw="", 
                selectdata=False, timerange="", uvrange="", antenna="", 
                scan="", msselect="", solint="int", combine="", preavg=-1.0,
                refant=refant, minblperant=2, minsnr=2.0, solnorm=False,
                gaintype="G", smodel=[], calmode="p", append=False,
                splinetime=3600.0, npointaver=3, phasewrap=180.0,
                gaintable=[''], gainfield=[''], interp=[''], spwmap=[], 
                gaincurve=False, opacity=0.0, parang=False)
        # save a plot of the results
        plotcal(caltable=caltable[0], xaxis="time", yaxis="phase", poln="",
                field="", antenna="", spw="", timerange="", subplot=111,
                overplot=False, clearpanel="Auto", iteration="", plotrange=[],
                showflags=False, plotsymbol="o", plotcolor="blue",
                markersize=5.0, fontsize=10.0, showgui=False,
                figfile=calname+".gcal.01-phase.png")

        # bandpass calibration
        bandpass(vis=viz[0], caltable=caltable[1], field="", spw="",
                    selectdata=False, timerange="", uvrange="", antenna="",
                    scan="", msselect="", solint="inf", combine="",
                    refant=refant, minblperant=2, minsnr=2.0, solnorm=False,
                    bandtype="B", append=False, fillgaps=0, degamp=3,
                    degphase=3, visnorm=False, maskcenter=0, maskedge=5,
                    gaintable=caltable[0], gainfield=[''], interp="nearest",
                    spwmap=[], gaincurve=False, opacity=0.0, parang=False)

        # plot bandpass solution
        plotcal(caltable=caltable[1], xaxis="chan", yaxis="phase", poln="",
                field="", antenna="", spw="", timerange="", subplot=441,
                overplot=False, clearpanel="Auto", iteration="antenna",
                plotrange=[], showflags=False, plotsymbol="o",
                plotcolor="blue", markersize=5.0, fontsize=5.5, showgui=False,
                figfile=calname+".bcal.01-phase.png")
        plotcal(caltable=caltable[1], xaxis="chan", yaxis="amp", poln="",
                field="", antenna="", spw="", timerange="", subplot=441,
                overplot=False, clearpanel="Auto", iteration="antenna",
                plotrange=[], showflags=False, plotsymbol="o",
                plotcolor="blue", markersize=5.0, fontsize=5.5, showgui=False,
                figfile=calname+".bcal.01-amp.png")

        # integration based phase solution
        gaincal(vis=viz[0], caltable=caltable[2], field="", spw="",
                selectdata=False, timerange="", uvrange="", antenna="",
                scan="", msselect="", solint="int", combine="", preavg=-1.0,
                refant=refant, minblperant=2, minsnr=2.0, solnorm=False,
                gaintype="G", smodel=[], calmode="p", append=False,
                splinetime=3600.0, npointaver=3, phasewrap=180.0,
                gaintable=caltable[1], gainfield=[''], interp="nearest",
                spwmap=[], gaincurve=False, opacity=0.0, parang=False)

        # scan based phase solution
        gaincal(vis=viz[0], caltable=caltable[3], field="", spw="",
                selectdata=False, timerange="", uvrange="", antenna="",
                scan="", msselect="", solint="inf", combine="", preavg=-1.0,
                refant=refant, minblperant=2, minsnr=2.0, solnorm=False,
                gaintype="G", smodel=[], calmode="p", append=False,
                splinetime=3600.0, npointaver=3, phasewrap=180.0,
                gaintable=caltable[1], gainfield=[''], interp="nearest",
                spwmap=[], gaincurve=False, opacity=0.0, parang=False)

        # amplitude and phase scan based solution
        gaincal(vis=viz[0], caltable=caltable[4], field="", spw="",
                selectdata=False, timerange="", uvrange="", antenna="",
                scan="", msselect="", solint="inf", combine="", preavg=-1.0,
                refant=refant, minblperant=2, minsnr=2.0, solnorm=False,
                gaintype="G", smodel=[], calmode="ap", append=False,
                splinetime=3600.0, npointaver=3, phasewrap=180.0,
                gaintable=[caltable[1], caltable[2]], gainfield=[''],
                interp=["nearest", "nearest"], spwmap=[], gaincurve=False,
                opacity=0.0, parang=False)

    if (APPLYCAL):
        print "---- Applying Calibration to the data ----"

        # apply to the primary calibrator
        applycal(vis=viz[0], field="", spw="", selectdata=False, timerange="",
                    uvrange="", antenna="", scan="", msselect="",
                    gaintable=[caltable[1], caltable[2], caltable[4]],
                    gainfield=[''], interp=['nearest',  'nearest',  'nearest'],
                    spwmap=[], gaincurve=False, opacity=0.0, parang=False,
                    calwt=True)

        # apply to the two MS for the target
        applycal(vis=viz[1], field="", spw="", selectdata=False, timerange="",
                    uvrange="", antenna="", scan="", msselect="",
                    gaintable=[caltable[1], caltable[3], caltable[4]],
                    gainfield=[''], interp=['nearest',  'nearest',  'nearest'],
                    spwmap=[], gaincurve=False, opacity=0.0, parang=False,
                    calwt=True)
        applycal(vis=viz[2], field="", spw="", selectdata=False, timerange="",
                    uvrange="", antenna="", scan="", msselect="",
                    gaintable=[caltable[1], caltable[3], caltable[4]],
                    gainfield=[''], interp=['nearest',  'nearest',  'nearest'],
                    spwmap=[], gaincurve=False, opacity=0.0, parang=False,
                    calwt=True)

        print "Finished applying calibrations to the raw data."

    # if requested, combine the two MS sets
    if (MSCAT):
        print "---- Concatenating Calibrated Measurement Sets ----"
        concat(vis=[viz[1], viz[2]], concatvis=source+'.ms')
        nvis=source+'.ms'
    else:
        nvis=viz[1]

    # image the data cube
    if (IMAGE):
        if (os.path.isdir('./'+source+'.ms')):
            print "---- Imaging concatenated, calibrated measurement set ----"
        else:
            print "---- Imaging calibrated data set ----"
        clean(vis=nvis, imagename=source, selectdata=False, mode='channel',
                imsize=[256, 256], cell='6arcsec', niter=100000,
                threshold='4mJy', interactive=False, multiscale=[])

    # do a generic continuum subtraction
    if (CONTSUB):
        print "---- Performing Continuum Subtraction ----"
        uvcontsub(vis=nvis, fitspw="0:50~375;650~800", fitorder=0,
                    want_cont=True)
    nvis=source+'.ms'
    if (CONTSUBIMG):
        print "---- Imaging Continuum Subtracted Data ----"
        # image the continuum subtracted data
        clean(vis=nvis+'.contsub', imagename=source+'.contsub',
                selectdata=False, mode='channel', interpolation='nearest',
                imsize=[256, 256], cell='6arcsec', niter=1000000, 
                threshold='4mJy', interactive=False, multiscale=[], width=FSMO)
        # and make a continuum image
        clean(vis=nvis+'.cont', imagename=source+'.cont', selectdata=False,
                mode='mfs', imsize=[256, 256], cell='6arcsec', niter=1000000,
                threshold='4mJy', interactive=False, multiscale=[])

    print "The following operations were performed on the data:"
    print "Flagging: "+str(FLAGGING)
    if (FLAGGING):
        print "\tRT5: "+str(flagRT5)
    print "Generate Calibration Tables: "+str(GENCAL)
    print "Apply calibration to the data: "+str(APPLYCAL)
    print "Measurement set concatenation: "+str(MSCAT)
    print "Dataset imaged: "+str(IMAGE)
    print "Continuum subtracted: "+str(CONTSUB)
    print "Continuum subtracted data imaged: "+str(CONTSUBIMG)+" and smoothed by +"+str(FSMO)+" channels."


    return 0
