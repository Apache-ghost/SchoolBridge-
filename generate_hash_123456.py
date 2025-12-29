import secrets
import hashlib

def hash_password(password):
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('utf-8'), 
                                      100000)
    return salt + password_hash.hex()

if __name__ == "__main__":
    print(hash_password("123456"))
