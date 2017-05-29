#!/bin/bash

for arg in $@
do
  if [ $arg = "-p" -o $arg = "--packages" ]
    then
      echo 'Setup Puss-In-Boots with reuiqred packages'
      sudo pip install -r requirements.txt
      sudo npm install -g coffee-script less uglify-js
  fi
done

sudo python setup.py install
