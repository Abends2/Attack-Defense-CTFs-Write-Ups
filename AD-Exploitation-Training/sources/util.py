import hmac
import hashlib
import time
import math
import os
import logging as l  # noqa: E741
import re

from Crypto.Cipher import AES

HMAC_DIGEST = hashlib.sha256
B62CHARSET = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
FLAG_LEN = 31
FLAG_RE = re.compile(b'^[a-zA-Z0-9]{%d}=$' % FLAG_LEN)
RAW_LEN = math.floor(FLAG_LEN * math.log(62) / math.log(256))
BLOCK_SIZE = 16
CURR_TIME_LEN = 4
SERVICE_ID_LEN = 2
TEAM_ID_LEN = 2
if BLOCK_SIZE - CURR_TIME_LEN - SERVICE_ID_LEN - TEAM_ID_LEN < 0:
    raise Exception("too much info for one AES block")
if RAW_LEN - BLOCK_SIZE < 7:
    raise Exception("can't use less than 7 bytes for the HMAC")
if 'SECRET_KEY' not in os.environ:
    l.warning('''Using default SECRET_KEY. It is suggested to provide your '''
              '''own via the environment variable SECRET_KEY instead.''')
SECRET_KEY = os.getenv('SECRET_KEY', 'SUPERsecretKEYaaaaaaaaa').encode()


def keys_for_password(pw):
    enc_key = hashlib.pbkdf2_hmac('sha256', pw, b"enc_key_salt!!!!!", 1000, 16)
    int_key = hashlib.pbkdf2_hmac('sha256', pw, b"int_key_salt?????", 1000)
    return enc_key, int_key


ENC_KEY, INT_KEY = keys_for_password(SECRET_KEY)


def b62encode(in_, len_=None):
    x = int.from_bytes(in_, 'little')
    out = b""
    i = 0
    while True:
        if len_ is not None and i >= len_:
            break
        if len_ is None and x == 0:
            break
        out += (B62CHARSET[x % 62:(x % 62)+1])
        x //= 62
        i += 1
    return out


def b62decode(in_, out_len=None):
    in_ = list(reversed(in_))
    len_ = len(in_)
    out = 0
    for i in range(len_):
        out *= 62
        x = B62CHARSET.find(in_[i])
        if x < 0:
            raise ValueError('Invalid base62 character: 0x%x' % in_[i])
        out += x
    if out_len is None:
        out_len = math.ceil(math.log(out, 256))
    return out.to_bytes(out_len, 'little')


def gen_flag(service_id, team_id, time_=None):
    if time_ is None:
        time_ = int(time.time())

    curr_time = time_.to_bytes(CURR_TIME_LEN, 'little')
    service_id = service_id.to_bytes(SERVICE_ID_LEN, 'little')
    team_id = team_id.to_bytes(TEAM_ID_LEN, 'little')
    padding = b'0'*(BLOCK_SIZE - CURR_TIME_LEN - SERVICE_ID_LEN - TEAM_ID_LEN)
    msg_to_encrypt = curr_time + service_id + team_id + padding
    aes = AES.new(ENC_KEY, AES.MODE_ECB)
    msg_to_sign = aes.encrypt(msg_to_encrypt)

    hmac_digest = hmac.new(INT_KEY, msg_to_sign, HMAC_DIGEST).digest()
    signature = hmac_digest[:RAW_LEN - BLOCK_SIZE]
    flag = b62encode(msg_to_sign + signature, FLAG_LEN) + b'='
    return flag


def verify_flag(flag, valid_secs=5):
    raw_flag = b62decode(flag[:-1], RAW_LEN)
    signed = raw_flag[:BLOCK_SIZE]
    hmac_digest = hmac.new(INT_KEY, signed, HMAC_DIGEST).digest()
    signature = hmac_digest[:RAW_LEN - BLOCK_SIZE]
    signature_from_msg = raw_flag[BLOCK_SIZE:]

    if not hmac.compare_digest(signature_from_msg, signature):
        return 'invalid', None

    aes = AES.new(ENC_KEY, AES.MODE_ECB)
    decrypted = aes.decrypt(signed)

    time_from_msg = int.from_bytes(decrypted[:CURR_TIME_LEN], 'little')
    decrypted = decrypted[CURR_TIME_LEN:]
    service_id = int.from_bytes(decrypted[:SERVICE_ID_LEN], 'little')
    decrypted = decrypted[SERVICE_ID_LEN:]
    team_id = int.from_bytes(decrypted[:TEAM_ID_LEN], 'little')

    if int(time.time()) - time_from_msg >= valid_secs:
        return 'expired', (service_id, team_id)
    return 'valid', (service_id, team_id)
