#!/bin/bash
echo '---- A peon start working ----'

# primary task
for arg in $@
do
  if [ $arg == "init" ]
    then
      echo '---- init ----'
      echo 'Install bower components'
      bower install
      echo 'Install node modules'
      npm install
      echo 'Copy libs intro src'
      python peon.py -c
  fi
  if [ $arg == "release" ]
    then
      echo '---- release ----'
      grunt release
      python peon.py -r
  fi
done

# seconed task
for arg in $@
do
  if [ $arg == "-d" -o $arg == "dev" ]
    then
      echo 'Start Dev'
      grunt dev
  fi
  if [ $arg == "-p" -o $arg == "preview" ]
    then
      echo 'Start Preview'
      grunt preview
  fi
done

echo '---- The peon finish his work ----'