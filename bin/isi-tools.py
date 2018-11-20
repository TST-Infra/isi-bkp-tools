#!/usr/bin/python3

from isi_bkp.entities import Groupnets, Zones, Shares, Exports, Pools, Rules, STAGE_DIR, BACKUP_DIR, CLASS_NAMES
from json import dumps, load
from datetime import datetime
import argparse, os, re, sys, shutil

parser = argparse.ArgumentParser(description='bkp-tools')
parser.add_argument('-b','--backup', action="store_true", help='Do backup')
parser.add_argument('-r','--restore', type = str, metavar = '', help='Do restore')
parser.add_argument('-l','--list', type = str,help='List')
parser.add_argument('-wc','--whatChanged', action="store_true" , help='What has changed?')
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

        share = Shares( {'zones': zone['name']} )
        share.backup()

        exports = Exports({'zones': zone['name']})
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