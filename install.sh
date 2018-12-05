#!/usr/bin/env bash

sudo apt-get install figlet

echo "Nephos" | figlet

DISTRO=$(lsb_release -is) # Finding Linux distribution
echo "The Linux distribution is $DISTRO"
DISTRO="${DISTRO,,}" # converting to lower case
if [[ $DISTRO == "ubuntu" ]]
then
  sudo ./ubuntu_install.sh
elif [[ $DISTRO == "debian" ]]
then
  sudo ./debian_install.sh
elif [[ $DISTRO == "centos" ]]
then
  sudo ./centos_install.sh
fi
