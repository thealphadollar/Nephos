#!/usr/bin/env bash

echo " | \ | | ___ _ __ | |__   ___  ___  "
echo " |  \| |/ _ \ '_ \| '_ \ / _ \/ __| "
echo " | |\  |  __/ |_) | | | | (_) \__ \ "
echo " |_| \_|\___| .__/|_| |_|\___/|___/ "
echo "            |_|                     "
DISTRO=$(awk '/^ID=/' /etc/*-release | awk -F'=' '{ print tolower($2) }') # Finding Linux distribution
echo "The Linux distribution is $DISTRO"
DISTRO="${DISTRO,,}" # converting to lower case
if [[ $DISTRO == "ubuntu" ]]
then
  sudo ./debian_install.sh $DISTRO
elif [[ $DISTRO == "centos" ]]
then
  sudo ./centos_install.sh
fi  
