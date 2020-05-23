from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='COSMOS_Astrometry',
      version='0.1',
      description='Repository of astrometric comparisons between cosmos field data from HST, HSC and Gaia',
      author='Remy Joseph',
      author_email='remyj@princeton.edu',
      packages=['COSMOS_Astrometry'],
      zip_safe=False,
      classifiers=[
                   "Programming Language :: Python :: 3.7",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   ])
