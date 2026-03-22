from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_SOFTWARE
)
import constants as const
from utils.id_tool import(
    get_uuid
)
from utils.misc import get_current_time,exec_cmd
import os
import resource_control.desktop.job as Job
from utils.net import get_hostname
import os
from common import get_target_host_list

def send_desktop_software_job(sender, software_ids, action, extra=None):

    if not isinstance(software_ids, list):
        software_ids = [software_ids]

    directive = {
        "sender": sender,
        "action": action,
        "software_id": software_ids,
    }
    if extra:
        directive.update(extra)

    ret = Job.submit_desktop_job(action, directive, software_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def is_software_exist(download_software_uri):

    if not os.path.exists(download_software_uri):
        if download_software_uri == const.DOWNLOAD_SOFTWARE_BASE_URI:
            ret = exec_cmd("/bin/mkdir -p /mnt/nasdata && chmod -R 777 /mnt/nasdata")
            if ret != None and ret[0] == 0:
                return True
        return False
    return True

def delete_origin_softwares_cmd(download_software_uri,target_hostname):

    os.system('/bin/rm -fr %s' %(download_software_uri))
    os.system('ssh -o StrictHostKeyChecking=no root@%s "/bin/rm -fr %s"' %(target_hostname, download_software_uri))

def get_vnas_node_remain_size(vnas_node_dir):
    ret = exec_cmd("df -h --block-size=k | grep %s | awk '{print $4}'" % (vnas_node_dir))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def rsync_system_custom_logo(software_name):

    ctx = context.instance()
    origin_vdi_portal_static_img = "%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, software_name)
    destination_vdi_portal_static_img = "%s/%s" % (const.VDI_PORTAL_STATIC_IMG_DIR, software_name)

    target_host_list = get_target_host_list(ctx)
    for target_host in target_host_list:

        cmd = "scp -r %s root@%s:%s" % (origin_vdi_portal_static_img, target_host, destination_vdi_portal_static_img)
        exec_cmd(cmd)

def upload_softwares(sender, req):

    ctx = context.instance()
    zone_id = sender["zone"]
    software_name = req.get("software_name")
    software_size = req.get("software_size")
    is_system_custom_logo = req.get("is_system_custom_logo",0)
    software_id = None
    if  is_system_custom_logo:
        rsync_system_custom_logo(software_name)

    return software_id

def download_softwares(software_id):

    ctx = context.instance()
    softwares = ctx.pgm.get_softwares(software_ids=software_id)
    if not softwares:
        logger.error("describe software no found %s" % software_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, software_id)

    for software_id,software in softwares.items():
        software_name = software["software_name"]

    download_software_uri = "%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, software_name)

    if is_software_exist(download_software_uri):
        download_software_exist = 1
    else:
        download_software_exist = 0

    return (download_software_uri, download_software_exist)

def delete_origin_softwares(download_software_uri,target_hostname):

    if is_software_exist(download_software_uri):
        delete_origin_softwares_cmd(download_software_uri,target_hostname)
    else:
        logger.error("software %s not found" % (download_software_uri))

def delete_softwares(software_ids):

    ctx = context.instance()
    if software_ids and not isinstance(software_ids, list):
        software_ids = [software_ids]

    softwares = ctx.pgm.get_softwares(software_ids=software_ids)
    if not softwares:
        logger.error("describe software no found %s" % software_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, software_ids)

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

    for software_id,software in softwares.items():

        software_name = software["software_name"]
        softwares = ctx.pgm.get_softwares(software_name=software_name)

        count = len(softwares)
        if count == 1:
            download_software_uri = "%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, software_name)
            delete_origin_softwares(download_software_uri,target_hostname)

        #delete software in db
        conditions = {"software_id": software_id}
        ctx.pg.base_delete(dbconst.TB_SOFTWARE_INFO, conditions)

    return None

def get_mnt_node_remain_size(vnas_node_dir):

    ret = exec_cmd("df -h --block-size=k  %s | awk 'NR==2 {print $4}'" % (vnas_node_dir))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def mkdir_vnas_node_dir(vnas_node_dir):

    os.system('mkdir -p %s && chmod -R 777 %s' %(vnas_node_dir,vnas_node_dir))

def check_software_vnas_node_dir(vnas_node_dir,zone_deploy):

    mkdir_vnas_node_dir(vnas_node_dir)
    if is_software_exist(vnas_node_dir):
        mnt_nasdata_exist = 1
        if zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            remain_size = get_mnt_node_remain_size(vnas_node_dir)
        else:
            remain_size = get_mnt_node_remain_size(vnas_node_dir)
    else:
        mnt_nasdata_exist = 0
        remain_size = 0

    return (mnt_nasdata_exist,remain_size)
