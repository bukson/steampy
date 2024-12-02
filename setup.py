
from setuptools import setup

version = '1.1.2'

setup(
    name='steampy',
    packages=['steampy', 'test', 'examples' ],
    version=version,
    description='A Steam lib for trade automation',
    author='Michał Bukowski',
    author_email='gigibukson@gmail.com',
    license='MIT',
    url='https://github.com/bukson/steampy',
    download_url='https://github.com/bukson/steampy/tarball/' + version,
    keywords=['steam', 'trade' ],
    classifiers=[],
    install_requires=[
        "requests",
        "beautifulsoup4",
        "rsa",
    ],
)
