import base64
import json
import struct
import time

from Crypto.Hash import HMAC, SHA

from steampy.confirmation import Tag


def load_steam_guard(steam_guard: str) -> dict:
    with open(steam_guard, 'r') as f:
        return json.loads(f.read())


def generate_code(shared_secret: str) -> str:
    return generate_code_from_secret(shared_secret, int(time.time()))


def generate_code_from_secret(shared_secret: str, timestamp: int) -> str:
    time_buffer = struct.pack('>Q', timestamp // 30)  # pack as Big endian, uint64
    hmac = HMAC.new(base64.b64decode(shared_secret), time_buffer, SHA).digest()
    begin = ord(hmac[19:20]) & 0xf
    full_code = struct.unpack('>I', hmac[begin:begin + 4])[0] & 0x7fffffff  # unpack as Big endian uint32
    chars = '23456789BCDFGHJKMNPQRTVWXY'
    code = ''

    for _ in range(5):
        full_code, i = divmod(full_code, len(chars))
        code += chars[i]

    return code


def generate_confirmation_key(identity_secret: str, timestamp: int = time.time(), tag: Tag = Tag.ALLOW) -> str:
    buffer = struct.pack('>Q', timestamp) + tag.value.encode('ascii')
    return base64.b64encode(HMAC.new(base64.b64decode(identity_secret), buffer, SHA).digest())


def generate_device_id(steam_id: str) -> str:
    hexed_steam_id = SHA.new(steam_id.encode('ascii')).hexdigest()
    return 'android:' + '-'.join([hexed_steam_id[:8],
                                 hexed_steam_id[8:12],
                                 hexed_steam_id[12:16],
                                 hexed_steam_id[16:20],
                                 hexed_steam_id[20:32]])
