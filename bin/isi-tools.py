#!/usr/bin/python3

"""

"""

from isi_bkp.entities import (
    Groupnets, Zones, Shares, Exports, Aliases, Connect, Pools, Rules, Quotas, STAGE_DIR, BACKUP_DIR, CLASS_NAMES
)
from json import dumps, load
from datetime import datetime
import argparse, os, re, sys, shutil

parser = argparse.ArgumentParser(description='Script to backup and restore Isilon Configurations')
parser.add_argument('-b','--backup', action="store_true", help='backup all objects')
parser.add_argument('-r','--restore', type=str, metavar = '', help='restore a backup file in ' + BACKUP_DIR)
parser.add_argument('-l','--list', type=str, metavar = '', help='list backups in ' + BACKUP_DIR + ' (use "all" to list all files)')
parser.add_argument('-u','--username', type=str, metavar='', required=False, help='Inform username to connect')
parser.add_argument('-p','--password', type=str, metavar='', required=False, help='Inform password to connect')
parser.add_argument('-url','--api_url', type=str, metavar='', required=False, help='Inform url to connect')
args = parser.parse_args()

def dump_conf_to_stage():
    """
    Dump Isilon configurations to filesystem
    """
    # cria os diretorios, se nao existirem
    for dir_path in [STAGE_DIR, BACKUP_DIR]:
        if not os.path.isdir(dir_path): 
            os.makedirs(dir_path)

    # backup de groupnets e filhos
    groupnets = Groupnets()
    groupnets.backup()

    # backup de zones
    zones = Zones()
    zones.backup()

    # backup de quotas
    quotas = Quotas()
    quotas.backup()

    # para cada zone, backup de exports, shares e aliases
    for zone in zones.objects:

        share = Shares([zone['name']])
        share.backup()

        exports = Exports([zone['name']])
        exports.backup()

        aliases = Aliases([zone['name']])
        aliases.backup()

def backup():
    """
    Backup all configured objects in Isilon
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

                    # se quotas, remover a chave usage
                    #TODO dar uma solucao mais estilosa para esse problema do backup de quotas
                    if 'quotas' in file_name:
                        stage_json.pop('usage', None)
                        backup_json.pop('usage', None)

                    if stage_json != backup_json:
                        old_version_file_path = os.path.join(BACKUP_DIR, '%s_%s.json' %(file_name[:-5],stringDate))
                        shutil.move(file_path_backup, old_version_file_path)

                        shutil.copyfile(file_path_stage, file_path_backup)

        else: 
            
            shutil.copyfile(file_path_stage, file_path_backup)
            os.remove(file_path_stage)

def restore(file_name):
    """
    Restore a isilon object using a backup file
    """
    # expressao regular adaptada para o caso de objetos que possuem parents
    m_parents = re.search(r'^(\w+)\-([\w\.\-]+)\.[\w\.\-_\d]+.json', file_name)

    # expressao regular adaptada para o caso de objetos que nao possuem parents (zones e groupnets)
    m_no_parents = re.search(r'^(\w+)\-[\w\.\-_\d]+.json', file_name) 

    if m_parents:
        tipo = m_parents.group(1)
        parents = m_parents.group(2).split('.')
        isiJsonObject = globals()[CLASS_NAMES[tipo]](parents)
        isiJsonObject.restore(file_name)
    elif m_no_parents:
        tipo = m_no_parents.group(1)
        isiJsonObject = globals()[CLASS_NAMES[tipo]]()
        isiJsonObject.restore(file_name)

def list_backup(filter):
    """
    List all backups 
    """
    for file_name in os.listdir(BACKUP_DIR):
        if filter in file_name or filter == 'all':
            print(file_name)

if __name__ == "__main__":
    
    if args.username and args.password and args.api_url:
        Connect.set_connection_params(username = args.username, password = args.password, api_url = args.api_url)

    if args.backup:
        backup()
    elif args.restore:
        restore(args.restore)
    elif args.list:
        list_backup(args.list) 
    else:
        sys.exit(0)