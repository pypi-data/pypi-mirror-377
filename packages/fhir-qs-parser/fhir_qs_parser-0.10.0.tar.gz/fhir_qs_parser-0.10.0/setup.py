import os
from setuptools import setup

NAME = 'fhir_parse_qs'

with open('README.md') as readme:
    README = readme.read()
    README_TYPE = "text/markdown"

with open(os.path.join(NAME, 'VERSION')) as version:
    VERSION = version.readlines()[0].strip()

# Fallback setup.py for legacy installers; primary metadata lives in pyproject.toml
REQUIREMENTS = [
    'pendulum>=3',
]

setup(
    name='fhir-qs-parser',
    version=VERSION,
    description='Parse FHIR query strings',
    long_description=README,
    long_description_content_type=README_TYPE,
    url='https://github.com/xjodoin/fhir_parse_qs',
    author='teffalump',
    author_email='chris@teffalump.com',
    packages=['fhir_parse_qs'],
    install_requires=REQUIREMENTS,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent'
    ],
)
