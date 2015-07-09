#!/bin/bash

for arg in $@
do
  if [ $arg == "-i" -o $arg == "init" ]
    then
      echo 'Start init Peon'
      sudo pip install -r requirements.txt
      sudo npm install -g coffee-script jade less
      sudo gem install sass
  fi
done

sudo python setup.py install
