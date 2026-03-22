import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    TB_SNAPSHOT_GROUP,
    TB_DESKTOP_SNAPSHOT
)
import constants as const 
from common import (
    build_filter_conditions,
    is_global_admin_user,
    is_console_admin_user,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
)
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.policy.snapshot as Snapshot
import resource_control.permission as Permission
import db.constants as dbconst

def handle_describe_desktop_snapshots(req):

    ctx = context.instance()
    sender = req["sender"]

    # get desktop snapshot set
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_SNAPSHOT)

    snapshot_ids = req.get("snapshots")
    if snapshot_ids:
        filter_conditions["snapshot_id"] = snapshot_ids

    desktop_resource_ids = req.get("desktop_resource")
    if desktop_resource_ids:
        filter_conditions["desktop_resource_id"] = desktop_resource_ids

    snapshot_type = req.get("snapshot_type")
    if snapshot_type is not None:
        filter_conditions["snapshot_type"] = snapshot_type

    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_SNAPSHOT]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_SNAPSHOT]
    else:
        display_columns = []

    desktop_snapshot_set = ctx.pg.get_by_filter(TB_DESKTOP_SNAPSHOT, filter_conditions, display_columns,
                                      sort_key = get_sort_key(TB_DESKTOP_SNAPSHOT, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )

    if desktop_snapshot_set is None:
        logger.error("describe desktop snapshot failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format desktop_snapshot
    Snapshot.format_desktop_snapshots(sender, desktop_snapshot_set,snapshot_type)

    # format desktop_snapshot ymd
    Snapshot.format_desktop_snapshots_ymd(sender, desktop_snapshot_set)

    # get total count
    total_count = len(desktop_snapshot_set)
    if total_count is None:
        logger.error("describe desktop snapshot total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count':total_count} 
    return return_items(req, desktop_snapshot_set, "desktop_snapshot", **rep)


def handle_create_desktop_snapshots(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["resources", "snapshot_group"], True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_resource_ids = req.get("resources")
    snapshot_group_id = req.get("snapshot_group")
    snapshot_name = req.get("snapshot_name","")
    is_full = req.get("is_full",0)
    desktop_snapshot_ids = []
    snapshot_group_snapshot_ids = ''

    if snapshot_group_id:

        ret = Snapshot.check_snapshot_group_status(sender, snapshot_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

        # register new snapshot_group_snapshot to generate snapshot_group_snapshot_id
        ret = Snapshot.register_snapshot_group_snapshot(sender, snapshot_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
        snapshot_group_snapshot_ids = ret

        # get desktop_resource_ids
        ret = Snapshot.get_resource_from_snapshot_group_resource(snapshot_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_resource_ids = ret

        # check desktop_snapshot transition_status valid
        ret = Snapshot.check_desktop_snapshot_transition_status(sender, desktop_resource_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        # check desktop_resource_ids valid
        ret = Snapshot.check_snapshot_resource_valid(sender, desktop_resource_ids,snapshot_group_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_snapshot_ids = ret
        extra = {"snapshot_name": snapshot_name, "is_full": is_full,"snapshot_group_snapshot":snapshot_group_snapshot_ids}

        # send desktop_snapshot job
        job_uuid = None
        if desktop_snapshot_ids:
            ret = Snapshot.send_desktop_snapshot_job(sender, desktop_snapshot_ids, snapshot_group_snapshot_ids,const.JOB_ACTION_CREATE_DESKTOP_SNAPSHOTS, extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret
        return return_success(req, None, job_uuid)
    else:
        # check desktop_snapshot transition_status valid
        ret = Snapshot.check_desktop_snapshot_transition_status(sender, desktop_resource_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        # check desktop_resource_ids valid
        ret = Snapshot.check_snapshot_resource_valid(sender, desktop_resource_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_snapshot_ids = ret

        extra = {"snapshot_name": snapshot_name,"is_full":is_full,"snapshot_group_snapshot":snapshot_group_snapshot_ids}

        # send desktop_snapshot job
        job_uuid = None
        if desktop_snapshot_ids:
            ret = Snapshot.send_desktop_snapshot_job(sender, desktop_snapshot_ids,desktop_resource_ids, const.JOB_ACTION_CREATE_DESKTOP_SNAPSHOTS,extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret
        return return_success(req, None, job_uuid)

def handle_modify_desktop_snapshot_attributes(req):

    sender = req["sender"]
    ctx = context.instance()
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    snapshot_id = req["snapshot"]
    snapshot_name = req.get("snapshot_name")
    description = req.get("description")

    ret = Snapshot.check_desktop_snapshot_vaild(snapshot_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Snapshot.check_resource_describe_snapshots(sender, snapshot_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Snapshot.modify_desktop_snapshot_attributes(sender,snapshot_id, snapshot_name, description)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = Snapshot.update_desktop_snapshot_attributes(snapshot_id, snapshot_name, description)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ctx.pgm.get_desktop_snapshot_id_from_snapshot_id(snapshot_id)
    desktop_snapshot_id = ret
    if desktop_snapshot_id:
        ret = Snapshot.update_snapshot_resource_attributes(desktop_snapshot_id, snapshot_name)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

def handle_delete_desktop_snapshots(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshots","snapshot_group_snapshots"],True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    snapshot_ids = req.get("snapshots")
    snapshot_group_snapshot_ids = req.get("snapshot_group_snapshots")
    desktop_snapshot_ids = []

    if snapshot_group_snapshot_ids:
        ret = Snapshot.get_snapshot_group_id_from_snapshot_group_snapshot_ids(snapshot_group_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.get_snapshot_ids_from_snapshot_resource(snapshot_group_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        new_snapshot_ids = ret

        # get desktop_resource_ids
        ret = Snapshot.get_resource_from_desktop_snapshot(new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_resource_ids = ret

        # check desktop_snapshot transition_status valid
        ret = Snapshot.check_desktop_snapshot_transition_status(sender, desktop_resource_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_resource_describe_snapshots(sender, new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_desktop_snapshot_ids_vaild(new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_snapshot_ids = ret
        extra = {"snapshot_group_snapshot": snapshot_group_snapshot_ids}

        job_uuid = None
        if desktop_snapshot_ids:
            ret = Snapshot.send_desktop_snapshot_job(sender, desktop_snapshot_ids, snapshot_group_snapshot_ids,const.JOB_ACTION_DELETE_DESKTOP_SNAPSHOTS,extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

        return return_success(req, None, job_uuid)

    else:
        ret = Snapshot.check_desktop_snapshot_vaild(snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        new_snapshot_ids = ret

        # get desktop_resource_ids
        ret = Snapshot.get_resource_from_desktop_snapshot(new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_resource_ids = ret

        # check desktop_snapshot transition_status valid
        ret = Snapshot.check_desktop_snapshot_transition_status(sender, desktop_resource_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_resource_describe_snapshots(sender, new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_desktop_snapshot_ids_vaild(new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_snapshot_ids = ret
        extra = {"snapshot_group_snapshot": snapshot_group_snapshot_ids}

        job_uuid = None
        if desktop_snapshot_ids:
            ret = Snapshot.send_desktop_snapshot_job(sender, desktop_snapshot_ids, desktop_resource_ids,const.JOB_ACTION_DELETE_DESKTOP_SNAPSHOTS,extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

        return return_success(req, None, job_uuid)

def handle_apply_desktop_snapshots(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshots","snapshot_group_snapshots","resources"],True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    snapshot_ids = req.get("snapshots")
    snapshot_group_snapshot_ids = req.get("snapshot_group_snapshots")
    desktop_resource_ids = req.get("resources")
    ymd = req.get("ymd")
    desktop_snapshot_ids = []

    if snapshot_group_snapshot_ids:
        ret = Snapshot.get_snapshot_group_id_from_snapshot_group_snapshot_ids(snapshot_group_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.get_snapshot_ids_from_snapshot_resource(snapshot_group_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        new_snapshot_ids = ret

        # get desktop_resource_ids
        ret = Snapshot.get_resource_from_desktop_snapshot(new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_resource_ids = ret
        
        # check desktop_snapshot transition_status valid
        ret = Snapshot.check_desktop_snapshot_transition_status(sender, desktop_resource_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_resource_describe_snapshots(sender, new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_desktop_snapshot_ids_vaild(new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_snapshot_ids = ret
        extra = {"snapshot_group_snapshot": snapshot_group_snapshot_ids}

        job_uuid = None
        if desktop_snapshot_ids:
            ret = Snapshot.send_desktop_snapshot_job(sender, desktop_snapshot_ids, snapshot_group_snapshot_ids,const.JOB_ACTION_APPLY_DESKTOP_SNAPSHOTS,extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

        return return_success(req, None, job_uuid)

    elif snapshot_ids:
        # get desktop_resource_ids
        ret = Snapshot.get_resource_from_desktop_snapshot(snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_resource_ids = ret

        # check desktop_snapshot transition_status valid
        ret = Snapshot.check_desktop_snapshot_transition_status(sender, desktop_resource_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_desktop_snapshot_vaild(snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        new_snapshot_ids = ret

        ret = Snapshot.check_resource_describe_snapshots(sender, new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_desktop_snapshot_ids_vaild(new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_snapshot_ids = ret
        extra = {"snapshot_group_snapshot": snapshot_group_snapshot_ids}

        job_uuid = None
        if desktop_snapshot_ids:
            ret = Snapshot.send_desktop_snapshot_job(sender, desktop_snapshot_ids, desktop_resource_ids,const.JOB_ACTION_APPLY_DESKTOP_SNAPSHOTS,extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

        return return_success(req, None, job_uuid)

    elif desktop_resource_ids:
        # check desktop_snapshot transition_status valid
        ret = Snapshot.check_desktop_snapshot_transition_status(sender, desktop_resource_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        # filter snapshot_id by desktop_resource and ymd
        ret = Snapshot.get_snapshot_ids_by_resource_ymd(desktop_resource_ids,ymd)
        if isinstance(ret, Error):
            return return_error(req, ret)
        snapshot_ids = ret

        ret = Snapshot.check_desktop_snapshot_vaild(snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        new_snapshot_ids = ret

        ret = Snapshot.check_resource_describe_snapshots(sender, new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Snapshot.check_desktop_snapshot_ids_vaild(new_snapshot_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_snapshot_ids = ret
        extra = {"snapshot_group_snapshot": snapshot_group_snapshot_ids}

        job_uuid = None
        if desktop_snapshot_ids:
            ret = Snapshot.send_desktop_snapshot_job(sender, desktop_snapshot_ids,desktop_resource_ids, const.JOB_ACTION_APPLY_DESKTOP_SNAPSHOTS,extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

        return return_success(req, None, job_uuid)

def handle_capture_desktop_from_desktop_snapshot(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot", "image_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    snapshot_id = req["snapshot"]
    image_name = req.get("image_name", "")

    ret = Snapshot.check_desktop_snapshot_vaild(snapshot_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Snapshot.check_resource_describe_snapshots(sender, snapshot_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    extra = {"image_name": image_name}
    
    ret = Snapshot.send_desktop_snapshot_job(sender, snapshot_id, const.JOB_ACTION_CAPTURE_INSTANCE_FROM_DESKTOP_SNAPSHOT,extra)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_create_disk_from_desktop_snapshot(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot", "disk_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    snapshot_id = req["snapshot"]
    disk_name = req["disk_name"]

    ret = Snapshot.check_desktop_snapshot_vaild(snapshot_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Snapshot.check_resource_describe_snapshots(sender, snapshot_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    extra = {"disk_name": disk_name}

    ret = Snapshot.send_desktop_snapshot_job(sender, snapshot_id,const.JOB_ACTION_CREATE_DISK_FROM_DESKTOP_SNAPSHOT, extra)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_uuid = ret
    return return_success(req, None, job_uuid)

def handle_describe_snapshot_groups(req):

    ctx = context.instance()
    sender = req["sender"]

    # get snapshot set
    filter_conditions = build_filter_conditions(req, TB_SNAPSHOT_GROUP)
    
    snapshot_group_ids = req.get("snapshot_groups")
    if snapshot_group_ids:
        filter_conditions["snapshot_group_id"] = snapshot_group_ids

    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_SNAPSHOT_GROUP]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_SNAPSHOT_GROUP]
    else:
        display_columns = []

    snapshot_group_set = ctx.pg.get_by_filter(TB_SNAPSHOT_GROUP, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_SNAPSHOT_GROUP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )

    if snapshot_group_set is None:
        logger.error("describe snapshot group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESCRIBE_SNAPSHOT_GROUP_FAILED))
    # format snapshot group
    Snapshot.format_snapshot_groups(sender, snapshot_group_set, req.get("verbose", 0))

    # get total count
    total_count = ctx.pg.get_count(TB_SNAPSHOT_GROUP, filter_conditions)
    if total_count is None:
        logger.error("describe snapshot group total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count':total_count} 
    return return_items(req, snapshot_group_set, "snapshot_group", **rep)

def handle_create_snapshot_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot_group_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    snapshot_group_name = req["snapshot_group_name"]
    description = req.get("description")

    ret = Snapshot.register_snapshot_group(sender, snapshot_group_name, description)
    if isinstance(ret, Error):
        return return_error(req, ret)
    snapshot_group_id = ret

    # register resource permission
    Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_SNAPSHOT_GROUP, snapshot_group_id, sender["zone"], dbconst.RES_SCOPE_DELETE)

    ret = {'snapshot_group': snapshot_group_id}
    return return_success(req, None, **ret)

def handle_modify_snapshot_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    snapshot_group_id = req["snapshot_group"]
    snapshot_group_name = req.get("snapshot_group_name")
    description = req.get("description")

    ret = Snapshot.check_snapshot_group_status(sender, snapshot_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = Snapshot.modify_snapshot_group_attributes(snapshot_group_id, snapshot_group_name, description)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_delete_snapshot_groups(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    snapshot_group_id = req["snapshot_groups"]
    is_delete_backup_resource = req.get("is_delete_backup_resource",0)
    desktop_snapshot_ids = []

    ret = Snapshot.check_snapshot_group_status(sender, snapshot_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    if is_delete_backup_resource:
        # check root snapshot_group_snapshot_id
        ret = Snapshot.get_root_snapshot_group_snapshot_ids(snapshot_group_id)
        if ret:
            root_snapshot_group_snapshot_id = ret
            ret = Snapshot.get_snapshot_ids_from_snapshot_resource(root_snapshot_group_snapshot_id)
            if isinstance(ret, Error):
                return return_error(req, ret)
            new_snapshot_ids = ret

            # get desktop_resource_ids
            ret = Snapshot.get_resource_from_desktop_snapshot(new_snapshot_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)
            desktop_resource_ids = ret

            # check desktop_snapshot transition_status valid
            ret = Snapshot.check_desktop_snapshot_transition_status(sender, desktop_resource_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)

            ret = Snapshot.check_resource_describe_snapshots(sender, new_snapshot_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)

            ret = Snapshot.check_desktop_snapshot_ids_vaild(new_snapshot_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)
            desktop_snapshot_ids = ret
            extra = {"snapshot_group_snapshot": root_snapshot_group_snapshot_id}
            
            job_uuid = None
            if desktop_snapshot_ids:
                ret = Snapshot.send_desktop_snapshot_job(sender, desktop_snapshot_ids, snapshot_group_id,const.JOB_ACTION_DELETE_DESKTOP_SNAPSHOTS,extra)
                if isinstance(ret, Error):
                    return return_error(req, ret)
                job_uuid = ret

            ret = Snapshot.delete_snapshot_groups(snapshot_group_id)
            if isinstance(ret, Error):
                return return_error(req, ret)
            # clear resource permisson
            Permission.clear_user_resource_scope(resource_ids=snapshot_group_id)

            return return_success(req, None, job_uuid)

        else:
            ret = Snapshot.delete_snapshot_groups(snapshot_group_id)
            if isinstance(ret, Error):
                return return_error(req, ret)
            # clear resource permisson
            Permission.clear_user_resource_scope(resource_ids=snapshot_group_id)

            return return_success(req, None)

    else:
        ret = Snapshot.delete_snapshot_groups(snapshot_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
        # clear resource permisson
        Permission.clear_user_resource_scope(resource_ids=snapshot_group_id)

        return return_success(req, None)

def handle_add_resource_to_snapshot_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot_group", "resources"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    snapshot_group_id = req["snapshot_group"]
    desktop_resource_ids = req["resources"]

    ret = Snapshot.check_snapshot_group_status(sender, snapshot_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Snapshot.check_desktop_resource_valid(sender, desktop_resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Snapshot.check_snapshot_group(sender, snapshot_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Snapshot.add_resource_to_snapshot_group(snapshot_group_id, desktop_resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_delete_resource_from_snapshot_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot_group", "resources"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    snapshot_group_id = req["snapshot_group"]
    desktop_resource_ids = req["resources"]

    ret = Snapshot.check_snapshot_group_status(sender, snapshot_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Snapshot.delete_resource_from_snapshot_group(snapshot_group_id, desktop_resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)


def handle_describe_snapshot_group_snapshots(req):

    ctx = context.instance()
    sender = req["sender"]

    # check request param
    ret = ResCheck.check_request_param(req, ["snapshot_group_snapshots"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    # get desktop snapshot set
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_SNAPSHOT)
    snapshot_group_snapshot_ids = req.get("snapshot_group_snapshots")

    # get snapshot_ids
    ret = Snapshot.get_snapshot_ids_from_snapshot_resource(snapshot_group_snapshot_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    snapshot_ids = ret
    if snapshot_ids:
        filter_conditions["snapshot_id"] = snapshot_ids

    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_SNAPSHOT]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_SNAPSHOT]
    else:
        display_columns = []

    desktop_snapshot_set = ctx.pg.get_by_filter(TB_DESKTOP_SNAPSHOT, filter_conditions, display_columns,
                                                sort_key=get_sort_key(TB_DESKTOP_SNAPSHOT, req.get("sort_key")),
                                                reverse=get_reverse(req.get("reverse")),
                                                offset=req.get("offset", 0),
                                                limit=req.get("limit", DEFAULT_LIMIT),
                                                )

    if desktop_snapshot_set is None:
        logger.error("describe desktop snapshot failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format snapshot_group_snapshots
    Snapshot.format_snapshot_group_snapshots(sender, desktop_snapshot_set)

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_SNAPSHOT, filter_conditions)
    if total_count is None:
        logger.error("describe desktop snapshot total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, desktop_snapshot_set, "snapshot_group_snapshots", **rep)
