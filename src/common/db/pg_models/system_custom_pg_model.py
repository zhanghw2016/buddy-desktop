import db.constants as dbconst
import constants as const

class SystemCustomPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm


    def get_system_custom_id(self, is_default=None,current_system_custom=None):

        conditions = {}
        if is_default is not None:
            conditions["is_default"] = is_default

        if current_system_custom is not None:
            conditions["current_system_custom"] = current_system_custom

        system_custom_set = self.pg.base_get(dbconst.TB_SYSTEM_CUSTOM, conditions)
        if system_custom_set is None or len(system_custom_set) == 0:
            return None

        system_custom_id = None
        for system_custom in system_custom_set:
            system_custom_id = system_custom["system_custom_id"]

        return system_custom_id

    def get_system_custom_configs(self, system_custom_ids=None,module_type=None,item_key=None):

        conditions = {}
        if system_custom_ids:
            conditions["system_custom_id"] = system_custom_ids

        if module_type:
            conditions["module_type"] = module_type

        if item_key:
            conditions["item_key"] = item_key

        system_custom_config_set = self.pg.base_get(dbconst.TB_SYSTEM_CUSTOM_CONFIG, conditions)
        if system_custom_config_set is None or len(system_custom_config_set) == 0:
            return None

        system_custom_configs = {}
        for system_custom_config in system_custom_config_set:
            item_key = system_custom_config["item_key"]
            system_custom_configs[item_key] = system_custom_config

        return system_custom_configs

    def get_url_prefix_item_value(self, system_custom_ids=None,item_key=None):

        conditions = {}
        if system_custom_ids:
            conditions["system_custom_id"] = system_custom_ids

        if item_key:
            conditions["item_key"] = item_key

        system_custom_config_set = self.pg.base_get(dbconst.TB_SYSTEM_CUSTOM_CONFIG, conditions)
        if system_custom_config_set is None or len(system_custom_config_set) == 0:
            return None

        item_value = None
        for system_custom_config in system_custom_config_set:
            item_value = system_custom_config["item_value"]

        return item_value
    
    def get_vnc_proxy_ip(self):

        conditions = {"module_type": const.CUSTOM_MODULE_TYPE_PROTOCOL, "item_key": const.CUSTOM_ITEM_KEY_VNC_PROXY_IP, "system_custom_id": const.REDEFINE_SYSTEM_CUSTOM}

        vnc_proxy_set = self.pg.base_get(dbconst.TB_SYSTEM_CUSTOM_CONFIG, conditions)
        if vnc_proxy_set is None or len(vnc_proxy_set) == 0:
            return None

        vnc_proxy = vnc_proxy_set[0]
        port_ips = {}
        
        item_value = vnc_proxy["item_value"]
        if not item_value:
            return None
        
        ip_port_list = item_value.split(",")
        for ip_port in ip_port_list:
            
            ip_port_value = ip_port.split(":")
            if len(ip_port_value) < 3:
                continue
            zone_id = ip_port_value[0]
            _port = ip_port_value[1]
            _ip = ip_port_value[2]
            
            if zone_id not in port_ips:
                port_ips[zone_id] = {}

            port_ips[zone_id].update({str(_port): _ip})
        
        return port_ips

    def get_default_security_ipset_port(self, ipset_configs):
        
        conditions = {"module_type": const.IPSET_PORT_CONFIG, "item_key": ipset_configs}
        
        ipset_set = self.pg.base_get(dbconst.TB_SYSTEM_CUSTOM_CONFIG, conditions)
        if ipset_set is None or len(ipset_set) == 0:
            return None

        default_ipsets = {}
        for ipset in ipset_set:
            item_key = ipset["item_key"]
            item_value = ipset["item_value"]
            default_ipsets[item_key] = item_value

        return default_ipsets
        

