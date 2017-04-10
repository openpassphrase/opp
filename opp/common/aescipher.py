import base64
import hashlib

from Crypto.Cipher import AES
from Crypto import Random


BS = 16


def pad(s):
    padding = BS - len(s) % BS
    return s + (padding * chr(padding)).encode('utf-8')


def unpad(s):
    return s[0:-ord(s.decode('utf-8')[-1])]


# Usage:
#   cipher = aescipher.AESCipher('secret passphrase')
#   encrypted = cipher.encrypt('My Secret Message')
#   decrypted = cipher.decrypt(encrypted)
class AESCipher(object):
    """AES cipher utility class for encrypting/decrypting data."""

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode('utf-8')).digest()

    def encrypt(self, raw):
        raw = pad(raw.encode('utf-8'))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:])).decode('utf-8')
