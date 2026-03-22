import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS
)
import db.constants as dbconst
import constants as const
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success
)
from utils.misc import get_columns
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.zone.zone as Zone
import api.user.user as APIUser
from utils.net import is_port_open

def handle_describe_desktop_zones(req):

    ctx = context.instance()
    sender = req["sender"]
    
    zone_ids = req.get("zones")
    
    filter_conditions = build_filter_conditions(req, dbconst.TB_DESKTOP_ZONE)
    if zone_ids:
        filter_conditions["zone_id"] = zone_ids
    
    ret = Zone.check_describe_desktop_zones(sender, zone_ids)

    if ret is None:
        rep = {'total_count': 0} 
        return return_items(req, None, "zone", **rep)
    
    if ret:
        filter_conditions["zone_id"] = ret
    
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_ZONE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_DESKTOP_ZONE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_DESKTOP_ZONE]

    zone_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_ZONE, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(dbconst.TB_DESKTOP_ZONE, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )

    if zone_set is None:
        logger.error("describe zone failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    Zone.format_zone_user_role(sender, zone_set)

    verbose = req.get("verbose", 0)
    if verbose:
        if APIUser.is_normal_console(sender):
            Zone.format_normal_user_desktop_zones(sender, zone_set)
        else:
            Zone.format_desktop_zones(sender, zone_set)

    if APIUser.is_global_admin_user(sender):
        Zone.init_zone_info(sender, zone_set)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_ZONE, filter_conditions)
    if total_count is None:
        logger.error("get zone config count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count}

    return return_items(req, zone_set, "zone", **rep)

def handle_refresh_desktop_zones(req):

    ctx = context.instance()
    sender = req["sender"]

    zone_ids = req.get("zones")

    filter_conditions = build_filter_conditions(req, dbconst.TB_DESKTOP_ZONE)
    if zone_ids:
        filter_conditions["zone_id"] = zone_ids

    ret = Zone.check_describe_desktop_zones(sender, zone_ids)
    if ret is None:
        rep = {'total_count': 0}
        return return_items(req, None, "zone", **rep)

    if ret:
        filter_conditions["zone_id"] = ret

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_ZONE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_DESKTOP_ZONE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_DESKTOP_ZONE]

    zone_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_ZONE, filter_conditions, display_columns,
                                    sort_key=get_sort_key(dbconst.TB_DESKTOP_ZONE, req.get("sort_key")),
                                    reverse=get_reverse(req.get("reverse")),
                                    offset=req.get("offset", 0),
                                    limit=req.get("limit", DEFAULT_LIMIT),
                                    )
    if zone_set is None:
        logger.error("describe zone failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    Zone.format_zone_user_role(sender, zone_set)

    verbose = req.get("verbose", 0)
    if verbose:
        Zone.format_desktop_zones(sender, zone_set)

    if APIUser.is_global_admin_user(sender):
        ret = Zone.refresh_other_desktop_server_host_zone_info()
        if not ret:
            logger.error("refresh_other_desktop_server_host_zone_info failed")

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_ZONE, filter_conditions)
    if total_count is None:
        logger.error("get zone config count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 

    return return_items(req, zone_set, "zone", **rep)

def handle_create_desktop_zone(req):

    ret = ResCheck.check_request_param(req, ["zone_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    zone_id = req["zone_id"]
    ret = Zone.check_create_desktop_zone(zone_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    zone_name = req.get("zone_name")
    if zone_name:
        ret = Zone.check_create_desktop_zone_name(zone_name)
        if isinstance(ret, Error):
            return return_error(req, ret)

    ret = Zone.create_desktop_zone(zone_id, req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Zone.refresh_other_desktop_server_host_zone_info()
    if not ret:
        logger.error("refresh_other_desktop_server_host_zone_info failed")

    ret = {"zone_id": zone_id}
    return return_success(req, None, **ret)

def handle_modify_desktop_zone_attributes(req):
    
    ret = ResCheck.check_request_param(req, ["zone_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    zone_id = req["zone_id"]
    
    ret = Zone.check_desktop_zone_vaild(zone_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    need_maint_columns = get_columns(req, ["zone_name", "description"])
    if need_maint_columns:
        ret = Zone.modify_desktop_zone_attributes(zone_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Zone.refresh_other_desktop_server_host_zone_info()
        if not ret:
            logger.error("refresh_other_desktop_server_host_zone_info failed")
    
    return return_success(req, None)

def handle_delete_desktop_zones(req):
    
    ret = ResCheck.check_request_param(req, ["zones"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    zone_ids = req["zones"]
    
    ret = Zone.check_delete_desktop_zone(zone_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = Zone.delete_desktop_zones(zone_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Zone.refresh_other_desktop_server_host_zone_info()
    if not ret:
        logger.error("refresh_other_desktop_server_host_zone_info failed")

    return return_success(req, None)

def handle_modify_desktop_zone_resource_limit(req):

    ret = ResCheck.check_request_param(req, ["zone_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    zone_id = req["zone_id"]

    ret = Zone.check_modify_desktop_zone_resource_limit(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_maint_columns = ret

    if need_maint_columns:
        ret = Zone.modify_desktop_zone_resource_limit(zone_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Zone.refresh_other_desktop_server_host_zone_info()
        if not ret:
            logger.error("refresh_other_desktop_server_host_zone_info failed")
    
    return return_success(req, None)

def handle_modify_desktop_zone_connection(req):

    ctx = context.instance()

    ret = ResCheck.check_request_param(req, ["zone_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    zone_id = req["zone_id"]

    ret = Zone.check_modify_desktop_zone_connection(zone_id, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_maint_columns = ret

    zone_depoly = ctx.zone_deploy
    if const.DEPLOY_TYPE_STANDARD == zone_depoly:
        ret = Zone.set_zone_connection_host(zone_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    if need_maint_columns:
        ret = Zone.modify_desktop_zone_connection(zone_id, need_maint_columns)
        if isinstance(ret, Error):
            Zone.reset_zone_connection_host(zone_id, need_maint_columns)
            return return_error(req, ret)

        ret = Zone.refresh_other_desktop_server_host_zone_info()
        if not ret:
            logger.error("refresh_other_desktop_server_host_zone_info failed")

    # ssh keypair
    ret = ctx.pgm.get_zone_connection(zone_id)
    if not ret:
        logger.error("no found zone connection %s" % zone_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)
    zone_connection = ret
    keypair_name = "%s-%s" % (zone_id, const.ZONE_SSH_KEY_PAIR_NAME_SUFFIX)
    owner = zone_connection["account_user_id"]
    ret = ctx.res.resource_describe_keypairs(zone_id, owner, keypair_name)
    if not ret:
        ret = ctx.res.resource_create_keypair(zone_id, owner, keypair_name)
        logger.info("create keypair return: %s" % ret)
        if ret:
            keypair = ret
            Zone.set_zone_keypair(zone_id, keypair)
        else:
            logger.error("create new ssh key pairs error.")

    return return_success(req, None)

def handle_modify_desktop_zone_citrix_connection(req):

    ret = ResCheck.check_request_param(req, ["zone_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    zone_id = req["zone_id"]
    host = req.get("host")
    ret = Zone.check_desktop_zone_citrix_connection_host(host,ignore_zone=zone_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = Zone.check_modify_desktop_zone_citrix_connection(zone_id, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_maint_columns = ret

    if need_maint_columns:
        ret = Zone.modify_desktop_zone_citrix_connection(zone_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Zone.refresh_other_desktop_server_host_zone_info()
        if not ret:
            logger.error("refresh_other_desktop_server_host_zone_info failed")
    
    return return_success(req, None)

def handle_describe_instance_class_disk_type(req):

    ctx = context.instance()
    sender = req["sender"]

    instance_class = req.get("instance_class")
    disk_type = req.get("disk_type")

    filter_conditions = build_filter_conditions(req, dbconst.TB_INSTANCE_CLASS_DISK_TYPE)
    if instance_class is not None:
        filter_conditions["instance_class"] = instance_class

    if disk_type is not None:
        filter_conditions["disk_type"] = disk_type

    filter_conditions["zone_deploy"] = ctx.zone_deploy
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_INSTANCE_CLASS_DISK_TYPE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_INSTANCE_CLASS_DISK_TYPE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_INSTANCE_CLASS_DISK_TYPE]

    instance_class_disk_type_set = ctx.pg.get_by_filter(dbconst.TB_INSTANCE_CLASS_DISK_TYPE, filter_conditions, display_columns,
                                    sort_key=get_sort_key(dbconst.TB_INSTANCE_CLASS_DISK_TYPE, req.get("sort_key")),
                                    reverse=get_reverse(req.get("reverse")),
                                    offset=req.get("offset", 0),
                                    limit=req.get("limit", DEFAULT_LIMIT),
                                    )
    if instance_class_disk_type_set is None:
        logger.error("describe instance_class_disk_type failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_INSTANCE_CLASS_DISK_TYPE, filter_conditions)
    if total_count is None:
        logger.error("get instance_class_disk_type count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, instance_class_disk_type_set, "instance_class_disk_type", **rep)

def handle_describe_gpu_class_type(req):

    ctx = context.instance()
    sender = req["sender"]

    gpu_class_key = req.get("gpu_class_key")
    gpu_class = req.get("gpu_class")

    filter_conditions = build_filter_conditions(req, dbconst.TB_GPU_CLASS_TYPE)
    if gpu_class_key is not None:
        filter_conditions["gpu_class_key"] = gpu_class_key

    if gpu_class is not None:
        filter_conditions["gpu_class"] = gpu_class

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_GPU_CLASS_TYPE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_GPU_CLASS_TYPE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_GPU_CLASS_TYPE]

    gpu_class_type_set = ctx.pg.get_by_filter(dbconst.TB_GPU_CLASS_TYPE, filter_conditions, display_columns,
                                    sort_key=get_sort_key(dbconst.TB_GPU_CLASS_TYPE, req.get("sort_key")),
                                    reverse=get_reverse(req.get("reverse")),
                                    offset=req.get("offset", 0),
                                    limit=req.get("limit", DEFAULT_LIMIT),
                                    )

    if gpu_class_type_set is None:
        logger.error("describe gpu_class_typ failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_GPU_CLASS_TYPE, filter_conditions)
    if total_count is None:
        logger.error("get gpu_class_typ count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, gpu_class_type_set, "gpu_class_type", **rep)

def handle_check_network_connection(req):

    ret = ResCheck.check_request_param(req, ["ip_addr", "port"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ip_addr = req["ip_addr"]
    port = req["port"]

    status = const.SERVICE_STATUS_CONN_ACTIVE
    if not is_port_open(ip_addr, port):
        status = const.SERVICE_STATUS_CONN_UNREACHABLE

    resp = {'service_status': status}
    return return_success(req, None, **resp)

def handle_check_gpu_config(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["zone_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = Zone.check_gpu_config(sender)
    if not ret:
        ret = []

    resp = {'gpu_info': ret}
    return return_success(req, None, **resp)
