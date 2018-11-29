#!/usr/bin/python3

from isi_bkp.entities import Groupnets, Zones, Shares, Exports, Connect, Pools, Rules, STAGE_DIR, BACKUP_DIR, CLASS_NAMES
from json import dumps, load
from datetime import datetime
import argparse, os, re, sys, shutil

parser = argparse.ArgumentParser(description='bkp-tools')
parser.add_argument('-b','--backup', action="store_true", help='Do backup')
parser.add_argument('-r','--restore', type = str, metavar = '', help='Do restore')
parser.add_argument('-l','--list', type = str,help='List',metavar = '')
parser.add_argument('-wc','--whatChanged', action="store_true" , help='What has changed')
parser.add_argument('-u','--username', type=str, metavar='', required=False, help='Inform username to connect')
parser.add_argument('-p','--password', type=str, metavar='', required=False, help='Inform password to connect')
parser.add_argument('-url','--api_url', type=str, metavar='', required=False, help='Inform url to connect')
parser.add_argument('-m','--migration', action="store_true", help='Migration process')
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

def listAll(filter = 'all'):
    """

    """
    for file_name in os.listdir(BACKUP_DIR):
        a = file_name
        b = a.split()
        for string in b:
            if filter in string:
                print (string)
            elif filter == 'all':
                print(string)

def whatChanged():
    """

    """
    
    # TO DO - o que foi modificado no arquivo

    dump_conf_to_stage()

    for file_name in os.listdir(STAGE_DIR):

        file_path_stage = os.path.join(STAGE_DIR, file_name)
        file_path_backup = os.path.join(BACKUP_DIR, file_name)

        if os.path.isfile(file_path_backup):
            
            with open(file_path_stage) as stage_fh:
                with open(file_path_backup) as backup_fh:
                    stage_json = load(stage_fh)
                    backup_json = load(backup_fh)

                    if stage_json != backup_json:
                        print(file_name)
                    else:
                        print('No files have been modified')
                        break

        else: 
            sys.exit(0)

        os.remove(file_path_stage)

def migration():
    """

    """
    # Abrindo os arquivos para pegar zones, shares e exports
    for file_name in os.listdir(BACKUP_DIR):
        
        b = os.path.join(BACKUP_DIR, file_name)
        
        if os.path.isfile(b):
            
            with open(b) as backup_fh:
                file_json = load(backup_fh)
                print(file_json['id'])

        else:
            print("erro")

if __name__ == "__main__":
    
    Connect.set_connection_params(username = args.username, password = args.password, api_url = args.api_url)

    if args.backup:
        backup()
    elif args.restore:
        restore(args.restore)
    elif args.list:
        listAll(args.list) 
    elif args.whatChanged:
        whatChanged()
    elif(args.migration):
        migration()
    else:
        sys.exit(0)