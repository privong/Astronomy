pro HST_throughput,infile,FILTER=filter,SPECTRA=spectra,LFLUX=lflux

; integrate the total flux from a filter throughput mulitiplied by the SDSS spectrum
; the user provides the file containing the flux seen by the detector
; user inputs the continuum regions, used to fit a spline to the continuum, which is then subtracted to give the line-only. the integration over the line will hopefully shed some light on the amount of continuum which needs to be removed.

;sample command to run
; HST_throughput,'working/photometry/SDSS-f547m.dat',FILTER='FILTERS/f547m.dat',SPECTRA='../SDSS/1d_25/0560/1d/spSpec-52296-0560-520.txt'

;start out by making sure we've got all the routines we need
RESOLVE_ALL,/QUIET

readcol,infile,wave,flux,/SILENT

print,'Loaded ',infile

read,x1,PROMPT='Please enter the lower plot limit: '
read,x2,PROMPT='upper plot limit: '

window,0
wset,0
plot,wave,flux,xrange=[x1,x2],xtitle="Angstroms",ytitle="Flux",title=infile

; if we have it, load the SDSS spectra in a new window
if (keyword_set(SPECTRA)) then begin
  readcol,spectra,swave,sflux,SKIPLINE=2,/SILENT
  window,1
  wset,1
  plot,swave,sflux,xrange=[x1,x2],yrange=[-0.1*max(sflux[where(swave gt x1 AND swave lt x2)]),1.05*max(sflux[where(swave gt x1 AND swave lt x2)])],xtitle="Angstroms",ytitle="Flux",title="SDSS Spectra"
  wset,0
endif

; figure out how many continuum regions to use
read,cnum,PROMPT="How many continuum regions to use? "

if (cnum eq 1) then begin
  ;prompt user for continuum sections
  read,l1,PROMPT='1st Continuum section lower limit: '
  read,l2,PROMPT='1st Continuum section upper limit: '

  print,'Fitting continuum between ',l1,':',l2

  ; extract the continuum regions (from the SDSS spectra) to be fit with a spline
  fitwave=swave[where((swave GT l1 and swave lt l2))]
  fitflux=sflux[where((swave GT l1 and swave lt l2))]
endif else if (cnum eq 2) then begin

  ;prompt user for continuum sections
  read,l1,PROMPT='1st Continuum section lower limit: '
  read,l2,PROMPT='1st Continuum section upper limit: '
  read,l3,PROMPT='2nd Continuum section lower limit: '
  read,l4,PROMPT='2nd Continuum section upper limit: '

  print,'Fitting continuum between ',l1,':',l2,' and ',l3,':',l4

  ; extract the continuum regions (from the SDSS spectra) to be fit with a spline
  fitwave=swave[where((swave GT l1 and swave lt l2) or (swave GT l3 and swave lt l4))]
  fitflux=sflux[where((swave GT l1 and swave lt l2) or (swave GT l3 and swave lt l4))]
endif else if (cnum eq 3) then begin
;prompt user for continuum sections
  read,l1,PROMPT='1st Continuum section lower limit: '
  read,l2,PROMPT='1st Continuum section upper limit: '
  read,l3,PROMPT='2nd Continuum section lower limit: '
  read,l4,PROMPT='2nd Continuum section upper limit: '
  read,l5,PROMPT='3nd Continuum section lower limit: '
  read,l6,PROMPT='3nd Continuum section upper limit: '

  ; extract the continuum regions (from the SDSS spectra) to be fit with a spline
  fitwave=swave[where((swave GT l1 and swave lt l2) or (swave GT l3 and swave lt l4) or (swave GT l5 and swave LT l6))]
  fitflux=sflux[where((swave GT l1 and swave lt l2) or (swave GT l3 and swave lt l4) or (swave GT l5 and swave LT l6))]
endif

; fit a spline to the SDSS continuum
;continuum=spline(fitwave,fitflux,nwave)

; do a linear regression to the continuum region
linear=linfit(fitwave,fitflux,CHISQ=chi)

; compute the linear model of the continuum
contmodel=linear[0]+swave*linear[1]

print,'Continuum Region fit with a line of parameters: ',linear

; over plot the continuum fit to the SDSS spectrum
wset,1
oplot,swave,contmodel,linestyle=2
;now, subtract the continnuum from the overall curve:
lineflux=sflux-(linear[0]+swave*linear[1])
;plot continuum subtracted spectra only
oplot,swave,lineflux,linestyle=3


; now, load the HST filter curve, interpolate, and multiply by the continuum fit
readcol,filter,rownum,hstwave,hstthrough,SKIPLINE=5
hstwave2=interpol(indgen(n_elements(hstthrough)),hstwave,swave)
hstthrough2=interpolate(hstthrough,hstwave2)
filtcont=hstthrough2*contmodel
;window,2
;plot,swave,hstthrough2
;oplot,hstwave,hstthrough-0.03,linestyle=2
wset,0
plot,wave,flux,xrange=[x1,x2],xtitle="Angstroms",ytitle="Flux",title=infile
oplot,swave,filtcont,linestyle=2
oplot,swave,flux-filtcont+2,linestyle=3

;integrate total curve
tflux=int_tabulated(wave,flux)

;integrate line flux
lflux=int_tabulated(wave,flux-filtcont)

;integrate continuum fit
cflux=int_tabulated(swave,filtcont)

print,'Total integrated flux: ',tflux
print,'Integrated (fit) continuum fit: ',cflux
print,'Integrated residual flux: ',lflux

;print,'Continuum + Integrated: ',cflux+lflux

; fit a gaussian to the line
;gaussval=gaussfit(nwave,lineflux,coeffs,NTERMS=3)

;print,'Gaussian Fit Coefficients:'
;print,'Amplitude: ',coeffs[0]
;print,'Center: ',coeffs[1]
;print,'Width: ',coeffs[2]

;oplot,wave,gaussian(wave,coeffs),linestyle=4

;also, plot this gaussian in a new window
;window,2
;wset,2
;plot,wave,gaussian(wave,coeffs),xrange=[l2,l3]
;wset,0

;flflux1=int_tabulated(wave,gaussian(wave,coeffs))

;print,'Fit Line (narrow) Flux: ',flflux1

if (keyword_set(LFLUX)) then  begin
  read,l8,PROMPT="Lower Line Limit:"
  read,l9,PROMPT="Upper Line Limit:"
  print,'Line flux: ',int_tabulated(swave[where(swave lt l9 and swave gt l8)],(flux-filtcont)[where(swave lt l9 and swave gt l8)])
endif

; if we've been given a filter curve file, integrate the response over wavelength to get the converstion from flux to f_lambda
if (keyword_set(FILTER)) then begin
  readcol,filter,row,fwave,fthru,/SILENT

  ;plot the filter curve on the data just to see
  oplot,fwave,fthru*10,linestyle=8

  ; now, integrate over the filter response
  tthru=int_tabulated(fwave,fthru)

  print,'Integrated throughput of the filter: ',tthru
endif

end
