import db.constants as dbconst

class NicPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_resource_nics(self, resource_ids, need_update=None, nic_ids=None, status=None):

        if not resource_ids:
            return None

        conditions = dict(resource_id=resource_ids)
        if need_update:
            conditions["need_update"] = need_update
        
        if status:
            conditions["status"] = status

        if nic_ids:
            conditions["nic_id"] = nic_ids

        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        resource_nic = {}
        for nic in nic_set:
            resource_id = nic["resource_id"]
            nic_id = nic["nic_id"]
            if resource_id not in resource_nic:
                resource_nic[resource_id] = {nic_id: nic}
            else:
                resource_nic[resource_id].update({nic_id: nic})

        return resource_nic

    def get_network_nics(self, network_ids, status=None, private_ips=None, is_free=False, desktop_group_id=None):

        conditions = dict(network_id=network_ids)
        if status:
            conditions["status"] = status
        if private_ips:
            conditions["private_ip"] = private_ips
        
        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        nics = {}
        for nic in nic_set:
            nic_id = nic["nic_id"]
            resource_id = nic["resource_id"]
            group_id = nic["desktop_group_id"]
            if is_free:
                if resource_id:
                    continue
                if group_id and group_id != desktop_group_id:
                    continue

            nics[nic_id] = nic

        return nics

    def get_nics(self, nic_ids=None, desktop_group_id=None, is_free=False, desktop_ids=None, need_update=None, status=None, network_id=None):

        conditions = {}

        if nic_ids:
            conditions["nic_id"] = nic_ids

        if desktop_group_id:
            conditions["desktop_group_id"] = desktop_group_id
        
        if desktop_ids:
            conditions["resource_id"] = desktop_ids
            
        if need_update:
            conditions["need_update"] = need_update
        
        if status:
            conditions["status"] = status

        if network_id:
            conditions["network_id"] = network_id

        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        nics = {}
        for nic in nic_set:
            nic_id = nic["nic_id"]
            resource_id = nic["resource_id"]
            group_id = nic["desktop_group_id"]
            if is_free:
                if resource_id:
                    continue
                if group_id and group_id != desktop_group_id:
                    continue

            nics[nic_id] = nic

        return nics

    def get_nic_by_private_ip(self, network_id, private_ips, is_free=False, is_alloc=False, desktop_group_id=None):
        
        if not private_ips:
            return None
        
        conditions = dict(
                          network_id=network_id,
                          private_ip = private_ips
                          )
        
        if desktop_group_id:
            conditions["desktop_group_id"] = desktop_group_id

        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        nics = {}
        for nic in nic_set:
            nic_id = nic["nic_id"]
            
            desktop_group_id = nic["desktop_group_id"]
            resource_id = nic["resource_id"]
            if is_free:
                if desktop_group_id or resource_id:
                    continue
            
            if is_alloc:
                if not desktop_group_id and not resource_id:
                    continue

            nics[nic_id] = nic

        return nics

    def get_private_ips(self, network_id, private_ips, is_free=False, is_alloc=False, desktop_group_id=None):
        
        if not private_ips:
            return None
        
        conditions = dict(
                          network_id=network_id,
                          private_ip = private_ips
                          )
        
        if desktop_group_id:
            conditions["desktop_group_id"] = desktop_group_id

        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        private_ips = {}
        for nic in nic_set:
            private_ip = nic["private_ip"]
            desktop_group_id = nic["desktop_group_id"]
            resource_id = nic["resource_id"]
            if is_free:
                if desktop_group_id or resource_id:
                    continue
            
            if is_alloc:
                if not desktop_group_id and not resource_id:
                    continue

            private_ips[private_ip] = nic

        return private_ips

    def get_network_config_nics(self, network_config_ids, status=None, has_resource=False):

        conditions = dict(network_config_id=network_config_ids)
        if status:
            conditions["status"] = status

        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        nics = {}
        for nic in nic_set:
            nic_id = nic["nic_id"]
            resource_id = nic["resource_id"]
            if has_resource and not resource_id:
                continue

            nics[nic_id] = nic

        return nics

    def get_desktop_nics(self, resource_ids, need_update=None, network_type=None, network_id=None, status=None):
        
        if not resource_ids:
            return None
        
        conditions = dict(resource_id=resource_ids)

        if need_update:
            conditions["need_update"] = need_update
        if network_type is not None:
            conditions["network_type"] = network_type
        if network_id:
            conditions["network_id"] = network_id
        if status:
            conditions["status"] = status
            
        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        desktop_nic = {}
        for nic in nic_set:
            resource_id = nic["resource_id"]
            
            if resource_id not in desktop_nic:
                desktop_nic[resource_id] = []
            desktop_nic[resource_id].append(nic)

        return desktop_nic

    def get_desktop_group_nics(self, desktop_group_id, network_type=None, network_id=None, is_free=False, status=None):

        conditions = dict(
                          desktop_group_id = desktop_group_id,
                         )

        if network_type:
            conditions["network_type"] = network_type

        if network_id:
            conditions["network_id"] = network_id
        
        if status:
            conditions["status"] = status
        
        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        nics = {}
        for nic in nic_set:
            nic_id = nic["nic_id"]
            resource_id = nic["resource_id"]
            if is_free and resource_id:
                continue
            
            nics[nic_id] = nic

        return nics

    def get_nic_desktop(self, desktop_ids, need_update=None, network_id=None, status=None):

        conditions = dict(
                          resource_id=desktop_ids
                          )
        
        if need_update:
            conditions["need_update"] = need_update
        
        if network_id:
            conditions["network_id"] = network_id
        
        if status:
            conditions["status"] = status
        
        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set is None or len(nic_set) == 0:
            return None

        nics = {}
        for nic in nic_set:
            nic_id = nic["nic_id"]
            nics[nic_id] = nic

        return nics


    