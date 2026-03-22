from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
from utils.id_tool import UUID_TYPE_MODULE_CUSTOM,UUID_TYPE_DESKTOP_USER_GROUP
import constants as const
from utils.id_tool import(
    get_uuid
)
from utils.misc import get_current_time
import api.user.user as APIUser

def parse_modify_contents(modify_contents):

    if not modify_contents:
        return None

    need_modify_contents = {}
    for modify_content in modify_contents:
        modify_content_list = modify_content.split("|")
        if len(modify_content_list) != 4:
            logger.error('modify module custom config parameters less 2')
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_MODULE_CUSTOM_CONFIG_COUNT, modify_content)
        need_modify_contents[modify_content_list[1]] = dict(
            module_type=modify_content_list[0],
            item_key=modify_content_list[1],
            item_value=modify_content_list[2],
            enable_module=modify_content_list[3]
        )

    return need_modify_contents

def format_module_custom(sender, module_custom_set):

    ctx = context.instance()

    zone_id = sender.get("zone_id")
    module_customs = {}
    zone_infos = ctx.pgm.get_zones()

    for module_custom_id, module_custom in module_custom_set.items():
        # get system module_type list
        system_module_types = ctx.pgm.get_module_types(enable_module=1)
        system_module_types_list = system_module_types.keys()

        # get module_custom_configs
        module_custom_configs = ctx.pgm.get_module_custom_configs(module_custom_ids=module_custom_id)

        #format module_custom_configs
        if module_custom_configs:
            for item_key,module_custom_config in module_custom_configs.items():
                if item_key not in system_module_types_list:
                    del module_custom_configs[item_key]

        if module_custom_configs:
            module_custom_set[module_custom_id]["module_custom_configs"] = module_custom_configs

        desktop_users = {}
        ret = ctx.pgm.get_module_custom_user(module_custom_ids=module_custom_id)
        if ret:
            user_ids = ret.keys()
            user_column = ["user_name", "user_id", "user_dn"]
            user_group_column = ["user_group_name", "user_group_id", "user_group_dn"]
            ret = ctx.pgm.get_user_and_user_group(user_ids, user_column, user_group_column)
            if ret:
                desktop_users = ret
        if APIUser.is_global_admin_user(sender):
            module_custom_zones = ctx.pgm.get_module_custom_zone(module_custom_ids=module_custom_id)
            if module_custom_zones:
                for zone_id, module_custom_zone in module_custom_zones.items():

                    zone = zone_infos.get(zone_id)
                    if zone:
                        module_custom_zone["zone_name"] = zone["zone_name"]

                    user_scope = module_custom_zone["user_scope"]
                    module_custom_zone["scope"] = user_scope
                    del module_custom_zone["user_scope"]
                    if user_scope == const.MODULE_CUSTOM_ZONE_SCOPE_ALL_ADMIN_ROLES:
                        continue

                    module_custom_users = ctx.pgm.get_module_custom_user(module_custom_ids=module_custom_id, zone_id=zone_id)

                    if not module_custom_users:
                        module_custom_users = {}

                    for user_id, module_custom_user in module_custom_users.items():

                        desktop_user = desktop_users.get(user_id)
                        if desktop_user:
                            module_custom_user.update(desktop_user)

                    module_custom_zone["user_ids"] = module_custom_users.values()

                module_custom["zone_scope"] = module_custom_zones.values()

            module_customs[module_custom_id] = module_custom

        elif APIUser.is_console_admin_user(sender):

            module_custom_zones = ctx.pgm.get_module_custom_zone(module_custom_ids=module_custom_id)
            if module_custom_zones:
                for zone_id, module_custom_zone in module_custom_zones.items():

                    zone = zone_infos.get(zone_id)
                    if zone:
                        module_custom_zone["zone_name"] = zone["zone_name"]

                    user_scope = module_custom_zone["user_scope"]
                    module_custom_zone["scope"] = user_scope
                    del module_custom_zone["user_scope"]
                    if user_scope == const.MODULE_CUSTOM_ZONE_SCOPE_ALL_ADMIN_ROLES:
                        continue

                    module_custom_users = ctx.pgm.get_module_custom_user(module_custom_ids=module_custom_id, zone_id=zone_id)
                    if not module_custom_users:
                        module_custom_users = {}

                    for user_id, module_custom_user in module_custom_users.items():

                        desktop_user = desktop_users.get(user_id)
                        if desktop_user:
                            module_custom_user.update(desktop_user)

                    module_custom_zone["user_ids"] = module_custom_users.values()

                module_custom["zone_scope"] = module_custom_zones.values()
            module_customs[module_custom_id] = module_custom

    return module_customs

def modify_module_custom_attributes(sender,module_custom_id,custom_name,description):

    ctx = context.instance()
    ret = ctx.pgm.get_module_customs(module_custom_ids=module_custom_id)
    if not ret:
        logger.error("module custom no found %s" % module_custom_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_MODULE_CUSTOM_NO_FOUND, module_custom_id)
    module_customs = ret

    module_custom = module_customs[module_custom_id]
    if custom_name is None and description is None:
        return None
    else:
        if custom_name == module_custom["custom_name"] and description == module_custom["description"]:
            return None

    update_module_custom = {}
    module_custom_info = dict(
        custom_name=custom_name,
        description=description if description else ''
    )
    update_module_custom[module_custom_id] = module_custom_info
    if not ctx.pg.batch_update(dbconst.TB_MODULE_CUSTOM, update_module_custom):
        logger.error("modify module custom update db fail %s" % update_module_custom)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_MODULE_CUSTOM_FAILED)

    return None

def delete_user_module_customs(sender,module_custom_ids):

    ctx = context.instance()
    ret = ctx.pgm.get_module_customs(module_custom_ids=module_custom_ids)
    if not ret:
        logger.error("module custom no found %s" % module_custom_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_MODULE_CUSTOM_NO_FOUND, module_custom_ids)
    module_customs = ret

    # delete module_custom module_custom_zone module_custom_user module_custom_config db
    for module_custom_id, _ in module_customs.items():
        if module_custom_id == const.DEFAULT_MODULE_CUSTOM:
            continue

        if not ctx.pg.delete(dbconst.TB_MODULE_CUSTOM, module_custom_id):
            logger.error("delete module custom %s fail" % module_custom_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_MODULE_CUSTOM_FAILED,module_custom_id)

        condition = {'module_custom_id': module_custom_id}
        if not ctx.pg.base_delete(dbconst.TB_MODULE_CUSTOM_ZONE, condition):
            logger.error("delete module custom zone %s fail" % module_custom_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_MODULE_CUSTOM_ZONE_FAILED,module_custom_id)

        ret = ctx.pgm.get_module_custom_user(module_custom_ids=module_custom_id)
        if ret:
            if not ctx.pg.base_delete(dbconst.TB_MODULE_CUSTOM_USER, condition):
                logger.error("delete module custom user %s fail" % module_custom_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DELETE_MODULE_CUSTOM_USER_FAILED,module_custom_id)

        if not ctx.pg.base_delete(dbconst.TB_MODULE_CUSTOM_CONFIG, condition):
            logger.error("delete module custom config %s fail" % module_custom_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_MODULE_CUSTOM_CONFIG_FAILED,module_custom_id)

    return None

def check_create_user_module_custom(sender, req):

    ctx = context.instance()
    custom_name = req.get("custom_name")
    ret = ctx.pgm.get_custom_name()
    if not ret:
        return custom_name

    if custom_name.upper() in ret:
        logger.error("custom_name already existd %s" % custom_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_CUSTOM_NAME_ALREADY_EXISTED, custom_name)
    return custom_name

def build_module_custom(req):

    module_custom = {}
    module_custom_key = ["custom_name", "description"]

    for key in module_custom_key:
        if key not in req:
            continue
        module_custom[key] = req[key]

    return module_custom

def modify_module_custom_configs(sender,module_custom_id,req):

    ctx = context.instance()
    modify_contents = req.get("modify_contents")
    ret = parse_modify_contents(modify_contents)
    if isinstance(ret, Error):
        return ret
    need_modify_contents = ret

    # update module_custom_config
    for item_key, module_custom_config in need_modify_contents.items():

        module_type = module_custom_config.get("module_type")
        item_value = module_custom_config.get("item_value")
        enable_module = module_custom_config.get("enable_module")

        ret = ctx.pgm.get_module_custom_configs(module_custom_ids=module_custom_id, module_type=module_type,item_key=item_key)
        if ret:
            conditions = dict(
                module_custom_id=module_custom_id,
                module_type=module_type,
                item_key=item_key
            )
            update_module_custom_config_info = dict(
                item_value=item_value,
                enable_module=enable_module,
                create_time=get_current_time()
            )
            if not ctx.pg.base_update(dbconst.TB_MODULE_CUSTOM_CONFIG, conditions, update_module_custom_config_info):
                logger.error("modify module custom config for [%s] to db failed" % (update_module_custom_config_info))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_MODULE_CUSTOM_CONFIG_FAILED)
        else:
            new_module_custom_config = {}
            module_custom_config_info = dict(
                module_custom_id=module_custom_id,
                module_type=module_type,
                item_key=item_key,
                item_value=item_value,
                enable_module=enable_module,
                create_time=get_current_time()
            )
            new_module_custom_config[module_type] = module_custom_config_info
            if not ctx.pg.batch_insert(dbconst.TB_MODULE_CUSTOM_CONFIG, new_module_custom_config):
                logger.error("insert newly created module custom config [%s] to db failed" % (new_module_custom_config))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_MODULE_CUSTOM_CONFIG_FAILED)

    return None

def modify_module_custom_user_scope(module_custom_id, zone_id, user_ids):

    ctx = context.instance()
    module_custom_zones = ctx.pgm.get_module_custom_zone(module_custom_id)

    if not module_custom_zones:
        module_custom_zones = {}
    module_custom_zone = module_custom_zones.get(zone_id)

    user_scope = module_custom_zone["user_scope"]
    if user_scope == const.MODULE_CUSTOM_ZONE_SCOPE_ALL_ADMIN_ROLES:

        conditions = {"module_custom_id": module_custom_id, "zone_id": zone_id}
        ctx.pg.base_delete(dbconst.TB_MODULE_CUSTOM_USER, conditions)

        return None

    elif user_scope == const.MODULE_CUSTOM_ZONE_SCOPE_PART_ADMIN_ROLES:

        zone_users = ctx.pgm.get_zone_users(zone_id, user_ids)
        if not zone_users:
            zone_users = {}

        for user_id,user in zone_users.items():
            role = user["role"]
            if role not in const.ADMIN_ROLES:
                del zone_users[user_id]

        zone_user_group = ctx.pgm.get_zone_user_groups(zone_id, user_ids)
        if not zone_user_group:
            zone_user_group = {}

        if not zone_users and not zone_user_group:
            return None

        zone_users.update(zone_user_group)

        new_user_ids = []
        delete_user_ids = []
        zone_user_ids = zone_users.keys()
        module_custom_user = ctx.pgm.get_module_custom_user(module_custom_id, zone_id)

        if not module_custom_user:
            new_user_ids = zone_user_ids
        else:
            for user_id in module_custom_user:
                if user_id not in zone_user_ids:
                    delete_user_ids.append(user_id)

            for user_id in zone_user_ids:
                if user_id not in module_custom_user:
                    new_user_ids.append(user_id)

        if new_user_ids:
            update_user = {}
            for user_id in new_user_ids:
                user_type = const.USER_TYPE_USER
                if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                    user_type = const.USER_TYPE_GROUP
                update_info = {
                    "zone_id": zone_id,
                    "module_custom_id": module_custom_id,
                    "user_id": user_id,
                    "user_type": user_type
                }
                update_user[user_id] = update_info
            if not ctx.pg.batch_insert(dbconst.TB_MODULE_CUSTOM_USER, update_user):
                logger.error("insert newly created module custom user for [%s] to db failed" % (update_user))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

        if delete_user_ids:
            conditions = {"module_custom_id": module_custom_id, "zone_id": zone_id, "user_id": delete_user_ids}
            ctx.pg.base_delete(dbconst.TB_MODULE_CUSTOM_USER, conditions)

    return None

def set_module_custom_zone_scope(module_custom_id, zone_id, zone_user):

    ctx = context.instance()
    module_custom_zones = ctx.pgm.get_module_custom_zone(module_custom_id)
    if not module_custom_zones:
        module_custom_zones = {}
    module_custom_zone = module_custom_zones.get(zone_id)
    user_ids = zone_user.get("user_ids")

    # if not user_scope:
    if user_ids:
        user_scope = const.MODULE_CUSTOM_ZONE_SCOPE_PART_ADMIN_ROLES
    else:
        user_scope = const.MODULE_CUSTOM_ZONE_SCOPE_ALL_ADMIN_ROLES

    if not module_custom_zone:
        update_info = {"module_custom_id": module_custom_id, "zone_id": zone_id, "user_scope": user_scope}
        if not ctx.pg.insert(dbconst.TB_MODULE_CUSTOM_ZONE, update_info):
            logger.error("insert newly created module custom zone for [%s] to db failed" % (update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    else:
        if module_custom_zone["user_scope"] != user_scope:
            condition = {"module_custom_id": module_custom_id, "zone_id": zone_id}
            if not ctx.pg.base_update(dbconst.TB_MODULE_CUSTOM_ZONE, condition, {"user_scope": user_scope}):
                logger.error("update module custom zone error")
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ret = modify_module_custom_user_scope(module_custom_id, zone_id, user_ids)
    if isinstance(ret, Error):
        return ret

    return None

def create_user_module_custom(sender, req,zone_users):

    ctx = context.instance()
    module_custom_id = get_uuid(UUID_TYPE_MODULE_CUSTOM, ctx.checker)
    module_custom_info = build_module_custom(req)

    update_info = dict(
        module_custom_id=module_custom_id,
        is_default=0,
        create_time=get_current_time()
    )
    update_info.update(module_custom_info)
    # register module_custom
    if not ctx.pg.insert(dbconst.TB_MODULE_CUSTOM, update_info):
        logger.error("insert newly created module_custom for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = check_set_module_custom_zone_user(sender, module_custom_id, zone_users)
    if isinstance(ret, Error):
        return Error(req, ret)

    if not ret:
        logger.error("request param %s format error" % "zone_users")
        return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                     ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED)

    zone_users = ret

    ret = modify_module_custom_zone_user(sender, module_custom_id, zone_users)
    if isinstance(ret, Error):
        return Error(req, ret)

    ret = modify_module_custom_configs(sender,module_custom_id,req)
    if isinstance(ret, Error):
        return ret

    return module_custom_id

def check_set_module_custom_zone_user(sender, module_custom_id, zone_users):

    zone_id = sender["zone"]
    ctx = context.instance()

    new_zone_users = {}
    for zone_user in zone_users:
        zone_id = zone_user["zone_id"]
        new_zone_users[zone_id] = zone_user

    module_custom = ctx.pgm.get_module_custom(module_custom_id)
    if not module_custom:
        logger.error("no found module_custom %s" % module_custom_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, module_custom_id)

    return new_zone_users

def clear_module_custom_zone_scope(module_custom_id, zone_ids=None):

    ctx = context.instance()
    conditions = {"module_custom_id": module_custom_id}
    if zone_ids:
        conditions["zone_id"] = zone_ids

    ctx.pg.base_delete(dbconst.TB_MODULE_CUSTOM_USER, conditions)
    ctx.pg.base_delete(dbconst.TB_MODULE_CUSTOM_ZONE, conditions)

    return None

def modify_module_custom_zone_user(sender, module_custom_id, zone_users):

    modify_zone_users = zone_users

    for zone_id, zone_user in modify_zone_users.items():

        user_scope = zone_user["user_scope"]
        if user_scope != const.MODULE_CUSTOM_ZONE_SCOPE_INVISIBLE:
            ret = set_module_custom_zone_scope(module_custom_id, zone_id, zone_user)
            if isinstance(ret, Error):
                return ret
        else:
            ret = clear_module_custom_zone_scope(module_custom_id, zone_id)
            if isinstance(ret, Error):
                return ret

    return None

def check_module_custom_zone_scope(sender, module_custom_ids=None):

    ctx = context.instance()
    zone_id = sender["zone"]
    user_id = sender["owner"]

    if APIUser.is_global_admin_user(sender):

        if module_custom_ids:
            return module_custom_ids
        else:
            return []
    elif APIUser.is_admin_console(sender):

        module_custom_users = ctx.pgm.get_module_custom_users(module_custom_ids, user_ids=user_id,zone_ids=zone_id)
        module_custom_zones = ctx.pgm.get_module_custom_zones(zone_ids=zone_id,user_scope=const.MODULE_CUSTOM_ZONE_SCOPE_ALL_ADMIN_ROLES)

        if module_custom_users:
            module_custom_ids = module_custom_users.keys()
        elif module_custom_zones:
            module_custom_ids = module_custom_zones.keys()[0]
        else:
            module_custom_ids = const.DEFAULT_MODULE_CUSTOM

    return module_custom_ids






