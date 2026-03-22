import db.constants as dbconst
import constants as const

class ZonePGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_zones(self, zone_ids=None, status=True,zone_name=None, platform=None):
        
        conditions = {}
        if zone_ids:
            conditions["zone_id"] = zone_ids
        
        if status:
            conditions["status"] = const.ZONE_STATUS_ACTIVE

        if zone_name:
            conditions["zone_name"] = zone_name
        
        if platform:
            conditions["platform"] = platform
        
        zone_set = self.pg.base_get(dbconst.TB_DESKTOP_ZONE, conditions)
        if zone_set is None or len(zone_set) == 0:
            return None

        zones = {}
        for zone in zone_set:
            zone_id = zone["zone_id"]
            zones[zone_id] = zone

        return zones

    def get_zone_name(self, is_upper=True):

        conditions = {}

        zone_set = self.pg.base_get(dbconst.TB_DESKTOP_ZONE, conditions)
        if zone_set is None or len(zone_set) == 0:
            return None

        zone_names = []
        for zone in zone_set:
            zone_name = zone["zone_name"]
            if is_upper:
                zone_names.append(zone_name.upper())
            else:
                zone_names.append(zone_name)

        return zone_names
    
    def get_zone(self, zone_id, extras=[dbconst.TB_ZONE_AUTH,
                                        dbconst.TB_ZONE_CITRIX_CONNECTION,
                                        dbconst.TB_ZONE_CONNECTION,
                                        dbconst.TB_ZONE_RESOURCE_LIMIT
                                        ], ignore_zone=False):
        
        conditions = {}
        conditions["zone_id"] = zone_id
        
        zone = {}
        zone_set = self.pg.base_get(dbconst.TB_DESKTOP_ZONE, conditions)
        if not zone_set:
            if not ignore_zone:
                return None

        if zone_set:
            zone = zone_set[0]
        
        if dbconst.TB_ZONE_AUTH in extras:
            auth_zone = self.get_auth_zone(zone_id)
            if not auth_zone:
                auth_zone = {}
            
            zone["auth_zone"] = auth_zone
            
        if dbconst.TB_ZONE_CITRIX_CONNECTION in extras:
            if zone.get("platform") == const.PLATFORM_TYPE_CITRIX:
                citrix_conn = self.get_zone_citrix_connection(zone_id)
                if not citrix_conn:
                    citrix_conn = {}
                
                zone["citrix_connection"] = citrix_conn
        
        if dbconst.TB_ZONE_CONNECTION in extras:
            conn = self.get_zone_connection(zone_id)
            if not conn:
                conn = {}
            
            zone["connection"] = conn
        
        if dbconst.TB_ZONE_RESOURCE_LIMIT in extras:
            resource_limit = self.get_zone_resource_limit(zone_id)
            if not resource_limit:
                resource_limit = {}
            
            zone["resource_limit"] = resource_limit
        
        return zone
    
    def get_zone_connection(self, zone_id):
        
        conditions = {}
        conditions["zone_id"] = zone_id

        zone_conn_set = self.pg.base_get(dbconst.TB_ZONE_CONNECTION, conditions)
        if zone_conn_set is None or len(zone_conn_set) == 0:
            return None
            
        return zone_conn_set[0]

    def get_zone_citrix_connection(self, zone_id):
        
        conditions = {}
        conditions["zone_id"] = zone_id

        zone_conn_set = self.pg.base_get(dbconst.TB_ZONE_CITRIX_CONNECTION, conditions)
        if zone_conn_set is None or len(zone_conn_set) == 0:
            return None
            
        return zone_conn_set[0]
    
    def get_zone_resource_limit(self, zone_id):

        conditions = {}
        conditions["zone_id"] = zone_id

        zone_resource_set = self.pg.base_get(dbconst.TB_ZONE_RESOURCE_LIMIT, conditions)
        if zone_resource_set is None or len(zone_resource_set) == 0:
            return None
            
        return zone_resource_set[0]

    def get_zone_auths(self, zone_ids):

        conditions = {}
        conditions["zone_id"] = zone_ids

        zone_auth_set = self.pg.base_get(dbconst.TB_ZONE_AUTH, conditions)
        if zone_auth_set is None or len(zone_auth_set) == 0:
            return None
        
        auth_zones = {}
        for zone_auth in zone_auth_set:
            zone_id = zone_auth["zone_id"]
            auth_zones[zone_id] = zone_auth
        
        return auth_zones

    def get_zone_auth(self, zone_id, place_dn=False):

        conditions = {}
        conditions["zone_id"] = zone_id

        zone_auth_set = self.pg.base_get(dbconst.TB_ZONE_AUTH, conditions)
        if zone_auth_set is None or len(zone_auth_set) == 0:
            return None
        
        zone_auth = zone_auth_set[0]
        auth_service_id = zone_auth["auth_service_id"]
        conditions = {}
        conditions["auth_service_id"] = auth_service_id
        auth_service_set = self.pg.base_get(dbconst.TB_AUTH_SERVICE, conditions)
        if auth_service_set is None or len(auth_service_set) == 0:
            return None
        
        auth_service = auth_service_set[0]
        if place_dn:
            auth_service["base_dn"] = zone_auth["base_dn"]

            conditions = {}
            conditions["ou_dn"] = zone_auth["base_dn"]
            base_user_ou = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conditions)
            if base_user_ou is None or len(base_user_ou) == 0:
                pass
            else:
                auth_service["base_user_ou_id"] =  base_user_ou[0]["user_ou_id"]
        
        return auth_service_set[0]

    def get_auth_zone(self, zone_id):

        conditions = {}
        
        if not zone_id:
            return None
        
        conditions["zone_id"] = zone_id

        auth_zone_set = self.pg.base_get(dbconst.TB_ZONE_AUTH, conditions)
        if auth_zone_set is None or len(auth_zone_set) == 0:
            return None
        
        return auth_zone_set[0]

    def get_auth_zones(self, auth_service_id, zone_ids=None):

        conditions = {}
        conditions["auth_service_id"] = auth_service_id
        if zone_ids:
            conditions["zone_id"] = zone_ids

        auth_zone_set = self.pg.base_get(dbconst.TB_ZONE_AUTH, conditions)
        if auth_zone_set is None or len(auth_zone_set) == 0:
            return None
        
        auth_zones = {}
        for auth_zone in auth_zone_set:
            zone_id = auth_zone["zone_id"]
            auth_zones[zone_id] = auth_zone
        
        return auth_zones

    def get_zone_by_auth_services(self, auth_service_ids, zone_ids=None):

        conditions = {}
        conditions["auth_service_id"] = auth_service_ids
        if zone_ids:
            conditions["zone_id"] = zone_ids

        auth_zone_set = self.pg.base_get(dbconst.TB_ZONE_AUTH, conditions)
        if auth_zone_set is None or len(auth_zone_set) == 0:
            return None
        
        auth_zones = {}
        for auth_zone in auth_zone_set:
            zone_id = auth_zone["zone_id"]
            auth_zones[zone_id] = auth_zone
        
        return auth_zones

    def get_auth_service_zone(self):

        conditions = {}
        auth_zone_set = self.pg.base_get(dbconst.TB_ZONE_AUTH, conditions)
        if auth_zone_set is None or len(auth_zone_set) == 0:
            return None
        
        auth_zones = {}
        for auth_zone in auth_zone_set:
            zone_id = auth_zone["zone_id"]
            auth_zones[zone_id] = auth_zone
        
        return auth_zones

    def get_zone_users(self, zone_id, user_ids=None, check_user=False, role=None):
        
        conditions = {}
        conditions["zone_id"] = zone_id
        if user_ids:
            conditions["user_id"] = user_ids

        if role:
            conditions["role"] = role
            
        if check_user and not user_ids:
            return None

        zone_user_set = self.pg.get_all(dbconst.TB_ZONE_USER, conditions)
        if zone_user_set is None or len(zone_user_set) == 0:
            return None

        zone_users = {}
        for zone_user in zone_user_set:
            user_id = zone_user["user_id"]
            zone_users[user_id] = zone_user

        return zone_users

    def get_user_zone_by_id(self, user_id, zone_ids=None):
        
        conditions = {}
        if zone_ids:
            conditions["zone_id"] = zone_ids
        conditions["user_id"] = user_id

        zone_user_set = self.pg.base_get(dbconst.TB_ZONE_USER, conditions)
        if zone_user_set is None or len(zone_user_set) == 0:
            return None

        zone_users = {}
        for zone_user in zone_user_set:
            user_id = zone_user["user_id"]
            zone_id = zone_user["zone_id"]
            zone_users[zone_id] = zone_user

        return zone_users

    def get_zone_user(self, zone_id, user_id=None, user_name=None):

        conditions = {"zone_id": zone_id}
        if user_id:
            conditions["user_id"] = user_id
        
        if user_name:
            conditions["user_name"] = user_name
        
        if not conditions:
            return None

        zone_user_set = self.pg.base_get(dbconst.TB_ZONE_USER, conditions)
        if zone_user_set is None or len(zone_user_set) == 0:
            return None

        return zone_user_set[0]

    def get_user_zone(self, user_id, zone_ids=None):

        conditions = {}
        conditions["user_id"] = user_id
        if zone_ids:
            conditions["zone_id"] = zone_ids
        
        zone_user_set = self.pg.base_get(dbconst.TB_ZONE_USER, conditions)
        if zone_user_set is None or len(zone_user_set) == 0:
            return None
        
        user_zones = {}
        for zone_user in zone_user_set:
            zone_id = zone_user["zone_id"]
            user_zones[zone_id] = zone_user

        return user_zones

    def get_local_user_zones(self, user_id):

        conditions = {}
        conditions["user_id"] = user_id

        zone_user_set = self.pg.base_get(dbconst.TB_ZONE_USER, conditions)
        if zone_user_set is None or len(zone_user_set) == 0:
            return None
        
        user_zones = []
        for zone_user in zone_user_set:
            zone_id = zone_user["zone_id"]
            user_zones.append(zone_id)
        
        return user_zones
        

    def get_zone_user_by_name(self, user_names, zone_id=None):

        conditions = {}
        conditions["user_name"] = user_names
        if zone_id:
            conditions["zone_id"] = zone_id

        zone_user_set = self.pg.base_get(dbconst.TB_ZONE_USER, conditions)
        if zone_user_set is None or len(zone_user_set) == 0:
            return None

        zone_users = {}
        for zone_user in zone_user_set:
            user_name = zone_user["user_name"]
            zone_users[user_name] = zone_user

        return zone_users

    def get_zone_user_id_by_name(self, zone_id, user_names):

        conditions = {}
        conditions["user_name"] = user_names
        conditions["zone_id"] = zone_id

        zone_user_set = self.pg.base_get(dbconst.TB_ZONE_USER, conditions)
        if zone_user_set is None or len(zone_user_set) == 0:
            return None

        zone_users = {}
        for zone_user in zone_user_set:
            user_name = zone_user["user_name"]
            user_id = zone_user["user_id"]
            zone_users[user_name] = user_id

        return zone_users

    def get_zone_resource_count(self, zone_ids=None, user_id=None):
        
        conditions = {}
        ret = self.get_zones(zone_ids, status=True)
        if not ret:
            return None, None
        zone_ids = ret.keys()
        
        conditions["zone"] = zone_ids
        if user_id:
            ret = self.pgm.get_resource_by_user(user_id, resource_type=dbconst.RESTYPE_DESKTOP)
            if not ret:
                return zone_ids[0], None
            user_desktops = []
            for _, desk_ids in ret.items():
                user_desktops.extend(desk_ids)

            conditions["desktop_id"] = user_desktops

        max_zone = None
        max_count = 0
        zone_resources = {}
        zone_resource_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if zone_resource_set is None or len(zone_resource_set) == 0:
            return zone_ids[0], None

        for zone_resource in zone_resource_set:
            zone_id = zone_resource["zone"]
            
            if zone_id not in zone_resources:
                zone_resources[zone_id] = 0

            zone_resources[zone_id] += 1

            if zone_resources[zone_id] > max_count:
                max_count = zone_resources[zone_id]
                max_zone = zone_id

        if max_zone is None:
            max_zone = zone_ids[0]

        return (max_zone, zone_resources)

    def get_zone_user_groups(self, zone_id, user_group_ids=None, check_user=False):
        
        conditions = {}
        conditions["zone_id"] = zone_id
        if user_group_ids:
            conditions["user_group_id"] = user_group_ids
            
        if check_user and not user_group_ids:
            return None

        zone_user_group_set = self.pg.base_get(dbconst.TB_ZONE_USER_GROUP, conditions)
        if zone_user_group_set is None or len(zone_user_group_set) == 0:
            return None
        
        zone_user_groups = {}
        for zone_user_group in zone_user_group_set:
            user_group_id = zone_user_group["user_group_id"]
            zone_user_groups[user_group_id] = zone_user_group

        return zone_user_groups

    def get_user_group_zone_by_id(self, user_group_id, zone_ids=None):
        
        conditions = {}
        if zone_ids:
            conditions["zone_id"] = zone_ids
        conditions["user_group_id"] = user_group_id

        zone_user_group_set = self.pg.base_get(dbconst.TB_ZONE_USER_GROUP, conditions)
        if zone_user_group_set is None or len(zone_user_group_set) == 0:
            return None

        zone_user_groups = {}
        for zone_user_group in zone_user_group_set:
            user_group_id = zone_user_group["user_group_id"]
            zone_id = zone_user_group["zone_id"]
            zone_user_groups[zone_id] = user_group_id

        return zone_user_groups

    def get_zone_citrix_connection_by_host(self,host=None,storefront_uri=None,ignore_zone=None,status=None):

        conditions = {}
        if host:
            conditions["host"] = host

        if storefront_uri:
            conditions["storefront_uri"] = storefront_uri

        if status:
            conditions["status"] = status

        zone_conn_set = self.pg.base_get(dbconst.TB_ZONE_CITRIX_CONNECTION, conditions)
        if zone_conn_set is None or len(zone_conn_set) == 0:
            return None

        for zone_conn in zone_conn_set:
            zone_id = zone_conn["zone_id"]
            if ignore_zone == zone_id:
                return None

        return zone_conn_set[0]
