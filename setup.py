import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requirements = ["requests==2.18.4", "celery==4.2.1"]

setup(
    author="picostocks",
    author_email='',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1.1',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    description=("This is an official Python django module for sync price "
                 "from pickostock.com"),
    install_requires=requirements,
    license="MIT license",
    long_description=README,
    include_package_data=True,
    keywords='pico picostocks exchange rest api bitcoin ehtereum btc eth',
    name='djangopicoframework',
    packages=find_packages(),
    version='0.1',
)
