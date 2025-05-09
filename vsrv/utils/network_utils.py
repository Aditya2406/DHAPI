'''
    vsys - Network Utilities
'''
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

class NetworkEncryption():
    '''
        Network Encryption
    '''
    PublicKey = 'Keys/public.key'

    @staticmethod
    def rsa_encrypt( msg:str = ''):
        '''
            RSA Encryption
        '''
        rkey = RSA.import_key(open(NetworkEncryption.PublicKey,encoding="UTF-8").read())
        crsa = PKCS1_v1_5.new(rkey)
        msg_bytes = bytes(msg,encoding='UTF-8')
        esk = crsa.encrypt(msg_bytes)
        eskb64 = base64.b64encode(esk)
        return eskb64
