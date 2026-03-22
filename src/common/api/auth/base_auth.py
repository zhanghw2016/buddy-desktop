
import ldap
import ldap.modlist as modlist
from ldap.controls import SimplePagedResultsControl
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import auth_const as AuthConst
import uuid
from utils.json import json_load
import HTMLParser

AD_USER_ATTRS = ['userAccountControl', 'whenChanged','displayName', 'description', 'homePhone', 'physicalDeliveryOfficeName', 
                 'title', 'mail', 'telephoneNumber','accountExpires', "userPrincipalName", "sAMAccountName"]

AD_COMPUTE_ATTRS = ['name', 'dNSHostName']
AUTH_ORGANIZATION_ATTRS = ['ou', 'description', 'objectGUID', 'name']

AD_USER_GROUP = ['description', 'mail', 'info', 'groupType', 'member']
RETURN_LIST_KEY = ["memberOf"]
PAGE_SIZE = 500
from conn_manager import ConnectionManager

class BaseServerAuth(object):

    def __init__(self, base_dn, admin, password, server_host,
                 server_port=389, secret_port=636):

        self.uri = "ldap://%s:%s" % (server_host, server_port)
        self.uri_s = "ldaps://%s:%s" % (server_host, secret_port)
        self.admin = admin
        self.password = password
        self.base_dn = base_dn
        self.conn = None
        self.conn_s = None
        self.server_port = server_port
        self.secret_port = secret_port
        self.conn_manager = ConnectionManager(self.uri, self.admin, self.password)
        self.conn_manager_s = ConnectionManager(self.uri_s, self.admin, self.password)
        
    def _get_ou(self, path):

        ou = ''
        orgs = path.split('-')
        for org in orgs:
            if org:
                ou = "%s,ou=%s" % (ou, org)
        return ou[1:]
    
    def __str__(self):

        return "uri:%s,%base_dn:%s,admin:%s,password:%s" % (self.uri, self.base_dn, self.admin, self.password)
    
    def check_html_str(self, access_key):
        
        try:
            html_parser = HTMLParser.HTMLParser()
            return html_parser.unescape(access_key)
        
        except Exception,e:
            logger.error("convert password fail :%s" % e)
            return access_key
   
    def pool_conn(self, access_id=None, access_key=None):
        
        access_key = self.check_html_str(access_key)
        
        conn = self.conn_manager.connection(access_id, access_key)
        self.conn = conn
        return conn


    def pool_conn_s(self, access_id=None, access_key=None):
        
        access_key = self.check_html_str(access_key)
        
        conn_s = self.conn_manager_s.connection(access_id, access_key)
        self.conn_s = conn_s
        return conn_s
    
    def pool_release(self, conn, is_unbind=False):
        
        if not conn:
            return None
        
        self.conn_manager.release_connection(conn, is_unbind=is_unbind)
    
    def create_organization_unit(self, parent_dn, attrs):

        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            attrs['objectClass'] = ['organizationalUnit','top']
            dn = 'ou=%s,%s' % (attrs['ou'], parent_dn)
            ldif = modlist.addModlist(attrs)

            retcode, _ = conn_s.add_s(dn,ldif)
            self.pool_release(conn_s)

            if retcode != ErrorCodes.LDAP_ADD_S_SUCCESS:
                return Error(ErrorCodes.CREATE_AUTH_ORGANIZATION_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_AUTH_ORGANIZATION_ERROR)

            return dn
        except Exception,e:
            logger.error("create organization with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def modify_organization_unit(self, dn, attrs={}):
        try:

            dn_list = dn.split(',')[1:]
            org_name = dn.split(',')[0][3:]
            parent_dn = ",".join(dn_list)
            
            ous = self.describe_organization_units(parent_dn, org_name, 1)
            if not ous:
                return None
            
            modify_ou = ous[0]
            
            old_attrs = {}
            for key, value in modify_ou.items():
                if key in attrs and attrs[key] != value:
                    old_attrs[key] = value
            
            if not old_attrs:
                return None
            
            conn_s = self.pool_conn_s(self.admin, self.password)

            ldif = modlist.modifyModlist(old_attrs, attrs)
            retcode, _ = conn_s.modify_s(dn,ldif)
            self.pool_release(conn_s)
            if retcode != ErrorCodes.LDAP_MODIFY_S_SUCCESS:
                return Error(ErrorCodes.MODIFY_AUTH_ORGANIZATION_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_AUTH_ORGANIZATION_ERROR)

            return dn
        except Exception,e:
            logger.error("modify organization with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def delete_organization_units(self, dns=[]):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            for dn in dns:
                retcode,_,_,_ = conn_s.delete_s(dn)
                if retcode != ErrorCodes.LDAP_DELETE_S_SUCCESS:
                    return Error(ErrorCodes.DELETE_AUTH_ORGANIZATIONS_ERROR,
                                 ErrorMsg.ERR_MSG_DELETE_AUTH_ORGANIZATIONS_ERROR)
            
            self.pool_release(conn_s)
            
            return dns
        except Exception, e:
            logger.error("delete organizations with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def describe_organization_units(self, parent_dn='', org_names=[], scope=0):
        try:
            
            if org_names and not isinstance(org_names, list):
                org_names = [org_names]
            
            conn = self.pool_conn(self.admin, self.password)

            filterstr = '(&(objectclass=organizationalUnit)'
            filterstr += '(!(OU=Domain Controllers))'
            if org_names:
                filterstr += "(|"
            for dn in org_names:
                objectGUID = '(ou=%s)' % dn
                filterstr += objectGUID
            filterstr += ')'
            if org_names:
                filterstr += ")"

            result = []
            msgid = None
            if not parent_dn:
                parent_dn = self.base_dn

            pg_ctrl = SimplePagedResultsControl(True, size=PAGE_SIZE, cookie="")
            while True:
                if scope>0:
                    msgid = conn.search_ext(parent_dn, ldap.SCOPE_SUBTREE, filterstr,
                                            AUTH_ORGANIZATION_ATTRS,serverctrls=[pg_ctrl])
                else:
                    msgid = conn.search_ext(parent_dn, ldap.SCOPE_ONELEVEL, filterstr,
                                            AUTH_ORGANIZATION_ATTRS,serverctrls=[pg_ctrl])
                _a, res_data, _b, srv_ctrls = conn.result3(msgid)
                result.extend(res_data)
                cookie = srv_ctrls[0].cookie
                if cookie:
                    pg_ctrl.cookie = cookie
                else:
                    break
            
            self.pool_release(conn)
            if result == None:
                return Error(ErrorCodes.DESCRIBE_AUTH_ORGANIZATIONS_ERROR,
                                 ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

            ret = []
            for dn, entry in result:
                if not isinstance(entry, dict):
                    continue
                if dn != parent_dn:
                    item = {'dn': dn}
                    for _key, _value in entry.items():
                        if _key == "objectGUID":
                            item[_key] = str(uuid.UUID(bytes_le=_value[0]))
                            continue
                        
                        item[_key] = _value[0]
                    ret.append(item)

            return ret
        except Exception,e:
            logger.error("describe organizations with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
    
    def modify_user(self, dn, attrs={}):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            result = conn_s.search_s(dn, ldap.SCOPE_SUBTREE, attrlist=AD_USER_ATTRS)

            old_attrs = {}
            for _dn, entry in result:
                for _key, _value in entry.items():
                    if attrs.has_key(_key):
                        old_attrs[_key] = _value[0]

            for _key, _value in attrs.items():
                if not old_attrs.has_key(_key):
                    old_attrs[_key] = ''
            
            if old_attrs == attrs:
                self.pool_release(conn_s)
                return dn
            
            ldif = modlist.modifyModlist(old_attrs, attrs)
            retcode, _ = conn_s.modify_s(dn,ldif)
            self.pool_release(conn_s)
            if retcode != ErrorCodes.LDAP_MODIFY_S_SUCCESS:
                return Error(ErrorCodes.MODIFY_AUTH_ORGANIZATION_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_AUTH_ORGANIZATION_ERROR)
            
            
            
            return dn
        except Exception, e:
            logger.error("modify user with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
            
    def delete_users(self, dns=[]):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)
            for dn in dns:
                retcode,_,_,_ = conn_s.delete_s(dn)
                
                if retcode != ErrorCodes.LDAP_DELETE_S_SUCCESS:
                    self.pool_release(conn_s)
                    return Error(ErrorCodes.DELETE_AUTH_USERS_ERROR,
                                 ErrorMsg.ERR_MSG_DELETE_AUTH_USERS_ERROR)
            self.pool_release(conn_s)
            
            return dns
        except Exception, e:
            logger.error("delete users with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
        
    
    def change_user_organizaion(self, user_dn, new_org_dn):
        try:
            conn_s = self.pool_conn_s(self.admin, self.password)

            cn = user_dn.split(',')[0]
            ret = conn_s.rename_s(user_dn, cn, new_org_dn)
            self.pool_release(conn_s)
            if not ret:
                return Error(ErrorCodes.CHANGE_AUTH_USER_IN_ORGANIZATION_ERROR,
                             ErrorMsg.ERR_MSG_CHANGE_AUTH_USER_IN_ORGANIZATION_ERROR)
                        
            return '%s,%s' % (cn, new_org_dn)
        except Exception,e:
            logger.error("change user organization with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
            
    def check_auth_error(self, error_msg):
        
        if not error_msg:
            return None
        
        error_msg = json_load(str(error_msg).replace('\'', '\"'), suppress_warning=True)
        if not error_msg:
            return None
        
        info = error_msg.get("info")
        if not info:
            return None
        
        data_code = info.split("data ")
        if len(data_code) <= 1:
            return None

        error_code = data_code[1].split(",")[0]
        int_error_code = AuthConst.ERROR_CODE_HEX_MAP.get(error_code,5000)
        return Error(int_error_code,
                     AuthConst.ERR_LDAP_CODE_MAP.get(str(error_code), ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION))

