#!/bin/bash

git clone https://github.com/open-source-parsers/jsoncpp.git
cd jsoncpp/
mkdir -p build/debug
cd build/debug
cmake -DCMAKE_BUILD_TYPE=debug -DBUILD_STATIC_LIBS=ON -DBUILD_SHARED_LIBS=OFF -DARCHIVE_INSTALL_DIR=. -G "Unix Makefiles" ../..
make
cd ../../
mkdir lib
cp build/debug/src/lib_json/libjsoncpp.a lib/
cd ..
./json2cpp.py jsoncpp sample.jsf test
cd test/test/
cp ../Makefile.jsoncpp ./Makefile
make clean
make
./test
