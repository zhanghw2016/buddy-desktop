
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
from utils.id_tool import (
    UUID_TYPE_DESKTOP_USER, 
    UUID_TYPE_DESKTOP_OU,
    get_uuid,
    UUID_TYPE_DESKTOP_USER_GROUP
)
import random
import db.constants as dbconst
from utils.misc import get_current_time
from utils.auth import check_password, get_hashed_password
from db.data_types import SearchType
import auth_const as AuthConst

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

class LocalServerAuth():

    def __init__(self, conn, ctx=None):

        self.domain = conn["domain"]
        self.base_dn = conn["base_dn"]
        self.admin = conn["admin_name"]
        self.password = conn["admin_password"]
        self.service_type = const.AUTH_TYPE_LOCAL
        self.ctx = ctx
        self.auth_service_id = conn["auth_service_id"]

    def get_local_user_base_dn(self, dn):
        
        dn_list = dn.split(',')[1:]
        return dn.split(',')[0][3:], ",".join(dn_list)


    def get_user_by_dn(self, user_dns):
        
        if not user_dns:
            return None
        
        if not isinstance(user_dns, list):
            user_dns = [user_dns]
        
        ret = self.ctx.pgm.get_user_by_user_dn(self.auth_service_id, user_dns)
        if not ret:
            return None

        return ret

    def get_user_group_by_dn(self, user_group_dns):
        
        if not user_group_dns:
            return None
        
        if not isinstance(user_group_dns, list):
            user_group_dns = [user_group_dns]
        
        ret = self.ctx.pgm.get_desktop_user_groups(self.auth_service_id, user_group_dns=user_group_dns, index_dn=True)
        if not ret:
            return None

        return ret

    def get_user_ou_by_dn(self, user_ous):
        
        if not user_ous:
            return None
        
        if not isinstance(user_ous, list):
            user_ous = [user_ous]
        
        ret = self.ctx.pgm.get_desktop_user_ous(user_ous)
        if not ret:
            return None

        return ret.values()[0]

    def build_user_info(self, user):
        
        base_dn = user.get("base_dn")
        if not base_dn:
            base_dn = self.base_dn
        
        auth_service_id = user.get("auth_service_id")
        if not auth_service_id:
            return None

        user_info = {}
        user_id = get_uuid(UUID_TYPE_DESKTOP_USER, self.ctx.checker, long_format=True)
        user_info["user_id"] = user_id
        user_info["auth_service_id"] = auth_service_id
        
        user_name = user.get("user_name")
        password = user.get("userPassword")
        if not user_name or not password:
            return None
        user_info["user_name"] = user_name
        real_name = user.get("displayName", "")
        if not real_name:
            real_name = user_name
        
        user_info["real_name"] = real_name

        user_info["personal_phone"] = user.get("telephoneNumber", "")
        user_info["email"] = user.get("mail", "")
        if not user_info["email"]:
            user_info["email"] = user.get("email", "")
            
        user_info["description"] = user.get("description", "")
        user_info["password"] = password
        
        user_info["ou_dn"] = base_dn
        user_info["user_dn"] = "cn=%s,%s" % (real_name, base_dn)
        user_info["status"] = const.USER_STATUS_ACTIVE
        user_info["create_time"] = get_current_time()

        object_guid = self.create_local_object_guid("local-user-")
        if not object_guid:
            object_guid = "local-guid-default"
        user_info["object_guid"] = object_guid
        
        user_control = user.get("account_control", 0)
        if not user_control:
            user_info["user_control"] = AuthConst.PASSWORD_MUST_CHANGE
        else:
            user_info["user_control"] = AuthConst.DONT_EXPIRE_PASSWORD
        
        return user_info

    def create_local_object_guid(self, prefix, width=16):

        count = 0
        if not prefix:
            prefix = "local-guid-"
        
        while True and count < 20:
            count += 1
            uuid = prefix
            for _ in range(width):
                uuid += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012356789')

            ret = self.ctx.pg.get_count(dbconst.TB_DESKTOP_USER, {"object_guid":uuid})
            if not ret:
                return uuid
        
        return None
    
    def login(self, user_name, auth_passwd):
        
        conditions = {}
        conditions["user_name"] = user_name
        conditions["auth_service_id"] = self.auth_service_id
        
        ret = self.ctx.pgm.get_local_auth_users(conditions)
        if not ret:
            logger.error("no found user %s" % (user_name))
            return Error(ErrorCodes.USER_NOT_FOUND,
                         ErrorMsg.ERR_CODE_MSG_DESCRIBE_USER_FAILED)
        
        user = ret[user_name]
        password = user["password"]
        if not check_password(auth_passwd, password) and password != auth_passwd:
            logger.error("check user session password %s fail" % (user_name))
            return Error(ErrorCodes.PASSWD_NOT_MATCHED,
                         ErrorMsg.ERR_CODE_MSG_USER_NOT_FOUND_OR_PASSWD_NOT_MATCHED)
        
        return None

    def create_user(self, org_dn, user):
        
        user_id = user["user_id"]
        user_info = {user_id: user}
        user["password"] = get_hashed_password(user["password"])
       
        if not self.ctx.pg.batch_insert(dbconst.TB_DESKTOP_USER, user_info):
            logger.error("insert newly created desktop user for [%s] to db failed" % (user_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        
        return user["user_dn"]

    def format_local_auth_users(self, auth_user_set):

        auth_users = {}
        if not auth_user_set:
            return auth_users
        
        local_users = []
        
        for auth_user in auth_user_set:
            
            user_name = auth_user["user_name"]
            user = {}
            user["dn"] = auth_user["user_dn"]
            user["userPrincipalName"] = "%s@%s" % (user_name, self.domain)
            user["sAMAccountName"] = user_name
            user["telephoneNumber"] = auth_user.get("personal_phone", "")
            user["description"] = auth_user.get("description", "")
            user["mail"] = auth_user.get("email", "")
            user["objectGUID"] = auth_user.get("object_guid", "")
            user["displayName"] = auth_user.get("real_name", "")
            user["user_control"] = auth_user.get("user_control")
            local_users.append(user)

        return local_users

    def describe_users(self, org_dn=None, user_names=None, scope=1, search_username=None, cn_names=None, object_guid=None):
        
        conditions = {}
        base_dn = self.ctx.pgm.user_unicode_to_string(org_dn)
        if scope:
            conditions["ou_dn"] = SearchType(base_dn)
        else:
            conditions["ou_dn"] = base_dn
        
        if search_username:
            conditions["user_name"] = SearchType(search_username)
        
        if user_names:
            conditions["user_name"] = user_names
        
        if cn_names:
            if not isinstance(cn_names, list):
                cn_names = [cn_names]
            
            user_dns = []
            for cn_name in cn_names:
                cn_name = 'cn=%s,%s' % (cn_name, org_dn)
                user_dns.append(cn_name)
            
            conditions["user_dn"] = user_dns
        
        ret = self.ctx.pgm.get_local_auth_users(conditions)
        if not ret:
            return None
        
        return self.format_local_auth_users(ret.values())

    def modify_user(self, dn, attrs={}):
        
        modify_keys = {
            "description": "description",
            "mail": "email",
            "telephoneNumber": "personal_phone",
            }

        ret = self.get_user_by_dn(dn)
        if not ret:
            return None
        
        user = ret.get(dn)
        if not user:
            return None
        
        user_id = user["user_id"]
        
        update_info = {}
        for key, value in modify_keys.items():
            if key in attrs:
                update_info[value] = attrs[key]
        
        if not update_info:
            return dn
        
        if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER, {user_id: update_info}):
            logger.error("modify desktop group update fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

        return dn

    def delete_users(self, user_dns):
        
        ret = self.get_user_by_dn(user_dns)
        if not ret:
            return None
        
        users = ret
        
        user_ids = []
        
        for _, user in users.items():
            user_id = user["user_id"]
            user_ids.append(user_id)
        
        conditions = {"user_id": user_ids}
        
        self.ctx.pg.base_delete(dbconst.TB_DESKTOP_USER, conditions)
        
        return user_dns
    
    def set_password(self, user_dn, password):
        
        ret = self.get_user_by_dn(user_dn)
        if not ret:
            return None
        
        users = ret
        user = users.get(user_dn)
        if not user:
            return None
        
        user_id = user["user_id"]
        # update_info = {"password": password}
        update_info = {"password": get_hashed_password(password)}

        user_control = user.get("user_control")
        if user_control == AuthConst.PASSWORD_MUST_CHANGE:
            update_info["user_control"] = AuthConst.DONT_EXPIRE_PASSWORD

        if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER, {user_id: update_info}):
            logger.error("modify desktop group update fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

        return user_dn

    def create_user_group(self, parent_dn, attrs):
        
        base_dn = parent_dn
        if not base_dn:
            base_dn = self.base_dn

        user_group_info = {}
        user_group_id = get_uuid(UUID_TYPE_DESKTOP_USER_GROUP, self.ctx.checker, long_format=True)
        user_group_info["user_group_id"] = user_group_id
        user_group_info["auth_service_id"] = self.auth_service_id
        
        user_group_name = attrs.get("user_group_name")
        if not user_group_name:
            return None
    
        user_group_info["user_group_name"] = user_group_name
        user_group_info["description"] = attrs.get("description", "")
        user_group_info["base_dn"] = parent_dn
        
        user_group_info["user_group_dn"] = "cn=%s,%s" % (user_group_name, base_dn)
        user_group_info["create_time"] = get_current_time()

        object_guid = self.create_local_object_guid("local-user_group-")
        if not object_guid:
            object_guid = "local-guid-default"
        user_group_info["object_guid"] = object_guid

        user_info = {user_group_id: user_group_info}
        if not self.ctx.pg.batch_insert(dbconst.TB_DESKTOP_USER_GROUP, user_info):
            logger.error("insert newly created desktop user for [%s] to db failed" % (user_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        
        return user_group_info["user_group_dn"]
    
    def rename_local_user(self, user_dn, new_name, login_name):

        old_user_name, ou_dn = self.get_local_user_base_dn(user_dn)
        if not old_user_name:
            return None
        
        conditions = {}
        conditions["user_dn"] = user_dn
        conditions["auth_service_id"] = self.auth_service_id
        ret = self.ctx.pgm.get_local_auth_users(conditions, index_dn=True)
        if not ret:
            logger.error("no found user %s" % (old_user_name))
            return Error(ErrorCodes.USER_NOT_FOUND,
                         ErrorMsg.ERR_CODE_MSG_DESCRIBE_USER_FAILED)
        
        user = ret.get(user_dn)
        if not user:
            logger.error("no found user %s" % (old_user_name))
            return Error(ErrorCodes.USER_NOT_FOUND,
                         ErrorMsg.ERR_CODE_MSG_DESCRIBE_USER_FAILED)
        user_id = user["user_id"]
        
        new_user_dn = 'cn=%s,%s' % (login_name, ou_dn)
        update_info = {"user_dn": new_user_dn, "user_name": login_name}
        if new_name is not None:
            update_info["real_name"] = new_name
        
        if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER, {user_id: update_info}):
            logger.error("modify desktop group update fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        return new_user_dn

    def rename_local_user_group(self, user_group_dn, new_name):

        old_user_group_name, ou_dn = self.get_local_user_base_dn(user_group_dn)
        if not old_user_group_name:
            return None
        
        conditions = {}
        conditions["user_group_name"] = old_user_group_name
        conditions["auth_service_id"] = self.auth_service_id
        
        ret = self.ctx.pgm.get_local_auth_user_group(conditions)
        if not ret:
            logger.error("no found user group %s" % (old_user_group_name))
            return Error(ErrorCodes.USER_NOT_FOUND,
                         ErrorMsg.ERR_CODE_MSG_DESCRIBE_USER_FAILED)
        
        user_group = ret[old_user_group_name]
        user_group_id = user_group["user_group_id"]
        
        new_user_group_dn = 'cn=%s,%s' % (new_name, ou_dn)
        update_info = {"user_group_dn": new_user_group_dn, "user_group_name": new_name}
        
        if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER_GROUP, {user_group_id: update_info}):
            logger.error("modify desktop group update fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        return new_user_group_dn

    def rename_local_user_ou(self, user_ou_dn, new_name):

        dn_list = user_ou_dn.split(',')[1:]
        parent_dn = ",".join(dn_list)    
        new_base_dn = 'ou=%s,%s' % (new_name, parent_dn)
        
        user_ous = self.ctx.pgm.search_user_ous(user_ou_dn, self.auth_service_id)
        if not user_ous:
            user_ous = {}
        
        
        update_users = {}
        update_user_groups= {}
        update_ous = {}
        for ou_dn, ou in user_ous.items():
            user_ou_id = ou["user_ou_id"]
            _ou_dn = ou["ou_dn"].replace(user_ou_dn, new_base_dn)
            _base_dn = ou["base_dn"].replace(user_ou_dn, new_base_dn)
            update_ous[user_ou_id] = {
                "ou_dn": _ou_dn,
                "base_dn": _base_dn
                }
            
            users = self.ctx.pgm.get_user_by_user_ou_dn(ou_dn)
            if users:
                for user_id, user in users.items():
                    real_name = user["real_name"] if user["real_name"] else user["user_name"]
                    update_users[user_id] = {
                        "ou_dn": _ou_dn,
                        "user_dn": "cn=%s,%s" % (real_name, _ou_dn)
                        }
                
            user_groups = self.ctx.pgm.get_user_group_by_user_group_ou_dn(ou_dn)
            if user_groups:
                for user_group_id, user_group in user_groups.items():
                    user_group_name = user_group["user_group_name"]
                    update_user_groups[user_group_id] = {
                            "base_dn": _ou_dn,
                            "user_group_dn": "cn=%s,%s" % (user_group_name,_ou_dn)
                            }
        
        if update_users:
            if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER, update_users):
                logger.error("modify desktop group update fail %s" % update_users)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        if update_user_groups:
            if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER_GROUP, update_user_groups):
                logger.error("modify desktop group update fail %s" % update_user_groups)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        if update_ous:
            if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER_OU, update_ous):
                logger.error("modify desktop group update fail %s" % update_ous)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)  
        
        return None

    def rename_user_dn(self, user_dn, new_name, dn_type=None, login_name=None):
        
        if dn_type == const.USER_DN_TYPE_USER:
           
            ret = self.rename_local_user(user_dn, new_name, login_name)
            if isinstance(ret, Error):
                return ret
        elif dn_type == const.USER_DN_TYPE_USER_GROUP:
            ret = self.rename_local_user_group(user_dn, new_name)
            if isinstance(ret, Error):
                return ret
        
        elif dn_type == const.USER_DN_TYPE_OU:
            ret = self.rename_local_user_ou(user_dn, new_name)
            if isinstance(ret, Error):
                return ret
    
        return None
        
    def modify_user_group(self, dn, attrs={}):
        
        modify_keys = {
            "description": "description",
            }

        ret = self.get_user_group_by_dn(dn)
        if not ret:
            return None
        
        user_group = ret.get(dn)
        if not user_group:
            return None
        
        user_group_id = user_group["user_group_id"]
        
        update_info = {}
        for key, value in modify_keys.items():
            if key in attrs:
                update_info[value] = attrs[key]
        
        if not update_info:
            return dn
        
        if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER_GROUP, {user_group_id: update_info}):
            logger.error("modify desktop group update fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

        return dn


    def delete_user_groups(self, dns=[]):
        
        ret = self.get_user_group_by_dn(dns)
        if not ret:
            return None
        
        user_groups = ret
        
        for _, user_group in user_groups.items():
            user_group_id = user_group["user_group_id"]
        
            conditions = {"user_group_id": user_group_id}
            self.ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)
            self.ctx.pg.delete(dbconst.TB_DESKTOP_USER_GROUP, user_group_id)

        return dns
    
    def get_local_user_group_users(self, user_group_id):
        
        ret = self.ctx.pgm.get_user_group_user(user_group_id)
        if not ret:
            return None

        user_ids = ret.keys()
        ret = self.ctx.pgm.get_desktop_users(user_ids)
        if not ret:
            return None
        
        user_dns = []
        for _, user in ret.items():
            
            user_dn = user["user_dn"]
            user_dns.append(user_dn)
        
        return user_dns

    def format_local_auth_user_groups(self, user_group_set):

        auth_user_groups = {}
        if not user_group_set:
            return auth_user_groups
        
        for user_group in user_group_set:

            user_group_id = user_group["user_group_id"]
            user_group_dn = user_group["user_group_dn"]
            group_info = {}
            group_info["dn"] = user_group_dn
            group_info["objectGUID"] = user_group["object_guid"]
            group_info['description'] = user_group.get("description", '')
            
            user_group_member = self.get_local_user_group_users(user_group_id)
            if not user_group_member:
                user_group_member = []

            group_info["member"] = user_group_member

            auth_user_groups[user_group_dn] = group_info

        return auth_user_groups

    def describe_user_groups(self, org_dn='', ug_names=[], scope=1, search_name=None):
        
        conditions = {}
       
        if not org_dn:
            org_dn = self.base_dn
        
        base_dn = self.ctx.pgm.user_unicode_to_string(org_dn)
        if scope:
            conditions["base_dn"] = SearchType(base_dn)
        else:
            conditions["base_dn"] = base_dn
        
        if ug_names:
            conditions["user_group_name"] = ug_names
        elif search_name:
            conditions["user_group_name"] = SearchType(search_name)
        
        ret = self.ctx.pgm.get_local_auth_user_group(conditions)
        if not ret:
            return None
        
        user_groups = self.format_local_auth_user_groups(ret.values())
        if not user_groups:
            user_groups = {}
        
        return user_groups.values()

    def insert_user_to_user_group(self, ug_dn, user_dns):
        
        ret = self.get_user_by_dn(user_dns)
        if not ret:
            return None
        
        local_users = ret
        user_names = {}
        for _, user in local_users.items():
            
            user_id = user["user_id"]
            user_name = user["user_name"]
            
            user_names[user_id] = user_name
        
        ret = self.get_user_group_by_dn(ug_dn)
        if not ret:
            return None
        
        user_group = ret[ug_dn]
        user_group_id = user_group["user_group_id"]
        
        user_group_users = self.ctx.pgm.get_user_group_user(user_group_id)
        if not user_group_users:
            user_group_users = {}
            
        for user_id, user_name in user_names.items():
            if user_id in user_group_users:
                continue
            new_group_users = {"user_id": user_id, "user_group_id": user_group_id, "user_name": user_name}

            if not self.ctx.pg.base_insert(dbconst.TB_DESKTOP_USER_GROUP_USER, new_group_users):
                logger.error("user group user insert new db fail %s" % new_group_users)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
                 
        return None

    def remove_user_from_user_group(self, ug_dn, user_dns):
        
        ret = self.get_user_by_dn(user_dns)
        if not ret:
            return None
        
        local_users = ret
        user_names = {}
        for _, user in local_users.items():
            
            user_id = user["user_id"]
            user_name = user["user_name"]
            
            user_names[user_id] = user_name
        
        ret = self.get_user_group_by_dn(ug_dn)
        if not ret:
            return None
        
        user_group = ret[ug_dn]
        user_group_id = user_group["user_group_id"]    
        
        conditions = {}
        conditions["user_group_id"] = user_group_id
        conditions["user_id"] = user_names.keys()
        self.ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)

        return None
    
    def get_parent_dn(self, parent_dn):
        
        conditions = {}
        conditions["ou_dn"] = parent_dn
        ret = self.ctx.pgm.get_local_auth_ous(conditions)
        if not ret:
            return None
        
        return ret

    def format_local_auth_ous(self, auth_ou_set):
        
        if not auth_ou_set:
            return None

        auth_ous = []
        for auth_ou in auth_ou_set:

            ou_info = {}
            
            ou_info["dn"] = auth_ou["ou_dn"]

            ou_info["objectGUID"] = auth_ou["object_guid"]
            ou_info["description"] = auth_ou.get("description", "")
            auth_ous.append(ou_info)
        
        return auth_ous

    def describe_organization_units(self, parent_dn='', org_names=[], scope=0):
        
        conditions = {}
        
        if not parent_dn:
            parent_dn = self.base_dn
        
        parent_ou = self.get_parent_dn(parent_dn)
        if not parent_ou:
            parent_ou = None
        
        base_dn = self.ctx.pgm.user_unicode_to_string(parent_dn)
        if scope:
            conditions["base_dn"] = SearchType(base_dn)
        else:
            conditions["base_dn"] = base_dn
        
        if org_names:
            conditions["ou_name"] = org_names

        user_ous = self.ctx.pgm.get_local_auth_ous(conditions)
        if not user_ous:
            if not org_names:
                user_ous = parent_ou
            else:
                return None
        else:
            if parent_ou and not org_names:
                user_ous.update(parent_ou)
        
        if not user_ous:
            return None
        
        return self.format_local_auth_ous(user_ous.values())

    def create_organization_unit(self, parent_dn, attrs):

        base_dn = parent_dn
        if not base_dn:
            base_dn = self.base_dn

        user_ou_info = {}
        user_ou_id = get_uuid(UUID_TYPE_DESKTOP_OU, self.ctx.checker, long_format=True)
        user_ou_info["user_ou_id"] = user_ou_id
        user_ou_info["auth_service_id"] = self.auth_service_id
        
        ou_name = attrs.get("ou")
        if not ou_name:
            return None
    
        user_ou_info["ou_name"] = ou_name
        user_ou_info["description"] = attrs.get("description", "")
        user_ou_info["base_dn"] = parent_dn
        
        ou_dn = "ou=%s,%s" % (ou_name, base_dn)
        user_ou_info["ou_dn"] = self.ctx.pgm.user_unicode_to_string(ou_dn)
        user_ou_info["create_time"] = get_current_time()

        object_guid = self.create_local_object_guid("local-ou-")
        if not object_guid:
            object_guid = "local-guid-default"
        user_ou_info["object_guid"] = object_guid

        if not self.ctx.pg.batch_insert(dbconst.TB_DESKTOP_USER_OU, {user_ou_id: user_ou_info}):
            logger.error("insert newly created desktop user for [%s] to db failed" % (user_ou_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        
        return user_ou_info["ou_dn"]

    def delete_desktop_ou_users(self, ou_dn, user_names=None, scope=0):
        
        conditions = {}
        if scope:
            conditions["ou_dn"] = SearchType(ou_dn)
        else:
            conditions["ou_dn"] = ou_dn
        
        if user_names:
            conditions["user_name"] = user_names
        
        ret = self.ctx.pgm.get_local_auth_users(conditions, index_dn=True)
        if not ret:
            return None
        
        user_dns = ret.keys()
        
        ret = self.delete_users(user_dns)
        if isinstance(ret, Error):
            return ret

        return user_dns
    
    def delete_desktop_ou_user_groups(self, ou_dn, user_group_names=None, scope=0):

        conditions = {}
        if scope:
            conditions["base_dn"] = SearchType(ou_dn)
        else:
            conditions["base_dn"] = ou_dn

        if user_group_names:
            conditions["user_group_name"] = user_group_names

        ret = self.ctx.pgm.get_local_auth_user_group(conditions)
        if not ret:
            return None
        
        user_group_names = ret.keys()
        ret = self.delete_user_groups(ou_dn, user_group_names)
        if isinstance(ret, Error):
            return ret

        return ret

    def modify_organization_unit(self, dn, attrs={}):


        ret = self.get_user_ou_by_dn(dn)
        if not ret:
            return None
        
        user_ou = ret
        
        user_ou_id = user_ou["user_ou_id"]

        dn_list = dn.split(',')[1:]
        org_name = dn.split(',')[0][3:]
        parent_dn = ",".join(dn_list)
        
        ous = self.describe_organization_units(parent_dn, org_name, 1)
        if not ous:
            return None
        
        modify_ou = ous[0]
        
        new_attrs = {}
        for key, value in modify_ou.items():
            if key in attrs and attrs[key] != value:
                new_attrs[key] = attrs[key]
        
        if not new_attrs:
            return None
        
        if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER_OU, {user_ou_id: new_attrs}):
            logger.error("modify desktop group update fail %s" % new_attrs)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        return dn

    def delete_organization_units(self, dns=[]):
        
        if not dns:
            return None

        conditions = {}
        
        delete_ou_dns = []
        for ou_dn in dns:
            _ou_dn = self.ctx.pgm.user_unicode_to_string(ou_dn)
            conditions["ou_dn"] = SearchType(_ou_dn)
            user_ous = self.ctx.pgm.get_local_auth_ous(conditions, index_dn=True)
            if not user_ous:
                continue
            
            for user_ou_dn, _ in user_ous.items():
                if user_ou_dn in delete_ou_dns:
                    continue
                delete_ou_dns.append(user_ou_dn)
        
        for delete_ou_dn in delete_ou_dns:
            
            ret = self.delete_desktop_ou_users(delete_ou_dn)
            if isinstance(ret, Error):
                return ret
            
            ret = self.delete_desktop_ou_user_groups(ou_dn)
            if isinstance(ret, Error):
                return ret

            conditions["ou_dn"] = delete_ou_dn
            self.ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_OU, conditions)

        return delete_ou_dns
    
    def change_user_organizaion(self, user_dn, new_org_dn):
        
        conditions = {}
        conditions["user_dn"] = user_dn
        conditions["auth_service_id"] = self.auth_service_id
        
        ret = self.ctx.pgm.get_local_auth_users(conditions, index_dn=True)
        if not ret:
            logger.error("no found user %s" % (user_dn))
            return Error(ErrorCodes.USER_NOT_FOUND,
                         ErrorMsg.ERR_CODE_MSG_DESCRIBE_USER_FAILED)
        
        user = ret[user_dn]
        user_id = user["user_id"]
        
        new_user_dn = "cn=%s,%s" % (user["real_name"], new_org_dn)
        
        update_info = {"user_dn": new_user_dn, "ou_dn": new_org_dn}
        
        if not self.ctx.pg.batch_update(dbconst.TB_DESKTOP_USER, {user_id: update_info}):
            logger.error("modify desktop group update fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        return new_user_dn
