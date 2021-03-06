import re

from setuptools import setup

with open('daiquiri_tap/__init__.py') as f:
    metadata = dict(re.findall(r'__(.*)__ = [\']([^\']*)[\']', f.read()))

setup(
    name=metadata['title'],
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['email'],
    maintainer=metadata['author'],
    maintainer_email=metadata['email'],
    license=metadata['license'],
    url='https://github.com/aipescience/django-daiquiri-tap',
    description=u'Daiquiri Tap is a tiny wrapper for astroquery, adding support for token authorization.',
    long_description=open('README.rst').read(),
    install_requires=[
        'astroquery>=0.3.7'
    ],
    classifiers=[],
    packages=['daiquiri_tap'],
    include_package_data=True
)
