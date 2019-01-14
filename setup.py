# Copyright 2019 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3
import sys
import os
import platform

import setuptools


with open("hafnian/_version.py") as f:
    version = f.readlines()[-1].split()[-1].strip("\"'")


requirements = [
    "numpy",
]


setup_requirements = [
    "numpy"
]


BUILD_EXT = True

try:
    import numpy as np
    from numpy.distutils.core import setup
    from numpy.distutils.extension import Extension
except ImportError:
    raise ImportError("ERROR: NumPy needs to be installed first. "
                      "You can install it with pip:"
                      "\n\npip install numpy")


if BUILD_EXT:

    USE_CYTHON = True
    try:
        from Cython.Build import cythonize
        ext = 'pyx'
    except:
        USE_CYTHON = False
        cythonize = lambda x: x
        ext = 'cpp'


    library_default = ""
    USE_OPENMP = True
    EIGEN_INCLUDE = [os.environ.get("EIGEN_INCLUDE_DIR", ""), "/usr/local/include/eigen3", "/usr/include/eigen3"]

    LD_LIBRARY_PATH = os.environ.get('LD_LIBRARY_PATH', library_default).split(":")
    C_INCLUDE_PATH = os.environ.get('C_INCLUDE_PATH', "").split(":") + [np.get_include()]  + EIGEN_INCLUDE + ["src"]

    if platform.system() == 'Windows':
        USE_OPENMP = False
        cflags_default = "-static -O3 -Wall -fPIC"
        extra_link_args = ["-std=c++11 -static", "-static-libgfortran", "-static-libgcc"]
    elif platform.system() == 'Darwin':
        cflags_default = "-O3 -Wall -fPIC -shared -Xpreprocessor -fopenmp -lomp -mmacosx-version-min=10.9"
        extra_link_args = ['-fopenmp']
        extra_include = ['/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include/c++/v1/']
    else:
        cflags_default = "-O3 -Wall -fPIC -shared -fopenmp"
        extra_link_args = ['-fopenmp']

    CFLAGS = os.environ.get('CFLAGS', cflags_default).split() + ['-I{}'.format(np.get_include())]

    LD_LIBRARY_PATH = [i for i in LD_LIBRARY_PATH if i]
    libraries = []

    USE_LAPACK = False
    if os.environ.get("USE_LAPACK", ""):
        USE_LAPACK = True
        CFLAGS += [" -llapacke -DLAPACKE=1"]
        libraries += ["lapacke"]
        extra_link_args[0] += " -llapacke"

    if os.environ.get("USE_OPENBLAS", ""):
        USE_LAPACK = True
        CFLAGS += [" -lopenblas -DLAPACKE=1"]
        libraries += ["openblas"]
        extra_link_args[0] += " -lopenblas"

    extensions = cythonize([
            Extension("libperm",
                sources=["src/permanent.F90"],
                include_dirs=C_INCLUDE_PATH,
                library_dirs=['/usr/lib', '/usr/local/lib'] + LD_LIBRARY_PATH,
                extra_compile_args=CFLAGS,
                extra_link_args=extra_link_args),
            Extension("libhaf",
                sources=["hafnian/hafnian."+ext,],
                depends=["src/hafnian.hpp"],
                include_dirs=C_INCLUDE_PATH,
                library_dirs=['/usr/lib', '/usr/local/lib'] + LD_LIBRARY_PATH,
                libraries=libraries,
                language="c++",
                extra_compile_args=["-std=c++11"] + CFLAGS,
                extra_link_args=extra_link_args)
    ], compile_time_env={'_OPENMP': USE_OPENMP, 'LAPACKE': USE_LAPACK})
else:
    extensions = []


info = {
    'name': 'hafnian',
    'version': version,
    'maintainer': 'Xanadu Inc.',
    'maintainer_email': 'nicolas@xanadu.ai',
    'url': 'http://xanadu.ai',
    'license': 'Apache License 2.0',
    'packages': [
                    'hafnian',
                    'hafnian.tests'
                ],
    'description': 'Open source library for hafnian calculation',
    'long_description': open('README.rst').read(),
    'provides': ["hafnian"],
    'install_requires': requirements,
    'ext_package': 'hafnian.lib',
    'setup_requires': setup_requirements,
    'ext_modules': extensions,
    # 'cmdclass': {'build_ext': build_ext},
    'command_options': {
        'build_sphinx': {
            'version': ('setup.py', version),
            'release': ('setup.py', version)}}
}

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
    "Topic :: Scientific/Engineering :: Physics"
]

setup(classifiers=classifiers, **(info))
