import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS
)
import db.constants as dbconst
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
)
from utils.json import json_load
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.module_custom.module_custom as ModuleCustom
import api.user.user as APIUser

def handle_describe_user_module_customs(req):
    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_MODULE_CUSTOM)
    module_custom_ids = req.get("module_customs")
    if module_custom_ids:
        filter_conditions["module_custom_id"] = module_custom_ids

    ret = ModuleCustom.check_module_custom_zone_scope(sender, module_custom_ids)
    if ret is None:
        rep = {'total_count': 0}
        return return_items(req, None, "module_custom", **rep)

    if ret:
        filter_conditions["module_custom_id"] = ret

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_MODULE_CUSTOM]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_MODULE_CUSTOM]
    else:
        display_columns = []

    module_custom_set = ctx.pg.get_by_filter(dbconst.TB_MODULE_CUSTOM, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_MODULE_CUSTOM, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if module_custom_set is None:
        logger.error("describe module custom failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format module_custom_set
    ModuleCustom.format_module_custom(sender, module_custom_set)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_MODULE_CUSTOM, filter_conditions)
    if total_count is None:
        logger.error("get module custom count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, module_custom_set, "module_custom", **rep)

def handle_create_user_module_custom(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["modify_contents","custom_name","zone_users"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    zone_users = json_load(req["zone_users"])

    ret = ModuleCustom.check_create_user_module_custom(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ModuleCustom.create_user_module_custom(sender, req,zone_users)
    if isinstance(ret, Error):
        return return_error(req, ret)

    module_custom_id = ret

    ret = {"module_custom_id": module_custom_id}
    return return_success(req, None, **ret)

def handle_modify_user_module_custom_attributes(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["module_customs","custom_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    module_custom_id = req.get("module_customs")
    custom_name = req.get("custom_name")
    description = req.get("description",'')

    ret = ModuleCustom.modify_module_custom_attributes(sender,module_custom_id,custom_name,description)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_modify_user_module_custom_configs(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["module_customs","modify_contents"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    module_custom_id = req.get("module_customs")
    ret = ModuleCustom.modify_module_custom_configs(sender,module_custom_id,req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_modify_modue_custom_zone_user(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["module_customs", "zone_users"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    zone_users = json_load(req["zone_users"])
    module_custom_id = req["module_customs"]

    ret = ModuleCustom.check_set_module_custom_zone_user(sender, module_custom_id, zone_users)
    if isinstance(ret, Error):
        return return_error(req, ret)

    if not ret:
        logger.error("request param %s format error" % "zone_users")
        return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                     ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED)

    zone_users = ret
    ret = ModuleCustom.modify_module_custom_zone_user(sender, module_custom_id, zone_users)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_delete_user_module_customs(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["module_customs"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    module_custom_ids = req.get("module_customs")

    ret = ModuleCustom.delete_user_module_customs(sender,module_custom_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_system_module_types(req):

    ctx = context.instance()
    sender = req["sender"]

    if ctx.module_type_set:
        module_type_set = ctx.module_type_set
        # get total count
        total_count = len(module_type_set)
        rep = {'total_count': total_count}
        return return_items(req, module_type_set, "module_type", **rep)

    filter_conditions = build_filter_conditions(req, dbconst.TB_MODULE_TYPE)
    item_key = req.get("item_key")
    if item_key:
        filter_conditions["item_key"] = item_key

    enable_module = req.get("enable_module", None)
    if enable_module is not None:
        filter_conditions["enable_module"] = enable_module

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_MODULE_TYPE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_MODULE_TYPE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_MODULE_TYPE]

    module_type_set = ctx.pg.get_by_filter(dbconst.TB_MODULE_TYPE, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_MODULE_CUSTOM, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if module_type_set is None:
        logger.error("describe system module type failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    ctx.module_type_set = module_type_set
    # get total count
    total_count = len(module_type_set)

    rep = {'total_count': total_count}
    return return_items(req, module_type_set, "module_type", **rep)
