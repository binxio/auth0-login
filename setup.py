# Copyright 2019 - binx.io B.V.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
"""
CLI for obtaining JWT access tokens using the PKCE flow
"""

import sys
if sys.version_info < (3,6):
    sys.exit('Sorry, Python < 3.6 is not supported')

from setuptools import find_packages, setup

dependencies = ['boto3', 'pyjwt', 'click', 'requests']

setup(
    name='auth0-login',
    version="0.4.5",
    url='https://github.com/binxio/auth0-login',
    license='Apache Software License (http://www.apache.org/licenses/LICENSE-2.0)',
    author='Mark van Holsteijn',
    author_email='mark@binx.io',
    description='CLI to obtain JWT, SAML tokens, and AWS credentials using Auth0, OAuth and SAML',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    tests_require=dependencies + ['pytest'],
    test_suite='tests',
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'saml-login = auth0_login.saml.__main__:cli',
            'pkce-login = auth0_login.pkce.__main__:cli',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
