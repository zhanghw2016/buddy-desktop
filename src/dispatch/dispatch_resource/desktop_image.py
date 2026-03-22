
import context
import constants as const
from log.logger import logger
import db.constants as dbconst
from utils.misc import get_current_time
import dispatch_resource.desktop_nic as Nic

def check_desktop_resource_image(sender, desktops):

    ctx = context.instance()
    
    desktop_ids = desktops.keys()
    ret = ctx.pgm.get_desktop_resource_image(desktop_ids)
    if not ret:
        logger.error("desktop no get image %s" % desktop_ids)
        return -1
    desktop_image = ret

    image_ids = desktop_image.values()
    ret = ctx.res.resource_describe_images(sender["zone"], image_ids)
    if not ret:
        logger.error("resource image no found %s" % image_ids) 
        return -1
    
    images = ret
    for desktop_id, image_id in desktop_image.items():
        image = images.get(image_id)
        if not image:
            logger.error("resource image no found %s" % image_id)
            return -1

        if image["status"] != const.IMG_STATUS_AVL:
            logger.error("image %s status dismatch %s" % (image_id, image["status"]))
            return -1

        desktop = desktops[desktop_id]
        desktop["image_id"] = image_id
        
    return 0

# common

def update_desktop_image(desktop_image_id, update_info):

    ctx = context.instance()

    update_info["status_time"] = get_current_time()

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_IMAGE, {desktop_image_id: update_info}):
        logger.error("update desktop image fail %s" % update_info)
        return -1

    return 0
    
# create desktop image
def check_create_desktop_image(sender, desktop_image_ids):

    ctx = context.instance()

    desktop_images = ctx.pgm.get_desktop_images(desktop_image_ids)
    if not desktop_images:
        logger.error("check desktop image[%s] fail." % desktop_image_ids)
        return -1

    base_image_ids = []
    for desktop_image_id in desktop_image_ids:
        desktop_image = desktop_images.get(desktop_image_id)
        if not desktop_image:
            logger.error("check desktop image[%s] no found resource." % desktop_image_id)
            return -1

        base_image_id = desktop_image["base_image_id"]
        if not base_image_id:
            logger.error("check desktop image[%s] base iamge no found ." % desktop_image_id)
            return -1

        cpu = desktop_image["cpu"]
        memory = desktop_image["memory"]
        if not cpu or not memory:
            logger.error("check desktop image[%s] no cpu/memory config ." % desktop_image_id)
            return -1

        base_image_ids.append(base_image_id)

    ret = ctx.res.resource_describe_images(sender["zone"], base_image_ids)
    if not ret:
        logger.error("Describe Image[%s] fail." % base_image_ids) 
        return -1

    images = ret
    for image_id in base_image_ids:
        image = images.get(image_id)
        if not image:
            logger.error("check desktop image[%s] no found image resource." % desktop_image_id)
            return -1

        status = image["status"]
        if status != const.IMG_STATUS_AVL:
            logger.error("check desktop image[%s] image status %s no match." % (desktop_image_id, status))
            return -1

    return desktop_images

def create_desktop_image(sender, desktop_image):

    ctx = context.instance()
    zone = sender["zone"]
    desktop_image_id = desktop_image["desktop_image_id"]

    
    default_passwd = ctx.zone_checker.get_resource_limit(zone, "default_passwd")
    if not default_passwd:
        default_passwd = const.LOGIN_PASSWD

    image_config = {
                    "image_id": desktop_image["base_image_id"],
                    "cpu": desktop_image["cpu"],
                    "memory": desktop_image["memory"],
                    "instance_class": desktop_image["instance_class"],
                    "instance_name": desktop_image["image_name"],
                    "login_mode": const.LOGIN_MODE_PASSWD,
                    "login_passwd": default_passwd
                    }
    if desktop_image.get("os_version").lower() == const.OS_VERSION_LINUX:
        zone_connection = ctx.pgm.get_zone_connection(zone)
        keypair = None
        if zone_connection:
            keypair = zone_connection.get("keypair")
        if keypair:
            del image_config["login_passwd"]
            image_config["login_mode"] = const.LOGIN_MODE_KEYPAIR
            image_config["login_keypair"] = keypair

    network_id = desktop_image.get("network_id")
    if network_id:
        image_config["vxnets"] = [network_id]
    
    if desktop_image["image_size"]:
        image_config["os_disk_size"] = desktop_image["image_size"]
    
    if desktop_image["ui_type"] == const.IMG_UI_TYPE_TUI:
        image_config["graphics_protocol"] = "vnc"
    elif desktop_image["ui_type"] == const.IMG_UI_TYPE_GUI:
        image_config["graphics_protocol"] = "spice"
    else:
        logger.error("desktop_image['ui_type'] = %s, is invalid" % desktop_image["ui_type"])
        return -1

    # run image instance
    ret = ctx.res.resource_create_instance(sender["zone"], image_config, platform=const.PLATFORM_TYPE_QINGCLOUD)
    if not ret:
        logger.error("task create image, image run instance fail[%s]" % desktop_image_id)
        return -1
    instance_id = ret
    
    update_info = {
                    "status": const.IMG_STATUS_EDITED,
                    "instance_id": instance_id,
                    "inst_status": const.INST_STATUS_RUN
                  }

    ret = update_desktop_image(desktop_image_id, update_info)
    if ret < 0:
        logger.error("update desktop image fail %s" % desktop_image_id)
        return -1

    return 0

# save desktop image
def check_save_desktop_image(sender, desktop_image_ids):

    ctx = context.instance()

    desktop_images = ctx.pgm.get_desktop_images(desktop_image_ids)
    if not desktop_images:
        logger.error("check desktop image[%s] fail." % desktop_image_ids)
        return -1

    instance_image = {}
    for desktop_image_id in desktop_image_ids:
        desktop_image = desktop_images.get(desktop_image_id)
        if not desktop_image:
            logger.error("no found desktop image %s" % desktop_image_id)
            return -1

        image_id = desktop_image["image_id"]
        if image_id:
            logger.error("no found desktop image %s" % image_id)
            return -1

        instance_id = desktop_image["instance_id"]
        if not instance_id:
            logger.error("no found image instance %s" % instance_id)
            return -1

        instance_image[instance_id] = desktop_image_id
    
    instance_ids = instance_image.keys()
    ret = ctx.res.resource_describe_instances(sender["zone"], instance_ids)
    if not ret:
        logger.error("Describe Instance[%s] fail." % instance_ids) 
        return -1
    instances = ret

    for instance_id, desktop_image_id in instance_image.items():
        instance = instances.get(instance_id)
        if not instance:
            logger.error("no found instance %s" % instance_id)
            return -1

        desktop_image = desktop_images.get(desktop_image_id)
        if not desktop_image:
            logger.error("no found desktop image %s" % desktop_image_id)
            return -1

        status = instance["status"]
        if status not in [const.INST_STATUS_RUN, const.INST_STATUS_STOP]:
            logger.error("desktop image status no match %s" % status)
            return -1
        
        if desktop_image["inst_status"] == instance["status"]:
            continue

        update_info = {
                      "inst_status": instance["status"]
                      }

        ret = update_desktop_image(desktop_image_id, update_info)
        if ret < 0:
            logger.error("update desktop image status no match %s" % desktop_image_id)
            return -1

    return desktop_images

def save_desktop_image(sender, desktop_image):
    
    ctx = context.instance()
    
    desktop_image_id = desktop_image["desktop_image_id"]
    image_name = desktop_image["image_name"]
    status = desktop_image["status"]
    if status != const.IMG_STATUS_EDITED:
        logger.error("save desktop image status no match %s" % status)
        return -1
    
    instance_id = desktop_image["instance_id"]
    inst_status = desktop_image["inst_status"]
    
    if inst_status == const.INST_STATUS_RUN:
        ret = ctx.res.resource_stop_instances(sender["zone"], desktop_image, const.PLATFORM_TYPE_QINGCLOUD)
        if not ret:
            logger.error("stop image instance fail %s" % instance_id)
            return -1

        update_info = {
                        "status": const.IMG_STATUS_EDITED,
                        "instance_id": instance_id,
                        "inst_status": const.INST_STATUS_STOP
                        }
    
        ret = update_desktop_image(desktop_image_id, update_info)
        if ret < 0:
            logger.error("update desktop image fail %s" % update_info)
            return -1

    ret = ctx.res.resource_capture_instance(sender["zone"], instance_id, image_name)
    if not ret:
        logger.error("capture instance fail %s" % instance_id)
        return -1
    image_id = ret

    update_info = {
                   "image_id": image_id,
                   "status": const.IMG_STATUS_AVL,
                  }
    ret = update_desktop_image(desktop_image_id, update_info)
    if ret < 0:
        logger.error("update desktop image fail %s" % update_info)
        return -1

    return image_id

def delete_desktop_image(sender, desktop_image):
    
    ctx = context.instance()
    desktop_image_id = desktop_image["desktop_image_id"]

    instance_id = desktop_image["instance_id"]
    image_id = desktop_image["image_id"]
    if instance_id:

        ret = ctx.res.resource_terminate_instances(sender["zone"], desktop_image, const.PLATFORM_TYPE_QINGCLOUD)
        if ret < 0:
            logger.error("delete dekstop image instance fail %s" % instance_id)
            return -1
        
        sender = {"zone": desktop_image["zone"]}
        Nic.clear_resource_nic(sender, desktop_image_id)
        update_info = {
                        "instance_id": '',
                        "inst_status": ''
                        }
        ret = update_desktop_image(desktop_image_id, update_info)
        if ret < 0:
            logger.error("update desktop image fail %s" % desktop_image_id)
            return -1

    if image_id:
        
        ret = ctx.res.resource_describe_images(desktop_image["zone"], image_id)
        if ret:
            ret = ctx.res.resource_delete_images(desktop_image["zone"], image_id)
            if ret < 0:
                logger.error("desktop image fail %s" % desktop_image_id)
                return -1

        update_info = {
                        "image_id": '',
                        }
        ret = update_desktop_image(desktop_image_id, update_info)
        if ret < 0:
            logger.error("update desktop image fail %s" % desktop_image_id)
            return -1

    return 0

def clear_desktop_image_info(desktop_image_id):
    
    ctx = context.instance()
    ctx.pg.delete(dbconst.TB_DESKTOP_IMAGE, desktop_image_id)
    condition = {'resource_id': desktop_image_id}
    ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, condition)
    
    return 0
