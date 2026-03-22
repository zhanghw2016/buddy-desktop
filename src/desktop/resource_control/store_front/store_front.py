
from common import is_citrix_platform
import context
from error.error import Error
from resource_control.desktop.desktop import check_citrix_is_lock
from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
import copy
def check_sf_cookies(req):
    
    ctx = context.instance()
    sender = req["sender"]
    password = req.get("password", "")
    
    user_name = sender["user_name"]
    user_id = sender["owner"]

    sf_info = {}

    user_zones = ctx.pgm.get_local_user_zones(user_id)
    if not user_zones:
        return None

    sf_cookies = {}

    sf_uris={}
    
    for zone_id in user_zones:

        if not is_citrix_platform(ctx, zone_id):
            continue

        uri = get_sf_uri(zone_id)
        if not uri:
            continue
        
        ret = check_store_front_session(zone_id, user_name, password,sf_uris)
        if isinstance(ret, Error):                
            sf_info[zone_id] = ret.get_message()
            continue
        if not ret:
            continue            
        sf_cookies[zone_id] = ret.replace('@',';') if ret else ''

    return sf_cookies, sf_info

def get_sf_uri(zone_id):

    ctx = context.instance()

    zone_storefronts = ctx.zone_storefronts.get(zone_id)
    if not zone_storefronts:
        return None

    citrix_connection = zone_storefronts.citrix_connection
    flag = citrix_connection["support_netscaler"]
    if flag:
        uri=citrix_connection["netscaler_uri"]
    else:
        uri=citrix_connection["storefront_uri"]
    if not uri:
        return None 
    return uri   

def get_sf_desktops(user_id, desktop_set, sf_cookies, req):
    
    ctx = context.instance()
    unassign_desktop = []
    randset_desktop = []
    appset_list = []
    sender = req["sender"]
    if not sf_cookies:
        return None

    sf_resources={}
    sf_uris={}
    for zone_id, sf_cookie in sf_cookies.items():
        
        if not sf_cookie:
            continue
        
        if not is_citrix_platform(ctx, zone_id):
            continue

        unassign = []
        randset = []
        appset = []         
        cookie_zone_sender = {"zone": zone_id, "owner": user_id}
        zone_store_front = ctx.zone_storefronts.get(zone_id)
        uri=zone_store_front.base_url
        if not uri:
            continue

        if uri not in sf_resources.keys():
            resource_ret = get_store_front_resource_list(zone_id, sf_cookie)          
            sf_resources[uri]=resource_ret
            sf_uris[uri]=sf_cookie
        else:
            resource_ret=sf_resources[uri]

        if isinstance(resource_ret, Error):
            password = req.get("password")
            if resource_ret.code == ErrorCodes.STOREFRONT_GETDESKTOPLIST_UNAUTHORIZE_ERROR and password:
                
                user_name = sender["user_name"]
                ret = check_store_front_session(zone_id, user_name, password,sf_uris)
                if isinstance(ret, Error) or not ret:
                    continue                
                sf_cookies[zone_id] = ret
                resource_ret = get_store_front_resource_list(zone_id, ret)  
                if isinstance(resource_ret, Error):
                    continue
                zone_store_front = ctx.zone_storefronts.get(zone_id)
                base_url=zone_store_front.base_url                
                sf_resources[base_url]=resource_ret    
            else:
                continue

        ret = describe_store_front_desktops(cookie_zone_sender, desktop_set, resource_ret)  
        if isinstance(ret, Error):
            continue
        unassign, randset, appset = ret
        if unassign:
            unassign_desktop.extend(unassign)
        
        if randset:
            randset_desktop.extend(randset)
            
        if appset:
            apps=copy.deepcopy(appset)
            for app in apps:
                app['zone']=zone_id
            appset_list.extend(apps)
    return unassign_desktop, randset_desktop,appset_list

def check_store_front_session(zone_id, user_name, password,sf_uris):

    ctx = context.instance()

    if not is_citrix_platform(ctx, zone_id):
        return None

    zone_store_front = ctx.zone_storefronts.get(zone_id)
    if not zone_store_front:
        logger.error("zone %s no config storefont" % zone_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_ZONE_NO_FOUND_STOREFRONT_CONFIG, zone_id)
    ret = zone_store_front.create_token_storefront_login(zone_store_front, user_name, password,sf_uris)
    if isinstance(ret, Error):
        return ret

    return ret
  
def create_store_front_broker(sender, req):

    ctx = context.instance()

    user_id = sender["owner"]
    cookie = req["sf_cookie"]
    zone_id = sender["zone"]
    ica_uri = req["ica_uri"]
    assign = int(req["assign_state"])
    desktop_id = req.get("desktop")
    assign_uri = req.get("assign_uri")
    zone_store_front = ctx.zone_storefronts.get(zone_id)
    ret = zone_store_front.storefront_get_ica(zone_store_front, cookie, assign ,ica_uri, user_id, desktop_id, assign_uri)
    if isinstance(ret, Error):
        return ret
    
    return ret

def get_store_front_resource_list(zone_id,cookie):
    ctx = context.instance()

    zone_store_front = ctx.zone_storefronts.get(zone_id)
    if not zone_store_front:
        logger.error("no found store front context info %s " % zone_id)
        return None

    ret = zone_store_front.get_storefront_desktoplist(zone_store_front, cookie)
    return ret

def describe_store_front_desktops(sender, desktop_set, resouce_ret):
    
    zone_id = sender["zone"]
    user_id = sender["owner"]

    assignlist, sf_unassign, sf_randset,sf_appset = resouce_ret
    ret = check_citrix_is_lock(sf_unassign, sf_randset, user_id, zone_id)
    (unassign, randset) = ret
    

    if assignlist and desktop_set:
        
        for _, desktop in desktop_set.items():
            if desktop["zone"] != zone_id:
                continue
            
            hostname = desktop["hostname"].lower()
            if hostname not in assignlist:
                continue
            
            delivery_group_id = desktop.get("delivery_group_id")
            if not delivery_group_id:
                continue

            assign_desktop = assignlist[hostname]
            desktop['launch_url'] = assign_desktop['launch_url']
            desktop['assign_state'] = 1
  
            
    return unassign, randset,sf_appset

