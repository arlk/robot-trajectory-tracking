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

echo "Deleting temporary files.."
rm -rf temp*

echo "Killing UDP simulator"
kill `ps a | grep udps.py | awk '{print $1}'`

echo "Finished. Find your trajectory files stored as robot_traj_id:1/2/3.txt etc"