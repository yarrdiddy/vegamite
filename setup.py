from __future__ import print_function

import io, codecs, os, sys, re

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


here = os.path.abspath(os.path.dirname(__file__))

VERSIONFILE="src/vegamite/_version.py"

verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
match_object = re.search(VSRE, verstrline, re.M)
if match_object:
    version_str = match_object.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


def read(*filenames, **kwargs):
    return ''

long_description = read('README.txt', 'CHANGES.txt')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='vegamite',
    version=version_str,
    url='https://github.com/yarrdiddy/vegamite',
    license='MIT License',
    author='David Reynolds',
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    author_email='d.reynoldz@gmail.com',
    description='Simple trading bot for cryptocurrency trading.',
    long_description=long_description,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    platforms='any',
    test_suite='vegamite.test.test_vegamite',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 0 - alpha',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
        'testing': ['pytest'],
    }

)


