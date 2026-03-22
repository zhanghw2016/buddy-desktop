'''
Created on 2012-9-17

@author: yunify
'''
import re

# At least one uppercase and one lowercase letter
# At least one number
# A length of at least six characters
PASSWD_TYPE_INST = r'^.*(?=.{8,})(?=.*[a-z])(?=.*[A-Z])(?=.*[\d]).*$'
PASSWD_TYPE_USER = r'^.*(?=.{6,})(?=.*[a-zA-Z])(?=.*[\d]).*$'
COMM_PASSWORDS = set(['kingcom5', 'qwer1234', '1qazxsw2', '123qweasd', 'ms0083jxj', '1q2w3e4r', '12345678a', '1234qwer', '123456asd', 'asdf1234', 'zxcvbnm123', '123456789a', 'woaini1314', 'a1234567', 'passw0rd', 'aa123456', '1q2w3e4r5t', '123456abc', 'code8925', 'asd123456', 'abcd1234', 'abc123456', 'a12345678', 'qq123456', 'a123456789', '123456aa', '1qaz2wsx', '1234abcd', '123456qq', 'q1w2e3r4', 'P@ssw0rd', 'Passw0rd'])
INVALID_CHARS = r'[;\s]'

def is_valid_chars(passwd):
    if re.search(INVALID_CHARS, passwd):
        return False
    return True 

def is_ascii_passwd(passwd):
    try:
        passwd = str(passwd)
        return True
    except:
        return False

def is_passwd_too_simple(passwd):
    if passwd in COMM_PASSWORDS:
        return True
    return False

def is_strong_user_passwd(passwd):
    if re.search(PASSWD_TYPE_USER, passwd):
        return True
    return False

def is_strong_inst_passwd(passwd):
    if re.search(PASSWD_TYPE_INST, passwd):
        return True
    return False

def is_strong_passwd(passwd):
    if re.search(PASSWD_TYPE_INST, passwd):
        return True
    return False

def is_cache_passwd(passwd):
    if re.match(r'^[A-Za-z0-9]*$', passwd):
        return True
    return False

def is_valid_pptp_password(passwd):
    if re.match(r'^[A-Za-z0-9]*$', passwd):
        return True
    return False