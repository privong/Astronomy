# Compute luminosity distance for a 3-attractor model (Mould+ 2000)

import numpy as np
import mysci

def vcosmic(vh,b1950ra,b1950dec):
    """
    vcosmic: Compute a "cosmic velocity", correcting for the Virgo Cluster, 
    the Great Attractor and the Shapley Supercluster.

    Based on fortran code provided by J. Condon.

    Angles in radians, velocities in km/s.
    """

    # constants
    cosdec=np.cos(b1950dec)
    sindec=np.sin(b1950dec)
    cosrara0=np.cos(b1950ra - mysci.galcenter['RA'])
    sinrara0=np.sin(b1950ra - mysci.galcenter['RA'])
    coscdec0=np.cos(np.pi*u.rad/2. - mysci.galcenter['Dec'])
    sincdec0=np.sin(np.pi*u.rad/2. - mysci.galcenter['Dec'])

    # galactic latitude
    singlat=-cosdec*sinrara0*sincdec0+sindec*coscdec0
    glat=np.arcsin(singlat)
    cosglat=np.sqrt(1.-singlat*singlat)
    # galactic longitude
    if cosglat==0:
        glon=0.*u.rad
    cosglon=cosdec * cosrara0 / cosglat
    singlon = (cosdec * sinrara0 * coscdec0 + sindec * sincdec0)/cosglat
    if cosglon!=0:
        glon = atan (singlon / cosglon)
    else:
        if singlon > 0: glon = np.pi/2.*u.rad
        if singlon < 0: glon = 1.5*np.pi*u.rad
    # resolve 180 degree ambiguity in glon
    if cosglon <0: glon = glon + np.pi*u.rad
    glon = glon + glon0
    twopi = 2. * np.pi*u.rad
    if glon < 0: glon = glon + twopi
    if glon > twopi: glon = glon - twopi


    # correct from heliocentric to local group velocity
    vlg = vh - 79. *np.cos(glon)*np.cos(glat) \
            + 296.*np.sin(glon)*np.cos(glat) \
            - 36. *np.sin(glat)
    vcosmic=vlg

    # correct for infall velocities
    # reformat attractor constants
    racl=[VirgoCluster['RA'],GreatAttractor['RA'],ShapleySupercluster['RA']]
    deccl=[VirgoCluster['Dec'],GreatAttractor['Dec'],ShapleySupercluster['Dec']]
    vlgcl=[VirgoCluster['vlgcl'],GreatAttractor['vlgcl'],ShapleySupercluster['vlgcl']]
    vfid=[VirgoCluster['vfid'],GreatAttractor['vfid'],ShapleySupercluster['vfid']]
    radius=[VirgoCluster['radius'],GreatAttractor['radius'],ShapleySupercluster['radius']]
    vmin=[VirgoCluster['vmin'],GreatAttractor['vmin'],ShapleySupercluster['vmin']]
    vmax=[VirgoCluster['vmax'],GreatAttractor['vmax'],ShapleySupercluster['vmax']]
    for i in range (3):
        x=np.sin(np.pi*u.rad/2.-b1950dec)*np.cos(b1950ra)
        y=np.sin(np.pi*u.rad/2.-b1950dec)*np.sin(b1950ra)
        z=np.cos(np.pi*u.rad/2.-b1950dec)
        xcl = np.sin (np.pi*u.rad / 2. - deccl[i]) * np.cos(racl[i])
        ycl = np.sin (np.pi*u.rad / 2. - deccl[i]) * np.sin(racl[i])
        zcl = np.cos (np.pi*u.rad / 2. - deccl[i])
        dist = (x - xcl)**2 + (y - ycl)**2 + (z - zcl)**2
        dist = np.sqrt(dist)
        theta = 2. * np.asin(dist / 2.)
        costheta = np.cos(theta)

        # is the galaxy in the attractor core cone?
        if theta < radius[i] and vh > vmin[i] and vh < vmax[i]:
            vcosmic=vlgcl[i]
            return vcosmic
        roa=vlg**2 + vlgcl[i]**2 - 2. * vlg * vlgcl[i] * costheta
        roa=roa**0.5
        vinlg = vfid[i] * costheta
        vingal = (vlg - vlgcl[i] * costheta) / roa
        vingal = vingal * vfid[i] * vlgcl[i] / roa
        vin = vinlg + vingal
        vin = -vin
        vcosmic = vcosmic - vin

        return vcosmic
