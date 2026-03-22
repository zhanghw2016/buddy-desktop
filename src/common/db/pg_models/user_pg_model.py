import db.constants as dbconst
import constants as const
from utils.id_tool import(
    UUID_TYPE_DESKTOP_USER,
    UUID_TYPE_DESKTOP_USER_GROUP
)

class UserPGModel():
    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    
    def get_table_ignore_case(self, table, condition, match_word,zone=None):

        zone_condition=''
        if zone:
            zone_condition=" and  zone='%s'"%zone
        if isinstance(match_word, list):
            
            upper_word = []
            for word in match_word:
                upper_word.append(word.upper())

            sql = "select * from %s where upper(%s) in %%s %s" % (table, condition,zone_condition)
            
            search_set = self.pg.execute_sql(sql, [tuple(upper_word)])
        else:
            sql = "select * from %s where upper(%s)=upper('%s') %s" % (table, condition, match_word,zone_condition)
            search_set = self.pg.execute_sql(sql)

        return search_set

    def user_unicode_to_string(self, user, unicode_keys=[]):

        if not user:
            return user
        
        check_keys = ["user_dn", "ou_dn", "real_name", "user_group_name", "base_dn", "user_group_dn", "ou_name", "user_name"]
        if unicode_keys:
            if isinstance(unicode_keys, list):
                check_keys.extend(unicode_keys)
            else:
                check_keys.append(unicode_keys)
        
        if isinstance(user, dict):
            for key, value in user.items():
                
                if key not in check_keys:
                    continue

                if isinstance(value, unicode):
                    user[key] = str(value).decode("string_escape").encode("utf-8")
        
        elif isinstance(user, list):
            new_values = []
            for value in user:
                if isinstance(value, unicode):
                    value = str(value).decode("string_escape").encode("utf-8")
                    new_values.append(value)
                    continue
                new_values.append(value)

            return new_values
        
        elif isinstance(user, unicode):
            return str(user).decode("string_escape").encode("utf-8")

        return user

    def get_user_scope(self, zone_id, user_id, resource_type=dbconst.SUPPORT_SCOPE_RESOURCE_TYPE, action_type=None):
        conditions = dict(zone_id=zone_id, user_id=user_id, resource_type=resource_type)
        
        if action_type is not None:
            conditions["action_type"] = action_type

        resources = self.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, conditions)
        if resources is None or len(resources) == 0:
            return None
        
        user_scope = {}
        for res in resources:
            resource_id = res["resource_id"]
            action_type = res["action_type"]
            resource_type = res["resource_type"]
            scope_key = "%s-%s-%s" % (resource_id, resource_type, action_type)
            if action_type == dbconst.RES_SCOPE_CREATE:
                scope_key = "%s-%s" % (resource_type, action_type)
            else:
                if not resource_id:
                    continue
       
            user_scope[scope_key] = res

        return user_scope

    def get_user_scope_resource_ids(self, zone_id, user_id, resource_type, action_type=None):
        conditions = dict(zone_id=zone_id, user_id=user_id, resource_type=resource_type)

        if action_type is not None:
            action_types = []
            for i in range(action_type, dbconst.RES_SCOPE_DELETE+1):
                action_types.append(i)
            conditions["action_type"] = action_types

        resources = self.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, conditions)
        if resources is None or len(resources) == 0:
            return None
        
        resource_ids = []
        for res in resources:
            resource_id = res.get("resource_id")
            if resource_id:
                resource_ids.append(resource_id)

        return resource_ids
    
    def get_scope_action(self, action_api=None):
        conditions = {}
        
        if action_api:
            conditions["action_api"] = action_api

        action_set = self.pg.base_get(dbconst.TB_ZONE_USER_SCOPE_ACTION, conditions)
        if action_set is None or len(action_set) == 0:
            return None
        
        actions = {}
        for action in action_set:
            action_id = action["action_id"]
            action_api = action["action_api"]
            if action_id not in actions:
                actions[action_id] = []
            actions[action_id].append(action_api)

        return actions

    def get_resource_scope(self, resource_ids):
        if not resource_ids:
            return None

        condition = {'resource_id': resource_ids}
        ret = self.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, condition)
        if not ret:
            return None

        return ret

    def get_global_admin_user_name(self, user_ids=None):

        conditions = {}
        if user_ids:
            conditions["user_id"] = user_ids

        conditions["role"] = const.USER_ROLE_GLOBAL_ADMIN
        
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None

        user_names = {}
        for user in user_set:
            user_id = user["user_id"]
            user_name = user["user_name"]
            user_names[user_id] = user_name

        return user_names

    def get_global_admin_user(self, user_ids=None, user_names=None, index_name=False):

        conditions = {}
        if user_ids:
            conditions["user_id"] = user_ids
        
        if user_names:
            if isinstance(user_names, int):
                user_names = str(user_names)

            conditions["user_name"] = user_names

        conditions["role"] = const.USER_ROLE_GLOBAL_ADMIN

        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None

        users = {}
        for user in user_set:
            user_id = user["user_id"]
            user_name = user["user_name"]
            if index_name:
                users[user_name] = user
            else:
                users[user_id] = user

        return users

    def get_desktop_user_detail(self, user_id, columns=None):
        
        if not user_id:
            return None
        
        conditions = dict(user_id = user_id)
        user = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions, columns=columns)
        if user is None or len(user) == 0:
            return None
        
        self.user_unicode_to_string(user)
        
        return user[0]

    def get_desktop_users(self, user_ids, status=None, user_role=None, columns=None):
        
        if not user_ids:
            return None
        
        conditions = dict(user_id = user_ids)
        if status:
            conditions["status"] = status
        
        if user_role:
            conditions["role"] = user_role
        
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions, columns=columns)
        if user_set is None or len(user_set) == 0:
            return None

        users = {}
        for user in user_set:
            self.user_unicode_to_string(user)
            user_id = user["user_id"]
            users[user_id] = user

        return users

    def get_user_by_user_dn(self, auth_service_id, user_dns):
        
        if not user_dns:
            return None
        
        user_dns = self.user_unicode_to_string(user_dns)
        
        conditions = dict(auth_service_id = auth_service_id, user_dn= user_dns)
        
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None

        users = {}
        for user in user_set:
            self.user_unicode_to_string(user)
            user_dn = user["user_dn"]
            users[user_dn] = user

        return users

    def get_auth_desktop_users(self, auth_service_id, user_names, index_guid=False):
        
        conditions = dict(auth_service_id = auth_service_id)
        
        user_names = self.user_unicode_to_string(user_names)
        
        conditions["user_name"] = user_names
       
        user_set = self.pg.get_all(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None

        users = {}
        for user in user_set:
            user = self.user_unicode_to_string(user)
            user_name = user["user_name"]
            guid = user["object_guid"]
            if index_guid:
                users[guid] = user
            else:
                users[user_name] = user

        return users

    def get_user_id_by_user_name(self, user_name, auth_service_id=None, zone_id=None):
        
        if not user_name:
            return None
        
        user_name = self.user_unicode_to_string(user_name)
        if not auth_service_id:
        
            auth_zone = self.pgm.get_auth_zone(zone_id)
            if not auth_zone:
                return None
            
            auth_service_id = auth_zone["auth_service_id"]
        
        conditions = dict(user_name=user_name, auth_service_id=auth_service_id)

        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            conditions = dict(real_name=user_name)
            user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
            if user_set is None or len(user_set) == 0:
                return None
        
        self.user_unicode_to_string(user_set)
        
        user = user_set[0]
        return user["user_id"]

    def get_user_by_user_ou_dn(self, ou_dn):
        
        if not ou_dn:
            return None
        
        ou_dn = self.user_unicode_to_string(ou_dn)
        
        conditions = dict(ou_dn=ou_dn)

        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None
        
        users = {}
        self.user_unicode_to_string(user_set)
        for user in user_set:
            user_id = user["user_id"]
            users[user_id] = user
        
        return users
            
    def get_user_group_by_user_group_ou_dn(self, ou_dn):
        
        if not ou_dn:
            return None
        
        ou_dn = self.user_unicode_to_string(ou_dn)
        
        conditions = dict(base_dn=ou_dn)

        user_group_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if user_group_set is None or len(user_group_set) == 0:
            return None
        
        user_groups = {}
        self.user_unicode_to_string(user_group_set)
        for user_group in user_group_set:
            user_group_id = user_group["user_group_id"]
            user_groups[user_group_id] = user_group
        
        return user_groups

    def get_user_dn_by_user_name(self, user_name):
        
        if not user_name:
            return None
        user_name = self.user_unicode_to_string(user_name)
        conditions = dict(user_name=user_name)
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            conditions = dict(real_name=user_name)
            user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
            if user_set is None or len(user_set) == 0:
                return None
        
        user = user_set[0]
        user_dn = user["user_dn"]
        
        return self.user_unicode_to_string(user_dn)

    def get_user_by_user_names(self, user_names, auth_service_id = None, zone_id=None):
        
        if not user_names:
            return None
        
        self.user_unicode_to_string(user_names)
        
        if not auth_service_id:
        
            auth_zone = self.pgm.get_auth_zone(zone_id)
            if not auth_zone:
                return None
            
            auth_service_id = auth_zone["auth_service_id"]

        conditions = dict(user_name=user_names)
        conditions["auth_service_id"] = auth_service_id
        
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return {}

        users = {}
        for user in user_set:
            user = self.user_unicode_to_string(user)
            user_id = user["user_id"]
            user_name = user["user_name"]
            users[user_name] = user_id

        return users

    def get_user_group_by_user_group_names(self, user_group_names, auth_service_id = None, zone_id=None):
        
        if not user_group_names:
            return None
        
        user_group_names = self.user_unicode_to_string(user_group_names)
        
        if not auth_service_id:
        
            auth_zone = self.pgm.get_auth_zone(zone_id)
            if not auth_zone:
                return None
            
            auth_service_id = auth_zone["auth_service_id"]

        conditions = dict(user_group_name=user_group_names)
        conditions["auth_service_id"] = auth_service_id
        
        user_group_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if user_group_set is None or len(user_group_set) == 0:
            return {}

        user_groups = {}
        for user_group in user_group_set:
            user_group = self.user_unicode_to_string(user_group)
            user_group_id = user_group["user_group_id"]
            user_group_name = user_group["user_group_name"]
            user_groups[user_group_name] = user_group_id

        return user_groups

    def search_user_by_name(self, user_name, auth_service_ids=None):
        
        user_name = self.user_unicode_to_string(user_name)
        
        if auth_service_ids and not isinstance(auth_service_ids, list):
            auth_service_ids = [auth_service_ids]

        if user_name.startswith(UUID_TYPE_DESKTOP_USER):
            sql = "select * from desktop_user where upper(user_id)=upper('%s')" % user_name
            user_set = self.pg.execute_sql(sql)
        elif auth_service_ids:
            sql = "select * from desktop_user where upper(user_name)=upper('%s') and auth_service_id='%s'" % (user_name, auth_service_ids[0])
            user_set = self.pg.execute_sql(sql, [tuple(auth_service_ids)])
        else:
            sql = "select * from desktop_user where upper(user_name)=upper('%s')" % user_name
            user_set = self.pg.execute_sql(sql)
            
        if user_set is None or len(user_set) == 0:
            return None

        users = {}
        for user in user_set:
            self.user_unicode_to_string(user)
            user_id = user["user_id"]
            user_name = user["user_name"]
            users[user_id] = user

        return users

    def get_user_names(self, user_ids, excluded_user = []):
        
        if not user_ids:
            return None
        
        conditions = dict(user_id=user_ids)
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None
        
        user_names = {}
        for user in user_set:
            
            self.user_unicode_to_string(user)
            
            user_name = user["user_name"]
            user_id = user["user_id"]
            if user_id in excluded_user:
                continue
            user_names[user_id] = user_name
        
        return user_names

    def get_user_group_names(self, user_group_ids):
        
        if not user_group_ids:
            return None
        
        conditions = dict(user_group_id=user_group_ids)
        user_group_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if user_group_set is None or len(user_group_set) == 0:
            return None
        
        user_group_names = {}
        for user_group in user_group_set:
            
            self.user_unicode_to_string(user_group)
            
            user_group_name = user_group["user_group_name"]
            user_group_id = user_group["user_group_id"]
            user_group_names[user_group_id] = user_group_name
        
        return user_group_names

    def get_user_by_name(self, user_ids):
        
        if not user_ids:
            return None
        
        conditions = dict(user_id=user_ids)
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None
        
        user_names = {}
        for user in user_set:
            user = self.user_unicode_to_string(user)
            user_name = user["user_name"]
            user_names[user_name] = user
        
        return user_names

    def get_user_name(self, user_id):

        conditions = dict(user_id=user_id)
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None
        
        self.user_unicode_to_string(user_set)
        
        return user_set[0]["user_name"]

    def get_users_by_name(self, user_names, zone_id):
        
        user_names = self.user_unicode_to_string(user_names)
        
        conditions = dict(user_name=user_names, zone_id=zone_id)
        user_set = self.pg.base_get(dbconst.TB_ZONE_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None
        
        user_names = {}
        for user in user_set:
            user = self.user_unicode_to_string(user)
            user_name = user["user_name"]
            user_names[user_name] = user
        
        return user_names
    
    def get_auth_service_users(self, auth_service_id, user_names=None):
        
        conditions = dict(auth_service_id=auth_service_id)
        if user_names:
            user_names = self.user_unicode_to_string(user_names)
            conditions["user_name"] = user_names
        
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None
        
        desktop_users = {}
        for user in user_set:
            user = self.user_unicode_to_string(user)
            user_name = user["user_name"]
            desktop_users[user_name] = user
        
        return desktop_users

    def get_desktop_user_password(self, user_id):

        conditions = dict(user_id = user_id)

        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None
        
        self.user_unicode_to_string(user_set)
        
        return user_set[0]["password"]

    def get_desktop_user_group(self, user_group_id):
        
        conditions = dict(user_group_id=user_group_id)
        
        user_group_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if user_group_set is None or len(user_group_set) == 0:
            return None

        for user_group in user_group_set:
            self.user_unicode_to_string(user_group)

        return user_group_set[0]

    def get_desktop_user_groups(self, auth_service_id=None, user_group_ids=None, user_group_dns=None, index_dn=False, index_guid=False):

        conditions = {}
        
        if auth_service_id:
            conditions["auth_service_id"] = auth_service_id

        if user_group_ids:
            conditions["user_group_id"] = user_group_ids
        
        if user_group_dns:
            self.user_unicode_to_string(user_group_dns)
            conditions["user_group_dn"] = user_group_dns

        user_group_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if user_group_set is None or len(user_group_set) == 0:
            return None
        
        desktop_user_groups = {}
        for user_group in user_group_set:
            user_group = self.user_unicode_to_string(user_group)
            user_group_id = user_group["user_group_id"]
            user_group_dn = user_group["user_group_dn"]
            object_guid = user_group["object_guid"]
            if index_dn:
                desktop_user_groups[user_group_dn] = user_group
            elif index_guid:
                desktop_user_groups[object_guid] = user_group
            else:
                desktop_user_groups[user_group_id] = user_group
        
        return desktop_user_groups

    def get_user_group_user(self, user_group_id):

        conditions = {}
        conditions["user_group_id"] = user_group_id

        user_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)
        if user_group_user_set is None or len(user_group_user_set) == 0:
            return None
        
        desktop_users = {}
        for user_group_user in user_group_user_set:
            self.user_unicode_to_string(user_group_user)
            user_id = user_group_user["user_id"]
            desktop_users[user_id] = user_group_user
        
        return desktop_users

    def get_user_group_users(self, user_group_ids):

        conditions = {}
        conditions["user_group_id"] = user_group_ids

        user_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)
        if user_group_user_set is None or len(user_group_user_set) == 0:
            return None
        
        desktop_users = []
        for user_group_user in user_group_user_set:
            self.user_unicode_to_string(user_group_user)
            user_id = user_group_user["user_id"]
            if user_id not in desktop_users:
                desktop_users.append(user_id)
        
        return desktop_users

    def get_user_group_user_name(self, user_group_id):

        conditions = {}
        conditions["user_group_id"] = user_group_id

        user_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)
        if user_group_user_set is None or len(user_group_user_set) == 0:
            return None
        
        user_ids = []
        for user_group_user in user_group_user_set:
            self.user_unicode_to_string(user_group_user)
            user_id = user_group_user["user_id"]
            user_ids.append(user_id)
        
        users = self.get_user_by_name(user_ids)
        
        return users
    
    def get_user_group_user_name_by_dn(self, user_group_dn):
        
        user_groups = self.get_desktop_user_group_by_dn(user_group_dn)
        if not user_groups:
            return None
        
        user_group = user_groups[user_group_dn]
        user_group_id = user_group["user_group_id"]
        
        user_names = self.get_user_group_user_name(user_group_id)
        
        return user_names
    
    def get_desktop_user_group_by_dn(self, user_group_dns, auth_service_id=None):
        
        user_group_dns = self.user_unicode_to_string(user_group_dns)
        
        conditions = dict(user_group_dn=user_group_dns)
        if auth_service_id:
            conditions["auth_service_id"] = auth_service_id
        
        user_group_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if user_group_set is None or len(user_group_set) == 0:
            return None
        
        desktop_user_groups = {}
        for user_group in user_group_set:
            user_group = self.user_unicode_to_string(user_group)
            user_group_dn = user_group["user_group_dn"]
            desktop_user_groups[user_group_dn] = user_group
        
        return desktop_user_groups

    def get_desktop_user_form_user_group(self, user_group_id):
        
        conditions = dict(user_group_id=user_group_id)
        
        user_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)
        if user_group_user_set is None or len(user_group_user_set) == 0:
            return None

        group_users = []
        for group_user in user_group_user_set:
            user_id = group_user["user_id"]
            group_users.append(user_id)
        
        return group_users

    def get_desktop_user_form_user_ou(self, user_ou_id):
        
        conditions = dict(user_group_id=user_ou_id)
        
        user_ou_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conditions)
        if user_ou_set is None or len(user_ou_set) == 0:
            return None
        
        
        user_ou = user_ou_set[0]
        self.user_unicode_to_string(user_ou)
        
        conditions = dict(auth_service_id=user_ou["auth_service_id"], ou_dn=user_ou["ou_dn"])

        desktop_user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if desktop_user_set is None or len(desktop_user_set) == 0:
            return None

        ou_users = []
        for desktop_user in desktop_user_set:
            desktop_user = self.user_unicode_to_string(desktop_user)
            user_id = desktop_user["user_id"]
            ou_users.append(user_id)
        
        return ou_users

    def get_user_role_by_user_id(self, user_id, zone_id):

        cons = {
            'user_id': user_id,
            'zone_id': zone_id
            }
    
        if user_id == const.GLOBAL_ADMIN_USER_ID:
            return const.USER_ROLE_GLOBAL_ADMIN

        result = self.pg.base_get(dbconst.TB_ZONE_USER, cons)
        if result is None:
            return None

        role = None
        for k,v in result[0].items():
            if k == 'role':
                role = v
                break

        return role

    def get_user_role_by_user_name(self, user_name, zone_id):

        cons = {
            'user_name': user_name,
            'zone_id': zone_id
            }
    
        if user_name == const.GLOBAL_ADMIN_USER_NAME:
            return const.USER_ROLE_GLOBAL_ADMIN

        result = self.pg.base_get(dbconst.TB_ZONE_USER, cons)
        if result is None:
            return None

        role = None
        for k,v in result[0].items():
            if k == 'role':
                role = v
                break

        return role

    def get_user_status(self, user_id):

        if not user_id:
            return None

        cons = {
            'user_id': user_id
            }

        result = self.pg.base_get(dbconst.TB_ZONE_USER, cons)
        if result is None:
            return None

        status = None
        for k,v in result[0].items():
            if k == 'status':
                status = v
                break

        return status
     
    def get_user_ous(self, user_ou_ids=None, auth_service_ids=None, user_group_names=None,
                     object_guids=None, user_group_dns=None, base_dns=None, index_id=False, index_guid=False):

        condition = {}
        if user_ou_ids:
            condition.update({"user_ou_id": user_ou_ids})
        if auth_service_ids:
            condition.update({"auth_service_id": auth_service_ids})
        if user_group_names:
            user_group_names = self.user_unicode_to_string(user_group_names)
            condition.update({"user_group_name": user_group_names})
        if object_guids:
            condition.update({"object_guid": object_guids})
        if user_group_dns:
            user_group_dns = self.user_unicode_to_string(user_group_dns)
            condition.update({"user_group_dn": user_group_dns})
        if base_dns:
            base_dns = self.user_unicode_to_string(base_dns)
            condition.update({"base_dn": base_dns})
        
        if not condition:
            return None
        
        user_ous = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, condition)
        if user_ous is None:
            return None
        
        dict_user_ous = {}
        
        dict_object_ous = {}
        for user_ou in user_ous:
            user_ou = self.user_unicode_to_string(user_ou)
            user_ou_id = user_ou["user_ou_id"]
            object_guid = user_ou["object_guid"]
            if index_id:
                dict_user_ous[user_ou_id] = user_ou
            
            if index_guid:
                dict_object_ous[object_guid] = user_ou
                
        if index_id:
            return dict_user_ous
        
        if index_guid:
            return dict_object_ous
        
        return user_ous

    def get_desktop_user_ou_id_by_ou_dn(self, auth_service_id, ou_dn):
        if not ou_dn or not auth_service_id:
            return None

        condition = {
            "auth_service_id": auth_service_id,
            "ou_dn": ou_dn
            }
        user_ous = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, condition)
        if user_ous is None or len(user_ous)==0:
            return None

        return user_ous[0]["user_ou_id"]

    def get_user_ou_name(self, user_ou_id):

        if not user_ou_id:
            return None

        user_ou = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, 
                                      {'user_ou_id':user_ou_id})
        if not user_ou or len(user_ou)==0:
            return None
        ou_name = user_ou[0]['ou_name']
        
        return self.user_unicode_to_string(ou_name)

    def get_user_ou_dn(self, user_ou_id):

        if not user_ou_id:
            return None

        user_ou = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, 
                                      {'user_ou_id':user_ou_id})
        if not user_ou or len(user_ou)==0:
            return None
        
        ou_dn = user_ou[0]['ou_dn']
        
        return self.user_unicode_to_string(ou_dn)

    def get_user_ou_path(self, user_ou_id):

        if not user_ou_id:
            return None

        user_ou = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, 
                                      {'user_ou_id':user_ou_id})
        if not user_ou or len(user_ou)==0:
            return None
        
        auth_ou = user_ou[0]
        self.user_unicode_to_string(auth_ou)
    
        ou_dn = auth_ou['ou_dn']
        ou_dn = ou_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        ou_dn = ou_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")
        
        auth_service_id = auth_ou['auth_service_id']
        auth_service = self.pg.base_get(dbconst.TB_AUTH_SERVICE, 
                                      {'auth_service_id':auth_service_id})
        if not auth_service or len(auth_service)==0:
            return None
        
        auth_service = auth_service[0]
        self.user_unicode_to_string(auth_service)
        base_dn = auth_service['base_dn']
        base_dn = base_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        base_dn = base_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")

        root_path_index = ou_dn.index(base_dn)
        path_str = ou_dn[:root_path_index]
        path_list = path_str.split("ou=")

        ou_path = "/"
        length = len(path_list)
        for i in range(length-1, -1, -1):
            ou_path = ou_path + path_list[i]
            if i>0:
                ou_path = ou_path + "/"

        return ou_path

    def get_user_zones(self, user_id):
        cons = {'user_id': user_id}
    
        if user_id == const.GLOBAL_ADMIN_USER_ID:
            return const.USER_ROLE_GLOBAL_ADMIN

        result = self.pg.base_get(dbconst.TB_ZONE_USER, cons)
        if result is None:
            return None

        zones = []
        for k,v in result[0].items():
            if k == 'zone':
                zones.append(v)

        return zones

    def get_user_ou_id(self, auth_service_id, user_id):

        if not user_id or not auth_service_id:
            return None

        user = self.pg.base_get(dbconst.TB_DESKTOP_USER, 
                                {'user_id': user_id})
        if not user or len(user)==0:
            return None
        
        auth_user = user[0]
        self.user_unicode_to_string(auth_user)

        ou_dn = auth_user['ou_dn']
        ou_dn = ou_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        ou_dn = ou_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")

        conds = {
            'ou_dn': ou_dn,
            'auth_service_id': auth_service_id
            }
        user_ou = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conds)
        if not user_ou or len(user_ou)==0:
            return None
        
        auth_ou = user_ou[0]
        
        user_ou_id =auth_ou['user_ou_id']
        return user_ou_id

    def get_ou_parent_ids(self, user_ou_id):

        if not user_ou_id:
            return None

        ou = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, 
                                {'user_ou_id': user_ou_id})
        if not ou or len(ou)==0:
            return None
        
        auth_ou = ou[0]
        self.user_unicode_to_string(auth_ou)
        ou_dn = auth_ou['ou_dn']
        auth_service_id = auth_ou['auth_service_id']
        parent_ou_ids = []

        while ou_dn:
            conds = {
                'ou_dn': ou_dn,
                'auth_service_id': auth_service_id
                }
            user_ou = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conds)
            if not user_ou or len(user_ou)==0:
                break
            
            _ou = user_ou[0]
            self.user_unicode_to_string(_ou)
            ou_id = _ou['user_ou_id']
            parent_ou_ids.append(ou_id)
            
            if ou_dn == _ou['base_dn']:
                break

            ou_dn = _ou['base_dn']
            
        return parent_ou_ids
    
    def get_user_group(self, user_id):

        conditions = dict(user_id=user_id)
        
        user_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)
        if not user_group_user_set:
            return None

        user_groups = []
        for group_user in user_group_user_set:
            user_group_id = group_user["user_group_id"]
            user_groups.append(user_group_id)
        
        return user_groups

    def get_user_group_detail(self, user_id):

        conditions = dict(user_id=user_id)
        
        user_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)
        if not user_group_user_set:
            return None

        user_groups = {}
        for group_user in user_group_user_set:
            user_group_id = group_user["user_group_id"]
            user_groups[user_group_id] = group_user
        
        return user_groups

    def get_user_group_info(self, user_group_id):

        conditions = dict(user_group_id=user_group_id)
        
        user_group_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if not user_group_set:
            return None

        user_groups = {}
        for group_user in user_group_set:
            info = {}
            user_group_id = group_user["user_group_id"]
            user_group_name = group_user["user_group_name"]
            user_group_dn = group_user["user_group_dn"]
            
            info = {
                "user_group_id": user_group_id,
                "user_group_name": user_group_name,
                "user_group_dn": user_group_dn
                }
            
            user_groups[user_group_id] = info
        
        return user_groups

    def get_user_and_user_group_names(self, user_ids):

        _user_ids = []
        _user_group_ids = []
        for user_id in user_ids:
            if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                _user_group_ids.append(user_id)
            elif user_id.startswith(UUID_TYPE_DESKTOP_USER):
                _user_ids.append(user_id)
        
        user_names = {}
        
        if _user_ids:
            ret = self.pgm.get_user_names(_user_ids)
            if ret:
                user_names.update(ret)
        
        if _user_group_ids:
            ret = self.pgm.get_user_group_names(_user_group_ids)
            if ret:
                user_names.update(ret)
        
        return user_names

    def get_user_and_user_group(self, user_ids, user_columns=[], user_group_conlumn=[]):
        
        if not isinstance(user_ids, list):
            user_ids = [user_ids]
        
        _user_ids = []
        _user_group_ids = []
        for user_id in user_ids:
            if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                _user_group_ids.append(user_id)
            elif user_id.startswith(UUID_TYPE_DESKTOP_USER):
                _user_ids.append(user_id)
        
        desktop_users = {}
        
        if _user_ids:
            
            conditions = {"user_id": _user_ids}
            ret = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions, columns=user_columns)
            if ret:
                for user in ret:
                    self.user_unicode_to_string(user)
                    user_id = user["user_id"]
                    desktop_users[user_id] = user
        
        if _user_group_ids:
            conditions = {"user_group_id": _user_group_ids}
            ret = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions, columns=user_group_conlumn)
            if ret:
                for user_group in ret:
                    self.user_unicode_to_string(user_group)
                    user_group_id = user_group["user_group_id"]
                    desktop_users[user_group_id] = user_group
        
        return desktop_users
    
    def get_resource_scope_by_user(self, user_id):

        conditions = dict(user_id=user_id)
        
        resource_set = self.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, conditions)
        if not resource_set:
            return None

        return resource_set
        
    def get_approve_by_user(self, user_id):

        conditions = dict(user_id=user_id)
        
        approve_user_set = self.pg.base_get(dbconst.TB_APPROVE_GROUP_USER, conditions)
        if not approve_user_set:
            return None
        
        user_ids = []
        for approve_user in approve_user_set:
            user_id = approve_user["user_id"]
            user_ids.append(user_id)
        
        return user_ids

    def get_apply_by_user(self, user_id):

        conditions = dict(user_id=user_id)
        
        apply_user_set = self.pg.base_get(dbconst.TB_APPLY_GROUP_USER, conditions)
        if not apply_user_set:
            return None
        
        user_ids = []
        for apply_user in apply_user_set:
            user_id = apply_user["user_id"]
            user_ids.append(user_id)
        
        return user_ids

    def check_reset_password(self, user_id=None, user_name=None):

        if not (user_id or user_name):
            return False

        conds = {}
        if user_id:
            conds["user_id"] = user_id
        if user_name:
            conds["user_name"] = user_name

        desktop_user = self.pg.base_get(dbconst.TB_DESKTOP_USER, conds)
        if not desktop_user:
            return False

        reset_password = desktop_user[0].get("reset_password", 0)
        if reset_password == 0:
            return False

        return True

    def get_password_prompt_answer(self, user_id):

        if not user_id:
            return 0

        conds = {"user_id": user_id}
        answers = self.pg.base_get(dbconst.TB_PROMPT_ANSWER, conds)
        if not answers:
            return 0

        return len(answers)


