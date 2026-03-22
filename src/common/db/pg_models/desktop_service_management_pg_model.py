import db.constants as dbconst
import constants as const
from log.logger import logger

class DesktopServiceManagementPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_desktop_service_managements(self, service_ids=None,service_node_type=None,service_type=None,service_node_ids=None,service_management_type=None,service_node_ips=None,service_version=None):

        conditions = {}

        if service_ids:
            conditions["service_id"] = service_ids

        if service_node_type:
            conditions["service_node_type"] = service_node_type

        if service_type:
            conditions["service_type"] = service_type

        if service_node_ids:
            conditions["service_node_id"] = service_node_ids

        if service_node_ips:
            conditions["service_node_ip"] = service_node_ips

        if service_management_type:
            conditions["service_management_type"] = service_management_type

        if service_version:
            conditions["service_version"] = service_version

        desktop_service_management_set = self.pg.base_get(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions)
        if desktop_service_management_set is None or len(desktop_service_management_set) == 0:
            return None

        desktop_service_managements = {}
        for desktop_service_management in desktop_service_management_set:
            service_node_id = desktop_service_management["service_node_id"]
            desktop_service_managements[service_node_id] = desktop_service_management

        return desktop_service_managements

    def get_desktop_services(self):

        conditions = {}
        conditions["service_type"] = const.LOADBALANCER_SERVICE_TYPE
        conditions["service_node_status"] = const.SERVICE_STATUS_ACTIVE
        columns = ["service_node_id", "service_node_ip", "service_node_name"]

        desktop_service_management_set = self.pg.base_get(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, 
                                                          conditions,
                                                          columns=columns)
        if desktop_service_management_set is None or len(desktop_service_management_set) == 0:
            return None

        desktop_service_ips = []
        for desktop_service_management in desktop_service_management_set:
            desktop_service_ip = desktop_service_management.get("service_node_ip")
            if desktop_service_ip:
                desktop_service_ips.append(desktop_service_ip)

        return desktop_service_ips

    def get_desktop_service_management_vnas_server_status(self):

        conditions = {}

        conditions["service_type"] = const.S2SERVER_SERVICE_TYPE

        desktop_service_management_set = self.pg.base_get(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions)
        if desktop_service_management_set is None or len(desktop_service_management_set) == 0:
            return None

        status = None
        for desktop_service_management in desktop_service_management_set:
            status = desktop_service_management["status"]

        return status

    def get_desktop_service_management_service_node_ip(self, service_type=None, service_node_name=None):

        conditions = {}

        if service_type:
            conditions["service_type"] = service_type

        if service_node_name:
            conditions["service_node_name"] = service_node_name

        logger.info("get_desktop_service_management_service_node_ip conditions == %s" %(conditions))
        desktop_service_management_set = self.pg.base_get(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions)
        if desktop_service_management_set is None or len(desktop_service_management_set) == 0:
            return None

        service_node_ips = []
        for desktop_service_management in desktop_service_management_set:
            service_node_ip = desktop_service_management["service_node_ip"]
            if service_node_ip not in service_node_ips:
                service_node_ips.append(service_node_ip)

        return service_node_ips


