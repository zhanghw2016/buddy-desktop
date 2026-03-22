import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS,
    TB_DELIVERY_GROUP
)
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
import constants as const
import db.constants as dbconst
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.citrix.delivery_group as DeliveryGroup
import resource_control.desktop.desktop as Desktop
import resource_control.user.apply_approve as ApplyApprove
import resource_control.permission as Permission
import api.user.user as APIUser

def handle_describe_delivery_groups(req):

    ctx = context.instance()
    sender = req["sender"]

    is_system = req.get("is_system", 0)

    if is_system:
        ret = DeliveryGroup.describe_system_delivery_groups(sender)
        rep = {'total_count':len(ret) if ret else 0} 
        return return_items(req, ret, "delivery_group", **rep)
    
    # get delivery group set
    filter_conditions = build_filter_conditions(req, TB_DELIVERY_GROUP)
    delivery_group_ids = req.get("delivery_groups")
    if delivery_group_ids:
        filter_conditions["delivery_group_id"] = delivery_group_ids
    
    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DELIVERY_GROUP]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DELIVERY_GROUP]
    else:
        display_columns = PUBLIC_COLUMNS[TB_DELIVERY_GROUP]
    
    delivery_group_set = ctx.pg.get_by_filter(TB_DELIVERY_GROUP, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_DELIVERY_GROUP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if delivery_group_set is None:
        logger.error("describe delivery group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    verbose = req.get("verbose", 0)
    Desktop.format_delivery_group_desktop(delivery_group_set, verbose)
        
    # get total count
    total_count = ctx.pg.get_count(TB_DELIVERY_GROUP, filter_conditions)
    if total_count is None:
        logger.error("describe delivery group total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count':total_count} 
    return return_items(req, delivery_group_set, "delivery_group", **rep)

def handle_create_delivery_group(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["delivery_group_name", "delivery_group_type", "allocation_type"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    delivery_group_name = req["delivery_group_name"]
    delivery_group_type = req["delivery_group_type"]
    allocation_type =  req["allocation_type"]
    description = req.get("description")
    user_ids = req.get("users")

    ret = DeliveryGroup.check_delivery_group_name(sender["zone"], delivery_group_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DeliveryGroup.register_delivery_group(sender, delivery_group_name, delivery_group_type, allocation_type, description, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    delivery_group_id = ret

    if user_ids:
        ret = DeliveryGroup.add_user_to_delivery_group(sender, delivery_group_id, user_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

    # register resource permission
    Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DELIVERY_GROUP, delivery_group_id, sender["zone"], dbconst.RES_SCOPE_DELETE)

    ret = {'delivery_group': delivery_group_id}
    return return_success(req, None, **ret)

def handle_modify_delivery_group_attributes(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["delivery_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    delivery_group_id = req["delivery_group"]
    delivery_group_name = req.get("delivery_group_name")
    description = req.get("description")
    desktop_hide_mode = req.get("desktop_hide_mode")
    ret = DeliveryGroup.modify_delivery_group_attributes(sender, delivery_group_id, delivery_group_name, description, desktop_hide_mode)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_delete_delivery_groups(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["delivery_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    delivery_group_ids = req["delivery_groups"]
    
    ret = DeliveryGroup.delete_delivery_groups(sender, delivery_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # clear resource in apply group
    ApplyApprove.clean_resource_in_apply_group(delivery_group_ids)

    # clear resource premisson
    Permission.clear_user_resource_scope(resource_ids=delivery_group_ids)

    return return_success(req, None)

def handle_load_delivery_groups(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["delivery_group_names"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    delivery_group_names = req["delivery_group_names"]
    
    ret = DeliveryGroup.check_delivery_group_name(sender["zone"], delivery_group_names, is_load=True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DeliveryGroup.load_system_delivery_groups(sender, delivery_group_names)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    delivery_group_ids = ret
    
    ret = {'delivery_group': delivery_group_ids}
    return return_success(req, None, **ret)

def handle_add_desktop_to_delivery_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["delivery_group", "desktop_user"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    delivery_group_id = req["delivery_group"]
    desktop_user = req["desktop_user"]

    ret = DeliveryGroup.build_delivery_group_desktop_user(sender, desktop_user)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_users = ret
    desktop_ids = desktop_users.keys()
    
    ret = DeliveryGroup.check_citrix_session_type(delivery_group_id, desktop_ids)
    if not ret:
        logger.error("delivery group type dismatch %s, %s" % (delivery_group_id, desktop_ids))
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_DELIVERY_GROUP_TYPE_DISMATCH))
    
    ret = DeliveryGroup.check_delivery_group_user(sender, delivery_group_id, desktop_users)
    if isinstance(ret, Error):
        return return_error(req, ret)
    delivery_group = ret

    ret = DeliveryGroup.check_attach_delivery_group_desktop(sender, delivery_group, desktop_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktops = ret

    ret = DeliveryGroup.add_desktop_to_delivery_group(sender, delivery_group, desktops, desktop_users)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    job_uuid = ret
    return return_success(req, None, job_uuid)

def handle_del_desktop_from_delivery_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktops"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_ids = req["desktops"]

    ret = DeliveryGroup.check_detach_delivery_group_desktop(desktop_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktops = ret
    ret = DeliveryGroup.del_desktop_from_delivery_group(sender, desktops)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_add_user_to_delivery_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["delivery_group", "users"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    delivery_group_id = req["delivery_group"]

    user_ids = req["users"]
    ret = DeliveryGroup.add_user_to_delivery_group(sender, delivery_group_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_del_user_from_delivery_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["delivery_group", "users"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    delivery_group_id = req["delivery_group"]
    user_ids = req["users"]

    ret = DeliveryGroup.del_user_from_delivery_group(sender, delivery_group_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_attach_desktop_to_delivery_group_user(req):

    ctx = context.instance()
    sender = req["sender"]
    zone_id = sender["zone"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop", "user_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_id = req["desktop"]
    user_ids = req.get("user_ids")

    ret = Desktop.check_desktop_vaild(desktop_id, check_trans_status=False)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop = ret[desktop_id]
    
    ret = APIUser.check_zone_user_vaild(ctx, zone_id, user_ids, const.USER_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    users = ret
    
    ret = DeliveryGroup.check_attach_desktop_to_delivery_group_user(sender, desktop, users)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    attach_users = ret
    if not attach_users:
        attach_users = {}
    
    for _, user in attach_users.items():
        ret = DeliveryGroup.attach_desktop_to_delivery_group_user(sender, desktop, user)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_detach_desktop_from_delivery_group_user(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_id = req["desktop"]
    user_ids = req.get("user_ids")

    ret = Desktop.check_desktop_vaild(desktop_id, check_trans_status=False)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop = ret[desktop_id]

    ret = DeliveryGroup.detach_desktop_from_delivery_group_user(sender, desktop, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_set_delivery_group_mode(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["delivery_group", "mode"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    delivery_group_id = req["delivery_group"]
    mode = req["mode"]

    ret = DeliveryGroup.set_delivery_group_mode(sender, delivery_group_id, mode)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_set_citrix_desktop_mode(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_id = req["desktop"]
    mode = req["mode"]

    ret = DeliveryGroup.set_citrix_desktop_mode(sender, desktop_id, mode)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)
