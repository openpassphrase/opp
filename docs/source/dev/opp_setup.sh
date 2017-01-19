#!/usr/bin/env bash

# Fix "unable to resolve host" when running sudo commands
machine=`uname -a | awk '{print $2}'`
sudo sed -i "s/^127.0.0.1 localhost[ ]*$/127.0.0.1 localhost $machine/" /etc/hosts

# Update package distros
sudo apt-get update

# Enable page-up/down history search
sudo sed -i "s/^# ..e.5~.: history-search-backward$/\"\\\e[5~\": history-search-backward/" /etc/inputrc
sudo sed -i "s/^# ..e.6~.: history-search-forward$/\"\\\e[6~\": history-search-forward/" /etc/inputrc

# Add unicode support in gnome-terminal
sudo locale-gen en_US.UTF-8

# Required packages
sudo apt-get install -y python2.7-dev
sudo apt-get install -y sqlite
sudo apt-get install -y python-pip
sudo pip install -U pip # upgrade pip
sudo pip install tox # this will also install virtualenv

# Useful packages
sudo apt-get install -y git
sudo apt-get install -y vim

# Upgrade all packages with conflict resolution
sudo apt-get -y full-upgrade

if [ "$USER" != "root" ]; then
    echo
    echo "To add pasword-less sudo for current user, edit /etc/sudoers and add:"
    echo "$USER ALL=(ALL) NOPASSWD:ALL"
fi

echo
echo "You likely need to restart your machine"
