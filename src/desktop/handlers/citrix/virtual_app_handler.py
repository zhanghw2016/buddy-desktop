

import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS,
    TB_BROKER_APP,
    TB_BROKER_APP_GROUP
)
from utils.misc import get_columns
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
    is_global_admin_user,
    is_console_admin_user,
)
from db.data_types import NotType
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import constants as const
import db.constants as dbconst
from log.logger import logger
from utils.json import json_load
import resource_control.desktop.desktop_group as DesktopGroup
import resource_control.desktop.resource_permission as ResCheck
import resource_control.permission as Permission
import resource_control.citrix.virtual_app as VirtualApp

def handle_create_app_desktop_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_group_name", "managed_resource"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_group_name = req["desktop_group_name"]
    ret = DesktopGroup.check_desktop_group_name(sender["zone"], desktop_group_name)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    # create desktop group
    ret = DesktopGroup.register_app_desktop_group(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_group_id = ret
    
    job_uuid = None

    is_load = req.get("is_load", 0)
    if not is_load:
        ret = DesktopGroup.send_desktop_group_job(sender, desktop_group_id, const.JOB_ACTION_CREATE_DESKTOP_GROUP)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    # register resource permission
    Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_GROUP, desktop_group_id, sender["zone"], dbconst.RES_SCOPE_DELETE)

    # return the desktop group id
    ret = {'desktop_group': desktop_group_id}
    return return_success(req, None, job_uuid, **ret)

def handle_describe_app_computes(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["search_word"])
    if isinstance(ret, Error):
        rep = {'total_count': 0}
        return return_items(req, None, "app_computes", **rep)

    search_word = req["search_word"]
    
    ret = VirtualApp.search_app_computes(sender["zone"], search_word)
    
    total_count = len(ret) if ret is not None else 0
    
    rep = {'total_count': total_count}
    return return_items(req, ret, "app_computes", **rep)

def handle_add_compute_to_desktop_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_group", "instance_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_group_id = req["desktop_group"]
    instance_id = req["instance_id"]
    
    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id,None, desktop_group_type=const.DG_TYPE_CITIRX)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]
    
    ret = VirtualApp.search_app_computes(sender["zone"], instance_id)
    if not ret:
        logger.error("instance %s %s no found" % (instance_id))
        return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_NO_FOUND_APP_INSTANCE_SERVER, (instance_id)))
    
    machine_info = ret.get(instance_id)
    if machine_info:
        ret = VirtualApp.add_machine_to_desktop_group(sender, machine_info, desktop_group)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

def handle_describe_app_startmemus(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["delivery_group", "desktop"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    delivery_group_id = req["delivery_group"]
    desktop_id = req["desktop"]

    ret = VirtualApp.check_app_delivery_group(sender, delivery_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = VirtualApp.check_app_compute(sender, desktop_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop = ret
    
    ret = VirtualApp.get_machine_app_startmemu(sender["zone"], desktop["hostname"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    total_count = len(ret) if ret else 0
    
    rep = {'total_count': total_count}
    return return_items(req, ret, "app_computes", **rep)

def handle_describe_broker_apps(req):

    ctx = context.instance()
    sender = req["sender"]
    
    broker_app_ids = req.get("broker_apps")
    # get delivery group set
    filter_conditions = build_filter_conditions(req, TB_BROKER_APP)
    if broker_app_ids:
        filter_conditions["broker_app_id"] = broker_app_ids

    filter_delivery_groups = req.get("filter_delivery_groups")
    if filter_delivery_groups:
        ret = ctx.pgm.get_delivery_group_broker_apps(filter_delivery_groups)
        if ret:
            filter_conditions["broker_app_id"] = NotType(ret.keys())
    
    delivery_group_id = req.get("delivery_group")
    if delivery_group_id:
        ret = ctx.pgm.get_delivery_group_broker_apps(delivery_group_id)
        if ret:
            filter_conditions["broker_app_id"] = ret.keys()
        else:
            filter_conditions["broker_app_id"] = None

    broker_app_names = req.get("broker_app_names")
    if broker_app_names:
        ret = ctx.pgm.get_table_ignore_case(TB_BROKER_APP, 'display_name', broker_app_names,sender["zone"])
        if ret:
            _app_ids = []
            for broker_app in ret:
                broker_app_id = broker_app["broker_app_id"]
                _app_ids.append(broker_app_id)
            filter_conditions["broker_app_id"] = _app_ids
        else:
            rep = {'total_count': 0} 
            return return_items(req, None, "broker_apps", **rep)
    
    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_BROKER_APP]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_BROKER_APP]
    else:
        display_columns = PUBLIC_COLUMNS[TB_BROKER_APP]
    
    broker_app_set = ctx.pg.get_by_filter(TB_BROKER_APP, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_BROKER_APP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if broker_app_set is None:
        logger.error("describe delivery group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    VirtualApp.format_broker_apps(broker_app_set)
    # get total count
    total_count = ctx.pg.get_count(TB_BROKER_APP, filter_conditions)
    if total_count is None:
        logger.error("describe delivery group total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count':total_count} 
    return return_items(req, broker_app_set, "broker_apps", **rep)

def handle_create_broker_apps(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["delivery_group", "desktop"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    is_startmenu = req.get("is_startmenu", 1)
    app_datas = req.get("app_datas")
    delivery_group_id = req["delivery_group"]
    desktop_id = req["desktop"]
    
    if app_datas:
        app_datas = json_load(app_datas)
    
    ret = VirtualApp.check_app_delivery_group(sender, delivery_group_id, desktop_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    delivery_group, desktop = ret
    
    ret = VirtualApp.check_broker_app_data(app_datas,sender["zone"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    app_datas = ret
    ret = VirtualApp.create_broker_apps(sender, delivery_group, desktop, app_datas, is_startmenu)
    if isinstance(ret, Error):
        return return_error(req, ret)
    broker_app_ids = ret
    
    ret = {'broker_apps': broker_app_ids}
    return return_success(req, None, **ret)

def handle_modify_broker_app(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["broker_app"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    broker_app_id = req["broker_app"]
    
    ret = VirtualApp.check_broker_app(sender, broker_app_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    broker_app = ret[broker_app_id]

    columns = get_columns(req, ["admin_display_name", "description", "normal_display_name"])
    if columns:

        ret = VirtualApp.modify_broker_app_attributes(sender, broker_app, columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_delete_broker_apps(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["broker_apps"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    broker_app_ids = req["broker_apps"]
    
    ret = VirtualApp.check_broker_app(sender, broker_app_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    broker_apps = ret
    
    ret = VirtualApp.delete_broker_apps(sender, broker_apps)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_attach_broker_app_to_delivery_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["delivery_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = ResCheck.check_request_param(req, ["broker_apps", "broker_app_groups"], is_or=True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    delivery_group_id = req["delivery_group"]
    broker_app_ids = req.get("broker_apps")
    broker_app_group_ids = req.get("broker_app_groups")
    
    ret = VirtualApp.check_broker_app(sender, broker_app_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = VirtualApp.check_broker_app_group(broker_app_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = VirtualApp.check_attach_delivery_group_broker_apps(delivery_group_id, broker_app_ids, broker_app_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    delivery_group = ret
    
    if broker_app_ids:
        ret = VirtualApp.attach_broker_app_to_delivery_group(sender, delivery_group, broker_app_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    if broker_app_group_ids:
        ret = VirtualApp.attach_broker_app_group_to_delivery_group(sender, delivery_group, broker_app_group_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_detach_broker_app_from_delivery_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["delivery_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ResCheck.check_request_param(req, ["broker_apps", "broker_app_groups"], is_or=True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    delivery_group_id = req.get("delivery_group")
    broker_app_ids = req.get("broker_apps")
    broker_app_group_ids = req.get("broker_app_groups")

    ret = VirtualApp.check_broker_app(sender, broker_app_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    broker_apps = ret

    ret = VirtualApp.check_broker_app_group(broker_app_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = VirtualApp.check_detach_broker_app_from_delivery_group(delivery_group_id, broker_app_ids, broker_app_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    delivery_group = ret
    
    if broker_app_ids:
        ret = VirtualApp.detach_broker_app_from_group(sender, broker_apps, delivery_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

    if broker_app_group_ids:
        for broker_app_group_id in broker_app_group_ids:
            ret = VirtualApp.detach_broker_app_group_from_delivery_group(sender, broker_app_group_id, delivery_group)
            if isinstance(ret, Error):
                return return_error(req, ret)

    return return_success(req, None)

def handle_create_broker_folder(req):
    
    
    
    return

def handle_delete_broker_folders(req):
    
    return

def handle_describe_broker_folers(req):
    
    
    return

def handle_create_broker_app_group(req):
    
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["broker_app_group_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    broker_app_group_name = req["broker_app_group_name"]
    
    ret = VirtualApp.check_broker_app_group_name(sender, broker_app_group_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = VirtualApp.create_broker_app_group(sender, broker_app_group_name, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    broker_app_group_id = ret
    ret = {'broker_app': broker_app_group_id}
    return return_success(req, None, **ret)

def handle_describe_broker_app_groups(req):

    ctx = context.instance()
    sender = req["sender"]
   
    # get delivery group set
    filter_conditions = build_filter_conditions(req, TB_BROKER_APP_GROUP)
    broker_app_group_ids = req.get("broker_app_groups")
    if broker_app_group_ids:
        filter_conditions["broker_app_group_id"] = broker_app_group_ids
    
    delivery_group_id = req.get("delivery_group")
    if delivery_group_id:
        ret = ctx.pgm.get_delivery_group_broker_app_groups(delivery_group_id, broker_app_group_ids)
        if not ret:
            filter_conditions["broker_app_group_id"] = None
        else:
            filter_conditions["broker_app_group_id"] =ret.keys()
    
    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_BROKER_APP_GROUP]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_BROKER_APP_GROUP]
    else:
        display_columns = PUBLIC_COLUMNS[TB_BROKER_APP_GROUP]
    
    broker_app_group_set = ctx.pg.get_by_filter(TB_BROKER_APP_GROUP, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_BROKER_APP_GROUP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if broker_app_group_set is None:
        logger.error("describe delivery group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    VirtualApp.format_broker_app_groups(broker_app_group_set)
    
    # get total count
    total_count = ctx.pg.get_count(TB_BROKER_APP_GROUP, filter_conditions)
    if total_count is None:
        logger.error("describe delivery group total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count':total_count} 
    return return_items(req, broker_app_group_set, "broker_app_groups", **rep)

def handle_delete_broker_app_groups(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["broker_app_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    broker_app_group_ids = req["broker_app_groups"]
    
    ret = VirtualApp.check_broker_app_group(broker_app_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    broker_app_groups = ret
    
    ret = VirtualApp.delete_broker_app_groups(sender, broker_app_groups)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_attach_broker_app_to_app_group(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["broker_app_group", "broker_apps"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    broker_app_group_id = req["broker_app_group"]
    broker_app_ids = req["broker_apps"]
    
    ret = VirtualApp.check_broker_app(sender, broker_app_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    broker_apps = ret
    
    ret = VirtualApp.check_broker_app_group(broker_app_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    broker_app_group = ret[broker_app_group_id]

    ret = VirtualApp.attach_broker_app_to_app_group(sender, broker_app_group, broker_apps)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_detach_broker_app_from_app_group(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["broker_apps", "broker_app_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    broker_app_group_id = req["broker_app_group"]
    broker_app_ids = req["broker_apps"]

    ret = VirtualApp.check_broker_app(sender, broker_app_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    broker_apps = ret

    ret = VirtualApp.check_broker_app_group(broker_app_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    broker_app_group = ret[broker_app_group_id]

    for _, broker_app in broker_apps.items():
        broker_app_group_name = broker_app_group["broker_app_group_name"]
        ret = VirtualApp.detach_broker_app_from_app_group(sender, broker_app, broker_app_group_name)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_refresh_broker_apps(req):
    
    sender = req["sender"]
    sync_type = req["sync_type"]
    
    if sync_type == "app":    
        ret = VirtualApp.refresh_broker_apps(sender)
        if isinstance(ret, Error):
            return return_error(req, ret)
    elif sync_type == "app_group":
        ret = VirtualApp.refresh_broker_app_groups(sender)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

