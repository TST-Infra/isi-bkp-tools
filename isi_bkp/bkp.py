from entities import *
import argparse, os, re

parser = argparse.ArgumentParser(description='bkp-tools')
parser.add_argument('-b','--backup', action="store_true", help='Do backup')
parser.add_argument('-r','--restore', type = str, metavar = '', help='Do restore')
parser.add_argument('-l','--list', type = str,help='List')
parser.add_argument('-wc','--whatChanged', action="store_true" , help='What has changed?')
args = parser.parse_args()

groupnets = Groupnets()
zones = Zones()

def backup():

    for dir_path in [STAGE_DIR, BACKUP_DIR]:
        if not os.path.isdir(dir_path): 
            os.mkdir(dir_path)

    groupnets.backup()
    zones.backup()

    for zone in zones.objects:

        share = Shares( {'zones': zone['name']} )
        share.backup()

        exports = Exports({'zones': zone['name']})
        exports.backup()

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

def restore(file_name):
    try:
        m = re.search(r'^(\w+)\-', file_name)
        tipo = m.group(1)
        objeto = globals()[CLASS_NAMES[tipo]]()
        groupnets.restore(file_name)
    except:
        print('Error')

def listAll(filter = 'all'):
    for file_name in os.listdir(BACKUP_DIR):
        a = file_name
        b = a.split()
        for string in b:
            if filter in string:
                print (string)
            elif filter == 'all':
                print(string)

def whatChanged():
    
    for dir_path in [STAGE_DIR, BACKUP_DIR]:
        if not os.path.isdir(dir_path): 
            os.mkdir(dir_path)

    groupnets.backup()
    zones.backup()

    for zone in zones.objects:

        share = Shares( {'zones': zone['name']} )
        share.backup()

        exports = Exports({'zones': zone['name']})
        exports.backup()

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