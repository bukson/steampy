from distutils.core import setup
import sys

if not sys.version_info[0] == 3 and sys.version_info[1] < 5:
    sys.exit('Python < 3.5 is not supported')

setup(
    name='steampy',
    packages=['steampy'],
    version='0.1',
    description='A Steam interaction lib',
    author='Michał Bukowski',
    author_email='gigibukson@gmail.com',
    license='MIT',
    url='TODO',
    download_url='TODO',
    keywords=['steam'],
    classifiers=[],
    install_requires=[
        "requests",
        "beautifulsoup4",
        'pycrypto'
    ],
)
