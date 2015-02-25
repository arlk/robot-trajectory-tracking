#!/bin/bash

# Before executing add the directory of processing-py.sh and, 
# pathgen_processing directory to your PATH environment variable
process=processing-py.sh
pathgen=pathgen.py
udpsend=udps.py #USE ONLY WHEN SENDING SIMULATION DATA

echo "UDP simulation data sending..."
exec ${udpsend} &	

echo "UDP receiving..."
echo "Starting simulation..."
${process} ${pathgen}

# Use the following cmd if program crashes 
# to stop udps.py to send data continously:
# kill -9 `ps -ef | grep python | grep -v grep | awk '{print $2}'`