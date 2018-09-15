from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client

class FDFSStorage(Storage):
    def _open(self, name, mode='rb'):
        pass
    def __init__(self, client_conf=None, base_url=None):
        '''inicial'''
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url

    def _save(self,name,content):
        """save file"""
        # name = file name  content is a object of file

        #must compare with dailfresh pwd

        client = Fdfs_client(self.client_conf)

        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }

        res = client.upload_by_buffer(content.read())

        if res.get('Status') != 'Upload successed.':

            raise Exception('upload fast dfs wrong')

            # acquire and return ID, this should saved in your excel
        filename = res.get('Remote file_id')
        # print(filename)
        return filename


    def exists(self, name):

        return False

    def url(self, name):

        return self.base_url+name







