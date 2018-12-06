#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from isi_bkp.entities import STAGE_DIR, Groupnets, Zones, Shares, Exports
from json import load
from datetime import datetime
import argparse, os, re, sys, shutil, json

GROUPNET_ORIGEM='groupnet1'
GROUPNET_DESTINO='groupnet0'

def dump_conf_to_stage():
    """
    Carrega os JSONs na area de stage
    """
    if not os.path.isdir(STAGE_DIR): 
        os.mkdir(STAGE_DIR)

    # backup de groupnets e filhos
    groupnets = Groupnets()
    groupnets.backup()

    # backup de zones
    zones = Zones()
    zones.backup()

    # para cada zone, backup de exports e shares
    for zone in zones.objects:

        share = Shares([zone['name']])
        share.backup()

        exports = Exports([zone['name']])
        exports.backup()

def restore_objects_in_original_groupnet(restore_files):
    """
    Carrega os objetos na sua conf padrão na Groupnet de origem (restaure controlado)
    """


if __name__ == "__main__":
    #Connect.set_connection_params(username = args.username, password = args.password, api_url = args.api_url)
    
    stage_json = dict()    # dict de objetos JSON nos arquivos da area de STAGE (file_name -> json)
    restore_files = list() # list de arquivos a serem restaurados no advento de uma falha do script

    # dump das configurações para a area de STAGE
    dump_conf_to_stage()

    # le todos os JSONs na area de stage
    for file_name in os.listdir(STAGE_DIR):

        file_path = os.path.join(STAGE_DIR, file_name)

        if os.path.isfile(file_path):
            with open(file_path) as stage_fh:
                stage_json[file_name] = load(stage_fh)

    # for file_name, json_object in stage_json.items():
    #     print ('No arquivo %s o ID eh %s' % (file_name, stage_json[file_name]['id']))

    # identificar objetos a serem migrados e criar um novo dict
    
    for file_name, json_object in stage_json.items():
        m = re.search(r'^(\w+)\-([\w\.\-]+)\.[\w\.\-_\d]+.json', file_name)
        match = m.group(1)
        type_object = m.group(2).split('.')
        print(type_object)


        # verificar se trata-se de groupnet e ignorar caso positivo
        if(type_object == "groupnets"):
            print('testando: '+type_object)

        # se for zone, a groupnet esta no objeto
        elif(type_object == "zones"):
            print('groupnet is on object')

        # se for export ou share, a identificacao sera feita pela zone
        elif(type_object == "exports" or type_object == "share"):
            print('identification by zone')

        # se for objeto de rede, a groupnet esta no nome do arquivo
        else:
            print('its in the file name')

    # fazer as alterações para criar os objetos no novo groupnet 

    # remover os objetos na origem 

    # criar os objetos no destino

    # se der merda, restaura tudo
    restore_objects_in_original_groupnet(restore_files)
