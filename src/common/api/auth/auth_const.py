# -*- coding: utf-8 -*-
from constants import EN, ZH_CN

# account control
ACCOUNTDISABLE = 2 #0x0002 -forbid account
PASSWD_NOTREQD = 32 # 0x0020 -no need password
NORMAL_ACCOUNT = 512 # 0x0200 -
DONT_EXPIRE_PASSWORD = 65536 # 0x10000
DONT_CHANGE_PASSWORD = 66048 # NORMAL_ACCOUNT|DONT_EXPIRE_PASSWORD
PASSWORD_MUST_CHANGE = 546

# error code
ERROR_NO_SUCH_USER = '525'
ERROR_LOGON_FAILURE = '52e'
ERROR_INVALID_LOGON_HOURS = '530'
ERROR_INVALID_WORKSTATION = '531'
ERROR_PASSWORD_EXPIRED = '532'
ERROR_ACCOUNT_DISABLED = '533'
ERROR_ACCOUNT_EXPIRED = '701'
ERROR_PASSWORD_MUST_CHANGE = '773'
ERROR_ACCOUNT_LOCKED_OUT = '775'

ERROR_CODE_HEX_MAP = {
    ERROR_NO_SUCH_USER: 1317,
    ERROR_LOGON_FAILURE: 1326,
    ERROR_INVALID_LOGON_HOURS: 1328,
    ERROR_INVALID_WORKSTATION: 1329,
    ERROR_PASSWORD_EXPIRED: 1330,
    ERROR_ACCOUNT_DISABLED: 1331,
    ERROR_ACCOUNT_EXPIRED: 1793,
    ERROR_PASSWORD_MUST_CHANGE: 1907,
    ERROR_ACCOUNT_LOCKED_OUT: 1909
}
ERR_MSG_NO_SUCH_USER = {EN: "user no found",
                         ZH_CN: u"用户不存在"}
ERR_MSG_LOGON_FAILURE = {EN: "password error",
                          ZH_CN: u"密码错误"}
ERR_MSG_INVALID_LOGON_HOURS = {EN: " invail logon hours",
                               ZH_CN: u"登录时间违规"}
ERR_MSG_INVALID_WORKSTATION = {EN: "user cant logon this desktop",
                               ZH_CN: u"用户禁止在当前桌面登录"}
ERR_MSG_PASSWORD_EXPIRED = {EN: "user password expried",
                        ZH_CN: u"登录密码过期，请联系管理员"}
ERR_MSG_ACCOUNT_DISABLED = {EN: " account disable",
                               ZH_CN: u"账户被禁用"}
ERR_MSG_ACCOUNT_EXPIRED  = {EN: "user account expried",
                               ZH_CN: u"用户账户过期"}
ERR_MSG_PASSWORD_MUST_CHANGE = {EN: "user password must be change",
                        ZH_CN: u"用户密码在第一次登录之前必须修改"}
ERR_MSG_ACCOUNT_LOCKED_OUT = {EN: " account lock",
                               ZH_CN: u"账户被锁定，请联系管理员"}
ERR_MSG_PASSWORD_EXCEED_ERROR_TIME_LOCKED_OUT = {EN: " account lock %s",
                               ZH_CN: u"密码超过错误次数，账户被锁定, %s秒后解锁"}
ERR_MSG_USER_NAME_NO_FOUND = {EN: "user name no found",
                               ZH_CN: u"用户名不存在"}
PMS_USER_BASE_DN = u"云桌面用户"
ERR_LDAP_CODE_MAP = {
    ERROR_NO_SUCH_USER: ERR_MSG_NO_SUCH_USER,
    ERROR_LOGON_FAILURE: ERR_MSG_LOGON_FAILURE,
    ERROR_INVALID_LOGON_HOURS: ERR_MSG_INVALID_LOGON_HOURS,
    ERROR_INVALID_WORKSTATION: ERR_MSG_INVALID_WORKSTATION,
    ERROR_PASSWORD_EXPIRED: ERR_MSG_PASSWORD_EXPIRED,
    ERROR_ACCOUNT_DISABLED: ERR_MSG_ACCOUNT_DISABLED,
    ERROR_ACCOUNT_EXPIRED: ERR_MSG_ACCOUNT_EXPIRED,
    ERROR_PASSWORD_MUST_CHANGE: ERR_MSG_PASSWORD_MUST_CHANGE,
    ERROR_ACCOUNT_LOCKED_OUT: ERR_MSG_ACCOUNT_LOCKED_OUT
}