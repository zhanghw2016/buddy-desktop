import context
from log.logger import logger
import constants as const
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from utils.id_tool import(
    get_uuid,
    UUID_TYPE_BROKER_APP,
    UUID_TYPE_BROKER_APP_GROUP
)
from utils.misc import get_current_time
import db.constants as dbconst
import resource_control.citrix.citrix as Citrix
from common import unicode_to_string

def format_broker_apps(broker_app_set):
    
    ctx = context.instance()
    
    for broker_app_id, broker_app in broker_app_set.items():
        
        ret = ctx.pgm.get_broker_app_in_app_group(broker_app_id)
        if not ret:
            ret = []
        
        broker_app["broker_app_groups"] = ret
        
        ret = ctx.pgm.get_broker_app_in_delivery_group(broker_app_id)
        if not ret:
            ret = []
        
        broker_app["delivery_groups"] = ret
    
    return broker_app_set

def format_broker_app_groups(broker_app_group_set):
    
    ctx = context.instance()
    
    for broker_app_group_id, broker_app_group in broker_app_group_set.items():
        
        ret = ctx.pgm.get_broker_app_group_app(broker_app_group_id)
        if not ret:
            ret = {}
            
        broker_app_ids = ret.keys()
        if broker_app_ids:
            ret = ctx.pgm.get_broker_apps(broker_app_ids)
            if not ret:
                ret = {}
            broker_app_group["broker_apps"] = ret.values()
        
        ret = ctx.pgm.get_broker_app_group_delivery_group(broker_app_group_id)
        if not ret:
            ret = {}
        broker_app_group["delivery_groups"] = ret.values()
        
    return broker_app_group_set

def check_app_machine(zone, machine_names):
     
    ctx = context.instance()
    ret = ctx.pgm.get_desktop_by_hostnames(machine_names, zone)
    if not ret:
        logger.error("desktop group name %s no found" % (machine_names))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_NO_FOUND_DESKTOP_GROUP, (machine_names))
    
    desktops = ret
    instance_ids = []
    for _, desktop in desktops.items():
        instance_id = desktop["instance_id"]
        instance_ids.append(instance_id)

    return

def search_app_computes(zone, search_word):
    
    ctx = context.instance()
    
    ret = ctx.res.resource_search_instances(zone, search_word, status=[const.INST_STATUS_RUN, const.INST_STATUS_STOP])
    if not ret:
        return None

    instances = ret
    instance_ids = instances.keys()
    instance_desktop = ctx.pgm.get_instance_desktop(instance_ids)
    if not instance_desktop:
        instance_desktop = {}

    filter_instances = {}
    
    for instance_id in instance_ids:
        if instance_id in instance_desktop:
            continue
        filter_instances[instance_id] = instances[instance_id]
    
    if not filter_instances:
        return None
    
    auth_zone = ctx.pgm.get_auth_zone(zone)
    if not auth_zone:
        return None
    
    auth_service_id = auth_zone["auth_service_id"]
    auth_service = ctx.pgm.get_auth_service(auth_service_id)
    if not auth_service:
        return None

    domain_dn = ctx.auth.get_domain_dn(auth_service["domain"])
    if not domain_dn:
        return None
    
    app_machines = {}
    for instance_id, instance in filter_instances.items():
        
        hostname = instance["instance_name"]
        if not hostname:
            hostname = instance["hostname"]
        
        if not hostname:
            continue
        # instance add domain
        ret = ctx.auth.get_auth_computes(auth_service_id, ou_dn=domain_dn, search_name=hostname)
        if not ret:
            continue
        
        if hostname.lower() not in ret:
            continue
        
        machine = ret[hostname.lower()]
        machine["image_id"] = instance["image"]["image_id"]
        machine["instance_id"] = instance_id

        machine["instance_name"] = instance["instance_name"]
        machine["image_name"] = instance["image"]["image_name"]
        machine["hostname"] = instance["instance_name"]
        machine["status"] = instance["status"]
        machine["transition_status"] = instance["transition_status"]

        app_machines[instance_id] = machine

    return app_machines

def add_machine_to_desktop_group(sender, machine_info, desktop_group):
    
    ctx = context.instance()
    zone = sender["zone"]
    machine_sid = machine_info["objectSid"]
    desktop_group_name = desktop_group["desktop_group_name"]
    machine_name = machine_info["hostname"]
    host_unit = desktop_group["managed_resource"]
    instance_id = machine_info["instance_id"]
    if not host_unit:
        logger.error("no found group %s managed resource" % (desktop_group_name))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_GROUP_NO_FOUND_MANAGED_RESOURCE, (desktop_group_name))
    
    ret = ctx.res.resource_describe_computer_catalogs(zone, desktop_group_name)
    if not ret:
        logger.error("describe compute catalog  %s fail" % (desktop_group_name))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_NO_FOUND_DESKTOP_GROUP, (desktop_group_name))
    
    ret = ctx.res.resource_add_computer(zone, desktop_group_name, machine_name, instance_id, machine_sid, host_unit)
    if not ret:
        logger.error("add compute to desktop group %s fail" % (desktop_group_name))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_ADD_COMPUTE_TO_DESKTOP_GROUP_FAILED, (machine_name,desktop_group_name))
    
    ret = Citrix.load_desktop_group_computers(sender, desktop_group, machine_name)
    if isinstance(ret, Error):
        return ret
    
    return None

def get_machine_app_startmemu(zone, machine_name):
    
    ctx = context.instance()

    ret = ctx.res.resource_describe_app_start_memu(zone, machine_name)
    if not ret:
        return None
    
    return ret

def check_broker_app_group_name(sender, broker_app_group_name):
    
    ctx = context.instance()
    broker_app_groups = ctx.pgm.get_app_group_by_name(sender["zone"], broker_app_group_name)
    if broker_app_groups:
        logger.error("app group has the same name %s" % (broker_app_group_name))
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_APP_GROUP_NAME_EXISTED, broker_app_group_name)

    return None

def check_app_delivery_group(sender, delivery_group_id, desktop_id=None):
    
    ctx = context.instance()
    delivery_group =  ctx.pgm.get_delivery_group(delivery_group_id)
    if not delivery_group:
        logger.error("no found delivery group resource %s" % (delivery_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)
    
    desktop = None
    if desktop_id:
        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("no found delivery group resource %s" % (desktop_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)

    delivery_group_name = delivery_group["delivery_group_name"]
    ret = ctx.res.resource_describe_delivery_groups(sender["zone"], delivery_group_name)
    if not ret:
        logger.error("no found delivery group resource %s" % (delivery_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)   

    return (delivery_group, desktop)

def check_app_compute(sender, desktop_id):
    
    ctx = context.instance()
    ret = ctx.pgm.get_desktop(desktop_id)
    if not ret:
        logger.error("no found desktop resource %s" % (desktop_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_id)   

    return ret

def check_broker_app_data(app_datas,zone=None):
    
    ctx = context.instance()
    
    if not isinstance(app_datas, list):
        app_datas = [app_datas]
    
    check_keys = ["cmd_exe_path", "cmd_argument", "working_dir", "display_name", "shortcut_path"]
    for app_data in app_datas:
        for key in check_keys:
            if key not in app_data:
                logger.error("app data %s lack key %s" % (app_data, key))
                return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                             ErrorMsg.ERR_MSG_CREATE_APP_PARAM_ERROR)
                
        ret = ctx.pgm.get_table_ignore_case(dbconst.TB_BROKER_APP, "display_name", app_data["display_name"],zone)
        if ret:
            logger.error("app data %s lack key %s" % (app_data, key))
            return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                             ErrorMsg.ERR_MSG_APP_NAME_EXISTED, app_data["display_name"])
        
    app_datas = unicode_to_string(app_datas)
    return app_datas

def register_broker_app(zone, broker_app):

    ctx = context.instance()
   
    broker_app_id = get_uuid(UUID_TYPE_BROKER_APP, ctx.checker)
    broker_app_info = dict(
                              broker_app_id = broker_app_id,
                              display_name = broker_app["app_name"],
                              cmd_argument = broker_app["cmd_argument"],
                              cmd_exe_path = broker_app["cmd_exe_path"],
                              working_dir = broker_app["working_dir"],
                              normal_display_name = broker_app["normal_display_name"],
                              admin_display_name = broker_app["admin_display_name"],
                              floder_name = broker_app["folder_name"],
                              broker_app_uid = broker_app["app_uid"],
                              create_time = get_current_time(),
                              status_time = get_current_time(),
                              zone = zone,
                              )

    # register desktop group
    if not ctx.pg.insert(dbconst.TB_BROKER_APP, broker_app_info):
        logger.error("insert newly created broker app for [%s] to db failed" % (broker_app_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return broker_app_id

def check_broker_app_info(resource_broker_app, broker_app):
    
    check_keys = ["cmd_argument", "cmd_exe_path", "working_dir", "shortcut_path", "admin_display_name", "normal_display_name", "description", "app_name"]
    
    update_info = {}
    for key in check_keys:
        if key not in resource_broker_app or key not in broker_app:
            continue

        if resource_broker_app[key] != broker_app[key]:
            update_info[key] = resource_broker_app[key]
    
    return update_info

def update_broker_app_group(sender, resource_broker_app, broker_app):
    
    ctx = context.instance()
    broker_app_id = broker_app["broker_app_id"]
    all_desktopgroup_uids = resource_broker_app.get("all_desktopgroup_uids", [])
    all_appgroup_uids = resource_broker_app.get("all_appgroup_uids", [])
    
    # check delivery group
    delivery_group_uids = {}
    delivery_group_ids = ctx.pgm.get_broker_app_delivery_group(broker_app_id)
    if delivery_group_ids:
        delivery_group_uids = ctx.pgm.get_delivery_group_uid(delivery_group_ids)
        if not delivery_group_uids:
            delivery_group_uids = {}
    
    new_delviery_groups = []
    del_delivery_groups = []
    for delivery_group_id, uid in delivery_group_uids.items():
        if uid not in all_desktopgroup_uids:
            del_delivery_groups.append(delivery_group_id)
    
    for uid in all_desktopgroup_uids:
        if uid not in delivery_group_uids.values():
            new_delviery_groups.append(uid)
    
    if new_delviery_groups:
        new_delivery_groups = ctx.pgm.get_delivery_group_by_uid(new_delviery_groups)
        if new_delivery_groups:
            for uid, delivery_group in new_delivery_groups.items():
                ret = attach_broker_app_to_delivery_group(sender, delivery_group, broker_app_id)
                if isinstance(ret, Error):
                    return ret
                
    if del_delivery_groups:
        ret = detach_broker_app_from_delivery_group(sender, broker_app, del_delivery_groups)
        if isinstance(ret, Error):
            return ret
    
    # check app group
    app_group_uids = {}
    app_group_ids = ctx.pgm.get_broker_app_app_group(broker_app_id)
    if app_group_ids:
        app_group_uids = ctx.pgm.get_broker_app_group_uid(app_group_ids)
        if not app_group_uids:
            app_group_uids = {}
    
    new_broker_app_groups = []
    del_broker_app_groups = []
    
    for app_group_id, uid in app_group_uids.items():
        if uid not in all_appgroup_uids:
            del_broker_app_groups.append(app_group_id)
    
    for uid in all_appgroup_uids:
        if uid not in app_group_uids.values():
            new_broker_app_groups.append(uid)
    
    if new_broker_app_groups:
        new_broker_app_groups = ctx.pgm.get_broker_app_group_by_uid(new_broker_app_groups)
        if new_broker_app_groups:
            for _, broker_app_group in new_broker_app_groups.items():
                ret = attach_broker_app_to_app_group(sender, broker_app_group, broker_app)
                if isinstance(ret, Error):
                    return ret
    
    if del_broker_app_groups:
        
        ret = ctx.pgm.get_app_group_names(del_broker_app_groups)
        if ret:
            app_group_names = ret.values()
            ret = detach_broker_app_from_app_group(sender, broker_app, app_group_names)
            if isinstance(ret, Error):
                return ret
    
    return None


def refresh_broker_apps(sender, broker_app_ids=None):
    
    ctx = context.instance()
    
    broker_apps = ctx.pgm.get_broker_apps(broker_app_ids, zone_id=sender["zone"], index_uid=True)
    if not broker_apps:
        broker_apps = {}
    
    broker_app_names = None
    if broker_app_ids:
        broker_app_names = ctx.pgm.get_broker_app_name(broker_app_ids)
        if not broker_app_names:
            broker_app_names = None
        
        broker_app_names = broker_app_names.values()

    resource_broker_apps = ctx.res.resource_describe_broker_apps(sender["zone"], app_names = broker_app_names, index_uid=True)
    if resource_broker_apps is None:
        resource_broker_apps = {}

    new_broker_apps = []
    del_broker_apps = []
    
    for broker_app_uid, broker_app in broker_apps.items():
        broker_app_id = broker_app["broker_app_id"]
        if broker_app_uid not in resource_broker_apps:
            del_broker_apps.append(broker_app)
            continue
        
        resource_broker_app = resource_broker_apps[broker_app_uid]
        update_info = check_broker_app_info(resource_broker_app, broker_app)
        if update_info:
            conditions = {"broker_app_id": broker_app_id}
            if not ctx.pg.base_update(dbconst.TB_BROKER_APP, conditions, update_info):
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        
        ret = update_broker_app_group(sender, resource_broker_app, broker_app)
        if isinstance(ret, Error):
            return ret
    
    for broker_app_uid, resource_app in resource_broker_apps.items():
        if broker_app_uid not in broker_apps:
            new_broker_apps.append(resource_app)
            continue
    
    if new_broker_apps:
        for broker_app in new_broker_apps:
            ret = register_broker_app(sender["zone"], broker_app)
            if isinstance(ret, Error):
                return ret

    if del_broker_apps:
        for broker_app in del_broker_apps:
            broker_app_id = broker_app["broker_app_id"]
            ctx.pg.base_delete(dbconst.TB_BROKER_APP_DELIVERY_GROUP, {"broker_app_id": broker_app_id})
            ctx.pg.base_delete(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, {"broker_app_id": broker_app_id})
            
            ret = delete_broker_app(sender, broker_app)
            if isinstance(ret, Error):
                return ret

    return None

def check_broker_app_group_member(sender, broker_app_group, resource_broker_app_group):
    
    ctx = context.instance()
    broker_app_group_id = broker_app_group["broker_app_group_id"]
    broker_app_group_uid = resource_broker_app_group["app_group_uid"]

    resource_broker_apps = ctx.res.resource_describe_broker_apps(sender["zone"], app_group_uids = [broker_app_group_uid], index_uid=True)
    if resource_broker_apps is None:
        resource_broker_apps = {}
    
    resource_broker_app_uids = resource_broker_apps.keys()
    resource_broker_group_uids = ctx.pgm.get_broker_app_by_uid(resource_broker_app_uids)
    if not resource_broker_group_uids:
        resource_broker_group_ids = []
    else:
        resource_broker_group_ids = resource_broker_group_uids.keys()

    app_group_broker_apps = ctx.pgm.get_broker_app_group_app(broker_app_group_id)
    if not app_group_broker_apps:
        app_group_broker_apps = {}

    new_broker_app_ids = []
    del_broker_app_ids = []
    
    for app_id, _ in app_group_broker_apps.items():
        if app_id not in resource_broker_group_ids:
            del_broker_app_ids.append(app_id)
    
    for resource_app_id in resource_broker_group_ids:
        if resource_app_id not in app_group_broker_apps:
            new_broker_app_ids.append(resource_app_id)

    if new_broker_app_ids:
        
        broker_apps = ctx.pgm.get_broker_apps(new_broker_app_ids)
        if not broker_apps:
            broker_apps = {}
        for broker_app_id in new_broker_app_ids:
            update_broker_apps = {}
            broker_app = broker_apps.get(broker_app_id)
            if not broker_app:
                continue
            update_broker_apps = {"broker_app_group_id": broker_app_group_id,
                                  "broker_app_group_name": broker_app_group["broker_app_group_name"],
                                  "broker_app_id": broker_app_id,
                                  "broker_app_name": broker_app["display_name"]}
        
            if not ctx.pg.insert(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, update_broker_apps):
                logger.error("insert newly created desktop group for [%s] to db failed" % (broker_app_id))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    if del_broker_app_ids:
        ctx.pg.base_delete(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, {"broker_app_id": del_broker_app_ids, "broker_app_group_id":broker_app_group_id})
    
    return None

def refresh_broker_app_groups(sender):
    
    ctx = context.instance()
    
    broker_app_groups = ctx.pgm.get_broker_app_groups(zone_id=sender["zone"], index_uid=True)
    if not broker_app_groups:
        broker_app_groups = {}

    resource_broker_app_groups = ctx.res.resource_describe_broker_app_groups(sender["zone"], index_uid=True)
    if resource_broker_app_groups is None:
        resource_broker_app_groups = {}

    new_broker_app_groups = []
    del_broker_app_groups = []
    
    for broker_app_group_uid, broker_app_group in broker_app_groups.items():
        if broker_app_group_uid not in resource_broker_app_groups:
            broker_app_group_id = broker_app_group["broker_app_group_id"]
            del_broker_app_groups.append(broker_app_group_id)
            continue
        resource_broker_app_group = resource_broker_app_groups[broker_app_group_uid]
        check_broker_app_group_member(sender, broker_app_group, resource_broker_app_group)
        
    for broker_app_group_uid, resource_app_group in resource_broker_app_groups.items():
        if broker_app_group_uid not in broker_app_groups:
            new_broker_app_groups.append(resource_app_group)
    
    if new_broker_app_groups:
        for broker_app_group in new_broker_app_groups:
            ret = register_broker_app_group(sender["zone"], broker_app_group)
            if isinstance(ret, Error):
                return ret
            
            new_brober_app_group_id = ret
            new_broker_app = ctx.pgm.get_broker_app_group(new_brober_app_group_id)
            check_broker_app_group_member(sender, new_broker_app, broker_app_group)

    if del_broker_app_groups:
        conditions = {"broker_app_group_id": del_broker_app_groups}
        ctx.pg.base_delete(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, conditions)
        ctx.pg.base_delete(dbconst.TB_BROKER_APP_GROUP, conditions)

    return None

def create_broker_apps(sender, delivery_group, desktop, app_datas, is_startmenu):
    
    ctx = context.instance()
    zone = sender["zone"]
    delivery_group_name = delivery_group["delivery_group_name"]
    broker_app_ids = []
    hostname = desktop["hostname"]
    for app_data in app_datas:
        app_name = app_data["display_name"]
        
        app_data["local_exe_flag"] = 0 if is_startmenu else 1
        ret = ctx.res.resource_create_broker_app(zone, delivery_group_name, hostname, app_data)
        if ret is None:
            logger.error("ceate broker apps fail %s" % (app_data))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_BROKER_APP_RESOURCE_FAILED, app_name)
        
        ret = ctx.res.resource_describe_broker_apps(zone, [app_name])
        if not ret:
            logger.error("app data %s lack key " % (app_name))
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                             ErrorMsg.ERR_MSG_CREATE_APP_PARAM_ERROR)
        broker_app = ret[app_name]
        ret = register_broker_app(zone, broker_app)
        if isinstance(ret, Error):
            return ret

        broker_app_ids.append(ret)
        
    ret = refresh_broker_apps(sender, broker_app_ids)
    if isinstance(ret, Error):
        return ret
        
    return broker_app_ids

def modify_broker_app_attributes(sender, broker_app, need_maint_columns):

    ctx = context.instance()
    broker_app_id = broker_app["broker_app_id"]
    
    ret = ctx.res.resource_modify_broker_app(sender["zone"], broker_app["broker_app_uid"], **need_maint_columns)
    if not ret:
        logger.error("modify broker app data fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if "admin_display_name" in need_maint_columns:
        need_maint_columns["display_name"] = need_maint_columns["admin_display_name"]
    
    broker_app_name = broker_app["display_name"] if "admin_display_name" not in need_maint_columns else need_maint_columns["admin_display_name"]
    
    ret = ctx.res.resource_describe_broker_apps(sender["zone"], broker_app_name)
    if not ret:
        logger.error("describe app group %s" % broker_app_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if not ctx.pg.batch_update(dbconst.TB_BROKER_APP, {broker_app_id: need_maint_columns}):
        logger.error("modify broker app data fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def describe_system_broker_apps(sender):

    ctx = context.instance()
    ret = ctx.res.resource_describe_delivery_groups(sender["zone"])
    if not ret:
        logger.error("resource describe delivery group fail")
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    delivery_group_set = ret

    existed_delivery_groups = ctx.pgm.get_delivery_group_name(zone_id=sender["zone"])
    if not existed_delivery_groups:
        existed_delivery_groups = {}
    
    system_delivery_group = {}
    for delivery_group_name, delivery_group in delivery_group_set.items():
        if delivery_group_name in existed_delivery_groups.values():
            continue
        delivery_group["delivery_group_name"] = delivery_group_name
        system_delivery_group[delivery_group_name] = delivery_group

    return system_delivery_group

def check_broker_app(sender, broker_app_ids):
    
    ctx = context.instance()
    
    if not broker_app_ids:
        return None

    if not isinstance(broker_app_ids, list):
        broker_app_ids = [broker_app_ids]

    broker_apps = ctx.pgm.get_broker_apps(broker_app_ids)
    if not broker_apps:
        broker_apps = {}

    broker_app_names = []
    for broker_app_id in broker_app_ids:
        if broker_app_id not in broker_apps:
            logger.error("resource describe delivery group fail")
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        broker_app = broker_apps[broker_app_id]
        broker_app_names.append(broker_app["display_name"])

    ret = ctx.res.resource_describe_broker_apps(sender["zone"], broker_app_names)
    if not ret:
        logger.error("resource ddc broker app fail")
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DDC_DESC_RESOURCE_FAILED)
    
    resource_broker_apps = ret
    for broker_app_name in broker_app_names:
        if broker_app_name not in resource_broker_apps:
            logger.error("no found resource broker app %s" % broker_app_name)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    return broker_apps

def delete_broker_app(sender, broker_app):
    
    ctx = context.instance()
    display_name = broker_app["display_name"]
    broker_app_id = broker_app["broker_app_id"]
    resource_broker_apps = ctx.res.resource_describe_broker_apps(sender["zone"], display_name)
    if not resource_broker_apps:
        resource_broker_apps = {}
    
    resource_broker_app = resource_broker_apps.get(display_name)
    if resource_broker_app:
        ret = ctx.res.resource_remove_broker_app(sender["zone"], display_name)
        if not ret:
            logger.error("no found resource broker app %s" % display_name)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    ctx.pg.delete(dbconst.TB_BROKER_APP, broker_app_id)
    
    return broker_app_id

def delete_broker_apps(sender, broker_apps):
   
    for _, broker_app in broker_apps.items():

        ret = detach_broker_app_from_delivery_group(sender, broker_app)
        if isinstance(ret, Error):
            return ret

        ret =  detach_broker_app_from_app_group(sender, broker_app)
        if isinstance(ret, Error):
            return ret
        
        ret = delete_broker_app(sender, broker_app)
        if isinstance(ret, Error):
            return ret
    
    return None

def check_detach_broker_app(broker_app_id, delivery_group_id=None, broker_app_group_id=None):
    
    ctx = context.instance()

    check_delivery_group = ctx.pgm.get_broker_app_delivery_group(broker_app_id)
    if not check_delivery_group:
        check_delivery_group = []
    
    check_app_group = ctx.pgm.get_broker_app_app_group(broker_app_id)
    if not check_app_group:
        check_app_group = []
    
    if delivery_group_id and delivery_group_id not in check_delivery_group:
        logger.error("broker app no found delviery group %s" % broker_app_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DETACH_BROKER_APP_NO_FOUND_GROUP, delivery_group_id)
    
    if broker_app_group_id and broker_app_group_id not in check_app_group:
        logger.error("detach broker app no found group %s" % broker_app_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DETACH_BROKER_APP_NO_FOUND_GROUP, broker_app_group_id)
    
    if len(check_delivery_group) + len(check_app_group) <= 1:
        logger.error("broker app %s must be in some group" % broker_app_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_BROKER_APP_MUST_BE_IN_A_GROUP, broker_app_id)
        
    return None

def check_detach_broker_app_from_delivery_group(delivery_group_id, broker_app_ids=None, broker_app_group_ids=None):
    
    ctx = context.instance()

    delivery_group = ctx.pgm.get_delivery_group(delivery_group_id)
    if not delivery_group:
        logger.error("resource describe delivery group fail %s" % delivery_group_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    if broker_app_ids:
        for broker_app_id in broker_app_ids:
            ret = check_detach_broker_app(broker_app_id, delivery_group_id)
            if isinstance(ret, Error):
                return ret

    if broker_app_group_ids:
        broker_app_groups = ctx.pgm.get_delivery_group_broker_app_groups(delivery_group_id, broker_app_group_ids)
        if not broker_app_groups:
            logger.error("resource describe broker app fail %s" % broker_app_ids)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    return delivery_group

def check_attach_delivery_group_broker_apps(delivery_group_id, broker_app_ids=None, broker_app_group_ids=None):
    
    ctx = context.instance()

    delivery_group = ctx.pgm.get_delivery_group(delivery_group_id)
    if not delivery_group:
        logger.error("resource describe delivery group fail %s" % delivery_group_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    if broker_app_ids:
        broker_apps = ctx.pgm.get_delivery_group_broker_apps(broker_app_ids, delivery_group_id)
        if not broker_apps:
            broker_apps = {}
    
        if broker_apps:
            logger.error("resource describe broker app fail %s" % broker_app_ids)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    if broker_app_group_ids:
        broker_app_groups = ctx.pgm.get_delivery_group_broker_app_groups(delivery_group_id, broker_app_group_ids)
        if not broker_app_groups:
            broker_app_groups = {}
        
        if broker_app_groups:
            logger.error("resource describe broker app fail %s" % broker_app_ids)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    return delivery_group

def attach_broker_app_to_delivery_group(sender, delivery_group, broker_app_ids, is_load=False):
    
    ctx = context.instance()
    
    delivery_group_id = delivery_group["delivery_group_id"]
    
    broker_apps = ctx.pgm.get_broker_apps(broker_app_ids)
    if not broker_apps:
        return None
    
    existed_broker_apps = ctx.pgm.get_delivery_group_broker_apps(delivery_group_id, broker_app_ids)
    if not existed_broker_apps:
        existed_broker_apps = {}
    
    delivery_group_name = delivery_group["delivery_group_name"]
    for broker_app_id, broker_app in broker_apps.items():
        
        if broker_app_id in existed_broker_apps:
            continue

        if not is_load:
            display_name = broker_app["display_name"]
            ret = ctx.res.resource_add_broker_app(sender["zone"], display_name, delivery_group_name)
            if ret is None:
                continue
        
        update_broker_apps = {"delivery_group_id": delivery_group_id,
                              "delivery_group_name": delivery_group["delivery_group_name"],
                              "broker_app_id": broker_app_id,
                              "broker_type": const.BROKER_APP_TYPE_APP,
                              "broker_app_name": broker_app["display_name"]}
        
        if not ctx.pg.insert(dbconst.TB_BROKER_APP_DELIVERY_GROUP, update_broker_apps):
            logger.error("insert newly created desktop group for [%s] to db failed" % (broker_app_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return None

def attach_broker_app_group_to_delivery_group(sender, delivery_group, broker_app_group_ids, is_load=False):
    
    ctx = context.instance()
    
    delivery_group_id = delivery_group["delivery_group_id"]
    
    broker_app_groups = ctx.pgm.get_broker_app_groups(broker_app_group_ids)
    if not broker_app_groups:
        return None
    
    existed_broker_app_groups = ctx.pgm.get_delivery_group_broker_app_groups(delivery_group_id, broker_app_group_ids)
    if not existed_broker_app_groups:
        existed_broker_app_groups = {}
    
    delivery_group_name = delivery_group["delivery_group_name"]
    for broker_app_group_id, broker_app_group in broker_app_groups.items():
        
        if broker_app_group_id in existed_broker_app_groups:
            continue
        
        broker_app_group_name = broker_app_group["broker_app_group_name"]
        if not is_load:
            ret = ctx.res.resource_add_broker_app_group(sender["zone"], broker_app_group_name, delivery_group_name)
            if ret is None:
                continue
        
        update_broker_apps = {"delivery_group_id": delivery_group_id,
                              "delivery_group_name": delivery_group["delivery_group_name"],
                              "broker_type": const.BROKER_APP_TYPE_APP_GROUP,
                              "broker_app_id": broker_app_group_id,
                              "broker_app_name": broker_app_group["broker_app_group_name"]}
        
        if not ctx.pg.insert(dbconst.TB_BROKER_APP_DELIVERY_GROUP, update_broker_apps):
            logger.error("insert newly created desktop group for [%s] to db failed" % (broker_app_group_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return None

def detach_broker_app_from_group(sender, broker_apps, delivery_group_ids=None, app_group_names=None):
    
    for _, broker_app in broker_apps.items():
        
        if delivery_group_ids:
            ret = detach_broker_app_from_delivery_group(sender, broker_app, delivery_group_ids)
            if isinstance(ret, Error):
                return ret
            
        if app_group_names:
            ret = detach_broker_app_from_app_group(sender, broker_app, delivery_group_ids)
            if isinstance(ret, Error):
                return ret
    
    return None

def detach_broker_app_from_delivery_group(sender, broker_app, delivery_group_ids=None):
    
    ctx = context.instance()
    broker_app_id = broker_app["broker_app_id"]

    delivery_group_ids = ctx.pgm.get_broker_app_delivery_group(broker_app_id, delivery_group_ids)
    if not delivery_group_ids:
        return None
    
    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_ids)
    if not delivery_groups:
        return None
    
    broker_app_name = broker_app["display_name"]
    ret = ctx.res.resource_describe_broker_apps(sender["zone"], broker_app_name)
    if not ret or not ret.get(broker_app_name):
        logger.error("no found broker app %s resource" % (broker_app_name))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    resource_broker_app = ret[broker_app_name]
    
    delivery_group_uids = resource_broker_app["all_desktopgroup_uids"]
    
    detach_delivery_uids = {}
    for delivery_group_id, delivery_group in delivery_groups.items():
        
        delivery_group_uid = delivery_group["delivery_group_uid"]
        if delivery_group_uid in delivery_group_uids:
            detach_delivery_uids[delivery_group_id] = delivery_group_uid
    
    if detach_delivery_uids:
        for delivery_group_id, detach_delivery_uid in detach_delivery_uids.items():
            ret = ctx.res.resource_remove_broker_app(sender["zone"], broker_app_name, detach_delivery_uid)
            if not ret:
                logger.error("no found broker app %s resource" % (broker_app_name))
                return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                             ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
            ctx.pg.base_delete(dbconst.TB_BROKER_APP_DELIVERY_GROUP, {"broker_app_id": broker_app_id, "delivery_group_id": delivery_group_id})
            delivery_group_ids.remove(delivery_group_id)
    
    if delivery_group_ids:
        ctx.pg.base_delete(dbconst.TB_BROKER_APP_DELIVERY_GROUP, {"broker_app_id": broker_app_id, "delivery_group_id": delivery_group_ids})
    
    return None

def detach_broker_app_group_from_delivery_group(sender, broker_app_group_id, delivery_group):
    
    ctx = context.instance()
    delivery_group_id = delivery_group["delivery_group_id"]
    
    delivery_group_ids = ctx.pgm.get_delivery_group_broker_app_groups(delivery_group_id, broker_app_group_id)
    if not delivery_group_ids:
        return None
    
    ret = ctx.pgm.get_broker_app_groups(broker_app_group_id)
    if not ret:
        logger.error("no found broker app %s resource" % (broker_app_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    broker_app_group = ret[broker_app_group_id]

    broker_app_group_name = broker_app_group["broker_app_group_name"]
    ret = ctx.res.resource_describe_broker_app_groups(sender["zone"], broker_app_group_name)
    if not ret or not ret.get(broker_app_group_name):
        logger.error("no found broker app %s resource" % (broker_app_group_name))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    resource_broker_app_group = ret[broker_app_group_name]
      
    delivery_group_uids = resource_broker_app_group["associated_deliverygroup_uids"]
    
    delivery_group_uid = delivery_group["delivery_group_uid"]
    delivery_group_name = delivery_group["delivery_group_name"]
    if delivery_group_uid in delivery_group_uids:
        ret = ctx.res.resource_delete_broker_app_group(sender["zone"], broker_app_group_name, delivery_group_name)
        if not ret:
            logger.error("no found broker app %s resource" % (broker_app_group_name))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    ctx.pg.base_delete(dbconst.TB_BROKER_APP_DELIVERY_GROUP, {"broker_app_id": broker_app_group_id, "delivery_group_id": delivery_group_id})
    
    return None

def register_broker_app_group(zone, app_group):

    ctx = context.instance()
   
    broker_app_group_id = get_uuid(UUID_TYPE_BROKER_APP_GROUP, ctx.checker)
    broker_app_group_info = dict(
                              broker_app_group_id = broker_app_group_id,
                              broker_app_group_name = app_group["app_group_name"],
                              broker_app_group_uid = app_group["app_group_uid"],
                              create_time = get_current_time(),
                              description = app_group.get("description"),
                              zone = zone,
                              )

    # register desktop group
    if not ctx.pg.insert(dbconst.TB_BROKER_APP_GROUP, broker_app_group_info):
        logger.error("insert newly create broker app group for [%s] to db failed" % (broker_app_group_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return broker_app_group_id

def check_broker_app_group(broker_app_group_ids):
    
    ctx = context.instance()
    
    if not broker_app_group_ids:
        return None
    
    if not isinstance(broker_app_group_ids, list):
        broker_app_group_ids = [broker_app_group_ids]
    
    broker_app_groups = ctx.pgm.get_broker_app_groups(broker_app_group_ids)
    if not broker_app_groups:
        broker_app_groups = {}
    
    for broker_app_group_id in broker_app_group_ids:
        
        if broker_app_group_id not in broker_app_groups:
            logger.error("no found desktop resource %s" % (broker_app_group_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, broker_app_group_id)
    
    return broker_app_groups

def create_broker_app_group(sender, broker_app_group_name, req):
    
    ctx = context.instance()
    zone = sender["zone"]
    
    ret = ctx.res.resource_create_broker_app_group(zone, broker_app_group_name, req.get("description"))
    if not ret:
        logger.error("app data %s lack key " % (broker_app_group_name))
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_CREATE_APP_PARAM_ERROR)

    ret = ctx.res.resource_describe_broker_app_groups(zone, broker_app_group_name)
    if ret is None:
        logger.error("no found desktop resource %s" % (broker_app_group_name))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, broker_app_group_name)

    app_group = ret[broker_app_group_name]

    ret = register_broker_app_group(zone, app_group)
    if isinstance(ret, Error):
        return ret
    
    broker_app_group_id = ret

    return broker_app_group_id

def attach_broker_app_to_app_group(sender, broker_app_group, broker_apps):
    
    ctx = context.instance()
    broker_app_group_id = broker_app_group["broker_app_group_id"]
  
    broker_app_ids = broker_apps.keys()
    ret = refresh_broker_apps(sender, broker_app_ids)
    if isinstance(ret, Error):
        return ret
    
    existed_broker_apps = ctx.pgm.get_broker_app_group_app(broker_app_group_id)
    if not existed_broker_apps:
        existed_broker_apps = {}
    
    for broker_app_id, broker_app in broker_apps.items():
        
        if broker_app_id in existed_broker_apps:
            continue
        
        broker_app_group_name = broker_app_group["broker_app_group_name"]
        display_name = broker_app["display_name"]
        ret = ctx.res.resource_add_broker_app(sender["zone"], display_name, app_group_name=broker_app_group_name)
        if ret is None:
            continue
        
        update_broker_apps = {"broker_app_group_id": broker_app_group_id,
                              "broker_app_group_name": broker_app_group_name,
                              "broker_app_id": broker_app_id,
                              "broker_app_name": broker_app["display_name"]}
        
        if not ctx.pg.insert(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, update_broker_apps):
            logger.error("insert newly created desktop group for [%s] to db failed" % (broker_app_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return None

def detach_broker_app_from_app_group(sender, broker_app, app_group_names=None):
    
    ctx = context.instance()
    
    broker_app_id = broker_app["broker_app_id"]
    broker_app_groups = ctx.pgm.get_app_group_by_name(sender["zone"], app_group_names)
    if not broker_app_groups:
        return None
    
    broker_app_name = broker_app["display_name"]
    ret = ctx.res.resource_describe_broker_apps(sender["zone"], broker_app_name)
    if not ret or not ret.get(broker_app_name):
        logger.error("no found broker app %s resource" % (broker_app_name))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    resource_broker_app = ret[broker_app_name]
    
    all_appgroup_uids = resource_broker_app["all_appgroup_uids"]
    
    if app_group_names:
        app_groups = ctx.res.resource_describe_broker_app_groups(sender["zone"], app_group_names)
        if app_groups:
            all_appgroup_uids = []
            for _, app_group in app_groups.items():
                app_group_uid = app_group["app_group_uid"]
                all_appgroup_uids.append(app_group_uid)
    
    if not all_appgroup_uids:
        return None

    for all_appgroup_uid in all_appgroup_uids:
        ret = ctx.res.resource_remove_broker_app(sender["zone"], broker_app_name, app_group_uid=all_appgroup_uid)
        if not ret:
            logger.error("no found broker app %s resource" % (broker_app_name))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        
    ctx.pg.base_delete(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, {"broker_app_id": broker_app_id, "broker_app_group_id": broker_app_groups.keys()})

    return None

def delete_broker_app_groups(sender, broker_app_groups):
    
    ctx = context.instance()
    
    broker_app_group_ids = broker_app_groups.keys()
    
    broker_app_group_names = ctx.pgm.get_app_group_names(broker_app_group_ids)
    resource_app_group_names = broker_app_group_names.values()
    
    resource_broker_app_groups = ctx.res.resource_describe_broker_app_groups(sender["zone"], resource_app_group_names)
    if not resource_broker_app_groups:
        resource_broker_app_groups = {}
    
    for _, broker_app_group_name in broker_app_group_names.items():
        
        if broker_app_group_name not in resource_broker_app_groups:
            continue
        
        ret = ctx.res.resource_delete_broker_app_group(sender["zone"], broker_app_group_name)
        if not ret:
            logger.error("no found resource broker app %s" % broker_app_group_name)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    conditions = {"broker_app_group_id": broker_app_group_ids}
    ctx.pg.base_delete(dbconst.TB_BROKER_APP_GROUP_BROKER_APP, conditions)
    ctx.pg.base_delete(dbconst.TB_BROKER_APP_GROUP, conditions)
    
    return broker_app_group_ids
