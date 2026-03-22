import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    MAX_LIMIT,
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
import resource_control.file_share.file_share as FileShare
import resource_control.file_share.sync_file_share as SyncFileShare
import api.user.user as APIUser
from utils.misc import get_columns
import constants as const
from db.data_types import SearchType
from utils.auth import get_base64_password,set_base64_password
import os

def handle_describe_file_share_groups(req):

    ctx = context.instance()
    sender = req["sender"]
    FileShare.check_file_share_unicode_param(req)

    filter_conditions = build_filter_conditions(req, dbconst.TB_FILE_SHARE_GROUP)

    file_share_group_ids = req.get("file_share_groups")
    if file_share_group_ids:
        filter_conditions["file_share_group_id"] = file_share_group_ids

    base_dn = req.get("base_dn",const.FILE_SHARE_GROUP_ROOT_BASE_DN)
    if base_dn:
        filter_conditions["base_dn"] = base_dn

    show_location = req.get("show_location")
    if show_location:
        filter_conditions["show_location"] = SearchType(show_location)

    filter_conditions["trashed_status"] = const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE

    logger.info("filter_conditions == %s" %(filter_conditions))
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_FILE_SHARE_GROUP]

    file_share_group_set = ctx.pg.get_by_filter(dbconst.TB_FILE_SHARE_GROUP, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_FILE_SHARE_GROUP, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if file_share_group_set is None:
        logger.error("describe file share group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format file_share_group_set
    FileShare.format_file_share_group(sender, file_share_group_set)

    # format file_share_group_set
    if not APIUser.is_global_admin_user(sender):
        FileShare.format_file_share_group_user(sender, file_share_group_set)

    # format file_share_grup_set
    FileShare.format_file_share_group_file_count(sender, file_share_group_set)

    # get total count
    total_count = len(file_share_group_set)
    rep = {'total_count': total_count}
    return return_items(req, file_share_group_set, "file_share_group", **rep)

def handle_create_file_share_group(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_group_name","file_share_service"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)

    file_share_group_name = req["file_share_group_name"]
    base_dn = req.get("base_dn",const.FILE_SHARE_GROUP_ROOT_BASE_DN)
    description = req.get("description")

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_service_transition_status(file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_file_share_group_name_vaild(file_share_group_name, base_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.create_file_share_group(sender,req,file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group_dn = ret

    ret = {"file_share_group_dn": file_share_group_dn}
    return return_success(req, None, **ret)

def handle_modify_file_share_group_attributes(req):

    ret = ResCheck.check_request_param(req, ["file_share_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)
    file_share_group_id = req["file_share_groups"]

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_modify_file_share_group_attributes(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_maint_columns = ret

    need_maint_columns["description"] = req.get("description","")

    if need_maint_columns:
        ret = FileShare.modify_file_share_group_attributes(file_share_group_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_rename_file_share_group(req):

    ret = ResCheck.check_request_param(req, ["file_share_groups","file_share_group_dn","new_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)
    file_share_group_id = req["file_share_groups"]
    file_share_group_dn = req["file_share_group_dn"]
    new_name = req["new_name"]

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_group_vaild(file_share_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group = ret[file_share_group_id]

    ret = FileShare.check_rename_file_share_group_dn(file_share_group,file_share_group_dn, new_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.rename_file_share_group_dn(file_share_group, file_share_group_dn, new_name,file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_delete_file_share_groups(req):

    ret = ResCheck.check_request_param(req, ["file_share_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    file_share_group_id = req["file_share_groups"][0]

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_group_vaild(file_share_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group = ret[file_share_group_id]

    ret = FileShare.delete_file_share_groups(file_share_group,file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_modify_file_share_group_zone_user(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_groups", "zone_users","scope"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    zone_users = json_load(req["zone_users"])
    file_share_group_id = req["file_share_groups"]
    scope = req["scope"]

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_set_file_share_group_zone_user(sender, file_share_group_id, zone_users)
    if isinstance(ret, Error):
        return return_error(req, ret)

    if not ret:
        logger.error("request param %s format error" % "zone_users")
        return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                     ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED)

    zone_users = ret
    ret = FileShare.modify_file_share_group(sender, file_share_group_id, scope)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.modify_file_share_group_zone_user(sender, file_share_group_id, zone_users)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_file_share_group_files(req):

    ctx = context.instance()
    sender = req["sender"]

    FileShare.check_file_share_unicode_param(req)

    filter_conditions = build_filter_conditions(req, dbconst.TB_FILE_SHARE_GROUP_FILE)
    file_share_group_ids = req.get("file_share_groups",[])
    if file_share_group_ids and file_share_group_ids != ['']:
        filter_conditions["file_share_group_id"] = file_share_group_ids

    if file_share_group_ids == ['']:
        rep = {'total_count': 0}
        return return_items(req, None, "file_share_group_file", **rep)

    file_share_group_file_ids = req.get("file_share_group_files",[])
    if file_share_group_file_ids:
        filter_conditions["file_share_group_file_id"] = file_share_group_file_ids

    filter_conditions["trashed_status"] = const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]

    logger.info("filter_conditions == %s" %(filter_conditions))
    file_share_group_file_set = ctx.pg.get_by_filter(dbconst.TB_FILE_SHARE_GROUP_FILE, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_FILE_SHARE_GROUP_FILE, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", MAX_LIMIT),
                                           )

    if file_share_group_file_set is None:
        logger.error("describe file share group file failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format file_share_group_file_set
    verbose = req.get("verbose",1)
    FileShare.format_file_share_group_file(sender, file_share_group_file_set, verbose)

    if not APIUser.is_global_admin_user(sender) and file_share_group_ids:
        # format file_share_group_file_set
        FileShare.format_file_share_group_file_user(sender, file_share_group_file_set,file_share_group_ids)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_FILE_SHARE_GROUP_FILE, filter_conditions)
    if total_count is None:
        logger.error("get file share group file count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}

    # get file_share_group_info
    ret = FileShare.get_file_share_group_info(file_share_group_id=file_share_group_ids)
    if ret:
        rep.update(ret)

    return return_items(req, file_share_group_file_set, "file_share_group_file", **rep)

def handle_upload_file_share_group_files(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_groups", "upload_files"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)

    file_share_group_id = req.get("file_share_groups")
    upload_files = json_load(req["upload_files"])

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_group_vaild(file_share_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group = ret[file_share_group_id]

    ret = FileShare.upload_file_share_group_files(file_share_group ,upload_files)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group_file_ids = ret

    # extra
    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
    extra = {"create_method": create_method}

    # send file_share_group_file job
    job_uuid = None
    if file_share_group_file_ids:
        ret = FileShare.send_desktop_file_share_job(sender, file_share_group_file_ids,const.JOB_ACTION_UPLOAD_FILE_SHARES,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_download_file_share_group_files(req):

    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_group_files"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    file_share_group_file_ids = req.get("file_share_group_files")

    ret = FileShare.register_download_file_share_group_file_history(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_group_file_vaild(file_share_group_file_ids,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group_files = ret

    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
        if const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED == create_method:
            ret = {"file_share_group_file_id": file_share_group_file_ids}
            return return_success(req, None, **ret)
        else:
            ret = FileShare.check_remote_cloned_instance_file_exist_status(sender, file_share_group_files)
            if ret:
                ret = {"file_share_group_file_id": file_share_group_file_ids}
                return return_success(req, None, **ret)

            for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
                transition_status = file_share_group_file["transition_status"]
                if const.FILE_SHARE_STATUS_DOWNLOADING == transition_status:
                    logger.info("resource [%s] is [downloading], please try later" %(file_share_group_file_id))
                    job_uuid = None
                    tasks = ctx.pgm.get_tasks(status=const.JOB_STATUS_WORKING,
                                              task_type=const.TASK_ACTION_DOWNLOAD_FILE_SHARES,
                                              task_level=1,
                                              resource_ids=file_share_group_file_id)
                    if tasks:
                        for task_id,task in tasks.items():
                            job_uuid = task["job_id"]
                    return return_success(req, None, job_uuid)

            # extra
            extra = {"create_method": create_method}

            # send file_share_group_file job
            job_uuid = None
            if file_share_group_file_ids:
                ret = FileShare.send_desktop_file_share_job(sender, file_share_group_file_ids,const.JOB_ACTION_DOWNLOAD_FILE_SHARES,extra)
                if isinstance(ret, Error):
                    return return_error(req, ret)
                job_uuid = ret

            return return_success(req, None, job_uuid)

def handle_describe_file_share_group_file_download_history(req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY)
    file_share_group_file_ids = req.get("file_share_group_files")
    if file_share_group_file_ids:
        filter_conditions["file_share_group_file_id"] = file_share_group_file_ids

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY]

    file_share_group_file_download_history_set = ctx.pg.get_by_filter(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if file_share_group_file_download_history_set is None:
        logger.error("describe file share group file download history failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, filter_conditions)
    if total_count is None:
        logger.error("get file share group file download history count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, file_share_group_file_download_history_set, "file_share_group_file_download_history", **rep)

def handle_modify_file_share_group_file_attributes(req):

    ret = ResCheck.check_request_param(req, ["file_share_group_files","file_share_group_file_alias_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)
    file_share_group_file_id = req["file_share_group_files"]

    ret = FileShare.check_modify_file_share_group_file_attributes(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_maint_columns = ret

    need_maint_columns["description"] = req.get("description","")
    if need_maint_columns:
        ret = FileShare.modify_file_share_group_file_attributes(file_share_group_file_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_delete_file_share_group_files(req):
  
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_group_files"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    file_share_group_file_ids = req["file_share_group_files"]

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_group_file_vaild(file_share_group_file_ids,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group_files = ret

    ret = FileShare.check_file_share_group_file_transition_status(file_share_group_file_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # extra
    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
    extra = {"create_method": create_method}

    # send file_share job
    job_uuid = None
    if file_share_group_file_ids:
        ret = FileShare.send_desktop_file_share_job(sender, file_share_group_file_ids,const.JOB_ACTION_DELETE_FILE_SHARE_GROUP_FILES,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_describe_file_share_capacity(req):

    sender = req["sender"]
    ctx=context.instance()
    ret = ResCheck.check_request_param(req, ["vnas_node_dir"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    # init info
    mnt_nasdata_exist = 1
    total_size = "0K"
    used_size = '0K'
    remain_size = '0K'
    local_desktop_server_remain_size = '0K'
    os.system("chmod -R 777 /mnt/nasdata")

    ret = ctx.pgm.get_file_share_services()
    if ret:
        file_share_services = ret

        for file_share_services,file_share_service in file_share_services.items():
            create_method = file_share_service.get("create_method")
            if const.FILE_SHARE_SERVICE_CREATE_METHOD_LOADED == create_method:
                mnt_nasdata_exist = 1
                total_size = "103081344K"
                used_size = "0K"
                remain_size = "103081344K"
                local_desktop_server_remain_size = "103081344K"
            elif const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED == create_method:
                vnas_node_dir = req.get("vnas_node_dir", const.DOWNLOAD_SOFTWARE_BASE_URI)
                ret = FileShare.check_file_share_vnas_node_dir(vnas_node_dir)
                if isinstance(ret, Error):
                    return return_error(req, ret)
                (mnt_nasdata_exist, total_size, used_size, remain_size, local_desktop_server_remain_size) = ret
            else:
                logger.error("invalid create_method %s" %(create_method))


    ret = {
            "mnt_nasdata_exist": mnt_nasdata_exist,
            "total_size":total_size,
            "used_size":used_size,
            "remain_size": remain_size,
            "local_desktop_server_remain_size":local_desktop_server_remain_size
        }

    return return_success(req, None, **ret)

def handle_change_file_in_file_share_group(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_group_files", "new_file_share_group_dn",'change_type'])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)

    file_share_group_file_ids = req["file_share_group_files"]
    new_file_share_group_dn = req["new_file_share_group_dn"]
    change_type = req["change_type"]
    file_save_method = req.get("file_save_method",'')

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_group_file_vaild(file_share_group_file_ids,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group_files = ret

    ret = FileShare.check_file_share_group_file_transition_status(file_share_group_file_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_file_share_group_file_name_vaild(file_share_group_files, new_file_share_group_dn,change_type)
    if isinstance(ret, Error):
        return return_error(req, ret)
    repeat_file_ids = ret


    if  repeat_file_ids and not file_save_method:
        file_save_method = const.SOURCE_FILE_SAVE_METHOD_OVERWRITE

    # extra
    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")

    extra = {
                "new_file_share_group_dn": new_file_share_group_dn,
                "change_type": change_type,
                "file_save_method":file_save_method,
                "repeat_file_ids":repeat_file_ids,
                "create_method": create_method
            }

    # send file_share job
    job_uuid = None
    if file_share_group_file_ids:
        ret = FileShare.send_desktop_file_share_job(sender, file_share_group_file_ids,const.JOB_ACTION_CHANGE_FILE_IN_FILE_SHARE_GROUP, extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_describe_file_share_recycles(req):

    ctx = context.instance()
    sender = req["sender"]

    FileShare.check_file_share_unicode_param(req)

    filter_conditions = build_filter_conditions(req, dbconst.TB_FILE_SHARE_GROUP_FILE)

    file_share_group_file_ids = req.get("file_share_group_files")
    if file_share_group_file_ids:
        filter_conditions["file_share_group_file_id"] = file_share_group_file_ids

    filter_conditions["trashed_status"] = const.FILE_SHARE_RECYCLES_TRASHED_STATUS_ACTIVE
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]

    file_share_group_file_set = ctx.pg.get_by_filter(dbconst.TB_FILE_SHARE_GROUP_FILE, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_FILE_SHARE_GROUP_FILE, req.get("sort_key"),default_key='trashed_time'),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", MAX_LIMIT),
                                           )

    if file_share_group_file_set is None:
        logger.error("describe file share group file failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_FILE_SHARE_GROUP_FILE, filter_conditions)
    if total_count is None:
        logger.error("get file share group file count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, file_share_group_file_set, "file_share_group_file", **rep)

def handle_restore_file_share_recycles(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_group_files"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    file_share_group_file_ids = req["file_share_group_files"]

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_group_file_vaild(file_share_group_file_ids,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group_files = ret

    ret = FileShare.check_file_share_group_file_transition_status(file_share_group_file_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_restore_folder_status(sender)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # extra
    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
    extra = {"create_method": create_method}

    # send file_share job
    job_uuid = None
    if file_share_group_file_ids:
        ret = FileShare.send_desktop_file_share_job(sender, file_share_group_file_ids,const.JOB_ACTION_RESTORE_FILE_SHARE_RECYCLES,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_delete_permanently_file_share_recycles(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_group_files"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    file_share_group_file_ids = req["file_share_group_files"]

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_delete_permanently_file_share_recycles_vaild(file_share_group_file_ids,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group_files = ret

    ret = FileShare.check_file_share_group_file_transition_status(file_share_group_file_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # extra
    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
    extra = {"create_method": create_method}

    # send file_share job
    job_uuid = None
    if file_share_group_file_ids:
        ret = FileShare.send_desktop_file_share_job(sender, file_share_group_file_ids,const.JOB_ACTION_DELETE_PERMANENTLY_FILE_SHARE_RECYCLES,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_empty_file_share_recycles(req):

    sender = req["sender"]

    ret = FileShare.check_file_share_service_status_valid(file_share_service_ids=None,status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_empty_file_share_recycles_vaild(trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_group_files = ret

    file_share_group_file_ids = file_share_group_files.keys()
    ret = FileShare.check_file_share_group_file_transition_status(file_share_group_file_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # extra
    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
    extra = {"create_method": create_method}

    # send file_share job
    job_uuid = None
    if file_share_group_file_ids:
        ret = FileShare.send_desktop_file_share_job(sender,file_share_group_file_ids,const.JOB_ACTION_EMPTY_FILE_SHARE_RECYCLES,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_create_file_share_service(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_service_name", "network_id","fuser","fpw","is_sync","scope"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)
    vnas_disk_size = req.get("vnas_disk_size",const.FILE_SHARE_DEFAULT_VNAS_DISK_SIZE)
    vnas_id = req.get("vnas_id", '')
    network_id = req.get("network_id", '')

    ret = FileShare.check_create_file_share_service_vaild()
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_user_quota_left(sender,vnas_disk_size,vnas_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_network_id_valid(sender,network_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.create_file_share_service(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_service_id = ret

    extra = {"vnas_disk_size":vnas_disk_size}
    # send file_share job
    job_uuid = None
    if file_share_service_id:
        ret = FileShare.send_file_share_service_job(sender, file_share_service_id,const.JOB_ACTION_CREATE_FILE_SHARE_SERVICE,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_load_file_share_service(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_service_name", "private_ip","fuser","fpw","is_sync","scope"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)
    fuser = req.get("fuser")
    fpw = req.get("fpw")
    private_ip = req.get("private_ip")
    is_sync = req.get("is_sync",0)

    ret = FileShare.check_create_file_share_service_vaild()
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_user_quota_left(sender,vnas_disk_size=const.FILE_SHARE_DEFAULT_VNAS_DISK_SIZE,vnas_id=None)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.get_available_network_id(sender)
    if isinstance(ret, Error):
        return return_error(req, ret)
    available_network_id = ret
    req["network_id"] = available_network_id

    # check_vsftp_access_status_valid
    ftp_username = fuser
    ftp_password = get_base64_password(fpw)
    ftp_ip = private_ip
    ret = FileShare.check_vsftp_access_status_valid(ftp_username=ftp_username,ftp_password=ftp_password,ftp_ip=ftp_ip,is_sync=is_sync)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.load_file_share_service(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_service_id = ret

    extra = {"vnas_disk_size":const.FILE_SHARE_DEFAULT_VNAS_DISK_SIZE}
    # send file_share job
    job_uuid = None
    if file_share_service_id:
        ret = FileShare.send_file_share_service_job(sender, file_share_service_id,const.JOB_ACTION_LOAD_FILE_SHARE_SERVICE,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_describe_file_share_services(req):

    ctx = context.instance()
    sender = req["sender"]

    FileShare.check_file_share_unicode_param(req)

    filter_conditions = build_filter_conditions(req, dbconst.TB_FILE_SHARE_SERVICE)

    file_share_service_ids = req.get("file_share_services")
    if file_share_service_ids:
        filter_conditions["file_share_service_id"] = file_share_service_ids

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_SERVICE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_SERVICE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_FILE_SHARE_SERVICE]

    file_share_serivce_set = ctx.pg.get_by_filter(dbconst.TB_FILE_SHARE_SERVICE, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_FILE_SHARE_GROUP_FILE, req.get("sort_key"),default_key='create_time'),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if file_share_serivce_set is None:
        logger.error("describe file share service failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_FILE_SHARE_SERVICE, filter_conditions)
    if total_count is None:
        logger.error("get file share service count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, file_share_serivce_set, "file_share_service", **rep)

def handle_modify_file_share_service_attributes(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_services","file_share_service_name","fuser","fpw","is_sync"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    FileShare.check_file_share_unicode_param(req)

    file_share_service_id = req["file_share_services"]
    scope = req.get("scope")
    fuser = req.get("fuser")
    fpw = req.get("fpw")
    # test
    # fpw = set_base64_password(fpw)
    is_sync = req.get("is_sync",0)

    ret = FileShare.check_file_share_service_vaild(file_share_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    # get private_ip
    private_ip = ''
    for _,file_share_service in file_share_services.items():
        private_ip = file_share_service.get("private_ip")

    ret = FileShare.check_file_share_service_transition_status(file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # check_vsftp_access_status_valid
    ftp_username = fuser
    ftp_password = get_base64_password(fpw)
    ftp_ip = private_ip
    ret = FileShare.check_vsftp_access_status_valid(ftp_username=ftp_username,ftp_password=ftp_password,ftp_ip=ftp_ip,is_sync=is_sync)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_modify_file_share_service_attributes(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_maint_columns = ret

    job_uuid = None
    need_maint_columns["description"] = req.get("description","")
    if need_maint_columns:
        ret = FileShare.modify_file_share_service_attributes(sender,file_share_service_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

        create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
        for file_share_service_id, file_share_service in file_share_services.items():
            create_method = file_share_service.get("create_method")

        # extra
        limit_rate = int(req.get("limit_rate", 1))
        limit_conn = int(req.get("limit_conn", 0))
        extra = {"limit_rate": limit_rate,"limit_conn":limit_conn,"create_method":create_method}

        # send file_share job
        if file_share_service_id and const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED == create_method:
            ret = FileShare.send_file_share_service_job(sender, file_share_service_id,const.JOB_ACTION_MODIFY_FILE_SHARE_SERVICE, extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_delete_file_share_services(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_services"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    file_share_service_ids = req["file_share_services"]
    force_delete = req.get("force_delete",0)

    ret = FileShare.check_file_share_service_vaild(file_share_service_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_service_transition_status(file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # extra
    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for _,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
    extra = {"create_method": create_method}

    # send file_share job
    job_uuid = None
    ret = FileShare.send_file_share_service_job(sender,file_share_service_ids,const.JOB_ACTION_DELETE_FILE_SHARE_SERVICE,extra)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_refresh_file_share_service(req):

    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["file_share_services"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    file_share_service_id = req["file_share_services"]

    ret = FileShare.check_file_share_service_vaild(file_share_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_service_transition_status(file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.refresh_file_share_service(sender,file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.refresh_file_share_service_vnas(sender)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.check_file_share_service_vaild(file_share_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    # extra
    create_method = const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED
    for file_share_service_id,file_share_service in file_share_services.items():
        create_method = file_share_service.get("create_method")
        status = file_share_service.get("status")
    extra = {"create_method": create_method}

    # send file_share job
    job_uuid = None
    if file_share_service_id and const.FILE_SHARE_SERVICE_STATUS_ACTIVE == status:
        ret = FileShare.send_file_share_service_job(sender,file_share_service_id,const.JOB_ACTION_REFRESH_FILE_SHARE_SERVICE,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_describe_file_share_service_vnas(req):

    ctx = context.instance()
    sender = req["sender"]

    ret = FileShare.refresh_file_share_service_vnas(sender)
    if isinstance(ret, Error):
        return return_error(req, ret)

    filter_conditions = build_filter_conditions(req, dbconst.TB_FILE_SHARE_SERVICE_VNAS)
    vnas_ids = req.get("vnas")
    if vnas_ids:
        filter_conditions["vnas_id"] = vnas_ids

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_SERVICE_VNAS]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_SERVICE_VNAS]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_FILE_SHARE_SERVICE_VNAS]

    file_share_serivce_vnas_set = ctx.pg.get_by_filter(dbconst.TB_FILE_SHARE_SERVICE_VNAS, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_FILE_SHARE_SERVICE_VNAS, req.get("sort_key"),default_key='create_time'),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if file_share_serivce_vnas_set is None:
        logger.error("describe file share service vnas failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_FILE_SHARE_SERVICE_VNAS, filter_conditions)
    if total_count is None:
        logger.error("get file share service vnas count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, file_share_serivce_vnas_set, "file_share_serivce_vnas", **rep)

def handle_reset_file_share_service_password(req):

    ctx = context.instance()
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ['fuser','fpw','file_share_services'])
    if isinstance(ret, Error):
        return return_error(req, ret)

    fuser = req.get("fuser")
    fpw = req.get("fpw")
    file_share_service_id = req["file_share_services"]

    ret = FileShare.check_file_share_service_vaild(file_share_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    file_share_services = ret

    ret = FileShare.check_file_share_service_create_method(file_share_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # reset_file_share_service_password
    ftp_username = fuser
    ftp_password = get_base64_password(fpw)
    ret = FileShare.reset_file_share_service_password(file_share_services,ftp_username=ftp_username,ftp_password=ftp_password)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = FileShare.update_file_share_service_password(file_share_services,fpw)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)
