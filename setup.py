"""
CLI for obtaining JWT access tokens using the PKCE flow
"""
from setuptools import find_packages, setup

dependencies = ['boto3', 'pyjwt', 'click', 'requests']

setup(
    name='auth0-login',
    version="0.4.2",
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
