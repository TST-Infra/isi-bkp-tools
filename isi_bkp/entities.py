import requests, urllib3, os, re, sys
from json import dumps, load

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

STAGE_DIR = '/opt/isi-bkp-tools/stage'
BACKUP_DIR = '/opt/isi-bkp-tools/backup'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Connect():
    """

    """

    username = 'root'
    password = 'laboratory'
    api_url  = 'https://labisilon-mgr.rede.tst:8080/platform'

    def set_connection_params(**kwargs):
        Connect.username = kwargs['username']
        Connect.password = kwargs['password']
        Connect.api_url  = kwargs['api_url']

class IsiJson(object):
    """

    """
    json_attribute_name = None
    parents = []
    children = []
    objects = []
    exclude_keys_for_restore = []

    def __init__(self, parents = []):
        """

        """
        self.parents = parents

    def __str__(self):
        """

        """
        return 'Objeto Isilon tipo %s' % (self.json_attribute_name)

    def print_username(self):
        print(Connect.username)

    def url(self):
        return Connect.api_url

    def _exclude_keys_from_json(self, json_object):
        """

        """
        for key in self.exclude_keys_for_restore:
            json_object.pop(key, None)
            
        return json_object

    def generate_dump_name(self, sub_object_id):
        """

        """
        return '%s-%s.json' % (self.json_attribute_name, sub_object_id)

    def backup(self):
        """

        """
        self.set_objects()

        for object_data in self.objects:
            dump_path = '%s/%s' % (STAGE_DIR, self.generate_dump_name(object_data['id']))
            fh_json = open(dump_path,'w')
            fh_json.write(dumps(object_data))
            fh_json.close()

        if len(self.children):
            self.backup_children()

    def set_objects(self):
        """

        """
        response = requests.get(self.get_api_call_string(), auth=(Connect.username, Connect.password), verify=False)

        if response.status_code == 200:
            
            data = response.json()
            self.objects = data[self.json_attribute_name]

        else: 
            sys.exit('error 404')

    def backup_children(self):
        """

        """
        for object_data in self.objects:
            
            object_name = object_data['name']

            for child_attribute in self.children:

                if len(object_data[child_attribute]):
                    
                    parents = self.parents
                    parents.append(object_name)

                    child_object = globals()[CLASS_NAMES[child_attribute]](parents)
                    child_object.backup()

    def get_api_call_string(self):
        """

        """
        return Connect.api_url + API_CALLS[self.json_attribute_name]

    def restore(self, backup_file_name):
        """

        """
        file_path_backup = os.path.join(BACKUP_DIR, backup_file_name)

        if os.path.isfile(file_path_backup):
            
            with open(file_path_backup) as backup_fh:
                
                backup_json = self._exclude_keys_from_json(load(backup_fh))

                response = requests.post(self.get_api_call_string(), auth=(Connect.username, Connect.password), verify=False, data = dumps(backup_json))

                if response.status_code == 201:
                    print('Restore concluido com sucesso')
                else:
                    print('Falha no processo de restore')
                    print(response.text)

    # Método que faz o processo de criação dos arquivos json
    def create(self, data):

        response = requests.put(self.get_api_call_string(), auth=(Connect.username, Connect.password, verify=False), data = dumps(data))
        if response.status_code == 201:
            print('201 Created')
        else:
            print('error 404')
            print(response.text)


    # Requisição para processo de deleção dos arquivos jsons
    def delete(self, file_json):

        # os arquivos tem que ser deletados em ordem, e caso haja qualquer erro, o processo de bkp deve acontecer

        response = requests.delete(self.get_api_call_string(), auth=(Connect.username, Connect.password), verify=False, data = dumps(file_json))
        if response.status_code == 204:
            print('Arquivos deletados com sucesso')
        else:
            print('Falha ao deletar')
            print(response.text)


class Groupnets(IsiJson):
    """

    """
    json_attribute_name = 'groupnets'
    exclude_keys_for_restore = ['id', 'subnets']
    children = ['subnets']

class Subnets(IsiJson):
    """

    """
    json_attribute_name = 'subnets'
    exclude_keys_for_restore = ['base_addr', 'groupnet', 'id', 'pools']
    children = ['pools']

    def get_api_call_string(self):
        """

        """
        return super().get_api_call_string() % (self.parents[0])

class Pools(IsiJson):
    """

    """
    json_attribute_name = 'pools'
    exclude_keys_for_restore = ['addr_family', 'groupnet', 'id', 'rules', 'sc_suspended_nodes', 'subnet']
    children = ['rules']

    def get_api_call_string(self):
        """

        """
        return super().get_api_call_string() % (self.parents[0], self.parents[1])

class Rules(IsiJson):
    """

    """
    json_attribute_name = 'rules'
    exclude_keys_for_restore = ['groupnet', 'id', 'pool', 'subnet']


    def get_api_call_string(self):
        """

        """
        return super().get_api_call_string() % (self.parents[0], self.parents[1], self.parents[2])

class Zones(IsiJson):
    """

    """
    json_attribute_name = 'zones'
    exclude_keys_for_restore = ['id', 'zone_id', 'system']

    def _exclude_keys_from_json(self, json_object):
        """

        """
        json_object = super()._exclude_keys_from_json(json_object)

        auth_providers = []

        for auth_provider in json_object['auth_providers']:
            
            m = re.search(r'lsa\-local\-provider',auth_provider)
            
            if not m:
                auth_providers.append(auth_provider)

        json_object['auth_providers'] = auth_providers

        return json_object

    
class Shares(IsiJson):
    """

    """
    json_attribute_name = 'shares'
    exclude_keys_for_restore = ['id', 'zid']

    def get_api_call_string(self):
        """

        """
        return super().get_api_call_string() % (self.parents[0])

    def generate_dump_name(self, sub_object_id):
        """

        """
        return '%s-%s.%s.json' % (self.json_attribute_name, self.parents[0], sub_object_id)

class Exports(IsiJson):
    """

    """
    json_attribute_name = 'exports'
    exclude_keys_for_restore = ['conflicting_paths', 'id', 'unresolved_clients']


    def get_api_call_string(self):
        """

        """
        return super().get_api_call_string() % (self.parents[0])

    def generate_dump_name(self, sub_object_id):
        """

        """
        return '%s-%s.%s.json' % (self.json_attribute_name, self.parents[0], sub_object_id)
        