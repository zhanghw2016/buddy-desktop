import db.constants as dbconst

class DiskPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    # volume
    def get_desktop_disks(self, desktop_ids):

        desktop_disk = {}
        conditions = {}
        conditions["desktop_id"] = desktop_ids

        
        if not conditions:
            return None
        
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None

        for disk in disk_set:
            desktop_id = disk["desktop_id"]
           
            if desktop_id not in desktop_disk:
                desktop_disk[desktop_id] = []

            desktop_disk[desktop_id].append(disk)

        return desktop_disk

    def get_desktop_disk(self, desktop_ids, need_update=None, status=None, disk_ids=None, has_volume=False, no_volume=False, disk_config_ids=None):
        
        if not desktop_ids:
            return None

        if not isinstance(desktop_ids, list):
            desktop_ids = [desktop_ids]

        desktop_disk = {}
        conditions = dict(desktop_id = desktop_ids)
        if disk_config_ids:
            conditions["disk_config_id"] = disk_config_ids
        
        if need_update is not None:
            conditions["need_update"] = need_update
        
        if status is not None:
            conditions["status"] = status
        
        if disk_ids is not None:
            conditions["disk_id"] = disk_ids

        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None

        for disk in disk_set:
            disk_id = disk["disk_id"]
            desktop_id = disk["desktop_id"]
            volume_id = disk["volume_id"]
            if has_volume and not volume_id:
                continue
            
            if no_volume and volume_id:
                continue

            if desktop_id not in desktop_disk:
                desktop_disk[desktop_id] = []
            desktop_disk[desktop_id].append(disk_id)
        
        return desktop_disk

    def get_disk_desktop(self, disk_ids, status=None):

        disk_desktop = {}
        conditions = dict(disk_id = disk_ids)
        
        if status:
            conditions["status"] = status

        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None
        
        for disk in disk_set:
            disk_id = disk["disk_id"]
            desktop_id = disk["desktop_id"]
            if not desktop_id:
                continue
            
            if desktop_id not in disk_desktop:
                disk_desktop[desktop_id] = []
            disk_desktop[desktop_id].append(disk_id)

        return disk_desktop

    def get_disk_desktops(self, disk_ids, status=None, need_update=None):

        disk_desktop = {}
        conditions = dict(disk_id = disk_ids)
        
        if status:
            conditions["status"] = status
        
        if need_update:
            conditions["need_update"] = need_update

        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None
        
        for disk in disk_set:
            desktop_id = disk["desktop_id"]
            if not desktop_id:
                continue
            
            if desktop_id not in disk_desktop:
                disk_desktop[desktop_id] = []
            disk_desktop[desktop_id].append(disk)

        return disk_desktop

    def get_desktop_group_disk(self, desktop_group_id, need_update=None, has_desktop=False, status=None):
        
        conditions = dict(desktop_group_id = desktop_group_id)
        if need_update is not None:
            conditions["need_update"] = need_update
        
        if status:
            conditions["status"] = status
        
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None

        disks = {}
        for disk in disk_set:
            disk_id = disk["disk_id"]
            desktop_id = disk["desktop_id"]

            if has_desktop and not desktop_id:
                continue

            disks[disk_id] = disk

        return disks

    def get_disks(self, disk_ids=None, desktop_group_ids=None, disk_config_ids=None, need_update=None, status=None, desktop_ids=None, user_ids=None):
        
        conditions = {}
        if disk_ids is not None:
            conditions["disk_id"] = disk_ids
        
        if desktop_group_ids is not None:
            conditions["desktop_group_id"] = desktop_group_ids
        
        if disk_config_ids:
            conditions["disk_config_id"] = disk_config_ids
        
        if need_update is not None:
            conditions["need_update"] = need_update
        
        if status:
            conditions["status"] = status
            
        if desktop_ids:
            conditions["desktop_id"] = desktop_ids
        
        if user_ids:
            ret = self.pgm.get_resource_by_user(user_ids, disk_ids, resource_type=dbconst.RESTYPE_DESKTOP_DISK)
            if not ret:
                return None
            user_disks = []
            for _, disk_ids in ret.items():
                user_disks.extend(disk_ids)

            conditions["disk_id"] = user_disks
        
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None

        desktop_disk = {}
        for disk in disk_set:
            
            disk_id = disk["disk_id"]

            desktop_disk[disk_id] = disk

        return desktop_disk

    def get_disk_config_disk(self, disk_config_ids):

        conditions = dict(disk_config_id=disk_config_ids)
        
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None
        
        disk_dict = {}
        for disk in disk_set:
            disk_id = disk["disk_id"]
            disk_dict[disk_id] = disk

        return disk_dict
    
    def get_disk_volume(self, disk_ids=None, has_volume=True, no_volume=False, need_update=None, desktop_ids=None):

        conditions = {}
        
        if disk_ids:
            conditions["disk_id"] = disk_ids
        
        if need_update:
            conditions["need_update"] = need_update
        
        if desktop_ids:
            conditions["desktop_id"] = desktop_ids
        
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None
        
        disk_volume = {}
        for disk in disk_set:
            disk_id = disk["disk_id"]
            volume_id = disk["volume_id"]
            if has_volume and not volume_id:
                continue
            
            if no_volume and volume_id:
                continue
            
            disk_volume[disk_id] = volume_id

        return disk_volume
    
    def get_desktop_volume(self, desktop_id, disk_config_id=None):

        conditions = dict(desktop_id=desktop_id)
        if disk_config_id:
            conditions["disk_config_id"] = disk_config_id
        
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None
        
        volume_ids = []
        for disk in disk_set:
            volume_id = disk["volume_id"]
            if not volume_id:
                continue
            volume_ids.append(volume_id)

        return volume_ids

    def get_desktop_volumes(self, desktop_id, volume_ids=None):

        conditions = dict(desktop_id=desktop_id)
        if volume_ids:
            conditions["volume_id"] = volume_ids
        
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None
        
        disk_volumes = {}
        for disk in disk_set:
            volume_id = disk["volume_id"]
            if not volume_id:
                continue
            disk_volumes[volume_id] = disk

        return disk_volumes

    def get_disk(self, disk_id):
        
        conditions = {}
        conditions["disk_id"] = disk_id
        disk_set = self.pg.base_get(dbconst.TB_DESKTOP_DISK, conditions)
        if disk_set is None or len(disk_set) == 0:
            return None
        
        return disk_set[0]

