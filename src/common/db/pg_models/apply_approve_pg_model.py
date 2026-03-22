import db.constants as dbconst
import constants as const
from utils.id_tool import(
    UUID_TYPE_DESKTOP_USER_GROUP
)

class ApplyApprovePGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_apply_group_name(self, zone_id=None,is_upper=True):

        conditions = {}

        if zone_id:
            conditions["zone_id"] = zone_id

        apply_group_set = self.pg.base_get(dbconst.TB_APPLY_GROUP, conditions)
        if apply_group_set is None or len(apply_group_set) == 0:
            return None

        apply_group_names = {}
        for apply_group in apply_group_set:
            apply_group_name = apply_group["apply_group_name"]
            apply_group_id = apply_group["apply_group_id"]
            if is_upper:
                apply_group_names[apply_group_id] = apply_group_name.lower()
            else:
                apply_group_names[apply_group_id] = apply_group_name

        return apply_group_names

    def get_apply_groups(self, apply_group_ids=None,apply_group_name=None,zone_id=None):

        conditions = {}
        if apply_group_ids:
            conditions["apply_group_id"] = apply_group_ids

        if apply_group_name:
            conditions["apply_group_name"] = apply_group_name

        if zone_id:
            conditions["zone_id"] = zone_id

        apply_group_set = self.pg.base_get(dbconst.TB_APPLY_GROUP, conditions)
        if apply_group_set is None or len(apply_group_set) == 0:
            return None

        apply_groups = {}
        for apply_group in apply_group_set:
            apply_group_id = apply_group["apply_group_id"]
            apply_groups[apply_group_id] = apply_group

        return apply_groups

    def get_approve_group_by_apply_group(self, apply_group_id, approve_group_ids=None):

        conditions = {"apply_group_id": apply_group_id}

        if approve_group_ids:
            conditions["approve_group_id"] = approve_group_ids

        apply_approve_group_map_set = self.pg.base_get(dbconst.TB_APPLY_APPROVE_GROUP_MAP, conditions)
        if apply_approve_group_map_set is None or len(apply_approve_group_map_set) == 0:
            return None

        approve_group_ids = []
        for apply_approve_group_map in apply_approve_group_map_set:
            approve_group_id = apply_approve_group_map["approve_group_id"]
            approve_group_ids.append(approve_group_id)

        return approve_group_ids

    def get_apply_group_by_approve_group(self, approve_group_id, apply_group_ids=None):

        conditions = {"approve_group_id": approve_group_id}

        if apply_group_ids:
            conditions["apply_group_id"] = apply_group_ids

        apply_approve_group_map_set = self.pg.base_get(dbconst.TB_APPLY_APPROVE_GROUP_MAP, conditions)
        if apply_approve_group_map_set is None or len(apply_approve_group_map_set) == 0:
            return None

        apply_group_ids = []
        for apply_approve_group_map in apply_approve_group_map_set:
            apply_group_id = apply_approve_group_map["apply_group_id"]
            apply_group_ids.append(apply_group_id)

        return apply_group_ids

    def get_apply_approve_group_maps(self, apply_group_ids=None,approve_group_ids=None):

        conditions = {}
        if apply_group_ids:
            conditions["apply_group_id"] = apply_group_ids

        if approve_group_ids:
            conditions["approve_group_id"] = approve_group_ids

        apply_approve_group_map_set = self.pg.base_get(dbconst.TB_APPLY_APPROVE_GROUP_MAP, conditions)
        if apply_approve_group_map_set is None or len(apply_approve_group_map_set) == 0:
            return None

        apply_approve_group_maps = {}
        for apply_approve_group_map in apply_approve_group_map_set:
            approve_group_id = apply_approve_group_map["approve_group_id"]
            apply_approve_group_maps[approve_group_id] = apply_approve_group_map

        return apply_approve_group_maps

    def get_approve_apply_group_maps(self, apply_group_ids=None,approve_group_ids=None):

        conditions = {}
        if apply_group_ids:
            conditions["apply_group_id"] = apply_group_ids

        if approve_group_ids:
            conditions["approve_group_id"] = approve_group_ids

        apply_approve_group_map_set = self.pg.base_get(dbconst.TB_APPLY_APPROVE_GROUP_MAP, conditions)
        if apply_approve_group_map_set is None or len(apply_approve_group_map_set) == 0:
            return None

        apply_approve_group_maps = {}
        for apply_approve_group_map in apply_approve_group_map_set:
            apply_group_id = apply_approve_group_map["apply_group_id"]
            apply_approve_group_maps[apply_group_id] = apply_approve_group_map

        return apply_approve_group_maps

    def get_apply_group_resources(self, apply_group_ids=None,resource_ids=None):

        conditions = {}
        if apply_group_ids:
            conditions["apply_group_id"] = apply_group_ids

        if resource_ids:
            conditions["resource_id"] = resource_ids

        apply_group_resource_set = self.pg.base_get(dbconst.TB_APPLY_GROUP_RESOURCE, conditions)
        if apply_group_resource_set is None or len(apply_group_resource_set) == 0:
            return None

        apply_group_resources = {}
        for apply_group_resource in apply_group_resource_set:
            resource_id = apply_group_resource["resource_id"]
            apply_group_resources[resource_id] = apply_group_resource

        return apply_group_resources

    def get_apply_group_user(self, apply_group_id=None, user_ids=None):

        conditions = {}
        if apply_group_id:
            conditions["apply_group_id"] = apply_group_id

        if user_ids:
            conditions["user_id"] = user_ids

        apply_group_user_set = self.pg.base_get(dbconst.TB_APPLY_GROUP_USER, conditions)
        if apply_group_user_set is None or len(apply_group_user_set) == 0:
            return None

        apply_group_users = {}
        for apply_group_user in apply_group_user_set:
            user_id = apply_group_user["user_id"]

            if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                ret = self.pgm.get_user_group_user(user_id)
                if not ret:
                    ret = {}
                apply_group_user["group_users"] = ret.values()

            apply_group_users[user_id] = apply_group_user

        return apply_group_users

    def get_approve_group_user(self, approve_group_id=None, user_ids=None):

        conditions = {}
        if approve_group_id:
            conditions["approve_group_id"] = approve_group_id

        if user_ids:
            conditions["user_id"] = user_ids

        approve_group_user_set = self.pg.base_get(dbconst.TB_APPROVE_GROUP_USER, conditions)
        if approve_group_user_set is None or len(approve_group_user_set) == 0:
            return None

        approve_group_users = {}
        for approve_group_user in approve_group_user_set:
            user_id = approve_group_user["user_id"]

            if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                ret = self.pgm.get_user_group_user(user_id)
                if not ret:
                    ret = {}
                approve_group_user["group_users"] = ret.values()

            approve_group_users[user_id] = approve_group_user

        return approve_group_users

    def get_approve_group_name(self, zone_id=None, is_upper=True):

        conditions = {}
        if zone_id:
            conditions["zone_id"] = zone_id

        approve_group_set = self.pg.base_get(dbconst.TB_APPROVE_GROUP, conditions)
        if approve_group_set is None or len(approve_group_set) == 0:
            return None

        approve_group_names = {}
        for approve_group in approve_group_set:
            approve_group_name = approve_group["approve_group_name"]
            approve_group_id = approve_group["approve_group_id"]
            if is_upper:
                approve_group_names[approve_group_id] = approve_group_name.lower()
            else:
                approve_group_names[approve_group_id] = approve_group_name

        return approve_group_names

    def get_approve_groups(self, approve_group_ids=None,approve_group_name=None,zone_id=None):

        conditions = {}
        if approve_group_ids:
            conditions["approve_group_id"] = approve_group_ids

        if approve_group_name:
            conditions["approve_group_name"] = approve_group_name

        if zone_id:
            conditions["zone_id"] = zone_id

        approve_group_set = self.pg.base_get(dbconst.TB_APPROVE_GROUP, conditions)
        if approve_group_set is None or len(approve_group_set) == 0:
            return None

        approve_groups = {}
        for approve_group in approve_group_set:
            approve_group_id = approve_group["approve_group_id"]
            approve_groups[approve_group_id] = approve_group

        return approve_groups

    def get_resource_apply_forms(self, resource_id=None, user_id=None, resource_group_id=None, apply_group_id=None, status=const.APPLY_FORM_VAILD_STATUS):

        conditions = {}
        if resource_id:
            conditions["resource_id"] = resource_id

        if resource_group_id:
            conditions["resource_group_id"] = resource_group_id

        if user_id:
            conditions["apply_user_id"] = user_id

        if status:
            conditions["status"] = status
        
        if apply_group_id:
            conditions["apply_group_id"] =apply_group_id

        apply_form_set = self.pg.base_get(dbconst.TB_APPLY, conditions)
        if apply_form_set is None or len(apply_form_set) == 0:
            return None

        apply_forms = {}
        for apply_form in apply_form_set:
            apply_id = apply_form["apply_id"]
            apply_forms[apply_id] = apply_form

        return apply_forms

    def get_user_apply_forms(self, apply_group_id=None, user_id=None, resource_ids = None, approve_group_id=None, status=const.APPLY_FORM_STATUS_LOCKED, approve_user_ids=None):

        conditions = {}
        if apply_group_id:
            conditions["apply_group_id"] = apply_group_id
        
        if approve_group_id:
            conditions["approve_group_id"] = approve_group_id

        if user_id:
            conditions["apply_user_id"] = user_id
        
        if resource_ids:
            conditions["resource_id"] = resource_ids
        
        if approve_user_ids:
            conditions["approve_user_id"] = approve_user_ids

        if status:
            conditions["status"] = status
        
        apply_form_set = self.pg.base_get(dbconst.TB_APPLY, conditions)
        if apply_form_set is None or len(apply_form_set) == 0:
            return None

        apply_forms = {}
        for apply_form in apply_form_set:
            apply_id = apply_form["apply_id"]
            apply_forms[apply_id] = apply_form

        return apply_forms

    def get_apply_forms(self,apply_ids=None,
                        apply_type=None,
                        resource_group_id=None,
                        apply_user_id=None,
                        status=None,
                        zone_id=None, 
                        approve_group_id=None, 
                        apply_group_id=None,
                        resource_id=None):

        conditions = {}
        if apply_ids:
            conditions["apply_id"] = apply_ids

        if apply_type:
            conditions["apply_type"] = apply_type

        if resource_group_id:
            conditions["resource_group_id"] = resource_group_id

        if apply_user_id:
            conditions["apply_user_id"] = apply_user_id
            
        if approve_group_id:
            conditions["approve_group_id"] = approve_group_id
        
        if apply_group_id:
            conditions["apply_group_id"] = apply_group_id
            
        if status:
            conditions["status"] = status

        if zone_id:
            conditions["zone_id"] = zone_id
        
        if resource_id:
            conditions["resource_id"] = resource_id

        apply_form_set = self.pg.base_get(dbconst.TB_APPLY, conditions)
        if apply_form_set is None or len(apply_form_set) == 0:
            return None

        apply_forms = {}
        for apply_form in apply_form_set:
            apply_id = apply_form["apply_id"]
            apply_forms[apply_id] = apply_form

        return apply_forms

    def get_apply_resource_groups(self, resource_group_id=None,apply_group_id=None):

        conditions = {}
        if resource_group_id:
            conditions["resource_id"] = resource_group_id

        if apply_group_id:
            conditions["apply_group_id"] = apply_group_id

        if not conditions:
            return None

        apply_resource_group_set = self.pg.base_get(dbconst.TB_APPLY_GROUP_RESOURCE, conditions)
        if apply_resource_group_set is None or len(apply_resource_group_set) == 0:
            return None

        apply_resources = {}
        for apply_resource in apply_resource_group_set:
            resource_group_id = apply_resource["resource_id"]
            apply_resources[resource_group_id] = apply_resource

        return apply_resources

    def get_resource_group_apply_group(self, resource_group_id):

        conditions = {}
        if resource_group_id:
            conditions["resource_id"] = resource_group_id

        if not conditions:
            return None

        apply_resource_group_set = self.pg.base_get(dbconst.TB_APPLY_GROUP_RESOURCE, conditions)
        if apply_resource_group_set is None or len(apply_resource_group_set) == 0:
            return None

        apply_group_ids = []
        for apply_resource in apply_resource_group_set:
            apply_group_id = apply_resource["apply_group_id"]
            apply_group_ids.append(apply_group_id)

        return apply_group_ids


    def get_apply_user(self, apply_group_id=None, user_ids=None):

        conditions = {}

        if user_ids and not isinstance(user_ids, list):
            user_ids = [user_ids]

        if user_ids:
            conditions["user_id"] = user_ids

        if apply_group_id:
            conditions["apply_group_id"] = apply_group_id

        if not conditions:
            return None

        apply_user_set = self.pg.base_get(dbconst.TB_APPLY_GROUP_USER, conditions)
        if apply_user_set is None or len(apply_user_set) == 0:
            return None

        apply_users = {}
        for apply_user in apply_user_set:
            user_id = apply_user["user_id"]
            apply_users[user_id] = apply_user

        return apply_users

