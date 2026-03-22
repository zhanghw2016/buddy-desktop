import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    PUBLIC_COLUMNS,
    DEFAULT_LIMIT
)
import db.constants as dbconst
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
import resource_control.system_custom.system_custom as SystemCustom
import api.user.user as APIUser
import constants as const
import resource_control.auth.password_prompt as PasswordPrompt


def handle_describe_system_custom_configs(req):

    ctx = context.instance()
    sender = req["sender"]
    system_custom_set = {
                            'redefine_system_custom':
                                {
                                    'is_default': 0,
                                    'current_system_custom': 1,
                                    'system_custom_id': 'redefine_system_custom'
                                }
    }

    force_refresh = req.get("force_refresh",0)
    if force_refresh:
        # format system_custom_set
        SystemCustom.format_system_customs(sender, system_custom_set, req)
        ctx.system_custom_set = system_custom_set

    if ctx.system_custom_set:
        system_custom_set = ctx.system_custom_set
    else:
        # format system_custom_set
        SystemCustom.format_system_customs(sender, system_custom_set, req)
        ctx.system_custom_set = system_custom_set

    rep = {'total_count': 1}
    return return_items(req, system_custom_set, "system_custom", **rep)

def handle_modify_system_custom_config_attributes(req):

    ctx = context.instance()
    sender = req["sender"]

    # check request param
    ret = ResCheck.check_request_param(req, ["modify_contents"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    modify_contents = req.get("modify_contents")

    ret = SystemCustom.parse_modify_contents(modify_contents)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_modify_contents = ret

    ret = SystemCustom.modify_system_custom_config(sender,const.REDEFINE_SYSTEM_CUSTOM,need_modify_contents)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = SystemCustom.refresh_ctx_system_custom_set(sender)
    ret = SystemCustom.refresh_other_desktop_server_host_system_custom_configs_info()

    for _, system_custom_config in need_modify_contents.items():

        module_type = system_custom_config.get("module_type")
        if module_type == const.CUSTOM_MODULE_TYPE_PASSWORD_RESTORE:
            PasswordPrompt.update_have_password_answer_users()

    return return_success(req, None)

def handle_reset_system_custom_configs(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["module_type"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    module_type = req.get("module_type")
    item_key = req.get("item_key")

    ret = SystemCustom.parse_reset_system_custom_config(module_type,item_key)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_reset_system_custom_configs = ret

    ret = SystemCustom.reset_system_custom_configs(const.REDEFINE_SYSTEM_CUSTOM,need_reset_system_custom_configs)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = SystemCustom.refresh_ctx_system_custom_set(sender)
    ret = SystemCustom.refresh_other_desktop_server_host_system_custom_configs_info()

    return return_success(req, None)

