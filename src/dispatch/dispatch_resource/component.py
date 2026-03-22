import context
from log.logger import logger
from utils.net import get_hostname,is_port_open
import constants as const
from utils.misc import exec_cmd,_exec_cmd
import os
import db.constants as dbconst
from send_request import (
    send_terminal_server_request,
    send_desktop_server_request
    )
import time
from common import get_target_host_list

def get_qingcloud_firstbox():

    ret = exec_cmd("cat /etc/hosts | grep qingcloud-firstbox | awk '{print $3}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def check_component_versions(component_ids=None):

    ctx = context.instance()
    component_versions = ctx.pgm.get_component_versions(component_ids=component_ids)
    if not component_versions:
        logger.error("describe component version %s no found in component_versions" % (component_ids))
        return -1

    return component_versions

def rsync_components_from_localhost_to_remotehost(update_component_uri,target_hostname):

    ret = exec_cmd("rsync -rtv %s root@%s:%s" %(update_component_uri,target_hostname,update_component_uri))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def rsync_components_from_remotehost_to_localhost(update_component_uri,target_hostname):

    ret = exec_cmd("rsync -rtv root@%s:%s %s" %(target_hostname,update_component_uri,update_component_uri))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_upgrade_component_version_log(component_type):

    if component_type == const.COMPONENT_TYPE_SERVER:
        ret = exec_cmd("cat /opt/pitrix_deb/readme.md")
    elif component_type == const.COMPONENT_TYPE_CLIENT:
        ret = exec_cmd("cat /tmp/linux-64/readme.md")
    elif component_type == const.COMPONENT_TYPE_FILE_SHARE_TOOLS:
        ret = exec_cmd("cat /tmp/qingcloud_file_share_tools/readme.md")
    elif component_type == const.COMPONENT_TYPE_TOOLS:
        ret = exec_cmd("cat /tmp/qingcloud_guest_tools/readme.md")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_upgrade_component_version_log_history(component_type):

    if component_type == const.COMPONENT_TYPE_SERVER:
        ret = exec_cmd("cat /opt/pitrix_deb/readme_history.md")
    elif component_type == const.COMPONENT_TYPE_CLIENT:
        ret = exec_cmd("cat /tmp/linux-64/readme_history.md")
    elif component_type == const.COMPONENT_TYPE_FILE_SHARE_TOOLS:
        ret = exec_cmd("cat /tmp/qingcloud_file_share_tools/readme_history.md")
    elif component_type == const.COMPONENT_TYPE_TOOLS:
        ret = exec_cmd("cat /tmp/qingcloud_guest_tools/readme_history.md")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def is_software_exist_localhost(upload_software_uri):

    if not os.path.exists(upload_software_uri):
        return False
    return True

def check_component_dir_exist(component_dir,target_hostname):

    if not os.path.exists(component_dir):
        os.system('mkdir -p %s && chmod -R 777 %s' %(component_dir,component_dir))

    os.system('ssh -o StrictHostKeyChecking=no root@%s "mkdir -p %s && chmod -R 777 %s"' % (target_hostname,component_dir,component_dir))

def check_filename_host(target_hosts,update_component_uri):
    logger.info("check_filename_host target_hosts == %s update_component_uri == %s" %(target_hosts,update_component_uri))
    filename_host = get_hostname()
    for filename_host in target_hosts:
        cmd = "ls %s" % (update_component_uri)
        logger.info("cmd == %s" % (cmd))
        if is_port_open(host=filename_host, port=22):
            ret = _exec_cmd(cmd=cmd, remote_host=filename_host, ssh_port=22)
            if ret != None and ret[0] == 0:
                return filename_host

    return filename_host

def rsync_components_to_target_hosts_from_filename_host(filename_host,target_hosts,component_dir,update_component_uri):
    logger.info("rsync_components_to_target_hosts_from_filename_host filename_host == %s target_hosts == %s" % (filename_host, target_hosts))
    for target_host in target_hosts:
        logger.info("target_host == %s" %(target_host))
        ret =rsync_components(filename_host,target_host,component_dir,update_component_uri)
        if not ret:
            return -1
    return 0

def rsync_components(filename_host,remote_host,component_dir,update_component_uri):

    cmd = "scp -r root@%s:%s root@%s:%s" % (filename_host,update_component_uri, remote_host,component_dir)
    logger.info("cmd == %s" % (cmd))
    ret = exec_cmd(cmd=cmd,timeout=300)
    if ret != None and ret[0] == 0:
        return True
    return False

def check_vnas_server_status(target_hosts):

    for desktop_server_host in target_hosts:
        cmd = "netstat -anp |grep 2049 | grep ESTABLISHED"
        if is_port_open(host=desktop_server_host, port=22):
            ret = _exec_cmd(cmd=cmd, remote_host=desktop_server_host, ssh_port=22)
            (_, output, _) = ret
            logger.info("output == %s" %(output))
            if not output:
                return False
    return True

def task_update_components(sender, component_id,filename,component_type):

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

    if component_type == const.COMPONENT_TYPE_CLIENT:
        update_component_uri = "%s/%s" %(const.COMPONENT_TYPE_CLIENT_DIR,filename)
        component_dir = const.COMPONENT_TYPE_CLIENT_DIR
        check_component_dir_exist(const.COMPONENT_TYPE_CLIENT_DIR,target_hostname)

    elif component_type == const.COMPONENT_TYPE_TOOLS:
        update_component_uri = "%s/%s" % (const.COMPONENT_TYPE_TOOLS_DIR, filename)
        component_dir = const.COMPONENT_TYPE_TOOLS_DIR
        check_component_dir_exist(const.COMPONENT_TYPE_TOOLS_DIR,target_hostname)

    elif component_type == const.COMPONENT_TYPE_SERVER:
        update_component_uri = "%s/%s" % (const.COMPONENT_TYPE_SERVER_DIR, filename)
        component_dir = const.COMPONENT_TYPE_SERVER_DIR
        check_component_dir_exist(const.COMPONENT_TYPE_SERVER_DIR,target_hostname)

    elif component_type == const.COMPONENT_TYPE_FILE_SHARE_TOOLS:
        update_component_uri = "%s/%s" % (const.COMPONENT_TYPE_FILE_SHARE_TOOLS_DIR, filename)
        component_dir = const.COMPONENT_TYPE_FILE_SHARE_TOOLS_DIR
        check_component_dir_exist(const.COMPONENT_TYPE_FILE_SHARE_TOOLS_DIR,target_hostname)

    else:
        logger.error("invalid component_type %s" % (component_type))
        return -1

    #check vnas status in all desktop_sever host
    target_hosts = get_target_host_list(ctx)
    ret = check_vnas_server_status(target_hosts)
    if not ret:
        #check where host is filename in
        target_hosts = get_target_host_list(ctx)
        filename_host = check_filename_host(target_hosts,update_component_uri)
        if filename_host in target_hosts:
            target_hosts.remove(filename_host)
        ret = rsync_components_to_target_hosts_from_filename_host(filename_host,target_hosts,component_dir,update_component_uri)
        if ret < 0:
            return -1

    #update_component_version_log
    component_version_log = ''
    component_version_log_history = ''
    if component_type == const.COMPONENT_TYPE_SERVER:
        os.system("/bin/bash %s -u n" % (update_component_uri))
        component_version_log = get_upgrade_component_version_log(component_type)
        component_version_log_history = get_upgrade_component_version_log_history(component_type)

    elif component_type == const.COMPONENT_TYPE_CLIENT:
        os.system("/bin/bash %s -u n" % (update_component_uri))
        component_version_log = get_upgrade_component_version_log(component_type)
        component_version_log_history = get_upgrade_component_version_log_history(component_type)

    elif component_type == const.COMPONENT_TYPE_FILE_SHARE_TOOLS:
        os.system("/bin/bash %s -u n" % (update_component_uri))
        component_version_log = get_upgrade_component_version_log(component_type)
        component_version_log_history = get_upgrade_component_version_log_history(component_type)

    elif component_type == const.COMPONENT_TYPE_TOOLS:
        os.system("/bin/bash %s -u n" % (update_component_uri))
        component_version_log = get_upgrade_component_version_log(component_type)
        component_version_log_history = get_upgrade_component_version_log_history(component_type)

    if component_version_log or component_version_log_history:
        update_component_version_log(component_ids=component_id,component_version_log=component_version_log,component_version_log_history=component_version_log_history)

    return 0

def update_component_version_log(component_ids,component_version_log='',component_version_log_history=''):

    ctx = context.instance()
    condition = {"component_id": component_ids}
    update_info = {"component_version_log": component_version_log,"component_version_log_history": component_version_log_history}

    if not ctx.pg.base_update(dbconst.TB_COMPONENT_VERSION, condition, update_info):
        logger.error("update component version for [%s] to db failed" % (update_info))
        return -1

    return 0

def update_component_status(component_ids,status=const.COMPONENT_STATUS_UPGRADING):

    ctx = context.instance()
    condition = {"component_id": component_ids}
    update_info = {"status": status}

    if not ctx.pg.base_update(dbconst.TB_COMPONENT_VERSION, condition, update_info):
        logger.error("update component version for [%s] to db failed" % (update_info))
        return -1

    return 0

def get_upgrade_packet_md5(update_component_uri):

    cmd = "md5sum %s | awk  '{print $1}'" % (update_component_uri)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return False

def get_upgrade_packet_size(update_component_uri):

    cmd = "stat %s | awk 'NR==2{print $2}'" % (update_component_uri)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return False

def refresh_component_type_file_share_tools_info(component_ids):

    ctx = context.instance()
    component_versions = ctx.pgm.get_component_versions(component_ids=component_ids)

    for component_id, component_version in component_versions.items():
        condition = {"component_id": component_id}
        new_filename = component_version.get("filename","").replace('.bin','.exe')
        new_update_component_uri = "/mnt/nasdata/qingcloud_file_share_tools/%s" %(new_filename)
        ret = get_upgrade_packet_md5(new_update_component_uri)
        if ret:
            new_upgrade_packet_md5 = ret
        else:
            new_upgrade_packet_md5 = component_version.get("upgrade_packet_md5")

        ret = get_upgrade_packet_size(new_update_component_uri)
        if ret:
            new_upgrade_packet_size = ret
        else:
            new_upgrade_packet_size = component_version.get("upgrade_packet_size")

        update_info = dict(
            filename=new_filename,
            upgrade_packet_md5=new_upgrade_packet_md5,
            upgrade_packet_size=int(new_upgrade_packet_size)
        )
        logger.debug("refresh_component_type_file_share_tools_info component_id == %s update_info == %s" %(component_id,update_info))
        if not ctx.pg.base_update(dbconst.TB_COMPONENT_VERSION, condition, update_info):
            logger.error("update component [%s] version for [%s] to db failed" % (component_id,update_info))
            return -1
    return 0

def refresh_component_type_tools_info(component_ids):

    ctx = context.instance()
    component_versions = ctx.pgm.get_component_versions(component_ids=component_ids)

    for component_id, component_version in component_versions.items():
        condition = {"component_id": component_id}
        new_filename = component_version.get("filename","").replace('.bin','.zip')
        new_update_component_uri = "/mnt/nasdata/qingcloud_guest_tools/%s" %(new_filename)
        ret = get_upgrade_packet_md5(new_update_component_uri)
        if ret:
            new_upgrade_packet_md5 = ret
        else:
            new_upgrade_packet_md5 = component_version.get("upgrade_packet_md5")

        ret = get_upgrade_packet_size(new_update_component_uri)
        if ret:
            new_upgrade_packet_size = ret
        else:
            new_upgrade_packet_size = component_version.get("upgrade_packet_size")

        update_info = dict(
            filename=new_filename,
            upgrade_packet_md5=new_upgrade_packet_md5,
            upgrade_packet_size=int(new_upgrade_packet_size)
        )
        logger.debug("refresh_component_type_tools_info component_id == %s update_info == %s" %(component_id,update_info))
        if not ctx.pg.base_update(dbconst.TB_COMPONENT_VERSION, condition, update_info):
            logger.error("update component [%s] version for [%s] to db failed" % (component_id,update_info))
            return -1
    return 0

def execute_server_component_upgrade(update_component_uri,filename,target_host):

    ctx = context.instance()
    hostname = get_hostname()
    zone_deploy = ctx.zone_deploy

    if zone_deploy == const.DEPLOY_TYPE_STANDARD:
        logger.info("upgrade standard desktop-server upgrade bin = %s" % (update_component_uri))
        if target_host != hostname:
            cmd = ('ssh -o StrictHostKeyChecking=no root@%s "chmod a+x %s && /bin/bash %s"' % (target_host, update_component_uri, update_component_uri))
            logger.info("cmd == %s" % (cmd))
            os.system("%s" %(cmd))
        else:
            cmd = ("chmod a+x %s && nohup /bin/bash %s &" % (update_component_uri, update_component_uri))
            logger.info("cmd == %s" % (cmd))
            os.system("%s" % (cmd))
            time.sleep(60)
    else:
        logger.info("upgrade express desktop-server upgrade bin = %s" % (update_component_uri))
        qingcloud_firstbox_ip=get_qingcloud_firstbox()
        os.system("scp -r %s root@%s:/opt" %(update_component_uri,qingcloud_firstbox_ip))
        os.system('nohup ssh -o StrictHostKeyChecking=no root@%s "chmod a+x /opt/%s && /bin/bash /opt/%s" &' % (qingcloud_firstbox_ip, filename, filename))
        time.sleep(50)

    return 0

def task_execute_server_component_upgrade(sender, component_id,filename,component_type,target_host):

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

    if component_type == const.COMPONENT_TYPE_CLIENT:
        update_component_uri = "%s/%s" %(const.COMPONENT_TYPE_CLIENT_DIR,filename)
        check_component_dir_exist(const.COMPONENT_TYPE_CLIENT_DIR,target_hostname)

    elif component_type == const.COMPONENT_TYPE_TOOLS:
        update_component_uri = "%s/%s" % (const.COMPONENT_TYPE_TOOLS_DIR, filename)
        check_component_dir_exist(const.COMPONENT_TYPE_TOOLS_DIR,target_hostname)

    elif component_type == const.COMPONENT_TYPE_SERVER:
        update_component_uri = "%s/%s" % (const.COMPONENT_TYPE_SERVER_DIR, filename)
        check_component_dir_exist(const.COMPONENT_TYPE_SERVER_DIR,target_hostname)

    else:
        logger.error("invalid component_type %s" % (component_type))
        return -1

    result = is_software_exist_localhost(update_component_uri)
    if result:
        ret = execute_server_component_upgrade(update_component_uri,filename,target_host)
        if ret < 0:
            logger.error("execute_server_component_upgrade failed")
            return -1

    return 0

def task_execute_client_component_upgrade(sender,req):

    rep = send_terminal_server_request(req)
    time.sleep(5)
    if rep is None:
        return -1
    ret = rep["ret_code"]
    if ret != 0:
        return -1

    return 0

def update_loadbalancer_desktop_service_management(sender):

    ctx = context.instance()
    req = {
           "type": "internal",
           "params": {
               "action": const.ACTION_VDI_REFRESH_DESKTOP_SERVICE_MANAGEMENT,
               "zone": sender["zone"]
                }
           }
    send_desktop_server_request(req)

    return None



