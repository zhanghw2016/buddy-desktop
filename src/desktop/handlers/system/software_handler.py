import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    PUBLIC_COLUMNS,
    DEFAULT_LIMIT,
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

from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.system.software as Software
import api.user.user as APIUser
import constants as const

def handle_describe_softwares(req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_SOFTWARE_INFO)
    software_ids = req.get("softwares")
    if software_ids:
        filter_conditions["software_id"] = software_ids

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_SOFTWARE_INFO]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_SOFTWARE_INFO]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_SOFTWARE_INFO]

    software_info_set = ctx.pg.get_by_filter(dbconst.TB_SOFTWARE_INFO, filter_conditions, display_columns,
                                      sort_key = get_sort_key(dbconst.TB_SOFTWARE_INFO, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if software_info_set is None:
        logger.error("describe software info failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_SOFTWARE_INFO, filter_conditions)
    if total_count is None:
        logger.error("get software info count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, software_info_set, "software_info", **rep)

def handle_upload_softwares(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["software_name", "software_size"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Software.upload_softwares(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    software_ids = ret

    # # send software job
    job_uuid = None
    if software_ids:
        ret = Software.send_desktop_software_job(sender, software_ids,const.JOB_ACTION_UPLOAD_SOFTWARES)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_download_softwares(req):

    ret = ResCheck.check_request_param(req, ["softwares"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    software_id = req.get("softwares")

    ret = Software.download_softwares(software_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    (download_software_uri, download_software_exist) = ret

    ret = {"download_software_uri": download_software_uri,"download_software_exist":download_software_exist}
    return return_success(req, None, **ret)

def handle_delete_softwares(req):

    ret = ResCheck.check_request_param(req, ["softwares"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    software_ids = req.get("softwares")

    ret = Software.delete_softwares(software_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = {"software_ids": software_ids}
    return return_success(req, None, **ret)

def handle_check_software_vnas_node_dir(req):

    ctx = context.instance()
    zone_deploy = ctx.zone_deploy
    ret = ResCheck.check_request_param(req, ["vnas_node_dir"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    vnas_node_dir = req.get("vnas_node_dir")

    ret = Software.check_software_vnas_node_dir(vnas_node_dir,zone_deploy)
    if isinstance(ret, Error):
        return return_error(req, ret)
    (mnt_nasdata_exist,remain_size) = ret

    ret = {"mnt_nasdata_exist": mnt_nasdata_exist,"remain_size":remain_size}
    return return_success(req, None, **ret)
