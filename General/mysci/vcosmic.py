# Compute "cosmic" velocity for a 3-attractor model (Mould+ 2000)

import numpy as _np
import astropy.units as _u
import mysci as _mysci

def vcosmic(vh, inpRA, inpDec):
    """
    vcosmic: Compute a "cosmic velocity", correcting for the Virgo Cluster,
    the Great Attractor and the Shapley Supercluster.

    Based on fortran code provided by J. Condon for the Mould+ 2000 3-attractor
    model.

    Angles and positions should be in radians or degrees, and velocities in km/s
    All values should be provided using astropy.units quantities.
    J2000 assumed.
    """

    # constants
    cosdec = _np.cos(inpDec)
    sindec = _np.sin(inpDec)
    cosrara0 = _np.cos(inpRA - _mysci.galcenter['RA'])
    sinrara0 = _np.sin(inpRA - _mysci.galcenter['RA'])
    coscdec0 = _np.cos(_np.pi * _u.rad/2. - _mysci.galcenter['Dec'])
    sincdec0 = _np.sin(_np.pi * _u.rad/2. - _mysci.galcenter['Dec'])

    # galactic latitude
    singlat = -cosdec * sinrara0 * sincdec0 + sindec * coscdec0
    glat = _np.arcsin(singlat)
    cosglat = _np.sqrt(1. - singlat * singlat)
    # galactic longitude
    if cosglat == 0.:
        glon = 0. * _u.rad
    cosglon = cosdec * cosrara0 / cosglat
    singlon = (cosdec * sinrara0 * coscdec0 + sindec * sincdec0) / cosglat
    if cosglon != 0.:
        glon = _np.arctan(singlon / cosglon)
    else:
        if singlon > 0.:
            glon = _np.pi / 2. * _u.rad
        if singlon < 0.:
            glon = 1.5 * _np.pi * _u.rad
    # resolve 180 degree ambiguity in glon
    if cosglon < 0.:
        glon = glon + _np.pi * _u.rad
    glon = glon + _mysci.galcenter['galLon']
    twopi = 2. * _np.pi * _u.rad
    if glon < 0:
        glon = glon + twopi
    if glon >= twopi:
        glon = glon - twopi

    # correct from heliocentric to local group velocity
    vlg = vh - 79. * _u.km / _u.s * _np.cos(glon) * _np.cos(glat) \
            + 296. * _u.km/ _u.s * _np.sin(glon) * _np.cos(glat) \
            - 36. * _u.km / _u.s * _np.sin(glat)
    vcorr = vlg

    # correct for infall velocities
    # reformat attractor constants
    racl = [_mysci.VirgoCluster['RA'],
            _mysci.GreatAttractor['RA'],
            _mysci.ShapleySupercluster['RA']]
    deccl = [_mysci.VirgoCluster['Dec'],
             _mysci.GreatAttractor['Dec'],
             _mysci.ShapleySupercluster['Dec']]
    vlgcl = [_mysci.VirgoCluster['vlgcl'],
             _mysci.GreatAttractor['vlgcl'],
             _mysci.ShapleySupercluster['vlgcl']]
    vfid = [_mysci.VirgoCluster['vfid'],
            _mysci.GreatAttractor['vfid'],
            _mysci.ShapleySupercluster['vfid']]
    radius = [_mysci.VirgoCluster['radius'],
              _mysci.GreatAttractor['radius'],
              _mysci.ShapleySupercluster['radius']]
    vmin = [_mysci.VirgoCluster['vmin'],
            _mysci.GreatAttractor['vmin'],
            _mysci.ShapleySupercluster['vmin']]
    vmax = [_mysci.VirgoCluster['vmax'],
            _mysci.GreatAttractor['vmax'],
            _mysci.ShapleySupercluster['vmax']]
    for i in range(3):
        x = _np.sin(_np.pi * _u.rad / 2. - inpDec) * _np.cos(inpRA)
        y = _np.sin(_np.pi * _u.rad / 2. - inpDec) * _np.sin(inpRA)
        z = _np.cos(_np.pi * _u.rad / 2. - inpDec)
        xcl = _np.sin(_np.pi * _u.rad / 2. - deccl[i]) * _np.cos(racl[i])
        ycl = _np.sin(_np.pi * _u.rad / 2. - deccl[i]) * _np.sin(racl[i])
        zcl = _np.cos(_np.pi * _u.rad / 2. - deccl[i])
        dist = (x - xcl)**2 + (y - ycl)**2 + (z - zcl)**2
        dist = _np.sqrt(dist)
        theta = 2. * _np.arcsin(dist / 2.)
        costheta = _np.cos(theta)

        # is the galaxy in the attractor core cone?
        if theta < radius[i] and vh > vmin[i] and vh < vmax[i]:
            vcorr = vlgcl[i]
        else:
            roa = vlg**2 + vlgcl[i]**2 - 2. * vlg * vlgcl[i] * costheta
            roa = _np.sqrt(roa)
            vinlg = vfid[i] * costheta
            vingal = (vlg - vlgcl[i] * costheta) / roa
            vingal = vingal * vfid[i] * vlgcl[i] / roa
            vin = vinlg + vingal
            vin = -vin
            vcorr = vcorr - vin

    return vcorr
