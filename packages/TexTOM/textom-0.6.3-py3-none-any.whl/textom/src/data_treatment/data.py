import os, glob
import numpy as np
from time import time
import sys
import h5py
from numba import prange, njit
from scipy.signal import find_peaks

# domestic
from .. import mask as msk
from . import baselines as bln
from .. import numba_plugins as nb
from ..misc import import_module_from_path
from ..model.model_textom import model_textom
from ...config import data_type

def import_data( sample_dir, pattern, mod:model_textom,  baseline_path,
                qmask_path, detmask_path, geo_path,
                use_ion=True ):
    """Looks for data in path/data_integrated/ and prepares them for textom reconstructions

    Parameters
    ----------
    sample_dir : str
        textom base directory
    pattern : str
        substring required to be in the files in path/data_integrated/
    mod : model
        model object, needs to have projectors and diffractlets
    baselines : str or False, optional
        'simple' to draw a straight line under each peak, (does not work if there is peak-overlap!)
        'polynomial' to fit the whole q-range minus the peaks with a 5th order polynomial (can
            handle peak-overlap, but data needs to be rather smooth where there is no peaks), 
        'chebyshev' same as polynomial but uses chebyshev polynomials
        anything else for no baselines (if your background is low), by default 'simple'
    bl_arg : effectively the polynomial order. recommended ~ 4 for polynomial, 10 for chebyshev
    qmask_path : str, optional
        path to a file containing the peak-regions in q, if None will be created
        from user input, by default None
    detmask_path : str, optional
        path to a file containing the detector mask, if None will be created
        from user input, by default None
    geo_path : str, optional
        path to the desired geometry module, by default 'input/geometry.py'
    flip_fov : bool, optional
        can be set to True if the fov metadata is switched by accident, by default False
    use_ion : bool, optional
        choose if normalisation by ionization chamber should be used (if present in
        data), by default True
    """
    # Load stuff
    geo = import_module_from_path('geometry', geo_path)
    bl = import_module_from_path('background_subtraction', baseline_path)
    peak_reg = load_peak_regions(qmask_path)
    mask_detector = np.genfromtxt(detmask_path, bool)
    # get the images that show the sample
    scanmask = mod.Beams[:,:,0].astype(bool)                           ###########
    cp_threshold = False # for crazy pixel filter

    print('Starting data import')
    print('\tLoading integrated data from files')
    t0=time()
    airscat, ion = [], []
    filelist = get_data_list(sample_dir, pattern)

    for g, file in enumerate( filelist ):
        # Read data from integrated file
        with h5py.File(os.path.join(sample_dir, 'data_integrated', file),'r') as hf:
            q_in = np.squeeze(hf['radial_units'][()] ).astype(data_type)
            chi_in = np.squeeze( hf['azimuthal_units'][()]*np.pi/180 ).astype(data_type)
            fov = ( hf['fov'][()] ).astype(np.int32)
            d = ( np.array(hf['cake_integ'][()]) ).astype(data_type)
            if 'ion' in hf and use_ion:
                try:
                    ion_g = winsorize(hf['ion'][()], 1)
                except:
                    ion_g = hf['ion'][()]
                ion.append(ion_g)
            else:
                use_ion=False

        # this is just for the case fast/slow axes were chosen wrong during integration
        if geo.flip_fov:
            fov = np.flip( fov )
            
        # rescale data by primary beam intensity if known
        if use_ion:
            d = _rescale( d, ion[g] )

        ## Reshaping in function of scanning mode ###
        # Base code written for column scan
        d = d.reshape( *fov, d.shape[1], d.shape[2] )
        
        if 'line' in geo.scan_mode:
            fov = np.flip( fov )
            # d = np.fliplr(np.flipud( np.transpose( d, axes=(1,0,2,3)) ) )
            d = np.transpose( d, axes=(1,0,2,3)) 

        # reorder data so that they are all treated the same in the model
        if 'snake' in geo.scan_mode:
            # Flip every second row
            for ii in range(d.shape[0]):
                if ii % 2 != 0:
                    d[ii] = d[ii][::-1]
        ##############################################

        i0=d.shape[-1]//4
        half_fov = fov[1]//2
        edge_sample = np.array([ 
            d[0,0,i0:].mean(),d[0,-1,:,i0:].mean(), 
            d[0,-half_fov,:,i0:].mean(),  d[-1,0,:,i0:].mean(), 
            d[-1,-half_fov,:,i0:].mean(),d[-1,-1,:,i0:].mean()]) 
        airscat.append( max( np.min( edge_sample), 0.) )
        # rescale by airscattering if primary beam intensity not known
        if not ion or not use_ion:
            # print('\tRescale by air scattering')
            d /= airscat[g]

        # pad the data as in mumottize
        n_chi = chi_in.size
        proj =  np.zeros( (*mod.fov, n_chi, *q_in.shape), data_type)
        si, sj = d.shape[:2]
        i0 = (mod.fov[0] - si)//2
        j0 = (mod.fov[1] - sj)//2
        proj[i0:i0+si, j0:j0+sj] = d
        proj = proj.reshape(mod.fov[0]*mod.fov[1], n_chi, *q_in.shape)
        
        if not cp_threshold: # like this it's done only once
            print('\tChoose threshold for crazy pixels (Everything below will be processed)')
            cp_threshold = msk.select_threshold_hist( proj.flatten(), 
                        xlabel='Counts', ylabel='No of data points', 
                        title='Choose threshold for crazy pixels (Everything below will be processed)',
                        logscale=True )

            _, q_mask_p = get_q_mask(q_in, peak_reg)
            match bl.mode:
                case 'simple':
                    print('\tSubtracting linear baselines')
                    bl_fun = bln.linear_baseline
                    bl_order = 0
                case 'polynomial':
                    print('\tSubtracting polynomial baselines')
                    bl_fun = bln.polynomial_baseline       
                    bl_order = bl.order_polynom     
                case 'chebyshev':
                    print('\tSubtracting chebyshev polynomial baselines')
                    bl_fun = bln.chebyshev_baseline
                    bl_order = bl.order_chebyshev
                case _:
                    print('\tNot subtracting baselines')
                    bl_fun = bln.no_baseline
                    bl_order = 0
            t1 = time()

        proj[proj > cp_threshold] = np.median(proj)

        t_mask = np.where(scanmask[g])[0]
        data_fit = _regroup_q_any_baseline( 
            proj, t_mask, mask_detector,
            bl_fun, bl_order, q_in, q_mask_p )

        # if baselines=='polynomial':
        #     # print('\tDrawing baselines')
        #     # t0=time()
        #     bl_coeff_tmp1, scanmask_g = _draw_baselines_polynom( 
        #         proj, scanmask_g, q_in, q_mask, q_mask_hp, prom, 5 )
        #     bl_coeff_tmp2 = bl_coeff_tmp1[scanmask_g]
        #     # # get rid of outliers
        #     t_mask_0 = np.where(scanmask_g)
        #     blc_weight = (bl_coeff_tmp2**2).sum(axis=1) 
        #     bl_mask = blc_weight < 200*np.median(blc_weight)
        #     t_mask = t_mask_0[0][bl_mask]
        #     scanmask_g = np.zeros_like(scanmask_g)
        #     scanmask_g[t_mask] = True
        #     scanmask[g] = scanmask_g
        #     bl_coeff_tmp1 = bl_coeff_tmp1[scanmask_g]    
        #     # print(f'\t\ttook {time()-t0:.2f} s')
        # elif baselines=='simple':
        #     bl_coeff_tmp1, scanmask_g = _draw_baselines_simple(
        #         proj, scanmask_g, q_mask_k, q_mask_hp, prom )
        #     scanmask[g] = scanmask_g
        # else:
        #     print('\tNo baseline subtraction')
        #     bl_coeff_tmp1 = np.zeros( [] )
        #     baselines = False # this is so that later 'if baselines' check gives False

        # # # plot data and baseline
        # # plt.plot(nb.nb_mean_ax0( proj[t] ))
        # # plt.plot(nb.nb_polyval(bl_coeff_tmp1[t], q_in))

        # bl_coeff.append(bl_coeff_tmp1)
        # t_mask = np.array( np.where(scanmask_g) ).T      

        # # print('\tSubstracting background, regrouping data')
        # # t0=time()
        # q_mask_k_ext = np.array([nb.nb_tile_1d(qmk, n_chi) for qmk in q_mask_k]
        #                         ).astype(data_type)
        # if baselines=='polynomial':
        #     data_fit = _regroup_q_polynombl( 
        #         proj, t_mask, mask_detector, 
        #         bl_coeff_tmp1, q_in, n_chi, q_mask_k_ext )
        # elif baselines=='simple':
        #     data_fit = _regroup_q_simplebl( 
        #         proj, t_mask, mask_detector, 
        #         bl_coeff_tmp1, q_in, n_chi, q_mask_k_ext )
        # else:
        #     data_fit = _regroup_q_nobaseline( 
        #         proj, t_mask, mask_detector, 
        #         n_chi, q_mask_k_ext )
        # # print(f'\t\ttook {time()-t0:.2f} s')

        # # dplot=np.zeros_like(scanmask_g).astype(data_type)
        # # dplot[scanmask_g] = data_fit.mean(axis=1)
        # # plt.figure()
        # # plt.imshow(dplot.reshape(fov_max))

        out_path = os.path.join( sample_dir, 'analysis', 'data_textom.h5')
        if g == 0:
            print('\tSaving data to file: %s' % out_path)
            with h5py.File( out_path, 'w') as hf:
                hf.create_dataset( 'data',
                        shape=(0, data_fit.shape[1]),
                        maxshape=(None, data_fit.shape[1]),
                        chunks=(1, data_fit.shape[1]),
                        dtype=data_type,
                    )
                hf.create_dataset( 'peak_reg', data=peak_reg )
                hf.create_dataset( 'q', data = np.mean(peak_reg, axis=1))
                hf.create_dataset( 'detShape', data = [q_mask_p.shape[0], n_chi] )
                hf.create_dataset( 'mask_detector', data = mask_detector)

        # add data to h5 file
        with h5py.File( out_path, 'r+') as hf:
            dset = hf['data']
            current_rows = dset.shape[0]
            new_rows = current_rows + data_fit.shape[0]
            dset.resize( new_rows, axis=0)
            dset[current_rows:new_rows, :] = data_fit

        try:
            t_it = (time()-t1)/(g)
        except:
            t_it=0
        Nrot = len(filelist)
        sys.stdout.write(f'\r\t\tProjection {(g+1):d} / {Nrot:d}, t/proj: {t_it:.1f} s, t left: {((Nrot-g-1)*t_it/60):.1f} min' )
        sys.stdout.flush()

    gt_mask = np.array( np.where(scanmask) ).T
    # add metadata to h5 file
    with h5py.File( out_path, 'r+') as hf:
        hf.create_dataset( 'scanmask', data=scanmask )
        hf.create_dataset( 'gt_mask', data=gt_mask )
        hf.create_dataset( 'baseline_mode', data=bl.mode )
        hf.create_dataset( 'baseline_order', data=bl_order )        
        hf.create_dataset( 'airscat', data = airscat )
        if ion:
            ion_av = np.array( [np.mean(i) for i in ion] ) # cannon write ion directly because shape
            hf.create_dataset( 'ion', data = ion_av )

    print(f'\n\t\ttook {(time()-t0)/60:.1f} min')

def get_data_list(sample_dir, pattern):
    """Looks for all data in data_integrated and makes a list. 
    One can choose a pattern include only the desired files.

    Parameters
    ----------
    sample_dir : str
        sample base directory
    pattern : str
        integrated data filename with * placeholders

    Returns
    -------
    list
        list of filenames to process
    """
    filelist = sorted( glob.glob(os.path.join(sample_dir,'data_integrated','[!sample_coeff]*h5')) )
    # the exception is for the coefficients for generated samples
    filelist = [s for s in filelist if pattern in s]#[:2]
    try:
        filelist = sort_data_list_by_angles( filelist, 'tilt_angle', 'rot_angle' )
    except:
        print('\t\tDid not find angles in files, just sorted data alphabetically')
    return filelist

def mask_peak_regions( sample_dir, mod:model_textom, q_data, powder_1D, qmask_path, show=False):
    t_inter = time() # this is to subtract the time it takes for user input for remaining time estimation
    # set up boolean mask for filtering data
    q = mod.Qq_det.reshape(mod.detShape)[0]
    q_mask = np.ones_like(q_data, dtype=bool)
    # select peak regions from data and simulated powder pattern
    print('\tChoose regions containing diffraction peaks')
    happy = 'n'
    while happy != 'y':
        # powder = mod.difflets[0].reshape(mod.detShape)[:,0]
        # powder = powder / powder[-10:].mean() * powder_1D[-10:].mean()
        
        powder = mod.powder_pattern * powder_1D.max()/mod.powder_pattern.max()

        peak_reg = msk.select_regions( q_data[q_mask], powder_1D[q_mask], q, powder, hkl=mod.hkl,
                max_regions=None,
                title='Select individual Bragg peaks by holding LMB, remove by RMB' )
        happy = input('\thappy? (y/n) ')
    peak_reg = peak_reg.get_regions()

    peak_reg_path = os.path.join(sample_dir,'analysis','peak_regions.txt')
    with open( peak_reg_path,'w') as fid:
        for reg in peak_reg:
            fid.write(f'{reg[0]}\t{reg[1]}\n')
    print(f'\tSaved peak regions to {peak_reg_path}')

    # q_peaks = np.mean(peak_reg, axis=1)

    # # find out prominence of the highest peak for filtering data
    # I_mx = 0.                   
    # q_mask_k = []
    # for k, (start, end) in enumerate( peak_reg ):
    #     q_mask_k.append( ((q_data >= start) & (q_data <= end)) )
    #     q_mask &= ~q_mask_k[k]
    #     dat_peak = powder_1D[q_mask_k[k]]
    #     if dat_peak.max() > I_mx:
    #         q_mask_hp = q_mask_k[k]
    #         _, info = find_peaks(dat_peak, prominence=0.)
    #         try:
    #             prom = info['prominences'].max()
    #         except:
    #             prom=0.
    #         I_mx = dat_peak.max()
    # q_mask_k = np.array(q_mask_k)#.astype(data_type)  

    # t_inter = time()-t_inter
    # return peak_reg, q_mask, q_mask_k, q_mask_hp, prom, q_peaks, t_inter

def load_peak_regions( peak_reg_path ):
    peak_reg = np.genfromtxt(peak_reg_path)
    peak_reg = peak_reg.reshape( (peak_reg.size//2, 2)  )
    return peak_reg

def get_q_mask( q, peak_regions ):
    q_mask_p = []
    for (start, end) in peak_regions:
        q_mask_p.append( ((q >= start) & (q <= end)) )
    q_mask_p = np.array(q_mask_p)
    q_mask = np.logical_not( q_mask_p.sum(axis=0) )
    return q_mask, q_mask_p

def mask_detector( sample_dir, detmask_path, powder_2D_masked, peak_reg, q_in, chi_in ):
    # check if there is a mask from pyfai
    cakemask_path = os.path.join(sample_dir, 'analysis', 'mask_detector_cake.h5')
    if os.path.isfile(cakemask_path):
        with h5py.File(cakemask_path,'r') as hf:
            mc = hf['mask_cake'][()]
        QQ,_ = np.meshgrid( q_in, chi_in )
        qm = [np.logical_and(QQ >= start, QQ <= end) for start,end in peak_reg]
        mask_detector = np.array([
            [np.logical_and.reduce(mc[k, qm[l][k]]) for k in range(chi_in.size)] 
                for l in range(len(peak_reg))])
    else:
        mask_detector = np.ones_like(powder_2D_masked).astype(bool)

    print('\tCreate mask by removing (left mouse button) or restoring pixels (right mouse button)')
    # start = np.argmax(q_mask) # this could be useful if taking a full mask, then partially regroup ? have to do it with diffractlets too maybe
    # end = len(q_mask) - 1 - np.argmax(q_mask[::-1]) # then make these values None and when regrouping do np.mean * number of points to make up for Nones
    mask_detector = msk.mask_detector( powder_2D_masked, mask_detector )
    with open( detmask_path, 'w' ) as fid:
        for pxl in mask_detector:
            fid.write(f'{pxl}\n')
    return mask_detector

def sort_data_list_by_angles( filelist, h5_outer_rotaxis_path, h5_inner_rotaxis_path ):

    inner_angle = []
    outer_angle = []
    for file in filelist:
        with h5py.File( file, 'r') as hf:
            inner_angle.append( hf[h5_inner_rotaxis_path][()] )
            outer_angle.append( hf[h5_outer_rotaxis_path][()] )
    # first sort by outer angles:
    order = np.lexsort([inner_angle, outer_angle])

    return [filelist[k] for k in order]

def winsorize(data, percent = 1):
    """Very simple filter, setting the upper and lower percentile to the next smaller/larger value
    """
    lower = np.percentile(data, percent)
    upper = np.percentile(data, 100-percent)
    data[data < lower] = lower
    data[data > upper] = upper
    return data

################## numba compiled functions
# @njit(parallel=True)
# def _draw_baselines_polynom(proj, scanmask, q, qmask, q_mask_hp, prom, porder=5 ):
#     """Draws a polynomial baseline through the azimuthally averaged data

#     Parameters
#     ----------
#     proj : ndarray
#         projection data
#     scanmask : ndarray
#         decides which data will be further used for fitting, baselines
#         will only be drawn on thse
#     q : ndarray
#         q-values of the data
#     qmask : ndarray
#         defines the ranges of the peaks to be treated
#     q_mask_hp : ndarray
#         defines the range of the highest peak
#     prom : float
#         prominence of the highest peak in the first projection
#     porder : int, optional
#         polynomial order for the baseline, by default 5

#     Returns
#     -------
#     ndarray
#         polynomial coefficients of the baselines
#     ndarray
#         updated scanmask
#     """
#     # draw baselines for chosen data
#     bl_coeff = np.zeros( (proj.shape[0],porder+1), data_type )
#     for t in prange(proj.shape[0]):
#         if scanmask[t]:
#             # regroup data azimutally
#             data_1D = nb.nb_mean_ax0( proj[t] )

#             if any_peak( data_1D[q_mask_hp], 0.05*prom ):
#                 # draw a baseline
#                 c = nb.nb_polyfit( q[qmask], data_1D[qmask], porder )
#                 b = nb.nb_polyval( c, q[qmask] )
#                 bl_coeff[t] = c * (data_1D[qmask]/b).min()
#             else:
#                 # exclude this image
#                 scanmask[t]=False
#     return bl_coeff, scanmask

# @njit(parallel=True)
# def _draw_baselines_simple(proj, scanmask, q_mask_k, q_mask_hp, prom ):
#     """Draws a polynomial baseline through the azimuthally averaged data

#     Parameters
#     ----------
#     proj : ndarray
#         projection data
#     scanmask : ndarray
#         decides which data will be further used for fitting, baselines
#         will only be drawn on these
#     q : ndarray
#         q-values of the data
#     qmask : ndarray
#         defines the ranges of the peaks to be treated
#     q_mask_hp : ndarray
#         defines the range of the highest peak
#     prom : float
#         prominence of the highest peak in the first projection

#     Returns
#     -------
#     ndarray
#         polynomial coefficients of the baselines
#     ndarray
#         updated scanmask
#     """
#     # draw baselines for chosen data
#     bl_coeff = np.zeros( (proj.shape[0],2*q_mask_k.shape[0]), data_type )
#     for t in prange(proj.shape[0]):
#         if scanmask[t]:
#             # regroup data azimutally
#             data_1D = nb.nb_mean_ax0( proj[t] )

#             if any_peak( data_1D[q_mask_hp], 0.05*prom ):
#                 # for each peak
#                 for p in range(q_mask_k.shape[0]):
#                     # get the value at the beginning and the end of the peak
#                     idxs = np.where(q_mask_k[p])[0]
#                     bl_coeff[t,2*p] = data_1D[idxs[0]-1:idxs[0]+1].mean()
#                     bl_coeff[t,2*p+1] = data_1D[idxs[-1]:idxs[-1]+2].mean()
#             else:
#                 # exclude this image
#                 scanmask[t]=False
#     return bl_coeff, scanmask

@njit
def any_peak( curve, prominence_threshold ):
    # numba-optimized function to check if there is a peak
    # with the given prominence in the data
    i_peak = np.argmax( curve )
    left_min = np.min(curve[:i_peak]) if i_peak > 0 else 0
    right_min = np.min(curve[i_peak + 1:]) if i_peak < curve.size-1 else 0
    prominence = curve[i_peak] - max(left_min, right_min)
    if prominence >= prominence_threshold:
        return True
    return False

# @njit(parallel=True)
# def _regroup_q_polynombl( proj, t_mask, mask_detector, bl_coeff, q_in, n_chi, q_mask_k_ext ):
#     nD = t_mask.shape[0] # effective number of images
#     data_fit = np.empty( (nD, mask_detector.sum()), data_type )
#     n_peaks = q_mask_k_ext.shape[0]
#     for k in prange(nD):
#         t = t_mask[k,0]
#         # get image and subtract baseline
#         d_k = proj[t] 
#         bl = nb.nb_polyval( bl_coeff[t], q_in)
#         d_k_sub = d_k - nb.nb_tile_1d(bl, n_chi)

#         # regroup data into peaks
#         d_k_regr = np.empty( (n_chi, n_peaks), data_type )
#         for p in range(n_peaks):
#             d_k_regr[:,p] = (d_k_sub*q_mask_k_ext[p]).sum(axis=1)
#         d_k_regr_fl = d_k_regr.flatten()[mask_detector]

#         data_fit[k] = d_k_regr_fl
#     return data_fit

# @njit(parallel=True)
# def _regroup_q_simplebl( proj, t_mask, mask_detector, bl_coeff, q_in, n_chi, q_mask_k_ext ):
#     nD = t_mask.shape[0] # effective number of images
#     data_fit = np.empty( (nD, mask_detector.sum()), data_type )
#     n_peaks = q_mask_k_ext.shape[0]
#     # get the q-range for each peak
#     q_range_p = np.empty(n_peaks, data_type)
#     for p in range(n_peaks):
#         qp_ind = np.where(q_mask_k_ext[p,0])[0]
#         q_range_p[p] = q_in[qp_ind[-1]+1] - q_in[qp_ind[0]]

#     for k in prange(nD):
#         t = t_mask[k,0]
#         # get image and subtract baseline
#         d_k = proj[t] 

#         # regroup data into peaks
#         d_k_regr = np.empty( (n_chi, n_peaks), data_type )
#         for p in range(n_peaks):
#             #calculate integrated baseline:
#             bl_int = (bl_coeff[t,2*p] + bl_coeff[t,2*p+1])/2 * q_mask_k_ext[p,0].sum()
#             # subtract from peak-integral
#             d_k_regr[:,p] = (d_k*q_mask_k_ext[p]).sum(axis=1) - bl_int
#         d_k_regr_fl = d_k_regr.flatten()[mask_detector]

#         data_fit[k] = d_k_regr_fl
#     return data_fit

# @njit(parallel=True)
# def _regroup_q_nobaseline( proj, t_mask, mask_detector, n_chi, q_mask_k_ext ):
#     nD = t_mask.shape[0] # effective number of images
#     data_fit = np.empty( (nD, mask_detector.sum()), data_type )
#     n_peaks = q_mask_k_ext.shape[0]
#     for k in prange(nD):
#         # get image and subtract baseline
#         d_k = proj[t_mask[k,0]] 

#         # regroup data into peaks
#         d_k_regr = np.empty( (n_chi, n_peaks), data_type )
#         for p in range(n_peaks):
#             d_k_regr[:,p] = (d_k*q_mask_k_ext[p]).sum(axis=1)
#         d_k_regr_fl = d_k_regr.flatten()[mask_detector]

#         data_fit[k] = d_k_regr_fl
#     return data_fit

@njit(parallel=True)
def _regroup_q_any_baseline( projection, t_mask, mask_detector, bl_fun, bl_order, q_in, q_mask_p ):
    n_data = t_mask.shape[0] # effective number of images
    regrouped_data = np.empty( (n_data, mask_detector.sum()), data_type )
    n_peaks = q_mask_p.shape[0]
    q_mask = np.logical_not( q_mask_p.sum(axis=0) )

    for k in prange(n_data):
        t = t_mask[k] # index within projection
        # get image and subtract baseline
        data_k = projection[t] 
        data_k_1d = nb.nb_mean_ax0( projection[t] )
        baseline = bl_fun( q_in, data_k_1d, q_mask, bl_order )

        # regroup data into peaks
        data_k_regrouped = np.empty( (data_k.shape[0], n_peaks), data_type )
        for p in range(n_peaks):
            #calculate integrated baseline:
            base_p = baseline[q_mask_p[p]].sum()
            # subtract from peak-integral
            data_k_regrouped[:,p] = data_k[:,q_mask_p[p]].sum(axis=1) - base_p

        regrouped_data[k] = data_k_regrouped.flatten()[mask_detector]
    return regrouped_data

@njit(parallel=True)
def _rescale( data, norm ):
    for k in prange( data.shape[0] ):
        if norm[k] == 0:
            data[k] = 0
        else:
            data[k] /= norm[k]
    return data

# @njit(parallel=True)
# def _rescale_perimage( data, norm ):
#     for k in prange( data.shape[0] ):
#         for l in range( data.shape[1] ):
#             data[k,l] /= norm[k,l]
#     return data

# @njit(parallel=True)
# def _remove_crazypixels( projection, scanmask ):
#     dat_new = projection.copy()
#     for k in prange(projection.shape[0]):
#         if scanmask[k]:
#             for l in range(1,projection.shape[2]-1):
#                 # base = np.median(projection[k,:,l])
#                 for m in range(-1,projection.shape[1]-1):
#                     sample = np.array([
#                         projection[k,m-1,l-1],projection[k,m-1,l],projection[k,m-1,l+1],
#                         projection[k,m,l-1],projection[k,m,l+1],                        
#                         projection[k,m,l-2],projection[k,m,l+2],
#                         projection[k,m+1,l-1],projection[k,m+1,l],projection[k,m+1,l+1]
#                     ])
#                     base = np.median(sample)
#                     if projection[k,m,l] > 10*np.abs(base):
#                         dat_new[k,m,l] = base
#     return dat_new

# # @njit
# def _remove_crazypixels_zscore( data, threshold=3 ):
#     #
#     z = (data - data.mean()) / data.std()
#     data[z > threshold] = np.median(data)
#     return data

# def _remove_crazypixels_manual( data, threshold ):
#     data[data > threshold] = np.median(data)
#     return data

# @njit(parallel=True)
# def rebin_stack_2d_dim0(stack, new_cols):
#     """
#     Rebin a stack of 2D arrays to a new shape using a weighted average of the corresponding regions.
    
#     Parameters:
#     - stack: 3D array with the arrays of original shape in dimensions 1/2.
#     - new_cols: int of the new number of cols.
    
#     Returns:
#     - stack_rebinned: 3D array with the rebinned arrays in dimensions 1/2.
#     """
#     n_images = stack.shape[0]
#     stack_reshaped = np.empty( (n_images, new_cols, stack.shape[2]) )
#     for k in prange( n_images ):
#         stack_reshaped[k] = rebin_2d_dim0( stack[k], new_cols )
#     return stack_reshaped

# @njit
# def rebin_2d_dim0(array, n_dim0):
#     """
#     Rebin a 2D array to a new shape using a weighted average of the corresponding regions.
    
#     Parameters:
#     - array: Input 2D array (original shape).
#     - n_dim0: int of the new size in dim 0cols.
    
#     Returns:
#     - rebinned_array: Rebinned 2D array with weighted averages.
#     """
#     n_dim0_orig, n_dim1_orig = array.shape # original shape
#     # new_rows, new_cols = new_shape
    
#     # Calculate the scaling factors (step size in each dimension)
#     bin_size = n_dim0_orig / n_dim0

#     # Create an empty rebinned array
#     rebinned_array = np.zeros((n_dim0, n_dim1_orig))

#     for i in range(n_dim0):
#         # Determine the range of pixels in the original array that contribute to the new bin
#         bin_start = i * bin_size
#         bin_end = (i + 1) * bin_size

#         # Find the indices of the original array that overlap with the new bin
#         indices_to_bin = np.arange(int(np.floor(bin_start)), int(np.ceil(bin_end)))

#         for j in range(n_dim1_orig):
#             # Accumulate weighted sum over these indices
#             weight_sum = 0
#             value_sum = 0
#             for c in indices_to_bin:
#                 # Compute the overlap (weight) for each pixel
#                 weight = min(bin_end, c + 1) - max(bin_start, c)

#                 # Add the contribution to the weighted sum
#                 value_sum += array[c, j] * weight
#                 weight_sum += weight

#             # Assign the weighted average to the rebinned array
#             rebinned_array[i, j] = value_sum / weight_sum

#     return rebinned_array

# @njit(parallel=True)
# def rebin_stack_2d(stack, new_shape):
#     """
#     Rebin a stack of 2D arrays to a new shape using a weighted average of the corresponding regions.
    
#     Parameters:
#     - stack: 3D array with the arrays of original shape in dimensions 1/2.
#     - new_shape: Tuple of the new shape (new_rows, new_cols).
    
#     Returns:
#     - stack_rebinned: 3D array with the rebinned arrays in dimensions 1/2.
#     """
#     n_images = stack.shape[0]
#     stack_reshaped = np.empty( (n_images, new_shape[0], new_shape[1]) )
#     for k in prange( n_images ):
#         stack_reshaped[k] = rebin_2d_weighted( stack[k], new_shape )
#     return stack_reshaped

# @njit
# def rebin_2d_weighted(array, new_shape):
#     """
#     Rebin a 2D array to a new shape using a weighted average of the corresponding regions.
    
#     Parameters:
#     - array: Input 2D array (original shape).
#     - new_shape: Tuple of the new shape (new_rows, new_cols).
    
#     Returns:
#     - rebinned_array: Rebinned 2D array with weighted averages.
#     """
#     original_shape = array.shape
#     orig_rows, orig_cols = original_shape
#     new_rows, new_cols = new_shape
    
#     # Calculate the scaling factors (step size in each dimension)
#     row_scale = orig_rows / new_rows
#     col_scale = orig_cols / new_cols

#     # Create an empty rebinned array
#     rebinned_array = np.zeros((new_rows, new_cols))

#     for i in range(new_rows):
#         for j in range(new_cols):
#             # Determine the range of pixels in the original array that contribute to the new bin
#             row_start = i * row_scale
#             row_end = (i + 1) * row_scale
#             col_start = j * col_scale
#             col_end = (j + 1) * col_scale

#             # Find the indices of the original array that overlap with the new bin
#             row_indices = np.arange(int(np.floor(row_start)), int(np.ceil(row_end)))
#             col_indices = np.arange(int(np.floor(col_start)), int(np.ceil(col_end)))

#             # Accumulate weighted sum over these indices
#             weight_sum = 0
#             value_sum = 0
#             for r in row_indices:
#                 for c in col_indices:
#                     # Compute the overlap (weight) for each pixel
#                     row_overlap = min(row_end, r + 1) - max(row_start, r)
#                     col_overlap = min(col_end, c + 1) - max(col_start, c)
#                     weight = row_overlap * col_overlap

#                     # Add the contribution to the weighted sum
#                     value_sum += array[r, c] * weight
#                     weight_sum += weight

#             # Assign the weighted average to the rebinned array
#             rebinned_array[i, j] = value_sum / weight_sum

#     return rebinned_array

def import_data_1d( path, pattern, mod:model_textom,
                geo_path='input/geometry.py',
                flip_fov=False, use_ion=True ):

    geo = import_module_from_path('geometry', geo_path)
    # get the images that show the sample
    scanmask = mod.Beams[:,:,0].astype(bool)                           ###########

    print('Starting data import')
    print('\tLoading integrated data from files')
    t0=time()
    airscat, ion = [], []
    filelist = sorted( os.listdir( os.path.join(path,'data_integrated_1d')) )
    filelist = [s for s in filelist if pattern in s]#[:2]
    t1=time()
    for g, file in enumerate( filelist ):
        # Read data from integrated file
        with h5py.File(os.path.join(path, 'data_integrated_1d', file),'r') as hf:
            q_in = ( hf['radial_units'][0] ).astype(data_type)
            fov = ( hf['fov'][()] ).astype(np.int32)
            d = np.array(hf['cake_integ'])[()]
            if 'ion' in hf:
                ion.append(hf['ion'][()])

        if flip_fov:
            fov = np.flip( fov )
            
        if ion and use_ion:
            # print('\tRescale by beam intensity')
            d = _rescale( d, ion[g] )

        ## Reshaping in function of scanning mode ###
        # Base code written for column scan
        d = d.reshape( *fov, d.shape[1] )
        
        if 'line' in geo.scan_mode:
            fov = np.flip( fov )
            d = np.transpose( d, axes=(1,0,2)) 

        # reorder data so that they are all treated the same in the model
        if 'snake' in geo.scan_mode:
            # Flip every second row
            for ii in range(d.shape[0]):
                if ii % 2 != 0:
                    d[ii] = d[ii][::-1]
        ##############################################

        i0=d.shape[-1]//4
        # get airscattering:
        edge_sample = np.array([ 
            d[0,0,i0:].mean(), 
            d[0,-1,:,i0:].mean(), 
            d[0,-fov[1]//2,:,i0:].mean(),  
            d[fov[0]//2,0,i0:].mean(), 
            d[fov[0]//2,-1,:,i0:].mean(), 
            d[-1,0,:,i0:].mean(), 
            d[-1,-fov[1]//2,:,i0:].mean(),
            d[-1,-1,:,i0:].mean()
            ]) 
        airscat.append( np.min( edge_sample[edge_sample > 0.] ))
        if not ion or not use_ion:
            # print('\tRescale by air scattering')
            d /= airscat[g]

        max_shape = mod.fov
        # pad the data as in mumottize
        # fill projections with air scattering
        proj =  np.random.normal(airscat[g],np.sqrt(airscat[g])/2,(*max_shape, d.shape[2]))
        si, sj = d.shape[:2]
        i0 = (max_shape[0] - si)//2
        j0 = (max_shape[1] - sj)//2
        proj[i0:i0+si, j0:j0+sj] = d
        proj = proj.reshape(max_shape[0]*max_shape[1], *q_in.shape)

        scanmask_g = scanmask[g].copy()
        proj = _remove_crazypixels_1d(proj, scanmask_g)

        out_path = os.path.join( path, 'analysis', 'data_1drec.h5')
        if g == 0:
            print('\tSaving data to file: %s' % out_path)
            with h5py.File( out_path, 'w') as hf:
                hf.create_dataset( 'data',
                        shape=(0, proj.shape[1]),
                        maxshape=(None, proj.shape[1]),
                        chunks=(1, proj.shape[1]),
                        dtype='float64'
                    )
                hf.create_dataset( 'radial_units', data = q_in )

        # add data to h5 file
        with h5py.File( out_path, 'r+') as hf:
            dset = hf['data']
            current_rows = dset.shape[0]
            new_rows = current_rows + proj.shape[0]
            dset.resize( new_rows, axis=0)
            dset[current_rows:new_rows, :] = proj


        t_it = (time()-t1)/(g+1)
        Nrot = len(filelist)
        sys.stdout.write(f'\r\t\tProjection {(g+1):d} / {Nrot:d}, t/proj: {t_it:.1f} s, t left: {((Nrot-g-1)*t_it/60):.1f} min' )
        sys.stdout.flush()

    ion_av = np.array( [i.mean() for i in ion] ) # cannon write ion directly because shape
    gt_mask = np.array( np.where(scanmask) ).T
    # add metadata to h5 file
    with h5py.File( out_path, 'r+') as hf:
        hf.create_dataset( 'scanmask', data=scanmask )
        hf.create_dataset( 'gt_mask', data=gt_mask )
        hf.create_dataset( 'airscat', data = airscat )
        hf.create_dataset( 'ion', data = ion_av )
        hf.create_dataset( 'q', data=q_in)

    print(f'\t\ttook {time()-t0:.2f} s')

@njit(parallel=True)
def _remove_crazypixels_1d( projection, scanmask ):
    dat_new = projection.copy()
    for k in prange(projection.shape[0]):
        if scanmask[k]:
            for m in range(-1,projection.shape[1]-1):
                sample = np.array([
                    projection[k,m-2],projection[k,m-1],projection[k,m+1],projection[k,m+2]
                ])
                base = np.median(sample)
                if projection[k,m] > 10*np.abs(base):
                    dat_new[k,m] = base
    return dat_new