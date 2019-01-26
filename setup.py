from setuptools import find_packages, setup

with open('bitsv/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('= ')[1].strip("'")
            break

setup(
    name='bitsv',
    version=version,
    description='Bitcoin SV made easier.',
    long_description=open('README.rst', 'r').read(),
    author='AustEcon',
    author_email='AustEcon0922@gmail.com',
    maintainer='AustEcon',
    maintainer_email='sega01@go-beyond.org',
    url='https://github.com/AustEcon/bitsv',
    download_url='https://github.com/AustEcon/bitsv/tarball/{}'.format(version),
    license='MIT',

    keywords=[
        'bitcoinsv',
        'bsv',
        'bitcoin sv',
        'cryptocurrency',
        'payments',
        'tools',
        'wallet',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],

    install_requires=['coincurve>=4.3.0', 'requests', 'cashaddress==1.0.4'],
    extras_require={
        'cli': ('appdirs', 'click', 'privy', 'tinydb'),
        'cache': ('lmdb', ),
    },
    tests_require=['pytest'],

    packages=find_packages(),
    entry_points={
        'console_scripts': (
            'bitsv = bitsv.cli:bitsv',
        ),
    },
)
