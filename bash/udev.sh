#!/bin/bash
path=$(dirname $0)/../config/udev_rules/

#Copy the new sensor ruleset to the udev rules
sudo cp $path/99-pcsensor-tempergold.rules /etc/udev/rules.d/99-pcsensor-tempergold.rules

# Reload the udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

