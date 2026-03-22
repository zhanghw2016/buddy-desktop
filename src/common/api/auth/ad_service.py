import ldap
import ldap.modlist as modlist
from ldap.controls import SimplePagedResultsControl
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
import auth_const as AuthConst
import uuid
import struct

AD_USER_ATTRS = ['userAccountControl', 'displayName', 'description', 'homePhone', 'physicalDeliveryOfficeName', 'sAMAccountName',
                 'title', 'mail', 'telephoneNumber','accountExpires','objectGUID', 'objectSid', 'pwdLastSet', 'userPrincipalName',
                 'badPasswordTime', 'badPwdCount']

AD_COMPUTE_ATTRS = ['cn', 'objectGUID', 'objectSid','operatingSystem', 'name']

AD_USER_GROUP = ['description', 'mail', 'info', 'groupType', 'member', 'objectGUID']
RETURN_LIST_KEY = ["memberOf"]
PAGE_SIZE = 500

from .base_auth import BaseServerAuth

def sid_convert(binary):

    version = struct.unpack('B', binary[0])[0]
    # I do not know how to treat version != 1 (it does not exist yet)
    assert version == 1, version
    length = struct.unpack('B', binary[1])[0]
    authority = struct.unpack('>Q', '\x00\x00' + binary[2:8])[0]
    string = 'S-%d-%d' % (version, authority)
    binary = binary[8:]
    assert len(binary) == 4 * length
    for i in xrange(length):
        value = struct.unpack('<L', binary[4*i:4*(i+1)])[0]
        string += '-%d' % value

    return string

def split_into_chunks(string, chunk_length=2):

    chunks = []
    while len(string) > 0:
        chunks.append(string[:chunk_length])
        string = string[chunk_length:]
    return chunks

def to_oracle_raw16(string, strip_dashes=True, dashify_result=False):

    oracle_format_indices = [3, 2, 1, 0, 5, 4, 7, 6, 8, 9, 10, 11, 12, 13, 14, 15]
    if strip_dashes:
        string = string.replace("-", "")
    parts = split_into_chunks(string)
    result = ""
    for index in oracle_format_indices:
        result = result + parts[index]
    if dashify_result:
        result = result[:8] + '-' + result[8:12] + '-' + result[12:16] + '-' + result[16:20] + '-' + result[20:]
    return result

class ADServerAuth(BaseServerAuth):

    def __init__(self, conn):

        self.domain = conn["domain"]
        self.base_dn = conn["base_dn"]
        self.admin = conn["admin_name"]
        self.password = conn["admin_password"]
        self.server_host = conn["host"]
        self.server_port = conn["port"]
        self.secret_port= conn["secret_port"]
        self.service_type = const.AUTH_TYPE_AD
        auth_user = '%s@%s' % (self.admin, self.domain)

        super(ADServerAuth, self).__init__(self.base_dn, auth_user, self.password, self.server_host,
                                           self.server_port, self.secret_port)

    def pack_guid(self, string):

        return bytearray.fromhex(to_oracle_raw16(string))
    
    def unpack_guid(self, ba):

        hex_s = "".join("%02x" % b for b in ba)
        return to_oracle_raw16(hex_s, True, True)

    def build_user_info(self, user):
    
        user_info = {}
        user_keys = ['userPassword', 'displayName', 'description', 'physicalDeliveryOfficeName', 'title', 'mail', 'telephoneNumber', 'homePhone']
        for key in user_keys:
            if key in user:
                user_info[key] = str(user[key])
        
        user_info['userPrincipalName'] = str(user['user_name'])
        user_info['cn'] = user_info["displayName"]
        user_info['name'] = user_info["displayName"]
        user_info['mail'] = str(user.get("email", ''))

        userAccountControl = str(AuthConst.NORMAL_ACCOUNT)
        account_control = user.get("account_control", 1)
        if account_control == const.DONT_CHNAGE_PASSWORD:
            userAccountControl = str(AuthConst.DONT_CHANGE_PASSWORD)

        user_info["userAccountControl"] = userAccountControl

        return user_info
    
    def login(self, user_name, auth_passwd):
        try:
            # login
            
            ret = self.describe_users(user_names=[user_name])
            if not ret:
                logger.error("login no found user %s" % user_name)
                return False
            
            auth_user = ret[0]
            
            user_name = auth_user["sAMAccountName"]
            user_dn = auth_user['dn']

            conn = self.pool_conn(user_dn, auth_passwd)

            # get user info
            ret = conn.search_s(
                self.base_dn, ldap.SCOPE_SUBTREE,
                "(sAMAccountName=%s)" % (user_name),
                ["sAMAccountName"])
            
            self.pool_release(conn, is_unbind=True)
            if ret is None or len(ret) == 0:
                logger.error("login to server [%s] succeeded but [%s] not found" % (self.uri, user_name))
                return False

            return True
        except Exception, e:
            logger.error("login to server [%s] for [%s] failed, [%s]" % (self.uri, user_name, e))
            ret = self.check_auth_error(e)            
            if isinstance(ret, Error):    
                return ret    
            else:
                return False          

    def create_user(self, org_dn, user={}):
        try:

            conn_s = self.pool_conn_s(self.admin, self.password)
            user['objectclass'] = ['top', 'person', 'organizationalPerson', 'user']
            password = user.pop('userPassword')
            unicode_password = unicode('\"' + str(password) + '\"', 'iso-8859-1')
            password_value = unicode_password.encode('utf-16-le')
            user['unicodePwd'] = password_value
            
            displayName = user.get("displayName")
            if displayName:
                dn = "cn=%s,%s" % (user['displayName'], org_dn)
            else:
                dn = "cn=%s,%s" % (user['userPrincipalName'], org_dn)

            user['sAMAccountName'] = user['userPrincipalName']
            user['userPrincipalName'] = '%s@%s' % (user['userPrincipalName'], self.domain)
            user['userAccountControl'] = str(user["userAccountControl"])
            user['pwdLastSet'] = str(0)
            user['accountExpires'] = str(user['accountExpires'])
            
            ldif = modlist.addModlist(user)

            retcode, _ = conn_s.add_s(dn, ldif)
            self.pool_release(conn_s)
            if retcode != ErrorCodes.LDAP_ADD_S_SUCCESS:
                logger.error("create auth user fail")
                return Error(ErrorCodes.CREATE_AUTH_USER_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_AUTH_USER_ERROR)

            return dn
        except Exception,e:
            logger.error("create user with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def describe_users(self, org_dn=None, user_names=None, scope=1, search_username=None, cn_names=None, object_guid=None):

        try:
            conn = self.pool_conn(self.admin, self.password)

            filterstr = '(&(objectclass=user)(!(objectclass=computer))'
            if object_guid:
                filterstr = filterstr + '(|(objectGUID=%s)))' % object_guid

            elif search_username:
                search_username = '*' + search_username + '*';
                search_username_domain = "%s@%s" % (search_username, self.domain)
                filterstr = filterstr + '(|(userPrincipalName=%s)(cn=%s)(displayName=%s)(sAMAccountName=%s)))' % (search_username_domain, search_username, search_username, search_username)
            elif user_names:
                if not isinstance(user_names, list):
                    user_names = [user_names]
                filterstr = filterstr + '(|'
                for user_name in user_names:
                    p_user_name = '%s@%s' % (user_name, self.domain)
                    userPrincipalName = '(userPrincipalName=%s)(sAMAccountName=%s)' % (p_user_name, user_name)
                    filterstr += userPrincipalName
                filterstr += '))'
            elif cn_names and org_dn:
                if not isinstance(cn_names, list):
                    cn_names = [cn_names]
                filterstr = filterstr + '(|'
                for cn_name in cn_names:
                    cn_name = 'cn=%s,%s' % (cn_name, org_dn)
                    userPrincipalName = '(distinguishedName=%s)' % cn_name
                    filterstr += userPrincipalName
                filterstr += '))'
            else:
                filterstr += ')'

            result = []
            msgid = None
            if not org_dn:
                org_dn = self.base_dn

            pg_ctrl = SimplePagedResultsControl(True, size=PAGE_SIZE, cookie="")

            while True:
                if scope > 0:
                    msgid = conn.search_ext(org_dn, ldap.SCOPE_SUBTREE, filterstr,
                                            AD_USER_ATTRS,serverctrls=[pg_ctrl])
                else:
                    msgid = conn.search_ext(org_dn, ldap.SCOPE_ONELEVEL, filterstr,
                                            AD_USER_ATTRS,serverctrls=[pg_ctrl])
                _a, res_data, _b, srv_ctrls = conn.result3(msgid)

                result.extend(res_data)
                cookie = srv_ctrls[0].cookie
                if cookie:
                    pg_ctrl.cookie = cookie
                else:
                    break
            
            self.pool_release(conn)
            if result == None:
                return Error(ErrorCodes.DESCRIBE_AUTH_USERS_ERROR,
                                 ErrorMsg.ERR_MSG_DESCRIBE_AUTH_USERS_ERROR)

            ret = []

            for dn, entry in result:
                if not isinstance(entry, dict):
                    continue
                item = {'dn': dn}
                for key in entry.keys():
                    
                    if not entry[key]:
                        continue
                    
                    if key == "objectGUID":
                        item[key] = str(uuid.UUID(bytes_le=entry[key][0]))
                        continue
                    if key in RETURN_LIST_KEY:
                        item[key] = entry[key]
                    else:
                        item[key] = entry[key][0]
                ret.append(item)

            return ret
        except Exception,e:
            logger.error("describe users with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def describe_computes(self, org_dn=None, compute_names=None, scope=1, search_compute_name=None):

        try:
            conn = self.pool_conn(self.admin, self.password)
            
            filterstr = '(&(objectclass=computer)'
            if search_compute_name:
                search_compute_name = '*' + search_compute_name + '*';
                filterstr = filterstr + '(|(name=%s)(cn=%s)))' % (search_compute_name, search_compute_name)
            elif compute_names:
                if not isinstance(compute_names, list):
                    compute_names = [compute_names]
                filterstr = filterstr + '(|'
                for compute_name in compute_names:
                    ComputeName = '(name=%s)(cn=%s)' % (compute_name, compute_name)
                    filterstr += ComputeName
                filterstr += '))'
            else:
                filterstr += ')'

            result = []
            msgid = None
            if not org_dn:
                org_dn = self.base_dn
            
            pg_ctrl = SimplePagedResultsControl(True, size=PAGE_SIZE, cookie="")

            while True:
                if scope > 0:
                    msgid = conn.search_ext(org_dn, ldap.SCOPE_SUBTREE, filterstr,
                                            AD_COMPUTE_ATTRS,serverctrls=[pg_ctrl])
                else:
                    msgid = conn.search_ext(org_dn, ldap.SCOPE_ONELEVEL, filterstr,
                                            AD_COMPUTE_ATTRS,serverctrls=[pg_ctrl])
                _a, res_data, _b, srv_ctrls = conn.result3(msgid)

                result.extend(res_data)
                cookie = srv_ctrls[0].cookie
                if cookie:
                    pg_ctrl.cookie = cookie
                else:
                    break
            
            self.pool_release(conn)
            if result == None:
                return Error(ErrorCodes.DESCRIBE_AUTH_USERS_ERROR,
                                 ErrorMsg.ERR_MSG_DESCRIBE_AUTH_USERS_ERROR)

            ret = []

            for dn, entry in result:
                if not isinstance(entry, dict):
                    continue
                item = {'dn': dn}
                for key in entry.keys():
                    
                    if not entry[key]:
                        continue
                    
                    if key == "objectGUID":
                        item[key] = str(uuid.UUID(bytes_le=entry[key][0]))
                        continue
                    if key == "objectSid":
                        item[key] = sid_convert(entry[key][0])
                        continue

                    if key in RETURN_LIST_KEY:
                        item[key] = entry[key]
                    else:
                        item[key] = entry[key][0]
                ret.append(item)

            return ret
        except Exception,e:
            logger.error("describe compute with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def describe_all_users(self, org_dn):
        try:
            conn = self.pool_conn(self.admin, self.password)

            filterstr = '(&(objectclass=user)(!(objectclass=computer)))'

            result = []
            if not org_dn:
                org_dn = self.base_dn
            pg_ctrl = SimplePagedResultsControl(True, size=PAGE_SIZE, cookie="")
            while True:
                msgid = conn.search_ext(org_dn, ldap.SCOPE_SUBTREE, filterstr,
                                        AD_USER_ATTRS,serverctrls=[pg_ctrl])
                _a, res_data, _b, srv_ctrls = conn.result3(msgid)
                result.extend(res_data)
                cookie = srv_ctrls[0].cookie
                if cookie:
                    pg_ctrl.cookie = cookie
                else:
                    break

            ret = []
            for dn, entry in result:
                item = {}
                item = {'dn': dn}
                for key in entry.keys():
                    item[key] = entry[key][0]
                ret.append(item)
            
            self.pool_release(conn)
            return ret
        except Exception,e:
            logger.error("describe users with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def describe_computers(self, org_dn='', computers = []):
        try:
            conn = self.pool_conn(self.admin, self.password)
            
            filterstr = '(&(objectclass=computer)'
            if len(computers) > 0:
                filterstr = filterstr + '(|'
            for cn in computers:
                cn = '(cn=%s)' % cn
                filterstr += cn
            if len(computers) > 0:
                filterstr += '))'
            else:
                filterstr += ')'

            result = []
            if org_dn:
                    result = conn.search_s(org_dn, ldap.SCOPE_SUBTREE, filterstr, 
                                           attrlist=AD_COMPUTE_ATTRS)
            else:
                    result = conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, filterstr, 
                                           attrlist=AD_COMPUTE_ATTRS)                
            self.pool_release(conn)
            if result == None:
                return Error(ErrorCodes.DESCRIBE_AUTH_USERS_ERROR,
                                 ErrorMsg.ERR_MSG_DESCRIBE_AUTH_USERS_ERROR)

            ret = []
            for dn, entry in result:
                item = {}
                item = {'dn': dn}
                for key in entry.keys():
                    item[key] = entry[key][0]
                ret.append(item)
            
            return ret
        except Exception,e:
            logger.error("describe users with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
            
    def set_password(self, user_dn, password):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            unicode_pwd = unicode('\"' + str(password) + '\"', 'iso-8859-1')
            password_utf16 = unicode_pwd.encode('utf-16-le')
            param_pwd = [(ldap.MOD_REPLACE, 'unicodePwd', [password_utf16]), (ldap.MOD_REPLACE, 'unicodePwd', [password_utf16])]

            ret,_ = conn_s.modify_s(user_dn, param_pwd)
            self.pool_release(conn_s)

            if ret != ErrorCodes.LDAP_MODIFY_S_SUCCESS:
                return Error(ErrorCodes.MODIFY_AUTH_USER_PASSWORD_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_AUTH_USER_PASSWORD_ERROR)

            return user_dn
        except Exception,e:
            logger.error("reset user password with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def create_user_group(self, parent_dn, attrs):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            attrs['objectClass'] = ['group','top']
            dn = 'cn=%s,%s' % (attrs['name'], parent_dn)
            ldif = modlist.addModlist(attrs)

            retcode, _ = conn_s.add_s(dn,ldif)
            self.pool_release(conn_s)

            if retcode != ErrorCodes.LDAP_ADD_S_SUCCESS:
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_AD_USER_GROUP_ERROR)

            return dn
        except Exception,e:
            logger.error("create user group with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION) 

    def rename_user_dn(self, user_dn, new_name, dn_type=None, login_name=None):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)
            
            old_name = user_dn.split(",")[0]
            new_dn = user_dn[len(old_name)+ 1:]
            
            name_type = old_name[0:3]
            _new_name = "%s%s" % (name_type, new_name)
            
            conn_s.rename_s(user_dn, _new_name, new_dn)
            self.pool_release(conn_s)
            if dn_type == const.USER_DN_TYPE_USER:
                attrs = {}
                modify_new_dn = "%s,%s" % (_new_name, new_dn)
                if login_name:
                    userPrincipalName = '%s@%s' % (login_name, self.domain)
                    
                    attrs["userPrincipalName"] = userPrincipalName
                    attrs["sAMAccountName"] = login_name
                
                attrs["displayName"] = new_name
                
                self.modify_user(modify_new_dn, attrs)
            elif dn_type == const.USER_DN_TYPE_USER_GROUP:
                attrs = {}
                modify_new_dn = "%s,%s" % (_new_name, new_dn)
                attrs["sAMAccountName"] = new_name
                self.modify_user(modify_new_dn, attrs)

        except Exception,e:
            logger.error("rename user dn with Exception:%s" % e)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def modify_user_group(self, dn, attrs={}):
        try:
            conn = self.pool_conn(self.admin, self.password)
            result = conn.search_s(dn, ldap.SCOPE_SUBTREE, attrlist=AD_USER_GROUP)

            old_attrs = {}
            for _dn, entry in result:
                if dn.lower().strip() == _dn.lower().strip():
                    for _key, _value in entry.items():
                        if _key in attrs.keys():
                            old_attrs[_key] = _value[0]
                    break

            ldif = modlist.modifyModlist(old_attrs, attrs)
            retcode, _ = conn.modify_s(dn,ldif)
            self.pool_release(conn)
            
            if retcode != ErrorCodes.LDAP_MODIFY_S_SUCCESS:
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_AD_USER_GROUP_ERROR)

            return dn
        except Exception,e:
            logger.error("modify user group with Exception:%s" % e)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def delete_user_groups(self, dns=[]):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            for dn in dns:
                retcode,_,_,_ = conn_s.delete_s(dn)
                self.pool_release(conn_s)
                if retcode != ErrorCodes.LDAP_DELETE_S_SUCCESS:
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_DELETE_AD_USER_GROUP_ERROR)
            
            return dns
        except Exception,e:
            logger.error("delete user groups with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def describe_user_groups(self, org_dn='', ug_names=[], scope=1, search_name=None):
        try:
            conn = self.pool_conn(self.admin, self.password)
            
            filterstr = '(&(objectclass=group)'
            filterstr += '(!(CN=Administrators))(!(CN=Users))(!(CN=CN=WinRMRemoteWMIUsers__))(!(CN=CN=Guests))'
            filterstr += '(!(CN=Print Operators))(!(CN=Backup Operators))(!(CN=Replicator,CN=Builtin))'
            filterstr += '(!(CN=Remote Desktop Users))(!(CN=Network Configuration Operators))(!(CN=Performance Monitor Users))'
            filterstr += '(!(CN=Guests))(!(CN=Replicator))(!(CN=Performance Log Users))'
            filterstr += '(!(CN=Distributed COM Users))(!(CN=Certificate Service DCOM Access))(!(CN=RDS Remote Access Servers))'
            filterstr += '(!(CN=RDS Endpoint Servers))(!(CN=RDS Management Servers))(!(CN=Hyper-V Administrators))'
            filterstr += '(!(CN=WinRMRemoteWMIUsers__))(!(CN=IIS_IUSRS))(!(CN=Cryptographic Operators))'
            filterstr += '(!(CN=Event Log Readers))(!(CN=Access Control Assistance Operators))(!(CN=Remote Management Users))'
            filterstr += '(!(CN=Domain Computers))(!(CN=Domain Controllers))(!(CN=Schema Admins))'
            filterstr += '(!(CN=Enterprise Admins))(!(CN=Cert Publishers))(!(CN=Domain Admins))'
            filterstr += '(!(CN=Domain Users))(!(CN=Domain Guests))(!(CN=Group Policy Creator Owners))'
            filterstr += '(!(CN=Server Operators))(!(CN=Account Operators))(!(CN=Pre-Windows 2000 Compatible Access))'
            filterstr += '(!(CN=Incoming Forest Trust Builders))(!(CN=Windows Authorization Access Group))(!(CN=Terminal Server License Servers))'
            filterstr += '(!(CN=Denied RODC Password Replication Group))(!(CN=Read-only Domain Controllers))(!(CN=Enterprise Read-only Domain Controllers))'
            filterstr += '(!(CN=RAS and IAS Servers))(!(CN=Allowed RODC Password Replication Group))(!(CN=Cloneable Domain Controllers))'
            filterstr += '(!(CN=Protected Users))(!(CN=DnsAdmins))(!(CN=DnsUpdateProxy))'
            
            if ug_names:
                filterstr += "(|"
                for dn in ug_names:
                    objectGUID = '(cn=%s)' % dn
                    filterstr += objectGUID
                filterstr += ")"

            elif search_name:
                search_name = '*' + search_name + '*';
                filterstr += "(|"
                filterstr += '(cn=%s)' % search_name
                filterstr += ")"

            filterstr += ')'
            result = []
            if not org_dn:
                org_dn = self.base_dn

            msgid = None
            pg_ctrl = SimplePagedResultsControl(True, size=PAGE_SIZE, cookie="")
            while True:
                if scope>0:
                    msgid = conn.search_ext(org_dn, ldap.SCOPE_SUBTREE, filterstr,
                                        AD_USER_GROUP,serverctrls=[pg_ctrl])
                else:
                    msgid = conn.search_ext(org_dn, ldap.SCOPE_ONELEVEL, filterstr,
                                        AD_USER_GROUP,serverctrls=[pg_ctrl])
                _a, res_data, _b, srv_ctrls = conn.result3(msgid)
                result.extend(res_data)
                cookie = srv_ctrls[0].cookie
                if cookie:
                    pg_ctrl.cookie = cookie
                else:
                    break
            
            self.pool_release(conn)
            if result == None:
                return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_DESCRIBE_AD_USER_GROUP_ERROR)

            ret = []
            for dn, entry in result:
                if not isinstance(entry, dict):
                    continue
                if dn != org_dn:
                    item = {'dn': dn}
                    
                    for _key, _value in entry.items():
                        
                        if not _value:
                            continue
                        
                        if _key == "member":
                            members = []
                            for member in _value:
                                members.append(member)
                            item[_key] = members
                        elif _key == "objectGUID":
                            item[_key] = str(uuid.UUID(bytes_le=_value[0]))
                        else:
                            item[_key] = _value[0]
                    ret.append(item)

            return ret
        except Exception,e:
            logger.error("describe user group with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def insert_user_to_user_group(self, ug_dn, user_dns):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            ug = conn_s.search_s(ug_dn, ldap.SCOPE_SUBTREE, filterstr='(objectclass=group)')
            old_members = []
            for _, entry in ug:
                for _key, _value in entry.items():
                    if _key == 'member':
                        old_members = _value
                        break

            old = {'member': old_members}
            new_members = []
            _old_members = []
            for member in old_members:
                _old_members.append(member.lower())
                new_members.append(member.lower())
            for user_dn in user_dns:
                if user_dn.lower() not in new_members:
                    new_members.insert(len(new_members), user_dn.lower())
            if _old_members == new_members:
                return ug_dn
            new = {'member': new_members}
            
            ldif = modlist.modifyModlist(old, new)
            retcode, _ = conn_s.modify_s(ug_dn, ldif)
            self.pool_release(conn_s)
            if retcode != ErrorCodes.LDAP_MODIFY_S_SUCCESS:
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_INSERT_AD_USER_TO_GROUP_ERROR)
                
            return ug_dn
        except Exception,e:
            logger.error("insert ad user to user group with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def remove_user_from_user_group(self, ug_dn, user_dns):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            ug = conn_s.search_s(ug_dn, ldap.SCOPE_SUBTREE, filterstr='(objectclass=group)')
            old_members = None
            for _, entry in ug:
                for _key, _value in entry.items():
                    if _key == 'member':
                        old_members = _value
                        break

            old = {'member': old_members}
            new_members = []
            _old_members = []
            for member in old_members:
                _old_members.append(member.lower())
                new_members.append(member.lower())
            for user_dn in user_dns:
                if user_dn.lower() in new_members:
                    new_members.remove(user_dn.lower())
            if _old_members == new_members:
                return ug_dn
            new = {'member': new_members}
            ldif = modlist.modifyModlist(old, new)
            retcode, _ = conn_s.modify_s(ug_dn, ldif)
            self.pool_release(conn_s)
            if retcode != ErrorCodes.LDAP_MODIFY_S_SUCCESS:
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_AUTH_ORGANIZATION_ERROR)

            return ug_dn
        except ldap.UNWILLING_TO_PERFORM:
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_REMOVE_AD_USER_FROM_GROUP_ERROR)
        except Exception,e:
            logger.error("remove ad user from user group with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
            
    def set_auth_user_status(self, user_name, user_dn, status):
        
        try:
            userAccountControl = AuthConst.NORMAL_ACCOUNT
            attrs = {"userAccountControl": userAccountControl}
            
            conn_s = self.pool_conn_s(self.admin, self.password)
            result = conn_s.search_s(user_dn, ldap.SCOPE_SUBTREE, attrlist=AD_USER_ATTRS)
            old_attrs = {}
            for _dn, entry in result:
                for _key, _value in entry.items():
                    if attrs.has_key(_key):
                        old_attrs[_key] = _value[0]

            for _key, _value in attrs.items():
                if not old_attrs.has_key(_key):
                    old_attrs[_key] = ''
            
            userAccountControl = old_attrs.get("userAccountControl")
            if not userAccountControl:
                userAccountControl = AuthConst.NORMAL_ACCOUNT
            
            userAccountControl = int(userAccountControl)
            if status:
                if userAccountControl&AuthConst.ACCOUNTDISABLE:
                    userAccountControl = userAccountControl&(~AuthConst.ACCOUNTDISABLE)
                else:
                    self.pool_release(conn_s)
                    return user_dn
            else:
                if userAccountControl&AuthConst.ACCOUNTDISABLE:
                    self.pool_release(conn_s)
                    return user_dn
                else:
                    userAccountControl = userAccountControl|AuthConst.ACCOUNTDISABLE
            
            attrs = {"userAccountControl": str(userAccountControl)}
            
            ldif = modlist.modifyModlist(old_attrs, attrs)
            retcode, _ = conn_s.modify_s(user_dn,ldif)
            self.pool_release(conn_s)
            if retcode != ErrorCodes.LDAP_MODIFY_S_SUCCESS:
                return Error(ErrorCodes.MODIFY_AUTH_ORGANIZATION_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_AUTH_ORGANIZATION_ERROR)

            return user_dn

        except Exception,e:
            logger.error("create user with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
