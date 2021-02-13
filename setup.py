import sys
import os
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
import conf
from version import __version__
from setuptools import setup, find_packages

# Get aw_client in path
# AW_CLIENT_DIR = Path(__file__).parent / 'aw-client' / 'aw_client'
# AW_CLIENT_OUT_DIR = Path(__file__).parent / 'aw_watcher_project' / 'aw_client'
# if AW_CLIENT_OUT_DIR.exists():
#     shutil.rmtree(AW_CLIENT_OUT_DIR)
# shutil.copytree(AW_CLIENT_DIR, AW_CLIENT_OUT_DIR)

extra_kwargs = {}

entry_points = None
if conf.CONSOLE_SCRIPTS:
    entry_points = dict(console_scripts=conf.CONSOLE_SCRIPTS)
    
extras_require = None
if conf.OPTIONAL_PACKAGE_INSTALL_REQUIRES:
    extras_require = conf.OPTIONAL_PACKAGE_INSTALL_REQUIRES

long_description = conf.PACKAGE_DESCRIPTION
if conf.PACKAGE_DESCRIPTION.strip().lower() == 'auto':
    with open('README.md', 'r') as f:
        long_description = f.read()
    extra_kwargs['long_description_content_type'] = 'text/markdown'
setup(
    name=conf.PACKAGE_NAME,
    version=__version__,
    description=conf.PACKAGE_SHORT_DESCRIPTION,
    long_description=long_description,
    author=conf.PACKAGE_AUTHOR,
    author_email=conf.PACKAGE_AUTHOR_EMAIL,
    license=conf.PACKAGE_LICENSE,
    packages=find_packages(),
    include_package_data=True,
    classifiers=conf.PACKAGE_CLASSIFIERS,
    install_requires=conf.PACKAGE_INSTALL_REQUIRES,
    extras_require=extras_require,
    project_urls=conf.PACKAGE_URLS,
    url=conf.PACKAGE_URLS['Code'],
    scripts=conf.SCRIPTS,
    entry_points=entry_points,
    **extra_kwargs
)