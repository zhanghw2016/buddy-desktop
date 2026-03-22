import constants as const
import db.constants as dbconst
from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import(
    UUID_TYPE_DESKTOP_IMAGE,
    get_uuid
)
from db.constants import (
    TB_DESKTOP_IMAGE
)
from constants import (
    REQ_TYPE_DESKTOP_JOB,
)
from common import (
    check_resource_transition_status,
    is_citrix_platform
)
from utils.misc import get_current_time
import resource_control.desktop.job as Job
import resource_control.permission as Permission
import resource_control.desktop.network as Network
from resource_control.zone.zone import zone_sync_to_other_server

def send_desktop_image_job(sender, desktop_image_ids, action):

    if not isinstance(desktop_image_ids, list):
        desktop_image_ids = [desktop_image_ids]
    
    directive = {
                "sender": sender,
                "action": action,
                "desktop_images": desktop_image_ids,
                }
    ret = Job.submit_desktop_job(action, directive, desktop_image_ids, REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def get_current_images(sender):
    
    ctx = context.instance()
    image_ids = []
    desktop_images = ctx.pgm.get_desktop_images(zone_id=sender["zone"])
    if not desktop_images:
        return image_ids
    
    for _, image in desktop_images.items():
        image_id = image["image_id"]
        image_ids.append(image_id)
    
    return image_ids
    
def filter_system_image(sender, body=None, image_ids=None):
    
    ctx = context.instance()
    images = {}
    
    offset = 0
    limit = const.MAX_LIMIT_PARAM
    if not body:
        body = {}
    
    body["offset"] = offset
    body["limit"] = limit
    
    image_set = {}

    for provider in const.SYSTEM_IMG_PROVIDER:
        body["provider"] = provider
    
        ret = ctx.res.resource_describe_images(sender["zone"], image_ids, const.IMG_STATUS_AVL, body)
        if not ret:
            continue

        image_set.update(ret)

    existed_image_ids = get_current_images(sender)
    
    for image_id, image in image_set.items():
        image_name = image["image_name"]
        if image_name.endswith("-baseDisk"):
            continue
        
        image_id = image["image_id"]
        if image_id in existed_image_ids:
            continue

        images[image_id] = image
    
    return images

def format_resource_image(sender, image_set):
    
    ctx = context.instance()
    res_images_ids = []
    
    for _, image in image_set.items():
        image_id = image["image_id"]
        if image_id not in res_images_ids:
            res_images_ids.append(image_id)
    
    if not res_images_ids:
        return None
    
    ret = ctx.res.resource_describe_images(sender["zone"], res_images_ids, status=const.IMG_STATUS_AVL)
    if ret is None:
        return None
    
    resource_images = ret
    update_image_status = {}
    for desktop_image_id, image in image_set.items():
        image_id = image["image_id"]
        if not image_id:
            continue
        
        if image_id not in resource_images:
            update_image_status[desktop_image_id] = {"status": const.IMG_STATUS_INVAILD}
            image["status"] = const.IMG_STATUS_INVAILD
            continue
        
        res_image = resource_images[image_id]
        if res_image["status"] != image["status"]:
            update_image_status[desktop_image_id] = {"status": res_image["status"]}
            image["status"] = res_image["status"]
        
    
    if not update_image_status:
        return None
    
    ctx.pg.batch_update(dbconst.TB_DESKTOP_IMAGE, update_image_status)
    
    return None

def format_desktop_image(image_set):
    
    for _, desktop_image in image_set.items():

        i = ["cpu", "memory", "instance_class", "inst_status"]

        for k, _ in desktop_image.items():
            if k in i:
                del desktop_image[k]

    return image_set

def check_desktop_image_ui_type(sender, desktop_image_id):
    
    ctx = context.instance()
    ret = ctx.pgm.get_desktop_images(desktop_image_id)
    if not ret:
        logger.error("desktop image [%s] no found" % desktop_image_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_image_id)
    
    desktop_image = ret[desktop_image_id]
    ui_type = desktop_image["ui_type"]
    if is_citrix_platform(ctx, sender["zone"]):
        if ui_type == const.IMG_UI_TYPE_GUI:
            logger.error("image %s ui type %s dismatch" % (desktop_image_id, ui_type))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_IMAGE_UI_TYPE_DISMATCH, desktop_image_id)
    
    return ui_type

def check_save_desktop_image_status(sender, desktop_images):
    
    ctx = context.instance()
    save_images = []
    
    if not is_citrix_platform(ctx, sender["zone"]):
        return desktop_images.keys()
    
    for desktop_image_id, desktop_image in desktop_images.items():
        
        instance_id = desktop_image["instance_id"]
        if not instance_id:
            continue
        
        instances = ctx.res.resource_describe_instances(sender["zone"], instance_id)
        if not instances:
            continue
        
        instance = instances[instance_id]
        
        inst_status = instance["status"]
        if inst_status != const.INST_STATUS_STOP:
            logger.error("citrix image %s need shutdown from  desktop internel" % (desktop_image_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_IMAGE_NEED_STOP_DESKTOP_FROM_INTERNEL, desktop_image_id)
        
        save_images.append(desktop_image_id)
    
    return save_images

def update_desktop_image_status(sender, desktop_images):
    
    ctx = context.instance()
    instance_image = {}
    image_image = {}

    delete_images = []
    clear_image = []

    for desktop_image_id, desktop_image in desktop_images.items():

        image_id = desktop_image["image_id"]
        instance_id = desktop_image["instance_id"]
        
        if desktop_image["image_type"] == const.IMG_TYPE_SYSTEM:
            clear_image.append(desktop_image_id)
            continue
        
        if image_id:
            image_image[image_id] = desktop_image_id
        if instance_id:
            instance_image[instance_id] = desktop_image_id
    

    if instance_image:

        instance_ids = instance_image.keys()
        ret = ctx.res.resource_describe_instances(sender["zone"], instance_ids)
        if ret is None:
            logger.error("get resource instance fail %s" % instance_ids)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        instances = ret

        for instance_id, desktop_image_id in instance_image.items():
            instance = instances.get(instance_id)
            if not instance or instance["status"] in [const.INST_STATUS_CEASED, const.INST_STATUS_TERM]:
                update_info = {
                                "instance_id": '',
                                "inst_status": ''
                                }
                ctx.pg.batch_update(dbconst.TB_DESKTOP_IMAGE, {desktop_image_id: update_info})

                clear_image.append(desktop_image_id)
                continue

            tran_status = instance["transition_status"]
            if tran_status:
                return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_IMAGE_IN_TRANS_STATUS, desktop_image_id)

            desktop_image = desktop_images.get(desktop_image_id)
            if not desktop_image:
                continue

            delete_images.append(desktop_image_id)
    
    if image_image:
        image_ids = image_image.keys()
        ret = ctx.res.resource_describe_images(sender["zone"], image_ids)
        if ret is None:
            logger.error("get resource instance fail %s" % instance_ids)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        images = ret
        
        for image_id, desktop_image_id in image_image.items():
            image = images.get(image_id)

            if not image:
                update_info = {
                                "image_id": ''
                               }
                ctx.pg.batch_update(dbconst.TB_DESKTOP_IMAGE, {desktop_image_id: update_info})
                clear_image.append(desktop_image_id)
                continue
            
            tran_status = image["transition_status"]
            if tran_status:
                return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_IMAGE_IN_TRANS_STATUS, desktop_image_id)    
            
            desktop_image = desktop_images.get(desktop_image_id)
            if not desktop_image:
                continue

            delete_images.append(desktop_image_id)
    
    return (delete_images, clear_image)

def check_desktop_image_in_used(desktop_images):
    
    ctx = context.instance()
    
    desktop_image_ids = desktop_images.keys()
    
    desktop_group_ids = ctx.pgm.get_desktop_group_image(desktop_image_ids)
    if desktop_group_ids:
        logger.error("resource [%s] in user the image[%s]" % (desktop_group_ids, desktop_image_ids))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_GROUP_OR_DESKTOP_USE_IMAGE, (desktop_group_ids, desktop_image_ids))
    
    image_ids = []
    for _, desktop_image in desktop_images.items():
        
        if desktop_image["image_type"] == const.IMG_TYPE_SYSTEM:
            continue
        
        image_id = desktop_image["image_id"]
        if not image_id:
            continue
        
        image_ids.append(image_id)
    
    if not image_ids:
        return None
    
    ret = ctx.pgm.get_system_image(image_ids)
    for desktop_image_id, _ in ret.items():
        if desktop_image_id not in desktop_image_ids:
            logger.error("desktop image [%s] in user the image" % (desktop_image_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_OTHER_IMAGE_USE_IMAGE, desktop_image_id)    
    
    return None

def check_desktop_image_vaild(desktop_image_ids, status=None, check_trans_status=True, is_used=False):

    ctx = context.instance()
    
    if not isinstance(desktop_image_ids, list):
        desktop_image_ids = [desktop_image_ids]
    
    desktop_images = ctx.pgm.get_desktop_images(desktop_image_ids)
    if not desktop_images:
        logger.error("desktop image [%s] no found" % desktop_image_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_image_ids)

    # check transition status
    if check_trans_status:
        ret = check_resource_transition_status(desktop_images)
        if isinstance(ret, Error):
            return ret

    if status:
        if not isinstance(status, list):
            status = [status]

        for desktop_image_id, desktop_image in desktop_images.items():

            if desktop_image['status'] not in status:
                logger.error("image [%s] status %s is not available" % (desktop_image, desktop_image['status']))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_IMAGE_STATUS_IS_NOT_AVAILABLE, (desktop_image_id))
    
    if is_used:
        ret = check_desktop_image_in_used(desktop_images)
        if isinstance(ret, Error):
            return ret

        desktops = ctx.pgm.get_desktops(desktop_image_ids)
        if desktops:
            logger.error("resource [%s] in user the image[%s]" % (desktops.keys(), desktop_image_ids))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_GROUP_OR_DESKTOP_USE_IMAGE, (desktops.keys(), desktop_image_ids))

    return desktop_images

# creat desktop image

def update_desktop_image_network(sender, desktop_image_id, network_id):
    
    ctx = context.instance()
    
    ret = Network.check_desktop_network_vaild(sender, network_id)
    if isinstance(ret, Error):
        return ret
    
    update_image = {
                    "network_id": network_id,
                   }
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_IMAGE, {desktop_image_id: update_image}):
        logger.error("Failed to update desktop image network[%s] " % (update_image))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return desktop_image_id

def check_image_os_size(desktop_image, image_size):
    
    ctx = context.instance()
    desktop_image_id = desktop_image["desktop_image_id"]
    if image_size == desktop_image["image_size"]:
        return None
    
    
    if image_size < desktop_image["image_size"]:
        logger.error("image %s size less than base image " % (desktop_image_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_IMAGE_SIZE_LESS_THAN_BASE_IMAGE)
    
    image_id = desktop_image["image_id"]
    ret = ctx.res.resource_describe_images(desktop_image["zone"], [image_id])
    if not ret:
        logger.error("no found image %s resource in cloud" % (image_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, image_id)
    
    resource_image = ret[image_id]
    if resource_image["feature"] == 4:
        logger.error("image cant support resize image size, feature is 4" % (image_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_IMAGE_SIZE_FEATURE_CANT_SUPPORT_RESIZE)
    
    return None

def register_self_image(sender, desktop_image):
    ''' create desktop image config'''

    ctx = context.instance()
    desktop_image_id = get_uuid(UUID_TYPE_DESKTOP_IMAGE, ctx.checker)
    image_config = dict(
                           desktop_image_id = desktop_image_id,
                           image_id = '',
                           base_image_id = desktop_image["image_id"],
                           image_name = desktop_image["image_name"],
                           description = desktop_image["description"],
                           cpu = desktop_image.get("cpu", 2),
                           memory = desktop_image.get("memory", 2048),
                           instance_class = desktop_image.get("instance_class", 0),
                           image_type = const.IMG_TYPE_DESKTOP,
                           platform = desktop_image["platform"],
                           os_family = desktop_image["os_family"],
                           create_time = get_current_time(),
                           status = const.IMG_STATUS_PEND,
                           session_type = desktop_image.get("session_type", ''),
                           os_version = desktop_image.get("os_version", ''),
                           image_size = desktop_image.get("image_size", 50),
                           ui_type = desktop_image.get("ui_type", "gui"),
                           owner = sender["owner"],
                           zone = sender["zone"],
                       )

    # register desktop image
    if not ctx.pg.insert(TB_DESKTOP_IMAGE, image_config):
        logger.error("insert newly created desktop group image for [%s] to db failed" % (desktop_image_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_IMAGE, desktop_image_id,zone_id=sender["zone"])
    if isinstance(ret, Error):
        return ret

    return desktop_image_id

def register_system_image(sender, desktop_image, image_id, is_default=0):
    ''' create system image config'''

    ctx = context.instance()
    desktop_image_id = get_uuid(UUID_TYPE_DESKTOP_IMAGE, ctx.checker)
    image_config = dict(
                           desktop_image_id = desktop_image_id,
                           image_id = image_id,
                           image_name = desktop_image["image_name"],
                           description = desktop_image["description"],
                           image_type = const.IMG_TYPE_SYSTEM,
                           platform = desktop_image["platform"],
                           os_family = desktop_image["os_family"],
                           session_type= desktop_image.get("session_type", ''),
                           create_time = get_current_time(),
                           status = desktop_image.get("status", const.IMG_STATUS_AVL),
                           os_version = desktop_image.get("os_version"),
                           image_size = desktop_image.get("image_size", 50),
                           ui_type = desktop_image.get("ui_type", "gui"),
                           owner = sender["owner"],
                           zone = sender["zone"],
                           is_default = is_default
                       )

    # register desktop image
    if not ctx.pg.insert(TB_DESKTOP_IMAGE, image_config):
        logger.error("insert newly created desktop image for [%s] to db failed" % (desktop_image_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_IMAGE, desktop_image_id,zone_id=sender["zone"])
    if isinstance(ret, Error):
        return ret

    return desktop_image_id

def delete_desktop_images(desktop_image_ids):
    
    ctx = context.instance()

    if not isinstance(desktop_image_ids, list):
        desktop_image_ids = [desktop_image_ids]

    for desktop_image_id in desktop_image_ids:
        ctx.pg.delete(TB_DESKTOP_IMAGE, desktop_image_id)

    ret = Permission.clear_user_resource_scope(desktop_image_ids)
    if not ret:
        logger.error("clear desktop group resource scope fail %s" % desktop_image_ids)

    return None

def refresh_desktop_image_name(desktop_image_id, image_name):
    
    ctx = context.instance()
    
    conditions = {"desktop_image_id": desktop_image_id}
    update_info = {"image_name": image_name}
    # update desktop group
    ctx.pg.base_update(dbconst.TB_DESKTOP_GROUP, conditions, update_info)
    
    # update desktop
    ctx.pg.base_update(dbconst.TB_DESKTOP, conditions, update_info)

    return None

def modify_desktop_image_attributes(sender, desktop_image, columns):
    
    ctx = context.instance()
    desktop_image_id = desktop_image["desktop_image_id"]
    image_name = columns.get("image_name")
    description = columns.get("description")
    
    image_update = {}
    if image_name and desktop_image["image_name"] != image_name:
        image_update["image_name"] = image_name
    if description is not None and desktop_image["description"] != description:
        image_update["description"] = description

    if not image_update:
        return None
    
    if not ctx.pg.update(TB_DESKTOP_IMAGE, desktop_image_id, image_update):
        logger.error("modify dekstop image attributes failed for [%s]" % desktop_image_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_RESOURCE_ATTRIBUTES_FAILED, desktop_image_id)
        
    image_id = desktop_image["image_id"]
    if image_update and image_id:
        ret = ctx.res.resource_modify_image_attributes(sender["zone"], image_id, image_update)
        if not ret:
            logger.error("modify dekstop image attributes failed for [%s]" % image_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_MODIFY_RESOURCE_ATTRIBUTES_FAILED, image_id)
        
        ret = refresh_desktop_image_name(desktop_image_id, columns["image_name"])
        if isinstance(ret, Error):
            return ret
    return None

def check_default_images(sender):

    zone_id = sender["zone"]
    ctx = context.instance()
    
    ret = init_default_image(zone_id)
    if isinstance(ret, Error):
        return ret

    if not ret:
        return None
    
    default_images = ret
    default_image_ids = {}
    for desktop_image_id, image in default_images.items():
        image_id = image["image_id"]
        default_image_ids[desktop_image_id] = image_id
    
    update_images = {}
    ret = ctx.res.resource_describe_images(zone_id, default_image_ids.values())

    if not ret:
        ret = {}
    
    for desktop_image_id, image_id in default_image_ids.items():
        sys_img = ret.get(image_id)
        if not sys_img:
            sys_img = {}
        status = sys_img.get("status", const.IMG_STATUS_INVAILD)
        if status == const.IMG_STATUS_AVL:
            update_images[desktop_image_id] = {"status": const.IMG_STATUS_AVL}
        else:
            update_images[desktop_image_id] = {"status": const.IMG_STATUS_INVAILD}
    
    if update_images:
        ctx.pg.batch_update(dbconst.TB_DESKTOP_IMAGE, update_images)

    return None

def filter_default_images(sender, image_ids):
    
    ctx = context.instance()
    zone_id = sender["zone"]
    ret = ctx.pgm.get_default_image(zone_id, image_ids)
    if ret:
        logger.error("default image cant be delete or modify %s" % image_ids)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DEFAULT_IMAGE_CANT_BE_DELET_OR_MODIFY, ret.keys())
    return None

def init_default_image(zone_id):

    ctx = context.instance()
    
    zone = ctx.pgm.get_zone(zone_id, extras=[])
    if not zone:
        return None
    
    if zone["status"] != const.ZONE_STATUS_ACTIVE:
        return None

    # refresh_zone_builder
    ctx.zone_builder.load_zone(zone_id)
    ctx.zone_builder.refresh_zone_builder()
    zone_sync_to_other_server(zone_id)

    ui_type = const.IMG_UI_TYPE_GUI
    if is_citrix_platform(ctx, zone_id):
        ui_type = const.IMG_UI_TYPE_TUI

    # get image model
    ret = ctx.pgm.get_desktop_images(image_type=const.IMG_TYPE_MODEL, ui_type=ui_type)
    if not ret:
        return None
    model_image_set = ret
    
    # model_images
    model_image_ids = []
    for _, model_image in model_image_set.items():
        image_id = model_image["image_id"]
        model_image_ids.append(image_id)

    ret = ctx.res.resource_describe_images(zone_id, model_image_ids)
    if not ret:
        return None
    
    res_model_images = ret

    # get existed default image
    default_images = []
    ret = ctx.pgm.get_default_image(zone_id)
    if ret:
        for _, image in ret.items():
            image_id = image["image_id"]
            default_images.append(image_id)
    
    # create new default image
    sender = {"zone": zone_id, "owner": "system"}   
    for _, model_image in model_image_set.items():

        image_id = model_image["image_id"]
        if image_id in default_images:
            continue

        status = const.IMG_STATUS_AVL
        res_image = res_model_images.get(image_id, {})
        if not res_image:
            continue

        desktop_image = {}
        desktop_image["image_name"] = model_image["image_name"]
        desktop_image["description"] = model_image["description"]
        desktop_image["platform"] = model_image["platform"]
        desktop_image["os_family"] = model_image["os_family"]
        desktop_image["session_type"] = model_image["session_type"]
        desktop_image["os_version"] = model_image["os_version"]
        desktop_image["image_size"] = res_image.get("size", 100)
        desktop_image["ui_type"] = ui_type
        desktop_image["status"] = status
        # create desktop image id
        ret = register_system_image(sender, desktop_image, image_id, is_default=1)
        if isinstance(ret, Error):
            return ret

    ret = ctx.pgm.get_default_image(zone_id)
    if not ret:
        ret = {}

    return ret
