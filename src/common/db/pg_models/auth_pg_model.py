import db.constants as dbconst
from db.data_types import SearchType, RegExpType
import constants as const

class AuthPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_auth_services(self, auth_service_ids=None, host=None, domain=None):
        
        conditions = {}
        if auth_service_ids:
            conditions["auth_service_id"] = auth_service_ids
        
        if host:
            conditions["host"] = host
        if domain:
            conditions["domain"] = domain

        auth_service_set = self.pg.base_get(dbconst.TB_AUTH_SERVICE, conditions)
        if auth_service_set is None or len(auth_service_set) == 0:
            return None

        auth_services = {}
        for auth_service in auth_service_set:
            self.pgm.user_unicode_to_string(auth_service)
            auth_service_id = auth_service["auth_service_id"]
            auth_services[auth_service_id] = auth_service
            
        return auth_services

    def get_auth_service_by_domain(self, domain):

        conditions = {}
        conditions["domain"] = RegExpType(domain, False)
        auth_service_set = self.pg.get_by_filter(dbconst.TB_AUTH_SERVICE, conditions, is_list=True)
        if auth_service_set is None or len(auth_service_set) == 0:
            return None

        auth_services = {}
        for auth_service in auth_service_set:
            
            self.pgm.user_unicode_to_string(auth_service)
            
            auth_service_id = auth_service["auth_service_id"]
            auth_services[auth_service_id] = auth_service

        return auth_services

    def get_auth_service(self, auth_service_id):
        
        conditions = {}
        conditions["auth_service_id"] = auth_service_id

        auth_service_set = self.pg.base_get(dbconst.TB_AUTH_SERVICE, conditions)
        if auth_service_set is None or len(auth_service_set) == 0:
            return None
        
        auth_service = auth_service_set[0]
        self.pgm.user_unicode_to_string(auth_service)
        
        return auth_service

    def get_auth_service_by_username(self, user_name):
        
        conditions = {}
        conditions["user_name"] = user_name

        desktop_user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if not desktop_user_set:
            return None

        auth_service_ids = []
        for desktop_user in desktop_user_set:
            auth_service_ids.append(desktop_user["auth_service_id"])

        return auth_service_ids
    
    def get_desktop_auth_users(self, auth_service_id, user_names=None):

        conditions = {}
        conditions["auth_service_id"] = auth_service_id
        if user_names:
            user_names = self.pgm.user_unicode_to_string(user_names)
            conditions["user_name"] = user_names

        auth_user_set = self.pg.get_all(dbconst.TB_DESKTOP_USER, conditions)
        if auth_user_set is None or len(auth_user_set) == 0:
            return None

        auth_users = {}
        for auth_user in auth_user_set:
            self.pgm.user_unicode_to_string(auth_user)
            user_name = auth_user["user_name"]
            auth_users[user_name] = auth_user

        return auth_users
    
    def get_zone_by_domain(self, domain):
        
        if not domain:
            return None
        
        ret = self.get_auth_service_by_domain(domain=domain)
        if not ret:
            return None
        
        auth_service_ids = ret.keys()
        
        conditions = {}
        conditions["auth_service_id"] = auth_service_ids

        zone_auth_set = self.pg.base_get(dbconst.TB_ZONE_AUTH, conditions)
        if zone_auth_set is None or len(zone_auth_set) == 0:
            return None
        
        zone_auths = {}
        for zone_auth in zone_auth_set:
            
            self.pgm.user_unicode_to_string(zone_auth)
            zone_id = zone_auth["zone_id"]
            auth_service_id = zone_auth["auth_service_id"]
            zone_auths[zone_id] = auth_service_id

        return zone_auths
    
    def get_desktop_ous(self, auth_service_id, ou_dns=None):
        
        conditions = {}
        conditions["auth_service_id"] = auth_service_id
        if ou_dns:
            ou_dns = self.pgm.user_unicode_to_string(ou_dns)
            conditions["ou_dn"] = RegExpType(ou_dns, False)

        auth_ou_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conditions)
        if auth_ou_set is None or len(auth_ou_set) == 0:
            return None

        auth_ous = {}
        for auth_ou in auth_ou_set:
            self.pgm.user_unicode_to_string(auth_ou)
            ou_dn = auth_ou["ou_dn"]
            auth_ous[ou_dn] = auth_ou

        return auth_ous

    def get_desktop_auth_ous(self, ou_dns):
        
        conditions = {}
        ou_dns = self.pgm.user_unicode_to_string(ou_dns)
        conditions["ou_dn"] = ou_dns

        auth_ou_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conditions)
        if auth_ou_set is None or len(auth_ou_set) == 0:
            return None

        auth_ous = {}
        for auth_ou in auth_ou_set:
            self.pgm.user_unicode_to_string(auth_ou)
            ou_dn = auth_ou["ou_dn"]
            auth_ous[ou_dn] = auth_ou

        return auth_ous

    def search_user_ous(self, base_dn=None, auth_service_id=None, ou_names=None, index_guid=False, exclude_ous=[], object_guid=None):
        
        conditions = {}
        if auth_service_id:
            conditions["auth_service_id"] = auth_service_id
        
        if base_dn:
            base_dn = self.pgm.user_unicode_to_string(base_dn)
            conditions["ou_dn"] = SearchType(base_dn)

        if ou_names:
            ou_names = self.pgm.user_unicode_to_string(ou_names)
            conditions["ou_name"] = ou_names
        
        if object_guid:
            conditions["object_guid"] = object_guid
 
        desktop_ou_set = self.pg.get_all(dbconst.TB_DESKTOP_USER_OU, conditions)
        if desktop_ou_set is None or len(desktop_ou_set) == 0:
            return None

        desktop_ous = {}
        for desktop_ou in desktop_ou_set:
            self.pgm.user_unicode_to_string(desktop_ou)
            ou_dn = desktop_ou["ou_dn"]
            guid = desktop_ou["object_guid"]
            
            if ou_dn in exclude_ous:
                continue

            if index_guid:
                if not guid:
                    continue
                
                desktop_ous[guid] = desktop_ou
            else:
                desktop_ous[ou_dn] = desktop_ou

        return desktop_ous

    def search_user_groups(self, auth_service_id, base_dn=None, user_group_names=None, index_guid=False, index_id=False, object_guids=None):
        
        conditions = {}
        conditions["auth_service_id"] = auth_service_id
        
        if base_dn:
            base_dn = self.pgm.user_unicode_to_string(base_dn)
            conditions["user_group_dn"] = SearchType(base_dn)

        if user_group_names:
            user_group_names = self.pgm.user_unicode_to_string(user_group_names)
            conditions["user_group_name"] = user_group_names
        
        if object_guids:
            conditions["object_guid"] = object_guids
 
        desktop_user_group_set = self.pg.get_all(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if desktop_user_group_set is None or len(desktop_user_group_set) == 0:
            return None
               
        desktop_user_groups = {}
        for desktop_user_group in desktop_user_group_set:
            
            self.pgm.user_unicode_to_string(desktop_user_group)
            
            user_group_id = desktop_user_group["user_group_id"]
            user_group_dn = desktop_user_group["user_group_dn"]
            guid = desktop_user_group["object_guid"]
            if index_guid:
                desktop_user_groups[guid] = desktop_user_group
            elif index_id:
                desktop_user_groups[user_group_id] = desktop_user_group
            else:
                desktop_user_groups[user_group_dn] = desktop_user_group

        return desktop_user_groups

    def search_users(self, auth_service_id, base_dn=None, user_names=None, index_guid=False, index_id=False, user_ids=None, object_guids=None, ou_guid=None):
        
        conditions = {}
        conditions["auth_service_id"] = auth_service_id
        
        if base_dn:
            base_dn = self.pgm.user_unicode_to_string(base_dn)
            conditions["user_dn"] = SearchType(base_dn)

        if user_names:
            user_names = self.pgm.user_unicode_to_string(user_names)
            conditions["user_name"] = user_names
        
        if user_ids:
            conditions["user_id"] = user_ids
        
        if object_guids:
            conditions["object_guid"] = object_guids
        
        if ou_guid:
            conditions["ou_guid"] = ou_guid

        desktop_user_set = self.pg.get_all(dbconst.TB_DESKTOP_USER, conditions)
        if desktop_user_set is None or len(desktop_user_set) == 0:
            return None

        desktop_users = {}
        for desktop_user in desktop_user_set:
            self.pgm.user_unicode_to_string(desktop_user)
            user_id = desktop_user["user_id"]
            user_dn = desktop_user["user_dn"]
            guid = desktop_user["object_guid"]
            if index_guid:
                desktop_users[guid] = desktop_user
            elif index_id:
                desktop_users[user_id] = desktop_user
            else:
                desktop_users[user_dn.lower()] = desktop_user

        return desktop_users
    
    def get_ou_resource(self, auth_service_id, ou_dn):
        
        ou_resources = {}
        
        ou_dn = self.pgm.user_unicode_to_string(ou_dn)
        
        ret = self.search_users(auth_service_id, ou_dn)
        if ret:
            ou_resources.update(ret)
        
        ret = self.search_user_groups(auth_service_id, ou_dn)
        if ret:
            ou_resources.update(ret)
        
        ret = self.search_user_ous(ou_dn, auth_service_id, exclude_ous=[ou_dn])
        if ret:
            ou_resources.update(ret)

        for table, key_value in dbconst.UPDATE_AUTH_BASE_DN.items():

                for _, value in key_value.items():
                    conditions = {value: SearchType(ou_dn)}
                    ret = self.pg.get_all(table, conditions)
                    if ret:
                        ou_resources[table] = ret

        return ou_resources

    def get_desktop_user_ou_id(self, auth_service_id, ou_dn):

        if not ou_dn:
            return None
        
        ou_dn = self.pgm.user_unicode_to_string(ou_dn)
        conds = {
            "auth_service_id": auth_service_id,
            "ou_dn": ou_dn
            }
        columns = ["user_ou_id"]
        ret = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conds, columns)
        if ret==None or len(ret)==0:
            return None

        return ret[0]['user_ou_id']

    def get_desktop_user_ous(self, ou_dns, index_guid=False):

        ou_dns = self.pgm.user_unicode_to_string(ou_dns)
        conds = {
            "ou_dn": ou_dns
            }
        ou_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conds)
        if ou_set==None or len(ou_set)==0:
            return None
        
        desktop_ous = {}
        for ou in ou_set:
            self.pgm.user_unicode_to_string(ou)
            user_ou_id = ou["user_ou_id"]
            object_guid = ou["object_guid"]
            if index_guid:
                desktop_ous[object_guid] = ou
            else:
                desktop_ous[user_ou_id] = ou

        return desktop_ous

    def get_radius_service(self, radius_service_id=None, host=None):
        
        conditions = {}
        conditions["radius_service_id"] = radius_service_id
        if host:
            conditions["host"] = host

        radius_service_set = self.pg.base_get(dbconst.TB_RADIUS_SERVICE, conditions)
        if radius_service_set is None or len(radius_service_set) == 0:
            return None
            
        return radius_service_set[0]

    def get_radius_services(self, radius_service_ids=None):
        
        conditions = {}
        if radius_service_ids:
            conditions["radius_service_id"] = radius_service_ids

        radius_service_set = self.pg.base_get(dbconst.TB_RADIUS_SERVICE, conditions)
        if radius_service_set is None or len(radius_service_set) == 0:
            return None
        
        radius_services = {}
        for radius_service in radius_service_set:
            radius_service_id = radius_service["radius_service_id"]
            radius_services[radius_service_id] = radius_service
        
        return radius_services

    def get_radius_users(self, radius_service_id=None, user_ids=None):
        
        conditions = {}
        if radius_service_id:
            conditions["radius_service_id"] = radius_service_id
        if user_ids:
            conditions["user_id"] = user_ids

        radius_user_set = self.pg.base_get(dbconst.TB_RADIUS_USER, conditions)
        if radius_user_set is None or len(radius_user_set) == 0:
            return None

        radius_users = {}
        for radius_user in radius_user_set:
            user_id = radius_user["user_id"]
            radius_users[user_id] = radius_user
        
        return radius_users

    def get_radius_user(self, user_id, radius_service_id=None):

        conditions = {}
        conditions["user_id"] = user_id
        if radius_service_id:
            conditions["radius_service_id"] = radius_service_id

        radius_user_set = self.pg.base_get(dbconst.TB_RADIUS_USER, conditions)
        if radius_user_set is None or len(radius_user_set) == 0:
            return None

        return radius_user_set[0]
    
    def get_auth_radius(self, auth_service_id):

        conditions = {}
        conditions["auth_service_id"] = auth_service_id

        radius_user_set = self.pg.base_get(dbconst.TB_RADIUS_SERVICE, conditions)
        if radius_user_set is None or len(radius_user_set) == 0:
            return None

        return radius_user_set[0]
    
    def get_ou_guid(self, ou_dn):

        conditions = {}
        ou_dn = self.pgm.user_unicode_to_string(ou_dn)
        conditions["ou_dn"] = ou_dn

        ou_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conditions)
        if ou_set is None or len(ou_set) == 0:
            return None

        return ou_set[0]["object_guid"]

    def get_ou_guids(self, ou_dns):

        conditions = {}
        ou_dns = self.pgm.user_unicode_to_string(ou_dns)
        conditions["ou_dn"] = ou_dns

        ou_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conditions)
        if ou_set is None or len(ou_set) == 0:
            return None
        
        ou_guid = {}
        
        for ou in ou_set:
            guid = ou.get("object_guid")
            ou_dn = ou["ou_dn"]
            if not guid:
                continue
            
            ou_guid[ou_dn] = guid
        
        return ou_guid

    def get_auth_password_config(self, item_keys=[const.CUSTOM_ITEM_KEY_BADPWDCOUNT,
                                                  const.CUSTOM_ITEM_KEY_LOCK_PASSWORD_TIME,
                                                  const.CUSTOM_ITEM_KEY_PASSWORD_EXPIRE_PREIOD]):

        conditions = {"module_type": const.CUSTOM_MODULE_TYPE_PASSWORD}
        if item_keys:
            conditions["item_key"] = item_keys

        system_custom_set = self.pg.base_get(dbconst.TB_SYSTEM_CUSTOM_CONFIG, conditions)
        if system_custom_set is None or len(system_custom_set) == 0:
            return {}

        custom_configs = {}
        for system_custom in system_custom_set:
            enable_module = system_custom["enable_module"]
            item_key = system_custom["item_key"]
            item_value = system_custom["item_value"]
            if not enable_module:
                continue
            custom_configs[item_key] = item_value
            
        return custom_configs
    

    def get_auth_service_by_ou_dn(self, ou_dn):
        
        conditions = {}

        ou_dn = self.pgm.user_unicode_to_string(ou_dn)
        conditions["base_dn"] = SearchType(ou_dn)
 
        auth_service_set = self.pg.base_get(dbconst.TB_AUTH_SERVICE, conditions)
        if auth_service_set is None or len(auth_service_set) == 0:
            return None
               
        auth_services = {}
        for auth_service in auth_service_set:
            service_id = auth_service["auth_service_id"]
            auth_services[service_id] = auth_service

        return auth_services