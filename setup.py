#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Scott Atkins",
    author_email='scott@kins.dev',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Quickly decode assets for RPG Maker MV, even if you don't have the key",
    entry_points={
        'console_scripts': [
            'rpgmaker_mv_decoder=rpgmaker_mv_decoder.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='rpgmaker_mv_decoder',
    name='rpgmaker_mv_decoder',
    packages=find_packages(include=['rpgmaker_mv_decoder', 'rpgmaker_mv_decoder.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kins-dev/rpgmaker_mv_decoder',
    version='0.1.0',
    zip_safe=False,
)