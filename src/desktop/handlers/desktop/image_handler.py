
import context
from db.constants  import (
    TB_DESKTOP_IMAGE,
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
)
from common import (
    build_filter_conditions,
    filter_out_none,
    check_global_admin_console,
    check_admin_console,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
    is_citrix_platform
)
import constants as const
import db.constants as dbconst
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.image as Image
import resource_control.desktop.resource_permission as ResCheck
import resource_control.permission as Permission
from utils.misc import get_columns

def handle_describe_desktop_images(req):

    ctx = context.instance()
    sender = req["sender"]

    desktop_image_ids = req.get("desktop_images")
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_IMAGE)
    if desktop_image_ids:
        filter_conditions["desktop_image_id"] = desktop_image_ids

    # global admin user can see all resources
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_IMAGE]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_IMAGE]
    else:
        display_columns = {}
    
    Image.check_default_images(sender)
    
    if "image_type" not in filter_conditions:
        filter_conditions["image_type"] = const.SUPPORT_IMG_TYPES

    image_set = ctx.pg.get_by_filter(TB_DESKTOP_IMAGE, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_DESKTOP_IMAGE, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if image_set is None:
        logger.error("describe desktop image failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    Image.format_desktop_image(image_set)
    Image.format_resource_image(sender, image_set)

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_IMAGE, filter_conditions)
    if total_count is None:
        logger.error("get desktop image count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, image_set, "desktop_image", **rep)

def handle_create_desktop_image(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_image", "instance_class"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_image_id = req["desktop_image"]
    instance_class = req["instance_class"]
    cpu = req["cpu"]
    memory = req["memory"]

    # check desktop image availd
    ret = Image.check_desktop_image_vaild(desktop_image_id, const.IMG_STATUS_AVL)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # check param
    desktop_image = ret[desktop_image_id]
    desktop_image["instance_class"] = instance_class
    desktop_image["image_name"] = req.get("image_name", '')
    desktop_image["description"] = req.get("description", '')
    desktop_image["cpu"] = cpu
    desktop_image["memory"] = memory
    if "image_size" in req:
        
        ret = Image.check_image_os_size(desktop_image, req["image_size"])
        if isinstance(ret, Error):
            return return_error(req, ret)

        desktop_image["image_size"] = req["image_size"]

    # create desktop image id
    ret = Image.register_self_image(sender, desktop_image)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_image_id = ret

    network_id = req.get("network")
    if network_id:
        ret = Image.update_desktop_image_network(sender, desktop_image_id, network_id)
        if isinstance(ret, Error):
            Image.delete_desktop_images(desktop_image_id)
            return return_error(req, ret)

    # submit desktop job
    ret = Image.send_desktop_image_job(sender, desktop_image_id, const.JOB_ACTION_CREATE_IMAGES)
    if isinstance(ret, Error):
        Image.delete_desktop_images(desktop_image_id)
        return return_error(req, ret)
    job_uuid = ret

    ret = {"desktop_image": desktop_image_id}
    return return_success(req, None, job_uuid, **ret)

def handle_save_desktop_images(req):

    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["desktop_images"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_image_ids = req["desktop_images"]

    # check desktop image availd
    ret = Image.check_desktop_image_vaild(desktop_image_ids, const.IMG_STATUS_EDITED)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_images = ret
        
    ret = Image.check_save_desktop_image_status(sender, desktop_images)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_image_ids = ret

    # submit desktop job
    ret = Image.send_desktop_image_job(sender, desktop_image_ids, const.JOB_ACTION_SAVE_IMAGES)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_uuid = ret

    # register resource permission
    for desktop_image_id in desktop_image_ids:
        Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_IMAGE, desktop_image_id, sender["zone"], dbconst.RES_SCOPE_DELETE)
    
    return return_success(req, None, job_uuid)

def handle_delete_desktop_images(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_images"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_image_ids = req.get("desktop_images")
    
    ret = Image.filter_default_images(sender, desktop_image_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    # check desktop image availd
    ret = Image.check_desktop_image_vaild(desktop_image_ids, is_used=True)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_images = ret
    
    ret = Image.update_desktop_image_status(sender, desktop_images)
    if isinstance(ret, Error):
        return return_error(req, ret)

    delete_image, clear_image= ret

    if clear_image:
        ret = Image.delete_desktop_images(clear_image)
        if isinstance(ret, Error):
            return return_error(req, ret)

    job_uuid = None
    if delete_image:
        # submit desktop job
        ret = Image.send_desktop_image_job(sender, delete_image, const.JOB_ACTION_DELETE_IMAGES)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    # clear resource permission
    Permission.clear_user_resource_scope(resource_ids=delete_image)

    return return_success(req, None, job_uuid)

def handle_modify_desktop_image_attributes(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_image"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_image_id = req.get("desktop_image")
    
    ret = Image.filter_default_images(sender, desktop_image_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # check desktop image availd
    ret = Image.check_desktop_image_vaild(desktop_image_id, check_trans_status=False)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_image = ret[desktop_image_id]
    
    columns = get_columns(req, ["image_name", "description"])
    if columns:
        ret = Image.modify_desktop_image_attributes(sender, desktop_image, columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_load_system_images(req):
    
    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["images"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    image_ids = req["images"]

    if not check_global_admin_console(sender):
        logger.error("only global admin user can load system image %s" % image_ids)
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_PRIVILEGE_ACCESS_DENIED))
    
    os_version = req.get("os_version")
    image_name = req.get("image_name")
    session_type = req.get("session_type", const.OS_SESSION_TYPE_SINGLE)
    
    ret = ctx.pgm.get_system_image(image_ids, zone_id=sender["zone"])
    if ret:
        logger.error("system image already existed %s" % ret.keys())
        return return_error(req, Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                                       ErrorMsg.ERR_MSG_SYSTEM_IMAGE_ALREADY_EXISTED, image_ids))
    
    ret = ctx.res.resource_describe_images(sender["zone"], image_ids)
    if ret is None:
        logger.error("describe image iaas request return fail %s" % ret)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, image_ids))
    images = ret

    desktop_image_ids = []
    for image_id in image_ids:
        if image_id not in images:
            logger.error("describe image iaas request return fail %s" % image_id)
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, image_id))
        image = images[image_id]
        status = image["status"]
        if status != const.IMG_STATUS_AVL:
            logger.error("describe image status invaild %s, %s" % (image_id, status))
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                           ErrorMsg.ERR_MSG_CLOUD_RESOURCE_STATUS_INVAILD, image_id))
        
        if is_citrix_platform(ctx, sender["zone"]):
            if image["ui_type"] == const.IMG_UI_TYPE_GUI:
                logger.error("image ui_type invaild %s , %s" % (image_id, image["ui_type"]))
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                               ErrorMsg.ERR_MSG_IMAGE_UI_TYPE_DISMATCH, image_id))

        desktop_image = {}
        desktop_image["image_name"] = image_name if image_name else image["image_name"]
        desktop_image["description"] = image["description"]
        desktop_image["platform"] = image["platform"]
        desktop_image["os_family"] = image["os_family"]
        desktop_image["session_type"] = session_type if session_type else ''
        desktop_image["os_version"] = os_version if os_version else ''
        desktop_image["image_size"] = image["size"]
        desktop_image["ui_type"] = image["ui_type"]
        # create desktop image id
        ret = Image.register_system_image(sender, desktop_image, image["image_id"])
        if isinstance(ret, Error):
            return return_error(req, ret)

        desktop_image_id = ret
        desktop_image_ids.append(desktop_image_id)

    ret = {'desktop_image': desktop_image_ids}
    return return_success(req, None, **ret)

def handle_describe_system_images(req):
    
    sender = req["sender"]
    ctx = context.instance()

    if not check_global_admin_console(sender):
        rep = {'total_count': 0} 
        return return_items(req, None, "image", **rep)

    valid_keys = ["provider", "os_family", "limit", "offset", "search_word"]
    body = filter_out_none(req, valid_keys)
    
    images = {}
    image_ids = req.get("images")

    if not image_ids:

        if is_citrix_platform(ctx, sender["zone"]):
            body["ui_type"] = const.IMG_UI_TYPE_TUI
        else:
            body["ui_type"] = const.IMG_UI_TYPE_GUI

    ret = Image.filter_system_image(sender, body, image_ids)
    if ret:
        images = ret
    total_count = len(images)
    
    rep = {'total_count': total_count} 
    return return_items(req, images, "image", **rep)

