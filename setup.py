from setuptools import setup, find_packages

description = 'django-ssheepdog is a public ssh key management tool for teams of programmers'
long_desc = open('README.rst').read()

setup(
    name='django-ssheepdog',
    version='0.1.4',
    url='https://github.com/SheepDogInc/django-ssheepdog',
    install_requires=[
        'django-celery',
        'django-kombu',
        'south',
        'ssh'
    ],
    description=description,
    long_description=long_desc,
    include_package_data=True,
    author='SheepDogInc',
    author_email='development@sheepdoginc.ca',
    packages=find_packages(),
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development'
    ]
)
