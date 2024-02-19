#!/usr/bin/env python3

if test -e ./data/buses.db 
then
    python -m scraping --quiet
# Passing to y to bash from: https://stackoverflow.com/a/3385064
else 
    y | python -m scraping