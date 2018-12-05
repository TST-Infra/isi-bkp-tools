#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from isi_bkp.entities import *
from json import dumps, load
from datetime import datetime
import argparse, os, re, sys, shutil, json


def migration():
    
    # Backup de tudo
    # backup() 
    # isi = IsiJson()
    # isi.migration()

    # Compilação do que migrar - nesse caso fiz um dump que contém todas as informações
    for file_name in os.listdir(BACKUP_DIR):

        files = os.path.join(BACKUP_DIR, file_name)

        if os.path.isfile(files):
            with open(files) as dump_file:
                
                # objeto do tipo dict
                files_json = load(dump_file)

                # Pegar zones, shares e exports
                # Zones - pegar zones
                # print(files_json.get('zone'))

                # preparação dos jsons
                print(files_json)

def teste():
    isi = IsiJson()
    isi.migration()


if __name__ == "__main__":
    #Connect.set_connection_params(username = args.username, password = args.password, api_url = args.api_url)
    migration()