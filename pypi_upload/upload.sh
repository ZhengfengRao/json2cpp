#!/bin/bash

python setup.py bdist_egg
python setup.py sdist
python setup.py register
python setup.py sdist upload
