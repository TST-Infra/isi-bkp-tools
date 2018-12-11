#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from isi_bkp.entities import STAGE_DIR, CLASS_NAMES, Groupnets, Zones, Shares, Exports
from json import load, dumps
from datetime import datetime
from collections import defaultdict
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



def nested_dict(n, type):
    """ 
    Cria dicionario multidimensional
    """
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n-1, type))

#def has_parent():

#def without_parent():


if __name__ == "__main__":
    #Connect.set_connection_params(username = args.username, password = args.password, api_url = args.api_url)
    
    stage_json = dict()    # dict de objetos JSON nos arquivos da area de STAGE (file_name -> json)
    new_objects = nested_dict(1, list) # dict de objetos JSON modificados para a carga (object_type -> json)
    restore_dict = nested_dict(1, list) # dict de files para a restauracao (object_type -> file_name)

    create_dict = nested_dict(1, list)

    groupnet_zones = list()

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

    # identificar objetos a serem migrados e criar um novo dict, jah com os dados alterados
    
    for file_name, json_object in stage_json.items():
        # caso não tenha parent
        m_no_parents = re.search(r'^(\w+)\-[\w\.\-_\d]+.json', file_name) 
        
        if m_no_parents:
            type_object = m_no_parents.group(1)
        
            # se for zone, a groupnet esta no objeto
            if type_object == "zones" and json_object['groupnet'] == GROUPNET_ORIGEM:
                
                groupnet_zones.append(json_object['name'])
                json_object['groupnet'] = GROUPNET_DESTINO

                new_objects[type_object].append(json_object)
                restore_dict[type_object].append(file_name)

                # Dados da zone com groupnet alterado
                print(dumps(json_object))
                #print('zone')

    for file_name, json_object in stage_json.items():
        # caso tenha parent
        m_parents = re.search(r'^(\w+)\-([\w\.\-]+)\.[\w\.\-_\d]+.json', file_name)
        
        if m_parents:
            type_object = m_parents.group(1)
            parents = m_parents.group(2).split('.')
            
            # se for export ou share, a identificacao sera feita pela zone
            if type_object in ["exports", "shares"]:
                if parents[0] in groupnet_zones: 
                    new_objects[type_object].append(json_object)
                    restore_dict[type_object].append(file_name)

                    print(dumps(json_object))
                    #print('exports e shares')

            # se for objeto de rede, a groupnet esta no nome do arquivo
            elif type_object in ['subnets', 'pools', 'rules']:
                if parents[0] == GROUPNET_ORIGEM:
                    json_object['id'] = json_object['id'].replace(GROUPNET_ORIGEM, GROUPNET_DESTINO)
                    new_objects[type_object].append(json_object)
                    restore_dict[type_object].append(file_name)

    # remover os objetos na origem 
    # isi = IsiJson()
    # isi.delete(json_object)

    for object_type in ['shares', 'exports', 'zones', 'rules', 'pools', 'subnets']:
        
        for file_name in restore_dict[object_type]:

            isiJsonObject = None
            id = None

            if object_type == 'zones':
                
                m = re.search(r'^(\w+)\-([\w\.\-_\d]+).json', file_name)
                
                if m:
                    tipo = m.group(1)
                    id = m.group(2)
                    isiJsonObject = globals()[CLASS_NAMES[tipo]]()
                    
            else:
                m = re.search(r'^(\w+)\-([\w\.\-]+)\.([\w\.\-_\d]+).json', file_name)

                if m:
                    tipo = m.group(1)
                    parents = m.group(2).split('.')
                    id = m.group(3)
                    isiJsonObject = globals()[CLASS_NAMES[tipo]](parents)
                    
            if isiJsonObject:
                isiJsonObject.delete(id) # tratar excecao se houver erro no delete
            else:
                # TODO gerar excecao se nao houver o objeto criado
                None

    # criar os objetos no destino
    # isi.create(json_object)

    # se der merda, restaura tudo
    # restore_objects_in_original_groupnet(restore_files)
