from setuptools import setup

description = 'django-ssheepdog is a public ssh key management tool for teams of programmers'
long_desc = open('README.rst').read()

setup(
    name='django-ssheepdog',
    version='0.1.0',
    url='https://github.com/SheepDogInc/django-ssheepdog',
    install_requires=[
        'django-celery',
        'django-kombu',
        'south',
        'ssh'
    ],
    description=description,
    long_description=long_desc,
    author='SheepDogInc',
    author_email='development@sheepdoginc.ca',
    packages=['ssheepdog']
)
