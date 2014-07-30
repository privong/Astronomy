# Compute luminosity distance for a 3-attractor model (Mould+ 2000)

import numpy as np
import astropy.units as u
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
    if cosglat==0.:
        glon=0.*u.rad
    cosglon=cosdec * cosrara0 / cosglat
    singlon = (cosdec * sinrara0 * coscdec0 + sindec * sincdec0)/cosglat
    if cosglon!=0.:
        glon = np.arctan (singlon / cosglon)
    else:
        if singlon > 0.: glon = np.pi/2.*u.rad
        if singlon < 0.: glon = 1.5*np.pi*u.rad
    # resolve 180 degree ambiguity in glon
    if cosglon < 0.: 
        glon = glon + np.pi*u.rad
    glon = glon + mysci.galcenter['galLon']
    twopi = 2. * np.pi*u.rad
    if glon < 0: 
        glon = glon + twopi
    if glon >= twopi: 
        glon = glon - twopi

    # correct from heliocentric to local group velocity
    vlg = vh - 79.*u.km/u.s*np.cos(glon)*np.cos(glat) \
            + 296.*u.km/u.s*np.sin(glon)*np.cos(glat) \
            - 36.*u.km/u.s*np.sin(glat)
    vcosmic=vlg

    # correct for infall velocities
    # reformat attractor constants
    racl=[mysci.VirgoCluster['RA'],mysci.GreatAttractor['RA'],mysci.ShapleySupercluster['RA']]
    deccl=[mysci.VirgoCluster['Dec'],mysci.GreatAttractor['Dec'],mysci.ShapleySupercluster['Dec']]
    vlgcl=[mysci.VirgoCluster['vlgcl'],mysci.GreatAttractor['vlgcl'],mysci.ShapleySupercluster['vlgcl']]
    vfid=[mysci.VirgoCluster['vfid'],mysci.GreatAttractor['vfid'],mysci.ShapleySupercluster['vfid']]
    radius=[mysci.VirgoCluster['radius'],mysci.GreatAttractor['radius'],mysci.ShapleySupercluster['radius']]
    vmin=[mysci.VirgoCluster['vmin'],mysci.GreatAttractor['vmin'],mysci.ShapleySupercluster['vmin']]
    vmax=[mysci.VirgoCluster['vmax'],mysci.GreatAttractor['vmax'],mysci.ShapleySupercluster['vmax']]
    for i in range (3):
        x=np.sin(np.pi*u.rad/2.-b1950dec)*np.cos(b1950ra)
        y=np.sin(np.pi*u.rad/2.-b1950dec)*np.sin(b1950ra)
        z=np.cos(np.pi*u.rad/2.-b1950dec)
        xcl = np.sin (np.pi*u.rad / 2. - deccl[i]) * np.cos(racl[i])
        ycl = np.sin (np.pi*u.rad / 2. - deccl[i]) * np.sin(racl[i])
        zcl = np.cos (np.pi*u.rad / 2. - deccl[i])
        dist = (x - xcl)**2 + (y - ycl)**2 + (z - zcl)**2
        dist = np.sqrt(dist)
        theta = 2. * np.arcsin(dist / 2.)
        costheta = np.cos(theta)

        # is the galaxy in the attractor core cone?
        if theta < radius[i] and vh > vmin[i] and vh < vmax[i]:
            vcosmic=vlgcl[i]
        else:
            roa=vlg**2 + vlgcl[i]**2 - 2. * vlg * vlgcl[i] * costheta
            roa=np.sqrt(roa)
            vinlg = vfid[i] * costheta
            vingal = (vlg - vlgcl[i] * costheta) / roa
            vingal = vingal * vfid[i] * vlgcl[i] / roa
            vin = vinlg + vingal
            vin = -vin
            vcosmic = vcosmic - vin

    return vcosmic
