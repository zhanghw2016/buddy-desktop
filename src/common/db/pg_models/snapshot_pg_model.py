
import db.constants as dbconst

from log.logger import logger
import context
class SnapshotPGModel():
    ''' VDI model for complicated requests '''

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_desktop_snapshots(self, snapshot_ids=None, desktop_snapshot_ids=None, desktop_resource_ids=None,status=None,snapshot_type=None):

        conditions = {}
        if snapshot_ids:
            conditions["snapshot_id"] =  snapshot_ids
        
        if desktop_snapshot_ids:
            conditions["desktop_snapshot_id"] = desktop_snapshot_ids

        if desktop_resource_ids:
            conditions["desktop_resource_id"] = desktop_resource_ids

        if status:
            conditions["status"] = status

        if snapshot_type is not None:
            conditions["snapshot_type"] = snapshot_type

        desktop_snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if desktop_snapshot_set is None or len(desktop_snapshot_set) == 0:
            return None

        desktop_snapshots = {}
        for desktop_snapshot in desktop_snapshot_set:
            snapshot_id = desktop_snapshot["snapshot_id"]
            desktop_snapshots[snapshot_id] = desktop_snapshot

        return desktop_snapshots

    def get_snapshot_resources(self, snapshot_ids=None,desktop_snapshot_ids = None,snapshot_group_snapshot_ids=None,resource_ids = None,desktop_resource_ids = None):

        conditions = {}
        if desktop_snapshot_ids:
            conditions["desktop_snapshot_id"] = desktop_snapshot_ids

        if snapshot_ids:
            conditions["snapshot_id"] = snapshot_ids

        if snapshot_group_snapshot_ids:
            conditions["snapshot_group_snapshot_id"] = snapshot_group_snapshot_ids

        if resource_ids:
            conditions["resource_id"] = resource_ids

        if desktop_resource_ids:
            conditions["desktop_resource_id"] = desktop_resource_ids

        snapshot_resource_set = self.pg.base_get(dbconst.TB_SNAPSHOT_RESOURCE, conditions)
        if snapshot_resource_set is None or len(snapshot_resource_set) == 0:
            return None

        snapshot_resources = {}
        for snapshot_resource in snapshot_resource_set:
            desktop_resource_id = snapshot_resource["desktop_resource_id"]
            snapshot_resources[desktop_resource_id] = snapshot_resource

        return snapshot_resources

    def get_snapshot_groups(self, snapshot_group_ids=None, zone_id=None):

        conditions = {}
        if snapshot_group_ids:
            conditions["snapshot_group_id"] = snapshot_group_ids
        
        if zone_id:
            conditions["zone"] = zone_id

        snapshot_group_set = self.pg.base_get(dbconst.TB_SNAPSHOT_GROUP, conditions)
        if snapshot_group_set is None or len(snapshot_group_set) == 0:
            return None

        snapshot_groups = {}
        for snapshot_group in snapshot_group_set:
            snapshot_group_id = snapshot_group["snapshot_group_id"]
            snapshot_groups[snapshot_group_id] = snapshot_group

        return snapshot_groups

    def get_snapshot_group(self, snapshot_group_id):

        conditions = {"snapshot_group_id": snapshot_group_id}

        snapshot_group_set = self.pg.base_get(dbconst.TB_SNAPSHOT_GROUP, conditions)
        if snapshot_group_set is None or len(snapshot_group_set) == 0:
            return None

        return snapshot_group_set[0]

    def get_snapshot_group_resources(self, snapshot_group_id=None, desktop_resource_ids=None):

        conditions = {}
        if snapshot_group_id:
            conditions["snapshot_group_id"] = snapshot_group_id
        
        if desktop_resource_ids:
            conditions["desktop_resource_id"] = desktop_resource_ids

        snapshot_group_resource_set = self.pg.base_get(dbconst.TB_SNAPSHOT_GROUP_RESOURCE, conditions)
        if snapshot_group_resource_set is None or len(snapshot_group_resource_set) == 0:
            return None

        snapshot_group_resources = {}
        for snapshot_group_resource in snapshot_group_resource_set:
            desktop_resource_id = snapshot_group_resource["desktop_resource_id"]
            snapshot_group_resources[desktop_resource_id] = snapshot_group_resource

        return snapshot_group_resources

    def get_snapshot_group_snapshots(self, snapshot_group_id=None, snapshot_group_snapshot_id=None):

        conditions = {}
        if snapshot_group_id:
            conditions["snapshot_group_id"] = snapshot_group_id

        if snapshot_group_snapshot_id:
            conditions["snapshot_group_snapshot_id"] = snapshot_group_snapshot_id

        snapshot_group_snapshot_set = self.pg.base_get(dbconst.TB_SNAPSHOT_GROUP_SNAPSHOT, conditions)
        if snapshot_group_snapshot_set is None or len(snapshot_group_snapshot_set) == 0:
            return None

        snapshot_group_snapshots = {}
        for snapshot_group_snapshot in snapshot_group_snapshot_set:
            snapshot_group_snapshot_id = snapshot_group_snapshot["snapshot_group_snapshot_id"]
            snapshot_group_snapshots[snapshot_group_snapshot_id] = snapshot_group_snapshot

        return snapshot_group_snapshots

    def get_desktop_snapshot_id_from_snapshot_id(self, snapshot_id):

        conditions = {}
        conditions["snapshot_id"] = snapshot_id

        snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if snapshot_set is None or len(snapshot_set) == 0:
            return None

        for snapshot in snapshot_set:
            desktop_snapshot_id = snapshot.get("desktop_snapshot_id")

        return desktop_snapshot_id

    def get_snapshot_id_from_parent_id(self, parent_id=None):

        conditions = {}
        snapshot_id = None

        if parent_id:
            conditions["parent_id"] = parent_id

        snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if snapshot_set is None or len(snapshot_set) == 0:
            return None

        for snapshot in snapshot_set:
            snapshot_id = snapshot.get("snapshot_id")

        return snapshot_id


    def get_root_id_from_snapshot_id(self, snapshot_id=None):

        conditions = {}
        root_id = None

        if snapshot_id:
            conditions["snapshot_id"] = snapshot_id

        snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if snapshot_set is None or len(snapshot_set) == 0:
            return None

        for snapshot in snapshot_set:
            root_id = snapshot.get("root_id")

        return root_id

    def get_parent_id_from_snapshot_id(self, snapshot_id=None):

        conditions = {}
        parent_id = None

        if snapshot_id:
            conditions["snapshot_id"] = snapshot_id

        snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if snapshot_set is None or len(snapshot_set) == 0:
            return None

        for snapshot in snapshot_set:
            parent_id = snapshot.get("parent_id")

        return parent_id

    def get_snapshot_ids_from_root_id(self, root_id=None):

        conditions = {}
        snapshot_ids = []

        if root_id:
            conditions["root_id"] = root_id

        snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if snapshot_set is None or len(snapshot_set) == 0:
            return None

        for snapshot in snapshot_set:
            snapshot_id = snapshot.get("snapshot_id")
            if snapshot_id:
                snapshot_ids.append(snapshot_id)

        return snapshot_ids

    def get_snapshot_group_details(self, snapshot_group_ids):

        conditions = {"snapshot_group_id": snapshot_group_ids}

        snapshot_group_set = self.pg.base_get(dbconst.TB_SNAPSHOT_GROUP, conditions)
        if snapshot_group_set is None or len(snapshot_group_set) == 0:
            return None

        snapshot_groups = {}
        for snapshot_group in snapshot_group_set:
            snapshot_group_id = snapshot_group["snapshot_group_id"]

            snapshot_groups[snapshot_group_id] = snapshot_group

        return snapshot_groups

    def get_snapshot_group_resource_detail(self, snapshot_group_id, extras=[dbconst.TB_DESKTOP]):

        ctx = context.instance()

        snapshot_group = self.pg.get(dbconst.TB_SNAPSHOT_GROUP, snapshot_group_id)
        if snapshot_group is None or len(snapshot_group) == 0:
            return None

        ret = self.get_snapshot_group_resources(snapshot_group_id=snapshot_group_id)
        if ret is not None:
            snapshot_group_resources = ret
            desktops = {}
            for desktop_resource_id,_ in snapshot_group_resources.items():

                conditions = dict(desktop_id=desktop_resource_id)
                if dbconst.TB_DESKTOP in extras:
                    desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)

                    if desktop_set is not None and len(desktop_set) > 0:
                        for desktop in desktop_set:
                            desktop_id = desktop["desktop_id"]

                            desktop_disks = self.pg.base_get(dbconst.TB_DESKTOP_DISK, {"desktop_id": desktop_id})
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
                    else:
                        # delete resource_id in snapshot_group_resource db
                        delete_snapshot_group_resource_info = dict(
                            snapshot_group_id=snapshot_group_id,
                            desktop_resource_id=desktop_resource_id
                        )
                        ctx.pg.base_delete(dbconst.TB_SNAPSHOT_GROUP_RESOURCE,delete_snapshot_group_resource_info)

            snapshot_group["desktops"] = desktops

        # get snapshot_group_snapshot info
        snapshot_group_snapshots = self.get_snapshot_group_snapshots(snapshot_group_id=snapshot_group_id)
        if snapshot_group_snapshots is not None:
            for snapshot_group_snapshot_id,_ in snapshot_group_snapshots.items():
                ret = self.get_snapshot_resources(snapshot_group_snapshot_ids=snapshot_group_snapshot_id)
                if ret is None:
                    del snapshot_group_snapshots[snapshot_group_snapshot_id]
                    # delete snapshot_group_snapshot_id in TB_SNAPSHOT_GROUP_SNAPSHOT
                    delete_snapshot_group_snapshot_info = dict(snapshot_group_snapshot_id=snapshot_group_snapshot_id)
                    ctx.pg.base_delete(dbconst.TB_SNAPSHOT_GROUP_SNAPSHOT, delete_snapshot_group_snapshot_info)

            snapshot_group["snapshot_group_snapshots"] = snapshot_group_snapshots

        return snapshot_group

    def get_desktop_resource_from_snapshot_id(self, snapshot_id=None):

        conditions = {}
        desktop_resource_id = None

        if snapshot_id:
            conditions["snapshot_id"] = snapshot_id


        snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if snapshot_set is None or len(snapshot_set) == 0:
            return None

        for snapshot in snapshot_set:
            desktop_resource_id = snapshot.get("desktop_resource_id")

        return desktop_resource_id

    def get_snapshot_ids(self, resource_id=None, desktop_resource_id=None,head_chain=None,snapshot_type=None):

        conditions = {}
        snapshot_ids = []

        if resource_id:
            conditions["resource_id"] = resource_id

        if desktop_resource_id:
            conditions["desktop_resource_id"] = desktop_resource_id

        if head_chain is not None:
            conditions["head_chain"] = head_chain

        if snapshot_type is not None:
            conditions["snapshot_type"] = snapshot_type

        snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if snapshot_set is None or len(snapshot_set) == 0:
            return None

        for snapshot in snapshot_set:
            snapshot_id = snapshot.get("snapshot_id")
            snapshot_ids.append(snapshot_id)

        return snapshot_ids

    def get_total_count(self, snapshot_id=None):

        conditions = {}
        total_count = None

        if snapshot_id:
            conditions["snapshot_id"] = snapshot_id

        snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if snapshot_set is None or len(snapshot_set) == 0:
            return None

        for snapshot in snapshot_set:
            total_count = snapshot.get("total_count")

        return total_count

    def get_snapshot_resources_snapshot_ids(self,desktop_resource_ids=None , ymd=None, snapshot_ids=None):

        conditions = {}
        if desktop_resource_ids:
            conditions["desktop_resource_id"] = desktop_resource_ids

        if ymd is not None:
            conditions["ymd"] = ymd

        if snapshot_ids:
            conditions["snapshot_id"] = snapshot_ids

        snapshot_resource_set = self.pg.base_get(dbconst.TB_SNAPSHOT_RESOURCE, conditions)
        if snapshot_resource_set is None or len(snapshot_resource_set) == 0:
            return None

        snapshot_resources = {}
        for snapshot_resource in snapshot_resource_set:
            snapshot_id = snapshot_resource["snapshot_id"]
            snapshot_resources[snapshot_id] = snapshot_resource

        return snapshot_resources

    def get_desktop_snapshots_snapshot_ids(self, desktop_resource_ids=None,root_ids = None,snapshot_type = None):

        conditions = {}

        if desktop_resource_ids:
            conditions["desktop_resource_id"] = desktop_resource_ids

        if root_ids:
            conditions["root_id"] = root_ids
        else:
            conditions["root_id"] = ""

        if snapshot_type is not None:
            conditions["snapshot_type"] = snapshot_type

        desktop_snapshot_set = self.pg.base_get(dbconst.TB_DESKTOP_SNAPSHOT, conditions)
        if desktop_snapshot_set is None or len(desktop_snapshot_set) == 0:
            return None

        desktop_snapshots = {}
        for desktop_snapshot in desktop_snapshot_set:
            snapshot_id = desktop_snapshot["snapshot_id"]
            desktop_snapshots[snapshot_id] = desktop_snapshot

        return desktop_snapshots

    def get_desktop_snapshot_ids_from_snapshot_group_snapshot_id(self, snapshot_group_snapshot_ids=None):

        conditions = {}
        desktop_snapshot_ids = []

        if snapshot_group_snapshot_ids:
            conditions["snapshot_group_snapshot_id"] = snapshot_group_snapshot_ids

        snapshot_resource_set = self.pg.base_get(dbconst.TB_SNAPSHOT_RESOURCE, conditions)
        if snapshot_resource_set is None or len(snapshot_resource_set) == 0:
            return None

        for snapshot_resource in snapshot_resource_set:
            desktop_snapshot_id = snapshot_resource.get("desktop_snapshot_id")
            if desktop_snapshot_id in desktop_snapshot_ids:
                continue
            desktop_snapshot_ids.append(desktop_snapshot_id)

        return desktop_snapshot_ids

    def get_snapshot_group_snapshot_ids_from_snapshot_id(self, snapshot_ids=None):

        conditions = {}
        snapshot_group_snapshot_ids = []

        if snapshot_ids:
            conditions["snapshot_id"] = snapshot_ids

        snapshot_resource_set = self.pg.base_get(dbconst.TB_SNAPSHOT_RESOURCE, conditions)
        if snapshot_resource_set is None or len(snapshot_resource_set) == 0:
            return None

        for snapshot_resource in snapshot_resource_set:
            snapshot_group_snapshot_id = snapshot_resource.get("snapshot_group_snapshot_id")
            if snapshot_group_snapshot_id in snapshot_group_snapshot_ids:
                continue
            snapshot_group_snapshot_ids.append(snapshot_group_snapshot_id)

        return snapshot_group_snapshot_ids

    def get_snapshot_resources_snapshot_ids_order_by_create_time(self ,snapshot_ids=None):

        conditions = {}
        lastest_snapshot_id = None

        if snapshot_ids:
            conditions["snapshot_id"] = snapshot_ids

        sort_key = "create_time"
        reverse = True

        snapshot_resource_set = self.pg.base_get(dbconst.TB_SNAPSHOT_RESOURCE, condition=conditions,sort_key=sort_key,reverse=reverse)
        if snapshot_resource_set is None or len(snapshot_resource_set) == 0:
            return None

        for snapshot_resource in snapshot_resource_set:
            lastest_snapshot_id = snapshot_resource["snapshot_id"]
            break

        return lastest_snapshot_id

    def get_snapshot_group_snapshot_ids_order_by_create_time(self, snapshot_group_ids=None):

        conditions = {}
        root_snapshot_group_snapshot_id = None

        if snapshot_group_ids:
            conditions["snapshot_group_id"] = snapshot_group_ids

        sort_key = "create_time"
        reverse = False

        snapshot_group_snapshot_set = self.pg.base_get(dbconst.TB_SNAPSHOT_GROUP_SNAPSHOT, condition=conditions, sort_key=sort_key,reverse=reverse)
        if snapshot_group_snapshot_set is None or len(snapshot_group_snapshot_set) == 0:
            return None

        for snapshot_group_snapshot in snapshot_group_snapshot_set:
            root_snapshot_group_snapshot_id = snapshot_group_snapshot["snapshot_group_snapshot_id"]
            break

        return root_snapshot_group_snapshot_id

