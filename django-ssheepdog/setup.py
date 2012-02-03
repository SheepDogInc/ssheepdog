from setuptools import setup

description = 'ssheepdog'
long_desc = description

setup(
    name='ssheepdog',
    version='0.0.1',
    url='https://github.com/SheepDogInc/ssheepdog',
    install_requires=[
        'django-celery',
        'django-kombu',
        'south',
        'ssh'
    ],
    description=description,
    long_description=long_desc,
    author='SheepDogInc',
    author_email='info@sheepdoginc.ca',
    packages=['ssheepdog']
)
