#!/usr/bin/env python2.7

import os.path
import setuptools

import mci

_APP_PATH = os.path.dirname(mci.__file__)

with open(os.path.join(_APP_PATH, 'resources', 'README.rst')) as f:
      _LONG_DESCRIPTION = f.read()

with open(os.path.join(_APP_PATH, 'resources', 'requirements.txt')) as f:
      _INSTALL_REQUIRES = list(map(lambda s: s.strip(), f))

setuptools.setup(
    name='magento_check_images',
    version=mci.__version__,
    description="Check for bad product images in Magento",
    long_description=_LONG_DESCRIPTION,
    classifiers=[],
    keywords='',
    author='Dustin Oprea',
    author_email='dustin@randomingenuity.com',
    url='https://github.com/CoffeeForThinkers/MagentoCheckImages',
    license='GPL3',
    packages=setuptools.find_packages(exclude=['dev']),
    include_package_data=True,
    zip_safe=False,
    install_requires=_INSTALL_REQUIRES,
    package_data={
        'mci': [
            'resources/README.rst',
            'resources/requirements.txt',
        ],
    },
    scripts=[
        'mci/resources/scripts/mci_check_images',
    ],
)
