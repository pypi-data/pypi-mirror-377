import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def generate_16_byte_key(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).digest()
    return sha256_hash[:16]


def generate_32_byte_key(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).digest()
    return sha256_hash[:32]


input_string = "Katonic@U7OS4o0mren8OHsIibbKOvekpJHx3T2020"
key = generate_32_byte_key(input_string)
iv = generate_16_byte_key(input_string)


def decrypt_encryption_seed(text):
    encrypted_data = bytes.fromhex(text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode("utf-8")