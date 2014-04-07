#!/bin/sh


# Install xeno
sudo cp xeno /usr/local/bin/xeno
which xeno
xeno daemon
ps -ef -u $(id -u) | grep xeno
