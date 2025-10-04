#!/bin/bash


sudo apt remove -y grubdeck
rm grubdeck-1.0.0-all.deb
./build-deb.sh 
sudo apt install ./grubdeck-1.0.0-all.deb 