import db.constants as dbconst

class ModuleCustomPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_module_custom_users(self, module_custom_ids=None,user_ids=None,zone_ids=None):

        conditions = {}
        if module_custom_ids:
            conditions["module_custom_id"] = module_custom_ids

        if user_ids:
            conditions["user_id"] = user_ids

        if zone_ids:
            conditions["zone_id"] = zone_ids

        module_custom_user_set = self.pg.base_get(dbconst.TB_MODULE_CUSTOM_USER, conditions)
        if module_custom_user_set is None or len(module_custom_user_set) == 0:
            return None

        module_custom_users = {}
        for module_custom_user in module_custom_user_set:
            module_custom_id = module_custom_user["module_custom_id"]
            module_custom_users[module_custom_id] = module_custom_user

        return module_custom_users

    def get_module_custom_configs(self, module_custom_ids=None,module_type=None,item_key=None):

        conditions = {}
        if module_custom_ids:
            conditions["module_custom_id"] = module_custom_ids

        if module_type:
            conditions["module_type"] = module_type

        if item_key:
            conditions["item_key"] = item_key

        module_custom_config_set = self.pg.base_get(dbconst.TB_MODULE_CUSTOM_CONFIG, conditions)
        if module_custom_config_set is None or len(module_custom_config_set) == 0:
            return None

        module_custom_configs = {}
        for module_custom_config in module_custom_config_set:
            item_key = module_custom_config["item_key"]
            module_custom_configs[item_key] = module_custom_config

        return module_custom_configs

    def get_module_customs(self, module_custom_ids=None,is_default=None):

        conditions = {}
        if module_custom_ids:
            conditions["module_custom_id"] = module_custom_ids

        if is_default is not None:
            conditions["is_default"] = is_default

        module_custom_set = self.pg.base_get(dbconst.TB_MODULE_CUSTOM, conditions)
        if module_custom_set is None or len(module_custom_set) == 0:
            return None

        module_customs = {}
        for module_custom in module_custom_set:
            module_custom_id = module_custom["module_custom_id"]
            module_customs[module_custom_id] = module_custom

        return module_customs

    def get_module_custom_zones(self, module_custom_ids=None,zone_ids=None,user_ids=None,user_scope=None):

        conditions = {}
        if module_custom_ids:
            conditions["module_custom_id"] = module_custom_ids

        if zone_ids:
            conditions["zone_id"] = zone_ids

        if user_ids:
            conditions["user_id"] = user_ids

        if user_scope:
            conditions["user_scope"] = user_scope

        module_custom_zone_set = self.pg.base_get(dbconst.TB_MODULE_CUSTOM_ZONE, conditions)
        if module_custom_zone_set is None or len(module_custom_zone_set) == 0:
            return None

        module_custom_zones = {}
        for module_custom_zone in module_custom_zone_set:
            module_custom_id = module_custom_zone["module_custom_id"]
            module_custom_zones[module_custom_id] = module_custom_zone

        return module_custom_zones

    def get_custom_name(self, is_upper=True):

        conditions = {}

        module_custom_set = self.pg.base_get(dbconst.TB_MODULE_CUSTOM, conditions)
        if module_custom_set is None or len(module_custom_set) == 0:
            return None

        custom_names = []
        for module_custom in module_custom_set:
            custom_name = module_custom["custom_name"]
            if is_upper:
                custom_names.append(custom_name.upper())
            else:
                custom_names.append(custom_name)

        return custom_names

    def get_module_custom(self, module_custom_id):

        conditions = {}
        conditions["module_custom_id"] = module_custom_id

        module_custom_set = self.pg.base_get(dbconst.TB_MODULE_CUSTOM, conditions)
        if module_custom_set is None or len(module_custom_set) == 0:
            return None

        return module_custom_set[0]

    def get_module_custom_zone(self, module_custom_ids=None, zone_id=None,user_scope=None):

        conditions = {}

        if module_custom_ids:
            conditions["module_custom_id"] = module_custom_ids

        if zone_id:
            conditions["zone_id"] = zone_id

        if user_scope:
            conditions["user_scope"] = user_scope

        module_custom_zone_set = self.pg.base_get(dbconst.TB_MODULE_CUSTOM_ZONE, conditions)
        if module_custom_zone_set is None or len(module_custom_zone_set) == 0:
            return None

        module_custom_zones = {}
        for module_custom_zone in module_custom_zone_set:
            zone_id = module_custom_zone["zone_id"]
            module_custom_zones[zone_id] = module_custom_zone

        return module_custom_zones

    def get_module_custom_user(self, module_custom_ids=None, zone_id=None, user_ids=None):

        conditions = {}

        if module_custom_ids:
            conditions["module_custom_id"] = module_custom_ids

        if zone_id:
            conditions["zone_id"] = zone_id

        if user_ids:
            conditions["user_id"] = user_ids

        module_custom_user_set = self.pg.base_get(dbconst.TB_MODULE_CUSTOM_USER, conditions)
        if module_custom_user_set is None or len(module_custom_user_set) == 0:
            return None

        module_custom_users = {}
        for module_custom_user in module_custom_user_set:
            user_id = module_custom_user["user_id"]
            module_custom_users[user_id] = module_custom_user

        return module_custom_users

    def get_module_types(self, item_key=None,enable_module=None):

        conditions = {}

        if item_key:
            conditions["item_key"] = item_key

        if enable_module is not None:
            conditions["enable_module"] = enable_module

        module_type_set = self.pg.base_get(dbconst.TB_MODULE_TYPE, conditions)
        if module_type_set is None or len(module_type_set) == 0:
            return None

        module_types = {}
        for module_type in module_type_set:
            item_key = module_type["item_key"]
            module_types[item_key] = module_type

        return module_types







