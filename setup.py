#!/usr/bin/env python

import funniest

#setup(
#    entry_points = {
#        'console_scripts': ['']
#    } 
#)

setup(
    scripts=['bin/isi-tools']
)

def main():
    print funniest.joke()

