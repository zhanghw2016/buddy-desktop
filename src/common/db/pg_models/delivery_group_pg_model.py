
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_DESKTOP_USER,
    UUID_TYPE_DESKTOP_USER_GROUP
)
import constants as const
from common import unicode_to_string

class DeliveryGroupPGModel():
    ''' VDI model for complicated requests '''

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_delivery_groups(self, delivery_group_ids=None, delivery_group_name=None, columns=None, zone_id=None):

        conditions = {}
        
        if delivery_group_ids:
            conditions["delivery_group_id"] = delivery_group_ids
        
        if delivery_group_name:
            conditions["delivery_group_name"] = delivery_group_name

        if zone_id:
            conditions["zone"] = zone_id
        
        delivery_group_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP, conditions, columns=columns)
        if delivery_group_set is None or len(delivery_group_set) == 0:
            return None

        delivery_groups = {}
        for delivery_group in delivery_group_set:
            delivery_group_id = delivery_group["delivery_group_id"]
            
            delivery_groups[delivery_group_id] = delivery_group
            
        return delivery_groups

    def get_delivery_group(self, delivery_group_id):

        conditions = {"delivery_group_id": delivery_group_id}
        
        delivery_group_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP, conditions)
        if not delivery_group_set:
            return None

        return delivery_group_set[0]

    def get_delivery_group_name(self, delivery_group_ids=None,zone_id=None):

        conditions = {}
        if delivery_group_ids:
            conditions["delivery_group_id"] = delivery_group_ids
        
        if zone_id:
            conditions["zone"] = zone_id
        
        delivery_group_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP, conditions)
        if delivery_group_set is None or len(delivery_group_set) == 0:
            return None

        delivery_group_names = {}
        for delivery_group in delivery_group_set:
            delivery_group_name = delivery_group["delivery_group_name"]
            delivery_group_id = delivery_group["delivery_group_id"]
            delivery_group_names[delivery_group_id] = delivery_group_name
            
        return delivery_group_names
    
    def get_delivery_group_users(self, delivery_group_id, user_ids=None, user_type=None):
        
        conditions = {"delivery_group_id": delivery_group_id}
        if user_ids:
            conditions["user_id"] = user_ids
        
        if user_type:
            conditions["user_type"] = user_type
        
        delivery_group_user_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP_USER, conditions)
        if delivery_group_user_set is None or len(delivery_group_user_set) == 0:
            return None
        
        user_names = {}
        delivery_group_users = []
        for delivery_group_user in delivery_group_user_set:
            user_id = delivery_group_user["user_id"]
            user_name = delivery_group_user["user_name"]
            if user_name:
                user_names[user_id] = user_name
                continue

            delivery_group_users.append(user_id)

        user_ids = []
        user_group_ids = []
        for user_id in delivery_group_users:
            if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                user_group_ids.append(user_id)
            elif user_id.startswith(UUID_TYPE_DESKTOP_USER):
                user_ids.append(user_id)
        
        if user_ids:
            ret = self.pgm.get_user_names(user_ids)
            if ret:
                user_names.update(ret)
        
        if user_group_ids:
            ret = self.pgm.get_user_group_names(user_group_ids)
            if ret:
                user_names.update(ret)

        return user_names

    def get_delivery_group_user(self, delivery_group_id, user_ids=None):
        
        conditions = {"delivery_group_id": delivery_group_id}
        if user_ids:
            conditions["user_id"] = user_ids

        delivery_group_user_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP_USER, conditions)
        if delivery_group_user_set is None or len(delivery_group_user_set) == 0:
            return None

        delivery_group_users = {}
        for delivery_group_user in delivery_group_user_set:
            user_id = delivery_group_user["user_id"]
            
            if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                ret = self.pgm.get_user_group_user(user_id)
                if not ret:
                    ret = {}
                delivery_group_user["group_users"] = ret.values()

            delivery_group_users[user_id] = delivery_group_user
            
        return delivery_group_users

    def get_delivery_group_user_ids(self, delivery_group_id):
        
        conditions = {"delivery_group_id": delivery_group_id}
        delivery_group_user_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP_USER, conditions)
        if delivery_group_user_set is None or len(delivery_group_user_set) == 0:
            return None
        
        deli_user_ids = []
        for delivery_group_user in delivery_group_user_set:
            user_id = delivery_group_user["user_id"]
            
            if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                ret = self.pgm.get_user_group_user(user_id)
                if ret:
                    deli_user_ids.extend(ret.keys())
            else:
                deli_user_ids.append(user_id)
            
        return deli_user_ids

    def get_delivery_group_by_user(self, user_id):
        
        conditions = {"user_id": user_id}

        delivery_group_user_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP_USER, conditions)
        if delivery_group_user_set is None or len(delivery_group_user_set) == 0:
            return None

        delivery_group_ids = []
        for delivery_group_user in delivery_group_user_set:
            delivery_group_id = delivery_group_user["delivery_group_id"]
            delivery_group_ids.append(delivery_group_id)
            
        return delivery_group_ids

    def get_delivery_group_by_name(self, delivery_group_name,zone_id):
        
        conditions = {"delivery_group_name": delivery_group_name,"zone":zone_id}

        delivery_group_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP, conditions)
        if not delivery_group_set:
            return None

        delivery_groups = {}
        for delivery_group in delivery_group_set:
            delivery_group_name = delivery_group["delivery_group_name"]
            delivery_groups[delivery_group_name] = delivery_group

        return delivery_groups

    def get_delivery_user_group(self, group_names):
        
        conditions = {"user_name": group_names, "user_type": "group"}

        delivery_group_user_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP_USER, conditions)
        if delivery_group_user_set is None or len(delivery_group_user_set) == 0:
            return None

        delivery_group_users = {}
        for delivery_group_user in delivery_group_user_set:
            user_name = delivery_group_user["user_name"]
            if user_name not in delivery_group_users:
                delivery_group_users[user_name] = []
            
            delivery_group_users[user_name].append(delivery_group_user)
                            
        return delivery_group_users
    
    def get_delivery_group_broker_apps(self, delivery_group_id, broker_app_ids=None):

        conditions = {"delivery_group_id": delivery_group_id, "broker_type": const.BROKER_APP_TYPE_APP}
        
        if broker_app_ids:
            conditions["broker_app_id"] = broker_app_ids

        broker_app_set = self.pg.base_get(dbconst.TB_BROKER_APP_DELIVERY_GROUP, conditions)
        if broker_app_set is None or len(broker_app_set) == 0:
            return None

        broker_apps = {}
        for broker_app in broker_app_set:
            broker_app_id = broker_app["broker_app_id"]
            broker_apps[broker_app_id] = broker_app
                            
        return broker_apps

    def get_delivery_group_broker_app_groups(self, delivery_group_id, broker_app_group_ids=None):

        conditions = {"delivery_group_id": delivery_group_id, "broker_type": const.BROKER_APP_TYPE_APP_GROUP}
        
        if broker_app_group_ids:
            conditions["broker_app_id"] = broker_app_group_ids

        broker_app_set = self.pg.base_get(dbconst.TB_BROKER_APP_DELIVERY_GROUP, conditions)
        if broker_app_set is None or len(broker_app_set) == 0:
            return None

        broker_apps = {}
        for broker_app in broker_app_set:
            broker_app_id = broker_app["broker_app_id"]
            broker_apps[broker_app_id] = broker_app
                            
        return broker_apps

    def get_broker_app_delivery_group(self, broker_app_id, delivery_group_ids=None):
        
        conditions = {"broker_app_id": broker_app_id}
        
        if delivery_group_ids:
            conditions["delivery_group_id"] = delivery_group_ids

        delivery_group_app_set = self.pg.base_get(dbconst.TB_BROKER_APP_DELIVERY_GROUP, conditions)
        if delivery_group_app_set is None or len(delivery_group_app_set) == 0:
            return None

        broker_app_deliverys = []
        for delivery_group_app in delivery_group_app_set:
            delivery_group_id = delivery_group_app["delivery_group_id"]
            
            broker_app_deliverys.append(delivery_group_id)
                            
        return broker_app_deliverys

    def get_delivery_group_uid(self, delivery_group_ids):
        
        conditions = {"delivery_group_id": delivery_group_ids}

        delivery_group_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP, conditions)
        if delivery_group_set is None or len(delivery_group_set) == 0:
            return None

        delivery_group_uids = {}
        for delivery_group in delivery_group_set:
            delivery_group_id = delivery_group["delivery_group_id"]
            uid = delivery_group["delivery_group_uid"]
            if not uid:
                continue
            delivery_group_uids[delivery_group_id] = uid
                            
        return delivery_group_uids

    def get_delivery_group_by_uid(self, delivery_group_uids):
        
        if not delivery_group_uids:
            return None
        
        conditions = {"delivery_group_uid": delivery_group_uids}
        
        delivery_group_set = self.pg.base_get(dbconst.TB_DELIVERY_GROUP, conditions)
        if delivery_group_set is None or len(delivery_group_set) == 0:
            return None

        delivery_groups = {}
        for delivery_group in delivery_group_set:
            delivery_group_uid = delivery_group["delivery_group_uid"]
            delivery_groups[delivery_group_uid] = delivery_group
            
        return delivery_groups

    def get_broker_app(self, broker_app_id):

        conditions = {"broker_app_id": broker_app_id}

        broker_app_set = self.pg.base_get(dbconst.TB_BROKER_APP, conditions)
        if broker_app_set is None or len(broker_app_set) == 0:
            return None

        return broker_app_set[0]

    def get_broker_apps(self, broker_app_ids=None, zone_id=None, index_uid=False):
        
        conditions = {}
        if broker_app_ids:
            conditions["broker_app_id"] = broker_app_ids
        
        if zone_id:
            conditions["zone"] = zone_id
            
        if not conditions:
            return None

        broker_app_set = self.pg.base_get(dbconst.TB_BROKER_APP, conditions)
        if broker_app_set is None or len(broker_app_set) == 0:
            return None
        
        broker_apps = {}
        for broker_app in broker_app_set:
            broker_app = unicode_to_string(broker_app)

            broker_app_id = broker_app["broker_app_id"]
            
            if index_uid:
                broker_app_uid = broker_app["broker_app_uid"]
                broker_apps[broker_app_uid] = broker_app
            else:
                broker_apps[broker_app_id] = broker_app
                            
        return broker_apps

    def get_broker_app_in_app_group(self, broker_app_id):
        
        conditions = {"broker_app_id": broker_app_id}


        app_group_app_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, conditions)
        if app_group_app_set is None or len(app_group_app_set) == 0:
            return None
                            
        return app_group_app_set
    
    def get_broker_app_in_delivery_group(self, broker_app_id):

        conditions = {"broker_app_id": broker_app_id}


        delivery_group_app_set = self.pg.base_get(dbconst.TB_BROKER_APP_DELIVERY_GROUP, conditions)
        if delivery_group_app_set is None or len(delivery_group_app_set) == 0:
            return None
                            
        return delivery_group_app_set

    def get_broker_app_name(self, broker_app_ids):

        conditions = {"broker_app_id": broker_app_ids}

        broker_app_set = self.pg.base_get(dbconst.TB_BROKER_APP, conditions)
        if broker_app_set is None or len(broker_app_set) == 0:
            return None

        broker_apps = {}
        for broker_app in broker_app_set:
            broker_app_id = broker_app["broker_app_id"]
            display_name = broker_app["display_name"]
            broker_apps[broker_app_id] = display_name
                            
        return broker_apps

    def get_broker_app_group(self, broker_app_group_id):

        conditions = {
                      "broker_app_group_id": broker_app_group_id}
        
        app_group_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP, conditions)
        if app_group_set is None or len(app_group_set) == 0:
            return None
            
        return app_group_set[0]

    def get_broker_app_groups(self, broker_app_group_ids=None, zone_id=None, index_uid=False, ):

        conditions = {}
        
        if broker_app_group_ids:
            conditions["broker_app_group_id"] = broker_app_group_ids
        
        if zone_id:
            conditions["zone"] = zone_id
        
        if not conditions:
            return None
        
        app_group_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP, conditions)
        if app_group_set is None or len(app_group_set) == 0:
            return None

        broker_app_groups = {}
        for app_group in app_group_set:
            broker_app_group_id = app_group["broker_app_group_id"]
            if index_uid:
                broker_app_group_uid = app_group["broker_app_group_uid"]
                broker_app_groups[broker_app_group_uid] = app_group
            else:
                broker_app_groups[broker_app_group_id] = app_group
            
        return broker_app_groups

    def get_app_group_by_name(self, zone, broker_app_group_names):

        conditions = {"zone":zone,
                      "broker_app_group_name": broker_app_group_names}
        
        app_group_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP, conditions)
        if app_group_set is None or len(app_group_set) == 0:
            return None

        app_group_names = {}
        for app_group in app_group_set:
            broker_app_group_name = app_group["broker_app_group_name"]
            broker_app_group_id = app_group["broker_app_group_id"]
            app_group_names[broker_app_group_id] = broker_app_group_name
            
        return app_group_names

    def get_app_group_names(self, broker_app_group_ids):

        conditions = {
                      "broker_app_group_id": broker_app_group_ids}
        
        app_group_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP, conditions)
        if app_group_set is None or len(app_group_set) == 0:
            return None

        app_group_names = {}
        for app_group in app_group_set:
            broker_app_group_name = app_group["broker_app_group_name"]
            broker_app_group_id = app_group["broker_app_group_id"]
            app_group_names[broker_app_group_id] = broker_app_group_name
            
        return app_group_names

    def get_broker_app_app_group(self, broker_app_id, app_group_ids=None):
        
        conditions = {"broker_app_id": broker_app_id}
        
        if app_group_ids:
            conditions["broker_app_group_id"] = app_group_ids

        app_group_app_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, conditions)
        if app_group_app_set is None or len(app_group_app_set) == 0:
            return None

        broker_app_groups = []
        for app_group_app in app_group_app_set:
            app_group_id = app_group_app["broker_app_group_id"]
            
            broker_app_groups.append(app_group_id)
                            
        return broker_app_groups

    def get_broker_app_group_app(self, broker_app_group_id):
        
        conditions = {"broker_app_group_id": broker_app_group_id}

        app_group_app_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, conditions)
        if app_group_app_set is None or len(app_group_app_set) == 0:
            return None

        broker_app_groups = {}
        for app_group_app in app_group_app_set:
            broker_app_id = app_group_app["broker_app_id"]
            
            broker_app_groups[broker_app_id] = app_group_app
                            
        return broker_app_groups

    def get_broker_app_group_delivery_group(self, broker_app_group_id):
        
        conditions = {"broker_app_id": broker_app_group_id}

        app_group_app_set = self.pg.base_get(dbconst.TB_BROKER_APP_DELIVERY_GROUP, conditions)
        if app_group_app_set is None or len(app_group_app_set) == 0:
            return None

        delivery_groups = {}
        for app_group in app_group_app_set:
            delivery_group_id = app_group["delivery_group_id"]
            
            delivery_groups[delivery_group_id] = app_group
                            
        return delivery_groups
    
    def get_broker_app_group_uid(self, broker_app_group_ids):
        
        conditions = {"broker_app_group_id": broker_app_group_ids}

        app_group_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP, conditions)
        if app_group_set is None or len(app_group_set) == 0:
            return None

        app_group_uids = {}
        for app_group in app_group_set:
            broker_app_group_uid = app_group["broker_app_group_uid"]
            broker_app_group_id = app_group["broker_app_group_id"]
            
            if not broker_app_group_uid:
                continue
            app_group_uids[broker_app_group_id] = broker_app_group_uid
                            
        return app_group_uids

    def get_broker_app_group_by_uid(self, uids):
        
        conditions = {"broker_app_group_uid": uids}

        app_group_set = self.pg.base_get(dbconst.TB_BROKER_APP_GROUP, conditions)
        if app_group_set is None or len(app_group_set) == 0:
            return None

        app_groups = {}
        for app_group in app_group_set:
            broker_app_group_id = app_group["broker_app_group_id"]
            app_groups[broker_app_group_id] = app_group
            
        return app_groups
    
    def get_broker_app_by_uid(self, app_uids):
        
        if not app_uids:
            return None
        
        conditions = {"broker_app_uid": app_uids}

        app_set = self.pg.base_get(dbconst.TB_BROKER_APP, conditions)
        if app_set is None or len(app_set) == 0:
            return None

        broker_apps = {}
        for app in app_set:
            broker_app_id = app["broker_app_id"]
            broker_app_uid = app["broker_app_uid"]
            broker_apps[broker_app_id] = broker_app_uid
            
        return broker_apps
