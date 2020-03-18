# COSMOS_astrometry

Notebooks, functions and catalogs that allow to compute the astrometric errors between HST and HSC in COSMOS fields. I use catalogs of stellar positions, match the star positions in a given catalog to the star positions of the apparent closest star in the Gaia survey and record the difference in positions at the positions of the gaia stars. This allows me to create catalogs of astrometric errors for HSC and HSC relative to Gaia. These catalogs can then be used to infer an estimate for the astrometric error at any location of the COSMOS fields.

The `astrometri_errors.ipynb` notebook allows to compute and visualise the astrometric differences between surveys HSC, HST and GAIA, which serves here as a reference catalog for stellar position.

Notebook `Test_get_error.ipynb` show cases and tests the interpolation strategy that is used to estimate the error at a given location in the sky (not a star location).
