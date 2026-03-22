from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from utils.id_tool import(
    UUID_TYPE_DESKTOP,
    UUID_TYPE_DESKTOP_DISK
)
from common import check_resource_transition_status
import resource_control.desktop.job as Job
from db.constants import TB_SNAPSHOT_GROUP
from utils.id_tool import(
    UUID_TYPE_SNAPHSOT_GROUP,
    UUID_TYPE_SNAPSHOT_RESOURCET,
    UUID_TYPE_SNAPSHOT_GROUP_SNAPSHOT,
    UUID_TYPE_SNAPSHOT_DISK_SNAPSHOT,
    get_uuid
)
from utils.misc import get_current_time
import datetime


def send_desktop_snapshot_job(sender, desktop_snapshot_ids,desktop_resource_ids, action,extra=None):

    if not isinstance(desktop_snapshot_ids, list):
        desktop_snapshot_ids = [desktop_snapshot_ids]
    
    directive = {
                "sender": sender,
                "action": action,
                "desktop_snapshots" : desktop_snapshot_ids,
                }
    if extra:
        directive.update(extra)

    ret = Job.submit_desktop_job(action, directive, desktop_resource_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def check_desktop_snapshot_vaild(snapshot_ids):

    ctx = context.instance()
    new_snapshot_ids = []
    desktop_snapshot_ids = []

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
        return None

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

    return new_snapshot_ids

def register_snapshot_resource(sender, resources,snapshot_group_snapshot_ids=None):

    ctx = context.instance()
    new_snapshot_resources = {}
    desktop_snapshot_id = get_uuid(UUID_TYPE_SNAPSHOT_RESOURCET, ctx.checker)

    for desktop_resource_id, desktop_resource in resources.items():

        resource_name = desktop_resource.get("resource_name")
        resource_type = desktop_resource["resource_type"]
        resource_id = desktop_resource["resource_id"]
        snapshot_resource_info = dict(
                                  desktop_snapshot_id = desktop_snapshot_id,
                                  snapshot_group_snapshot_id = snapshot_group_snapshot_ids if snapshot_group_snapshot_ids else '',
                                  snapshot_name = "",
                                  snapshot_id= "",
                                  desktop_resource_id=desktop_resource_id,
                                  resource_name = resource_name,
                                  resource_type = resource_type,
                                  resource_id = resource_id,
                                  create_time = get_current_time(),
                                  status_time = get_current_time(),
                                  ymd= datetime.date.today(),
                                  owner = sender["owner"],
                                  zone = sender["zone"]
                                  )
        new_snapshot_resources[desktop_resource_id] = snapshot_resource_info

    # register snapshot_resource
    if not ctx.pg.batch_insert(dbconst.TB_SNAPSHOT_RESOURCE, new_snapshot_resources):
        logger.error("insert newly created snapshot for [%s] to db failed" % (new_snapshot_resources))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    # return new_snapshot_resources.keys()
    return desktop_snapshot_id

def register_snapshot_disk_snapshot(sender, resources):

    ctx = context.instance()

    desktop_ids = []
    disk_ids = []

    for desktop_resource_id, _ in resources.items():
        prefix = desktop_resource_id.split("-")[0]
        if prefix in [UUID_TYPE_DESKTOP]:
            desktop_ids.append(desktop_resource_id)
        elif prefix in [UUID_TYPE_DESKTOP_DISK]:
            disk_ids.append(desktop_resource_id)
        else:
            continue

    # register snapshot_disk_snapshot
    new_snapshot_disk_snapshot = {}
    snapshot_disk_snapshot_id = get_uuid(UUID_TYPE_SNAPSHOT_DISK_SNAPSHOT, ctx.checker)
    for desktop_id in desktop_ids:
        for disk_id in disk_ids:
            snapshot_disk_snapshot_info = dict(
                snapshot_disk_snapshot_id=snapshot_disk_snapshot_id,
                desktop_id=desktop_id,
                disk_id=disk_id,
                create_time=get_current_time(),
                owner=sender["owner"],
                zone=sender["zone"]
            )

            new_snapshot_disk_snapshot[snapshot_disk_snapshot_id] = snapshot_disk_snapshot_info
            if not ctx.pg.batch_insert(dbconst.TB_SNAPSHOT_DISK_SNAPSHOT, new_snapshot_disk_snapshot):
                logger.error("insert newly created snapshot_disk_snapshot for [%s] to db failed" % (new_snapshot_disk_snapshot))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_SNAPSHOT_GROUP_SNAPSHOT_FAILED)

    return snapshot_disk_snapshot_id

def register_snapshot_group_snapshot(sender, snapshot_group_id):

    ctx = context.instance()

    new_snapshot_group_snapshot = {}
    snapshot_group_snapshot_id = get_uuid(UUID_TYPE_SNAPSHOT_GROUP_SNAPSHOT, ctx.checker)
    snapshot_group_snapshot_info = dict(
        snapshot_group_snapshot_id=snapshot_group_snapshot_id,
        snapshot_group_id=snapshot_group_id,
        transition_status="",
        status="",
        create_time=get_current_time(),
        owner=sender["owner"],
        zone=sender["zone"]
    )

    new_snapshot_group_snapshot[snapshot_group_snapshot_id] = snapshot_group_snapshot_info
    if not ctx.pg.batch_insert(dbconst.TB_SNAPSHOT_GROUP_SNAPSHOT, new_snapshot_group_snapshot):
        logger.error("insert newly created snapshot_group_snapshot for [%s] to db failed" % (new_snapshot_group_snapshot))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_SNAPSHOT_GROUP_SNAPSHOT_FAILED)

    return snapshot_group_snapshot_id

def check_desktop_snapshot(resource_ids):
    
    ctx = context.instance()
    
    desktop_snapshot_ids = []
    for resource_id in resource_ids:
        desktop_resource = ctx.pgm.get_resource_snapshot(resource_id, is_current=True)
        if not desktop_resource:
            logger.error("insert newly created snapshot for [%s] to db failed" % (resource_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
                
        desktop_snapshot_ids.extend(desktop_resource.keys())
        
    return desktop_snapshot_ids

def check_apply_desktop_snapshot_vaild(sender, snapshot_ids):
    
    ctx = context.instance()
    if snapshot_ids and not isinstance(snapshot_ids, list):
        snapshot_ids = [snapshot_ids]
    
    snapshots = ctx.pgm.get_desktop_snapshots(snapshot_ids)
    if not snapshots:
        logger.error("describe snapshot no found %s" % snapshot_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, snapshot_ids)

    # check desktop transition status
    ret = check_resource_transition_status(snapshots)
    if isinstance(ret, Error):
        return ret

    return snapshots

def check_snapshot_resource_limit(sender, resource_ids):
    ctx = context.instance()
    zone_id = sender["zone_id"]
    
    max_chain_count = ctx.zone_checker.get_resource_limit(zone_id, "max_chain_count")

    for resource_id in resource_ids:
        # Check the number of full backup chains
        ret = ctx.pgm.get_snapshot_id(desktop_resource=resource_id,snapshot_type=1)
        if not ret:
            return None
        snapshot_id = ret

        full_backup_chain_count = len(snapshot_id)

        # Check how many backup nodes are in the current backup chain
        ret = ctx.pgm.get_snapshot_id(desktop_resource=resource_id,head_chain=1,snapshot_type=1)
        if not ret:
            return None
        snapshot_id = ret

        ret = ctx.pgm.get_total_count(snapshot_id)
        if ret is not None:
            total_count = ret
            if total_count >= 3 and full_backup_chain_count >= 2:
                logger.error("snapshot exceed max chain count %s, %s" % (max_chain_count, total_count))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_SNAPSHOT_EXCEED_MAX_CHAIN_COUNT, (max_chain_count, total_count))
    return None

def check_snapshot_resource_valid(sender, desktop_resource_ids=None,snapshot_group_snapshot_ids=None):

    ctx = context.instance()
    desktop_snapshot_ids = []

    for desktop_resource_id in desktop_resource_ids:

        desktop_ids = []
        disk_ids = []
        resources = {}
        prefix = desktop_resource_id.split("-")[0]
        if prefix in [UUID_TYPE_DESKTOP]:
            desktop_ids = desktop_resource_id
            resources[desktop_resource_id] = {"resource_type": dbconst.RESTYPE_DESKTOP}
            if desktop_ids:

                desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,has_disk=True)
                if not desktops:
                    desktops = {}
                    logger.error("snapshot resource %s no instance" % desktop_ids)
                    return Error(ErrorCodes.PERMISSION_DENIED,
                                 ErrorMsg.ERR_MSG_SNAPSHOT_NO_DESKTOP_INSTANCE, desktop_ids)

                for desktop_id, desktop in desktops.items():
                    instance_id = desktop["instance_id"]
                    if not instance_id:
                        logger.error("snapshot resource %s no instance" % desktop_id)
                        return Error(ErrorCodes.PERMISSION_DENIED,
                                     ErrorMsg.ERR_MSG_SNAPSHOT_NO_DESKTOP_INSTANCE, desktop_id)
                    if desktop_id not in resources:
                        continue

                    resources[desktop_id].update({"resource_name": desktop["hostname"], "resource_id": instance_id})

                    save_disk = desktop["save_disk"]
                    if save_disk:
                        disk_set = desktop["disks"]
                        for disk in disk_set:
                            disk_id = disk["disk_id"]
                            disk_ids.append(disk_id)
                            resources[disk_id] = {"resource_type": dbconst.RESTYPE_DESKTOP_DISK}

                        if disk_ids:

                            disks = ctx.pgm.get_disks(disk_ids)
                            if not disks:
                                disks = {}

                            for disk_id, disk in disks.items():
                                volume_id = disk["volume_id"]
                                if not volume_id:
                                    continue

                                if disk_id not in resources:
                                    continue
                                resources[disk_id].update({"resource_name": disk["disk_name"], "resource_id": volume_id})

                    #register snapshot_resource db
                    ret = register_snapshot_resource(sender, resources,snapshot_group_snapshot_ids)
                    if isinstance(ret, Error):
                        return ret
                    desktop_snapshot_ids.append(ret)

    return desktop_snapshot_ids

def update_desktop_snapshot_attributes(snapshot_ids, snapshot_name, description):

    ctx = context.instance()
    if snapshot_ids and not isinstance(snapshot_ids, list):
        snapshot_ids = [snapshot_ids]

    snapshots = ctx.pgm.get_desktop_snapshots(snapshot_ids)
    if not snapshots:
        logger.error("describe snapshot no found %s" % snapshot_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, snapshot_ids)

    for snapshot_id,snapshot in snapshots.items():
        if snapshot_name is None and description is None:
            return None
        else:
            if snapshot_name == snapshot["snapshot_name"] and description == snapshot["description"]:
                return None

        update_info = {
                        "snapshot_name": snapshot_name,
                        "description": description
                        }

        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_SNAPSHOT, {snapshot_id: update_info}):
            logger.error("modify desktop snapshot attributes update db fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def update_snapshot_resource_attributes(desktop_snapshot_ids, snapshot_name):

    ctx = context.instance()
    if desktop_snapshot_ids and not isinstance(desktop_snapshot_ids, list):
        desktop_snapshot_ids = [desktop_snapshot_ids]

    snapshots = ctx.pgm.get_snapshot_resource(desktop_snapshot_ids)
    if not snapshots:
        logger.error("describe snapshot resource no found %s" % desktop_snapshot_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_snapshot_ids)

    for desktop_snapshot_id,snapshot in snapshots.items():
        if snapshot_name is None:
            return None
        else:
            if snapshot_name == snapshot["snapshot_name"]:
                return None

        update_info = {"snapshot_name": snapshot_name}
        if not ctx.pg.batch_update(dbconst.TB_SNAPSHOT_RESOURCE, {desktop_snapshot_id: update_info}):
            logger.error("modify snapshot resource attributes update db fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def apply_desktop_snapshots(sender, snapshots):
    
    ctx = context.instance()
    
    snapshot_ids = snapshots.keys()
    ret = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_ids)
    if ret is None:
        logger.error("resource describe snapshot fail %s" % snapshot_ids)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, snapshot_ids)

    return snapshot_ids

def capture_desktop_from_desktop_snapshot(sender, snapshots):

    ctx = context.instance()
    
    snapshot_ids = snapshots.keys()
    ret = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_ids)
    if ret is None:
        logger.error("resource describe snapshot fail %s" % snapshot_ids)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, snapshot_ids)

    return snapshot_ids

def create_disk_from_desktop_snapshot(sender, snapshots):
    ctx = context.instance()
    
    snapshot_ids = snapshots.keys()
    ret = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_ids)
    if ret is None:
        logger.error("resource describe snapshot fail %s" % snapshot_ids)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, snapshot_ids)

    return snapshot_ids

def get_snapshot_resource_name(desktop_resource_ids):

    ctx = context.instance()
    resource_name = {}
    desktop_ids = []
    disk_ids = []

    for desktop_resource_id in desktop_resource_ids:
        prefix = desktop_resource_id.split("-")[0]
        if prefix in [UUID_TYPE_DESKTOP]:
            desktop_ids.append(desktop_resource_id)
        elif prefix in [UUID_TYPE_DESKTOP_DISK]:
            disk_ids.append(desktop_resource_id)
        else:
            continue
    
    if desktop_ids:
        desktops = ctx.pgm.get_desktops(desktop_ids)
        if desktops:
            for desktop_id, desktop in desktops.items():
                hostname = desktop["hostname"]
                resource_name[desktop_id] = hostname
    
    if disk_ids:
        disks = ctx.pgm.get_disks(disk_ids)
        if disks:
            for disk_id, disk in disks.items():
                disk_name = disk["disk_name"]
                resource_name[disk_id] = disk_name
            
    return resource_name

def add_resource_to_snapshot_group(snapshot_group_id, desktop_resource_ids):

    ctx = context.instance()
    existed_desktop_resource_ids = []
    ret = ctx.pgm.get_snapshot_group_resources(snapshot_group_id, desktop_resource_ids)
    if ret:
        snapshot_group_resources = ret
        for desktop_resource_id,_ in snapshot_group_resources.items():
            existed_desktop_resource_ids.append(desktop_resource_id)
        logger.error("add resource to snapshot group %s, resource %s existed" % (snapshot_group_id, existed_desktop_resource_ids))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_ALREAY_EXISTED_SNAPSHOT_GROUP, (existed_desktop_resource_ids, snapshot_group_id))

    ret = ctx.pgm.get_snapshot_group_resources(desktop_resource_ids=desktop_resource_ids)
    if ret:
        for desktop_resource_id,snapshot_group_resource in ret.items():
            existed_snapshot_group_id = snapshot_group_resource["snapshot_group_id"]
            resource_name = snapshot_group_resource["resource_name"]
            snapshot_groups = ctx.pgm.get_snapshot_groups(snapshot_group_ids=existed_snapshot_group_id)
            if snapshot_groups:
                for snapshot_group_id,snapshot_group in snapshot_groups.items():
                    snapshot_group_name = snapshot_group.get("snapshot_group_name")
                    logger.error("add resource to snapshot group %s, resource %s existed" % (snapshot_group_name, resource_name))
                    return Error(ErrorCodes.PERMISSION_DENIED,
                                ErrorMsg.ERR_MSG_RESOURCE_ALREAY_EXISTED_SNAPSHOT_GROUP, (resource_name, snapshot_group_name))

    resource_names = get_snapshot_resource_name(desktop_resource_ids)
    new_snapshot_group_resource_info = {}
    for desktop_resource_id in desktop_resource_ids:

        snapshot_group_resource_info = dict(
                         snapshot_group_id=snapshot_group_id,
                         desktop_resource_id = desktop_resource_id,
                         resource_name = resource_names.get(desktop_resource_id, '')
                         )
        new_snapshot_group_resource_info[desktop_resource_id] = snapshot_group_resource_info

    if not ctx.pg.batch_insert(dbconst.TB_SNAPSHOT_GROUP_RESOURCE, new_snapshot_group_resource_info):
        logger.error("insert newly created snapshot group resource [%s] to db failed" % (snapshot_group_resource_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_SNAPSHOT_GROUP_RESOURCE_FAILED)

    return None

def delete_resource_from_snapshot_group(snapshot_group_id, desktop_resource_ids):

    ctx = context.instance()
    ret = ctx.pgm.get_snapshot_group_resources(snapshot_group_id,desktop_resource_ids)
    if not ret:
        logger.error("delete resource from snapshot group %s, resource %s not exist" % (snapshot_group_id, desktop_resource_ids))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_IN_SNAPSHOT_GROUP, (desktop_resource_ids, snapshot_group_id))

    delete_snapshot_group_resource_info = {}
    for desktop_resource_id in desktop_resource_ids:
        delete_snapshot_group_resource_info = dict(
                                snapshot_group_id=snapshot_group_id,
                                desktop_resource_id=desktop_resource_id
                                )
        if not ctx.pg.base_delete(dbconst.TB_SNAPSHOT_GROUP_RESOURCE, delete_snapshot_group_resource_info):
            logger.error("delete snapshot group resource [%s] to db failed" % (delete_snapshot_group_resource_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_SNAPSHOT_GROUP_RESOURCE_FAILED,snapshot_group_id)

    return None

def register_snapshot_group(sender, snapshot_group_name, description=None):

    ctx = context.instance()
    new_snapshot_group = {}
    snapshot_group_id = get_uuid(UUID_TYPE_SNAPHSOT_GROUP, ctx.checker)
    snapshot_group_info = dict(
                    snapshot_group_id = snapshot_group_id,
                    snapshot_group_name = snapshot_group_name,
                    create_time = get_current_time(False),
                    description = description if description else '',
                    zone = sender["zone"],
                    status = "normal"
                    )
    new_snapshot_group[snapshot_group_id] = snapshot_group_info

    if not ctx.pg.batch_insert(dbconst.TB_SNAPSHOT_GROUP, new_snapshot_group):
        logger.error("insert newly created snapshot group [%s] to db failed" % (new_snapshot_group))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_SNAPSHOT_GROUP_FAILED)
    
    return snapshot_group_id

def modify_snapshot_group_attributes(snapshot_group_id, snapshot_group_name, description):

    ctx = context.instance()
    ret = ctx.pgm.get_snapshot_groups(snapshot_group_id)
    if not ret:
        logger.error("snapshot group no found %s" % snapshot_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_SNAPSHOT_GROUP_NO_FOUND, snapshot_group_id)
    snapshot_groups = ret

    snapshot_group = snapshot_groups[snapshot_group_id]
    if snapshot_group_name is None and description is None:
        return None
    else:
        if snapshot_group_name == snapshot_group["snapshot_group_name"] and description == snapshot_group["description"]:
            return None

    update_snapshot_group = {}
    snapshot_group_info = dict(
                snapshot_group_name = snapshot_group_name,
                description = description if description else '',
                )
    update_snapshot_group[snapshot_group_id] = snapshot_group_info

    if not ctx.pg.batch_update(TB_SNAPSHOT_GROUP, update_snapshot_group):
        logger.error("modify snapshot group update db fail %s" % update_snapshot_group)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_SNAPSHOT_GROUP_FAILED)
    
    return None

def delete_snapshot_groups(snapshot_group_ids):

    ctx = context.instance()
    ret = ctx.pgm.get_snapshot_groups(snapshot_group_ids)
    if not ret:
        logger.error("snapshot group no found %s" % snapshot_group_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_SNAPSHOT_GROUP_NO_FOUND, snapshot_group_ids)
    snapshot_groups = ret

    # delete snapshot_group and snapshot_group_resource db
    for snapshot_group_id, _ in snapshot_groups.items():
        if not ctx.pg.delete(dbconst.TB_SNAPSHOT_GROUP_RESOURCE, snapshot_group_id):
            logger.error("delete snapshot group resource %s fail" % snapshot_group_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_SNAPSHOT_GROUP_RESOURCE_FAILED,snapshot_group_id)

        if not ctx.pg.delete(dbconst.TB_SNAPSHOT_GROUP, snapshot_group_id):
            logger.error("delete snapshot group %s fail" % snapshot_group_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_SNAPSHOT_GROUP_FAILED,snapshot_group_id)

    return None

def update_snapshot_resource_curr_chain(sender, resource_ids):

    ctx = context.instance()
    new_snapshots = {}

    desktop_resource = ctx.pgm.get_resource_snapshot(resource_ids)
    if not desktop_resource:
        return None

    for desktop_snapshot_id, _ in desktop_resource.items():
        update_info = dict(
            desktop_snapshot_id=desktop_snapshot_id,
            curr_chain=0,
            status_time=get_current_time()
        )
        new_snapshots[desktop_snapshot_id] = update_info

        if not ctx.pg.batch_update(dbconst.TB_SNAPSHOT_RESOURCE, new_snapshots):
            logger.error("update snapshot_resource %s fail " % desktop_snapshot_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_resource_describe_snapshots(sender, snapshot_ids):

    ctx = context.instance()

    ret = ctx.res.resource_describe_snapshots(sender["zone"], snapshot_ids)
    if not ret:
        logger.error("resource describe snapshot fail %s" % snapshot_ids)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, snapshot_ids)

    return snapshot_ids

def modify_desktop_snapshot_attributes(sender,snapshot_id, snapshot_name, description):

    ctx = context.instance()

    ret = ctx.res.resource_modify_snapshot_attributes(sender["zone"], snapshot_id, snapshot_name, description)
    if ret is None:
        logger.error("resource modify snapshot attributes fail %s" % snapshot_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, snapshot_id)

    return snapshot_id

# describe snapshot groups
def format_snapshot_groups(sender, snapshot_group_set, verbose=0):

    ctx = context.instance()
    for snapshot_group_id, _ in snapshot_group_set.items():
        if verbose:
            ret = ctx.pgm.get_snapshot_group_resource_detail(snapshot_group_id)
            if ret:
                snapshot_group_set[snapshot_group_id] = ret

        # get snapshot_group resource_count
        ret = ctx.pgm.get_snapshot_group_resources(snapshot_group_id=snapshot_group_id)
        if ret is None:
            resource_count = 0
        else:
            resource_count = len(ret)
        snapshot_group_set[snapshot_group_id]["resource_count"] = resource_count

    return snapshot_group_set

# describe snapshot_group_snapshots
def format_snapshot_group_snapshots(sender, desktop_snapshot_set):

    for snapshot_id, desktop_snapshot in desktop_snapshot_set.items():
        desktop_resource_id = desktop_snapshot["desktop_resource_id"]
        prefix = desktop_resource_id.split("-")[0]
        if prefix in [UUID_TYPE_DESKTOP_DISK]:
            del desktop_snapshot_set[snapshot_id]

    return desktop_snapshot_set

def get_resource_from_snapshot_group_resource(snapshot_group_id):
    ctx = context.instance()
    desktop_resource_ids = []

    ret = ctx.pgm.get_snapshot_group_resources(snapshot_group_id)
    if not ret:
        logger.error("snapshot group resource no found %s" % snapshot_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_SNAPSHOT_GROUP_RESOURCE_NO_FOUND, snapshot_group_id)

    snapshot_group_resources = ret
    for desktop_resource_id,_ in snapshot_group_resources.items():
        if desktop_resource_id in desktop_resource_ids:
            continue
        desktop_resource_ids.append(desktop_resource_id)

    return desktop_resource_ids

def update_snapshot_group_resource(snapshot_group_id, resource_ids, desktop_snapshot_ids):

    ctx = context.instance()

    for desktop_snapshot_id in desktop_snapshot_ids:
        ret = ctx.pgm.get_snapshot_resource(desktop_snapshot_id)
        if ret:
            snapshot_resources = ret
            for _,snapshot_resource in snapshot_resources.items():
                resource_id = snapshot_resource["desktop_resource"]

                condition = {"snapshot_group_id": snapshot_group_id, "resource_id": resource_id}

                update_info = dict(
                    desktop_snapshot_id=desktop_snapshot_id,
                )

                if not ctx.pg.base_update(dbconst.TB_SNAPSHOT_GROUP_RESOURCE, condition, update_info):
                    logger.error("update TB_SNAPSHOT_GROUP_RESOURCE error")
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_MODIFY_SNAPSHOT_GROUP_RESOURCE_FAILED,snapshot_group_id)

    return None

def get_snapshot_ids_from_snapshot_resource(snapshot_group_snapshot_ids):

    ctx = context.instance()

    snapshot_ids = []
    snapshot_resources = ctx.pgm.get_snapshot_resources(snapshot_group_snapshot_ids=snapshot_group_snapshot_ids)
    if not snapshot_resources:
        logger.error("describe snapshot_group_snapshot_id %s no found in desktop_snapshot" % (snapshot_group_snapshot_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, snapshot_group_snapshot_ids)

    for _,snapshot_resource in snapshot_resources.items():
        snapshot_id = snapshot_resource["snapshot_id"]
        snapshot_ids.append(snapshot_id)

    return snapshot_ids

def get_snapshot_group_snapshot_ids(snapshot_group_id):

    ctx = context.instance()
    snapshot_group_snapshot_ids = []
    snapshot_group_snapshots = ctx.pgm.get_snapshot_group_snapshots(snapshot_group_id=snapshot_group_id)

    if not snapshot_group_snapshots:
        logger.info("describe snapshot_group_snapshots no found in snapshot_group_snapshots %s" % (snapshot_group_id))
        return None

    for snapshot_group_snapshot_id,_ in snapshot_group_snapshots.items():
        snapshot_group_snapshot_ids.append(snapshot_group_snapshot_id)

    return snapshot_group_snapshot_ids

def get_root_snapshot_group_snapshot_ids(snapshot_group_id):

    ctx = context.instance()
    root_snapshot_group_snapshot_id = ctx.pgm.get_snapshot_group_snapshot_ids_order_by_create_time(snapshot_group_ids=snapshot_group_id)

    if not root_snapshot_group_snapshot_id:
        logger.info("describe snapshot_group_snapshots no found in snapshot_group_snapshots %s" % (snapshot_group_id))
        return None

    return root_snapshot_group_snapshot_id

def get_snapshot_ids_by_resource_ymd(desktop_resource_ids,ymd):

    ctx = context.instance()
    apply_snapshot_ids = []

    for desktop_resource_id in desktop_resource_ids:

        ret = ctx.pgm.get_snapshot_resources_snapshot_ids(desktop_resource_ids=desktop_resource_id,ymd=ymd)
        if ret is None:
            continue
        snapshot_resources = ret
        snapshot_ids = []
        for snapshot_id,_ in snapshot_resources.items():
            snapshot_ids.append(snapshot_id)

        # select the latest backup snapshot_id of the day
        ret = ctx.pgm.get_snapshot_resources_snapshot_ids_order_by_create_time(snapshot_ids=snapshot_ids)
        if ret:
            lastest_snapshot_id = ret
            apply_snapshot_ids.append(lastest_snapshot_id)

    return apply_snapshot_ids


def get_resource_from_desktop_snapshot(snapshot_ids):

    ctx = context.instance()
    desktop_ids = []

    ret = ctx.pgm.get_desktop_snapshots(snapshot_ids=snapshot_ids)
    if not ret:
        logger.error("desktop snapshot  no found %s" % snapshot_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESKTOP_SNAPSHOT_NO_FOUND, snapshot_ids)
    desktop_snapshots = ret

    for _, desktop_snapshot in desktop_snapshots.items():
        desktop_resource_id = desktop_snapshot["desktop_resource_id"]
        prefix = desktop_resource_id.split("-")[0]
        if prefix in [UUID_TYPE_DESKTOP]:
            desktop_id = desktop_resource_id
            if desktop_id in desktop_ids:
                continue
            desktop_ids.append(desktop_id)
        elif prefix in [UUID_TYPE_DESKTOP_DISK]:
            disk_id = desktop_resource_id
            ret = ctx.pgm.get_disks(disk_ids=disk_id)
            if not ret:
                continue
            desktop_disks = ret
            for disk_id,disk in desktop_disks.items():
                desktop_id = disk["desktop_id"]
                if desktop_id in desktop_ids:
                    continue
                desktop_ids.append(desktop_id)

    return desktop_ids

def check_desktop_resource_valid(sender, desktop_resource_ids=None):

    ctx = context.instance()
    for desktop_resource_id in desktop_resource_ids:
        desktop_ids = desktop_resource_id
        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids)
            if not desktops:
                logger.error("desktop_resource %s no instance" % desktop_ids)
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_SNAPSHOT_NO_DESKTOP_INSTANCE, desktop_ids)
    return None

def check_snapshot_group(sender, snapshot_group_ids=None):

    ctx = context.instance()
    if snapshot_group_ids and not isinstance(snapshot_group_ids, list):
        snapshot_group_ids = [snapshot_group_ids]

    for snapshot_group_id in snapshot_group_ids:
        snapshot_groups = ctx.pgm.get_snapshot_groups(snapshot_group_ids=snapshot_group_id)
        if not snapshot_groups:
            logger.error("snapshot_groups %s no found" % (snapshot_group_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_SNAPSHOT_GROUP_NO_FOUND, snapshot_group_id)
    return None

# format_desktop_snapshots
def format_desktop_snapshots(sender, desktop_snapshot_set,snapshot_type=None):

    ctx = context.instance()
    for snapshot_id, desktop_snapshot in desktop_snapshot_set.items():
        desktop_resource_id = desktop_snapshot["desktop_resource_id"]
        ret = ctx.pgm.get_desktop_snapshots_snapshot_ids(desktop_resource_ids=desktop_resource_id,root_ids='',snapshot_type=snapshot_type)
        if ret:
            desktop_snapshots = ret
            for snapshot_id,desktop_snapshot in desktop_snapshots.items():
                desktop_snapshot_set[snapshot_id] = desktop_snapshot
            break
        else:
            break

    return desktop_snapshot_set

# format_desktop_snapshots_ymd
def format_desktop_snapshots_ymd(sender, desktop_snapshot_set):

    ctx = context.instance()
    for snapshot_id, desktop_snapshot in desktop_snapshot_set.items():
        desktop_resource_id = desktop_snapshot["desktop_resource_id"]
        ret = ctx.pgm.get_snapshot_resources_snapshot_ids(desktop_resource_ids=desktop_resource_id,snapshot_ids=snapshot_id)
        if ret:
            snapshot_resources = ret
            for snapshot_id,snapshot_resource in snapshot_resources.items():
                desktop_snapshot_set[snapshot_id]['ymd'] = snapshot_resource["ymd"]

    return desktop_snapshot_set

def check_desktop_snapshot_ids_vaild(snapshot_ids):

    ctx = context.instance()
    desktop_snapshot_ids = []

    for snapshot_id in snapshot_ids:

        ret = ctx.pgm.get_desktop_snapshots(snapshot_ids=snapshot_id)
        if ret is None:
            continue
        desktop_snapshots = ret
        for _, desktop_snapshot in desktop_snapshots.items():
            desktop_snapshot_id = desktop_snapshot["desktop_snapshot_id"]
            if desktop_snapshot_id in desktop_snapshot_ids:
                continue
            desktop_snapshot_ids.append(desktop_snapshot_id)

    if not desktop_snapshot_ids:
        return None

    return desktop_snapshot_ids

def get_snapshot_group_id_from_snapshot_group_snapshot_ids(snapshot_group_snapshot_ids):

    ctx = context.instance()
    snapshot_group_id = []

    snapshot_group_snapshots = ctx.pgm.get_snapshot_group_snapshots(snapshot_group_snapshot_id=snapshot_group_snapshot_ids)
    if not snapshot_group_snapshots:
        logger.error("describe snapshot_group_snapshot_id %s no found in desktop_snapshot" % (snapshot_group_snapshot_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, snapshot_group_snapshot_ids)

    for _,snapshot_group_snapshot in snapshot_group_snapshots.items():
        snapshot_group_id = snapshot_group_snapshot["snapshot_group_id"]
        break

    return snapshot_group_id

def check_desktop_snapshot_transition_status(sender, desktop_resource_ids):

    ctx = context.instance()
    desktop_snapshots = ctx.pgm.get_desktop_snapshots(desktop_resource_ids=desktop_resource_ids)
    if not desktop_snapshots:
        return None

    # check desktop transition status
    ret = check_resource_transition_status(desktop_snapshots)
    if isinstance(ret, Error):
        return ret

    return None

def check_snapshot_group_status(sender, snapshot_group_id):

    ctx = context.instance()
    ret = ctx.pgm.get_snapshot_groups(snapshot_group_ids=snapshot_group_id)
    if not ret:
        logger.error("snapshot group no found %s" % snapshot_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_SNAPSHOT_GROUP_NO_FOUND, snapshot_group_id)
    snapshot_groups = ret

    for snapshot_group_id,snapshot_group in snapshot_groups.items():
        status = snapshot_group.get("status")
        if const.SNAPSHOT_GROUP_STATUS_NORMAL != status:
            logger.error("snapshot_group [%s] is [%s], please try later" % (snapshot_group_id, status))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_RESOURCE_IN_TRANSITION_STATUS, (snapshot_group_id, status))

    return None
