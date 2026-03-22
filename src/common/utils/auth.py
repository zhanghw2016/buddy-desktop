'''
Created on 2012-7-9

@author: yunify
'''

import re
import base64
import hmac
import urllib
import bcrypt
from utils.misc import get_utf8_value
from log.logger import logger
from hashlib import sha1 as sha
from hashlib import md5
from hashlib import sha256 as sha256
import random,string

class HmacKeys(object):
    """Key based Auth handler helper."""

    def __init__(self, host, access_key_id, secret_access_key):
        self.host = host
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    def sign_string(self, string_to_sign):
        if self._hmac_256:
            hmac = self._hmac_256.copy()
        else:
            hmac = self._hmac.copy()
        hmac.update(string_to_sign)
        return base64.b64encode(hmac.digest()).strip()

class SignatureAuthHandler(HmacKeys):
    """Provides Console Query Signature Authentication."""

    SignatureVersion = 1

    def _calc_signature(self, params, verb, path, safe='-_~'):
        ''' calc signature for request '''
        
        algorithm = params['signature_method']
        if algorithm == "HmacSHA256":
            self._hmac_256 = hmac.new(self.secret_access_key,
                                      digestmod=sha256)
        else:
            self._hmac_256 = None
            self._hmac = hmac.new(self.secret_access_key,
                                      digestmod=sha)
        # build string to signature
        string_to_sign = '%s\n%s\n' % (verb, path)
        keys = sorted(params.keys())
        pairs = []
        for key in keys:
            val = get_utf8_value(params[key])
            pairs.append(urllib.quote(key, safe='') + '=' + urllib.quote(val, safe=safe))
        qs = '&'.join(pairs)
        string_to_sign += qs
        b64 = self.sign_string(string_to_sign)
        return (qs, b64)
    
    def check_auth(self, req, **kwargs):
        ''' check authorize information for request '''
        req_params = {}
        for k, v in req.params.items():
            req_params[k] = v
        ori_signature = req.params["signature"]
        del req_params["signature"]
        _, signature = self._calc_signature(req_params, req.method,
                                             req.path)
        if ori_signature != signature:
            _, signature = self._calc_signature(req_params, req.method, req.path, '-_~.*!\'()')
            if ori_signature != signature:
                logger.error('signature not match [%s] [%s]' % (ori_signature, signature))
                return False
        return True

_SK = "".join(['9', '=', 'r', '8', 'y', 'h', 'a', 
                'c', 'o', '5', '5', 'a', '2', '=', 
                't', 'z', 'b', 'a', 'p', '2', 'a', 
                's', 'u', '0', 'i', 'x', 'g', 'w', 
                '5', '2', '3', 'g', 'l', 'd', 'h', 
                'd', 'x', 'm', 'h', 't', 'e', '3', 
                't', 't', '9', '9', 'q', 'y', '2', 
                'y', 'q', 's', 'a', '9', 'm', '1', 
                '5', '5', '0', 'r', 'j', 'i', '2', 
                'i', '=', '9', '5', 'g', 'z', 's', 
                '0', 'n', '-', 'p', 'k', 'p', 'h', 
                'b', 's', 'h'][21:60])

def get_hashed_password(password):
    ''' hash a password using bcrypt '''
    return bcrypt.hashpw(password, bcrypt.gensalt())

def check_password(password, hashed):
    ''' Check that an unencrypted password matches one that has
        previously been hashed
    '''
    try:
        return (bcrypt.hashpw(password, hashed) == hashed)
    except Exception, e:
        logger.error('check password failed. [%s]' % (e))
        return False        

def get_md5_password(password):
    m = md5()
    m.update(password)
    return m.hexdigest()

def check_password_rule(password):
    return True if re.search("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$", password) and len(password) >= 8 else False

def gen_salt(num=6):
    return ''.join(random.sample(string.ascii_letters + string.digits, num))

def set_base64_password(password):
    logger.info("set_base64_password password == %s" %(password))

    base64_password = base64.b64encode(password)
    encrypt_base64_password = gen_salt(num=6) + base64_password + gen_salt(num=4)
    logger.info("encrypt_base64_password == %s" %(encrypt_base64_password))
    return encrypt_base64_password

def get_base64_password(password):
    # logger.info("get_base64_password password == %s" %(password))

    real_password_str = password[6:(len(password) - 4)]
    # logger.info("real_password_str == %s" %(real_password_str))
    try:
        decrypt_base64_password = base64.b64decode(real_password_str).replace('\n', '').replace('\r', '')
        # logger.info("decrypt_base64_password == %s" %(decrypt_base64_password))
    except:
        logger.error("invalid base64 password [%s]" % (real_password_str))
        return password

    return decrypt_base64_password


