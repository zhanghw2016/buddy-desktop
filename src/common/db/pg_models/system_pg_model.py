import db.constants as dbconst

class SystemPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_notice_pushs(self, notice_ids=None, scope=None, user_id=None):

        conditions = {}
        if scope:
            conditions["scope"] = scope

        if notice_ids:
            conditions["notice_id"] = notice_ids
        
        if user_id:
            conditions["owner"] = user_id

        notice_set = self.pg.base_get(dbconst.TB_NOTICE_PUSH, conditions)
        if notice_set is None or len(notice_set) == 0:
            return None

        notices = {}
        for notice in notice_set:
            notice_id = notice["notice_id"]
            notices[notice_id] = notice

        return notices
    
    def get_notice_push(self, notice_id):

        conditions = {}
        conditions["notice_id"] = notice_id

        notice_set = self.pg.base_get(dbconst.TB_NOTICE_PUSH, conditions)
        if notice_set is None or len(notice_set) == 0:
            return None
            
        return notice_set[0]

    def get_notice_push_read(self, notice_id, user_id):

        conditions = {}
        conditions["notice_id"] = notice_id
        conditions["user_id"] = user_id

        notice_read_set = self.pg.base_get(dbconst.TB_NOTICE_READ, conditions)
        if notice_read_set is None or len(notice_read_set) == 0:
            return None
            
        return notice_read_set

    def get_zone_notice(self, zone_id, notice_ids=None, user_scope=None, user_id=None):

        conditions = {}
        conditions["zone_id"] = zone_id

        if notice_ids:
            conditions["notice_id"] = notice_ids
        
        if user_scope:
            conditions["user_scope"] = user_scope
        
        if user_id:
            conditions["owner"] = user_id

        notice_zone_set = self.pg.base_get(dbconst.TB_NOTICE_ZONE, conditions)
        if notice_zone_set is None or len(notice_zone_set) == 0:
            return None

        notices = []
        for notice_zone in notice_zone_set:
            notice_id = notice_zone["notice_id"]
            notices.append(notice_id)
            
        return notices

    def get_notice_zone(self, notice_id, zone_id=None):

        conditions = {}
        conditions["notice_id"] = notice_id
        if zone_id:
            conditions["zone_id"] = zone_id

        notice_zone_set = self.pg.base_get(dbconst.TB_NOTICE_ZONE, conditions)
        if notice_zone_set is None or len(notice_zone_set) == 0:
            return None

        zone_notices = {}
        for notice_zone in notice_zone_set:
            zone_id = notice_zone["zone_id"]
            zone_notices[zone_id] = notice_zone

        return zone_notices

    def get_user_notice(self, user_id, notice_ids=None, zone_id = None):

        conditions = {}
        
        user_ids = [user_id]
        ret = self.pgm.get_user_group(user_id)
        if ret:
            user_ids.extend(ret)

        conditions["user_id"] = user_ids
        if notice_ids:
            conditions["notice_id"] = notice_ids
        
        if zone_id:
            conditions["zone_id"] = zone_id
        
        notice_user_set = self.pg.base_get(dbconst.TB_NOTICE_USER, conditions)
        if notice_user_set is None or len(notice_user_set) == 0:
            return None

        notices = []
        for notice_user in notice_user_set:
            notice_id = notice_user["notice_id"]
            notices.append(notice_id)
            
        return notices

    def get_notice_user(self, notice_id, zone_id=None, user_ids=None):

        conditions = {}
        conditions["notice_id"] = notice_id
        if zone_id:
            conditions["zone_id"] = zone_id
        
        if user_ids:
            conditions["user_id"] = user_ids

        notice_user_set = self.pg.base_get(dbconst.TB_NOTICE_USER, conditions)
        if notice_user_set is None or len(notice_user_set) == 0:
            return None

        notice_users = {}
        for notice_user in notice_user_set:
            user_id = notice_user["user_id"]
            notice_users[user_id] = notice_user

        return notice_users

    def get_notice_by_user(self, user_id):

        conditions = {}
        conditions["user_id"] = user_id

        notice_user_set = self.pg.base_get(dbconst.TB_NOTICE_USER, conditions)
        if notice_user_set is None or len(notice_user_set) == 0:
            return None

        notice_users = {}
        for notice_user in notice_user_set:
            user_id = notice_user["user_id"]
            notice_users[user_id] = notice_user

        return notice_users

    def get_softwares(self, software_ids=None, software_name=None,zone=None):

        conditions = {}
        if software_ids:
            conditions["software_id"] = software_ids

        if software_name:
            conditions["software_name"] = software_name

        if zone:
            conditions["zone_id"] = zone

        software_set = self.pg.base_get(dbconst.TB_SOFTWARE_INFO, conditions)
        if software_set is None or len(software_set) == 0:
            return None

        softwares = {}
        for software in software_set:
            software_id = software["software_id"]
            softwares[software_id] = software

        return softwares

    def get_system_config(self, config_key):

        condiction = {'config_key': config_key}
        result = self.pg.base_get(dbconst.TB_VDI_SYSTEM_CONFIG, condiction)
        if result is None or len(result) == 0:
            return None

        return result[0]['config_value']

