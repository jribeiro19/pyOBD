#!/bin/sh

# This script encapsulates all Python scripts needed to run the OBD Application
# It is supose to add here any commands to be executed in the startup and for shuting down 
# the application

clear

echo "======== Drivers Identification Based On Driving Signature - DIBODS ======"
echo
#read -p "Press ENTER within 3 seconds if you want abort DIBODS: " #; echo "not aborted"; echo "aborted"



echo "Running as ....$USER"
echo

sudo python /home/pi/OBD/pyOBD/sandbox/obd_0.12/obd.py         #insert complete path


