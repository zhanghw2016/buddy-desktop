from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from utils.id_tool import(
    get_uuid,
    UUID_TYPE_FILE_SHARE_GROUP,
    UUID_TYPE_DESKTOP_USER_GROUP,
    UUID_TYPE_FILE_SHARE_GROUP_FILE,
    UUID_TYPE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY,
    UUID_TYPE_FILE_SHARE_SERVICE,
)
from utils.misc import get_current_time
import api.user.user as APIUser
from utils.json import json_dump, json_load
import resource_control.desktop.job as Job
import os
import resource_control.file_share.sync_file_share as SyncFileShare
import api.file_share.file_share as APIFileShare
from common import check_resource_transition_status
import base64
from utils.misc import exec_cmd,_exec_cmd
from utils.auth import get_base64_password

def format_file_share_group(sender, file_share_group_set):

    ctx = context.instance()

    zone_id = sender.get("zone_id")
    file_share_groups = {}
    zone_infos = ctx.pgm.get_zones()

    for file_share_group_id, file_share_group in file_share_group_set.items():

        desktop_users = {}
        ret = ctx.pgm.get_file_share_group_user(file_share_group_ids=file_share_group_id)
        if ret:
            user_ids = ret.keys()
            user_column = ["user_name", "user_id", "user_dn"]
            user_group_column = ["user_group_name", "user_group_id", "user_group_dn"]
            ret = ctx.pgm.get_user_and_user_group(user_ids, user_column, user_group_column)
            if ret:
                desktop_users = ret
        if APIUser.is_global_admin_user(sender):
            file_share_group_zones = ctx.pgm.get_file_share_group_zone(file_share_group_ids=file_share_group_id)
            if file_share_group_zones:
                for zone_id, file_share_group_zone in file_share_group_zones.items():

                    zone = zone_infos.get(zone_id)
                    if zone:
                        file_share_group_zone["zone_name"] = zone["zone_name"]

                    user_scope = file_share_group_zone["user_scope"]
                    file_share_group_zone["scope"] = user_scope
                    del file_share_group_zone["user_scope"]
                    if user_scope == const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES:
                        continue

                    file_share_group_users = ctx.pgm.get_file_share_group_user(file_share_group_ids=file_share_group_id, zone_id=zone_id)

                    if not file_share_group_users:
                        file_share_group_users = {}

                    for user_id, file_share_group_user in file_share_group_users.items():

                        desktop_user = desktop_users.get(user_id)
                        if desktop_user:
                            file_share_group_user.update(desktop_user)

                    file_share_group_zone["user_ids"] = file_share_group_users.values()

                file_share_group["zone_scope"] = file_share_group_zones.values()

            file_share_groups[file_share_group_id] = file_share_group

        elif APIUser.is_console_admin_user(sender) or APIUser.is_normal_user(sender):

            file_share_group_zones = ctx.pgm.get_file_share_group_zone(file_share_group_ids=file_share_group_id)
            if file_share_group_zones:
                for zone_id, file_share_group_zone in file_share_group_zones.items():

                    zone = zone_infos.get(zone_id)
                    if zone:
                        file_share_group_zone["zone_name"] = zone["zone_name"]

                    user_scope = file_share_group_zone["user_scope"]
                    file_share_group_zone["scope"] = user_scope
                    del file_share_group_zone["user_scope"]
                    if user_scope == const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES:
                        continue

                    file_share_group_users = ctx.pgm.get_file_share_group_user(file_share_group_ids=file_share_group_id, zone_id=zone_id)
                    if not file_share_group_users:
                        file_share_group_users = {}

                    for user_id, file_share_group_user in file_share_group_users.items():

                        desktop_user = desktop_users.get(user_id)
                        if desktop_user:
                            file_share_group_user.update(desktop_user)

                    file_share_group_zone["user_ids"] = file_share_group_users.values()

                file_share_group["zone_scope"] = file_share_group_zones.values()
            file_share_groups[file_share_group_id] = file_share_group

    return file_share_groups

def check_create_file_share_group(sender, req):

    ctx = context.instance()
    file_share_group_name = req.get("file_share_group_name")
    ret = ctx.pgm.get_file_share_group_name()
    if not ret:
        return file_share_group_name

    if file_share_group_name.upper() in ret:
        logger.error("file_share_group_name already existd %s" % file_share_group_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_NAME_ALREADY_EXISTED, file_share_group_name)

    return file_share_group_name

def build_file_share_group(req):

    modify_keys = ["file_share_group_name","description","scope","show_location"]
    dump_keys = ['show_location']

    file_share_group = {}
    for modify_key in modify_keys:
        if modify_key not in req:
            continue

        value = req[modify_key]
        if modify_key in dump_keys:
            value = json_dump(value)

        file_share_group[modify_key] = value

    return file_share_group

def modify_file_share_group_user_scope(file_share_group_id, zone_id, user_ids):

    ctx = context.instance()
    file_share_group_zones = ctx.pgm.get_file_share_group_zone(file_share_group_id)
    file_share_group_dn = ctx.pgm.get_file_share_group_dn_by_file_share_group_id(file_share_group_ids=file_share_group_id)

    if not file_share_group_zones:
        file_share_group_zones = {}
    file_share_group_zone = file_share_group_zones.get(zone_id)

    user_scope = file_share_group_zone["user_scope"]
    if user_scope == const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES:

        conditions = {"file_share_group_id": file_share_group_id, "zone_id": zone_id}
        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_USER, conditions)

        return None

    elif user_scope == const.FILE_SHARE_GROUP_ZONE_SCOPE_PART_ROLES:

        zone_users = ctx.pgm.get_zone_users(zone_id, user_ids)
        if not zone_users:
            zone_users = {}

        for user_id,user in zone_users.items():
            role = user["role"]
            # if role not in const.ADMIN_ROLES:
            #     del zone_users[user_id]

        zone_user_group = ctx.pgm.get_zone_user_groups(zone_id, user_ids)
        if not zone_user_group:
            zone_user_group = {}

        if not zone_users and not zone_user_group:
            return None

        zone_users.update(zone_user_group)

        new_user_ids = []
        delete_user_ids = []
        zone_user_ids = zone_users.keys()
        file_share_group_user = ctx.pgm.get_file_share_group_user(file_share_group_id, zone_id)

        if not file_share_group_user:
            new_user_ids = zone_user_ids
        else:
            for user_id in file_share_group_user:
                if user_id not in zone_user_ids:
                    delete_user_ids.append(user_id)

            for user_id in zone_user_ids:
                if user_id not in file_share_group_user:
                    new_user_ids.append(user_id)

        if new_user_ids:
            update_user = {}
            for user_id in new_user_ids:
                user_type = const.USER_TYPE_USER
                if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                    user_type = const.USER_TYPE_GROUP
                update_info = {
                    "zone_id": zone_id,
                    "file_share_group_id": file_share_group_id,
                    "user_id": user_id,
                    "user_type": user_type,
                    "file_share_group_dn": file_share_group_dn
                }
                update_user[user_id] = update_info
            if not ctx.pg.batch_insert(dbconst.TB_FILE_SHARE_GROUP_USER, update_user):
                logger.error("insert newly created file share group user for [%s] to db failed" % (update_user))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

        if delete_user_ids:
            conditions = {"file_share_group_id": file_share_group_id, "zone_id": zone_id, "user_id": delete_user_ids}
            ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_USER, conditions)

    return None

def set_file_share_group_zone_scope(file_share_group_id, zone_id, zone_user):

    ctx = context.instance()
    file_share_group_zones = ctx.pgm.get_file_share_group_zone(file_share_group_ids=file_share_group_id)
    if not file_share_group_zones:
        file_share_group_zones = {}
    file_share_group_zone = file_share_group_zones.get(zone_id)
    user_ids = zone_user.get("user_ids")

    # if not user_scope:
    if user_ids:
        user_scope = const.FILE_SHARE_GROUP_ZONE_SCOPE_PART_ROLES
    else:
        user_scope = const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES

    if not file_share_group_zone:
        update_info = {"file_share_group_id": file_share_group_id, "zone_id": zone_id, "user_scope": user_scope}
        logger.info("update_info == %s" %(update_info))
        if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_ZONE, update_info):
            logger.error("insert newly created file share group zone for [%s] to db failed" % (update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    else:
        if file_share_group_zone["user_scope"] != user_scope:
            condition = {"file_share_group_id": file_share_group_id, "zone_id": zone_id}
            logger.info("condition == %s" % (condition))
            if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP_ZONE, condition, {"user_scope": user_scope}):
                logger.error("update file share group zone error")
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ret = modify_file_share_group_user_scope(file_share_group_id, zone_id, user_ids)
    if isinstance(ret, Error):
        return ret

    return None

def clear_file_share_group_zone_scope(file_share_group_id, zone_ids=None):

    ctx = context.instance()
    conditions = {"file_share_group_id": file_share_group_id}
    if zone_ids:
        conditions["zone_id"] = zone_ids

    ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_USER, conditions)
    ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_ZONE, conditions)

    return None

def set_file_share_group_zone(sender, file_share_group_id=None,user_scope=const.FILE_SHARE_GROUP_ZONE_SCOPE_PART_ROLES):

    ctx = context.instance()
    ret = ctx.pgm.get_zones()
    zones = ret
    for zone_id,_ in zones.items():

        update_info = {"file_share_group_id": file_share_group_id, "zone_id": zone_id, "user_scope": user_scope}
        if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_ZONE, update_info):
            logger.error("insert newly created file share group zone for [%s] to db failed" % (update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    return 0

def check_modify_file_share_group_attributes(req):

    ctx = context.instance()
    file_share_group_id = req.get("file_share_groups")
    file_share_group = ctx.pgm.get_file_share_group(file_share_group_id)
    if not file_share_group:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, file_share_group_id)

    modify_keys = ["description","show_location"]
    dump_keys = ["show_location"]

    need_maint_columns = {}
    for modify_key in modify_keys:
        if modify_key not in req:
            continue

        value = req[modify_key]
        if modify_key in dump_keys:
            value = json_dump(value)

        need_maint_columns[modify_key] = value

    return need_maint_columns

def modify_file_share_group_attributes(file_share_group_id, need_maint_columns):

    ctx = context.instance()
    if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_GROUP, {file_share_group_id: need_maint_columns}):
        logger.error("modify file share group update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    show_location = need_maint_columns.get("show_location")
    if show_location == const.FILE_SHARE_GROUP_SHOW_LOCATION_VM_WEB or show_location == const.FILE_SHARE_GROUP_SHOW_LOCATION_WEB_VM:
        if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_GROUP, {file_share_group_id: need_maint_columns}):
            logger.error("modify file share group update DB fail %s" % need_maint_columns)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    else:
        file_share_groups = ctx.pgm.get_file_share_groups(file_share_group_ids=file_share_group_id)
        for file_share_group_id, file_share_group in file_share_groups.items():
            file_share_group_dn = file_share_group["file_share_group_dn"]
            search_file_share_groups = ctx.pgm.search_file_share_groups(file_share_group_dn=file_share_group_dn,exclude_file_share_groups=[file_share_group_dn])
            if not search_file_share_groups:
                continue
            for search_file_share_group_id,search_file_share_group in search_file_share_groups.items():
                if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_GROUP, {search_file_share_group_id: {'show_location':show_location}}):
                    logger.error("modify file share group update DB fail %s" % search_file_share_group_id)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

        if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_GROUP, {file_share_group_id: need_maint_columns}):
            logger.error("modify file share group update DB fail %s" % need_maint_columns)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_delete_file_share_group(sender, file_share_group_ids):

    ctx = context.instance()
    user_id = sender["owner"]
    file_share_groups = ctx.pgm.get_file_share_groups(file_share_group_ids=file_share_group_ids)
    if not file_share_groups:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, file_share_group_ids)

    return file_share_groups

def check_file_share_group(sender, file_share_group_id):

    ctx = context.instance()
    file_share_groups = ctx.pgm.get_file_share_groups(file_share_group_ids=file_share_group_id)
    if not file_share_groups:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, file_share_group_id)

    return file_share_group_id

def modify_file_share_group(sender, file_share_group_id=None,scope=const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES):

    ctx = context.instance()

    condition = {"file_share_group_id": file_share_group_id}
    if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP, condition, {"scope": scope}):
        logger.error("update file share group error")
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def modify_file_share_group_zone(sender, file_share_group_id=None,user_scope=const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES):

    ctx = context.instance()
    zone_id = sender["zone"]

    condition = {"file_share_group_id": file_share_group_id, "zone_id": zone_id}
    if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP_ZONE, condition, {"user_scope": user_scope}):
        logger.error("update file share group zone error")
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_set_file_share_group_zone_user(sender, file_share_group_id, zone_users):

    zone_id = sender["zone"]
    ctx = context.instance()

    new_zone_users = {}
    for zone_user in zone_users:
        zone_id = zone_user["zone_id"]
        new_zone_users[zone_id] = zone_user

    file_share_group = ctx.pgm.get_file_share_group(file_share_group_id)
    if not file_share_group:
        logger.error("no found file_share_group %s" % file_share_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, file_share_group_id)

    return new_zone_users

def modify_file_share_group_zone_user(sender, file_share_group_id, zone_users):

    modify_zone_users = zone_users

    for zone_id, zone_user in modify_zone_users.items():

        user_scope = zone_user["user_scope"]
        if user_scope != const.FILE_SHARE_GROUP_ZONE_SCOPE_INVISIBLE:
            ret = set_file_share_group_zone_scope(file_share_group_id, zone_id, zone_user)
            if isinstance(ret, Error):
                return ret
        else:
            ret = clear_file_share_group_zone_scope(file_share_group_id, zone_id)
            if isinstance(ret, Error):
                return ret

    return None

def check_file_share_group_zone_scope(sender, file_share_group_id=None):

    ctx = context.instance()
    zone_id = sender["zone"]
    user_id = sender["owner"]
    scope_file_share_group_ids = []

    # get all_roles
    ret = ctx.pgm.get_file_share_group_zones(file_share_group_ids=file_share_group_id,user_scope=const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES)
    if ret:
        scope_file_share_group_ids.extend(ret.keys())

    # get part_roles user
    ret = ctx.pgm.get_file_share_group_users(file_share_group_ids=file_share_group_id, user_ids=user_id)
    if ret:
        scope_file_share_group_ids.extend(ret)

    if not scope_file_share_group_ids:
        return None

    return scope_file_share_group_ids

def check_file_share_group_name(file_share_group_id=None):
    ctx = context.instance()
    file_share_groups = ctx.pgm.get_file_share_groups(file_share_group_ids=file_share_group_id)
    if not file_share_groups:
        logger.error("file_share_group %s no found" % file_share_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, file_share_group_id)

    for file_share_group_id,file_share_group in file_share_groups.items():
        file_share_group_name = file_share_group.get("file_share_group_name")

    return file_share_group_name

def upload_file_share_group_files(file_share_group ,upload_files):

    ctx = context.instance()
    file_share_group_file_ids = []

    for upload_file in upload_files:
        file_share_group_file_name = upload_file.get("file_share_group_file_name",'')
        file_share_group_file_size = upload_file.get("file_share_group_file_size",0)
        if file_share_group_file_size <= 1:
            file_share_group_file_size = 1
        file_share_group_id = file_share_group["file_share_group_id"]
        file_share_group_dn = file_share_group["file_share_group_dn"]
        file_share_group_file_dn = "cn=%s,%s" % (file_share_group_file_name, file_share_group_dn)

        file_share_group_file_name = format_file_share_unicode_param(file_share_group_file_name)
        file_share_group_dn = format_file_share_unicode_param(file_share_group_dn)
        file_share_group_file_dn = format_file_share_unicode_param(file_share_group_file_dn)

        file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_ids=file_share_group_id,file_share_group_file_name=file_share_group_file_name,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
        if file_share_group_files is None or len(file_share_group_files) == 0:
            file_share_group_file_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP_FILE, ctx.checker)
            update_info = dict(
                file_share_group_file_id=file_share_group_file_id,
                file_share_group_id=file_share_group_id,
                file_share_group_file_name=file_share_group_file_name,
                file_share_group_file_alias_name='',
                description='',
                file_share_group_file_size=file_share_group_file_size,
                transition_status='',
                file_share_group_dn=file_share_group_dn,
                file_share_group_file_dn=file_share_group_file_dn,
                create_time=get_current_time()
            )
            if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_FILE, update_info):
                logger.error("insert newly created file share group file for [%s] to db failed" % (update_info))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

        else:
            for file_share_group_file_id, _ in file_share_group_files.items():
                condition = {"file_share_group_file_id": file_share_group_file_id}
                update_info = dict(
                    file_share_group_file_size=file_share_group_file_size,
                    file_share_group_dn=file_share_group_dn,
                    file_share_group_file_dn=file_share_group_file_dn,
                    create_time=get_current_time()
                )
                if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP_FILE, condition, update_info):
                    logger.error("update file share group file for [%s] to db failed" % (update_info))
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

        if file_share_group_file_id not in file_share_group_file_ids:
            file_share_group_file_ids.append(file_share_group_file_id)

    return file_share_group_file_ids

def send_desktop_file_share_job(sender, file_share_group_file_ids, action, extra=None):

    if not isinstance(file_share_group_file_ids, list):
        file_share_group_file_ids = [file_share_group_file_ids]

    directive = {
        "sender": sender,
        "action": action,
        "file_share_group_file_id": file_share_group_file_ids,
    }
    if extra:
        directive.update(extra)

    ret= Job.submit_desktop_job(action, directive, file_share_group_file_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def send_file_share_service_job(sender, file_share_service_ids, action, extra=None):

    if not isinstance(file_share_service_ids, list):
        file_share_service_ids = [file_share_service_ids]

    directive = {
        "sender": sender,
        "action": action,
        "file_share_service_id": file_share_service_ids,
    }
    if extra:
        directive.update(extra)

    ret= Job.submit_desktop_job(action, directive, file_share_service_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def URLencode(sStr):

    return sStr.replace('%', '%25').replace('#', '%23').replace('&', '%26').replace('+', '%2B').replace('?', '%3F').replace(':', '%3A')

def format_file_share_group_file(sender, file_share_group_file_set,verbose):

    ctx = context.instance()
    # get download_file_ip
    download_file_ip = None
    file_share_apache2_http_eip = APIFileShare.get_file_share_apache2_http_eip(ctx)
    file_share_apache2_http_ip = APIFileShare.get_file_share_apache2_http_ip(ctx)
    loaded_clone_instance_ip = APIFileShare.get_file_share_service_loaded_clone_instance_ip(ctx)
    download_file_uri_port = APIFileShare.check_download_file_uri_port(ctx)

    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    file_share_services = ctx.pgm.get_file_share_services()
    if not file_share_services:
        return file_share_group_file_set

    for _, file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")

    if file_share_apache2_http_eip:
        download_file_ip = file_share_apache2_http_eip
    else:
        if const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED == create_method:
            download_file_ip = file_share_apache2_http_ip
        else:
            download_file_ip = loaded_clone_instance_ip

    # # get fuser and fpw
    # fuser = ctx.pgm.get_file_share_service_fuser()
    # fpw = ctx.pgm.get_file_share_service_fpw()

    # get max_download_file_size
    max_download_file_size = ctx.pgm.get_file_share_service_max_download_file_size()

    if verbose:
        for file_share_group_file_id, file_share_group_file in file_share_group_file_set.items():

            file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
            file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
            file_share_group_dn = file_share_group_file["file_share_group_dn"]
            path = APIFileShare.dn_to_path(file_share_group_file_dn)
            path = URLencode(path)

            #http://192.168.13.172/file/installer/mk_image.zip
            path = APIFileShare.dn_to_path(file_share_group_dn)
            download_file_uri = "http://%s:%s/file%s/%s" % (download_file_ip,download_file_uri_port, path, file_share_group_file_name)
            logger.info("download_file_uri == %s" % (download_file_uri))

            file_share_group_file_set[file_share_group_file_id]["download_file_uri"] = download_file_uri
            file_share_group_file_set[file_share_group_file_id]["download_file_exist"] = 1
            file_share_group_file_set[file_share_group_file_id]["path"] = path
            file_share_group_file_set[file_share_group_file_id]["max_download_file_size"] = max_download_file_size
    else:
        for file_share_group_file_id, file_share_group_file in file_share_group_file_set.items():
            file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
            path = APIFileShare.dn_to_path(file_share_group_file_dn)
            file_share_group_file_set[file_share_group_file_id]["path"] = path

    return file_share_group_file_set

def format_file_share_group_file_count(sender, file_share_group_set):

    ctx = context.instance()

    for file_share_group_id, file_share_group in file_share_group_set.items():
        file_total_count = 0
        file_total_size = 0
        file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_ids=file_share_group_id,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
        if file_share_group_files:
            file_total_count = len(file_share_group_files.keys())
            for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
                file_share_group_file_size = file_share_group_file.get("file_share_group_file_size",0)
                file_total_size = file_total_size + file_share_group_file_size

        file_share_group_set[file_share_group_id]["file_total_count"] = file_total_count
        file_share_group_set[file_share_group_id]["file_total_size"] = file_total_size
        file_share_group_set[file_share_group_id]["path"] = APIFileShare.dn_to_path(file_share_group["file_share_group_dn"])

    return file_share_group_set

def get_file_share_group_info(file_share_group_id=None):

    ctx = context.instance()
    file_total_count = 0
    file_total_size = 0

    if not file_share_group_id:
        return None

    ret = ctx.pgm.get_file_share_groups(file_share_group_ids=file_share_group_id)
    if not ret:
        return None
    file_share_groups = ret

    for file_share_group_id, file_share_group in file_share_groups.items():
        file_share_group_create_time = file_share_group["create_time"]
        show_location = file_share_group["show_location"]
        file_share_group_name = file_share_group["file_share_group_name"]
        file_share_group_description = file_share_group["description"]
        file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_ids=file_share_group_id,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
        if file_share_group_files:
            file_total_count = len(file_share_group_files.keys())
            for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
                file_share_group_file_size = file_share_group_file.get("file_share_group_file_size",0)
                file_total_size = file_total_size + file_share_group_file_size

    return {"file_total_count":file_total_count,
            "file_total_size":file_total_size,
            "file_share_group_create_time":file_share_group_create_time,
            "show_location":show_location,
            "file_share_group_name":file_share_group_name,
            "file_share_group_description":file_share_group_description
            }

def format_file_share_group_user(sender, file_share_group_set):

    ctx = context.instance()
    user_id = sender["owner"]
    zone_id = sender["zone"]
    file_share_group_ids = file_share_group_set.keys()

    for file_share_group_id, file_share_group in file_share_group_set.items():

        # get all_roles
        ret = ctx.pgm.get_file_share_group_zones(zone_ids=zone_id,file_share_group_ids=file_share_group_id,user_scope=const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES)
        if ret:
            continue

        # get part_roles user
        file_share_group_dn = file_share_group["file_share_group_dn"]
        file_share_group_users = ctx.pgm.search_file_share_group_users(user_id=user_id,file_share_group_dn=file_share_group_dn)
        if file_share_group_users:
            continue

        del file_share_group_set[file_share_group_id]

    return file_share_group_set

def format_file_share_group_file_user(sender, file_share_group_file_set,file_share_group_ids=None):

    ctx = context.instance()
    if not file_share_group_ids:
        return None

    if file_share_group_ids and not isinstance(file_share_group_ids,list):
        file_share_group_ids = [file_share_group_ids]

    file_share_group_id = file_share_group_ids[0]
    ret = check_file_share_group_zone_scope(sender, file_share_group_id)
    if not ret:
        file_share_group_file_set.clear()

    return file_share_group_file_set

def register_download_file_share_group_file_history(sender, req):

    ctx = context.instance()
    file_share_group_file_ids = req.get("file_share_group_files")
    user_name = sender["user_name"]
    user_id = sender["owner"]

    file_download_history_ids = []
    for file_share_group_file_id in file_share_group_file_ids:
        file_download_history_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, ctx.checker)
        file_download_history_info = dict(
                                file_download_history_id=file_download_history_id,
                                file_share_group_file_id=file_share_group_file_id,
                                user_id=user_id,
                                user_name=user_name,
                                create_time=get_current_time(),
                                update_time=get_current_time()
                                )

        if not ctx.pg.batch_insert(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, {file_download_history_id: file_download_history_info}):
            logger.error("insert newly created file_share_group_file_download_history [%s] to db failed" % (file_download_history_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

        if file_download_history_id not in file_download_history_ids:
            file_download_history_ids.append(file_download_history_id)

    return file_download_history_ids

def check_modify_file_share_group_file_attributes(req):

    ctx = context.instance()
    file_share_group_file_id = req.get("file_share_group_files")
    file_share_group_file = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not file_share_group_file:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, file_share_group_file_id)

    modify_keys = ["file_share_group_file_alias_name", "description"]
    dump_keys = []

    need_maint_columns = {}
    for modify_key in modify_keys:
        if modify_key not in req:
            continue

        value = req[modify_key]
        if modify_key in dump_keys:
            value = json_dump(value)

        need_maint_columns[modify_key] = value

    return need_maint_columns

def modify_file_share_group_file_attributes(file_share_group_file_id, need_maint_columns):

    ctx = context.instance()
    if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_GROUP_FILE, {file_share_group_file_id: need_maint_columns}):
        logger.error("modify file share group file update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_file_share_unicode_param(file_share, params=[]):

    if not file_share:
        return file_share

    check_keys = ["file_share_group_name", 'search_name', 'base_dn','file_share_group_dn','description',
                  'new_name','upload_files','file_share_group_file_alias_name','new_file_share_group_dn','file_share_service_name']
    if params:
        if isinstance(params, list):
            check_keys.extend(params)
        else:
            check_keys.append(params)

    if isinstance(file_share, dict):
        for key, value in file_share.items():
            if key not in check_keys:
                continue
            if isinstance(value, unicode):
                a = str(value).decode("string_escape").encode("utf-8")
                file_share[key] = a
            elif isinstance(value, list):
                new_values = []
                for _value in value:
                    _value = check_file_share_unicode_param(_value)
                    new_values.append(_value)
                file_share[key] = new_values

    elif isinstance(file_share, list):
        new_values = []
        for value in file_share:
            if isinstance(value, unicode):
                value = str(value).decode("string_escape").encode("utf-8")
                new_values.append(value)
                continue
            new_values.append(value)
        return new_values

    elif isinstance(file_share, unicode):
        return str(file_share).decode("string_escape").encode("utf-8")

    return file_share

def check_file_share_group_name_vaild(file_share_group_name, base_dn):

    ctx = context.instance()
    file_share_group_dn = "ou=%s,%s" % (file_share_group_name, base_dn)
    ret = ctx.pgm.get_file_share_group_dns(file_share_group_dn=file_share_group_dn, file_share_group_names=file_share_group_name,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if isinstance(ret, Error):
        return ret
    if ret:
        logger.error("file_share_group [%s] existed" % file_share_group_name)
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_NAME_ALREADY_EXISTED, file_share_group_name)

    return None

def check_file_share_group_show_location_vaild(show_location_list,base_dn):

    ctx = context.instance()
    if base_dn == const.FILE_SHARE_GROUP_ROOT_BASE_DN:
        return None

    ret = ctx.pgm.get_file_share_groups(file_share_group_dn=base_dn,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if not ret:
        logger.error("file_share_group [%s] no found" % base_dn)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_NO_FOUND, base_dn)
    file_share_groups = ret

    for file_share_group_id,file_share_group in file_share_groups.items():
        parent_show_location = file_share_group["show_location"]
        for show_location in show_location_list:
            if show_location not in parent_show_location:
                logger.error("show_location %s error" % show_location)
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_SHOW_LOCATION_ERROR, show_location)

    return None

def register_file_share_group(sender, req):

    ctx = context.instance()
    file_share_group_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP, ctx.checker)
    file_share_group_info = build_file_share_group(req)

    base_dn = req.get("base_dn",const.FILE_SHARE_GROUP_ROOT_BASE_DN)
    file_share_group_dn = "ou=%s,%s" %(req.get("file_share_group_name"),req.get("base_dn",const.FILE_SHARE_GROUP_ROOT_BASE_DN))
    file_share_service_id = req.get("file_share_service")
    scope = req["scope"]

    update_info = dict(
        file_share_group_id=file_share_group_id,
        file_share_service_id=file_share_service_id,
        base_dn=base_dn,
        file_share_group_dn=file_share_group_dn,
        scope=scope,
        # show_location='["vm_tools_page","user_web_page"]',
        create_time=get_current_time(),
        update_time=get_current_time()
    )
    update_info.update(file_share_group_info)

    # check show_location
    show_location = update_info.get("show_location")
    if not show_location:
        update_info["show_location"] = '["vm_tools_page","user_web_page"]'

    logger.info("update_info == %s" % (update_info))
    # register file_share_group
    if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP, update_info):
        logger.error("insert newly created file share group for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return file_share_group_id

def get_file_share_group_scope(base_dn):

    ctx = context.instance()
    scope = const.FILE_SHARE_GROUP_ZONE_SCOPE_PART_ROLES
    if const.FILE_SHARE_GROUP_ROOT_BASE_DN == base_dn:
        ret = ctx.pgm.get_file_share_services(status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
        if ret:
            file_share_services = ret
            for file_share_service_id,file_share_service in file_share_services.items():
                scope = file_share_service["scope"]
    else:
        # check Up-level directory scope
        ret = ctx.pgm.get_file_share_groups(file_share_group_dn=base_dn)
        if ret:
            file_share_groups = ret
            for file_share_group_id,file_share_group in file_share_groups.items():
                scope = file_share_group["scope"]

    return scope

def create_file_share_group(sender,req,file_share_services):

    ctx = context.instance()
    # get scope
    base_dn = req.get("base_dn", const.FILE_SHARE_GROUP_ROOT_BASE_DN)
    scope = get_file_share_group_scope(base_dn)
    req["scope"] = scope

    ret = register_file_share_group(sender, req)
    if isinstance(ret, Error):
        return ret
    file_share_group_id = ret

    file_share_groups = ctx.pgm.get_file_share_groups(file_share_group_ids=file_share_group_id)
    if not file_share_groups:
        logger.error("file share group resource not found %s " % file_share_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, file_share_group_id)

    ret = set_file_share_group_zone(sender, file_share_group_id=file_share_group_id,user_scope=scope)
    if isinstance(ret, Error):
        return ret

    for _,file_share_group in file_share_groups.items():

        # create_remote_ftp_server_file_share_dir
        file_share_group_dn = file_share_group["file_share_group_dn"]
        file_share_group_name = file_share_group["file_share_group_name"]
        path = APIFileShare.dn_to_path(file_share_group_dn)
        dir_path = "%s" % (path)
        dir_path = format_file_share_unicode_param(dir_path)
        ret = APIFileShare.create_remote_ftp_server_file_share_dir(ctx, dir_path)
        if ret:
            logger.error("create_remote_ftp_server_file_share_dir ret == %s" % (ret))
            # Delete file records in file share
            conditions = {"file_share_group_id": file_share_group_id}
            ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP, conditions)

            logger.error("file share group create failed %s " % file_share_group_name)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_CREATE_FILE_SHARE_GROUP_FAILED)

    return file_share_group_dn

def check_file_share_vnas_node_dir(vnas_node_dir):

    ctx = context.instance()
    mnt_nasdata_exist = 0
    total_size = 0
    used_size = 0
    remain_size = 0
    os.system("mkdir -p %s && chmod -R 777 %s" % (vnas_node_dir, vnas_node_dir))
    local_desktop_server_remain_size = APIFileShare.get_local_desktop_server_mnt_node_remain_size(ctx, vnas_node_dir)

    ret = ctx.pgm.get_file_share_services()
    if ret:
        file_share_services = ret
        for _,file_share_service in file_share_services.items():
            status = file_share_service["status"]
            if const.FILE_SHARE_SERVICE_STATUS_ACTIVE == status:
                ret = APIFileShare.check_download_file_uri(ctx,file_path=vnas_node_dir)
                if ret:
                    mnt_nasdata_exist = 1
                    total_size = APIFileShare.get_mnt_node_total_size(ctx,vnas_node_dir)
                    used_size = APIFileShare.get_mnt_node_used_size(ctx,vnas_node_dir)
                    remain_size = APIFileShare.get_mnt_node_remain_size(ctx,vnas_node_dir)


    return (mnt_nasdata_exist,total_size,used_size,remain_size,local_desktop_server_remain_size)

def check_file_share_group_base_dn(sender, file_share_group_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group(file_share_group_id=file_share_group_id)
    if not ret:
        logger.error("no found file_share_group %s" % (file_share_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_NO_FOUND, file_share_group_id)
    file_share_group = ret
    base_dn = file_share_group["file_share_group_dn"]

    return base_dn

def format_file_share_unicode_param(check_param):

    if not check_param:
        return check_param

    if isinstance(check_param, list):
        temp_list = []
        for _param in check_param:
            if isinstance(_param, unicode):
                _param = str(_param).decode("string_escape").encode("utf-8")

            temp_list.append(_param)
        return temp_list

    elif isinstance(check_param, unicode):
        _param = str(check_param).decode("string_escape").encode("utf-8")
        return _param

    return check_param

def check_file_share_group_vaild(file_share_group_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_groups(file_share_group_ids=file_share_group_id)
    if not ret:
        logger.error("file share group [%s] no found" % file_share_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_NO_FOUND, file_share_group_id)
    file_share_groups = ret

    return file_share_groups

def check_file_share_group_cn_name_vaild(new_name, base_dn):

    ctx = context.instance()
    new_file_share_group_dn = "ou=%s,%s" %(new_name,base_dn)
    ret = ctx.pgm.get_file_share_groups(file_share_group_dn=new_file_share_group_dn, file_share_group_names=new_name,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if ret:
        logger.error("file share group [%s] existed in file share" % new_name)
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_NAME_ALREADY_EXISTED, new_name)

    return None

def check_rename_file_share_group_dn(file_share_group,file_share_group_dn, new_name):

    ctx = context.instance()
    base_dn = file_share_group.get("base_dn")
    file_share_group_name = file_share_group.get("file_share_group_name")
    if file_share_group_name == new_name:
        return None

    ret = check_file_share_group_cn_name_vaild(new_name, base_dn)
    if isinstance(ret, Error):
        return ret

    return new_name

def rename_file_share_group(file_share_group_id, new_name,file_share_group_dn,new_file_share_group_dn,file_share_services):

    ctx = context.instance()
    condition = {"file_share_group_id": file_share_group_id}
    # update TB_FILE_SHARE_GROUP file_share_group_name
    update_info = dict(
        file_share_group_name=new_name
    )
    if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP, condition, update_info):
        logger.error("update file share group for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    # update TB_FILE_SHARE_GROUP_USER file_share_group_dn
    ret = ctx.pgm.get_file_share_group_users(file_share_group_ids=file_share_group_id)
    if ret:
        condition = {"file_share_group_id": file_share_group_id}
        update_info = dict(
            file_share_group_dn=new_file_share_group_dn
        )
        if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP_USER, condition, update_info):
            logger.error("update file share group user for [%s] to db failed" % (update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    # rename_remote_ftp_server_file_share_dir
    dir_path = "%s" % (APIFileShare.dn_to_path(file_share_group_dn))
    new_dir_path = "%s" % (APIFileShare.dn_to_path(new_file_share_group_dn))

    # format_file_share_unicode_param
    dir_path = format_file_share_unicode_param(dir_path)
    new_dir_path = format_file_share_unicode_param(new_dir_path)

    ret = APIFileShare.rename_remote_ftp_server_file_share_dir(ctx, dir_path, new_dir_path)
    logger.info("rename_remote_ftp_server_file_share_dir ret == %s" %(ret))
    if ret:
        logger.error("rename_remote_ftp_server_file_share_dir ret == %s" % (ret))
        logger.error("file share group rename failed")
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RENAME_FILE_SHARE_GROUP_FAILED)

    return None

def refresh_file_share_group(file_share_group, file_share_group_dn,new_file_share_group_dn):

    ctx = context.instance()
    file_share_group_id = file_share_group["file_share_group_id"]

    ret = SyncFileShare.sync_file_share_group(file_share_group_id, file_share_group_dn,new_file_share_group_dn)
    if isinstance(ret, Error):
        return ret

    ret = SyncFileShare.sync_file_share_group_user(file_share_group_id, file_share_group_dn,new_file_share_group_dn)
    if isinstance(ret, Error):
        return ret

    ret = SyncFileShare.sync_file_share_group_file(file_share_group_id, file_share_group_dn,new_file_share_group_dn)
    if isinstance(ret, Error):
        return ret

    return None

def rename_file_share_group_dn(file_share_group, file_share_group_dn, new_name,file_share_services):

    ctx = context.instance()
    file_share_group_id = file_share_group["file_share_group_id"]
    base_dn = file_share_group.get("base_dn")
    new_file_share_group_dn = "ou=%s,%s" % (new_name, base_dn)

    ret = refresh_file_share_group(file_share_group, file_share_group_dn,new_file_share_group_dn)
    if isinstance(ret, Error):
        return ret

    ret = rename_file_share_group(file_share_group_id, new_name,file_share_group_dn,new_file_share_group_dn,file_share_services)
    if isinstance(ret, Error):
        return ret

    return new_name

def delete_file_share_group(file_share_group,file_share_services):

    ctx = context.instance()
    file_share_group_id = file_share_group["file_share_group_id"]
    file_share_group_dn = file_share_group["file_share_group_dn"]
    file_share_group_name = file_share_group["file_share_group_name"]

    # directly delete the folder: rmdir dir-name
    dir_path = "%s" % (APIFileShare.dn_to_path(file_share_group_dn))

    # format_file_share_unicode_param
    dir_path = format_file_share_unicode_param(dir_path)

    ret = APIFileShare.rmdir_remote_ftp_server_file_share_dir(ctx, dir_path)
    logger.info("rmdir_remote_ftp_server_file_share_dir ret == %s" %(ret))
    if not ret:
        logger.error("rmdir_remote_ftp_server_file_share_dir failed ret == %s" %(ret))
        logger.error("delete_file_share_group failed [%s]" % (file_share_group_name))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NO_DELETE_FILE_SHARE_GROUP_FAILED, file_share_group_name)

    # Delete file records in file share
    conditions = {"file_share_group_id": file_share_group_id}
    ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP, conditions)
    ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_ZONE, conditions)
    ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_USER, conditions)

    return None

def delete_file_share_groups(file_share_group,file_share_services):

    ctx = context.instance()
    file_share_group_id = file_share_group["file_share_group_id"]
    file_share_group_dn = file_share_group["file_share_group_dn"]
    file_share_group_name = file_share_group["file_share_group_name"]

    ret = ctx.pgm.get_file_share_group_resource(file_share_group_dn=file_share_group_dn,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if ret:
        logger.error("file share group has resource cant delete %s" % file_share_group_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_HAS_RESOURCE_CANT_DELETE, file_share_group_name)

    ret = delete_file_share_group(file_share_group,file_share_services)
    if isinstance(ret, Error):
        return ret

    return None

def check_file_share_group_file_vaild(file_share_group_file_ids=None,trashed_status=None):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids,trashed_status=trashed_status)
    if not ret:
        logger.error("file_share_group file [%s] no found" % file_share_group_file_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_FILE_SHARE_GROUP_FILE_NO_FOUND, file_share_group_file_ids)
    file_share_group_files = ret

    return file_share_group_files

def check_file_share_group_file_name_vaild(file_share_group_files, new_file_share_group_dn,change_type):

    ctx = context.instance()
    repeat_file_ids = []
    for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
        file_share_group_dn = file_share_group_file["file_share_group_dn"]
        if file_share_group_dn == new_file_share_group_dn and const.FILE_SHARE_CHANGE_TYPE_MOVE == change_type:
            logger.error("Cannot move [%s] to the current folder of the file." %(file_share_group_file_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_CANNOT_MOVE_CURRENT_GROUP_OF_THE_FILE, file_share_group_file_id)

        ret = ctx.pgm.get_file_share_group_files(file_share_group_dn=new_file_share_group_dn,file_share_group_file_name=file_share_group_file_name,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
        if not ret:
            continue
        if file_share_group_file_id not in repeat_file_ids:
            repeat_file_ids.append(file_share_group_file_id)

    return repeat_file_ids

def check_delete_permanently_file_share_recycles_vaild(file_share_group_file_ids=None,trashed_status=None):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids,trashed_status=trashed_status)
    if not ret:
        logger.error("no found file [%s] in the recycle" % file_share_group_file_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_NO_FOUND_FILE_IN_THE_RECYCLE, file_share_group_file_ids)
    file_share_group_files = ret

    return file_share_group_files

def check_empty_file_share_recycles_vaild(trashed_status=None):

    ctx = context.instance()
    file_share_group_files = {}
    file_share_group_files = ctx.pgm.get_file_share_group_files(trashed_status=trashed_status)
    if not file_share_group_files:
        logger.error("No deleted files in the recycle")
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_NO_DELETEED_FILES_IN_THE_RECYCLE)

    return file_share_group_files

def check_file_share_group_file_transition_status(file_share_group_file_ids):

    ctx = context.instance()
    file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if not file_share_group_files:
        return None

    # check file_share_group_files transition status
    ret = check_resource_transition_status(file_share_group_files)
    if isinstance(ret, Error):
        return ret

    return None

def create_file_share_service(req):

    ctx = context.instance()
    desktop_server_instance_id = APIFileShare.get_desktop_server_instance_id()
    file_share_service_id = get_uuid(UUID_TYPE_FILE_SHARE_SERVICE, ctx.checker)
    update_info = dict(
        file_share_service_id=file_share_service_id,
        file_share_service_name=req.get("file_share_service_name", ''),
        description=req.get("description", ''),
        network_id=req.get("network_id", ''),
        desktop_server_instance_id=desktop_server_instance_id,
        file_share_service_instance_id='',
        private_ip=req.get("private_ip", ''),
        vnas_id=req.get("vnas_id", ''),
        is_sync=req.get("is_sync",0),
        limit_rate=req.get("limit_rate", 1),
        limit_conn=req.get("limit_conn", 0),
        status=const.FILE_SHARE_SERVICE_STATUS_INACTIVE,
        scope=req.get("scope",const.FILE_SHARE_GROUP_ZONE_SCOPE_PART_ROLES),
        fuser=req.get("fuser"),
        fpw=req.get("fpw"),
        ftp_chinese_encoding_rules=const.FTP_SERVER_CHINESE_ENCODING_RULES_UTF_8,
        create_method=const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED,
        max_download_file_size=req.get("max_download_file_size", 100),
        max_upload_size_single_file=req.get("max_upload_size_single_file", 1),
        create_time=get_current_time(),
        status_time=get_current_time(),
    )
    # register file_share_service

    if not ctx.pg.insert(dbconst.TB_FILE_SHARE_SERVICE, update_info):
        logger.error("insert newly created file share service for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return file_share_service_id

def check_create_file_share_service_vaild():

    ctx = context.instance()
    file_share_services = ctx.pgm.get_file_share_services()
    if file_share_services:
        for file_share_service_id,file_share_service in file_share_services.items():
            file_share_service_name = file_share_service['file_share_service_name']
            logger.error("file share service %s already existed" %(file_share_service_name))
            return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                         ErrorMsg.ERR_MSG_ACTIVE_STATUS_FILE_SHARE_SERVICE_ALREADY_EXISTED, (file_share_service_name))

    return None

def get_user_quota_left(sender, resource_type):

    ctx = context.instance()
    ret = ctx.res.resource_get_quota_left(sender["zone"], resource_type=resource_type)
    if not ret:
        logger.error("resource_get_quota_left fail %s " % resource_type)
        return -1
    quota_left_set = ret
    for quota_left in quota_left_set:
        resource_type_left = quota_left.get("left")

    return resource_type_left

def check_ubuntu_images(sender, image_id):

    ctx = context.instance()
    ret = ctx.res.resource_describe_images(sender["zone"], image_ids=[image_id])
    if not ret:
        logger.error("resource_describe_images fail %s " % image_id)
        return False
    image_set = ret

    return image_set

def check_user_quota_left(sender,vnas_disk_size,vnas_id):

    ctx = context.instance()
    if ctx.zone_deploy == const.DEPLOY_TYPE_STANDARD:
        volume_size_quota_left = get_user_quota_left(sender,resource_type='volume_size')
        if int(volume_size_quota_left) <=  int(vnas_disk_size):
            logger.error("QuotasExceeded, you only have [%s GB] high performance volume size quota left currently" %(volume_size_quota_left))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_FILE_SHARE_VOLUME_SIZE_QUOTA_EXCEEDED, (volume_size_quota_left))

        instance_quota_left = get_user_quota_left(sender,resource_type='instance')
        if int(instance_quota_left) <= 1:
            logger.error("QuotasExceeded, you only have %s instance quota left currently" %(instance_quota_left))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_FILE_SHARE_INSTANCE_QUOTA_EXCEEDED, (instance_quota_left))

        if not vnas_id:
            s2_server_quota_left = get_user_quota_left(sender,resource_type='s2_server')
            if int(s2_server_quota_left) <= 1:
                logger.error("QuotasExceeded, you only have %s s2_server quota left currently" %(s2_server_quota_left))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_FILE_SHARE_S2_SERVER_QUOTA_EXCEEDED, (s2_server_quota_left))
    elif ctx.zone_deploy == const.DEPLOY_TYPE_EXPRESS:
        ret = check_ubuntu_images(sender, image_id=const.FILE_SHARE_SERVICE_FTP_SERVER_DEFAULT_IMAGE_ID)
        if not ret:
            logger.error("Ubuntu Server 16.04.5 LTS 64bit [%s] image is not found in iaas console" % (const.FILE_SHARE_SERVICE_FTP_SERVER_DEFAULT_IMAGE_ID))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_NO_FOUND_IMAGE_UBUNTU_SERVER_160405_ERROR, (const.FILE_SHARE_SERVICE_FTP_SERVER_DEFAULT_IMAGE_ID))

    return None

def check_network_id_valid(sender,network_id):

    ctx = context.instance()
    networks = ctx.pgm.get_networks(network_ids=network_id)
    if networks:
        for network_id,network in networks.items():
            manager_ip = network.get("manager_ip")
            if APIFileShare.check_host_valid(manager_ip):
                logger.info("localhost can connect manager_ip %s" % (manager_ip))
            else:
                logger.error("localhost cant connect manager_ip %s" % (manager_ip))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_LOCALHOST_CANT_CONNECT_NETWORK, (manager_ip))
    else:
        logger.error("No found network_id %s" %(network_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_BASE_NETWORK_NOT_EXISTED,(network_id))

    return None

def get_available_network_id(sender):

    ctx = context.instance()
    available_network_id = None
    networks = ctx.pgm.get_networks()
    if networks:
        for network_id,network in networks.items():
            manager_ip = network.get("manager_ip")
            if APIFileShare.check_host_valid(manager_ip):
                logger.info("localhost can connect network_id [%s] manager_ip [%s]" % (network_id,manager_ip))
                available_network_id = network_id
                break

    else:
        logger.error("No found available network_id %s" %(available_network_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_BASE_NETWORK_NOT_EXISTED,(available_network_id))

    return available_network_id

def check_file_share_service_vaild(file_share_service_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_services(file_share_service_ids=file_share_service_id)
    if not ret:
        logger.error("No found file share service %s" %(file_share_service_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_FILE_SHARE_SERVICE_NO_FOUND,(file_share_service_id))
    file_share_services = ret

    return file_share_services

def check_modify_file_share_service_attributes(req):

    ctx = context.instance()
    file_share_service_id = req.get("file_share_services")
    file_share_services = ctx.pgm.get_file_share_services(file_share_service_ids=file_share_service_id)
    if not file_share_services:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, file_share_service_id)

    modify_keys = ["file_share_service_name", "description","scope",'is_sync','max_download_file_size','max_upload_size_single_file']
    dump_keys = []

    need_maint_columns = {}
    for modify_key in modify_keys:
        if modify_key not in req:
            continue

        value = req[modify_key]
        if modify_key in dump_keys:
            value = json_dump(value)

        need_maint_columns[modify_key] = value

    return need_maint_columns

def modify_file_share_service_attributes(sender,file_share_service_id, need_maint_columns):

    ctx = context.instance()
    logger.info("need_maint_columns == %s" %(need_maint_columns))
    if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_SERVICE, {file_share_service_id: need_maint_columns}):
        logger.error("modify file share service update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ret = ctx.pgm.get_file_share_services(file_share_service_ids=file_share_service_id)
    if not ret:
        logger.error("No found file share service %s")
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_FILE_SHARE_SERVICE_NO_FOUND,(file_share_service_id))
    file_share_services = ret

    for file_share_service_id,file_share_service in file_share_services.items():
        file_share_service_instance_id = file_share_service.get("file_share_service_instance_id")
        file_share_service_name = file_share_service["file_share_service_name"]
        description = file_share_service["description"]
        if file_share_service_instance_id:
            ret = ctx.res.resource_modify_instance_attributes(sender["zone"], instance_id=file_share_service_instance_id,config={"instance_name":file_share_service_name,"description":description})
            if not ret:
                logger.error("resource modify_instance_attributes fail %s " % file_share_service_instance_id)
                return None

    return None

def check_file_share_service_status(file_share_services,force_delete=0):

    if not force_delete:
        for file_share_service_id,file_share_service in file_share_services.items():
            status = file_share_service["status"]
            if const.FILE_SHARE_SERVICE_STATUS_ACTIVE == status:
                logger.error("active status file share service cant delete.")
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_ACTIVE_STATUS_FILE_SHARE_SERVICE_CANT_DELETE, (file_share_service_id))

    return None

def check_file_share_service_transition_status(file_share_services):

    ret = check_resource_transition_status(file_share_services)
    if isinstance(ret, Error):
        return ret

    return None

def check_instance_private_ip(sender,instance_id=None):

    ctx = context.instance()
    private_ip = ctx.pgm.get_file_share_service_private_ip()

    if not instance_id:
        return private_ip

    body = {}
    offset = 0
    limit = const.MAX_LIMIT_PARAM

    body["offset"] = offset
    body["limit"] = limit
    body["search_word"] = instance_id

    ret = ctx.res.resource_describe_instances_by_search_word(sender["zone"], body)
    if ret:
        for _, instance in ret.items():
            vxnets = instance.get("vxnets")
            if vxnets:
                vxnet = vxnets[0]
                if vxnet:
                    private_ip = vxnet.get("private_ip", '')

    return private_ip

def check_instance_eip_addr(sender,instance_id=None):

    ctx = context.instance()
    eip_addr = ctx.pgm.get_file_share_service_eip_addr()

    if not instance_id:
        return eip_addr

    body = {}
    offset = 0
    limit = const.MAX_LIMIT_PARAM

    body["offset"] = offset
    body["limit"] = limit
    body["search_word"] = instance_id

    ret = ctx.res.resource_describe_instances_by_search_word(sender["zone"], body)
    if ret:
        for _, instance in ret.items():
            eip = instance.get("eip")
            if eip:
                eip_addr = eip.get("eip_addr",'')

    return eip_addr

def check_instance_status(sender,instance_id=None):

    ctx = context.instance()
    status = const.INST_STATUS_RUN

    if not instance_id:
        return status

    body = {}
    offset = 0
    limit = const.MAX_LIMIT_PARAM

    body["offset"] = offset
    body["limit"] = limit
    body["search_word"] = instance_id

    ret = ctx.res.resource_describe_instances_by_search_word(sender["zone"], body)
    if ret:
        for _, instance in ret.items():
            status = instance.get("status")

    return status

def check_ftp_server_status(ftp_username=None,ftp_password=None,ftp_ip=None):

    ctx = context.instance()
    status = const.FILE_SHARE_SERVICE_STATUS_ACTIVE

    exec_script = "/pitrix/conf/configure_vsftp/check_vsftp_access_status.sh -p %s -u %s -w %s" % (ftp_ip,ftp_username, ftp_password)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))

    # check_ftp_ip_flag
    ret = check_ftp_ip_flag()
    if not ret:
        logger.error("check_ftp_ip_flag fail")
        status = const.FILE_SHARE_SERVICE_STATUS_INACTIVE

    # check_ftp_username_password_flag
    ret = check_ftp_username_password_flag()
    if not ret:
        logger.error("check_ftp_username_password_flag fail")
        status = const.FILE_SHARE_SERVICE_STATUS_INACTIVE

    return status

def refresh_file_share_service(sender,file_share_services):

    ctx = context.instance()
    for file_share_service_id,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
        if const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED == create_method:
            file_share_service_instance_id = file_share_service.get("file_share_service_instance_id",'')
            instance_private_ip = check_instance_private_ip(sender,instance_id=file_share_service_instance_id)
            instance_eip_addr = check_instance_eip_addr(sender,instance_id=file_share_service_instance_id)
            status = check_instance_status(sender,instance_id=file_share_service_instance_id)


            if status != const.INST_STATUS_RUN:
                status = const.FILE_SHARE_SERVICE_STATUS_INACTIVE
            else:
                status = const.FILE_SHARE_SERVICE_STATUS_ACTIVE

            ret = ctx.pgm.get_file_share_services()
            if ret:
                condition = {"file_share_service_id": file_share_service_id}
                update_info = dict(
                    private_ip=instance_private_ip,
                    eip_addr=instance_eip_addr,
                    status=status,
                    status_time=get_current_time()
                )

                if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_SERVICE, condition, update_info):
                    logger.error("update file share service for [%s] to db failed" % (update_info))
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        elif const.FILE_SHARE_SERVICE_CREATE_METHOD_LOADED == create_method:

            fuser = file_share_service.get("fuser")
            fpw = file_share_service.get("fpw")
            private_ip = file_share_service.get("private_ip")

            ftp_username = fuser
            ftp_password = get_base64_password(fpw)
            ftp_ip = private_ip
            status = check_ftp_server_status(ftp_username=ftp_username,ftp_password=ftp_password,ftp_ip=ftp_ip)

            file_share_service_instance_id = file_share_service.get("file_share_service_instance_id",'')
            loaded_clone_instance_ip = check_instance_private_ip(sender,instance_id=file_share_service_instance_id)
            loaded_clone_instance_eip_addr = check_instance_eip_addr(sender,instance_id=file_share_service_instance_id)
            status = check_instance_status(sender,instance_id=file_share_service_instance_id)

            if status != const.INST_STATUS_RUN:
                status = const.FILE_SHARE_SERVICE_STATUS_INACTIVE
            else:
                status = const.FILE_SHARE_SERVICE_STATUS_ACTIVE

            ret = ctx.pgm.get_file_share_services()
            if ret:
                condition = {"file_share_service_id": file_share_service_id}
                update_info = dict(
                    loaded_clone_instance_ip=loaded_clone_instance_ip,
                    eip_addr=loaded_clone_instance_eip_addr,
                    status=status,
                    status_time=get_current_time()
                )

                if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_SERVICE, condition, update_info):
                    logger.error("update file share service for [%s] to db failed" % (update_info))
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        else:
            logger.error("invalid create_method %s" % (create_method))
            return None

    return None

def check_s2servers(sender,s2_servers):

    ctx = context.instance()
    ret = ctx.res.resource_describe_s2servers(sender["zone"], service_id=s2_servers)
    if not ret:
        logger.error("resource describe_s2servers fail %s" % s2_servers)
        return None
    s2_server_sets = ret

    return s2_server_sets

def refresh_file_share_service_vnas(sender):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_service_vnass()
    if not ret:
        return None
    file_share_service_vnass = ret

    for vnas_id,file_share_service_vnas in file_share_service_vnass.items():

        s2_server_sets = check_s2servers(sender,s2_servers=vnas_id)
        if not s2_server_sets:
            continue
        for s2_server_id,s2_server in s2_server_sets.items():
            s2_server_status = s2_server["status"]
            s2_server_name = s2_server["s2_server_name"]
            private_ip = s2_server["private_ip"]
            if "active" == s2_server_status:
                status = const.FILE_SHARE_SERVICE_STATUS_ACTIVE
            else:
                status = const.FILE_SHARE_SERVICE_STATUS_INACTIVE

            condition = {"vnas_id": vnas_id}
            update_info = dict(
                vnas_name=s2_server_name,
                vnas_private_ip=private_ip,
                status=status
            )
            if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_SERVICE_VNAS, condition, update_info):
                logger.error("update file share service vnas for [%s] to db failed" % (update_info))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return None

def check_file_share_service_status_valid(file_share_service_ids=None,status=None):
    ctx = context.instance()

    ret = ctx.pgm.get_file_share_services(file_share_service_ids)
    if not ret:
        logger.error("no found file share service %s" % (file_share_service_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_FILE_SHARE_SERVICE_NO_FOUND, file_share_service_ids)
    file_share_services = ret

    if not status:
        return file_share_services

    for file_share_service_id, file_share_service in file_share_services.items():
        if file_share_service["status"] != status:
            logger.error("file share service %s status %s invaild" % (file_share_service_id, file_share_service["status"]))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_FILE_SHARE_SERVICE_CANT_USE)

    return file_share_services

def register_new_file_share_group(sender,file_share_group_name,file_share_group_dn,base_dn):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_services(status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if not ret:
        return 0
    file_share_services = ret
    file_share_service_id = file_share_services.keys()[0]

    # get scope
    scope = get_file_share_group_scope(base_dn)

    file_share_group_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP, ctx.checker)
    update_info = dict(
        file_share_service_id=file_share_service_id,
        file_share_group_id=file_share_group_id,
        file_share_group_name=file_share_group_name,
        show_location= '["vm_tools_page","user_web_page"]',
        scope=scope,
        file_share_group_dn=file_share_group_dn,
        base_dn=base_dn,
        create_time=get_current_time()
    )
    if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP, update_info):
        logger.error("insert newly created file share group for [%s] to db failed" % (update_info))
        return -1

    ret = set_file_share_group_zone(sender, file_share_group_id=file_share_group_id,user_scope=scope)
    if isinstance(ret, Error):
        return ret

    return file_share_group_id

def check_restore_folder_status(sender):
    ctx = context.instance()

    # If the original folder has been deleted, you need to create a new folder Restore_Folder in the root directory
    file_share_group_dn = "ou=%s,%s" % (const.FILE_SHARE_RESTORE_FOLDER,const.FILE_SHARE_GROUP_ROOT_BASE_DN)
    file_share_group_name = const.FILE_SHARE_RESTORE_FOLDER
    base_dn = const.FILE_SHARE_GROUP_ROOT_BASE_DN
    ret = ctx.pgm.get_file_share_groups(file_share_group_dn=file_share_group_dn,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if not ret:
        ret = register_new_file_share_group(sender, file_share_group_name, file_share_group_dn, base_dn)
        if ret < 0:
            logger.error("register_new_file_share_group %s fail" % (file_share_group_name))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_ftp_ip_flag():

    cmd = "ls /pitrix/conf/configure_vsftp/check_ftp_ip_flag"
    ret = exec_cmd(cmd=cmd)
    if ret != None and ret[0] == 0:
        return True
    return False

def check_ftp_username_password_flag():

    cmd = "ls /pitrix/conf/configure_vsftp/check_ftp_username_password_flag"
    ret = exec_cmd(cmd=cmd,suppress_log=True)
    if ret != None and ret[0] == 0:
        return True
    return False

def check_ftp_put_status_flag():

    cmd = "ls /pitrix/conf/configure_vsftp/check_ftp_put_status_flag"
    ret = exec_cmd(cmd=cmd,suppress_log=True)
    if ret != None and ret[0] == 0:
        return True
    return False

def check_ftp_get_status_flag():

    cmd = "ls /pitrix/conf/configure_vsftp/check_ftp_get_status_flag"
    ret = exec_cmd(cmd=cmd,suppress_log=True)
    if ret != None and ret[0] == 0:
        return True
    return False

def check_ftp_mkdir_and_delete_status_flag():

    cmd = "ls /pitrix/conf/configure_vsftp/check_ftp_mkdir_and_delete_status_flag"
    ret = exec_cmd(cmd=cmd,suppress_log=True)
    if ret != None and ret[0] == 0:
        return True
    return False

def check_vsftp_access_status_valid(ftp_username,ftp_password,ftp_ip,is_sync):

    ctx = context.instance()
    exec_script = "/pitrix/conf/configure_vsftp/check_vsftp_access_status.sh -p %s -u %s -w %s" %(ftp_ip,ftp_username,ftp_password)
    cmd = "/bin/bash %s" %(exec_script)
    os.system("%s" % (cmd))

    # check_ftp_ip_flag
    ret = check_ftp_ip_flag()
    if not ret:
        logger.error("check_ftp_ip_flag fail")
        return Error(ErrorCodes.LOAD_FTP_FILE_SHARE_SERVICE_ERROR,
                     ErrorMsg.ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_IP_ERROR)

    # check_ftp_username_password_flag
    ret = check_ftp_username_password_flag()
    if not ret:
        logger.error("check_ftp_username_password_flag fail")
        return Error(ErrorCodes.LOAD_FTP_FILE_SHARE_SERVICE_ERROR,
                     ErrorMsg.ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_USERNAME_PASSWORD_ERROR)

    if is_sync:
        # check_ftp_put_status_flag
        ret = check_ftp_put_status_flag()
        if not ret:
            logger.error("check_ftp_put_status_flag fail")
            return Error(ErrorCodes.LOAD_FTP_FILE_SHARE_SERVICE_ERROR,
                         ErrorMsg.ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_PUT_FAIL)

        # check_ftp_get_status_flag
        ret = check_ftp_get_status_flag()
        if not ret:
            logger.error("check_ftp_get_status_flag fail")
            return Error(ErrorCodes.LOAD_FTP_FILE_SHARE_SERVICE_ERROR,
                         ErrorMsg.ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_GET_FAIL)

        # check_ftp_mkdir_and_delete_status_flag
        ret = check_ftp_mkdir_and_delete_status_flag()
        if not ret:
            logger.error("check_ftp_mkdir_and_delete_status_flag fail")
            return Error(ErrorCodes.LOAD_FTP_FILE_SHARE_SERVICE_ERROR,
                         ErrorMsg.ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_DELETE_FAIL)

    return None

def load_file_share_service(req):

    ctx = context.instance()
    desktop_server_instance_id = APIFileShare.get_desktop_server_instance_id()
    file_share_service_id = get_uuid(UUID_TYPE_FILE_SHARE_SERVICE, ctx.checker)
    update_info = dict(
        file_share_service_id=file_share_service_id,
        file_share_service_name=req.get("file_share_service_name", ''),
        description=req.get("description", ''),
        network_id=req.get("network_id", ''),
        desktop_server_instance_id=desktop_server_instance_id,
        file_share_service_instance_id='',
        private_ip=req.get("private_ip", ''),
        vnas_id=req.get("vnas_id", ''),
        is_sync=req.get("is_sync",0),
        limit_rate=req.get("limit_rate", 1),
        limit_conn=req.get("limit_conn", 0),
        status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE,
        scope=req.get("scope",const.FILE_SHARE_GROUP_ZONE_SCOPE_PART_ROLES),
        fuser=req.get("fuser"),
        fpw=req.get("fpw"),
        ftp_chinese_encoding_rules=const.FTP_SERVER_CHINESE_ENCODING_RULES_GBK,
        create_method=const.FILE_SHARE_SERVICE_CREATE_METHOD_LOADED,
        max_download_file_size=req.get("max_download_file_size", 100),
        max_upload_size_single_file=req.get("max_upload_size_single_file", 1),
        create_time=get_current_time(),
        status_time=get_current_time(),
    )
    # register file_share_service
    if not ctx.pg.insert(dbconst.TB_FILE_SHARE_SERVICE, update_info):
        logger.error("insert newly created file share service for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return file_share_service_id

def check_file_share_service_create_method(file_share_services):

    ctx = context.instance()

    if not file_share_services:
        return None

    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
        if create_method != const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED:
            logger.error("the loaded server does not support password reset")
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_LOADED_FILE_SHAER_SERVICE_NOT_SUPPORT_PASSWORD_RESET)

    return None

def reset_file_share_service_password(file_share_services,ftp_username,ftp_password):

    ctx = context.instance()

    if not file_share_services:
        return None

    # reset password
    ret = APIFileShare.reset_remote_ftp_server_vsftp_password(ctx,ftp_username,ftp_password)
    if not ret:
        logger.error("reset remote_ftp_server login user [%s] password failed" % ftp_username)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESET_FILE_SHARE_SERVICE_PASSWORD_FAILED, ftp_username)

    return None


def update_file_share_service_password(file_share_services,fpw):

    ctx = context.instance()
    # update db ftp_password
    for file_share_service_id,file_share_service in file_share_services.items():

        condition = {"file_share_service_id": file_share_service_id}
        update_info = dict(
            fpw=fpw
        )
        if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_SERVICE, condition, update_info):
            logger.error("update file share service for [%s] to db failed" % (update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return None

def check_remote_cloned_instance_file_exist_status(sender, file_share_group_files):

    ctx = context.instance()
    if not file_share_group_files:
        return None

    for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
        file_share_group_file_size = file_share_group_file["file_share_group_file_size"]
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
        file_share_group_dn = file_share_group_file["file_share_group_dn"]

        path = APIFileShare.dn_to_path(file_share_group_dn)
        destination_path = "%s%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI,path,file_share_group_file_name)

        # check remote_cloned_instance /mnt/nasdata/ront/***.txt is exist or not
        localhost_cache = APIFileShare.check_remote_cloned_instance_mnt_nasdata_file_exist_status(ctx,destination_path,file_share_group_file_size)

        if localhost_cache:
            return True
        else:
            return False
        
    return None









