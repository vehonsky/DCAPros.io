#!/usr/bin/env python
import base64
import yaml
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2

def encrypt_before_storing(string_to_encrypt):

    with open('/Users/jvehonsk/Documents/GitHub/DCAPros.io/credentials.yaml', 'r') as file: #needs to be real path on virtual machine for apache2 to run
        credentials = yaml.safe_load(file)

    BLOCK_SIZE = 16
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    password = credentials['ENCRYPTION']['WOUND']

    def get_private_key(password):
        salt = credentials['ENCRYPTION']['SALT'].encode("utf8")
        kdf = PBKDF2(password, salt, 64, 1000)
        key = kdf[:32]
        return key

    def encrypt(raw, password):
        private_key = get_private_key(password)
        raw = pad(raw).encode("utf8")
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    encrypted = encrypt(string_to_encrypt, password)
    print(encrypted.decode("utf8"))
    encrypted = encrypted.decode("utf8")
    return encrypted
    
def decrypt_before_use(encrypted_string):
    
    with open('/Users/jvehonsk/Documents/GitHub/DCAPros.io/credentials.yaml', 'r') as file: #needs to be real path on virtual machine for apache2 to run
        credentials = yaml.safe_load(file)

    BLOCK_SIZE = 16
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    password = credentials['ENCRYPTION']['WOUND']

    def get_private_key(password):
        salt = credentials['ENCRYPTION']['SALT'].encode("utf8")
        kdf = PBKDF2(password, salt, 64, 1000)
        key = kdf[:32]
        return key

    def decrypt(enc, password): #Takes an encrypted plaintext value from encrypt(raw,password) and decrypts it to the original plaintext: for storage in database
        private_key = get_private_key(password)
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        decryptedByteString = unpad(cipher.decrypt(enc[16:]))
        #decryptedString = decryptedByteString.decode("utf8")
        return decryptedByteString

    encrypted_bytes = encrypted_string.encode("utf8")
    decrypted = decrypt(encrypted_bytes, password)
    decrypted = decrypted.decode("utf8")
    return decrypted

if __name__ == "__main__":
    encrypted = encrypt_before_storing("Hello World")
    decrypted = decrypt_before_use(encrypted)


