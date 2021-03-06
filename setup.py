try:
    import multiprocessing
except ImportError:
    pass

import re
from setuptools import setup
version = 1.0

setup(
    name='ptt_crawler',
    version=version,
    url='https://github.com/allenwhale',
    license='MIT',
    author='allenwhale(Allen Wu)',
    author_email='allencat850502@gmail.com',
    packages=[
        'ptt_crawler',
    ],
    platforms='any',
    install_requires=[
        'requests>=2.5.1',
        'beautifulsoup4',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Traditional)',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
