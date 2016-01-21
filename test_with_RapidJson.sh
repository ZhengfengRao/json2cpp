#!/bin/bash

./json2cpp.py rapidjson sample.jsf test
cd test/test/
cp ../Makefile.rapidjson ./Makefile
make clean
make
./test
