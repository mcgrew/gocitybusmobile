#!/bin/bash

curl http://gocitybus.com/GTFS/google_transit.zip > google_transit.zip
unzip -o google_transit.zip
rm google_transit.zip

