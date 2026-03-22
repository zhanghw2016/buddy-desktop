import context

from common import (
    return_error,
    return_items,
    return_success,
)
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.citrix.citrix as Citrix
import resource_control.citrix.delivery_group as DeliveryGroup
from log.logger import logger
import resource_control.desktop.disk as Disk
import constants as const

def handle_describe_computer_catalogs(req):

    ctx = context.instance()
    sender = req["sender"]
    
    catalog_names = req.get("catalog_names")
    catalogs = ctx.res.resource_describe_computer_catalogs(sender["zone"], catalog_names, verbose=1)
    if not catalogs:
        catalogs = {}

    existed_catalog_names = []
    ret = ctx.pgm.get_desktop_groups(zone_id=sender["zone"])
    if ret:
        for _, desktop_group in ret.items():
            desktop_group_name = desktop_group["desktop_group_name"]
            if desktop_group_name in existed_catalog_names:
                continue
            existed_catalog_names.append(desktop_group_name)
    
    ret_catalogs = {}
    for catalog_name, catalog in catalogs.items():
        if catalog_name in existed_catalog_names:
            continue
        
        name = catalog.get("name")
        if name:
            del catalog["name"]
            catalog["catalog_name"] = name
        
        ret_catalogs[catalog_name] = catalog
    
    rep = {'total_count':len(ret_catalogs)} 
    return return_items(req, ret_catalogs, "computer_catalogs", **rep)

def handle_describe_computers(req):

    ctx = context.instance()
    sender = req["sender"]
    
    computer_names = req.get("computers")
    delivery_group_id = req.get("delivery_group")
    desktop_group_id = req.get("desktop_group")
    offset = req.get("offset")
    limit = req.get("limit")
    ret_computers = {}
    desktop_group_name = None
    delivery_group_name = None
    
    if desktop_group_id:
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
        if not desktop_group:
            logger.error("load computer no found desktop group %s" % desktop_group_id)
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

        desktop_group_name = desktop_group["desktop_group_name"]
        computers = ctx.res.resource_describe_computers(sender["zone"], desktop_group_name, computer_names, offset=offset, limit=limit)
        if not computers:
            rep = {'total_count':0} 
            return return_items(req, None, "computers", **rep)
    
        computer_names = computers.keys()
        desktop_names = ctx.pgm.get_group_desktop_name(desktop_group_id)
        if not desktop_names:
            desktop_names = {}
        
        for computer_name in computer_names:
            if computer_name in desktop_names:
                continue
            
            ret_computers[computer_name] = computers[computer_name]
        
    elif delivery_group_id:
        delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
        if not delivery_groups:
            logger.error("load computer no found delivery group %s" % delivery_group_id)
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
        
        delivery_group = delivery_groups[delivery_group_id]
        delivery_group_name = delivery_group["delivery_group_name"]

        computers = ctx.res.resource_describe_computers(sender["zone"], None, computer_names, delivery_group_name, offset=offset, limit=limit)
        if not computers:
            rep = {'total_count':0} 
            return return_items(req, None, "computers", **rep)
        
        existed_desktop_names = ctx.pgm.get_desktop_hostname(False)
        if not existed_desktop_names:
            existed_desktop_names = []
        
        computer_names = computers.keys()
        desktop_names = ctx.pgm.get_group_desktop_name(None,delivery_group_id)
        if not desktop_names:
            desktop_names = {}
        for computer_name in computer_names:
            if computer_name in desktop_names:
                continue
            if computer_name not in existed_desktop_names:
                continue
            
            ret_computers[computer_name] = computers[computer_name]

    computers = Citrix.format_computers(ret_computers)
    
    rep = {'total_count':len(computers)} 
    return return_items(req, computers, "computer", **rep)

def handle_load_computer_catalogs(req):
    
    ctx = context.instance()
    sender = req["sender"]
    catalog_names = req["catalog_names"]
    
    ret = ctx.res.resource_describe_computer_catalogs(sender["zone"], catalog_names, verbose=1)
    if not ret:
        logger.error("resource describe computer catalog fail %s" % ret)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    catalog_set = ret
    
    ret = Citrix.build_load_computer_catalog(sender, catalog_set, req)
    if isinstance(ret, Error):
        return return_error(req,ret)
    bodys = ret

    desktop_group_ids = []
    for body in bodys:
        
        body["is_load"] = 1

        if body["provision_type"] == const.PROVISION_TYPE_MCS:
            ret = ctx.res.resource_create_desktop_group(sender["zone"], body)
            if not ret or ret["ret_code"] != 0:
                logger.error("load computer catalog, create desktop group fail %s" % ret)
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
            desktop_group_ids.append(ret["desktop_group"])
        else:
            ret = ctx.res.resource_create_app_desktop_group(sender["zone"], body)
            if not ret or ret["ret_code"] != 0:
                logger.error("load computer catalog, create desktop group fail %s" % ret)
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
            desktop_group_ids.append(ret["desktop_group"])
        
    ret = {'desktop_groups': desktop_group_ids}
    return return_success(req, None, **ret)

def handle_load_computers(req):
    
    ctx = context.instance()
    sender = req["sender"]
    computers = req.get("computers")
    desktop_group_id = req.get("desktop_group")
    delivery_group_id = req.get("delivery_group")
    
    if not desktop_group_id and not delivery_group_id:
        logger.error("load computers param is null %s")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                       ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))
    
    desktop_ids = []
    if desktop_group_id:
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
        if not desktop_group:
            logger.error("load computer no found desktop group %s" % desktop_group_id)
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

        ret = Citrix.load_desktop_group_computers(sender, desktop_group, computers)
        if isinstance(ret, Error):
            return return_error(req,ret)
        
        desktop_ids = ret

    if delivery_group_id:
        delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
        if not delivery_groups:
            logger.error("load computer no found delivery group %s" % delivery_group_id)
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
        
        delivery_group = delivery_groups[delivery_group_id]
        ret = Citrix.load_delivery_group_computers(sender, delivery_group, computers)
        if isinstance(ret, Error):
            return return_error(req,ret)
        
        desktop_ids = ret
        
    ret = {'desktops': desktop_ids}
    return return_success(req, None, **ret)

def handle_refresh_citrix_desktops(req):
    
    ctx = context.instance()
    sender = req["sender"]
    desktop_ids = req.get("desktops")
    desktop_group_id = req.get("desktop_group")
    delivery_group_id = req.get("delivery_group")

    desktop_group_name = None
    if desktop_group_id:
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
        if not desktop_group:
            logger.error("refresh desktop no found desktop group %s" % desktop_group_id)
            return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND, 
                                           ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_group_id))

        desktop_group_name = desktop_group["desktop_group_name"]
    
    delivery_group_name = None
    delivery_group = None
    if delivery_group_id:
        delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
        if not delivery_groups or delivery_group_id not in delivery_groups:
            logger.error("refresh desktop no found delivery group %s" % delivery_group_id)
            return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND, 
                                           ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id))
        delivery_group = delivery_groups[delivery_group_id]
        delivery_group_name = delivery_groups[delivery_group_id]["delivery_group_name"]
    
    hostnames = None
    if desktop_ids:
        desktop_names = ctx.pgm.get_desktop_name(desktop_ids)
        if desktop_names:
            logger.error("refresh desktop no found desktop %s" % desktop_ids)
            return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND, 
                                           ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_ids))
        
        hostnames = desktop_names.values()
    
    if hostnames:
        desktop_group_name = None
        delivery_group_name = None

    if desktop_group_name:
        delivery_group_name = None
    
    ret = Citrix.refresh_citrix_desktops(sender, hostnames, desktop_group_name, delivery_group_name)
    if isinstance(ret, Error):
        return return_error(req,ret)
    
    desktop_ids = ret
    if not desktop_ids:
        desktop_ids = []
    job_disks = None

    if desktop_group_name:
        ret = Citrix.refresh_citrix_disks(sender, desktop_group_name)
        if isinstance(ret, Error):
            return return_error(req,ret)
        
        if ret:
            for _id in ret:
                if _id not in desktop_ids:
                    desktop_ids.append(_id)
        
        ret = Citrix.create_citrix_disks(desktop_group_id)
        if isinstance(ret, Error):
            return return_error(req,ret)
        if ret:
            (job_disks, update_desktops) = ret
            if update_desktops:
                for _id in update_desktops:
                    if _id not in desktop_ids:
                        desktop_ids.append(_id)
                        
        ret = Citrix.refresh_citrix_ivshmem(sender, desktop_group_name)
        if isinstance(ret, Error):
            return return_error(req,ret)
    
    if delivery_group_id:
        delivery_type = delivery_group.get("delivery_type")
        if delivery_type == const.CITRIX_DELIVERY_TYPE_DESKTOP_APP:
            ret = DeliveryGroup.refresh_broker_app_in_delivery_group(sender, delivery_group)
            if isinstance(ret, Error):
                return return_error(req,ret)
            
            ret = DeliveryGroup.refresh_broker_app_group_in_delivery_group(sender, delivery_group)
            if isinstance(ret, Error):
                return return_error(req,ret)
    
    rep = {'desktops': desktop_ids}
    job_uuid = None
    if job_disks:
        ret = Disk.send_disk_job(sender, job_disks, const.JOB_ACTION_ATTACH_DISKS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret
        
        rep["disks"] = job_disks
    
    return return_success(req, None, job_uuid, **rep)

