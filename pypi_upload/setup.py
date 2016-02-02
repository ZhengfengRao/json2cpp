from setuptools import setup, find_packages

setup(
    name = 'json2cpp',
    version = '1.0.0',
    keywords = ('JSON', 'C++'),
    description = 'A tool for JSON & C++ Mapping',
    license = 'BSD License',
    install_requires = ['pyparsing>=2.0.1'],
    author = 'nasacj',
    author_email = 'cj.nasa@gmail.com',
    packages = find_packages(),
    platforms = 'any',
)
