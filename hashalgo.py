from enum import IntEnum
from pathlib import Path
import hashlib

class hash_function_t(IntEnum):
    MD5 = 0
    SHA1 = 1
    SHA256 = 2
    SHA384 = 3
    SHA512 = 4

class hash_function_data:
    def __init__(self):
        self.function_type = hash_function_t.SHA256
        self.target = ""

def generate_hash(hash):
    if(Path(hash.target).is_file() == False):
        return ""
    hasher = None
    if(hash.function_type == hash_function_t.SHA1):
        hasher = hashlib.sha1()
    elif(hash.function_type == hash_function_t.SHA256):
        hasher = hashlib.sha256()
    elif(hash.function_type == hash_function_t.SHA384):
        hasher = hashlib.sha384()
    elif(hash.function_type == hash_function_t.SHA512):
        hasher = hashlib.sha512()
    elif(hash.function_type == hash_function_t.MD5):
        hasher = hashlib.md5()
    else:
        raise Exception("Invalid hash type passed: " + hash.function_type)
    file = open(hash.target, "rb")
    hasher.update(file.read())
    return hasher.hexdigest()