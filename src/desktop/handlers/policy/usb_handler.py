import context
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from resource_control.policy.usb import(
    create_usb_policy,
    modify_usb_policy,
    delete_usb_policy
    )
from common import (
    return_error,
    return_success,
    return_items,
    is_admin_user,
    is_admin_console,
    build_filter_conditions,
    get_sort_key,
    get_reverse
    )
from db.constants import TB_USB_POLICY, PUBLIC_COLUMNS, DEFAULT_LIMIT

def handle_create_desktop_usb_policy(req):
    if not is_admin_user(req['sender']):
        logger.error("only admin can create desktop usb policy")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    object_id = req.get("object_id")
    policy_type = req.get("policy_type") 
    if not object_id or not policy_type:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE, 
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE,("object_id", "policy_type")))
    priority = req.get("priority")
    if not object_id or not policy_type:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE, 
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE,("priority")))

    params = {"class_id": req.get("class_id", "-1"),
              "vendor_id": req.get("vendor_id", "-1"),
              "product_id": req.get("product_id", "-1"),
              "version_id": req.get("version_id", "-1"),
              "allow": req.get("allow", 1),
              "policy_type": policy_type,
              "priority": priority}

    usb_policy_id = create_usb_policy(object_id, params)
    if not usb_policy_id:
        logger.error("create usb policy error")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_CODE_MSG_CREATE_USB_POLICY_FAILED))

    return return_success(req, {'usb_policy_id': usb_policy_id})

def handle_modify_desktop_usb_policy(req):
    if not is_admin_user(req['sender']):
        logger.error("only admin can modify desktop usb policy")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    usb_policy_id = req.get("usb_policy_id")
    if not usb_policy_id:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE, 
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "priority"))
    params = {}
    if req.get("priority"):
        params["priority"] = req.get("priority")
    if req.get("class_id"):
        params["class_id"] = req.get("class_id")
    if req.get("vendor_id"):
        params["vendor_id"] = req.get("vendor_id")
    if req.get("product_id"):
        params["product_id"] = req.get("product_id")
    if req.get("version_id"):
        params["version_id"] = req.get("version_id")
    if req.get("allow") in [0, 1]:
        params["allow"] = req.get("allow")

    if not modify_usb_policy(usb_policy_id, params):
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_CODE_MSG_MODIFY_USB_POLICY_FAILED))

    return return_success(req, {'usb_policy_id': usb_policy_id})

def handle_delete_desktop_usb_policy(req):
    if not is_admin_user(req['sender']):
        logger.error("only admin can delete desktop usb policy")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    usb_policy_ids = req.get("usb_policy_ids")
    if not usb_policy_ids:
        return return_success(req, {'usb_policy_ids': []})

    if not delete_usb_policy(usb_policy_ids=usb_policy_ids):
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_CODE_MSG_DELETE_USB_POLICY_FAILED))
        
    return return_success(req, {'usb_policy_ids': usb_policy_ids})

def handle_describe_desktop_usb_policy(req):
    if not is_admin_user(req['sender']):
        logger.error("only admin can describe desktop usb policy")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    if not is_admin_console(req['sender']):
        logger.error("only admin console can describe desktop usb policy")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
    ctx = context.instance()

    filter_conditions = build_filter_conditions(req, TB_USB_POLICY)
    usb_policy_set = ctx.pg.get_by_filter(TB_USB_POLICY, filter_conditions, PUBLIC_COLUMNS[TB_USB_POLICY], 
                                    sort_key = get_sort_key(TB_USB_POLICY, req.get("sort_key")),
                                    reverse = get_reverse(req.get("reverse")),
                                    offset = req.get("offset", 0),
                                    limit = req.get("limit", DEFAULT_LIMIT),
                                    )
    if usb_policy_set is None:
        logger.error("describe desktop usb policy error.")
        return return_success(req, {"total_count": 0, "usb_policy_set":[]})

    total_count = ctx.pg.get_count(TB_USB_POLICY, filter_conditions)
    if total_count is None:
        logger.error("get usb policy count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count':total_count}

    return return_items(req, usb_policy_set, "usb_policy", **rep)

