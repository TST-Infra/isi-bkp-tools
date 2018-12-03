#!/usr/bin/python3

from isi_bkp.entities import Groupnets, Zones, Shares, Exports, Connect, Pools, Rules, STAGE_DIR, BACKUP_DIR, CLASS_NAMES
from json import dumps, load
from datetime import datetime
import argparse, os, re, sys, shutil, json

parser = argparse.ArgumentParser(description='migration')
parser.add_argument('-u','--username', type=str, metavar='', required=False, help='Inform username to connect')
parser.add_argument('-p','--password', type=str, metavar='', required=False, help='Inform password to connect')
parser.add_argument('-url','--api_url', type=str, metavar='', required=False, help='Inform url to connect')
args = parser.parse_args()

def dump_conf_to_stage():
    """

    """
    # cria os diretorios, se nao existirem
    for dir_path in [STAGE_DIR, BACKUP_DIR]:
        if not os.path.isdir(dir_path): 
            os.mkdir(dir_path)

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

def backup():
    """

    """
    dump_conf_to_stage()
    stringDate = datetime.now().strftime("%Y%m%d_%H%M")

    # copia dos arquivos para a area de backup
    for file_name in os.listdir(STAGE_DIR):

        file_path_stage = os.path.join(STAGE_DIR, file_name)
        file_path_backup = os.path.join(BACKUP_DIR, file_name)

        if os.path.isfile(file_path_backup):
            
            with open(file_path_stage) as stage_fh:
                with open(file_path_backup) as backup_fh:
                    stage_json = load(stage_fh)
                    backup_json = load(backup_fh)

                    if stage_json != backup_json:
                        old_version_file_path = os.path.join(BACKUP_DIR, '%s_%s.json' %(file_name[:-5],stringDate))
                        shutil.move(file_path_backup, old_version_file_path)

                        shutil.copyfile(file_path_stage, file_path_backup)

        else: 
            
            shutil.copyfile(file_path_stage, file_path_backup)
            os.remove(file_path_stage)

def restore(file_name):
    """

    """
    m = re.search(r'^(\w+)\-([\w\.\-]+)\.[\w\.\-_\d]+.json', file_name)
    
    if m:
        tipo = m.group(1)
        parents = m.group(2).split('.')
        isiJsonObject = globals()[CLASS_NAMES[tipo]](parents)
        isiJsonObject.restore(file_name)

def migration():
    
    # Backup de tudo
    # backup() 
    # isi = IsiJson()
    # isi.migration()

    # Compilação do que migrar - nesse caso fiz um dump que contém todas as informações
    for file_name in os.listdir(BACKUP_DIR):

        files = os.path.join(BACKUP_DIR, file_name)

        print(files)

        if os.path.isfile(files):
            with open(files) as dump_file:
                
                # objeto do tipo dict
                files_json = load(dump_file)

                # Pegar zones, shares e exports
                # Zones - pegar zones
                print(files_json.get('zone'))

                # Dump do arquivo
                print(files_json)
                


if __name__ == "__main__":

    Connect.set_connection_params(username = args.username, password = args.password, api_url = args.api_url)
    migration()