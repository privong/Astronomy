pro gbt_cal_loop,sscan,escan,outfile,PLNUM=plnum,SCALEV=scalev,BREGION=bregion,NFIT=nfit

; gbt_cal_loop
; loop through the Jy calibrated data and apply a scaling factor to it
;
; sscan - starting scan number
; escan - ending scan number
; outfile - log file to contain debugging information
; plnum - which polarization to use (1 or 0)
; scalev - scaling factor with which to multiply the GBT data
; bregion - baseline fit regions to be passed to 'baseline'
; nfit - fit order (5 is default)
;
; Last modified - 30 April 2009 by George Privon

if (not(keyword_set(nfit))) then begin
  nfit=5
endif

; open a logfile for writing
openu,1,outfile+'.log',/APPEND

printf,1,'# Reduction log.'
printf,1,'# Reduction parameters:'
printf,1,'sscan:',sscan
printf,1,'escan:',escan
printf,1,'nfit:',nfit
printf,1,'scalev:',scalev
printf,1,'bregion:',bregion

nregion,bregion		; set the baseline fit region
fileout,outfile+'.fits',/new	; make a keep file for the baseline subtracted data

for i=sscan,escan,2 do begin
  print,'Applying Calibration to scan ',i
  printf,1,'# Applying Calibration to scan ',i
  gettp,i,plnum=plnum	; load total power scan
  boxcar,20,/decimate	; boxcar smooth the data
  scale,scalev		; scale data by specified factor
  baseline,nfit=nfit	; fit and subtract a baseline
  stats,bregion[0],bregion[1],ret=mystats,/chan
  print,'Region 1 statistics'
  print,'mean:',mystats.mean
  print,'RMS:',mystats.rms
  printf,1,'Region 1 statistics'
  printf,1,'mean:',mystats.mean
  printf,1,'RMS:',mystats.rms
  stats,bregion[2],bregion[3],ret=mystats,/chan
  print,'Region 2 statistics'
  print,'mean:',mystats.mean
  print,'RMS:',mystats.rms
  printf,1,'Region 2 statistics'
  printf,1,'mean:',mystats.mean
  printf,1,'RMS:',mystats.rms
  plotfile=outfile+'-plnum_'+strtrim(string(plnum),1)+'-'+strtrim(string(i),1)+'.ps'
  asciifile=outfile+'-plnum_'+strtrim(string(plnum),1)+'-'+strtrim(string(i),1)+'.txt'
  write_ps,plotfile
  write_ascii,asciifile
  accum			; accumulate the data into the stack
  keep			; save the baseline subtracted data

endfor

close,1
end
