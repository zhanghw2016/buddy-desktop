'''
Created on 2012-7-12

@author: yunify
'''

import random
import uuid
from log.logger import logger
import db.constants as dbconst

UUID_TYPE_DESKTOP_GROUP = "dgroup"
UUID_TYPE_DESKTOP_GROUP_NETWORK = "dgnet"
UUID_TYPE_DESKTOP_GROUP_DISK = "dgdisk"
UUID_TYPE_DESKTOP = "desktop"
UUID_TYPE_DESKTOP_IMAGE = "dimg"
UUID_TYPE_DESKTOP_DISK = "disk"
UUID_TYPE_DESKTOP_NETWORK = "vxnet"
UUID_TYPE_DESKTOP_JOB = "job"
UUID_TYPE_DESKTOP_TASK = "task"
UUID_TYPE_SNAPHSOT_GROUP = "snapgroup"
UUID_TYPE_SNAPSHOT_RESOURCET = "dsnapshot"
UUID_TYPE_SNAPSHOT_GROUP_SNAPSHOT = "snapgpsnap"
UUID_TYPE_SNAPSHOT_DISK_SNAPSHOT = "snapdisksnap"

UUID_TYPE_DESKTOP_USER = "dusr"
UUID_TYPE_DESKTOP_OU = "dou"
UUID_TYPE_DESKTOP_USER_GROUP = "dug"
UUID_TYPE_VDI_SYSTEM_LOG = "vlog"
UUID_TYPE_VDI_DESKTOP_MESSAGE = "vmsg"

UUID_TYPE_APPLY_FORM = "apy"
UUID_TYPE_APPLY_GROUP_FORM = "apyg"
UUID_TYPE_APPROVE_GROUP_FORM = "apvg"

UUID_TYPE_VDI_SCHEDULER_TASK_HISTORY = 'vschh'
UUID_TYPE_VDI_SCHEDULER_TASK = 'vscht'

UUID_TYPE_DELIVERY_GROUP = 'deliv'

UUID_TYPE_VDHOST_REQUEST = "vdhreq"
UUID_TYPE_TERMINAL_REQUEST = "temreq"
UUID_TYPE_VDHOST_JOB = "vdhjob"
UUID_TYPE_VDAGENT_JOB = "vdajob"

UUID_TYPE_DESKTOP_GUEST_REQUEST = "dtpgt"

UUID_TYPE_USB_POLICY = "usbplc"

UUID_TYPE_CITRIX_POLICY = "ctxpol"
UUID_TYPE_POLICY_ITEM = "politem"
UUID_TYPE_POLICY_FILTER="polflt"

UUID_TYPE_POLICY_GROUP = 'polg'
UUID_TYPE_SECURITY_POLICY = 'sg'
UUID_TYPE_SECURITY_POLICY_SGRS = 'sgrs'
UUID_TYPE_SECURITY_IPSET = 'sgi'
UUID_TYPE_SECURITY_POLICY_SHARE = 'sgm'
UUID_TYPE_SECURITY_RULE_SHARE = 'srs'

UUID_TYPE_COMPONENT_VERSION = "compvn"
UUID_TYPE_AUTH_SERVICE = 'aus'
UUID_TYPE_RADIUS_SERVICE = 'ras'
UUID_TYPE_NOTICE_PUSH = 'np'
UUID_TYPE_SOFTWARE = 'sw'

UUID_TYPE_PROMPT_QUESTION = "pmtqsn"
UUID_TYPE_PROMPT_ANSWER = "pmtasr"

UUID_TYPE_RECORD_USER_LOGIN = "rdul"

UUID_TYPE_RECORD_DESKTOP_LOGIN = "rddl"
UUID_TYPE_SYSLOG_SERVER = "slgsvr"

UUID_TYPE_TERMINAL = 'te'
UUID_TYPE_TERMINAL_GROUP = "tegroup"
UUID_TYPE_MODULE_CUSTOM = 'modcus'
UUID_TYPE_WORKFLOW_MODEL = 'wfm'
UUID_TYPE_WORKFLOW_CONFIG = 'wfc'
UUID_TYPE_WORKFLOW = 'wf'
UUID_TYPE_FILE_SHARE_GROUP = 'fsgroup'
UUID_TYPE_FILE_SHARE_GROUP_FILE = 'fsgfile'
UUID_TYPE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY = 'fhistory'
UUID_TYPE_FILE_SHARE_SERVICE = 'fsservice'


# app
UUID_TYPE_BROKER_APP = "app"
UUID_TYPE_BROKER_APP_GROUP = "appg"

UUID_TYPE_DESKTOP_MAINTAINER = "dsktpmtn"
UUID_TYPE_GUEST_SHELL_COMMAND = "guestcmd"
UUID_TYPE_GUEST_SHELL_COMMAND_RUN_HISTORY = "gcmdhory"



UUID_PREFIX_TABLE_MAP = {
    UUID_TYPE_DESKTOP_GROUP: dbconst.TB_DESKTOP_GROUP,
    UUID_TYPE_DESKTOP_GROUP_NETWORK: dbconst.TB_DESKTOP_GROUP_NETWORK,
    UUID_TYPE_DESKTOP_GROUP_DISK: dbconst.TB_DESKTOP_GROUP_DISK,
    UUID_TYPE_DESKTOP: dbconst.TB_DESKTOP,
    UUID_TYPE_DESKTOP_DISK: dbconst.TB_DESKTOP_DISK,
    UUID_TYPE_DESKTOP_IMAGE: dbconst.TB_DESKTOP_IMAGE,
    UUID_TYPE_DESKTOP_JOB: dbconst.TB_DESKTOP_JOB,
    UUID_TYPE_DESKTOP_TASK: dbconst.TB_DESKTOP_TASK,
    UUID_TYPE_SNAPHSOT_GROUP: dbconst.TB_SNAPSHOT_GROUP,
    UUID_TYPE_SNAPSHOT_RESOURCET: dbconst.TB_SNAPSHOT_RESOURCE,
    UUID_TYPE_SNAPSHOT_GROUP_SNAPSHOT: dbconst.TB_SNAPSHOT_GROUP_SNAPSHOT,
    UUID_TYPE_SNAPSHOT_DISK_SNAPSHOT: dbconst.TB_SNAPSHOT_DISK_SNAPSHOT,
    UUID_TYPE_DESKTOP_USER: dbconst.TB_DESKTOP_USER,
    UUID_TYPE_DESKTOP_OU: dbconst.TB_DESKTOP_USER_OU,
    UUID_TYPE_DESKTOP_USER_GROUP: dbconst.TB_DESKTOP_USER_GROUP,
    UUID_TYPE_VDI_SYSTEM_LOG: dbconst.TB_VDI_SYSTEM_LOG,
    UUID_TYPE_APPLY_FORM: dbconst.TB_APPLY,
    UUID_TYPE_APPLY_GROUP_FORM: dbconst.TB_APPLY_GROUP,
    UUID_TYPE_APPROVE_GROUP_FORM: dbconst.TB_APPROVE_GROUP,
    UUID_TYPE_VDI_DESKTOP_MESSAGE: dbconst.TB_VDI_DESKTOP_MESSAGE,

    UUID_TYPE_VDI_SCHEDULER_TASK_HISTORY: dbconst.TB_SCHEDULER_TASK_HISTORY,
    UUID_TYPE_VDI_SCHEDULER_TASK: dbconst.TB_SCHEDULER_TASK,
    
    UUID_TYPE_DELIVERY_GROUP: dbconst.TB_DELIVERY_GROUP,
    UUID_TYPE_POLICY_GROUP: dbconst.TB_POLICY_GROUP,
    UUID_TYPE_CITRIX_POLICY:dbconst.TB_CITRIX_POLICY,
    UUID_TYPE_POLICY_ITEM:dbconst.TB_CITRIX_POLICY_ITEM,
    UUID_TYPE_POLICY_FILTER:dbconst.TB_CITRIX_POLICY_FILTER,    
    UUID_TYPE_SECURITY_POLICY: dbconst.TB_SECURITY_POLICY,
    UUID_TYPE_SECURITY_POLICY_SGRS: dbconst.TB_SECURITY_RULE,
    UUID_TYPE_SECURITY_IPSET: dbconst.TB_SECURITY_IPSET,
    UUID_TYPE_SECURITY_POLICY_SHARE: dbconst.TB_SECURITY_POLICY,
    UUID_TYPE_SECURITY_RULE_SHARE: dbconst.TB_SECURITY_RULE,
    UUID_TYPE_VDAGENT_JOB: dbconst.TB_VDAGENT_JOB,
    UUID_TYPE_VDHOST_JOB: dbconst.TB_VDHOST_JOB,
    UUID_TYPE_USB_POLICY: dbconst.TB_USB_POLICY,
    
    UUID_TYPE_COMPONENT_VERSION: dbconst.TB_COMPONENT_VERSION,
    
    UUID_TYPE_AUTH_SERVICE: dbconst.TB_AUTH_SERVICE,
    UUID_TYPE_RADIUS_SERVICE: dbconst.TB_RADIUS_SERVICE,
    UUID_TYPE_NOTICE_PUSH: dbconst.TB_NOTICE_PUSH,
    UUID_TYPE_SOFTWARE: dbconst.TB_SOFTWARE_INFO,
    
    UUID_TYPE_PROMPT_QUESTION: dbconst.TB_PROMPT_QUESTION,
    UUID_TYPE_PROMPT_ANSWER: dbconst.TB_PROMPT_ANSWER,
    UUID_TYPE_RECORD_USER_LOGIN: dbconst.TB_USER_LOGIN_RECORD,

    UUID_TYPE_RECORD_DESKTOP_LOGIN: dbconst.TB_DESKTOP_LOGIN_RECORD,
    UUID_TYPE_SYSLOG_SERVER: dbconst.TB_SYSLOG_SERVER,

    UUID_TYPE_TERMINAL: dbconst.TB_TERMINAL_MANAGEMENT,
    UUID_TYPE_TERMINAL_GROUP: dbconst.TB_TERMINAL_GROUP,
    UUID_TYPE_MODULE_CUSTOM: dbconst.TB_MODULE_CUSTOM,
    UUID_TYPE_WORKFLOW_MODEL: dbconst.TB_WORKFLOW_MODEL,
    UUID_TYPE_WORKFLOW_CONFIG: dbconst.TB_WORKFLOW_CONFIG,
    UUID_TYPE_WORKFLOW: dbconst.TB_WORKFLOW,
    UUID_TYPE_FILE_SHARE_GROUP: dbconst.TB_FILE_SHARE_GROUP,
    UUID_TYPE_FILE_SHARE_GROUP_FILE: dbconst.TB_FILE_SHARE_GROUP_FILE,
    UUID_TYPE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY,
    UUID_TYPE_FILE_SHARE_SERVICE: dbconst.TB_FILE_SHARE_SERVICE,

    UUID_TYPE_BROKER_APP: dbconst.TB_BROKER_APP,
    UUID_TYPE_BROKER_APP_GROUP: dbconst.TB_BROKER_APP_GROUP,


    UUID_TYPE_DESKTOP_MAINTAINER: dbconst.TB_DESKTOP_MAINTAINER,
    UUID_TYPE_GUEST_SHELL_COMMAND: dbconst.TB_GUEST_SHELL_COMMAND,
    UUID_TYPE_GUEST_SHELL_COMMAND_RUN_HISTORY: dbconst.TB_GUEST_SHELL_COMMAND_RUN_HISTORY,

}

UUID_TABLE_PREFIX_MAP = {v: k for k, v in UUID_PREFIX_TABLE_MAP.items()}

UUID_TYPE_NOT_DEFINED = "not-defined"
RESOURCE_TYPE_UUID_SEPERATOR = "-"

GLOBAL_ADMIN_USER_ID = "global_admin"

class IUUIDChecker():
    def check(self, uuid):
        return False

class UUIDPGChecker(IUUIDChecker):
    '''uuid checker for postgreSQL tables '''

    def __init__(self, pg):
        self.pg = pg
        self.simple_map = UUID_PREFIX_TABLE_MAP

    def _check(self, uuid, tb):
        ret = self.pg.get_count(tb, {dbconst.INDEXED_COLUMNS[tb][0]:uuid})
        if ret is not None and ret == 0:
            return True
        return False

    def check(self, uuid):
        prefix = uuid.split(RESOURCE_TYPE_UUID_SEPERATOR)[0]

        if prefix in self.simple_map:
            return self._check(uuid, self.simple_map[prefix])

        logger.error("invalid uuid [%s]" % uuid)
        return False

class IUUIDAllocator(object):
    def allocate(self, prefix):
        return None


class UUIDAllocator(IUUIDAllocator):
    def __init__(self, allocate_func):
        self.__allocate_func = allocate_func

    def allocate(self, prefix):
        return self.__allocate_func(prefix)

def get_uuid(prefix=None, checker=None, digit_only=False, width=8, long_format=False, allocator=None):
    ''' generate an uuid with form <prefix>-XXXXXXXX
        XXXXXXXX are eight random letters
    
        @param prefix - the prefix letter
        @param checker - a checker object to check if this uuid is unique
        @return an uuid or None if failed
    '''
    if checker:
        if not isinstance(checker, IUUIDChecker):
            return None

    if allocator:
        if not isinstance(allocator, IUUIDAllocator):
            return None

    # get uuid at a maximum of 20 times in case of infinite loop when something bad happens.
    count = 0
    while True and count < 20:
        count += 1

        # Customized allocator, highest priority.
        if allocator:
            uuid = allocator.allocate(prefix)
            if uuid:
                return uuid
        else:
            uuid = ""
            if prefix is not None:
                uuid = prefix + RESOURCE_TYPE_UUID_SEPERATOR

            for _ in range(width):
                if digit_only:
                    uuid += random.choice('012356789')
                elif long_format:
                    uuid += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012356789')
                else:
                    uuid += random.choice('abcdefghijklmnopqrstuvwxyz012356789')

            if checker is None:
                return uuid
            if checker.check(uuid):
                return uuid

    return None

def alloc_graphics_passwd():
    '''' allocate a new graphics passwd for VM '''
    passwd = ""
    for _ in range(0, 32):
        passwd += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012356789')
    return passwd

def alloc_session_id():
    '''' allocate a new session id for login console user '''
    sk = ""
    for _ in range(0, 32):
        sk += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012356789')
    return sk

def alloc_access_key_id():
    '''' allocate a new access key id '''
    key_id = ""
    for _ in range(0, 20):
        key_id += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return key_id

def alloc_secret_access_key():
    '''' allocate a new secret access key'''
    secret_key = ""
    for _ in range(0, 40):
        secret_key += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012356789')
    return secret_key

def alloc_reset_passwd_token():
    ''' allocate reset password token '''
    token = ""
    for _ in range(0, 40):
        token += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ012356789-')
    return token

def get_resource_type(uuid):

    prefix = uuid.split("-")[0]
    if prefix == UUID_TYPE_DESKTOP_GROUP:
        return dbconst.RESTYPE_DESKTOP_GROUP
    elif prefix == UUID_TYPE_DESKTOP:
        return dbconst.RESTYPE_DESKTOP
    elif prefix == UUID_TYPE_DESKTOP_USER:
        return dbconst.RESTYPE_USER
    elif prefix == UUID_TYPE_DESKTOP_OU:
        return dbconst.RESTYPE_USER_OU
    elif prefix == UUID_TYPE_DESKTOP_USER_GROUP:
        return dbconst.RESTYPE_USER_GROUP
    elif prefix == UUID_TYPE_DESKTOP_GROUP_DISK:
        return dbconst.RESTYPE_DESKTOP_GROUP_DISK
    elif prefix == UUID_TYPE_DESKTOP_GROUP_NETWORK:
        return dbconst.RESTYPE_DESKTOP_GROUP_NETWORK
    elif prefix == UUID_TYPE_DESKTOP_DISK:
        return dbconst.RESTYPE_DESKTOP_DISK
    elif prefix == UUID_TYPE_DESKTOP_IMAGE:
        return dbconst.RESTYPE_DESKTOP_IMAGE
    elif prefix == UUID_TYPE_DESKTOP_NETWORK:
        return dbconst.RESTYPE_DESKTOP_NETWORK
    elif prefix == UUID_TYPE_VDI_SCHEDULER_TASK_HISTORY:
        return dbconst.RESTYPE_SCHEDULER_TASK_HISTORY
    elif prefix == UUID_TYPE_VDI_SCHEDULER_TASK:
        return dbconst.RESTYPE_SCHEDULER_TASK
    elif prefix == GLOBAL_ADMIN_USER_ID:
        return dbconst.RESTYPE_USER
    elif prefix == UUID_TYPE_DELIVERY_GROUP:
        return dbconst.RESTYPE_DELIVERY_GROUP
    elif prefix == UUID_TYPE_POLICY_GROUP:
        return dbconst.RESTYPE_POLICY_GROUP
    elif prefix == UUID_TYPE_CITRIX_POLICY:
        return dbconst.RESTYPE_CITRIX_POLICY   
    elif prefix == UUID_TYPE_POLICY_ITEM:
        return dbconst.RESTYPE_CITRIX_POLICY_ITEM     
    elif prefix == UUID_TYPE_POLICY_FILTER:
        return dbconst.RESTYPE_CITRIX_POLICY_FILTER            
    elif prefix == UUID_TYPE_SECURITY_POLICY:
        return dbconst.RESTYPE_SECURITY_POLICY
    elif prefix == UUID_TYPE_SECURITY_POLICY_SHARE:
        return dbconst.RESTYPE_SECURITY_POLICY
    elif prefix == UUID_TYPE_SECURITY_POLICY_SGRS:
        return dbconst.RESTYPE_SECURITY_RULE
    elif prefix == UUID_TYPE_SECURITY_RULE_SHARE:
        return dbconst.RESTYPE_SECURITY_RULE
    elif prefix == UUID_TYPE_SECURITY_IPSET:
        return dbconst.RESTYPE_SECURITY_IPSET
    elif prefix == UUID_TYPE_SNAPHSOT_GROUP:
        return dbconst.RESTYPE_SNAPSHOT_GROUP
    elif prefix == UUID_TYPE_AUTH_SERVICE:
        return dbconst.RESTYPE_AUTH_SERVICE
    elif prefix == UUID_TYPE_RADIUS_SERVICE:
        return dbconst.RESTYPE_RADIUS_SERVICE
    elif prefix == UUID_TYPE_NOTICE_PUSH:
        return dbconst.RESTYPE_NOTICE_PUSH
    elif prefix == UUID_TYPE_TERMINAL_GROUP:
        return dbconst.RESTYPE_TERMINAL_GROUP
    elif prefix == UUID_TYPE_WORKFLOW:
        return dbconst.RESTYPE_WORKFLOW
    elif prefix == UUID_TYPE_WORKFLOW_MODEL:
        return dbconst.RESTYPE_WORKFLOW_MODEL

    # return default
    return dbconst.RESOURCE_TYPE_NOT_DEFINED
