##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup
"""
import os.path

from setuptools import setup


def read_file(*args):
    path = os.path.join(*args)
    with open(path) as f:
        return f.read() + '\n\n'


setup(
    name='zc.sourcefactory',
    version='3.0',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.dev',
    url='https://github.com/zopefoundation/zc.sourcefactory',
    keywords='zope vocabulary source factory',
    description='An easy way to create custom Zope sources.',
    license='ZPL-2.1',
    long_description=(
        read_file('README.rst') +
        '\n\n.. contents::\n\n' +
        read_file('src', 'zc', 'sourcefactory', 'README.txt') +
        read_file('src', 'zc', 'sourcefactory', 'mapping.txt') +
        read_file('src', 'zc', 'sourcefactory', 'constructors.txt') +
        read_file('src', 'zc', 'sourcefactory', 'adapters.txt') +
        read_file('src', 'zc', 'sourcefactory', 'browser', 'README.txt') +
        read_file('src', 'zc', 'sourcefactory', 'browser', 'token.txt') +
        read_file('CHANGES.txt')
    ),
    classifiers=[
        'Topic :: Software Development',
        'Framework :: Zope :: 3',
        'Framework :: Zope :: 4',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    python_requires='>=3.9',
    install_requires=[
        'ZODB',
        'persistent',
        'setuptools',
        'zope.intid',
        'zope.browser',
        'zope.component',
        'zope.dublincore',
        'zope.interface',
        'zope.proxy',
        'zope.publisher',
        'zope.schema',
    ],
    extras_require={
        'test': [
            'zope.component[zcml]',
            'persistent >= 4.4.3',
            'zope.site',
            'zope.testing',
            'zope.testrunner >= 6.4',
            'zope.keyreference',
        ]},
    zip_safe=False,
)
