#!/bin/bash

pip3 install numpy

cd ../elasticsearch-7.6.2
./bin/elasticsearch -d

cd

cd OSP_Project-master

flask run
