import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as sci
import os
import matplotlib
matplotlib.rc('xtick', labelsize=15) 
matplotlib.rc('ytick', labelsize=15) 

def get_distances(coord_ref, coord2, rad):
    '''
    matches coordinates of stars between two datasets and computes the distance between the position of the stars in the 2 datasets

    Inputs:
        coord_ref: coordinates (ra, dec) of stars in a FoV from a given dataset
            numpy array (Nx2)
        coord2: coordinates (ra dec) of stars in the same FoV in an other dataset
            numpy array (Mx2)
        rad: radius (deg) around stars in coord_ref where to find a corresponding star in coord2
            float
    Outputs:
         modulus: containing the distance between matching stars
            numpy array (N')
         angle: angle between matching stars
            numpy array (N')
         v_coord: coordinates in the coord_ref set of matching stars
            numpy array(N',2)
         garbage: coordinates of non matching stars
            numpy array (N-N',2)
    '''
    modulus = []
    angle = []
    v_coord = []
    garbage = []
    x_err = []
    y_err = []
    s = np.size(coord_ref[:,0])
    print('number of points in reference catalog: {0}'.format(s))

    for i,c in enumerate(coord_ref):

        if i % 3000 == 0:
            print('point number {0} out of {1}'.format(i, s))

        r = ((c[0]-coord2[:,0])**2+(c[1]-coord2[:,1])**2)**0.5
        loc = np.array(np.where(r == np.min(r))).flatten()

        if np.size(loc) > 1:

            loc = loc[0]


        rmin = r[loc]

        if rmin <= rad:

            c_ref = coord2[loc].flatten()

            v_coord.append(c)
            modulus.append(rmin.item())
            x_err.append(-c[0]+c_ref[0])
            y_err.append(-c[1] + c_ref[1])

        else:
            garbage.append(c)
    angle = (np.arctan2(y_err, x_err))
    return np.array(modulus), np.array(angle), np.array(v_coord), np.array(garbage), np.array(x_err), np.array(y_err)

def get_error(position, catalog, radius = None, N_star = 10, method = 'cubic'):
    """ Function that evaluates the error on the astrometry at a given position on the sky based on a catalog of errors as a function of the position of the stars the error was computed from.
    
    Parameters
    ----------
    position: Array,
        A 2-element array with the position at which we seek to know the error
    catalog: Array,
        Catalog of errors as a function of star positions. The columns should be as follow:
        'Ra, Dec, Radial error, angular error, Ra-direction error, Dec-direction error', with the error as computed from the 'get_distances' function
    Radius: float (optional,)
        Radius around 'position' that should be used to find star in the catalog from which the error is going to be computed via interpolation.
    N_star: int,
        if set get_error uses the N_star stars in the catalog closest to 'position' to infer the error at 'position' via inerpolation
    method: string,
        Method to use in the interpolation. See scipy.interpolate.griddata.

    Returns
    -------
        error: array
            the error on astrometry infered from 'catalog' at 'position' as: [Ra-direction error, Dec-direction error]
    """
    if np.size(position.shape) > 1:
        errors = []
        for pos in position:
            errors.append(get_error(pos, catalog, radius = None, N_star = N_star, method = 'cubic'))
        return np.array(errors)
    # Compute distances between catalog's stars an 'position'
    d = np.sqrt(np.sum((catalog[:, 0:2]-position[np.newaxis, :])**2, axis = 1))
    if radius is None:
        cut = np.sort(d)
        radius = cut[N_star]
    # Star used in the interpolation
    selection = catalog[d < radius,:]
    Ra_error = sci.griddata(selection[:,0:2], selection[:,-2], position, method=method)
    Dec_error = sci.griddata(selection[:,0:2], selection[:,-1], position, method=method) 
    return Ra_error, Dec_error
        
def HST_HSC_errors(position, interpolation = "cubic"):
    """ Compute astrometric errors at a given position for both HST and HSC data relative to the Gaia catalog
    
    Parameters
    ----------
    Position: `tuple`
        position in (Ra, Dec) where to interpolate the errors
    interpolation: `string`
        method of interpolation among: "cubic", "linear", "nearest"
    
    Returns
    -------
    Error_HST: `tuple`
        The error between Gaia and HSCC
    """
    hst_file = os.path.join(os.path.dirname(__file__), '../Results/HST_astrometric_errors.csv')
    hsc_file = os.path.join(os.path.dirname(__file__), '../Results/HSC_astrometric_errors.csv')
    cat_HST = np.loadtxt(hst_file, dtype = str, delimiter = ',')[1:,:].astype(float)
    cat_HSC = np.loadtxt(hsc_file, dtype = str, delimiter = ',')[1:,:].astype(float)
        
    Ra_HST = sci.griddata(cat_HST[:,0:2], cat_HST[:,-2], position, method=interpolation)
    Dec_HST = sci.griddata(cat_HST[:,0:2], cat_HST[:,-1], position, method=interpolation) 
    
    Ra_HSC = sci.griddata(cat_HST[:,0:2], cat_HST[:,-2], position, method=interpolation)
    Dec_HSC = sci.griddata(cat_HST[:,0:2], cat_HST[:,-1], position, method=interpolation) 
    
    return (Ra_HST, Dec_HST), (Ra_HSC, Dec_HSC)

def plot_results(mod, ang, xerr, yerr, vcoord, pixel = None, label = None, legend = '', init = 0, fontsize = 15):
    '''
    Plots the results of the coordinate matching of stars by showing the distributions of modulus and angles,
    both as a histogram and on the plane of the sky

    Inputs:
        mod: distances between matching stars
            numpy array
        ang: angle between matching stars
            numpy array
        vcoord: coordinates of matching stars
            numpy array
        pixel: size of pixels to display on the histogram
            list
        label: labels of the pixel sizes in pixel. Should either be None or of the same size as pixel.
            list
        legend: title for the plots (name of the datasets in the comparison)
            string
        init: number to initialise the figure numbers
            int

    Outputs:
        None
            Produces plots of the results
    '''
    plt.figure(init+1, figsize=(20,9))
    plt.suptitle(legend, fontsize = 25)
    plt.subplot(211)
    plt.title('modulus distribution', fontsize = 25)
    plt.hist(mod*3600., bins=30)
    if pixel is not None:
        for count, p in enumerate(pixel):
            plt.plot([p, p], [0, mod.size/20], label=label[count])
    plt.legend(fontsize = 15)
    plt.xlabel('modulus (arcsec)', fontsize = 15)
    plt.subplot(212)
    plt.title('')
    plt.hist(ang, bins=30)
    plt.xlabel('angle (rad)', fontsize = 15)

    plt.figure(init+2, figsize=(20,7))
    plt.suptitle(legend, fontsize = 15)
    plt.subplot(122)
    plt.title('modulus across the field', fontsize = 25)
    plt.scatter(vcoord[:, 0], vcoord[:, 1], c=mod*3600., s=15, cmap='gist_stern')
    plt.xlabel('Ra', fontsize = 20)
    plt.ylabel('Dec', fontsize = 20)

    # plt.plot(garbage[:,0], garbage[:,1], 'ok', markersize =1)
    cbar = plt.colorbar()
    cbar.set_label('distance modulus (arcsec)', rotation=270, fontsize = 20, labelpad = 20)

    plt.subplot(121)
    plt.title('angles across the field', fontsize = 25)
    plt.scatter(vcoord[:, 0], vcoord[:, 1], c=ang, s=13, cmap='twilight')
    plt.xlabel('Ra', fontsize = 20)
    plt.ylabel('Dec', fontsize = 20)

    # plt.plot(garbage[:,0], garbage[:,1], 'ok', markersize =1)
    cbar = plt.colorbar()
    cbar.set_label('distance argument (arcsec)', rotation=270, fontsize = 20, labelpad = 20)

    plt.figure(init+3, figsize=(20,7))
    plt.suptitle(legend, fontsize = 15)
    plt.subplot(122)
    plt.title('distance along x-axis', fontsize = 25)
    plt.scatter(vcoord[:, 0], vcoord[:, 1], c=xerr*3600., s=15, cmap='gist_stern')
    plt.xlabel('Ra', fontsize = 20)
    plt.ylabel('Dec', fontsize = 20)
    # plt.plot(garbage[:,0], garbage[:,1], 'ok', markersize =1)

    cbar = plt.colorbar()
    cbar.set_label('Dec-distance (arcsec)', rotation=270, fontsize = 20, labelpad = 20)

    plt.subplot(121)
    plt.title('distance along y-axis', fontsize = 25)
    plt.scatter(vcoord[:, 0], vcoord[:, 1], c=yerr*3600, s=13, cmap='gist_stern')
    plt.xlabel('Ra', fontsize = 20)
    plt.ylabel('Dec', fontsize = 20)

    # plt.plot(garbage[:,0], garbage[:,1], 'ok', markersize =1)
    cbar = plt.colorbar()
    cbar.set_label('Ra-distance (arcsec)', rotation=270, fontsize = 20, labelpad = 20)
    return None
