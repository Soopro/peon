#!/bin/bash
echo '---- Catching a Peon ----'
git pull
echo '---- The Peon is in cage ----'

# installation
file="/usr/local/bin/peon.py"
install=true

for arg in $@
do
  if [ $arg == "pass" -o $arg == '-p' ]
    then
      install=false
  fi
done

if [ -f "$file" ] && [ "$install" = true ]
then
  sh install.sh
fi