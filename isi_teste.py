#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests, urllib3, os, glob, sys
from json import dumps, load
import shutil
from hashlib import md5
from datetime import datetime,date,time

USERNAME = 'root'
PASSWORD = 'laboratory'

API_URL = 'https://labisilon-mgr.rede.tst:8080/platform'

API_CALLS = {
    'groupnets': '/3/network/groupnets',
    'subnets': '/3/network/groupnets/%s/subnets',
    'pools': '/3/network/groupnets/%s/subnets/%s/pools',
    'rules': '/3/network/groupnets/%s/subnets/%s/pools/%s/rules',
    'zones': '/3/zones',
    'shares': '/4/protocols/smb/shares?zone=%s',
    'exports': '/4/protocols/nfs/exports?zone=%s',
}

CLASS_NAMES = {
    'groupnets': 'Groupnets',
    'subnets': 'Subnets',
    'pools': 'Pools',
    'rules': 'Rules',
    'zones': 'Zones',
}

STAGE_DIR = '/tmp/stage'
BACKUP_DIR = '/tmp/backup'
now = datetime.now()
stringDate = now.strftime("%Y%m%d_%H%M")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IsiJson(object):

    json_attribute_name = None
    parents = {}
    children = []
    objects = []
    exclude_keys_for_restore = []

    def __init__(self, parents={}):
        self.parents = parents

    def generate_dump_name(self, sub_object_id):
        return '%s-%s.json' % (self.json_attribute_name, sub_object_id)

    def backup(self):
        self.set_objects()

        for object_data in self.objects:
            dump_path = '%s/%s' % (STAGE_DIR, self.generate_dump_name(object_data['id']))
            fh_json = open(dump_path,'w')
            fh_json.write(dumps(object_data))
            fh_json.close()

        self.backup_children()

    def set_objects(self):
        response = requests.get(self.get_api_call_string(), auth=('root', 'laboratory'), verify=False)

        if response.status_code == 200:
            
            data = response.json()
            self.objects = data[self.json_attribute_name]

        else: 
            print('deu merda')

    def backup_children(self):

        for data in self.objects:
            
            object_name = data['name']

            for child_attribute in self.children:

                if len(data[child_attribute]):
                    
                    parents = self.parents
                    parents[self.json_attribute_name] = object_name

                    child_object = globals()[CLASS_NAMES[child_attribute]](parents)
                    child_object.backup()

    def get_api_call_string(self):
        return API_URL + API_CALLS[self.json_attribute_name]

    def restore(self, backup_file_name):
        
        file_path_backup = os.path.join(BACKUP_DIR, backup_file_name)

        if os.path.isfile(file_path_backup):
            
            with open(file_path_backup) as backup_fh:
                
                backup_json = load(backup_fh)

                for key in self.exclude_keys_for_restore:
                    backup_json.pop(key, None)

                print(backup_json)

                response = requests.post(self.get_api_call_string(), auth=('root', 'laboratory'), verify=False, data = dumps(backup_json))

                if response.status_code == 201:
                    print('Restore concluido com sucesso')
                else:
                    print('Falha no processo de restore')
                    print(response.text)

class Groupnets(IsiJson):

    json_attribute_name = 'groupnets'
    children = ['subnets']

class Subnets(IsiJson):

    json_attribute_name = 'subnets'
    children = ['pools']

    def get_api_call_string(self):
        return super().get_api_call_string() % (self.parents['groupnets'])

class Pools(IsiJson):

    json_attribute_name = 'pools'
    children = ['rules']

    def get_api_call_string(self):
        return super().get_api_call_string() % (self.parents['groupnets'], self.parents['subnets'])

class Rules(IsiJson):

    json_attribute_name = 'rules'

    def get_api_call_string(self):
        return super().get_api_call_string() % (self.parents['groupnets'], self.parents['subnets'], self.parents['pools'])

class Zones(IsiJson):

    json_attribute_name = 'zones'
    
class Shares(IsiJson):

    json_attribute_name = 'shares'
    exclude_keys_for_restore = ['id', 'zid']

    def get_api_call_string(self):
        return super().get_api_call_string() % (self.parents['zones'])

    def generate_dump_name(self, sub_object_id):
        return '%s-%s.%s.json' % (self.json_attribute_name, self.parents['zones'], sub_object_id)

class Exports(IsiJson):

    json_attribute_name = 'exports'

    def get_api_call_string(self):
        return super().get_api_call_string() % (self.parents['zones'])

    def generate_dump_name(self, sub_object_id):
        return '%s-%s.%s.json' % (self.json_attribute_name, self.parents['zones'], sub_object_id)

    def backup_children(self):
        return True


if __name__ == "__main__":

    for dir_path in [STAGE_DIR, BACKUP_DIR]:
        if not os.path.isdir(dir_path): 
            os.mkdir(dir_path)

    #
    # backup
    #

    # cria os dumps
    groupnets = Groupnets()
    groupnets.backup()

    zones = Zones()
    zones.backup()

    for zone in zones.objects:

        share = Shares( {'zones': zone['name']} )
        share.backup()

        exports = Exports({'zones': zone['name']})
        exports.backup()

    for file_name in os.listdir(STAGE_DIR):

        file_path_stage = os.path.join(STAGE_DIR, file_name)
        file_path_backup = os.path.join(BACKUP_DIR, file_name)

        # verifica se existe o arquivo no destino
        if os.path.isfile(file_path_backup):
            
            # se existir o arquivo, verifica se houve alteracao no arquivo
            with open(file_path_stage) as stage_fh:
                with open(file_path_backup) as backup_fh:
                    stage_json = load(stage_fh)
                    backup_json = load(backup_fh)

                    if stage_json != backup_json:
                        # Caso tenha modificação, é criado um novo arquivo, em que o mesmo consta a prefixação da data
                        old_version_file_path = os.path.join(BACKUP_DIR, '%s_%s.json' %(file_name[:-5],stringDate))
                        shutil.move(file_path_backup, old_version_file_path)

                        # e um novo arquivo é criado com os dados atuais
                        shutil.copyfile(file_path_stage, file_path_backup)

        else: 
            
            # se nao existir o arquivo, basta copiar o arquivo da area de stage para backup
            shutil.copyfile(file_path_stage, file_path_backup)
            
        # remove os arquivos da area de stage    
        os.remove(file_path_stage)
