pro HST_filter_mult,filter,spectra,output

; interpolate and multiply a HST filter curve by an SDSS spectra
; write the output to a separate file

;read the HST filter curve info
; wavelength is in angstroms
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

; write the output to file
openw,outout,output,/GET_LUN
printf,outout,'#Wavelength	SDSS*HST_Filter'
printf,outout,'#Angstroms	contribution to flux'
for i=0,n_elements(hstthrough2)-1 do begin
  printf,outout,sdsswave[i],out[i]
endfor

close,outout

end
