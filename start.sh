#!/bin/bash

pip install numpy
pip install nltk

cd /elasticsearch-7.6.2
./bin/elasticsearch -d
cd

cd OSP_Project-master

flask run
