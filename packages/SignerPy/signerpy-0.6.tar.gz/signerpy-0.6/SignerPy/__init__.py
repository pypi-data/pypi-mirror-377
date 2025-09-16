from SignerPy.argus  import *
from SignerPy.ladon  import *
from SignerPy.gorgon import *
from SignerPy import md5, ladon, argus, gorgon
from random import choice
from urllib.parse import urlencode
import hmac, uuid, random, binascii, os, secrets, time, hashlib

def sign(params=None, data=None, url=None, device_id='', aid=1233, license_id=1611921764, 
                       sdk_version_str='v04.04.05-ov-android', sdk_version=134744640, 
                       platform=0, cookie=''):
    x_ss_stub = hashlib.md5(urlencode(data).encode()).hexdigest() if data else None
    ticket = time.time()
    unix = int(ticket)
    
    if not device_id:
        trace = (
            str("%x" % (round(ticket * 1000) & 0xffffffff))
            + "10"
            + "".join(choice('0123456789abcdef') for _ in range(16))
        )
    else:
        trace = (
    device_id.encode('utf-8').hex()
    + "".join(choice('0123456789abcdef') for _ in range(2))
    + "0"
    + hex(aid)[2:]
)

    if params is None and url:
        url, param_str = url.split('?', 1)
        params = dict(p.split('=') for p in param_str.split('&'))
    elif params is None:
        params = {}

    if data is None:
        data = ''
    if cookie is None:
        cookie = ''
    if not unix:
        unix = time.time()
    if aid is None:
        aid = int(params.get('aid', 1233))
       
    if params:
     params = urlencode(params)
    if cookie:
        cookie = urlencode(cookie)
    if data:
        data = urlencode(data) 
    return {
        'x-argus': argus.Argus.get_sign(
            params, x_ss_stub, unix,
            platform=platform,
            aid=aid,
            license_id=license_id,
            sec_device_id=device_id,
            sdk_version=sdk_version_str,
            sdk_version_int=sdk_version
        ),
        'x-ladon': ladon.Ladon.encrypt(unix, license_id, aid),
        'x-gorgon': gorgon.get_xgorgon(
            params=params, ticket=ticket, data=data if data else "", cookie=cookie
        ),
        'x-khronos': str(unix),
        'x-ss-req-ticket': str(time.time()).replace(".", "")[:13],
        'x-tt-trace-id': f"00-{trace}-{trace[:16]}-01",
        'x-ss-stub': x_ss_stub.upper() if data else None
    }
    
    
def xor(string: str) -> str:
        return "".join([hex(ord(_) ^ 5)[2:] for _ in string]) 
        
        
        
def get(params: dict):
    params.update({
    '_rticket': int(round(time.time() * 1000)),
    'cdid': str(uuid.uuid4()),
    'ts': int(time.time()),
    'iid': str(random.randint(1, 10**19)),
    'device_id': str(random.randint(1, 10**19)),
    'openudid': str(binascii.hexlify(os.urandom(8)).decode()),
    'app_version': '35.3.2'
})
    return params

    
        
def xtoken(params=None, sessionid=None):
    
    ts = str(params.get("ts", int(time.time()))) if params else str(int(time.time()))
    if sessionid is None:
        sessionid = secrets.token_bytes(32)
    elif isinstance(sessionid, str):
        try:
            sessionid = bytes.fromhex(sessionid)
        except:
            sessionid = sessionid.encode()
    ms_token = secrets.token_hex(64)
    message = (ms_token + ts).encode() + sessionid
    x = hmac.new(sessionid, message, hashlib.sha256).hexdigest()
    
    return f"{ms_token}--{x}-3.0.0"
#L7N