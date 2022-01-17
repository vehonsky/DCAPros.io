#!/usr/bin/env python
import base64
import yaml
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2

def main():

    with open('../../credentials.yaml', 'r') as file: #needs to be real path on virtual machine for apache2 to run
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

    def decrypt(enc, password):
        private_key = get_private_key(password)
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))

    # First let us encrypt secret message
    encrypted = encrypt("t7uT9aU/4B8d8Y1N9imyJFWgW6d+6jnwknjgn2sVJvOoLAbDO+SGURTqC7NVUX+A0f9IiZA5upf5luczMM/ZuA==", password)
    print(encrypted.decode("utf8"))

    # Let us decrypt using our original password
    decrypted = decrypt(encrypted, password)
    print(bytes.decode(decrypted))

if __name__ == "__main__":
    main()


