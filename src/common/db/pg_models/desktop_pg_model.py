
import db.constants as dbconst

class DesktopPGModel():
    ''' VDI model for complicated requests '''

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_desktops(self, desktop_ids=None, need_update=None, status=None, desktop_group_ids=None, 
                     owner=None, is_global_admin=False, has_instance=False, has_disk=False, desktop_image_ids=None,
                     delivery_group_id=None, zone=None, in_domain=None,hostname=None):

        conditions = {}
        if desktop_ids:
            conditions["desktop_id"] = desktop_ids
        
        if status is not None:
            conditions["status"] = status

        if desktop_group_ids is not None:
            conditions["desktop_group_id"] = desktop_group_ids
        
        if need_update is not None:
            conditions["need_update"] = need_update
            
        if owner:
            ret = self.get_resource_by_user(owner, desktop_ids, resource_type=dbconst.RESTYPE_DESKTOP)
            if not ret:
                return None
            user_desktops = []
            for _, desk_ids in ret.items():
                user_desktops.extend(desk_ids)

            conditions["desktop_id"] = user_desktops
        
        if delivery_group_id:
            conditions["delivery_group_id"] = delivery_group_id
        
        if desktop_image_ids:
            conditions["desktop_image_id"] = desktop_image_ids
        
        if zone:
            conditions["zone"] = zone

        if in_domain:
            conditions["in_domain"] = in_domain

        if hostname is not None:
            conditions["hostname"] = hostname
        
        if not conditions and not is_global_admin:
            return None
        
        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktops = {}
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            instance_id = desktop["instance_id"]
            if has_instance and not instance_id:
                continue
            
            if has_disk:
                disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, {"desktop_id": desktop_id})
                if not disk_set:
                    disk_set = []
                
                desktop["disks"] = disk_set
                    
            desktops[desktop_id] = desktop
            
        return desktops

    def get_desktop_name(self, desktop_ids):

        conditions = {}
        conditions["desktop_id"] = desktop_ids

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None
        
        desktop_name = {}
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            hostname = desktop["hostname"]
            desktop_name[desktop_id] = hostname

        return desktop_name
    
    def get_zone_desktops(self, zone_id):
        
        conditions = {}
        conditions["zone"] = zone_id

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        return desktop_set

    def get_desktop_hostname(self, is_upper=True):

        conditions = {}

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        hostnames = []
        for desktop in desktop_set:
            hostname = desktop["hostname"]
            if is_upper:
                hostnames.append(hostname.upper())
            else:
                hostnames.append(hostname)

        return hostnames

    def get_desktop_instance(self, desktop_ids, has_instance=True, no_instance=False, need_update=None):

        if not desktop_ids:
            return None

        conditions = {}
        conditions["desktop_id"] = desktop_ids
        
        if need_update:
            conditions["need_update"] = need_update
        
        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktop_instance = {}
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            instance_id = desktop["instance_id"]
            if has_instance:
                if instance_id:
                    desktop_instance[desktop_id] = instance_id           
            elif no_instance:
                if not instance_id:
                    desktop_instance[desktop_id] = instance_id
            else:
                desktop_instance[desktop_id] = instance_id

        return desktop_instance

    def get_instance_desktop(self, instance_ids):

        if not instance_ids:
            return None

        conditions = {}
        conditions["instance_id"] = instance_ids
        
        desktop_set = self.pg.get_all(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        instance_desktop = {}
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            instance_id = desktop["instance_id"]
            instance_desktop[instance_id] = desktop_id

        return instance_desktop

    def get_all_desktops(self, zone_id, desktop_ids=None):

        conditions = {"zone": zone_id}
        if desktop_ids:
            conditions["desktop_id"] = desktop_ids
        
        desktop_set = self.pg.get_all(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktops = {}
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            desktops[desktop_id] = desktop

        return desktops

    def get_free_random_desktops(self, desktop_group_id=None, desktop_ids=None):
        
        conditions = {}
        if desktop_group_id:
            conditions["desktop_group_id"] = desktop_group_id
            
        if desktop_ids:
            conditions["desktop_id"] = desktop_ids

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None
        
        desktop_ids = []
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            desktop_ids.append(desktop_id)
        
        resource_users = self.pgm.get_resource_user_ids(desktop_ids)
        if not resource_users:
            resource_users = {}
        
        random_desktop = {}
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]

            trans_status = desktop["transition_status"]
            if trans_status:
                continue

            if desktop_id not in resource_users:
                random_desktop[desktop_id] = desktop

        return random_desktop

    def get_group_by_desktop(self, desktop_ids):

        conditions = {"desktop_id": desktop_ids}

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktop_group_index = {}
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            desktop_group_id = desktop["desktop_group_id"]
            if desktop_group_id not in desktop_group_index:
                desktop_group_index[desktop_group_id] = []
            desktop_group_index[desktop_group_id].append(desktop_id)

        return desktop_group_index
    
    def get_user_desktop(self, desktop_group_id, user_ids):

        conditions = dict(
                          desktop_group_id = desktop_group_id,
                          )

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None
        
        desktop_ids = []
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            desktop_ids.append(desktop_id)
        
        user_desktops = self.pgm.get_resource_by_user(user_ids, desktop_ids)
        if not user_desktops:
            user_desktops = {}

        return user_desktops

    def get_desktop_user(self, desktop_ids):
        
        if not desktop_ids:
            return None
        
        conditions = dict(desktop_id = desktop_ids)

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktop_user = {}
        for desktop in desktop_set:
            user_id = desktop.get("owner") # sync old version to new
            if not user_id:
                continue
            desktop_id = desktop["desktop_id"]
            desktop_user[desktop_id] = user_id

        return desktop_user

    def get_desktop_owner(self, desktop_ids):
        
        if not desktop_ids:
            return None
        
        conditions = dict(desktop_id = desktop_ids)

        desktop_set = self.pg.get_all(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktop_user = {}
        for desktop in desktop_set:
            user_id = desktop.get("owner") # sync old version to new
            if not user_id:
                continue
            desktop_id = desktop["desktop_id"]
            desktop_user[desktop_id] = user_id

        return desktop_user

    def get_desktop_group_hostname(self, desktop_group_id):
        desktop_hostname = {}

        conditions = dict(desktop_group_id = desktop_group_id)
        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            hostname = desktop["hostname"]
            if not hostname:
                continue

            desktop_hostname[desktop_id] = hostname
  
        return desktop_hostname
    
    def get_user_desktops(self, desktop_group_id, user_ids):

        conditions = {}
        conditions["desktop_group_id"] = desktop_group_id
        
        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None
        
        desktop_ids = []
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            desktop_ids.append(desktop_id)
        
        user_desktops = self.pgm.get_resource_by_user(user_ids, desktop_ids)
        if not user_desktops:
            user_desktops = {}
            
        return user_desktops
    
    def format_user_desktop(self, desktop, desktop_group_name):
        avail_key = ["desktop_id", "hostname", "status", "transition_status", "desktop_group_id", "create_time"]

        fort_desktop = {}
        for dsk_key, dsk_value in desktop.items():
            if dsk_key not in avail_key:
                continue
            if dsk_key == "desktop_group_id":
                if dsk_value not in desktop_group_name:
                    dg_name = self.get_desktop_name(dsk_value)
                    if not dg_name:
                        continue
                    desktop_group_name.update(dg_name)
                dg_name = desktop_group_name[dsk_value]
                fort_desktop["desktop_group_name"] = dg_name

            fort_desktop[dsk_key] = dsk_value
    
        return fort_desktop

    def format_user_disk(self, disk, desktop_group_name):
        avail_key = ["disk_id", "volume_id", "disk_type", "status", "transition_status", "desktop_group_id", "create_time", "size", "disk_name"]

        fort_disk = {}
        for disk_key, disk_value in disk.items():
            if disk_key not in avail_key:
                continue
            if disk_key == "desktop_group_id":
                if disk_value not in desktop_group_name:
                    dg_name = self.get_desktop_name(disk_value)
                    if not dg_name:
                        continue
                    desktop_group_name.update(dg_name)
                dg_name = desktop_group_name[disk_value]
                fort_disk["desktop_group_name"] = dg_name

            fort_disk[disk_key] = disk_value

        return fort_disk

    def format_user_nics(self, nics):
        avail_key = ["nic_id", "network_type", "status", "transition_status", "private_ip", "network_id"]

        fort_nics = []
        for nic in nics:
            fort_nic = {}
            for nic_key, nic_value in nic.items():
                if nic_key not in avail_key:
                    continue
                fort_nic[nic_key] = nic_value
            fort_nics.append(fort_nic)

        return fort_nics
        
    def get_desktop(self, desktop_id, disk_update=None):

        conditions = {"desktop_id": desktop_id}
        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktop = desktop_set[0]
        
        disks = {}
        if disk_update is not None:
            conditions["need_update"] = disk_update

        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set:
            for disk in disk_set:
                disk_id = disk["disk_id"]
                disks[disk_id] = disk
        desktop["disks"] = disks
        
        conditions = {"resource_id": desktop_id}
        nics = {}
        nic_set = self.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions)
        if nic_set:
            for nic in nic_set:
                nic_id = nic["nic_id"]
                nics[nic_id] = nic
            
            desktop["nics"] = nics
        
        return desktop

    def get_desktop_by_hostnames(self, hostnames, zone_id=None):
        
        conditions = {"hostname": hostnames}
        if zone_id:
            conditions["zone"] = zone_id
        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktops= {}
        for desktop in desktop_set:
            hostname = desktop["hostname"]
            desktops[hostname] = desktop
        
        return desktops

    def get_group_desktop_name(self, desktop_group_id=None, delivery_group_id=None):
        
        conditions ={}
        if desktop_group_id:
            conditions["desktop_group_id"] = desktop_group_id
        if delivery_group_id:
            conditions["delivery_group_id"] = delivery_group_id
        
        if not conditions:
            return None

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktops = {}
        for desktop in desktop_set:
            hostname = desktop["hostname"]
            desktops[hostname] = desktop
            
        return desktops

    def get_instance_class_disk_type(self, zone_deploy=None, instance_class=None):

        conditions = {}
        if zone_deploy is not None:
            conditions["zone_deploy"] = zone_deploy
        if instance_class is not None:
            conditions["instance_class"] = instance_class

        instance_class_disk_type_set = self.pg.base_get(dbconst.TB_INSTANCE_CLASS_DISK_TYPE, conditions)
        if instance_class_disk_type_set is None or len(instance_class_disk_type_set) == 0:
            return None

        instance_class_disk_types = {}
        for instance_class_disk_type in instance_class_disk_type_set:
            instance_class_key = instance_class_disk_type["instance_class_key"]
            instance_class_disk_types[instance_class_key] = instance_class_disk_type

        return instance_class_disk_types

    def get_gpu_class_type(self, gpu_class_key=None,gpu_class=None, zone_id=None):

        conditions = {}
        if gpu_class_key is not None:
            conditions["gpu_class_key"] = gpu_class_key

        if gpu_class is not None:
            conditions["gpu_class"] = gpu_class
        
        if zone_id:
            conditions["zone_id"] = zone_id

        gpu_class_type_set = self.pg.base_get(dbconst.TB_GPU_CLASS_TYPE, conditions)
        if gpu_class_type_set is None or len(gpu_class_type_set) == 0:
            return None

        gpu_class_types = {}
        for gpu_class_type in gpu_class_type_set:
            gpu_class_key = gpu_class_type["gpu_class_key"]
            gpu_class_types[gpu_class_key] = gpu_class_type

        return gpu_class_types
    
    def get_resource_users(self, resource_ids, is_sync=None, user_ids = None):
        
        if not resource_ids:
            return None
        
        conditions ={"resource_id": resource_ids}
        if is_sync is not None:
            conditions["is_sync"] = is_sync
        
        if user_ids:
            conditions["user_id"] = user_ids

        if not conditions:
            return None

        resource_user_set = self.pg.base_get(dbconst.TB_RESOURCE_USER, conditions)
        if resource_user_set is None or len(resource_user_set) == 0:
            return None

        resource_users = {}
        for resource_user in resource_user_set:
            resource_id = resource_user["resource_id"]
            if resource_id not in resource_users:
                resource_users[resource_id] = []
            resource_users[resource_id].append(resource_user)

        return resource_users

    def get_resource_user(self, resource_id, is_sync=None, user_ids = None):
        
        if not resource_id:
            return None
        
        conditions ={"resource_id": resource_id}
        if is_sync is not None:
            conditions["is_sync"] = is_sync
        
        if user_ids:
            conditions["user_id"] = user_ids

        if not conditions:
            return None

        resource_user_set = self.pg.base_get(dbconst.TB_RESOURCE_USER, conditions)
        if resource_user_set is None or len(resource_user_set) == 0:
            return None

        resource_users = []
        for resource_user in resource_user_set:
            resource_id = resource_user["resource_id"]
            user_id = resource_user["user_id"]
            resource_users.append(user_id)

        return resource_users

    def get_resource_user_ids(self, resource_ids, user_ids = None):
        
        if not resource_ids:
            return None
        
        conditions ={"resource_id": resource_ids}

        if user_ids:
            conditions["user_id"] = user_ids

        if not conditions:
            return None

        resource_user_set = self.pg.base_get(dbconst.TB_RESOURCE_USER, conditions)
        if resource_user_set is None or len(resource_user_set) == 0:
            return None

        resource_users = {}
        for resource_user in resource_user_set:
            resource_id = resource_user["resource_id"]
            user_id = resource_user["user_id"]
            if resource_id not in resource_users:
                resource_users[resource_id] = []
            resource_users[resource_id].append(user_id)

        return resource_users

    def get_resource_by_user(self, user_ids, resource_ids = None, resource_type=None):
        
        if not user_ids:
            return None
        
        conditions ={"user_id": user_ids}
        if resource_ids:
            conditions["resource_id"] = resource_ids
        
        if resource_type:
            conditions["resource_type"] = resource_type
        
        resource_user_set = self.pg.base_get(dbconst.TB_RESOURCE_USER, conditions)
        if resource_user_set is None or len(resource_user_set) == 0:
            return None

        resource_users = {}
        for resource_user in resource_user_set:
            resource_id = resource_user["resource_id"]
            user_id = resource_user["user_id"]
            if user_id not in resource_users:
                resource_users[user_id] = []
            resource_users[user_id].append(resource_id)

        return resource_users

    def get_desktop_zone(self, desktop_id):
        ''' get desktop zone by desktop_id '''
        columns = ["zone"]
        try:
            result = self.pg.get(dbconst.TB_DESKTOP, 
                                desktop_id, 
                                columns)
            if not result or len(result) == 0:
                return None
        except Exception:
            return None

        return result['zone']

    def get_desktop_image_id(self, desktop_ids):
        conditions = {}
        conditions["desktop_id"] = desktop_ids

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktop_image_id = None
        for desktop in desktop_set:
            desktop_image_id = desktop["desktop_image_id"]

        return desktop_image_id

    def get_desktop_image_os_version(self, desktop_image_ids):
        conditions = {}
        conditions["desktop_image_id"] = desktop_image_ids

        desktop_image_set = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, conditions)
        if desktop_image_set is None or len(desktop_image_set) == 0:
            return None

        os_version = 'Windows10'
        for desktop_image in desktop_image_set:
            os_version = desktop_image["os_version"]

        return os_version
