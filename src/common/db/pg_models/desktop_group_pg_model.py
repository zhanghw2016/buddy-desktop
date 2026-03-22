import db.constants as dbconst

class DesktopGroupPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_desktop_group(self, desktop_group_id, extras=[dbconst.TB_DESKTOP_GROUP_NETWORK,
                                                          dbconst.TB_DESKTOP_GROUP_USER,
                                                          dbconst.TB_DESKTOP,
                                                          dbconst.TB_DESKTOP_GROUP_DISK,
                                                          dbconst.TB_DESKTOP_IMAGE]):

        desktop_group = self.pg.get(dbconst.TB_DESKTOP_GROUP, desktop_group_id)
        if desktop_group is None or len(desktop_group) == 0:
            return None
        
        conditions = dict(desktop_group_id=desktop_group_id)
        if dbconst.TB_DESKTOP_GROUP_NETWORK in extras:
            networks = {}
            network_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_NETWORK, conditions)
            if network_set is not None and len(network_set) > 0:
                for network in network_set:
                    network_id = network["network_config_id"]
                    networks[network_id] = network

            desktop_group["networks"] = networks

        if dbconst.TB_DESKTOP_GROUP_DISK in extras:
            disks = {}
            disk_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_DISK, conditions)
            if disk_set is not None and len(disk_set) > 0:
                for disk in disk_set:
                    disk_config_id = disk["disk_config_id"]
                    disks[disk_config_id] = disk
            desktop_group["disks"] = disks

        if dbconst.TB_DESKTOP_GROUP_USER in extras:
            users = {}
            user_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_USER, conditions)
            if user_set is not None and len(user_set) > 0:
                for user in user_set:
                    user_id = user["user_id"]
                    users[user_id] = user
            desktop_group["users"] = users
        
        if dbconst.TB_DESKTOP_IMAGE in extras:
            desktop_image_id = desktop_group["desktop_image_id"]
            images = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, {"desktop_image_id": desktop_image_id})
            if images:
                image = images[0]
                desktop_group["image"] = image
            else:
                desktop_group["image"] = None

        if dbconst.TB_DESKTOP in extras:
            desktops = {}
            desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
            if desktop_set is not None and len(desktop_set) > 0:
                for desktop in desktop_set:
                    desktop_id = desktop["desktop_id"]
                    desktop_disks = self.pg.base_get(dbconst.TB_DESKTOP_DISK,{"desktop_id": desktop_id})
                    if desktop_disks is not None and len(desktop_disks) > 0:
                        desktop["disks"] = desktop_disks
                    else:
                        desktop["disks"] = []
                        
                    desktop_nics = self.pg.base_get(dbconst.TB_DESKTOP_NIC, {"resource_id": desktop_id})
                    if desktop_nics is not None and len(desktop_nics) > 0:
                        desktop["nics"] = desktop_nics
                    else:
                        desktop["nics"] = []
                    
                    desktops[desktop_id] = desktop
            desktop_group["desktops"] = desktops

        return desktop_group

    def get_desktop_groups(self, desktop_group_ids=None, is_apply=None, desktop_group_type=None, columns=None, zone_id=None):
        
        conditions = {}
        if desktop_group_ids is not None:
            conditions["desktop_group_id"] = desktop_group_ids
        
        if is_apply is not None:
            conditions["is_apply"] = is_apply
        if desktop_group_type is not None:
            conditions["desktop_group_type"] = desktop_group_type
        
        if zone_id:
            conditions["zone"] = zone_id
        
        desktop_group_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP, conditions, columns=columns)
        if desktop_group_set is None or len(desktop_group_set) == 0:
            return None

        desktop_group_dict = {}
        for desktop_group in desktop_group_set:
            desktop_group_id = desktop_group["desktop_group_id"]
            desktop_group_dict[desktop_group_id] = desktop_group

        return desktop_group_dict

    def get_desktop_group_naming_rule(self, zone_id):
        
        conditions = {"zone": zone_id}

        desktop_group_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP, conditions)
        if desktop_group_set is None or len(desktop_group_set) == 0:
            return None

        naming_rules = []
        for desktop_group in desktop_group_set:
            naming_rule = desktop_group["naming_rule"]
            naming_rules.append(naming_rule.upper())

        return naming_rules

    def get_user_desktop_groups(self, user_id, desktop_group_ids=None):
        
        conditions = {
                      "user_id": user_id
                     }
        
        if desktop_group_ids:
            conditions["desktop_group_id"] = desktop_group_ids
        
        desktop_group_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_USER, conditions)
        if desktop_group_set is None or len(desktop_group_set) == 0:
            return None

        user_desktop_group = []
        for desktop_group in desktop_group_set:
            desktop_group_id = desktop_group["desktop_group_id"]
            user_desktop_group.append(desktop_group_id)

        return user_desktop_group

    def get_user_status_in_desktop_group(self, user_ids, desktop_group_id):
        
        conditions = {
                      "user_id": user_ids,
                      "desktop_group_id": desktop_group_id
                     }
        
        desktop_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_USER, conditions, ["user_id", "status"])
        if desktop_group_user_set is None or len(desktop_group_user_set) == 0:
            return None

        return desktop_group_user_set

    def get_desktop_group_users(self, desktop_group_id, need_desktop = None, user_ids=None, status=None):

        conditions = dict(desktop_group_id=desktop_group_id)
        if need_desktop:
            conditions["need_desktop"] = need_desktop
        
        if user_ids:
            conditions["user_id"] = user_ids
        
        if status:
            conditions["status"] = status

        user_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_USER, conditions)
        if user_set is None or len(user_set) == 0:
            return None

        users = {}
        for user in user_set:
            user_id = user["user_id"]
            users[user_id] = user

        return users

    def get_desktop_group_user(self, desktop_group_id, user_id):

        conditions = dict(desktop_group_id=desktop_group_id,
                          user_id=user_id)

        desktop_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_USER, conditions)
        if desktop_group_user_set is None or len(desktop_group_user_set) == 0:
            return None

        return desktop_group_user_set[0]

    def get_desktop_group_by_user(self, user_id, desktop_group_ids=None):

        conditions = dict(user_id=user_id)
        
        if desktop_group_ids:
            conditions["desktop_group_id"] = desktop_group_ids

        desktop_group_user_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_USER, conditions)
        if desktop_group_user_set is None or len(desktop_group_user_set) == 0:
            return None
        
        desktop_groups = {}
        for desktop_group in desktop_group_user_set:
            desktop_group_id = desktop_group["desktop_group_id"]
            desktop_groups[desktop_group_id] = desktop_group
        
        return desktop_groups

    def get_disk_config(self, disk_config_ids=None, desktop_group_id=None, need_update=None, disk_name=None):
        
        conditions = {}
        if disk_config_ids:
            conditions["disk_config_id"] = disk_config_ids
        
        if need_update:
            conditions["need_update"] = need_update
            
        if desktop_group_id:
            conditions["desktop_group_id"] = desktop_group_id
            
        if disk_name:
            conditions["disk_name"] = disk_name
        
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None
        
        disk_config = {}
        for disk in disk_set:
            disk_config_id = disk["disk_config_id"]
            disk_config[disk_config_id] = disk

        return disk_config

    def get_network_config(self, network_config_ids =None, desktop_group_id=None, network_type=None, network_id=None, no_range=False):
        
        conditions = {}
        if desktop_group_id:
            conditions["desktop_group_id"] = desktop_group_id

        if network_config_ids:
            conditions["network_config_id"] = network_config_ids
        
        if network_type:
            conditions["network_type"] = network_type
        
        if network_id:
            conditions["network_id"] = network_id
        
        network_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_NETWORK, conditions)
        if network_set is None or len(network_set) == 0:
            return None

        network_config = {}
        for network in network_set:
            network_config_id = network["network_config_id"]
            
            if no_range:
                start_ip = network["start_ip"]
                if start_ip:
                    continue
            
            network_config[network_config_id] = network

        return network_config

    def get_desktop_group_network(self, desktop_group_id, network_type=None, network_id=None):
        
        conditions = {}
        conditions["desktop_group_id"] = desktop_group_id
        
        if network_type is not None:
            conditions["network_type"] = network_type
        
        if network_id:
            conditions["network_id"] = network_id
        
        network_config_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_NETWORK, conditions)
        if network_config_set is None or len(network_config_set) == 0:
            return None

        network_configs = {}
        for network_config in network_config_set:
            network_config_id = network_config["network_config_id"]
            network_id = network_config["network_id"]           
            network_configs[network_id] = network_config_id

        return network_configs

    def get_desktop_group_networks(self, desktop_group_ids=None):
        
        conditions = {}
        if desktop_group_ids:
            conditions["desktop_group_id"] = desktop_group_ids
        
        network_config_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_NETWORK, conditions)
        if network_config_set is None or len(network_config_set) == 0:
            return None

        desktop_group_networks = {}
        for network_config in network_config_set:
            desktop_group_id = network_config["desktop_group_id"]
            network_id = network_config["network_id"]
            network_config_info = {}
            network_config_info[network_id] = network_config
            
            if desktop_group_id not in desktop_group_networks:
                desktop_group_networks[desktop_group_id] = {}
            
            desktop_group_networks[desktop_group_id].update(network_config)

        return desktop_group_networks

    def get_desktop_group_image(self, desktop_image_ids):
        
        conditions = dict(desktop_image_id = desktop_image_ids)

        desktop_group_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP, conditions)
        if desktop_group_set is None or len(desktop_group_set) == 0:
            return None
        
        desktop_group_ids = []
        for desktop_group in desktop_group_set:
            desktop_group_id = desktop_group["desktop_group_id"]
            desktop_group_ids.append(desktop_group_id)
        
        return desktop_group_ids
    
    def get_desktop_group_by_name(self, desktop_group_name, extras=[], zone=None):
        
        conditions = {}
        
        ret = self.pgm.get_table_ignore_case(dbconst.TB_DESKTOP_GROUP, 'desktop_group_name', desktop_group_name)
        if not ret:
            return None
        
        desktop_group_ids = []
        for desktop_group in ret:
            desktop_group_id = desktop_group["desktop_group_id"]
            desktop_group_ids.append(desktop_group_id)
        
        conditions["desktop_group_id"] = desktop_group_ids
        if zone:
            conditions["zone"] = zone
        
        desktop_group_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP, conditions)
        if desktop_group_set is None or len(desktop_group_set) == 0:
            return None
        
        desktop_group = desktop_group_set[0]
        
        if "zone" in conditions:
            del conditions["zone"]
        if dbconst.TB_DESKTOP_GROUP_DISK in extras:
            
            disks = {}
            disk_set = self.pg.base_get(dbconst.TB_DESKTOP_GROUP_DISK, conditions)
            if disk_set is not None and len(disk_set) > 0:
                for disk in disk_set:
                    disk_config_id = disk["disk_config_id"]
                    disks[disk_config_id] = disk
            desktop_group["disks"] = disks

        if dbconst.TB_DESKTOP in extras:
            desktops = {}
            desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
            if desktop_set is not None and len(desktop_set) > 0:
                for desktop in desktop_set:
                    desktop_id = desktop["desktop_id"]
                    desktop_disks = self.pg.base_get(dbconst.TB_DESKTOP_DISK,{"desktop_id": desktop_id})
                    if desktop_disks is not None and len(desktop_disks) > 0:
                        desktop["disks"] = desktop_disks
                    else:
                        desktop["disks"] = []
                    
                    desktops[desktop_id] = desktop
            desktop_group["desktops"] = desktops

        return desktop_group

