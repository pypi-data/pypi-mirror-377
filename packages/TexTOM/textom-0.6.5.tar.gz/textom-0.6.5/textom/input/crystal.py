import numpy as np
## Define diffraction-related parameters:
# x-ray energy in keV
E_keV = 15.2
# q range for fitting: (lower,upper) boundary in nm^-1
q_range = (10,35)
# path to crystal cif file
cifPath = 'analysis/BaCO3.cif'
# parameters for diffractlet calculation
cutoff_structure_factor=1e-4
max_hkl=4

odf_mode = 'hsh' # 'grid' # 
grid_resolution = 15 # degree # ignored if hsh
hsh_max_order = 12 # ignored if gridbased

# classic mode parameters
# approximate crystal size along (a,b,c)-axes in nm
crystalsize = (15,15,15)
# angular sampling
sampling = 'cubochoric' # or 'simple' (legacy)
# angular sampling resolution
dchi = 2*np.pi / 120
