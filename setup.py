#!/usr/bin/env python
#pip install funniest-joke

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

#python
#import funniest.command_line
#funniest.command_line.main()
