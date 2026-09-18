import os
import hashlib
from config import env_loead

SALT = os.getenv("PSEUDONYMIZATION_SALT").encode('utf-8')

def pseudonymize(value):
    value= str(value).strip().lower().encode('utf-8')
    return hashlib.sha256(SALT + value).hexdigest()