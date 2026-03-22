import context
from log.logger import logger
import constants as const
import db.constants as dbconst
import dispatch_resource.desktop_common as DeskComm
import resource_common as ResComm
from utils.misc import rLock, get_current_time
from utils.id_tool import(
    UUID_TYPE_DESKTOP,
    UUID_TYPE_DESKTOP_DISK
)

def check_desktop_snapshot(sender, desktop_ids):

    ctx = context.instance()
    if not desktop_ids:
        return None

    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        logger.error("check desktop instance no found desktop %s" % desktop_ids)
        return None
    
    # only check instance desktop
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        return None

    instance_ids = desktop_instance.values()
    # get instance resource
    res_instances = DeskComm.get_instances(sender, instance_ids)
    if res_instances is None:
        logger.error("resource describe instance return none %s" % instance_ids)
        return None
    
    snapshot_desktop = []
    for desktop_id, _ in desktops.items():
        
        if desktop_id not in desktop_instance:
            continue
        
        instance_id = desktop_instance[desktop_id]
        # maybe instance has already be deleted
        instance = res_instances.get(instance_id)
        if not instance:
            continue

        inst_status = instance["status"]
        if inst_status in [const.INST_STATUS_CEASED, const.INST_STATUS_TERM]:
            continue
        
        snapshot_desktop.append(desktop_id)

    return snapshot_desktop

def check_disk_snapshot(sender, disk_ids):
    
    ctx = context.instance()
    disks = ctx.pgm.get_disks(disk_ids)
    if not disks:
        logger.error("job no found disks %s" % disk_ids)
        return None

    disk_volume = ctx.pgm.get_disk_volume(disk_ids)
    if not disk_volume:
        return None

    volume_ids = disk_volume.values()
    ret = ctx.res.resource_describe_volumes(sender["zone"], volume_ids)
    if ret is None:
        logger.error("describe disk resource fail %s" % volume_ids)
        return None
    volumes = ret
    
    snapshot_disk = []
    for disk_id, volume_id in disk_volume.items():
        volume = volumes.get(volume_id)
        if not volume or volume["status"] in [const.DISK_STATUS_CEASED, const.DISK_STATUS_DELETED]:
            continue
        
        snapshot_disk.append(disk_id)
    
    return snapshot_disk

def get_snapshot_instance_volume(snapshots):

    instance_ids = []
    volume_ids = []
    resource_snapshot = {}
    for snapshot_id, snapshot in snapshots.items():
        desktop_resource_id = snapshot["desktop_resource_id"]
        prefix = desktop_resource_id.split("-")[0]
        if prefix in [UUID_TYPE_DESKTOP]:
            instance_id = snapshot["resource_id"]
            if instance_id:
                resource_snapshot[instance_id] = snapshot_id
                instance_ids.append(instance_id)

        elif prefix in [UUID_TYPE_DESKTOP_DISK]:
            
            volume_id = snapshot["resource_id"]
            if volume_id:
                resource_snapshot[volume_id] = snapshot_id
                volume_ids.append(volume_id)

    return (resource_snapshot, instance_ids, volume_ids)

def check_desktop_snapshot_resource(sender, desktop_snapshot_ids):
    
    ctx = context.instance()
    snapshot_resource = ctx.pgm.get_snapshot_resource(desktop_snapshot_ids)
    if not snapshot_resource:
        logger.error("no found snapshot resource %s" % desktop_snapshot_ids)
        return -1
    
    desktop_ids = []
    disk_ids = []
    for desktop_snapshot_id, desktop_snapshot in snapshot_resource.items():
        desktop_resource = desktop_snapshot["desktop_resource"]
        if not desktop_resource:
            logger.error("check desktop snapshot resource no found resource %s" % desktop_snapshot_id)
            return -1
    
        prefix = desktop_resource.split("-")[0]
        if prefix in [UUID_TYPE_DESKTOP]:
            desktop_ids.append(desktop_resource)
        elif prefix in [UUID_TYPE_DESKTOP_DISK]:
            disk_ids.append(desktop_resource)
    
    snapshot_resource = []
    if desktop_ids:
        ret = check_desktop_snapshot(sender, desktop_ids)
        if not ret:
            logger.error("check desktop snapshot resource no found resource %s" % desktop_ids)
            return -1

        if ret:
            snapshot_resource.extend(ret)
        
    if disk_ids:
        ret = check_disk_snapshot(sender, disk_ids)
        if not ret:
            logger.error("check desktop snapshot resource no found resource %s" % disk_ids)
            return -1

        if ret:
            snapshot_resource.extend(ret)

    return snapshot_resource

def get_snapshot_info(snapshot):
        
    parent_keys = ["total_store_size", "total_size", "total_count","head_chain"]
    snapshot_keys = ["snapshot_id", "snapshot_name", "description", "resource_id", "snapshot_type",
                     "root_id", "parent_id", "is_head", "raw_size", "store_size", "size",
                     "transition_status", "status", "status_time", "create_time"]
        
    snapshot_info = {}
    for snapshot_key in snapshot_keys:
        if snapshot_key not in snapshot:
            logger.error("create snapshot key %s dismatch %s" % (snapshot_key, snapshot))
            return None
        
        snapshot_info[snapshot_key] = snapshot[snapshot_key]   
       
    for parent_key in parent_keys:
        if parent_key not in snapshot:
            snapshot_info[parent_key] = 0
        else:
            snapshot_info[parent_key] = snapshot[parent_key]
    
    return snapshot_info

def register_desktop_snapshot(sender, res_snapshot, snapshot_resource):

    ctx = context.instance()
    new_desktop_snapshot = {}
        
    snapshot_info = get_snapshot_info(res_snapshot)
    if not snapshot_info:
        return -1

    resource_id = res_snapshot["resource_id"]
    if resource_id != snapshot_resource["resource_id"]:
        return -1
    
    desktop_snapshot_id = snapshot_resource["desktop_snapshot_id"]
    if desktop_snapshot_id:
        snapshot_info["desktop_snapshot_id"] = desktop_snapshot_id

    desktop_resource_id = snapshot_resource["desktop_resource_id"]
    if desktop_resource_id:
        snapshot_info["desktop_resource_id"] = desktop_resource_id

    snapshot_info["owner"] = sender["owner"]
    snapshot_info["zone"] = sender["zone"]
    snapshot_info["snapshot_time"] = get_current_time()


    snapshot_id = res_snapshot["snapshot_id"]

    new_desktop_snapshot[snapshot_id] = snapshot_info

    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_SNAPSHOT, new_desktop_snapshot):
        logger.error("insert newly created desktop snapshot for [%s] to db failed" % (new_desktop_snapshot))
        return -1

    return 0

def update_snapshot_resource(sender, snapshot_id,snapshot_resource,snapshot_group_snapshot_id):

    ctx = context.instance()

    desktop_snapshot_id = snapshot_resource.get("desktop_snapshot_id")
    desktop_resource_id = snapshot_resource.get("desktop_resource_id")
    conditions = {
        "desktop_snapshot_id": desktop_snapshot_id,
        "desktop_resource_id": desktop_resource_id
    }
    update_snapshot_resource_info = {
        "snapshot_id" : snapshot_id,
        "snapshot_group_snapshot_id" : snapshot_group_snapshot_id if snapshot_group_snapshot_id else '',
    }

    if not ctx.pg.base_update(dbconst.TB_SNAPSHOT_RESOURCE, conditions, update_snapshot_resource_info):
        logger.error("refresh snapshot resource for [%s] to db failed" % (update_snapshot_resource_info))
        return -1

    return 0

def update_snapshot_group_snapshot(sender, res_snapshot,snapshot_group_snapshot_id):

    ctx = context.instance()

    transition_status = res_snapshot.get("transition_status")
    status = res_snapshot.get("status")
    conditions = {"snapshot_group_snapshot_id": snapshot_group_snapshot_id}

    update_snapshot_group_snapshot_info = {
        "transition_status" : transition_status if transition_status else '',
        "status" : status if status else '',
    }

    if not ctx.pg.base_update(dbconst.TB_SNAPSHOT_GROUP_SNAPSHOT, conditions, update_snapshot_group_snapshot_info):
        logger.error("refresh snapshot group snapshot for [%s] to db failed" % (update_snapshot_group_snapshot_info))
        return -1

    return 0

def update_snapshot_group(sender, res_snapshot,snapshot_group_id):

    ctx = context.instance()
    status = res_snapshot.get("status")
    conditions = {"snapshot_group_id": snapshot_group_id}
    update_snapshot_group_info = {"status" : status if status else '',}

    if not ctx.pg.base_update(dbconst.TB_SNAPSHOT_GROUP, conditions, update_snapshot_group_info):
        logger.error("refresh snapshot group for [%s] to db failed" % (update_snapshot_group_info))
        return -1

    return 0

def refresh_desktop_snapshot(sender, snapshot_ids):

    ctx = context.instance()
    if not isinstance(snapshot_ids, list):
        snapshot_ids = [snapshot_ids]
    
    ret = ctx.pgm.get_desktop_snapshots(snapshot_ids=snapshot_ids)
    if not ret:
        logger.error("refresh desktop snapshot get resource fail %s" % snapshot_ids)
        return -1
    snapshots = ret

    res_snapshots = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_ids)
    if res_snapshots is None:
        logger.error("resource describe snapshots fail %s" % snapshot_ids)
        return -1

    refresh_desktop_snapshot_info = {}
    for snapshot_id, _ in snapshots.items():

        res_snapshot = res_snapshots.get(snapshot_id)
        if not res_snapshot:
            logger.error("snapshot refresh fail %s" % snapshot_id)
            return 0

        snapshot_info = get_snapshot_info(res_snapshot)
        if not snapshot_info:
            return -1

        refresh_desktop_snapshot_info[snapshot_id] = snapshot_info

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_SNAPSHOT, refresh_desktop_snapshot_info):
        logger.error("refresh desktop snapshot for [%s] to db failed" %(refresh_desktop_snapshot_info))
        return -1
    
    return 0

def refresh_full_backup_chain_desktop_snapshot(sender, root_id=None):

    ctx = context.instance()

    if root_id:
        snapshot_ids = ctx.pgm.get_snapshot_ids_from_root_id(root_id)
        if snapshot_ids:
            for snapshot_id in snapshot_ids:
                ret = refresh_desktop_snapshot(sender, snapshot_id)
                if ret < 0:
                    logger.error("refresh desktop snapshot db fail %s" % snapshot_ids)
                    return -1
    return 0

def update_desktop_snaphost_status(snapshot_ids, status):
    
    ctx = context.instance()
    
    snapshot_info = {snapshot_id: {"status": status} for snapshot_id in snapshot_ids}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_info):
        logger.error("update desktop_snaphost status filed fail %s " % snapshot_ids)
        return -1
    
    return 0

def task_create_desktop_snapshot(sender, resource_id, snapshot_name, is_full):

    ctx = context.instance()
    
    with rLock(resource_id):
        ret = ctx.res.resource_create_snapshots(sender["zone"], resource_id, snapshot_name, is_full)
        if not ret:
            logger.error("resource create snapshot fail %s" % resource_id)
            return -1
        
        (snapshot_ids, job_id) = ret

        return (snapshot_ids, job_id)

def task_register_desktop_snapshots(sender,desktop_snapshot_id,snapshot_id,snapshot_group_snapshot_id):

    ctx = context.instance()

    # resource_describe_snapshots
    res_snapshots = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_id)
    if not res_snapshots:
        logger.error("resource_describe_snapshots, no found snapshot %s" %(snapshot_id))
        return -1

    # get res_snapshot
    for _,res_snapshot in res_snapshots.items():
        if not res_snapshot:
            return -1

    resource_id = res_snapshot["resource_id"]

    # get snapshot_resource
    ret = ctx.pgm.get_snapshot_resources(desktop_snapshot_ids=desktop_snapshot_id,resource_ids=resource_id)
    if ret is None:
        logger.error("get snapshot resource fail %s" %(resource_id))
        return -1
    snapshot_resources = ret

    for _,snapshot_resource in snapshot_resources.items():
        if not snapshot_resource:
            return -1

    # register desktop_snapshot db
    ret = register_desktop_snapshot(sender, res_snapshot, snapshot_resource)
    if ret < 0:
        logger.error("register desktop snapshot fail %s" %(snapshot_id))
        return -1


    # update snapshot_resource db
    ret = update_snapshot_resource(sender, snapshot_id, snapshot_resource,snapshot_group_snapshot_id)
    if ret < 0:
        logger.error("update snapshot resource fail %s" %(snapshot_id))
        return -1

    return 0

def task_refresh_desktop_snapshots(sender, snapshot_id):

    ctx = context.instance()
    # refresh desktop_snapshot current snapshot_id
    ret = refresh_desktop_snapshot(sender, snapshot_id)
    if ret < 0:
        logger.error("refresh desktop snapshot db fail %s" %(snapshot_id))
        return -1

    # refresh desktop_snapshot the current full backup chain
    ret = ctx.pgm.get_root_id_from_snapshot_id(snapshot_id)
    if ret is not None:
        root_id = ret
        ret = refresh_full_backup_chain_desktop_snapshot(sender, root_id)
        if ret < 0:
            logger.error("refresh full_backup_chain desktop snapshot db fail %s" %(snapshot_id))
            return -1

    # refresh desktop_snapshot the old full backup chain
    ret = ctx.pgm.get_desktop_resource_from_snapshot_id(snapshot_id)
    if ret is not None:
        desktop_resource_id = ret
        ret = ctx.pgm.get_snapshot_ids(desktop_resource_id=desktop_resource_id,head_chain=1,snapshot_type=1)
        if ret is not None:
            snapshot_id_s = ret
            if root_id in snapshot_id_s:
                snapshot_id_s.remove(root_id)
            for snapshot_id in snapshot_id_s:
                ret = refresh_full_backup_chain_desktop_snapshot(sender, snapshot_id)
                if ret < 0:
                    logger.error("refresh full_backup_chain desktop snapshot db fail %s" % (snapshot_id))
                    return -1

    return 0

def check_delete_desktop_snapshot(sender, snapshot_ids):

    ctx = context.instance()
    ret = ctx.pgm.get_desktop_snapshots(snapshot_ids=snapshot_ids)
    if not ret:
        return -1
    snapshots = ret

    ret = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_ids)
    if ret is None:
        return -1
    res_snapshots = ret
    
    task_snapshot = {}
    delete_snapshot = []
    for snapshot_id, snapshot in snapshots.items():
        res_snapshot = res_snapshots.get(snapshot_id)
        if not res_snapshot or res_snapshot["status"] in [const.SNAPSHOT_STATUS_DELETED]:
            delete_snapshot.append(snapshot_id)
            continue

        task_snapshot[snapshot_id] = snapshot

    if delete_snapshot:
        ret = delete_desktop_snapshots(sender, delete_snapshot)
        if ret < 0:
            logger.error("delete desktop snapshot db fail %s" % snapshot_id)
            return -1
    return task_snapshot

def delete_desktop_snapshot_info(snapshot_ids):
    
    ctx = context.instance()
    if not isinstance(snapshot_ids, list):
        snapshot_ids = [snapshot_ids]
    
    for snapshot_id in snapshot_ids:
        ret = ctx.pg.delete(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_id)
        if not ret:
            logger.error("delete_desktop_snapshot_info fail %s" % (snapshot_id))
            return -1
    return 0

def task_delete_desktop_snapshot(sender, snapshot_id):
    logger.info("task_delete_desktop_snapshot snapshot_id == %s" % (snapshot_id))
    ctx = context.instance()
    
    ret = ctx.res.resource_delete_snapshots(sender["zone"], snapshot_id)
    if ret is None:
        logger.error("resource delete snapshot fail %s" % snapshot_id)
        return -1

    return 0

def check_capture_instance_from_desktop_snapshot(sender, snapshot_ids):
    
    ctx = context.instance()
    
    if not isinstance(snapshot_ids, list):
        snapshot_ids = [snapshot_ids]
    
    ret = ctx.pgm.get_desktop_snapshots(snapshot_ids)
    if not ret:
        return -1
    snapshots = ret

    ret = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_ids)
    if ret is None:
        return -1
    res_snapshots = ret
    
    task_snapshot = {}
    delete_snapshot = []
    for snapshot_id, snapshot in snapshots.items():
        res_snapshot = res_snapshots.get(snapshot_id)
        if not res_snapshot or res_snapshot["status"] in [const.SNAPSHOT_STATUS_DELETED]:
            delete_snapshot.append(snapshot_id)
            continue

        task_snapshot[snapshot_id] = snapshot
        
    if delete_snapshot:
        ret = delete_desktop_snapshots(sender, delete_snapshot)
        if ret < 0:
            logger.error("delete desktop snapshot db fail %s" % snapshot_id)
            return -1

    return task_snapshot


def check_create_disk_from_desktop_snapshot(sender, snapshot_ids):
    ctx = context.instance()

    if not isinstance(snapshot_ids, list):
        snapshot_ids = [snapshot_ids]

    ret = ctx.pgm.get_desktop_snapshots(snapshot_ids)
    if not ret:
        return -1
    snapshots = ret

    ret = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_ids)
    if ret is None:
        return -1
    res_snapshots = ret

    task_snapshot = {}
    delete_snapshot = []
    for snapshot_id, snapshot in snapshots.items():
        res_snapshot = res_snapshots.get(snapshot_id)
        if not res_snapshot or res_snapshot["status"] in [const.SNAPSHOT_STATUS_DELETED]:
            delete_snapshot.append(snapshot_id)
            continue

        task_snapshot[snapshot_id] = snapshot

    if delete_snapshot:
        ret = delete_desktop_snapshots(sender, delete_snapshot)
        if ret < 0:
            logger.error("delete desktop snapshot db fail %s" % snapshot_id)
            return -1

    return task_snapshot

def check_apply_desktop_snapshot(sender, snapshot_ids):

    ctx = context.instance()
    
    ret = ctx.pgm.get_desktop_snapshots(snapshot_ids=snapshot_ids)
    if not ret:
        return -1
    snapshots = ret
    
    apply_snapshot = []
    (resource_snapshot, instance_ids, volume_ids) = get_snapshot_instance_volume(snapshots)
    if instance_ids:
        ret = ctx.res.resource_describe_instances(sender["zone"], instance_ids)
        if ret is None:
            return -1
        
        instances = ret
        for instance_id in instance_ids:
            instance = instances.get(instance_id)
            if not instance:
                continue

            status = instance["status"]
            if status in [const.INST_STATUS_CEASED, const.INST_STATUS_TERM]:
                continue
            
            snapshot_id = resource_snapshot.get(instance_id)
            if snapshot_id:
                apply_snapshot.append(snapshot_id)
    
    if volume_ids:
        ret = ctx.res.resource_describe_volumes(sender["zone"], volume_ids)
        if ret is None:
            return -1
        volumes = ret
        for volume_id in volume_ids:
            volume = volumes.get(volume_id)
            if not volume:
                continue
            status = volume["status"]
            if status in [const.DISK_STATUS_CEASED, const.DISK_STATUS_DELETED]:
                continue
            snapshot_id = resource_snapshot.get(volume_id)
            if snapshot_id:
                apply_snapshot.append(snapshot_id)

    if not apply_snapshot:
        return -1

    ret = ctx.res.resource_describe_snapshots(sender["zone"], apply_snapshot)
    if ret is None:
        return -1
    res_snapshots = ret
    
    task_snapshot = {}
    delete_snapshot = []
    for snapshot_id, snapshot in snapshots.items():
        res_snapshot = res_snapshots.get(snapshot_id)
        if not res_snapshot or res_snapshot["status"] in [const.SNAPSHOT_STATUS_DELETED]:
            delete_snapshot.append(snapshot_id)
            continue

        task_snapshot[snapshot_id] = snapshot
        
    if delete_snapshot:
        ret = delete_desktop_snapshots(sender, delete_snapshot)
        if ret < 0:
            logger.error("delete desktop snapshot db fail %s" % snapshot_id)
            return -1
            
    return task_snapshot

def task_apply_desktop_snapshot(sender, snapshot_id):

    ctx = context.instance()
    ret = ctx.res.resource_apply_snapshots(sender["zone"], snapshot_id)
    if ret is None:
        logger.error("resource apply snapshot fail %s" % snapshot_id)
        return -1

    return 0

def task_capture_instance_from_desktop_snapshot(sender,snapshot_id,image_name):

    ctx = context.instance()
    ret = ctx.res.resource_capture_instance_from_snapshot(sender["zone"], snapshot_id, image_name)
    if ret is None:
        logger.error("resource capture instance from snapshot fail %s" % snapshot_id)
        return -1

    return 0

def task_create_disk_from_desktop_snapshot(sender,snapshot_id,disk_name):

    ctx = context.instance()
    ret = ctx.res.resource_create_volume_from_snapshot(sender["zone"], snapshot_id, disk_name)
    if ret is None:
        logger.error("resource create volume from desktop snapshot fail %s" % snapshot_id)
        return -1

    return 0

def delete_desktop_snapshots(sender,snapshot_ids):

    ctx = context.instance()
    snapshot_group_snapshot_ids = []

    if not isinstance(snapshot_ids, list):
        snapshot_ids = [snapshot_ids]

    delete_snapshot_ids = snapshot_ids
    #When you delete an incremental backup point, all its child nodes are also deleted.
    ret = ctx.pgm.get_snapshot_id_from_parent_id(parent_id=snapshot_ids)
    while ret:
        delete_snapshot_ids.append(ret)
        snapshot_id = ret
        ret = ctx.pgm.get_snapshot_id_from_parent_id(parent_id=snapshot_id)
        if ret is None:
            break

    # save snapshot_group_snapshot_id from snapshot_ids
    ret = ctx.pgm.get_snapshot_group_snapshot_ids_from_snapshot_id(snapshot_ids=delete_snapshot_ids)
    if ret:
        snapshot_group_snapshot_ids = ret


    for snapshot_id in delete_snapshot_ids:
        ret = ctx.pg.base_delete(dbconst.TB_DESKTOP_SNAPSHOT, {"snapshot_id": snapshot_id})
        if ret < 0:
            return -1

        ret = ctx.pg.base_delete(dbconst.TB_SNAPSHOT_RESOURCE, {"snapshot_id": snapshot_id})
        if ret < 0:
            return -1


    # check if snapshot_group_snapshot is exist or not
    ret = check_snapshot_group_snapshot_ids_valid(sender,snapshot_group_snapshot_ids)
    if ret:
        delete_snapshot_group_snapshot_ids = ret
        # delete snapshot_group_snapshot
        ret = ctx.pg.base_delete(dbconst.TB_SNAPSHOT_GROUP_SNAPSHOT, {"snapshot_group_snapshot_id": delete_snapshot_group_snapshot_ids})
        if ret < 0:
            return -1

    return 0

def delete_snapshot_resource(sender,desktop_snapshot_ids):

    ctx = context.instance()
    if not isinstance(desktop_snapshot_ids, list):
        desktop_snapshot_ids = [desktop_snapshot_ids]

    for desktop_snapshot_id in desktop_snapshot_ids:

        ret = ctx.pg.base_delete(dbconst.TB_SNAPSHOT_RESOURCE, {"desktop_snapshot_id": desktop_snapshot_id})
        if ret < 0:
            return -1
        #If a full backup node is deleted, then all incremental backup points based on it should be automatically deleted.
        ret = ctx.pg.base_delete(dbconst.TB_DESKTOP_SNAPSHOT, {"desktop_snapshot_id": desktop_snapshot_id})
        if ret < 0:
            return -1

    return 0

def check_snapshot_resource_ids(sender, desktop_snapshot_id):

    ctx = context.instance()

    resource_ids = []
    ret = ctx.pgm.get_snapshot_resources(desktop_snapshot_ids=desktop_snapshot_id)
    if ret is None:
        logger.error("get snapshot resources fail %s" %(desktop_snapshot_id))
        return -1
    snapshot_resources = ret
    for _,snapshot_resource in snapshot_resources.items():
        resource_id = snapshot_resource["resource_id"]
        if resource_id in resource_ids:
            continue
        resource_ids.append(resource_id)

    return resource_ids

def check_snapshot_is_full(sender, desktop_snapshot_id,resource_ids,is_full=0):

    ctx = context.instance()
    # determine whether it is an incremental backup or a full backup
    total_count = 0
    full_backup_chain_count = 0
    oldest_full_backup_chain = None
    zone_id = sender["zone"]
    max_chain_count = ctx.zone_checker.get_resource_limit(zone_id, "max_chain_count")
    max_snapshot_count = ctx.zone_checker.get_resource_limit(zone_id, "max_snapshot_count")

    # get desktop_id
    for resource_id in resource_ids:
        ret = ctx.pgm.get_snapshot_resources(desktop_snapshot_ids=desktop_snapshot_id,resource_ids=resource_id)
        if ret is None:
            logger.error("get snapshot resources fail %s" % (resource_id))
            return -1
        snapshot_resources = ret
        for desktop_resource_id, _ in snapshot_resources.items():
            prefix = desktop_resource_id.split("-")[0]
            if prefix in [UUID_TYPE_DESKTOP]:
                desktop_id = desktop_resource_id

    if not desktop_id:
        return -1

    # Check the number of full backup chains
    ret = ctx.pgm.get_snapshot_ids(desktop_resource_id=desktop_id, snapshot_type=1)
    if ret is not None:
        snapshot_ids = ret
        full_backup_chain_count = len(snapshot_ids)

        # Check how many backup nodes are in the current backup chain
        ret = ctx.pgm.get_snapshot_ids(desktop_resource_id=desktop_id, head_chain=1, snapshot_type=1)
        if ret is not None:
            snapshot_id = ret
            ret = ctx.pgm.get_total_count(snapshot_id)
            if ret is not None:
                total_count = ret
                if total_count >= max_snapshot_count:
                    is_full = 1

        # More than 2 cases will delete the oldest backup chain.
        if (full_backup_chain_count > max_chain_count) or (total_count == max_snapshot_count and full_backup_chain_count == max_chain_count):
            ret = ctx.pgm.get_snapshot_ids(desktop_resource_id=desktop_id, head_chain=0, snapshot_type=1)
            if ret is not None:
                oldest_full_backup_chain = ret

    return (is_full,oldest_full_backup_chain)

def delete_oldest_full_backup_chain(sender, oldest_full_backup_chain):

    ctx = context.instance()
    snapshot_ids = oldest_full_backup_chain
    new_snapshot_ids = []
    desktop_snapshot_ids = []

    if not snapshot_ids:
        return 0

    # get desktop_snapshot_ids
    for snapshot_id in snapshot_ids:
        ret = ctx.pgm.get_desktop_snapshots(snapshot_ids=snapshot_id)
        if ret is None:
            logger.info("get desktop_snapshots fail %s" % (snapshot_id))
            continue
        desktop_snapshots = ret
        for _,desktop_snapshot in desktop_snapshots.items():
            desktop_snapshot_id = desktop_snapshot["desktop_snapshot_id"]
            if desktop_snapshot_id in desktop_snapshot_ids:
                continue
            desktop_snapshot_ids.append(desktop_snapshot_id)

    if not desktop_snapshot_ids:
        return 0

    # get new_snapshot_ids
    for desktop_snapshot_id in desktop_snapshot_ids:
        ret = ctx.pgm.get_desktop_snapshots(desktop_snapshot_ids=desktop_snapshot_id)
        if ret is None:
            logger.info("get desktop_snapshots fail %s" % (desktop_snapshot_id))
            continue
        desktop_snapshots = ret
        for snapshot_id,desktop_snapshot in desktop_snapshots.items():
            if snapshot_id in new_snapshot_ids:
                continue
            new_snapshot_ids.append(snapshot_id)

    # task_delete_desktop_snapshot
    for snapshot_id in new_snapshot_ids:

        with ResComm.transition_status(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_id,const.SNAPSHOT_TRAN_STATUS_DELETING):
            ret = task_delete_desktop_snapshot(sender, snapshot_id)
            if ret < 0:
                logger.error("task delete desktop snapshot fail %s" % snapshot_id)
                return -1

        # delete desktop_snapshot db
        ret = delete_desktop_snapshots(sender, snapshot_id)
        if ret < 0:
            logger.error("delete desktop snapshot db fail %s" % snapshot_id)
            return -1

    return 0

def check_snapshot_ids(sender, desktop_snapshot_id):

    ctx = context.instance()
    snapshot_ids = []
    ret = ctx.pgm.get_snapshot_resources(desktop_snapshot_ids=desktop_snapshot_id)
    if ret is None:
        logger.error("get snapshot resources fail %s" %(desktop_snapshot_id))
        return -1
    snapshot_resources = ret
    for _,snapshot_resource in snapshot_resources.items():
        snapshot_id = snapshot_resource["snapshot_id"]
        if snapshot_id in snapshot_ids:
            continue
        snapshot_ids.append(snapshot_id)

    return snapshot_ids

def check_snapshot_ids_by_desktop_id(sender, desktop_id):

    ctx = context.instance()
    snapshot_ids = []
    ret = ctx.pgm.get_desktop_snapshots(desktop_resource_ids=desktop_id,snapshot_type=1)
    if ret is None:
        logger.info("get desktop snapshot no found %s" %(desktop_id))
        return None
    desktop_snapshots = ret
    for snapshot_id,_ in desktop_snapshots.items():

        if snapshot_id in snapshot_ids:
            continue
        snapshot_ids.append(snapshot_id)

    return snapshot_ids

def task_refresh_delete_desktop_snapshots(sender, snapshot_id):

    ctx = context.instance()

    root_id = ctx.pgm.get_root_id_from_snapshot_id(snapshot_id)
    if root_id == snapshot_id:
        # if snapshot_id is root_id
        ret = delete_desktop_snapshots(sender, root_id)
        if ret < 0:
            logger.error("delete desktop snapshot db fail %s" % root_id)
            return -1
    else:
        # if snapshot_id is not root_id
        # when you delete an incremental backup point, all its child nodes are also deleted.
        ret = delete_desktop_snapshots(sender, snapshot_id)
        if ret < 0:
            logger.error("delete desktop snapshot db fail %s" % snapshot_id)
            return -1

        # refresh the full backup chain
        ret = refresh_full_backup_chain_desktop_snapshot(sender, root_id)
        if ret < 0:
            logger.error("refresh full_backup_chain desktop snapshot db fail %s" % snapshot_id)
            return -1
    return 0

def task_refresh_snapshot_group_snapshots(sender, snapshot_group_snapshot_id):

    ctx = context.instance()
    status_list = []
    status_finished=['available']

    transition_status_list = []
    transition_status_finished=['']

    ret = ctx.pgm.get_desktop_snapshot_ids_from_snapshot_group_snapshot_id(snapshot_group_snapshot_ids=snapshot_group_snapshot_id)
    if ret:
        desktop_snapshot_ids = ret
        ret = ctx.pgm.get_desktop_snapshots(desktop_snapshot_ids=desktop_snapshot_ids)
        if ret:
            desktop_snapshots = ret
            for _,desktop_snapshot in desktop_snapshots.items():
                status = desktop_snapshot["status"]
                if status in status_list:
                    continue
                status_list.append(status)


            for _, desktop_snapshot in desktop_snapshots.items():
                transition_status = desktop_snapshot["transition_status"]
                if transition_status in transition_status_list:
                    continue
                transition_status_list.append(transition_status)


    if status_list == status_finished and transition_status_list == transition_status_finished:

        #update snapshot_group_snapshot db
        conditions = {"snapshot_group_snapshot_id": snapshot_group_snapshot_id}
        update_snapshot_group_snapshot_info = {
            "transition_status": '',
            "status": 'available',
        }
        if not ctx.pg.base_update(dbconst.TB_SNAPSHOT_GROUP_SNAPSHOT, conditions, update_snapshot_group_snapshot_info):
            logger.error("refresh snapshot group snapshot for [%s] to db failed" % (update_snapshot_group_snapshot_info))
            return -1

        #update snapshot_group db
        snapshot_group_id = get_snapshot_group_id(snapshot_group_snapshot_ids=snapshot_group_snapshot_id)
        if snapshot_group_id:
            conditions = {"snapshot_group_id": snapshot_group_id}
            update_snapshot_group_info = {"status": 'normal'}
            if not ctx.pg.base_update(dbconst.TB_SNAPSHOT_GROUP, conditions, update_snapshot_group_info):
                logger.error("refresh snapshot group for [%s] to db failed" % (update_snapshot_group_info))
                return -1

    return 0

def task_wait_create_desktop_snapshot_done(sender, snapshot_ids, job_id,snapshot_group_snapshot_id=None):

    ctx = context.instance()

    with ResComm.transition_status(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_ids, const.SNAPSHOT_TRAN_STATUS_CREATING):

        # resource_wait_job_done
        ret = ctx.res.resource_wait_job_done(sender["zone"], job_id, const.PLATFORM_TYPE_QINGCLOUD)
        if ret < 0:
            logger.error("resource wait job done %s fail or time" % job_id)
            return -1


    logger.info("task_wait_create_desktop_snapshot_done finished")
    for snapshot_id in snapshot_ids:

        ret = task_refresh_desktop_snapshots(sender, snapshot_id)
        if ret < 0:
            logger.error("task refresh desktop snapshot fail %s" % (snapshot_id))
            return -1

    # refresh snapshot_group_snapshot if the snapshot_group_snapshot_id is exist
    if snapshot_group_snapshot_id:
        ret = task_refresh_snapshot_group_snapshots(sender, snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("task refresh snapshot_group_snapshot fail %s" % (snapshot_group_snapshot_id))
            return -1

    return 0


def task_wait_apply_desktop_snapshot_done(sender, snapshot_ids,snapshot_group_snapshot_id=None):

    with ResComm.transition_status(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_ids, const.SNAPSHOT_TRAN_STATUS_APPLYING):

        ret = task_apply_desktop_snapshot(sender, snapshot_ids)
        if ret < 0:
            logger.error("Task apply desktop snapshot fail:%s " % (snapshot_ids))
            return -1


    logger.info("task_wait_apply_desktop_snapshot_done finished")

    for snapshot_id in snapshot_ids:

        ret = task_refresh_desktop_snapshots(sender, snapshot_id)
        if ret < 0:
            logger.error("task refresh desktop snapshot fail %s" % (snapshot_id))
            return -1

    # refresh snapshot_group_snapshot if the snapshot_group_snapshot_id is exist
    if snapshot_group_snapshot_id:
        ret = task_refresh_snapshot_group_snapshots(sender, snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("task refresh snapshot_group_snapshot fail %s" % (snapshot_group_snapshot_id))
            return -1

    return 0


def task_wait_delete_desktop_snapshot_done(sender, snapshot_ids,snapshot_group_snapshot_id=None):

    with ResComm.transition_status(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_ids, const.SNAPSHOT_TRAN_STATUS_DELETING):

        ret = task_delete_desktop_snapshot(sender, snapshot_ids)
        if ret < 0:
            logger.error("Task delete desktop snapshot fail:%s " % (snapshot_ids))
            return -1

    for snapshot_id in snapshot_ids:
        ret = task_refresh_delete_desktop_snapshots(sender, snapshot_id)
        if ret < 0:
            logger.error("task refresh delete desktop snapshot fail %s" % (snapshot_id))
            return -1

    return 0


def delete_desktop_full_backup_chain(sender, snapshot_ids):

    ctx = context.instance()
    new_snapshot_ids = []
    desktop_snapshot_ids = []

    if not snapshot_ids:
        return 0

    # get desktop_snapshot_ids
    for snapshot_id in snapshot_ids:
        ret = ctx.pgm.get_desktop_snapshots(snapshot_ids=snapshot_id)
        if ret is None:
            logger.info("get desktop_snapshots fail %s" % (snapshot_id))
            continue
        desktop_snapshots = ret
        for _, desktop_snapshot in desktop_snapshots.items():
            desktop_snapshot_id = desktop_snapshot["desktop_snapshot_id"]
            if desktop_snapshot_id in desktop_snapshot_ids:
                continue
            desktop_snapshot_ids.append(desktop_snapshot_id)

    if not desktop_snapshot_ids:
        return 0

    # get new_snapshot_ids
    for desktop_snapshot_id in desktop_snapshot_ids:
        ret = ctx.pgm.get_desktop_snapshots(desktop_snapshot_ids=desktop_snapshot_id)
        if ret is None:
            logger.info("get desktop_snapshots fail %s" % (desktop_snapshot_id))
            continue
        desktop_snapshots = ret
        for snapshot_id, desktop_snapshot in desktop_snapshots.items():
            if snapshot_id in new_snapshot_ids:
                continue
            new_snapshot_ids.append(snapshot_id)


    # task_delete_desktop_snapshot
    for snapshot_id in new_snapshot_ids:

        with ResComm.transition_status(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_id, const.SNAPSHOT_TRAN_STATUS_DELETING):
            ret = task_delete_desktop_snapshot(sender, snapshot_id)
            if ret < 0:
                logger.error("task delete desktop snapshot fail %s" % snapshot_id)
                return -1

        # delete desktop_snapshot db
        ret = delete_desktop_snapshots(sender, snapshot_id)
        if ret < 0:
            logger.error("delete desktop snapshot db fail %s" % snapshot_id)
            return -1

    return 0

def check_snapshot_group_snapshot_ids_valid(sender,snapshot_group_snapshot_ids=None):

    ctx = context.instance()
    delete_snapshot_group_snapshot_ids = []

    for snapshot_group_snapshot_id in snapshot_group_snapshot_ids:

        ret = ctx.pgm.get_snapshot_resources(snapshot_group_snapshot_ids=snapshot_group_snapshot_id)
        if not ret:
            if snapshot_group_snapshot_id in delete_snapshot_group_snapshot_ids:
                continue
            delete_snapshot_group_snapshot_ids.append(snapshot_group_snapshot_id)

    return delete_snapshot_group_snapshot_ids

def get_snapshot_group_id(snapshot_group_snapshot_ids=None):

    ctx = context.instance()
    snapshot_group_id = []

    if not snapshot_group_snapshot_ids:
        return  None

    snapshot_group_snapshots = ctx.pgm.get_snapshot_group_snapshots(snapshot_group_snapshot_id=snapshot_group_snapshot_ids)
    if not snapshot_group_snapshots:
        logger.error("describe snapshot_group_snapshot_id %s no found in desktop_snapshot" % (snapshot_group_snapshot_ids))
        return None

    for _,snapshot_group_snapshot in snapshot_group_snapshots.items():
        snapshot_group_id = snapshot_group_snapshot["snapshot_group_id"]
        break

    return snapshot_group_id
