import db.constants as dbconst
import user

class LocalUserPGModel():
    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_local_auth_users(self, conditions, index_dn=False):
        
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None

        users = {}
        for user in user_set:
            self.pgm.user_unicode_to_string(user)
            
            if index_dn:
                user_dn = user["user_dn"]
                users[user_dn] = user
            else:
                user_name = user["user_name"]
                users[user_name] = user

        return users

    def get_local_auth_ous(self, conditions, index_dn=False):
        
        user_ou_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_OU, conditions)
        if user_ou_set is None or len(user_ou_set) == 0:
            return None

        user_ous = {}
        for user_ou in user_ou_set:
            self.pgm.user_unicode_to_string(user_ou)
            
            if index_dn:
                ou_dn = user_ou["ou_dn"]
                user_ous[ou_dn] = user_ou
            else:
                object_guid = user_ou["object_guid"]
                user_ous[object_guid] = user_ou

        return user_ous

    def get_local_auth_user_group(self, conditions, index_dn=False):
        
        user_group_set = self.pg.base_get(dbconst.TB_DESKTOP_USER_GROUP, conditions)
        if user_group_set is None or len(user_group_set) == 0:
            return None

        user_groups = {}
        for user_group in user_group_set:
            self.pgm.user_unicode_to_string(user_group)
            if index_dn:
                user_group_dn = user_group["user_group_dn"]
                user_groups[user_group_dn] = user_group
            else:
                user_group_name = user_group["user_group_name"]
                user_groups[user_group_name] = user_group

        return user_groups
