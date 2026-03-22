import context
from log.logger import logger
import constants as const
import db.constants as dbconst
import time
import resource_common as ResComm
import dispatch_resource.guest as Guest
import api.auth.ad_service as ADService 

def update_desktop_in_domain(desktop_ids, in_domain=1):
    
    ctx = context.instance()
    if not ctx.pg.base_update(dbconst.TB_DESKTOP, {"desktop_id": desktop_ids}, {"in_domain": in_domain}):
        logger.error("update desktop domain[%s] to 1 fail" % desktop_ids)
        return -1
    return 0

def desktop_in_domain(desktop, domain_info):

    ctx = context.instance()
    zone_id = desktop["zone"]

    auth_service = ctx.pgm.get_zone_auth(zone_id)
    if not auth_service:
        logger.error("zone %s no found auth service" %(zone_id))
        return -1

    desktop_id = desktop["desktop_id"]
    desktop_dn = domain_info["desktop_dn"]
    ips = [] 
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return -1
    for _,nic in nics.items():
        ips.append(nic["private_ip"])

    domain_req = {
        "action": const.REQUEST_VDHOST_SERVER_ADD_AD,
        "desktop_id": desktop_id,
        "desktop_ips": ips,
        "params": {
            "username": auth_service["admin_name"],
            "password": auth_service["admin_password"],
            "domain": auth_service["domain"],
            "ou": desktop_dn
        }
    }

    in_domain = 1
    ret = Guest.add_active_directory(domain_req)
    if ret < 0:
        logger.error("add desktop[%s] to AD error." % desktop_id)
        return -1

    ret = update_desktop_in_domain(desktop_id, in_domain)
    if ret < 0:
        logger.error("update desktop in domain fail: %s" % desktop_id)
        return -1
    return 0

def desktop_join_domain(desktop):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    
    desktop_dn = desktop.get("desktop_dn")
    if not desktop_dn:
        return 0
    
    desktop_nics = ctx.pgm.get_desktop_nics(desktop_id)
    if not desktop_nics:
        logger.error("desktop %s no network to add domain" % desktop_id)
        return -1

    time.sleep(100)
    domain_info= {
                  "desktop_dn": desktop_dn,
                  "hostname": desktop["hostname"],
                  "desktop_id": desktop_id,
                  }
    retries = 3
    while True:
        if retries == 0:
            logger.error("do desktop in domain fail: %s" % desktop_id)
            return -1

        ret = desktop_in_domain(desktop, domain_info)
        if ret==0:
            return 0

        retries -= 1
        time.sleep(30)

    return 0

def desktop_leave_domain(sender, desktop):
    
    ctx = context.instance()
    desktop_dn = desktop["desktop_dn"]
    hostname = desktop["hostname"]
    desktop_id = desktop["desktop_id"]

    if not desktop["in_domain"]:
        return 0

    auth_zone = ctx.pgm.get_auth_zone(sender["zone"])
    if not auth_zone:
        return 0
    auth_service_set = ctx.pgm.get_auth_services(auth_service_ids=[auth_zone["auth_service_id"]])
    auth_service = auth_service_set.get(auth_zone["auth_service_id"])
    if(auth_service):
        conn = {
            "domain": auth_service["domain"],
            "base_dn": auth_service["base_dn"],
            "admin_name": auth_service["admin_name"],
            "admin_password": auth_service["admin_password"],
            "host": auth_service["host"],
            "port": auth_service["port"],
            "secret_port": auth_service["secret_port"]
            }
        ad_auth = ADService.ADServerAuth(conn)
        desktop_dn = "cn=%s,%s" % (hostname, desktop_dn)
        ad_auth.delete_users([desktop_dn])

    ret = update_desktop_in_domain(desktop_id, 0)
    if ret < 0:
        logger.error("update desktop in domain fail: %s" % desktop_id)
        return -1
    return 0

def desktop_domain(desktop):

    desktop_dn = desktop["desktop_dn"]
    if not desktop_dn:
        return 0
    
    desktop_id = desktop["desktop_id"]
    ResComm.send_internel_req(const.INTERNEL_ACTION_DESKTOP_JOIN_DOMAIN, desktop_id)
    
