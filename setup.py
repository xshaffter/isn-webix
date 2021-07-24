import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='isn-webix',
    version='0.2.4',
    packages=['isn', 'isn.models', 'isn.serializers', 'isn.serializers.fields'],
    description='Work with prepared Webix-django classes',
    long_description=README,
    author='Alfredo Martinez',
    author_email='xshaffter@gamil.com',
    url='https://github.com/xshaffter/django-isn-webix/',
    license='MIT',
    install_requires=[
        'Django>=1.11.29',
        'djangorestframework>=3.9.4',
        'api-auto-doc>=0.1.3',
        'django-post-office>=2.0.8',
    ]
)