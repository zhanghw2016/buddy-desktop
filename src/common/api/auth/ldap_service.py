
import ldap
import ldap.modlist as modlist
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error

AD_USER_ATTRS = ['userAccountControl', 'displayName', 'description', 'homePhone', 'physicalDeliveryOfficeName', 'title', 'mail', 'telephoneNumber','accountExpires']
AD_COMPUTE_ATTRS = ['name', 'dNSHostName']
AD_USER_GROUP = ['description', 'mail', 'info', 'groupType', 'member']
RETURN_LIST_KEY = ["memberOf"]
PAGE_SIZE = 500
from .base_auth import BaseServerAuth
import constants as const
            
class LDAPServerAuth(BaseServerAuth):
    '''linux ldap server authentication'''

    def __init__(self, conn):
        
        self.domain = conn["domain"]
        self.base_dn = conn["base_dn"]
        self.admin = conn["admin_name"]
        self.password = conn["admin_password"]
        self.server_host = conn["host"]
        self.server_port = conn["port"]
        self.secret_port= conn["secret_port"]
        self.service_type = const.AUTH_TYPE_LDAP
        super(LDAPServerAuth, self).__init__(self.base_dn, self.admin, self.password, self.server_host,
                                             self.server_port, self.secret_port)

    def build_user_info(self, user):

        user_info = {}
        user_keys = ['userPassword', 'displayName', 'description', 'physicalDeliveryOfficeName', 'title', 'mail', 'telephoneNumber', 'homePhone']
        for key in user_keys:
            if key in user:
                user_info[key] = user[key]

        user_info['cn'] = str(user['user_name'])

        return user_info

    def login(self, auth_dn, auth_passwd):
        try:
            # login
            cn = auth_dn.split(',')[0].split('=')
            conn = self._conn()
            conn.simple_bind_s(auth_dn, auth_passwd)

            # get user info
            ret = conn.search_s(
                self.base_dn, ldap.SCOPE_SUBTREE,
                "%s=%s" % (cn[0], cn[1]))
            if ret is None or len(ret) == 0:
                return False

            return True
        except Exception, e:
            logger.error("login to server [%s] for [%s] failed, [%s]" % (self.uri, auth_dn, e))
            return False
    
    def create_user(self, org_dn, user={}):
        user['objectclass'] = ['top', 'person', 'inetOrgPerson']
        try:
            conn = self._conn()
            conn.bind_s(self.admin, self.password)

            user['objectclass'] = ['top', 'person', 'inetOrgPerson']
            user['sn'] = user['cn']
            dn = "cn=%s,%s" % (user['cn'], org_dn)
            ldif = modlist.addModlist(user)

            retcode, _ = conn.add_s(dn, ldif)
            if retcode != ErrorCodes.LDAP_ADD_S_SUCCESS:
                return Error(ErrorCodes.CREATE_AUTH_USER_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_AUTH_USER_ERROR)

            return dn
        except Exception,e:
            logger.error("create user with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)

    def modify_password(self, user_dn, old_password, new_password):
        try:
            conn = self._conn()
            conn.bind_s(self.admin, self.password)
            conn.passwd_s(user_dn, old_password, new_password)

            return user_dn
        except Exception,e:
            logger.error("modify user password with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
    
    def set_password(self, user_dn, password):
        try:
            conn = self._conn()
            conn.bind_s(self.admin, self.password)
            conn.passwd_s(user_dn, None, password)

            return user_dn
        except Exception,e:
            logger.error("reset user password with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)
    
    def describe_users(self, org_dn='', usernames = [], object_guid=None):
        try:
            conn = self._conn()
            conn.bind_s(self.admin, self.password)
            
            filterstr = '(&(objectclass=person)'
            if len(usernames) > 0:
                filterstr = filterstr + '(|'
            for cn in usernames:
                cn = '(cn=%s)' % cn
                filterstr += cn
            if len(usernames) > 0:
                filterstr += '))'
            else:
                filterstr += ')'

            result = []
            if org_dn:
                result = conn.search_s(org_dn, ldap.SCOPE_SUBTREE, filterstr, 
                                       attrlist=AD_USER_ATTRS)
            else:
                result = conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, filterstr, 
                                       attrlist=AD_USER_ATTRS)

            if result == None:
                return Error(ErrorCodes.DESCRIBE_AUTH_USERS_ERROR,
                                 ErrorMsg.ERR_MSG_DESCRIBE_AUTH_USERS_ERROR)

            ret = []
            for dn, entry in result:
                item = {'dn': dn}
                for _key, _value in entry.items():
                    item[_key] = _value[0]
                ret.append(item)

            return ret
        except Exception,e:
            logger.error("describe users with Exception:%s" % e)
            return Error(ErrorCodes.AUTH_SERVER_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION)