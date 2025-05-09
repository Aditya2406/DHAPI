'''
    Cryptography Utility
'''
import base64
from Crypto.Hash import HMAC, SHA256, SHA512


def encrypt_artist_key(text: str) -> str:
    '''
        Encrypt artist Information
    '''
    _salt_ = '!*!JHGGS-jktlu*!*'

    salt_bytes = _salt_.encode(encoding='utf-32-le')
    text_bytes = text.encode(encoding='utf-32-le')

    hmac = HMAC.new(key=salt_bytes, digestmod=SHA512)
    hmac.update(msg=text_bytes)
    hdeg = hmac.digest()

    htext = base64.b64encode(hdeg).decode('utf-8')
    return htext


def encrypt_player_key(text: str) -> str:
    '''
        Encrypt Player Information
    '''
    salt = '!*!JHGGS-jktlu*!*'.encode()
    hmac = HMAC.new(key=salt, digestmod=SHA256)
    hmac.update(
        text.encode('utf-8')
    )
    htext = hmac.hexdigest()
    return htext


def encrypt_vsecure_key(text: str) -> str:
    '''
        Encrypt vsecure Information
    '''
    salt = '!*!JHGGS-jktlu*!*'.encode()
    hmac = HMAC.new(key=salt, digestmod=SHA256)
    hmac.update(
        text.encode('utf-8')
    )
    htext = hmac.hexdigest()
    return htext
