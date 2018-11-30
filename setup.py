"""
used to create pypi package to make the nephos module pip installable
"""

from os import path
import subprocess
import platform
from setuptools import setup


# =============================================
# version information

VERSION = (0, 0, 1)
VERSION_SUFFIX = 'under.dev'
VERSION_STRING = ".".join(str(x) for x in VERSION)
RELEASE_STRING = VERSION_STRING + " " + VERSION_SUFFIX

# make changes above when deploying new version
# =============================================


__title__ = "Nephos"
__description__ = "Nephos - Capture streams, process them and upload to cloud storage"
__author__ = "Shivam Kumar Jha (github@thealphadollar)"
__author_mail__ = "shivam.cs.iit.kgp+Nephos@gmail.com"  # TODO: Update author's mail address
__license__ = "GNU GPL v3"
__version__ = VERSION_STRING
__release__ = RELEASE_STRING


def update_version():
    """
    Rewrites version information to `/nephos/ver_info.py` on every new deployment.

    Returns
    -------

    """
    info = '''# -*- coding: utf-8 -*-

"""
Stores basic version information about the project
"""

# =====================================
# THIS FILE WAS GENERATED AUTOMATICALLY
# =====================================
#

VER_INFO = """
__title__ = 'Nephos'
__description__ = 'Nephos - Capture streams, process them and upload to cloud storage'
__author__ = 'Shivam Kumar Jha (github@thealphadollar)'
__author_mail__ = 'shivam.cs.iit.kgp+Nephos@gmail.com'
__license__ = 'GNU GPL v3'
__version__ = '0.0.1'
__release__ = '0.0.1 under.dev'"""
'''.format(
        title=__title__,
        description=__description__,
        author=__author__,
        author_mail=__author_mail__,
        license=__license__,
        version=__version__,
        release=__release__,
    )
    outfile = path.join('nephos', 'ver_info.py')

    with open(outfile, 'w+', encoding='utf-8') as ver_file:
        ver_file.write(info)


def read(file_name):
    """
    Reads data from file for the description parameter of `setup()`.

    Parameters
    ----------
    file_name: str
        path to the README.md file.

    Returns
    -------
    str
        the text contained in the given file.

    """
    with open(file_name, mode='r') as readme:
        return readme.read()


# update version information before launching setup
update_version()

DISTRO = platform.dist()[0]
if DISTRO == "CentOS":
    subprocess.run("sudo ./install.sh")
elif DISTRO in ['debian', 'ubuntu']:
    subprocess.run("sudo ./debian_install.sh")
else:
    print('I cannot run installation script!')

setup(
    name=__title__,
    version=__version__,
    url="https://github.com/thealphadollar/Nephos.wiki",
    download_url="https://github.com/thealphadollar/Nephos",
    license=__license__,
    author=__author__,
    author_email=__author_mail__,
    description=__description__,
    long_description=read('README.md'),
    keywords='network stream closed_captions subtitles',
    install_requires=[
        'pydash',
        'coloredlogs',
        'PyYAML',
        'click',
        'apscheduler',
        'sqlalchemy',
        'oauth2client',
        'google-api-python-client'
    ],
    setup_requires=[
	'pytest-runner'
    ],
    test_requires=[
        'pytest',
        'mock',
        'unittest'
    ],
    entry_points={
        'console_scripts': ['nephos=nephos:main']
    },
    zip_safe=False,
    include_package_data=True
)
