# File: setup.py
#
# This file is used to package your project so it can be
# installed with pip or uploaded to the Python Package Index (PyPI).
# You need to run this file from the root directory of your project
# (the 'thesis' folder) using a command like `python setup.py sdist bdist_wheel`.
# You will also need to have `setuptools` and `wheel` installed.

from setuptools import setup, find_packages

setup(
    name='adaptive-ml',
    version='0.1.0',
    description='A collection of adaptive machine learning algorithms for clustering.',
    author='Andreotti Stefano',
    author_email='andreotti.stefano.sa@gmail.com',
    packages=find_packages(),
    install_requires=[
        'dadapy >= 0.3.2',
        'numpy == 1.26.4', #2.3.2
        'scikit_learn >= 1.6.1', #1.7.1
        'scipy >= 1.13.1', #1.16.1
        'setuptools >= 75.8.0',
        'umap_learn >= 0.5.7'

    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    # You can also include non-code files like the ones in the 'datasets' folder
    # by uncommenting the following lines:
    # include_package_data=True,
    # package_data={
    #     'adaptive_ml_package': ['datasets/*', 'examples/*']
    # },
)
