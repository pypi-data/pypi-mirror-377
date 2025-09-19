from setuptools import setup, find_packages
#import os
#import sys
# current dir
#current_dir = os.path.dirname(__file__)

# Get the absolute path to the main directory (one level up)
#main_dir = os.path.abspath(os.path.join(current_dir, ".."))

DESCRIPTION = 'This is the python library for Gradient COBRA by S. Has (2023) with other aggregation and kernel methods'
with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

version = "1.1.6"
setup(name='gradientcobra',
      version=version,
      description='Python implementation for Gradient COBRA by S. Has (2023) with other aggregation and kernel methods.',
      author='Sothea Has',
      author_email="sothea.has@lpsm.paris",
      url='https://github.com/hassothea/gradientcobra/',
      packages=["gradientcobra"],
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Operating System :: Microsoft :: Windows',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering'
      ],
      install_requires=[
          'numpy>=1.20.1',
          'pandas>=2.1.0',
          'scipy>=1.10.1',
          'scikit-learn>=1.2',
          'matplotlib',
          'seaborn',
          'kaleido',
          'plotly>=5.10.0',
          'tqdm'

      ],
      test_suite='tests',
      keywords=[
          'Consensual aggregation',
          'Kernel',
          'Regression',
          'Statistical Aggregation'
      ],
      long_description=LONG_DESCRIPTION)