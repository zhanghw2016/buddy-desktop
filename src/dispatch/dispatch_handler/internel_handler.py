import constants as const
import traceback
from log.logger import logger
import dispatch_resource.desktop_domain as Domain
import context
import dispatch_resource.desktop_citrix as Citrix

def handle_internel_desktop_join_domain(req):

    ctx = context.instance()

    resources = req.get("resources")
    if not resources:
        return 0
    desktop_id = resources[0]

    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        logger.error("join domain no found resource %s" % desktop_id)
        return -1
    
    desktop = desktops[desktop_id]
    ret = Domain.desktop_join_domain(desktop)
    if ret < 0:
        logger.error("desktop join domain fail %s" % desktop_id)
        return -1

    return 0

def handle_internel_wait_citrix_login(req):
    
    resources = req.get("resources")
    if not resources:
        return 0

    desktop_id = resources[0]
    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        logger.error("wait citrix desktop login, no found desktop resource %s" % desktop_id)
        return -1
    
    desktop = desktops[desktop_id]
    ret = Citrix.wait_citrix_desktop_login(desktop)
    if ret < 0:
        logger.error("desktop wait login fail %s" % desktop_id)
        return -1
    
    return 0

class InternelHandler():

    def __init__(self):
        self.handler = {
            const.INTERNEL_ACTION_DESKTOP_JOIN_DOMAIN: handle_internel_desktop_join_domain,
            const.INTERNEL_ACTION_WAIT_CITRIX_LOGIN: handle_internel_wait_citrix_login
        }
   
    def handle(self, action, req):

        try:
            if action in self.handler:
                # handle directly
                ret = self.handler[action](req)
                if ret < 0:
                    logger.error("internel handler %s resource %s fail" % (action, req))
                else:
                    logger.info("internel handler %s resource %s done" % (action, req))

            return
        except:
            logger.critical("handle request [%s] failed: [%s] [%s]" % (action, req, traceback.format_exc()))
            return

