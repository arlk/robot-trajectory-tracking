#!/bin/bash

#Address of your processing-py.sh script
process=/home/arun/Documents/processing/processing.py-0202-linux64/processing-py.sh
sampleproc=/home/arun/sketchbook/mynew/mynew.py
udpsend=/home/arun/sketchbook/mynew/udpsend.py
udprecv=/home/arun/sketchbook/mynew/udprecv.py

echo "UDP simulation data sending..."
exec ${udpsend} &

echo "UDP receiving..."
echo "Starting simulation..."
exec ${sampleproc}