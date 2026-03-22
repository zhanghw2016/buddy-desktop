from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from .ad_service import ADServerAuth
from .ldap_service import LDAPServerAuth
from .local_service import LocalServerAuth
import constants as const
import copy
import auth_const as authconst
import time
import datetime
from utils.misc import get_current_time

class AuthUser():

    def __init__(self, ctx):
        
        self.ctx = ctx
        self.auth_services = {}
        self.zone_auths = {}
        self.refresh_auth_service()

    def refresh_auth_service(self):
        
        self.auth_services = {}
        ret = self.ctx.pgm.get_auth_services()
        if not ret:
            return None

        zone_auths = {}
        for auth_service_id, auth_service in ret.items():
            
            self.get_auth_service(auth_service_id)

            ret = self.ctx.pgm.get_auth_zones(auth_service_id)
            if not ret:
                continue
            
            for zone_id, auth_zone in ret.items():
                zone_auths[zone_id] = auth_service
                zone_auths[zone_id]["base_dn"] = auth_zone["base_dn"]
        
        self.zone_auths = zone_auths

        return None

    def convert_nt_to_unix(self, accountexpires):
        
        account_expires = int(accountexpires)
        
        if not account_expires or account_expires == 9223372036854775807:
            return 0
        
        unixtime = account_expires / 10000000 - 11644473600

        timeArray = time.localtime(unixtime)

        return time.strftime('%Y-%m-%d %H:%M:%S', timeArray)

    def convert_unix_to_nt(self, accountexpires):
        
        if accountexpires == 0:
            return 0

        timestamp = time.mktime(accountexpires.timetuple())
        nttime = (timestamp + 11644473600) * 10000000

        return nttime
    
    def get_account_expires(self, pwdLastSet=0):
        
        ret = self.ctx.pgm.get_auth_password_config()
        if not ret:
            return str(0)

        expire_period = int(ret.get(const.CUSTOM_ITEM_KEY_PASSWORD_EXPIRE_PREIOD, 0))
        if not expire_period:
            return str(0)

        if pwdLastSet and isinstance(pwdLastSet, str):
            pwdLastSet = datetime.datetime.strptime(pwdLastSet,'%Y-%m-%d %H:%M:%S')
        
        if not pwdLastSet:
            pwdLastSet = get_current_time()

        expires_time = pwdLastSet + datetime.timedelta(days =expire_period)
        return str(int(self.convert_unix_to_nt(expires_time)))

    def get_dc(self, base_dn):
        
        return base_dn[base_dn.replace('DC=','dc=').index('dc='):]
        
    def test_auth_service(self, auth_config, scope=0):
        
        config = copy.deepcopy(auth_config)
        
        base_dn = config["base_dn"]
        dc_dn = self.get_dc(base_dn)
        config["base_dn"] = dc_dn

        auth_service_type = config.get("auth_service_type", const.AUTH_TYPE_AD)
        if auth_service_type == const.AUTH_TYPE_LOCAL:
            return None
        
        if auth_service_type == const.AUTH_TYPE_AD:
            auth_service = ADServerAuth(config)
        else:
            auth_service = LDAPServerAuth(config)

        ret = auth_service.login(config["admin_name"], config["admin_password"])
        if isinstance(ret, Error) or not ret:
            return Error(ErrorCodes.AUHT_SERVICE_CONFIG_ERROR,
                         ErrorMsg.ERR_MSG_AUTH_SERVICE_CONN_ERROR)
        
        ret = auth_service.describe_organization_units(base_dn, scope=scope)
        if isinstance(ret, Error):
            logger.error("auth service base dn %s no found " % base_dn)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_AUTH_SERVICE_BASE_DN_NO_FOUND, base_dn)
        
        ret = self.format_auth_ous(ret)
        
        return ret
    
    def check_unicode_to_string(self, attrs):
        
        if isinstance(attrs, dict):
            for key, value in attrs.items():
                if isinstance(value, unicode):
                    attrs[key] = str(value).decode("string_escape").encode("utf-8")
                elif isinstance(value, dict):
                    self.check_unicode_to_string(value)
                elif isinstance(value, list):
                    value = self.check_unicode_to_string(value)
                    attrs[key] = value
            
            return attrs
                    
        elif isinstance(attrs, list):
            new_values = []
            for value in attrs:
                if isinstance(value, unicode):
                    value = str(value).decode("string_escape").encode("utf-8")
                
                if isinstance(value, dict):
                    self.check_unicode_to_string(value)

                new_values.append(value)
            
            return new_values
        elif isinstance(attrs, unicode):
            return str(attrs).decode("string_escape").encode("utf-8")
        
        return attrs

    def dn_to_path(self, dn):

        path_str = copy.deepcopy(dn)
        path_str = path_str[:path_str.replace('DC=','dc=').index('dc=')-1].replace('ou=','').replace('OU=','').replace('CN=','').replace('cn=','')
        path_list = path_str.split(',')
        path_list.reverse()
        path = '/'
        for path_item in path_list:
            path = path + path_item
            path = path + '/'
        path = path[:len(path)-1]

        return path
    
    def is_domain(self, ou_dn):
        
        index = ou_dn.replace('DC=','dc=').index('dc=')
        if index == 0:
            return True
        
        return False

    def get_domain_dn(self, domain):
    
        domain_list = domain.split(".")
        base_dn = ""
        for _list in domain_list:
            base_dn += "dc=%s," % _list
        
        base_dn = base_dn[:len(base_dn)-1]
    
        return base_dn

    def get_root_base_dn(self, ou_dns):
        
        if not isinstance(ou_dns, list):
            ou_dns = [ou_dns]
        
        root_base_dn = None

        for ou_dn in ou_dns:
            
            if self.is_domain(ou_dn):
                return ou_dn
                   
            _, base_dn = self.get_base_dn(ou_dn)
            if root_base_dn is None:
                root_base_dn = base_dn
            
            if root_base_dn not in base_dn:
                root_base_dn = base_dn

        return root_base_dn
    
    def format_base_dn(self, base_dn):

        base_dn = base_dn.replace('DC=','dc=').replace('CN=','cn=').replace('OU=','ou=')
        return base_dn
    
    def get_base_dn(self, dn):
        
        dn_list = dn.split(',')[1:]
        return dn.split(',')[0][3:], ",".join(dn_list)
    
    def check_user_change_password(self, auth_user):
        
        auth_service_type = const.AUTH_TYPE_AD
        auth_service_id = auth_user.get("auth_service_id")
        
        if auth_service_id:
            auth_service = self.ctx.pgm.get_auth_service(auth_service_id)
            if not auth_service:
                logger.error("get auth service, no found service %s" % auth_service_id)
                return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                             ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, auth_service_id)
            
            auth_service_type = auth_service["auth_service_type"]

        userAccountControl = auth_user.get("user_control", authconst.NORMAL_ACCOUNT)

        if auth_service_type == const.AUTH_TYPE_LOCAL:
            if userAccountControl == authconst.PASSWORD_MUST_CHANGE:
                return Error(authconst.ERROR_CODE_HEX_MAP.get(authconst.ERROR_PASSWORD_MUST_CHANGE), 
                             authconst.ERR_MSG_PASSWORD_MUST_CHANGE)
        elif auth_service_type == const.AUTH_TYPE_AD:
            pwdLastSet = auth_user.get("pwdLastSet", 0)
            if pwdLastSet == 0 and not int(userAccountControl)&authconst.DONT_EXPIRE_PASSWORD:
                return Error(authconst.ERROR_CODE_HEX_MAP.get(authconst.ERROR_PASSWORD_MUST_CHANGE), 
                             authconst.ERR_MSG_PASSWORD_MUST_CHANGE)

        return None

    def update_auth_service(self, auth_service_id):

        auth_service = self.ctx.pgm.get_auth_service(auth_service_id)
        if not auth_service:
            logger.error("get auth service, no found service %s" % auth_service_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, auth_service_id)

        auth_service_type = auth_service["auth_service_type"]
        if auth_service_type == const.AUTH_TYPE_AD:
            self.auth_services[auth_service_id] = ADServerAuth(auth_service)
        elif auth_service_type == const.AUTH_TYPE_LDAP:
            self.auth_services[auth_service_id] = LDAPServerAuth(auth_service)
        else:
            self.auth_services[auth_service_id] = LocalServerAuth(auth_service, self.ctx)
    
    def get_auth_service(self, auth_service_id):

        auth_service = self.auth_services.get(auth_service_id)
        if auth_service:
            return auth_service

        auth_service = self.ctx.pgm.get_auth_service(auth_service_id)
        if not auth_service:
            logger.error("get auth service, no found service %s" % auth_service_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, auth_service_id)
        
        auth_service_type = auth_service["auth_service_type"]
        if auth_service_type == const.AUTH_TYPE_AD:
            self.auth_services[auth_service_id] = ADServerAuth(auth_service)
        elif auth_service_type == const.AUTH_TYPE_LDAP:
            self.auth_services[auth_service_id] = LDAPServerAuth(auth_service)
        else:
            self.auth_services[auth_service_id] = LocalServerAuth(auth_service, self.ctx)

        return self.auth_services[auth_service_id]

    def get_auth_user_dns(self, auth_service_id, user_names):

        ret = self.get_auth_users(auth_service_id, user_names=user_names)
        if isinstance(ret, Error):
            return ret

        user_dns = {}
        for user_name, auth_user in ret.items():
            user_dn = auth_user["user_dn"]
            user_dns[user_name] = user_dn

        return user_dns

    def format_auth_computes(self, auth_compute_set):

        auth_computes = {}
        if not auth_compute_set:
            return auth_computes

        for auth_compute in auth_compute_set:
            self.check_unicode_to_string(auth_compute)

            compute = {}
            dn = auth_compute['dn'].replace('DC=','dc=').replace('CN=','cn=').replace('OU=','ou=')
            compute_name, _ = self.get_base_dn(dn)

            compute['name'] = auth_compute["name"]
            compute["objectGUID"] = auth_compute["objectGUID"]
            compute["objectSid"] = auth_compute["objectSid"]
            compute["operatingSystem"] = auth_compute.get("operatingSystem", "")
            compute_name = compute_name.lower()
            auth_computes[compute_name] = compute

        return auth_computes


    def get_auth_computes(self, auth_service_id, ou_dn=None, compute_names=None, search_name=None, scope=1):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            logger.error("no found auth service % "% auth_service_id)
            return {}

        auth_service = ret
        if not compute_names:
            compute_names = []
        if compute_names and not isinstance(compute_names, list):
            compute_names = [compute_names]

        if not ou_dn:
            ou_dn = auth_service.base_dn

        ret = auth_service.describe_computes(ou_dn, compute_names, scope=scope, search_compute_name=search_name)
        if isinstance(ret, Error) or not ret:
            return {}
        auth_user_set = ret

        return self.format_auth_computes(auth_user_set)

    def get_auth_users(self, auth_service_id, ou_dn=None, user_names=None, search_name=None, scope=1, cn_name=None, object_guid=None, index_uuid=False):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            logger.error("no found auth service % "% auth_service_id)
            return {}

        auth_service = ret
        if not user_names:
            user_names = []
        if user_names and not isinstance(user_names, list):
            user_names = [user_names]

        if not ou_dn:
            ou_dn = auth_service.base_dn

        ret = auth_service.describe_users(ou_dn, user_names, scope=scope, search_username=search_name, cn_names=cn_name, object_guid=object_guid)
        if isinstance(ret, Error) or not ret:
            return {}
        auth_user_set = ret
        
        return self.format_auth_users(auth_user_set, index_uuid)

    def format_auth_users(self, auth_user_set, index_uuid=False):

        auth_users = {}
        if not auth_user_set:
            return auth_users

        for auth_user in auth_user_set:
            
            self.check_unicode_to_string(auth_user)

            user = {}
            dn = auth_user['dn'].replace('DC=','dc=').replace('CN=','cn=').replace('OU=','ou=')
            user_name, ou_dn = self.get_base_dn(dn)

            userPrincipalName = auth_user.get("userPrincipalName")
            sAMAccountName = auth_user.get("sAMAccountName")
            
            if sAMAccountName:
                user_name = sAMAccountName
            else:
                user_name = userPrincipalName.split('@')[0]

            user["user_dn"] = dn
            user['user_name'] = user_name
            user['path'] = self.dn_to_path(dn)
            user['personal_phone'] = auth_user.get('telephoneNumber', '')
            user['position'] = auth_user.get('physicalDeliveryOfficeName', '')
            user['description'] = auth_user.get('description', '')
            user['title'] = auth_user.get('title', '')
            user['email'] = auth_user.get('mail', '')
            user['object_guid'] = auth_user.get('objectGUID')
            user['real_name'] = auth_user.get('displayName', auth_user['dn'].split(',')[0][3:])
            user['company_phone'] = auth_user.get('homePhone', '')

            if "user_control" in auth_user:
                user['user_control'] = int(auth_user.get('user_control', 0))

            if "userAccountControl" in auth_user:
                user['user_control'] = int(auth_user.get('userAccountControl', 0))
            
            status = int(auth_user.get('userAccountControl', 0))
            user['status'] = const.AUTH_USER_STATUS_DISABLED if status & const.AUTH_USER_ACCOUNT_CONTROL_ACCOUNTDISABLE > 0 else const.AUTH_USER_STATUS_ACTIVE
            user["ou_dn"] = ou_dn
            user['accountExpires'] = self.convert_nt_to_unix(auth_user.get('accountExpires', 0))
            user['badPasswordTime'] = self.convert_nt_to_unix(auth_user.get('badPasswordTime', 0))
            user['badPwdCount'] = int(auth_user.get('badPwdCount', 0))
            user['pwdLastSet'] = self.convert_nt_to_unix(auth_user.get('pwdLastSet', 0))
            
            if index_uuid:
                auth_users[user['object_guid']] = user
            else:
                auth_users[user_name] = user

        return auth_users

    def create_auth_user(self, auth_service_id, base_dn, user):
        
        self.check_unicode_to_string(user)
        
        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        
        auth_service_type = auth_service.service_type
        if auth_service_type == const.AUTH_TYPE_LOCAL:
            user["auth_service_id"] = auth_service_id
            user["base_dn"] = base_dn
        
        user_info = auth_service.build_user_info(user)
        
        if auth_service_type != const.AUTH_TYPE_LOCAL:
            user_info["accountExpires"] = self.get_account_expires()

        ret = auth_service.create_user(base_dn, user_info)
        if isinstance(ret, Error):
            return ret
        return ret

    def modify_auth_user(self, auth_service_id, user_dn, attrs):
        
        self.check_unicode_to_string(attrs)
        
        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret

        ret = auth_service.modify_user(user_dn, attrs)
        if isinstance(ret, Error):
            return ret
        
        return ret
    
    def delete_auth_users(self, auth_service_id, user_names):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        
        ret = self.get_auth_user_dns(auth_service_id, user_names)
        if isinstance(ret, Error):
            return ret
        if not ret:
            return None
        user_dns = ret

        ret = auth_service.delete_users(user_dns.values())
        if isinstance(ret, Error):
            return ret

        return ret
    
    def update_auth_user_password_info(self, auth_service_id, user_dn, user_name, new_password, is_expired=False):
        
        if not is_expired:
            ret = self.auth_login(auth_service_id, user_name, new_password)
            if isinstance(ret, Error):
                return ret

        # reset user password accountExpires and badPwdCount
        ret = self.get_auth_users(auth_service_id, user_names=user_name)
        if not ret:
            logger.error("modify auth user password no found user %s" % user_name)
            return None
        auth_user = ret[user_name]

        pwdLastSet = auth_user["pwdLastSet"]
        accountExpires = self.get_account_expires(pwdLastSet)
        ret = self.modify_auth_user(auth_service_id, user_dn, {"accountExpires": accountExpires})
        if isinstance(ret, Error):
            return ret

        if is_expired:
            ret = self.auth_login(auth_service_id, user_name, new_password)
            if isinstance(ret, Error):
                return ret

        return None
    
    def modify_auth_user_password(self, auth_service_id, user_name, old_password, new_password):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        
        is_expired = False
        
        ret = auth_service.login(user_name, old_password)
        if isinstance(ret, Error):
            if ret.code not in [authconst.ERROR_CODE_HEX_MAP[authconst.ERROR_PASSWORD_MUST_CHANGE],
                                authconst.ERROR_CODE_HEX_MAP[authconst.ERROR_ACCOUNT_EXPIRED],
                                authconst.ERROR_CODE_HEX_MAP[authconst.ERROR_PASSWORD_EXPIRED]]:
                return ret
            
            if ret.code in [authconst.ERROR_CODE_HEX_MAP[authconst.ERROR_ACCOUNT_EXPIRED]]:
                is_expired = True

        ret = self.get_auth_user_dns(auth_service_id, user_name)
        if isinstance(ret, Error):
            return ret

        if not ret:
            return None

        user_dns = ret
        user_dn = user_dns[user_name]
        
        ret = auth_service.set_password(user_dn, new_password)
        if isinstance(ret, Error):
            return ret
        
        ret = self.update_auth_user_password_info(auth_service_id, user_dn, user_name, new_password, is_expired)
        if isinstance(ret, Error):
            return ret
        
        return None

    def reset_auth_user_password(self, auth_service_id, user_name, password):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret

        ret = self.get_auth_user_dns(auth_service_id, user_name)
        if isinstance(ret, Error):
            return ret
        if not ret:
            return None

        user_dns = ret
        user_dn = user_dns[user_name]

        is_expired = False
        
        ret = auth_service.login(user_name, password)
        if isinstance(ret, Error):
            if ret.code in [authconst.ERROR_CODE_HEX_MAP[authconst.ERROR_ACCOUNT_EXPIRED]]:
                is_expired = True

        ret = auth_service.set_password(user_dn, password)
        if isinstance(ret, Error):
            return ret

        ret = self.update_auth_user_password_info(auth_service_id, user_dn, user_name, password, is_expired)
        if isinstance(ret, Error):
            return ret

        return None
    
    def format_auth_ous(self, auth_ou_set):
        
        if not auth_ou_set:
            return None

        auth_ous = {}
        for auth_ou in auth_ou_set:
            
            self.check_unicode_to_string(auth_ou)
            
            ou_info = {}

            dn = auth_ou["dn"].replace('DC=','dc=').replace('CN=','cn=').replace('OU=','ou=')
            ou_name, base_dn = self.get_base_dn(dn)
            ou_info["ou_dn"] = dn
            ou_info["ou_name"] = ou_name
            ou_info["base_dn"] = base_dn   
            ou_info['path'] = self.dn_to_path(dn)
            ou_info["description"] = auth_ou.get("description", '')
            ou_info["object_guid"] = auth_ou["objectGUID"]
            
            auth_ous[dn] = ou_info
        
        return auth_ous

    def get_auth_ous(self, auth_service_id, base_dn=None, ou_names=None, scope=1):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret

        if not base_dn:
            base_dn = auth_service.base_dn
        if not ou_names:
            ou_names = []
        
        ret = auth_service.describe_organization_units(base_dn, ou_names, scope)
        if isinstance(ret, Error):
            return ret
        auth_ou_set = ret

        return self.format_auth_ous(auth_ou_set)

    def create_auth_ou(self, auth_service_id, base_dn, attrs):
        
        self.check_unicode_to_string(attrs)

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        
        ret = auth_service.create_organization_unit(base_dn, attrs)
        if isinstance(ret, Error):
            return ret

        return ret
    
    def modify_auth_ou(self, auth_service_id, ou_dn, attrs):
        
        self.check_unicode_to_string(attrs)
        
        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
    
        ret = auth_service.modify_organization_unit(ou_dn, attrs)
        if isinstance(ret, Error):
            return ret
        
        return ret

    def delete_auth_ous(self, auth_service_id, ou_dns):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        
        if not isinstance(ou_dns, list):
            ou_dns = [ou_dns]

        ret = auth_service.delete_organization_units(ou_dns)
        if isinstance(ret, Error):
            return ret
        
        return ret
    
    def change_auth_user_ou_dn(self, auth_service_id, ou_dn, user_dn):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        
        ret = auth_service.change_user_organizaion(user_dn, ou_dn)
        if isinstance(ret, Error):
            return ret
        
        return ret

    def format_auth_user_groups(self, user_group_set, index_name=False):

        auth_user_groups = {}
        if not user_group_set:
            return auth_user_groups
        
        for user_group in user_group_set:
            
            self.check_unicode_to_string(user_group)
            
            group_info = {}
            dn = user_group['dn'].replace('DC=','dc=').replace('CN=','cn=').replace('OU=','ou=')
            user_group_name, base_dn = self.get_base_dn(dn)
            group_info["user_group_dn"] = dn
            group_info["base_dn"] = base_dn
            group_info["member"] = user_group.get("member", [])
            group_info["object_guid"] = user_group["objectGUID"]
            group_info['user_group_name'] = user_group_name
            group_info['path'] = self.dn_to_path(dn)
            group_info['description'] = user_group.get("description", '')
            
            format_members = []
            for member in group_info["member"]:
                _member = self.format_base_dn(member)
                format_members.append(_member)
            
            group_info["member"] = format_members
            if index_name:
                auth_user_groups[user_group_name] = group_info
            else:
                auth_user_groups[dn] = group_info

        return auth_user_groups

    def get_auth_user_groups(self, auth_service_id, base_dn=None, user_group_names=None, search_name=None, scope=1, index_name=False):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return {}
        auth_service = ret
        
        if not user_group_names:
            user_group_names = []
        
        if user_group_names and not isinstance(user_group_names, list):
            user_group_names = [user_group_names]
    
        ret = auth_service.describe_user_groups(base_dn, user_group_names, scope = scope, search_name=search_name)
        if isinstance(ret, Error) or not ret:
            return {}
        user_group_set = ret

        return self.format_auth_user_groups(user_group_set, index_name=index_name)

    def create_auth_user_group(self, auth_service_id, base_dn, attrs):
        
        self.check_unicode_to_string(attrs)

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret

        ret = auth_service.create_user_group(base_dn, attrs)
        if isinstance(ret, Error):
            return ret
        
        return ret
    
    def rename_auth_user_dn(self, auth_service_id, user_dn, new_name, dn_type, login_name=None):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret

        ret = auth_service.rename_user_dn(user_dn, new_name, dn_type, login_name)
        if isinstance(ret, Error):
            return ret

        return ret  

    def modify_auth_user_group(self, auth_service_id, user_group_dn, attrs):
        
        self.check_unicode_to_string(attrs)

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        group_name, base_dn = self.get_base_dn(user_group_dn)

        ret = self.get_auth_user_groups(auth_service_id, base_dn=base_dn, user_group_names=group_name)
        if isinstance(ret, Error):
            return ret
        if not ret:
            return None

        auth_group = ret.get(user_group_dn)
        if not auth_group:
            return None

        ret = auth_service.modify_user_group(user_group_dn, attrs)
        if isinstance(ret, Error):
            return ret

        return ret
    
    def delete_auth_user_groups(self, auth_service_id, user_group_dns):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        
        ret = auth_service.delete_user_groups(user_group_dns)
        if isinstance(ret, Error):
            return ret
        
        return ret
    
    def add_auth_user_to_user_group(self, auth_service_id, user_names, user_group_dn):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret
        
        ret = self.get_auth_user_dns(auth_service_id, user_names)
        if isinstance(ret, Error):
            return ret
        if not ret:
            return None
        
        auth_user_dns = ret
        user_dns = auth_user_dns.values()
        ret = auth_service.insert_user_to_user_group(user_group_dn, user_dns)
        if isinstance(ret, Error):
            return ret
        
        return ret

    def remove_auth_user_from_user_group(self, auth_service_id, user_names, user_group_dn):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret

        ret = self.get_auth_user_dns(auth_service_id, user_names)
        if isinstance(ret, Error):
            return ret

        if not ret:
            return None

        auth_user_dns = ret
        user_dns = auth_user_dns.values()
        
        ret = auth_service.remove_user_from_user_group(user_group_dn, user_dns)
        if isinstance(ret, Error):
            return ret
        
        return ret
    
    def auth_login(self, auth_service_id, user_name, passowrd):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret

        ret = auth_service.login(user_name, passowrd)
        if isinstance(ret, Error):
            return ret
        
        return ret
    
    def set_auth_user_status(self, auth_service_id, user_name, user_dn, status):

        ret = self.get_auth_service(auth_service_id)
        if isinstance(ret, Error):
            return ret
        auth_service = ret

        ret = auth_service.set_auth_user_status(user_name, user_dn, status)
        if isinstance(ret, Error):
            return ret

        return ret
