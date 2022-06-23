#!/bin/bash

base_url="http://archive.routeviews.org/bgpdata/$(date -u +%Y).$(date -u +%m)/RIBS/"

fn="rib.$(date -u +%Y%m%d).$(printf %02d $(($(date -u +%H)-$(date -u +%H)%2)))00"

wget "$base_url$fn.bz2"

bzip2 -d "$fn.bz2"

python3 main.py $fn
