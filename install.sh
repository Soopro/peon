#!/bin/bash

for arg in $@
do
  if [ $arg = "-p" -o $arg = "--packages" ]
    then
      echo 'Setup Peon with reuiqred packages'
      sudo pip3 install -r requirements.txt
      sudo npm install -g coffeescript less uglify-js
  fi
done

sudo python3 setup.py install
