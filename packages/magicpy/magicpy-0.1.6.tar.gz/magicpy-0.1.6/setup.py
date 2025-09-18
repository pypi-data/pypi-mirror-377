#!/usr/bin/env python
import os
import re
from pathlib import Path
from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
# read version string from __init__py
dir_path = os.path.dirname(os.path.realpath(__file__))
verstrline = open(f"{dir_path}/magicpy/__init__.py", "rt").read()
v_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(v_re, verstrline, re.M)
verstr = mo.group(1)

setup(name='magicpy',
      version=verstr,
      description='Toolbox to control MagVenture TMS stimulators',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Ole Numssen',
      author_email='numssen@posteo.de',
      project_urls={'Home': 'https://gitlab.gwdg.de/tms-localization/utils/magicpy',
                    'Docs': 'https://magicpy.readthedocs.io/',
                    'Twitter': 'https://twitter.com/num_ole',
                    'Download': 'https://pypi.org/project/magigpy/'},
      packages=['magicpy'],
      install_requires=['pyserial>=3.5', 'numpy>=1.20.0', 'pyparallel'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Science/Research',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Software Development :: Build Tools',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9', ]
      )
