"""
Pontus
------

Flask utility for signing Amazon S3 POST requests and validating Amazon S3
files.
"""

import os
import re
import subprocess

from setuptools import Command, setup


def get_version():
    filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'pontus',
        '__init__.py'
    )
    contents = open(filename).read()
    pattern = r"^__version__ = '(.*?)'$"
    return re.search(pattern, contents, re.MULTILINE).group(1)


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)


extras_require = {
    'test': [
        'flexmock>=0.9.7',
        'freezegun>=0.1.18',
        'py>=1.4.20',
        'pytest>=2.5.2',
        'moto>=1.3.7',
    ]
}


setup(
    name='Pontus',
    version=get_version(),
    url='https://github.com/fastmonkeys/pontus',
    author='Vesa Uimonen',
    author_email='vesa@fastmonkeys.com',
    description='Flask utility for Amazon S3.',
    license='MIT',
    packages=['pontus'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.10.1',
        'python-magic>=0.4.6',
        'boto3>=1.4.7'
    ],
    extras_require=extras_require,
    cmdclass={'test': PyTest},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
