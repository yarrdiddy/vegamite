from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import sandman

here = os.path.abspath(os.path.dirname(__file__))


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
	version=vegamite.__version__,
	url='https://github.com/yarrdiddy/vegamite',
	license='MIT License',
	author='David Reynolds',
	tests_require=['pytest'],
	install_requires=['Flask>=0.10.1',
                    'Flask-SQLAlchemy>=1.0',
                    'SQLAlchemy==0.8.2',
                ],
    cmdclass={'test': PyTest},
    author_email='d.reynoldz@gmail.com',
    description='Simple trading bot for cryptocurrency trading.',
    long_description=long_description,
    packages=['vegamite'],
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


