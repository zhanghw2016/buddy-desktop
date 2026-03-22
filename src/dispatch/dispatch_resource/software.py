import context
from log.logger import logger
from utils.net import get_hostname
import constants as const
from utils.misc import exec_cmd
import os

def check_softwares(software_ids=None):

    ctx = context.instance()
    softwares = ctx.pgm.get_softwares(software_ids=software_ids)
    if not softwares:
        logger.error("describe software %s no found in softwares" % (software_ids))
        return -1

    return softwares

def rsync_softwares_from_localhost_to_remotehost(software_name,local_hostname,target_hostname):

    ret = exec_cmd("rsync -rtv /mnt/nasdata/%s root@%s:/mnt/nasdata/" %(software_name,target_hostname))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def rsync_softwares_from_remotehost_to_localhost(software_name,local_hostname,target_hostname):

    ret = exec_cmd("rsync -rtv root@%s:/mnt/nasdata/%s /mnt/nasdata/" %(target_hostname,software_name))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def is_software_exist_localhost(upload_software_uri):

    if not os.path.exists(upload_software_uri):
        return False
    return True

def task_upload_softwares(sender, software_id,software_name):

    ctx = context.instance()
    zone_deploy = ctx.zone_deploy
    if zone_deploy == const.DEPLOY_TYPE_STANDARD:
        local_hostname = get_hostname()
        target_hostname = const.DESKTOP_SERVER_HOSTNAME_1 if local_hostname == const.DESKTOP_SERVER_HOSTNAME_0 else const.DESKTOP_SERVER_HOSTNAME_0
    else:
        local_hostname = get_hostname()
        if local_hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_0):
            target_hostname = local_hostname.replace(const.DESKTOP_SERVER_HOSTNAME_0, const.DESKTOP_SERVER_HOSTNAME_1)

        if local_hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_1):
            target_hostname = local_hostname.replace(const.DESKTOP_SERVER_HOSTNAME_1, const.DESKTOP_SERVER_HOSTNAME_0)

    upload_software_uri = "/mnt/nasdata/%s" %(software_name)
    if(is_software_exist_localhost(upload_software_uri)):
        ret = rsync_softwares_from_localhost_to_remotehost(software_name,local_hostname,target_hostname)
        if not ret:
            logger.error("rsync_softwares_from_localhost_to_remotehost failed %s" % software_name)
            return -1
    else:
        ret = rsync_softwares_from_remotehost_to_localhost(software_name,local_hostname,target_hostname)
        if not ret:
            logger.error("rsync_softwares_from_remotehost_to_localhost failed %s" % software_name)
            return -1

    return 0


