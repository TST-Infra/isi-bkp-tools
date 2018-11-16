#!/usr/bin/python
# -*- coding: utf-8 -*-

from bkp import *

if __name__ == "__main__":
    
    if args.backup:
        backup()
    elif args.restore:
        restore(args.restore)
    elif args.list:
        listAll(args.list) 
    elif args.whatChanged:
        whatChanged()
    else:
        sys.exit(0)