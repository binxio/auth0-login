"""
CLI for obtaining JWT access tokens using the PKCE flow
"""
from setuptools import find_packages, setup

dependencies = ['boto3', 'pyjwt', 'click']

setup(
    name='oauth-cli',
    version="0.1.1",
    url='https://github.com/binxio/oauth-cli',
    license='Apache Software License (http://www.apache.org/licenses/LICENSE-2.0)',
    author='Mark van Holsteijn',
    author_email='mark@binx.io',
    description='utility to obtain an JWT access token using OAuth PKCE flow',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    tests_require=dependencies + ['pytest'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'oauth-cli = oauth_cli.__main__:cli',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
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
