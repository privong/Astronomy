pro HST_line_contrib,filter,spectra,output

; load an SDSS spectrum and an HST filter curve. Gets the residual of the 
; combination of the SDSS spectrum + Filter curve with and without an emission
; line. The line is fit in the SDSS spectrum by a gaussian and removed in this 
; script

; Last modified: 22 September 2008 by George Privon

; read HST filter curve info
; wavelength in angstroms
readcol,filter,rownum,hstwave,hstthrough,SKIPLINE=5

;read the SDSS spectra
; wavelength is in angstroms
; flux is in 10^-17 erg cm-2 s-1 A-1
readcol,spectra,sdsswave,sdssflux,SKIPLINE=2

; interpolate filter curve to the SDSS spectrum grid
hstwave2=interpol(indgen(n_elements(hstthrough)),hstwave,sdsswave)
hstthrough2=interpolate(hstthrough,hstwave2)

; multiply the SDSS spectrum by the (interpolated) HST filter curve
out=hstthrough2
out=hstthrough2*sdssflux

; now, fit a gaussian to the emission line in the spectrum
gaussval=gaussfit(sdsswave[where (sdsswave GT 6650 AND sdsswave lt 6800)],sdssflux[where (sdsswave GT 6650 and sdsswave lt 6800)],coeffs,NTERMS=4,ESTIMATES=[37.,6691.,12.,87.])

print,coeffs

gaussval=gaussval-coeffs[3]

; now subtract this fit from the data
sclean=sdssflux[where (sdsswave GT 6650 AND sdsswave lt 6800)]-gaussval

window,0
plot,sdsswave[where (sdsswave GT 6650 AND sdsswave lt 6800)],sclean,xrange=[6600,6850]
oplot,sdsswave,sdssflux-50
oplot,sdsswave[where (sdsswave GT 6650 and sdsswave lt 6800)],gaussval

; multiply this by the HST filter curve
noline=sclean*hstthrough2[where (sdsswave GT 6650 and sdsswave lt 6800)]

window,1
plot,sdsswave,out,xrange=[6600,6850],xtitle='Angstroms',ytitle='Flux at Detector',title='F673N Contribution from OI'
oplot,sdsswave[where (sdsswave GT 6650 and sdsswave lt 6800)],noline,linestyle=2
oplot,sdsswave[where (sdsswave GT 6650 and sdsswave lt 6800)],(out[where (sdsswave GT 6650 and sdsswave lt 6800)]-noline)+6,linestyle=3

;integrate under the residual curve to determine the contribution from OI
o1cont=int_tabulated(sdsswave[where (sdsswave GT 6650 and sdsswave lt 6800)],(out[where (sdsswave GT 6650 and sdsswave lt 6800)]-noline))

;get total flux to the detector in that filter
totalcont=int_tabulated(sdsswave,out)

print,'OI line contributes ',o1cont/totalcont*100.,'% of the counts'

; save the plot
set_plot,"ps"
device,filename='F673N_OI_contribution.ps',/portrait
plot,sdsswave,out,xrange=[6600,6850],xtitle='Angstroms',ytitle='Flux at Detector',title='F673N Contribution from OI'
oplot,sdsswave[where (sdsswave GT 6650 and sdsswave lt 6800)],noline,linestyle=2
oplot,sdsswave[where (sdsswave GT 6650 and sdsswave lt 6800)],(out[where (sdsswave GT 6650 and sdsswave lt 6800)]-noline)+6,linestyle=3
device,/close

end
