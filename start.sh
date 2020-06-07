#!/bin/bash

if [ -d ./dir ] ;then
	rm -rf dir
fi
mkdir -p dir/templates
mkdir dir/uploads

cp app.py dir
cp cal.py dir
cp index.html dir/templates

cd dir
chmod 755 app.py
chmod 755 cal.py

flask run
