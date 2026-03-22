
import constants as const
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from db.constants import TB_DESKTOP_ZONE
from api.citrix.store_front import ZoneStoreFront
from api.zone.zone import ZoneInfo
from utils.global_conf import get_zone_conf

class ZoneBuilder():

    def __init__(self, ctx):
    
        self.ctx = ctx
        self.zones = {}
        self.zone_users = {}
        
    def load_zone(self, zone_ids=None):

        if zone_ids and not isinstance(zone_ids, list):
            zone_ids = [zone_ids]

        ret = self.ctx.pgm.get_zones(zone_ids)
        if not ret:
            if zone_ids:
                for zone_id in zone_ids:
                    if zone_id in self.zones:
                        del self.zones[zone_id]
                        del self.zone_users[zone_id]
                if self.ctx.res:
                    self.ctx.res.init_resource_adapter()
                return None

            ret = {}
        zones = ret

        if not zone_ids:
            zone_ids = zones.keys()

        for zone_id in zone_ids:

            zone_info = zones.get(zone_id)
            if not zone_info:
                if zone_id in self.zones:
                    del self.zones[zone_id]
                    del self.zone_users[zone_id]
                continue

            zone = ZoneInfo(self.ctx, zone_info)
            ret = zone.build_zone_info()
            if ret < 0:
                continue
            
            self.zone_users[zone_id] = zone.user_id
            self.zones[zone_id] = zone

        self.ctx.zones = self.zones
        self.ctx.zone_users = self.zone_users
        if self.ctx.res:
            self.ctx.res.init_resource_adapter()

        return None

    def get_base_zone(self, base_zone_id, conn):

        conn_key = ["access_key_id", "secret_access_key", "host",
                         "port", "protocol", "http_socket_timeout","account_user_id"]

        zone_conn = {}
        for key in conn_key:
            if key not in conn:
                logger.error("ZoneBuilder: key %s no foud in conn %s" % (key, conn))
                return None

            zone_conn[key] = conn[key]

        is_region = False
        ret = self.ctx.res.get_test_connection(base_zone_id, zone_conn)
        if not ret:
            logger.error("get test connection fail %s, %s" % (base_zone_id, zone_conn))
            return None

        test_handler = ret
        ret = self.ctx.res.resource_test_describe_zones(test_handler, base_zone_id)
        if not ret:
            ret = self.ctx.res.resource_test_describe_zones(test_handler, region=base_zone_id)
            is_region = True

        if not ret or not ret.get(base_zone_id):
            logger.error("resource test zone fail %s" % (base_zone_id))
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_ZONE_CONFIG_ERROR,base_zone_id)
        base_zone = ret[base_zone_id]

        #check account_user_id
        access_keys = zone_conn.get("access_key_id")
        account_user_id = zone_conn.get("account_user_id")
        ret = self.ctx.res.resource_describe_access_keys(test_handler, base_zone_id,access_keys)
        if ret:
            access_key_sets = ret
            for _, access_key_set in access_key_sets.items():
                owner = access_key_set.get("owner")
                if owner != account_user_id:
                    logger.error("account_user_id %s error" % (account_user_id))
                    return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                 ErrorMsg.ERR_MSG_ZONE_CONFIG_ACCOUNT_USER_ID_ERROR, account_user_id)

        if is_region:
            return {"zone_id": base_zone_id}

        return base_zone

    def check_account_user_id(self,base_zone_id, conn):

        conn_key = ["access_key_id", "secret_access_key", "host",
                    "port", "protocol", "http_socket_timeout", "account_user_id"]

        zone_conn = {}
        for key in conn_key:
            if key not in conn:
                logger.error("ZoneBuilder: key %s no foud in conn %s" % (key, conn))
                return None

            zone_conn[key] = conn[key]

        ret = self.ctx.res.get_test_connection(base_zone_id, zone_conn)
        if not ret:
            logger.error("get test connection fail %s, %s" % (base_zone_id, zone_conn))
            return None

        test_handler = ret

        # check account_user_id role
        account_user_id = zone_conn.get("account_user_id")
        ret = self.ctx.res.resource_describe_users(test_handler, base_zone_id, account_user_id)
        if ret:
            user_sets = ret
            for _, user_set in user_sets.items():
                role = user_set.get("role")
                if role not in const.ADMIN_ROLES:
                    logger.error("account_user_id %s is not admin role" % (account_user_id))
                    return None

        return account_user_id

    def update_zone_status(self, zone_id):
        
        zone = self.ctx.pgm.get_zone(zone_id)
        if not zone:
            logger.error("zone %s no found" % (zone_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)

        platform = zone["platform"]
        status = const.ZONE_STATUS_ACTIVE

        ret = self.ctx.pgm.get_zone_connection(zone_id)
        if not ret or ret["status"] != const.ZONE_STATUS_ACTIVE:
            logger.error("update zone %s status invaild " % zone_id)
            status = const.ZONE_STATUS_INVAILD

        if status == const.ZONE_STATUS_ACTIVE:
            if platform == const.PLATFORM_TYPE_CITRIX:
                ret = self.ctx.pgm.get_zone_citrix_connection(zone_id)
                if not ret or ret["status"] != const.ZONE_STATUS_ACTIVE:
                    logger.error("update zone %s status connection citrix invaild " % zone_id)
                    status = const.ZONE_STATUS_INVAILD

        if status == const.ZONE_STATUS_ACTIVE:
            ret = self.ctx.pgm.get_zone_auth(zone_id)
            if not ret or ret["status"] != const.ZONE_STATUS_ACTIVE:
                logger.error("update zone %s status auth service invaild " % zone_id)
                status = const.ZONE_STATUS_INVAILD

        if not self.ctx.pg.batch_update(TB_DESKTOP_ZONE, {zone_id: {"status": status}}):
            logger.error("modify zone status update DB fail %s" % zone_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        zone_info = self.ctx.zones.get(zone_id)
        if zone_info:
            zone_info.status = status

        return status

    def init_zone_storefront(self, zone_ids=None):
    
        if not self.ctx.zones:
            return None
        
        if zone_ids and not isinstance(zone_ids, list):
            zone_ids = [zone_ids]
        
        zone_store_fronts = {}
        for zone_id, zone in self.ctx.zones.items():
            if zone_ids and zone_id not in zone_ids:
                continue
            
            if zone.platform != const.PLATFORM_TYPE_CITRIX:
                continue

            # check citrix connection
            ret = self.ctx.pgm.get_zone_citrix_connection(zone_id)
            if not ret:
                logger.error("init zone storefront, no found citrix conn %s" % zone_id)
                continue
            
            citrix_connection = ret
            if not citrix_connection["storefront_uri"] and not citrix_connection["netscaler_uri"]:
                continue
            
            # check auth service
            auth_service = self.ctx.pgm.get_zone_auth(zone_id)
            if not auth_service:
                continue
    
            ret = ZoneStoreFront(self.ctx, zone_id, citrix_connection, auth_service)
            zone_store_fronts[zone_id] = ret
        
        self.ctx.zone_storefronts = zone_store_fronts
    
    def refresh_zone_builder(self, zone_ids=None):
        
        self.init_zone_storefront(zone_ids)

    def init_zone_config(self):

        zone_conf = get_zone_conf()
        if not zone_conf:
            logger.error("no found zone config")
            return -1

        # deploy
        deploy = zone_conf.get("deploy", const.DEPLOY_TYPE_STANDARD)
        if deploy not in const.SUPPORTED_DEPLOY_TYPES:
            logger.error("zone conf deploy dismatch %s" % deploy)
            return -1

        self.ctx.zone_deploy = deploy

        return 0
