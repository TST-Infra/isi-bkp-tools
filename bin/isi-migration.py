#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from isi_bkp.entities import Groupnets, Zones, Shares, Exports, Connect, Subnets, Pools, Rules, STAGE_DIR, BACKUP_DIR, CLASS_NAMES
from json import load, dumps
from datetime import datetime
from collections import defaultdict
import argparse, os, re, sys, shutil, json

GROUPNET_ORIGEM='groupnet1'
GROUPNET_DESTINO='groupnet0'

parser = argparse.ArgumentParser(description='bkp-tools')
parser.add_argument('-u','--username', type=str, metavar='', required=False, help='Inform username to connect')
parser.add_argument('-p','--password', type=str, metavar='', required=False, help='Inform password to connect')
parser.add_argument('-url','--api_url', type=str, metavar='', required=False, help='Inform url to connect')
args = parser.parse_args()

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

def restore_all(restore_file):
    
    """
    Restaura tudo caso ocorra erro
    """

    for object_type in ['zones', 'exports', 'shares','subnets', 'pools', 'rules']:

        for file_name in restore_file[object_type]:
            print(file_name)

            isiJsonObject = None
            
            if object_type == 'zones':
                
                m = re.search(r'^(\w+)\-([\w\.\-_\d]+).json', file_name)
                
                if m:
                    tipo = m.group(1)
                    isiJsonObject = globals()[CLASS_NAMES[tipo]]()
            else:

                m = re.search(r'^(\w+)\-([\w\.\-]+)\.([\w\.\-_\d]+).json', file_name)
                
                if m:
                    tipo = m.group(1)
                    parents = m.group(2).split('.')
                    isiJsonObject = globals()[CLASS_NAMES[tipo]](parents)

            if isiJsonObject:
                isiJsonObject.restore(file_name)
            else:
                print('Erro')

def delete_all(delete):
    # remover os objetos na origem

    for object_type in ['pools','zones','subnets']:

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
                print(type(isiJsonObject))
                isiJsonObject.delete(id)
            else:
                restore_all(restore_dict)

def restore_objects_in_original_groupnet(original_groupnet):
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


if __name__ == "__main__":

    if args.username and args.password and args.api_url:
        Connect.set_connection_params(username = args.username, password = args.password, api_url = args.api_url)
    
    stage_json = dict()                 # dict de objetos JSON nos arquivos da area de STAGE (file_name -> json)
    new_objects = nested_dict(1, list)  # dict de objetos JSON modificados para a carga (object_type -> json)
    restore_dict = nested_dict(1, list) # dict de files para a restauracao (object_type -> file_name)
    shares_zone_map = dict()            # map de shares para cada zone (share path -> zone name)

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
            object_type = m_no_parents.group(1)
        
            # se for zone, a groupnet esta no objeto
            if object_type == "zones" and json_object['groupnet'] == GROUPNET_ORIGEM:
                
                groupnet_zones.append(json_object['name'])
                json_object['groupnet'] = GROUPNET_DESTINO

                new_objects[object_type].append(json_object)
                restore_dict[object_type].append(file_name)

    for file_name, json_object in stage_json.items():
        # caso tenha parent
        m_parents = re.search(r'^(\w+)\-([\w\.\-]+)\.[\w\.\-_\d]+.json', file_name)
        
        if m_parents:
            object_type = m_parents.group(1)
            parents = m_parents.group(2).split('.')
            
            # se for export ou share, a identificacao sera feita pela zone
            if object_type in ["exports", "shares"]:
                if parents[0] in groupnet_zones: 
                    new_objects[object_type].append(json_object)
                    restore_dict[object_type].append(file_name)

                    if object_type == 'shares':
                        shares_zone_map[json_object['path']] = parents[0]

            # se for objeto de rede, a groupnet esta no nome do arquivo
            elif object_type in ['subnets', 'pools', 'rules']:
                if parents[0] == GROUPNET_ORIGEM:
                    json_object['id'] = json_object['id'].replace(GROUPNET_ORIGEM, GROUPNET_DESTINO)
                    new_objects[object_type].append(json_object)
                    restore_dict[object_type].append(file_name)


# criar os objetos no destino

    for object_type in ['zones','shares','exports','subnets','pools','rules']:

        for json_object in new_objects[object_type]:

            if object_type == 'shares':
                zone_name = shares_zone_map[json_object['path']]    
                shares = Shares([zone_name])
                shares.create(json_object)
            elif object_type == 'exports':
                zone_name = json_object['zone']
                exports = Exports([zone_name])
                exports.create(json_object)
            elif object_type == 'zones':
                zone_id = json_object['id']
                zone = Zones()
                zone.create(json_object)
            elif object_type == 'subnets':
                id_sub = (json_object['id'])
                m = re.search(r'^(\w+)\.([\w\.\-]+)', id_sub)
                parents = m.group(1)
                subnet = Subnets([parents])
                subnet.create(json_object)
            elif object_type == 'pools':
                id_pool = (json_object['id'])
                m = re.search(r'^(\w+)\.(\w+)', id_pool)
                parents = m.group(2)
                pool = Pools(parents)
                pool.create(json_object)

    # restaurar tudo
    # restore_all(restore_dict)

    # deletar tudo
    # delete_all(restore_dict)
    