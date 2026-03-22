import datetime
import context
from constants import (
    TOPIC_EVENT_SUB_TYPE_LICENSE,
    PUSH_EVENT_LICENSE_PROMPT,
    GLOBAL_ADMIN_USER_ID,
    ACTION_VDI_UPDATE_LICENSE
    )
from log.logger import logger
from send_request import push_topic_event, send_desktop_server_request

def check_license():
    ctx = context.instance()
    try:
        lic = ctx.pgm.load_license_info()
        if not lic:
            logger.error("load license error")
            return False

        logger.info("license = %s" % lic)
        (y,m,d) = str.split(lic["terminate_date"], '-')
        terminate_date = datetime.date(int(y), int(m), int(d))
        ret = terminate_date - datetime.date.today()
        if(ret.days < 0):
            logger.error("license is expired")
            # send to push server and update license
            data = {
                "event": PUSH_EVENT_LICENSE_PROMPT,
                "valid_day": ret.days
                }
            push_topic_event(GLOBAL_ADMIN_USER_ID, TOPIC_EVENT_SUB_TYPE_LICENSE, data)
            
            req = {"type": "internal",
                   "params": {
                       "action": ACTION_VDI_UPDATE_LICENSE,
                       "zone": "ignore"
                       }
                   }
            send_desktop_server_request(req)
            return False
        if(ret.days>0 and ret.days<30):
            # send to push server
            logger.info("license will be expired")
            data = {
                "event": PUSH_EVENT_LICENSE_PROMPT,
                "valid_day": ret.days
                }
            push_topic_event(GLOBAL_ADMIN_USER_ID, TOPIC_EVENT_SUB_TYPE_LICENSE, data)

        return True
    except Exception,e:
        logger.error("check license exception:" + e)
        return False
    