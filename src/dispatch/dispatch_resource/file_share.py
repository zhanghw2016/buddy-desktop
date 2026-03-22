import context
from log.logger import logger
import constants as const
import db.constants as dbconst
from utils.misc import get_current_time,exec_cmd,_exec_cmd,get_current_timestamp,redefine_format_timestamp
import time
from utils.id_tool import (
    get_uuid,
    UUID_TYPE_FILE_SHARE_GROUP_FILE,
    UUID_TYPE_FILE_SHARE_GROUP,
)
import api.file_share.file_share as APIFileShare
import resource_common as ResComm
import os
from utils.auth import get_base64_password
import chardet
from utils.misc import rLock
from utils.net import get_hostname,is_port_open
from common import get_target_host_list

g_number=const.FILE_SHARE_MAX_REFRESH_COUNT

def check_file_share_group_files(file_share_group_file_ids=None):

    ctx = context.instance()
    file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if not file_share_group_files:
        logger.error("file share group file %s no found" % file_share_group_file_ids)
        return -1

    return file_share_group_files

def check_file_share_services(file_share_service_ids=None):

    ctx = context.instance()
    file_share_services = ctx.pgm.get_file_share_services(file_share_service_ids=file_share_service_ids)
    if not file_share_services:
        logger.error("file share service %s no found" % file_share_service_ids)
        return -1

    return file_share_services

def task_upload_file_shares(sender, file_share_group_file_id,file_share_group_file_name,file_share_group_dn):

    ctx = context.instance()
    source_path = "%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, file_share_group_file_name)
    path = APIFileShare.dn_to_path(file_share_group_dn)
    destination_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, path)

    time.sleep(3)
    upload = False
    retries = 10
    while retries > 0:
        # check if the file exists on remote file_share_server /mnt/nasdata/xxxx
        ret = APIFileShare.check_uploaded_file_exist(ctx,source_path)
        if ret:
            ret = APIFileShare.mv_file_share_dir(ctx,source_path, destination_path)
            if ret:
                upload = True
                break

        time.sleep(3)
        retries -= 1

    if not upload:
        logger.error("mv [%s] to [%s] failed" % (source_path, destination_path))
        return -1
    else:
        logger.info("mv [%s] to [%s] successfully" % (source_path, destination_path))
        return 0

def check_new_file_share_group_file(new_file_share_group_dn,new_file_share_group_file_dn, new_file_share_group_id,file_share_group_file_name,file_share_group_file_size):

    new_file_share_group_file = {}
    new_file_share_group_file["file_share_group_dn"] = new_file_share_group_dn
    new_file_share_group_file["file_share_group_file_dn"] = new_file_share_group_file_dn
    new_file_share_group_file["file_share_group_id"] = new_file_share_group_id
    new_file_share_group_file["file_share_group_file_name"] = file_share_group_file_name
    new_file_share_group_file["file_share_group_file_size"] = file_share_group_file_size
    new_file_share_group_file["create_time"] = get_current_time()

    return new_file_share_group_file

def add_file_share_group_file_dn(new_file_share_group_files):

    ctx = context.instance()
    for _,file_share_group_file in new_file_share_group_files.items():

        file_share_group_file_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP_FILE, ctx.checker)
        update_info = dict(
            file_share_group_file_id=file_share_group_file_id
        )
        file_share_group_file.update(update_info)
        if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file):
            logger.error("insert newly created file share group file for [%s] to db failed" % (update_info))
            return -1

    return 0

def delete_file_share_group_file_dn(delete_file_share_group_files):

    ctx = context.instance()
    if delete_file_share_group_files and not isinstance(delete_file_share_group_files, list):
        delete_file_share_group_files = [delete_file_share_group_files]

    for file_share_group_file_id in delete_file_share_group_files:
        # Delete file records in file share
        conditions = {"file_share_group_file_id": file_share_group_file_id}
        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions)
        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, conditions)

    return 0

def create_new_file_share_group_file_record(file_share_group_file,new_file_share_group_dn,file_save_method='',repeat_file_ids=[]):

    ctx = context.instance()
    new_file_share_group_files = {}
    file_share_group_file_id = file_share_group_file["file_share_group_file_id"]
    file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
    file_share_group_file_size = file_share_group_file["file_share_group_file_size"]
    if file_share_group_file_id in repeat_file_ids and file_save_method != const.SOURCE_FILE_SAVE_METHOD_OVERWRITE:
        file_share_group_file_name = APIFileShare.rename_filename(filename=file_share_group_file_name,suffix_string="Duplicate_At")
    new_file_share_group_file_dn = "cn=%s,%s" % (file_share_group_file_name, new_file_share_group_dn)
    new_file_share_group_id = ctx.pgm.get_file_share_group_id(file_share_group_dn=new_file_share_group_dn,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if not new_file_share_group_id:
        logger.error("no found new_file_share_group_dn %s" % (new_file_share_group_dn))
        return -1

    # create new destination file_share_group_file record
    ret = check_new_file_share_group_file(new_file_share_group_dn,new_file_share_group_file_dn,new_file_share_group_id,file_share_group_file_name,file_share_group_file_size)
    if ret:
        new_file_share_group_files[new_file_share_group_file_dn] = ret

    if new_file_share_group_files:
        ret = add_file_share_group_file_dn(new_file_share_group_files)
        if ret < 0:
            return -1

    return new_file_share_group_file_dn

def delete_old_file_share_group_file_record(file_share_group_file_id,file_share_group_file_name,new_file_share_group_dn,repeat_file_ids=[]):

    ctx = context.instance()
    delete_file_share_group_files = []
    if file_share_group_file_id in repeat_file_ids:
        ret = ctx.pgm.get_file_share_group_file_id(file_share_group_file_name=file_share_group_file_name,
                                                   file_share_group_dn=new_file_share_group_dn,
                                                   trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
        if ret:
            if ret not in delete_file_share_group_files:
                delete_file_share_group_files.append(ret)

    if delete_file_share_group_files:
        ret = delete_file_share_group_file_dn(delete_file_share_group_files)
        if ret < 0:
            return -1

    return 0

def change_file_in_file_share_group_execute_comand(file_share_group_file_dn,new_file_share_group_file_dn,change_type):

    ctx = context.instance()
    file_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, APIFileShare.dn_to_path(file_share_group_file_dn))
    ret = APIFileShare.check_uploaded_file_exist(ctx, file_path)
    if not ret:
        ret = ctx.pgm.get_file_share_group_files(file_share_group_file_dn=file_share_group_file_dn)
        if ret:
            delete_file_share_group_file_id = ret.keys()[0]
            if delete_file_share_group_file_id:
                ret = delete_file_share_group_file_dn(delete_file_share_group_file_id)
                if ret < 0:
                    return -1
        return 0

    new_file_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, APIFileShare.dn_to_path(new_file_share_group_file_dn))
    if const.FILE_SHARE_CHANGE_TYPE_MOVE == change_type:
        ret = APIFileShare.mv_file_share_dir(ctx,file_path, new_file_path)
        if not ret:
            return -1
    elif const.FILE_SHARE_CHANGE_TYPE_COPY == change_type:
        ret = APIFileShare.cp_file_share_dir(ctx,file_path, new_file_path)
        if not ret:
            return -1
    else:
        logger.error("change_type %s is invalid" %(change_type))
        return -1

    return 0

def task_change_file_in_file_share_group(sender,file_share_group_file_id,file_share_group_file, new_file_share_group_dn,change_type,file_save_method='',repeat_file_ids=[]):

    ctx = context.instance()
    file_share_group_file_dn = file_share_group_file['file_share_group_file_dn']
    file_share_group_file_name = file_share_group_file['file_share_group_file_name']
    if not file_save_method:
        ret = create_new_file_share_group_file_record(file_share_group_file, new_file_share_group_dn, file_save_method,repeat_file_ids)
        if ret < 0:
            return -1
        new_file_share_group_file_dn = ret

        ret = change_file_in_file_share_group_execute_comand(file_share_group_file_dn, new_file_share_group_file_dn,change_type)
        if ret < 0:
            return -1

    elif const.SOURCE_FILE_SAVE_METHOD_SAVE == file_save_method:
        ret = create_new_file_share_group_file_record(file_share_group_file, new_file_share_group_dn, file_save_method,repeat_file_ids)
        if ret < 0:
            return -1
        new_file_share_group_file_dn = ret

        ret = change_file_in_file_share_group_execute_comand(file_share_group_file_dn, new_file_share_group_file_dn,change_type)
        if ret < 0:
            return -1

    elif const.SOURCE_FILE_SAVE_METHOD_OVERWRITE == file_save_method:
        ret = delete_old_file_share_group_file_record(file_share_group_file_id, file_share_group_file_name,new_file_share_group_dn, repeat_file_ids)
        if ret < 0:
            return -1

        ret = create_new_file_share_group_file_record(file_share_group_file, new_file_share_group_dn,file_save_method,repeat_file_ids)
        if ret < 0:
            return -1
        new_file_share_group_file_dn = ret

        ret = change_file_in_file_share_group_execute_comand(file_share_group_file_dn, new_file_share_group_file_dn,change_type)
        if ret < 0:
            return -1
    else:
        logger.error("file_save_method  %s is invalid" %(file_save_method))
        return -1

    return 0

def task_resource_clone_instances(sender, desktop_server_instance_id,network_id,private_ip=None):

    ctx = context.instance()
    ret = ctx.res.resource_clone_instances(sender["zone"], resource_id=desktop_server_instance_id,vxnet_id=network_id,private_ip=private_ip)
    if not ret:
        logger.error("resource clone instance fail %s " % desktop_server_instance_id)
        return -1
    instance_id = ret

    return instance_id

def task_resource_modify_instance_attributes(sender, instance_id,instance_name):

    ctx = context.instance()
    ret = ctx.res.resource_modify_instance_attributes(sender["zone"], instance_id=instance_id,config={"instance_name":instance_name})
    if not ret:
        logger.error("resource modify_instance_attributes fail %s " % instance_id)
        return -1
    instance_id = ret

    return instance_id

def task_resource_describe_s2_accounts(sender, file_share_service_id,search_word):

    ctx = context.instance()
    ret = ctx.res.resource_describe_s2_accounts(sender["zone"], search_word=search_word)
    if not ret:
        return None
    s2_account = ret

    return s2_account

def task_resource_describe_s2_groups(sender, file_share_service_id,group_types):

    ctx = context.instance()
    ret = ctx.res.resource_describe_s2_groups(sender["zone"], group_types=group_types)
    if not ret:
        logger.error("resource describe_s2_groups fail %s " % file_share_service_id)
        return -1
    s2_group_sets = ret

    for s2_group_id,s2_group in s2_group_sets.items():
        if s2_group["is_default"] == 1:
            s2_group_id = s2_group_id
            break

    return s2_group_id

def task_resource_create_s2_account(sender, file_share_service_id,account_name,account_type,nfs_ipaddr,s2_group,opt_parameters,s2_groups):

    ctx = context.instance()
    ret = ctx.res.resource_create_s2_account(sender["zone"], account_name=account_name,account_type=account_type,nfs_ipaddr=nfs_ipaddr,
                                             s2_group=s2_group,opt_parameters=opt_parameters,s2_groups=s2_groups)
    if not ret:
        logger.error("resource create_s2_account fail %s " % file_share_service_id)
        return -1
    s2_account_id = ret

    return s2_account_id

def task_resource_update_s2_servers(sender, file_share_service_id,s2_servers):

    ctx = context.instance()
    ret = ctx.res.resource_update_s2_servers(sender["zone"], s2_servers=s2_servers)
    logger.info("resource_update_s2_servers ret == %s" % (ret))
    if not ret:
        logger.error("resource update_s2_servers fail %s " % file_share_service_id)
        return -1
    s2_server_id = ret

    return s2_server_id

def task_resource_poweroff_s2_servers(sender, file_share_service_id,s2_servers):

    ctx = context.instance()
    ret = ctx.res.resource_poweroff_s2_servers(sender["zone"], s2_servers=s2_servers)
    logger.info("resource_poweroff_s2_servers ret == %s" %(ret))
    if not ret:
        logger.error("resource poweroff_s2_servers fail %s " % s2_servers)
        return -1
    s2_server_id = ret

    return s2_server_id

def task_resource_poweron_s2_servers(sender, file_share_service_id,s2_servers):

    ctx = context.instance()
    ret = ctx.res.resource_poweron_s2_servers(sender["zone"], s2_servers=s2_servers)
    logger.info("resource_poweron_s2_servers ret == %s" % (ret))
    if not ret:
        logger.error("resource poweron_s2_servers fail %s " % s2_servers)
        return -1
    s2_server_id = ret

    return s2_server_id

def task_resource_terminate_instances(sender, instance_id):

    ctx = context.instance()
    ret = ctx.res.resource_terminate_instances(sender["zone"], resource={"instance_id":instance_id},platform=const.PLATFORM_TYPE_QINGCLOUD)
    if not ret:
        logger.error("resource_terminate_instances fail %s " % instance_id)
        return -1
    instance_id = ret

    return instance_id

def check_instance_private_ips(sender,instance_id=None):

    ctx = context.instance()
    instance_private_ips = []
    body = {}
    offset = 0
    limit = const.MAX_LIMIT_PARAM

    body["offset"] = offset
    body["limit"] = limit
    body["search_word"] = instance_id

    ret = ctx.res.resource_describe_instances_by_search_word(sender["zone"], body)
    if ret:
        # add private_ip
        for _, instance in ret.items():
            vxnets = instance.get("vxnets")
            if vxnets:
                vxnet = vxnets[0]
                if vxnet:
                    private_ip = vxnet.get("private_ip", '')
                    if  private_ip != '':
                        instance_private_ips.append(private_ip)

    return instance_private_ips

def update_file_share_service(sender,file_share_service_id,file_share_service_instance_id=None,vnas_private_ip=None,vnas_id=None):

    ctx = context.instance()
    if not file_share_service_instance_id:
        logger.error("no found file_share_service_instance")
        return -1

    private_ip_exist = False
    retries = 100
    instance_private_ips = []
    while retries > 0:
        # check instance private_ip exist
        ret = check_instance_private_ips(sender,instance_id=file_share_service_instance_id)
        if len(ret) >= 1:
            instance_private_ips = ret
            private_ip_exist = True
            break

        time.sleep(3)
        retries -= 1

    if not private_ip_exist:
        logger.error("file_share_service_instance %s private_ips %s not exist" % (file_share_service_instance_id,instance_private_ips))
        return -1

    file_share_service_info = {
                    "file_share_service_instance_id": file_share_service_instance_id,
                    "private_ip":instance_private_ips[0],
                    "vnas_private_ip": vnas_private_ip if vnas_private_ip else '',
                    "vnas_id": vnas_id if vnas_id else '',
                    "status_time": get_current_time()
                    }

    if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_SERVICE, {file_share_service_id: file_share_service_info}):
        logger.error("create file share service update fail: %s, %s" % (file_share_service_id, file_share_service_info))
        return -1

    return 0

def update_loaded_file_share_service(sender,file_share_service_id,file_share_service_instance_id=None,vnas_private_ip=None,vnas_id=None):

    ctx = context.instance()
    if not file_share_service_instance_id:
        logger.error("no found file_share_service_instance")
        return -1

    private_ip_exist = False
    retries = 100
    instance_private_ips = []
    while retries > 0:
        # check instance private_ip exist
        ret = check_instance_private_ips(sender,instance_id=file_share_service_instance_id)
        if len(ret) >= 1:
            instance_private_ips = ret
            private_ip_exist = True
            break

        time.sleep(3)
        retries -= 1

    if not private_ip_exist:
        logger.error("file_share_service_instance %s private_ips %s not exist" % (file_share_service_instance_id,instance_private_ips))
        return -1

    file_share_service_info = {
                    "file_share_service_instance_id": file_share_service_instance_id,
                    "loaded_clone_instance_ip":instance_private_ips[0],
                    "vnas_private_ip": vnas_private_ip if vnas_private_ip else '',
                    "vnas_id": vnas_id if vnas_id else '',
                    "status_time": get_current_time()
                    }

    if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_SERVICE, {file_share_service_id: file_share_service_info}):
        logger.error("create file share service update fail: %s, %s" % (file_share_service_id, file_share_service_info))
        return -1

    return 0

def active_file_share_service_status(file_share_service_id):

    ctx = context.instance()
    file_share_service_info = {
                    "status": const.FILE_SHARE_SERVICE_STATUS_ACTIVE,
                    "status_time": get_current_time()
                    }

    if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_SERVICE, {file_share_service_id: file_share_service_info}):
        logger.error("create file share service update fail: %s, %s" % (file_share_service_id, file_share_service_info))
        return -1

    return 0

def get_file_share_service_instance_class(sender,instance_id):

    ctx = context.instance()
    ret = ctx.res.resource_describe_instances(sender["zone"], instance_ids=instance_id)
    if not ret:
        logger.error("resource describe instance fail %s " % instance_id)
        return -1
    instances = ret
    for instance_id,instance in instances.items():
        instance_class = instance.get("instance_class")

    return instance_class

def task_resource_create_s2_server(sender,vxnet_id,s2_server_name,s2_class):

    ctx = context.instance()
    ret = ctx.res.resource_create_s2_server(sender["zone"], vxnet_id=vxnet_id,s2_server_name=s2_server_name,s2_class=s2_class)
    if not ret:
        logger.error("resource create_s2_server fail %s" % vxnet_id)
        return -1
    s2_server = ret

    return s2_server

def task_resource_create_volume(sender,size,volume_type,volume_name):

    ctx = context.instance()
    ret = ctx.res.resource_create_volume(sender["zone"], size=size, volume_type=volume_type, volume_name=volume_name)
    if not ret:
        logger.error("resource create_volume fail %s" % volume_name)
        return -1
    volumes = ret

    return volumes

def task_resource_create_s2_shared_target(sender,vxnet,s2_server_id,target_type,export_name_nfs,export_name,volumes):

    ctx = context.instance()
    ret = ctx.res.resource_create_s2_shared_target(sender["zone"], vxnet=vxnet, s2_server_id=s2_server_id,
                                                   target_type=target_type,export_name_nfs=export_name_nfs,
                                                   export_name=export_name,volumes=volumes)
    if not ret:
        logger.error("resource create_s2_shared_target fail")
        return -1
    s2_shared_target = ret

    return s2_shared_target

def task_resource_describe_s2servers(sender,s2_servers):

    ctx = context.instance()
    ret = ctx.res.resource_describe_s2servers(sender["zone"], service_id=s2_servers)
    if not ret:
        logger.error("resource describe_s2servers fail %s" % s2_servers)
        return -1
    s2_server_sets = ret

    return s2_server_sets

def task_wait_create_file_share_service_done(sender,
                                             file_share_service_id,
                                             network_id,
                                             desktop_server_instance_id,
                                             private_ip,
                                             file_share_service_name,
                                             vnas_disk_size,
                                             vnas_id,
                                             limit_rate,
                                             limit_conn,
                                             fuser,
                                             fpw):

    ctx = context.instance()
    with ResComm.transition_status(dbconst.TB_FILE_SHARE_SERVICE, file_share_service_id, const.FILE_SHARE_SERVICE_STATUS_CREATING):

        ret = task_resource_clone_instances(sender, desktop_server_instance_id,network_id,private_ip)
        if ret < 0:
            logger.error("Task clone instances fail:%s " % (file_share_service_id))
            return -1
        instance_id = ret

        #change instance_name
        ret = task_resource_modify_instance_attributes(sender, instance_id,instance_name=file_share_service_name)
        if ret < 0:
            logger.error("Task resource_modify_instance_attributes fail:%s " % (instance_id))
            return -1
        instance_id = ret

        ret = update_file_share_service(sender,file_share_service_id,file_share_service_instance_id=instance_id)
        if ret < 0:
            logger.error("update_file_share_service fail %s " % file_share_service_id)
            return -1

        #Check the file_share_service HOST IP supports accounts that can access services
        private_ip = ctx.pgm.get_file_share_service_private_ip(file_share_service_ids=file_share_service_id)
        logger.info("file_share_service host private_ip == %s" %(private_ip))
        if not private_ip:
            logger.error("file_share_service %s no found private_ip" % file_share_service_id)
            return -1

        ret = task_resource_describe_s2_accounts(sender, file_share_service_id,search_word=private_ip)
        s2_account = ret
        exist_s2_account = False
        if s2_account:
            for account_id,s2account in s2_account.items():
                nfs_ipaddr = s2account.get("nfs_ipaddr")
                if private_ip == nfs_ipaddr:
                    logger.info("private_ip %s in support accounts" %(private_ip))
                    exist_s2_account = True
                    break
        logger.info("exist_s2_account == %s" %(exist_s2_account))
        if not exist_s2_account:

            ret = task_resource_describe_s2_groups(sender, file_share_service_id,group_types=['NFS_GROUP'])
            logger.info("task_resource_describe_s2_groups ret == %s" %(ret))
            if ret < 0:
                logger.error("Task describe_s2_groups fail:%s " % (file_share_service_id))
                return -1
            s2_group_id = ret

            account_name = 'file-share-account'
            account_type = 'NFS'
            nfs_ipaddr = private_ip
            s2_group = s2_group_id
            opt_parameters = 'squash=no_root_squash,sync=sync'
            s2_groups = [{"group_id":s2_group_id,"rw_flag":"rw"}]
            ret = task_resource_create_s2_account(sender, file_share_service_id,account_name,account_type,nfs_ipaddr,s2_group,opt_parameters,s2_groups)
            if ret < 0:
                logger.error("Task create_s2_account fail:%s " % (file_share_service_id))
                return -1
            s2_account_id = ret

        if not vnas_id:
            # Create a vNAS shared storage server
            current_time = time.strftime("%Y-%m-%d", time.localtime())
            s2_server_name = 'File Share vNAS %s' % (current_time)

            # get the s2_class corresponding to the instance class
            instance_class = get_file_share_service_instance_class(sender,instance_id)
            s2_class = const.INSTANCE_CLASS_S2_CLASS_MAP[instance_class]
            logger.info("instance_class == %s" % (instance_class))
            logger.info("s2_class == %s" % (s2_class))
            # get desktop_server_instance vxnet_id
            s2_server_vxnet_id = get_desktop_server_instance_vxnet_id()
            if not s2_server_vxnet_id:
                logger.error("not get desktop_sever_instance vxnet_id in /opt/instance_vxnet_id_conf")
                return -1
            ret = task_resource_create_s2_server(sender,vxnet_id=s2_server_vxnet_id,s2_server_name=s2_server_name,s2_class=s2_class)
            if ret < 0:
                logger.error("Task resource_create_s2_server fail")
                return -1
            s2_server_id = ret

            # attach tags to vNAS
            tag_name = 'File Share vNAS %s' % (redefine_format_timestamp(get_current_timestamp()))
            color = '#FF615A'
            ret = attach_tags_to_resource(sender, color=color, tag_name=tag_name, resource_type='s2_server',
                                          resource_id=s2_server_id)
            if ret < 0:
                logger.error("Task attach_tags_to_resource fail")
                return -1

            # create_volume
            # get the volume_type corresponding to the instance class
            volume_type = const.INSTANCE_CLASS_VOLUME_TYPE_MAP[instance_class]
            logger.info("instance_class == %s" % (instance_class))
            logger.info("volume_type == %s" % (volume_type))
            ret = task_resource_create_volume(sender, size=vnas_disk_size, volume_type=volume_type,
                                              volume_name='vdi-portal-vnas-disk')
            if ret < 0:
                logger.error("Task create_volume fail")
                return -1
            volume_id = ret
            if volume_id and not isinstance(volume_id, list):
                volume_id = [volume_id]

            # CreateS2SharedTarget
            ret = task_resource_create_s2_shared_target(sender, vxnet=s2_server_vxnet_id, s2_server_id=s2_server_id,
                                                        target_type='NFS', export_name_nfs='nas',
                                                        export_name='/mnt/nas', volumes=volume_id)
            if ret < 0:
                logger.error("Task create_s2_shared_target fail")
                return -1

            # attach tags
            tag_name = 'File Share vNAS Storage Hard Disk %s' % (redefine_format_timestamp(get_current_timestamp()))
            color = '#FF615A'
            ret = attach_tags_to_resource(sender, color=color, tag_name=tag_name, resource_type='volume',resource_id=volume_id[0])
            if ret < 0:
                logger.error("Task attach_tags_to_resource fail")
                return -1

        else:
            s2_server_id = vnas_id

        # get vnas_private_ip s2_server_name status
        ret = task_resource_describe_s2servers(sender,s2_servers=s2_server_id)
        if ret < 0:
            logger.error("Task resource_describe_s2servers fail")
            return -1
        s2_server_sets = ret
        for s2_server_id, s2_server in s2_server_sets.items():
            vnas_private_ip = s2_server.get("private_ip")
            s2_server_name = s2_server.get("s2_server_name")
            s2_server_status = s2_server.get("status")

        ret = task_resource_update_s2_servers(sender, file_share_service_id,s2_servers=s2_server_id)
        if ret < 0:
            logger.error("Task resource_update_s2_servers fail:%s " % (s2_server_id))
            ret = task_resource_poweroff_s2_servers(sender, file_share_service_id, s2_servers=s2_server_id)
            if ret < 0:
                logger.error("Task resource_poweroff_s2_servers fail:%s " % (s2_server_id))
                return -1

            ret = task_resource_poweron_s2_servers(sender, file_share_service_id, s2_servers=s2_server_id)
            if ret < 0:
                logger.error("Task resource_poweron_s2_servers fail:%s " % (s2_server_id))
                return -1

        # attach tags
        tag_name = 'File Share Server Instance %s' % (redefine_format_timestamp(get_current_timestamp()))
        color = '#FF615A'
        ret = attach_tags_to_resource(sender,color=color,tag_name=tag_name,resource_type='instance',resource_id=instance_id)
        if ret < 0:
            logger.error("Task attach_tags_to_resource fail")
            return -1

        ret = update_file_share_service(sender,file_share_service_id,file_share_service_instance_id=instance_id,vnas_private_ip=vnas_private_ip,vnas_id=s2_server_id)
        if ret < 0:
            logger.error("update_file_share_service fail %s " % file_share_service_id)
            return -1

        ret = register_file_share_service_vnas(vnas_id=s2_server_id,vnas_name=s2_server_name,vnas_private_ip=vnas_private_ip,status=s2_server_status)
        if ret < 0:
            logger.error("register_file_share_service_vnas fail %s " % s2_server_id)
            return -1

        # ret = register_desktop_server_manangement_vnas(vnas_id=s2_server_id,vnas_name=s2_server_name,vnas_private_ip=vnas_private_ip,status=s2_server_status)
        # if ret < 0:
        #     logger.error("register_desktop_server_manangement_vnas fail %s " % s2_server_id)
        #     return -1

        # desktop_server_host_list = APIFileShare.get_target_host_list(ctx)
        # umount_nfs_from_desktop_server_instance(desktop_server_host_list)
        ret = configure_file_share_service_instance(remote_host=private_ip,vnas_private_ip=vnas_private_ip,limit_rate=limit_rate,limit_conn=limit_conn,fuser=fuser,fpw=fpw)
        if not ret:
            return -1

        return 0

def task_wait_load_file_share_service_done(sender,
                                             file_share_service_id,
                                             network_id,
                                             desktop_server_instance_id,
                                             file_share_service_name,
                                             vnas_disk_size,
                                             vnas_id,
                                             limit_rate,
                                             limit_conn,
                                             fuser,
                                             fpw):

    ctx = context.instance()
    with ResComm.transition_status(dbconst.TB_FILE_SHARE_SERVICE, file_share_service_id, const.FILE_SHARE_SERVICE_STATUS_IMPORTING):

        ret = task_resource_clone_instances(sender, desktop_server_instance_id,network_id,None)
        if ret < 0:
            logger.error("Task clone instances fail:%s " % (file_share_service_id))
            return -1
        instance_id = ret

        #change instance_name
        ret = task_resource_modify_instance_attributes(sender, instance_id,instance_name=file_share_service_name)
        if ret < 0:
            logger.error("Task resource_modify_instance_attributes fail:%s " % (instance_id))
            return -1
        instance_id = ret

        ret = update_loaded_file_share_service(sender,file_share_service_id,file_share_service_instance_id=instance_id)
        if ret < 0:
            logger.error("update_loaded_file_share_service fail %s " % file_share_service_id)
            return -1

        #Check the file_share_service HOST IP supports accounts that can access services
        loaded_clone_instance_ip = ctx.pgm.get_file_share_service_loaded_clone_instance_ip(file_share_service_ids=file_share_service_id)
        logger.info("get_file_share_service_loaded_clone_instance_ip host loaded_clone_instance_ip == %s" %(loaded_clone_instance_ip))
        if not loaded_clone_instance_ip:
            logger.error("file_share_service %s no found loaded_clone_instance_ip" % file_share_service_id)
            return -1

        ret = task_resource_describe_s2_accounts(sender, file_share_service_id,search_word=loaded_clone_instance_ip)
        s2_account = ret
        exist_s2_account = False
        if s2_account:
            for account_id,s2account in s2_account.items():
                nfs_ipaddr = s2account.get("nfs_ipaddr")
                if loaded_clone_instance_ip == nfs_ipaddr:
                    logger.info("loaded_clone_instance_ip %s in support accounts" %(loaded_clone_instance_ip))
                    exist_s2_account = True
                    break
        logger.info("exist_s2_account == %s" %(exist_s2_account))
        if not exist_s2_account:

            ret = task_resource_describe_s2_groups(sender, file_share_service_id,group_types=['NFS_GROUP'])
            logger.info("task_resource_describe_s2_groups ret == %s" %(ret))
            if ret < 0:
                logger.error("Task describe_s2_groups fail:%s " % (file_share_service_id))
                return -1
            s2_group_id = ret

            account_name = 'file-share-account'
            account_type = 'NFS'
            nfs_ipaddr = loaded_clone_instance_ip
            s2_group = s2_group_id
            opt_parameters = 'squash=no_root_squash,sync=sync'
            s2_groups = [{"group_id":s2_group_id,"rw_flag":"rw"}]
            ret = task_resource_create_s2_account(sender, file_share_service_id,account_name,account_type,nfs_ipaddr,s2_group,opt_parameters,s2_groups)
            if ret < 0:
                logger.error("Task create_s2_account fail:%s " % (file_share_service_id))
                return -1
            s2_account_id = ret

        if not vnas_id:
            # Create a vNAS shared storage server
            current_time = time.strftime("%Y-%m-%d", time.localtime())
            s2_server_name = 'File Share vNAS %s' % (current_time)

            # get the s2_class corresponding to the instance class
            instance_class = get_file_share_service_instance_class(sender,instance_id)
            s2_class = const.INSTANCE_CLASS_S2_CLASS_MAP[instance_class]
            print("instance_class == %s" % (instance_class))
            print("s2_class == %s" % (s2_class))
            # get desktop_server_instance vxnet_id
            s2_server_vxnet_id = get_desktop_server_instance_vxnet_id()
            if not s2_server_vxnet_id:
                logger.error("not get desktop_sever_instance vxnet_id in /opt/instance_vxnet_id_conf")
                return -1
            ret = task_resource_create_s2_server(sender,vxnet_id=s2_server_vxnet_id,s2_server_name=s2_server_name,s2_class=s2_class)
            if ret < 0:
                logger.error("Task resource_create_s2_server fail")
                return -1
            s2_server_id = ret

            # attach tags to vNAS
            tag_name = 'File Share vNAS %s' % (redefine_format_timestamp(get_current_timestamp()))
            color = '#FF615A'
            ret = attach_tags_to_resource(sender, color=color, tag_name=tag_name, resource_type='s2_server',
                                          resource_id=s2_server_id)
            if ret < 0:
                logger.error("Task attach_tags_to_resource fail")
                return -1

            # create_volume
            # get the volume_type corresponding to the instance class
            volume_type = const.INSTANCE_CLASS_VOLUME_TYPE_MAP[instance_class]
            logger.info("instance_class == %s" % (instance_class))
            logger.info("volume_type == %s" % (volume_type))
            ret = task_resource_create_volume(sender, size=vnas_disk_size, volume_type=volume_type,
                                              volume_name='vdi-portal-vnas-disk')
            if ret < 0:
                logger.error("Task create_volume fail")
                return -1
            volume_id = ret
            if volume_id and not isinstance(volume_id, list):
                volume_id = [volume_id]

            # CreateS2SharedTarget
            ret = task_resource_create_s2_shared_target(sender, vxnet=s2_server_vxnet_id, s2_server_id=s2_server_id,
                                                        target_type='NFS', export_name_nfs='nas',
                                                        export_name='/mnt/nas', volumes=volume_id)
            if ret < 0:
                logger.error("Task create_s2_shared_target fail")
                return -1

            # attach tags
            tag_name = 'File Share vNAS Storage Hard Disk %s' % (redefine_format_timestamp(get_current_timestamp()))
            color = '#FF615A'
            ret = attach_tags_to_resource(sender, color=color, tag_name=tag_name, resource_type='volume',resource_id=volume_id[0])
            if ret < 0:
                logger.error("Task attach_tags_to_resource fail")
                return -1

        else:
            s2_server_id = vnas_id

        # get vnas_private_ip s2_server_name status
        ret = task_resource_describe_s2servers(sender,s2_servers=s2_server_id)
        if ret < 0:
            logger.error("Task resource_describe_s2servers fail")
            return -1
        s2_server_sets = ret
        for s2_server_id, s2_server in s2_server_sets.items():
            vnas_private_ip = s2_server.get("private_ip")
            s2_server_name = s2_server.get("s2_server_name")
            s2_server_status = s2_server.get("status")

        ret = task_resource_update_s2_servers(sender, file_share_service_id,s2_servers=s2_server_id)
        if ret < 0:
            logger.error("Task resource_update_s2_servers fail:%s " % (file_share_service_id))
            return -1

        # attach tags
        tag_name = 'File Share Server Instance %s' % (redefine_format_timestamp(get_current_timestamp()))
        color = '#FF615A'
        ret = attach_tags_to_resource(sender,color=color,tag_name=tag_name,resource_type='instance',resource_id=instance_id)
        if ret < 0:
            logger.error("Task attach_tags_to_resource fail")
            return -1

        ret = update_loaded_file_share_service(sender,file_share_service_id,file_share_service_instance_id=instance_id,vnas_private_ip=vnas_private_ip,vnas_id=s2_server_id)
        if ret < 0:
            logger.error("update_loaded_file_share_service fail %s " % file_share_service_id)
            return -1

        ret = register_file_share_service_vnas(vnas_id=s2_server_id,vnas_name=s2_server_name,vnas_private_ip=vnas_private_ip,status=s2_server_status)
        if ret < 0:
            logger.error("register_file_share_service_vnas fail %s " % s2_server_id)
            return -1

        # ret = register_desktop_server_manangement_vnas(vnas_id=s2_server_id,vnas_name=s2_server_name,vnas_private_ip=vnas_private_ip,status=s2_server_status)
        # if ret < 0:
        #     logger.error("register_desktop_server_manangement_vnas fail %s " % s2_server_id)
        #     return -1

        # desktop_server_host_list = APIFileShare.get_target_host_list(ctx)
        # umount_nfs_from_desktop_server_instance(desktop_server_host_list)
        ret = configure_loaded_file_share_service_instance(remote_host=loaded_clone_instance_ip,vnas_private_ip=vnas_private_ip,limit_rate=limit_rate,limit_conn=limit_conn,fuser=fuser,fpw=fpw)
        if not ret:
            return -1

        # task_refresh_loaded_file_share_service
        global g_number
        g_number = const.FILE_SHARE_MAX_REFRESH_COUNT
        ret = task_refresh_loaded_file_share_service(sender,
                                                     file_share_service_id=file_share_service_id,
                                                     base_dn=const.FILE_SHARE_GROUP_ROOT_BASE_DN,
                                                     root_folder=const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR
                                                     )
        if ret < 0:
            logger.error("task_refresh_loaded_file_share_service fail:%s " % (file_share_service_id))
            return -1

        ret = task_refresh_loaded_file_share_service_local_file(sender, file_share_service_id=file_share_service_id)
        if ret < 0:
            logger.error("task_refresh_loaded_file_share_service_local_file fail:%s " % (file_share_service_id))
            return -1

        return 0

def umount_nfs_from_desktop_server_instance(desktop_server_host_list):

    for desktop_server_host in desktop_server_host_list:
        unmount_nfs_cmd(desktop_server_host)
        sed_nfs_cmd(desktop_server_host)

    return None

def cancel_url_prefix_cmd(remote_host):
    cmd = "/pitrix/conf/configure_vdi_portal.sh -f N -c y"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def replace_urls_cmd(remote_host):

    cmd = "cp -fr /pitrix/conf/urls.py /pitrix/lib/vdi-portal/server/mysite/urls.py"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def configure_django_cmd(remote_host):
    cmd = "sed -i '/CsrfViewMiddlewar/'d  /pitrix/conf/vdi_portal_settings.py"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def configure_nginx_cmd(remote_host):
    cmd = "cd /etc/nginx/sites-enabled && rm -fr * && ln -s /etc/nginx/sites-available/vdi-portal-cross-domain vdi-portal-cross-domain"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def update_django_port_cmd(remote_host,nginx_default_server_listen):

    cmd = "sed -i 's/^PORT.*=.*/PORT = %s/g'  /pitrix/conf/vdi_portal_settings.py" % (nginx_default_server_listen)
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def update_nginx_default_server_listen_cmd(remote_host,nginx_default_server_listen):

    cmd = "sed -i 's/listen.*;$/listen %s default_server;/g'  /etc/nginx/sites-available/vdi-portal-cross-domain" % (nginx_default_server_listen)
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def restart_nginx_cmd(remote_host):
    cmd = "/etc/init.d/nginx restart"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def restart_apache2_cmd(remote_host):
    cmd = "/etc/init.d/apache2 restart"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def configure_vsftp_cmd(remote_host,ftp_username,ftp_password):

    cmd = "/pitrix/conf/configure_vsftp/configure_vsftp.sh -m virtual -u %s -w %s" %(ftp_username,ftp_password)
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def remove_pitrix_desktop_agent(remote_host):

    cmd = "dpkg -P pitrix-desktop-agent"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    if ret != None and ret[0] == 0:
        return True
    return False

def configure_file_share_service_instance(remote_host=None,vnas_private_ip=None,limit_rate=1,limit_conn=5,fuser=None,fpw=None):
    ctx = context.instance()
    nginx_default_server_listen = APIFileShare.check_nginx_default_server_listen(ctx)
    logger.info("nginx_default_server_listen == %s" %(nginx_default_server_listen))

    unmount_nfs_cmd(remote_host)
    sed_nfs_cmd(remote_host)
    echo_fstab_nfs_cmd(remote_host,vnas_private_ip)
    mount_nfs_cmd(remote_host, vnas_private_ip)
    cancel_url_prefix_cmd(remote_host)
    replace_urls_cmd(remote_host)
    configure_django_cmd(remote_host)
    configure_nginx_cmd(remote_host)
    update_django_port_cmd(remote_host, nginx_default_server_listen)
    update_nginx_default_server_listen_cmd(remote_host, nginx_default_server_listen)

    restart_nginx_cmd(remote_host)
    restart_apache2_cmd(remote_host)
    remove_pitrix_desktop_agent(remote_host)

    # configure vsftp
    ftp_username = fuser
    ftp_password = get_base64_password(fpw)
    ret = configure_vsftp_cmd(remote_host,ftp_username=ftp_username,ftp_password=ftp_password)
    logger.info("configure_vsftp_cmd ret == %s" %(ret))
    if not ret:
        return False

    # modify_vsfpd_limit_rate
    # limit_rate default is xxxMB
    # 1MB=1024 * 1024B
    limit_rate = int(limit_rate) * 1024 * 1024
    ret = APIFileShare.modify_vsfpd_limit_rate(ctx, limit_rate)
    logger.info("modify_vsfpd_limit_rate ret == %s" % (ret))
    if not ret:
        return False

    # modify_vsfpd_limit_conn
    limit_conn = int(limit_conn)
    ret = APIFileShare.modify_vsfpd_limit_conn(ctx, limit_conn)
    logger.info("modify_vsfpd_limit_conn ret == %s" % (ret))
    if not ret:
        return False

    # restart_vsftpd_service
    ret = APIFileShare.restart_vsftpd_service(ctx)
    if not ret:
        return False

    return True

def configure_loaded_file_share_service_instance(remote_host=None,vnas_private_ip=None,limit_rate=1,limit_conn=5,fuser=None,fpw=None):
    ctx = context.instance()
    nginx_default_server_listen = APIFileShare.check_nginx_default_server_listen(ctx)
    logger.info("nginx_default_server_listen == %s" %(nginx_default_server_listen))

    unmount_nfs_cmd(remote_host)
    sed_nfs_cmd(remote_host)
    echo_fstab_nfs_cmd(remote_host,vnas_private_ip)
    mount_nfs_cmd(remote_host, vnas_private_ip)
    cancel_url_prefix_cmd(remote_host)
    replace_urls_cmd(remote_host)
    configure_django_cmd(remote_host)
    configure_nginx_cmd(remote_host)
    update_django_port_cmd(remote_host, nginx_default_server_listen)
    update_nginx_default_server_listen_cmd(remote_host, nginx_default_server_listen)

    restart_nginx_cmd(remote_host)
    restart_apache2_cmd(remote_host)
    remove_pitrix_desktop_agent(remote_host)

    return True

def register_file_share_service_vnas(vnas_id,vnas_name,vnas_private_ip,status):

    ctx = context.instance()
    file_share_service_vnass = ctx.pgm.get_file_share_service_vnass(vnas_ids=vnas_id)
    if file_share_service_vnass is None or len(file_share_service_vnass) == 0:
        update_info = dict(
            vnas_id=vnas_id,
            vnas_name=vnas_name,
            vnas_private_ip=vnas_private_ip,
            status=status,
            create_time=get_current_time()
        )
        if not ctx.pg.insert(dbconst.TB_FILE_SHARE_SERVICE_VNAS, update_info):
            logger.error("insert newly created file share service vnas for [%s] to db failed" % (update_info))
            return -1

    else:
        for vnas_id, _ in file_share_service_vnass.items():
            condition = {"vnas_id": vnas_id}
            update_info = dict(
                vnas_name=vnas_name,
                vnas_private_ip=vnas_private_ip,
                status=status,
                create_time=get_current_time()
            )
            if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_SERVICE_VNAS, condition, update_info):
                logger.error("update file share service vnas for [%s] to db failed" % (update_info))
                return -1
    return 0

def register_desktop_server_manangement_vnas(vnas_id,vnas_name,vnas_private_ip,status):

    ctx = context.instance()
    #delete s2server in desktop_server_manangement
    conditions = {"service_type": const.S2SERVER_SERVICE_TYPE}
    ctx.pg.base_delete(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions)

    service_id = vnas_id
    service_node_id = vnas_id
    service_ip = vnas_private_ip
    service_node_ip = vnas_private_ip
    status = status
    update_desktop_service_management_info = {}
    update_info = dict(
        service_node_id=service_node_id,
        service_id=service_id,
        service_name=const.S2SERVER_NAME,
        description= '',
        status=status,
        service_version=const.S2SERVER_SERVICE_VERSION,
        service_ip=service_ip,
        service_node_status=status,
        service_node_ip=service_node_ip,
        service_node_type=const.MASTER_SERVICE_NODE_TYPE,
        service_port=const.S2SERVER_SERVICE_PORT,
        service_type=const.S2SERVER_SERVICE_TYPE,
        service_management_type=const.DESKTOP_SERVICE_MANAGEMENT_TYPE,
        create_time=get_current_time(),
    )
    update_desktop_service_management_info[service_node_id] = update_info
    # register desktop_service_management
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, update_desktop_service_management_info):
        logger.error("insert newly created desktop service management for [%s] to db failed" % (update_desktop_service_management_info))
        return -1

    return 0

def task_wait_delete_file_share_service_done(sender,file_share_service_id,file_share_service_instance_id,create_method):
    ctx = context.instance()

    with ResComm.transition_status(dbconst.TB_FILE_SHARE_SERVICE, file_share_service_id,const.FILE_SHARE_SERVICE_STATUS_DELETING):

        if const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED == create_method or file_share_service_instance_id:
            ret = task_resource_terminate_instances(sender, instance_id=file_share_service_instance_id)
            if ret < 0:
                logger.error("Task resource_terminal_instances fail:%s " % (file_share_service_instance_id))
                return -1
            instance_id = ret

    return 0

def task_wait_refresh_file_share_service_done(sender,file_share_service_id,create_method):
    ctx = context.instance()

    with ResComm.transition_status(dbconst.TB_FILE_SHARE_SERVICE, file_share_service_id,const.FILE_SHARE_SERVICE_STATUS_REFRESHING):

        global g_number
        g_number = const.FILE_SHARE_MAX_REFRESH_COUNT

        ret = task_refresh_loaded_file_share_service(sender,
                                                     file_share_service_id=file_share_service_id,
                                                     base_dn=const.FILE_SHARE_GROUP_ROOT_BASE_DN,
                                                     root_folder=const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR
                                                    )
        if ret < 0:
            logger.error("task_refresh_loaded_file_share_service fail:%s " % (file_share_service_id))
            return -1

        ret = task_refresh_loaded_file_share_service_local_file(sender,file_share_service_id=file_share_service_id)
        if ret < 0:
            logger.error("task_refresh_loaded_file_share_service_local_file fail:%s " % (file_share_service_id))
            return -1

    return 0

def attach_tags_to_resource(sender,color,tag_name,resource_type,resource_id):

    ctx = context.instance()
    # ret = ctx.res.resource_describe_tags(sender["zone"], search_word=tag_name)
    # tag_set = ret
    # if tag_set is None or len(tag_set) == 0:
    #     # CreateTag
    #     ret = ctx.res.resource_create_tag(sender["zone"], color=color,tag_name=tag_name)
    #     if not ret:
    #         logger.error("resource_create_tag fail")
    #         return -1
    #     tag_id = ret
    # else:
    #     for _,tag in tag_set.items():
    #         tag_id = tag.get("tag_id")
    #
    # # AttachTags
    # resource_tag_pairs = [{"resource_type": resource_type, "resource_id": resource_id, "tag_id": tag_id}]
    # selectedData = [tag_id]
    # ret = ctx.res.resource_attach_tags(sender["zone"], resource_tag_pairs=resource_tag_pairs,selectedData=selectedData)
    # if not ret:
    #     logger.error("resource_attach_tags fail")
    #     return -1
    # tag_id = ret

    return 0

def unmount_nfs_cmd(remote_host):

    cmd = "umount /mnt/nasdata"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return True
    return False

def get_desktop_server_instance_vxnet_id():

    cmd = "cat /opt/instance_vxnet_id_conf | awk '{print $2}'"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    logger.info("get_desktop_server_instance_vxnet_id output == %s" %(output))
    if ret != None and ret[0] == 0:
        return output
    return None

def mount_nfs_cmd(remote_host,vnas_private_ip):

    cmd = "mount -t nfs -o soft -o intr %s:/mnt/nas /mnt/nasdata" %(vnas_private_ip)
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return True
    return False

def sed_nfs_cmd(remote_host):

    cmd = "sed -i '/nfs/'d /etc/fstab"
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return True
    return False

def echo_fstab_nfs_cmd(remote_host,vnas_private_ip):

    cmd = "echo '%s:/mnt/nas /mnt/nasdata nfs defaults,soft,intr 0 0' >> /etc/fstab" %(vnas_private_ip)
    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return True
    return False

def delete_file_share_service(file_share_service_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_services(file_share_service_ids=file_share_service_id)
    if not ret:
        return 0
    file_share_services = ret
    for file_share_service_id,file_share_service in file_share_services.items():

        # delelte desktop_server_manangement vnas
        vnas_id = file_share_service.get("vnas_id")
        ret = ctx.pgm.get_desktop_service_managements(service_node_ids=vnas_id)
        if ret:
            conditions = {"service_node_id": vnas_id}
            ctx.pg.base_delete(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions)

        # delete file_share_service
        conditions = {"file_share_service_id": file_share_service_id}
        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_SERVICE, conditions)

        ret = ctx.pgm.get_file_share_groups()
        if not ret:
            continue
        file_share_groups = ret
        for file_share_group_id,file_share_group in file_share_groups.items():
            conditions = {"file_share_group_id": file_share_group_id}
            ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP, conditions)
            ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_ZONE, conditions)
            ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_USER, conditions)

            # delete file_share_group_file and file_share_group_file_download_history
            ret = ctx.pgm.get_file_share_group_files(file_share_group_ids=file_share_group_id)
            if not ret:
                continue
            file_share_group_files = ret
            for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
                conditions = {"file_share_group_file_id": file_share_group_file_id}
                ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions)
                ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, conditions)

    return 0

def register_new_folder_file(file_share_group_file):

    ctx = context.instance()
    file_share_group_file_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP_FILE, ctx.checker)
    update_info = dict(
        file_share_group_file_id=file_share_group_file_id,
        transition_status='',
        create_time=get_current_time()
    )
    update_info.update(file_share_group_file)
    if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_FILE, update_info):
        logger.error("register file_share create a record of file for [%s] to db failed" % (update_info))
        return -1

    return file_share_group_file_id

def update_folder_file(file_share_group_file_id,file_share_group_file_size):

    ctx = context.instance()
    condition = {"file_share_group_file_id": file_share_group_file_id}
    update_info = dict(
        file_share_group_file_size=file_share_group_file_size,
    )
    if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP_FILE, condition, update_info):
        logger.error("update file share group file for [%s] to db failed" % (update_info))
        return -1

    return 0

def get_file_share_group_scope(base_dn):

    ctx = context.instance()
    scope = const.FILE_SHARE_GROUP_ZONE_SCOPE_PART_ROLES
    if const.FILE_SHARE_GROUP_ROOT_BASE_DN == base_dn:
        ret = ctx.pgm.get_file_share_services(status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
        if ret:
            file_share_services = ret
            for file_share_service_id,file_share_service in file_share_services.items():
                scope = file_share_service["scope"]
    else:
        # check Up-level directory scope
        ret = ctx.pgm.get_file_share_groups(file_share_group_dn=base_dn)
        if ret:
            file_share_groups = ret
            for file_share_group_id,file_share_group in file_share_groups.items():
                scope = file_share_group["scope"]

    return scope

def set_file_share_group_zone(sender, file_share_group_id=None,user_scope=const.FILE_SHARE_GROUP_ZONE_SCOPE_PART_ROLES):

    ctx = context.instance()
    ret = ctx.pgm.get_zones()
    zones = ret
    for zone_id,_ in zones.items():

        update_info = {"file_share_group_id": file_share_group_id, "zone_id": zone_id, "user_scope": user_scope}
        if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_ZONE, update_info):
            logger.error("insert newly created file share group zone for [%s] to db failed" % (update_info))
            return -1

    return 0

def register_new_file_share_group(sender,file_share_group_name,file_share_group_dn,base_dn):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_services(status=const.FILE_SHARE_SERVICE_STATUS_ACTIVE)
    if not ret:
        return 0
    file_share_services = ret
    file_share_service_id = file_share_services.keys()[0]

    # get scope
    scope = get_file_share_group_scope(base_dn)

    file_share_group_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP, ctx.checker)
    update_info = dict(
        file_share_service_id=file_share_service_id,
        file_share_group_id=file_share_group_id,
        file_share_group_name=file_share_group_name,
        show_location= '["vm_tools_page","user_web_page"]',
        scope=scope,
        file_share_group_dn=file_share_group_dn,
        base_dn=base_dn,
        create_time=get_current_time()
    )

    if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP, update_info):
        logger.error("insert newly created file share group for [%s] to db failed" % (update_info))
        return -1

    file_share_groups = ctx.pgm.get_file_share_groups(file_share_group_ids=file_share_group_id)
    if not file_share_groups:
        return -1

    ret = set_file_share_group_zone(sender, file_share_group_id=file_share_group_id,user_scope=scope)
    if ret < 0:
        return -1

    return file_share_group_id

def format_file_share_unicode_param(check_param):

    if not check_param:
        return check_param

    if isinstance(check_param, list):
        temp_list = []
        for _param in check_param:
            if isinstance(_param, unicode):
                _param = str(_param).decode("string_escape").encode("utf-8")

            temp_list.append(_param)
        return temp_list

    elif isinstance(check_param, unicode):
        _param = str(check_param).decode("string_escape").encode("utf-8")
        return _param

    return check_param

def task_delete_file_share_group_files(sender, file_share_group_file_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0
    file_share_group_files = ret

    for file_share_group_file_id, file_share_group_file in file_share_group_files.items():
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
        file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
        file_share_group_dn = file_share_group_file["file_share_group_dn"]

        # recycle bin create a record of deleted file
        # If the same name needs to be renamed, add a time stamp suffix.
        ret = ctx.pgm.get_file_share_group_files(file_share_group_file_name=file_share_group_file_name,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_ACTIVE)
        if ret:
            file_share_group_file_name = APIFileShare.rename_filename(filename=file_share_group_file_name,suffix_string="Delete_At")
            file_share_group_file_dn = "cn=%s,%s" % (file_share_group_file_name, file_share_group_dn)

        new_file_share_group_file_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP_FILE, ctx.checker)
        update_info = dict(
            file_share_group_file_id=new_file_share_group_file_id,
            file_share_group_id=file_share_group_file["file_share_group_id"],
            file_share_group_file_name=file_share_group_file_name,
            file_share_group_file_alias_name=file_share_group_file.get("file_share_group_file_alias_name", ''),
            description=file_share_group_file.get("description", ''),
            file_share_group_file_size=file_share_group_file["file_share_group_file_size"],
            transition_status='',
            file_share_group_dn=file_share_group_dn,
            file_share_group_file_dn=file_share_group_file_dn,
            trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_ACTIVE,
            trashed_time=get_current_time(),
            create_time=get_current_time()
        )

        if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_FILE, update_info):
            logger.error("recycle bin create a record of deleted file for [%s] to db failed" % (update_info))
            return -1

        # Move files to the recycle bin dir
        recycle_bin_dir_path = const.FILE_SHARE_RECYCLES_BIN_DIR
        ret = APIFileShare.create_file_share_dir(ctx, recycle_bin_dir_path)
        if not ret:
            return -1

        file_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, APIFileShare.dn_to_path(file_share_group_file["file_share_group_file_dn"]))
        new_file_path = "%s/%s" % (const.FILE_SHARE_RECYCLES_BIN_DIR, file_share_group_file_name)
        ret = APIFileShare.mv_file_share_dir(ctx, file_path, new_file_path)
        if not ret:
            delete_file_share_group_file_dn(new_file_share_group_file_id)
            return 0

    return 0

def delete_file_share_group_file_record(file_share_group_file_id):

    ctx = context.instance()
    # # Delete file records in file share
    ctx.pg.delete(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id)

    return 0

def register_new_file_share_group_file(file_share_group_file,file_share_group_id,file_share_group_file_name,file_share_group_dn,file_share_group_file_dn):

    ctx = context.instance()
    file_share_group_file_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP_FILE, ctx.checker)
    update_info = dict(
        file_share_group_file_id=file_share_group_file_id,
        file_share_group_id=file_share_group_id,
        file_share_group_file_name=file_share_group_file_name,
        file_share_group_file_alias_name=file_share_group_file.get("file_share_group_file_alias_name",''),
        description=file_share_group_file.get("description",''),
        file_share_group_file_size=file_share_group_file["file_share_group_file_size"],
        transition_status='',
        file_share_group_dn=file_share_group_dn,
        file_share_group_file_dn=file_share_group_file_dn,
        create_time=get_current_time()
    )
    if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_FILE, update_info):
        logger.error("create a record of file for [%s] to db failed" % (update_info))
        return -1

    return file_share_group_file_id

def create_new_file_share_group_file(sender,file_share_group_file,file_share_group_dn,file_share_group_file_dn,file_share_group_file_name):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_groups(file_share_group_dn=file_share_group_dn,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if ret:
        file_share_groups = ret
        file_share_group_id = file_share_groups.keys()[0]
        # If the same name needs to be renamed, add a time stamp suffix.
        ret = ctx.pgm.get_file_share_group_files(file_share_group_file_dn=file_share_group_file_dn,
                                                 trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
        if ret:
            file_share_group_file_name = APIFileShare.rename_filename(filename=file_share_group_file_name,suffix_string="Restore_At")
            file_share_group_file_dn = "cn=%s,%s" % (file_share_group_file_name, file_share_group_dn)
    else:
        # If the original folder has been deleted, you need to create a new folder Restore_Folder in the root directory
        file_share_group_name = const.FILE_SHARE_RESTORE_FOLDER
        file_share_group_dn = "ou=%s,%s" % (const.FILE_SHARE_RESTORE_FOLDER, const.FILE_SHARE_GROUP_ROOT_BASE_DN)
        base_dn = const.FILE_SHARE_GROUP_ROOT_BASE_DN
        file_share_group_file_dn = "cn=%s,%s" % (file_share_group_file_name, file_share_group_dn)

        ret = ctx.pgm.get_file_share_groups(file_share_group_dn=file_share_group_dn,
                                            trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
        if ret:
            file_share_groups = ret
            file_share_group_id = file_share_groups.keys()[0]
            # If the same name needs to be renamed, add a time stamp suffix.
            ret = ctx.pgm.get_file_share_group_files(file_share_group_file_dn=file_share_group_file_dn,
                                                     trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
            if ret:
                file_share_group_file_name = APIFileShare.rename_filename(filename=file_share_group_file_name,suffix_string="Restore_At")
                file_share_group_file_dn = "cn=%s,%s" % (file_share_group_file_name, file_share_group_dn)
        else:
            logger.error("Restore_Folder no found")
            return -1

    ret = register_new_file_share_group_file(file_share_group_file,file_share_group_id,file_share_group_file_name,file_share_group_dn,file_share_group_file_dn)
    if ret < 0:
        return -1
    file_share_group_file_id = ret

    return  file_share_group_file_id

def task_restore_file_share_recycles(sender, file_share_group_file_id):

    logger.info("task_restore_file_share_recycles")
    ctx = context.instance()
    file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    for file_share_group_file_id, file_share_group_file in file_share_group_files.items():

        file_share_group_dn = file_share_group_file["file_share_group_dn"]
        file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]

        # create new file_share_group_file record
        ret = create_new_file_share_group_file(sender,file_share_group_file,file_share_group_dn,file_share_group_file_dn,file_share_group_file_name)
        if ret < 0:
            return -1
        new_file_share_group_file_id = ret
        ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=new_file_share_group_file_id)
        if not ret:
            logger.error("no found new file_share_group_file %s" % (new_file_share_group_file_id))
            continue
        for _,file in ret.items():
            file_share_group_dn = file["file_share_group_dn"]
            file_share_group_file_dn = file["file_share_group_file_dn"]

        # Move file to new dir
        new_dir_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, APIFileShare.dn_to_path(file_share_group_dn))
        ret = APIFileShare.create_file_share_dir(ctx,new_dir_path)
        if not ret:
            return -1

        file_path = "%s/%s" % (const.FILE_SHARE_RECYCLES_BIN_DIR, file_share_group_file_name)
        new_file_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, APIFileShare.dn_to_path(file_share_group_file_dn))
        ret = APIFileShare.mv_file_share_dir(ctx,file_path, new_file_path)
        if not ret:
            return -1

    return 0

def task_delete_permanently_file_share_recycles(sender, file_share_group_file_id):

    ctx = context.instance()
    file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    for file_share_group_file_id, file_share_group_file in file_share_group_files.items():
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]

        # 'rm  -fr files'
        file_path = "%s/%s" % (const.FILE_SHARE_RECYCLES_BIN_DIR, file_share_group_file_name)
        ret = APIFileShare.rm_file_share_dir(ctx,file_path)

    return 0

def task_empty_file_share_recycles(sender, file_share_group_file_id):

    ctx = context.instance()
    file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if file_share_group_files:
        for file_share_group_file_id, file_share_group_file in file_share_group_files.items():
            file_share_group_file_name = file_share_group_file["file_share_group_file_name"]

            # 'rm  -fr files'
            file_path = "%s/%s" % (const.FILE_SHARE_RECYCLES_BIN_DIR, file_share_group_file_name)
            ret = APIFileShare.rm_file_share_dir(ctx,file_path)

    return 0

def task_refresh_local_file_share_file(sender,file_share_service_id):
    ctx = context.instance()
    file_share_groups = ctx.pgm.get_file_share_groups(file_share_service_ids=file_share_service_id)
    if file_share_groups:
        for file_share_group_id, file_share_group in file_share_groups.items():
            file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_ids=file_share_group_id)
            if file_share_group_files:
                for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
                    file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
                    # check file exist
                    file_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, APIFileShare.dn_to_path(file_share_group_file_dn))
                    ret = APIFileShare.check_uploaded_file_exist(ctx,file_path)
                    if not ret:
                        logger.info("delete db file_path == %s" % (file_path))
                        # # Delete file records in file share
                        conditions = {"file_share_group_file_id": file_share_group_file_id}
                        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions)
                        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, conditions)

    return 0


def task_refresh_loaded_file_share_service(sender,file_share_service_id,base_dn=None,root_folder=None):

    global g_number
    ctx = context.instance()
    if not root_folder:
        return None

    root_folder = format_file_share_unicode_param(root_folder)
    ret = APIFileShare.search_remote_ftp_server_folder(ctx,root_folder)
    if not ret:
        return 0

    folder_list = format_file_share_unicode_param(ret.replace('\n', ' ').split(" "))
    logger.info("folder_list == %s" %(folder_list))

    for folder in folder_list:

        if folder in const.FILE_SHARE_EXCLUDE_GROUPS:
            continue

        file_share_group_dn = "ou=%s,%s" %(folder,base_dn)
        file_share_group_path = "%s" % (APIFileShare.dn_to_path(file_share_group_dn))
        ret = ctx.pgm.get_file_share_groups(file_share_service_ids=file_share_service_id,file_share_group_dn=file_share_group_dn)
        if not ret:
            # create new file_share_group
            ret = register_new_file_share_group(sender,file_share_group_name=folder, file_share_group_dn=file_share_group_dn, base_dn=base_dn)
            if ret < 0:
                return -1
            file_share_group_id = ret

            # create new file_share_group_file
            file_share_group_path = format_file_share_unicode_param(file_share_group_path)
            ret = APIFileShare.search_remote_ftp_server_folder_file(ctx, root_folder=file_share_group_path)
            if ret:
                folder_file_list = format_file_share_unicode_param(ret.replace('\n', ' ').split(" "))
                for folder_file in folder_file_list:
                    file_share_group_file_name = folder_file
                    file_share_group_file_dn = "cn=%s,%s" %(file_share_group_file_name,file_share_group_dn)
                    file_share_group_file_path = "%s" % (APIFileShare.dn_to_path(file_share_group_file_dn))
                    file_share_group_file_path = format_file_share_unicode_param(file_share_group_file_path)
                    file_share_group_file_size = APIFileShare.get_remote_ftp_server_folder_file_size(ctx, folder_file=file_share_group_file_path)
                    if not file_share_group_file_size:
                        file_share_group_file_size = 0
                    file_share_group_file = {}
                    file_share_group_file["file_share_group_id"] = file_share_group_id
                    file_share_group_file["file_share_group_file_name"] = file_share_group_file_name
                    file_share_group_file["file_share_group_file_size"] = file_share_group_file_size
                    file_share_group_file["file_share_group_dn"] = file_share_group_dn
                    file_share_group_file["file_share_group_file_dn"] = file_share_group_file_dn

                    ret = register_new_folder_file(file_share_group_file)
                    if ret < 0:
                        return -1

        else:
            file_share_groups = ret
            file_share_group_id = file_share_groups.keys()[0]
            file_share_group_path = format_file_share_unicode_param(file_share_group_path)
            ret = APIFileShare.search_remote_ftp_server_folder_file(ctx, root_folder=file_share_group_path)
            if ret:
                folder_file_list = format_file_share_unicode_param(ret.replace('\n', ' ').split(" "))
                for folder_file in folder_file_list:
                    file_share_group_file_name = folder_file
                    file_share_group_file_dn = "cn=%s,%s" % (file_share_group_file_name, file_share_group_dn)
                    file_share_group_file_path = "%s" % (APIFileShare.dn_to_path(file_share_group_file_dn))
                    file_share_group_file_path = format_file_share_unicode_param(file_share_group_file_path)
                    file_share_group_file_size = APIFileShare.get_remote_ftp_server_folder_file_size(ctx, folder_file=file_share_group_file_path)
                    if not file_share_group_file_size:
                        file_share_group_file_size = 0

                    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_dn=file_share_group_file_dn)
                    if ret:
                        file_share_group_files = ret
                        file_share_group_file_id = file_share_group_files.keys()[0]

                        ret = update_folder_file(file_share_group_file_id,file_share_group_file_size)
                        if ret < 0:
                            return -1
                    else:
                        file_share_group_file = {}
                        file_share_group_file["file_share_group_id"] = file_share_group_id
                        file_share_group_file["file_share_group_file_name"] = file_share_group_file_name
                        file_share_group_file["file_share_group_file_size"] = file_share_group_file_size
                        file_share_group_file["file_share_group_dn"] = file_share_group_dn
                        file_share_group_file["file_share_group_file_dn"] = file_share_group_file_dn

                        ret = register_new_folder_file(file_share_group_file)
                        if ret < 0:
                            return -1

        if g_number > 0:
            g_number = g_number - 1
            task_refresh_loaded_file_share_service(sender,file_share_service_id, base_dn=file_share_group_dn, root_folder=file_share_group_path)

    return 0

def task_refresh_loaded_file_share_service_local_file(sender,file_share_service_id):

    ctx = context.instance()
    file_share_groups = ctx.pgm.get_file_share_groups(file_share_service_ids=file_share_service_id)
    if file_share_groups:
        for file_share_group_id, file_share_group in file_share_groups.items():
            file_share_group_dn = file_share_group["file_share_group_dn"]
            file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_ids=file_share_group_id)
            if file_share_group_files:
                for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
                    file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
                    file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
                    file_share_group_dn = file_share_group_file["file_share_group_dn"]

                    # check if or  not exist remote ftp server file
                    file_path = "%s" % (APIFileShare.dn_to_path(file_share_group_file_dn))
                    ret = APIFileShare.check_remote_ftp_server_file_share_file(ctx,file_path,file_share_group_file_name)
                    if not ret:
                        logger.info("delete db file_path == %s" % (file_path))
                        # Delete file records in file share
                        conditions = {"file_share_group_file_id": file_share_group_file_id}
                        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions)
                        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, conditions)

                    # check if or  not exist remote ftp server file dir
                    dir_path = "%s" % (APIFileShare.dn_to_path(file_share_group_dn))
                    ret = APIFileShare.check_remote_ftp_server_file_share_dir(ctx, dir_path)
                    # logger.info("check_remote_ftp_server_file_share_dir ret == %s" %(ret))
                    if ret:
                        logger.info("delete db dir_path == %s" % (dir_path))
                        # Delete file records in file share
                        conditions = {"file_share_group_file_id": file_share_group_file_id}
                        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions)
                        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, conditions)

                        # Delete group records in file share
                        conditions = {"file_share_group_id": file_share_group_id}
                        ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP, conditions)
            else:
                # check if or  not exist remote ftp server file dir
                dir_path = "%s" % (APIFileShare.dn_to_path(file_share_group_dn))
                ret = APIFileShare.check_remote_ftp_server_file_share_dir(ctx, dir_path)
                # logger.info("check_remote_ftp_server_file_share_dir ret == %s" %(ret))
                if ret:
                    logger.info("delete db dir_path == %s" % (dir_path))

                    # Delete group records in file share
                    conditions = {"file_share_group_id": file_share_group_id}
                    ctx.pg.base_delete(dbconst.TB_FILE_SHARE_GROUP, conditions)

    return 0

def task_created_file_share_service_upload_file_shares(sender, file_share_group_file_id,file_share_group_file_name,file_share_group_dn):

    ctx = context.instance()
    source_path = "%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, file_share_group_file_name)
    path = APIFileShare.dn_to_path(file_share_group_dn)
    destination_path = "%s%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI,path, file_share_group_file_name)

    upload = APIFileShare.scp_file_to_remote_ftp_server(ctx,source_path,destination_path)

    if not upload:
        logger.error("upload localhost [%s] to remote-ftp [%s] failed" % (source_path, destination_path))
        os.system("rm -fr /mnt/nasdata/%s" %(file_share_group_file_name))
        return -1
    else:
        logger.info("upload localhost [%s] to remote-ftp [%s] successfully" % (source_path, destination_path))
        os.system("rm -fr /mnt/nasdata/%s" % (file_share_group_file_name))
        return 0

def check_filename_host(target_hosts,upload_file_uri):
    logger.info("check_filename_host target_hosts == %s upload_file_uri == %s" %(target_hosts,upload_file_uri))
    filename_host = get_hostname()
    for filename_host in target_hosts:
        cmd = "ls %s" % (upload_file_uri)
        logger.info("cmd == %s" % (cmd))
        if is_port_open(host=filename_host, port=22):
            ret = _exec_cmd(cmd=cmd, remote_host=filename_host, ssh_port=22)
            if ret != None and ret[0] == 0:
                return filename_host

    return filename_host

def rsync_upload_files_to_target_hosts_from_filename_host(filename_host,target_hosts,file_dir,upload_file_uri):

    ctx = context.instance()
    for target_host in target_hosts:
        logger.info("target_host == %s" %(target_host))
        ret =rsync_upload_files(filename_host,target_host,file_dir,upload_file_uri)
        if not ret:
            return -1
    return 0

def rsync_upload_files(filename_host,remote_host,file_dir,upload_file_uri):

    cmd = "scp -r root@%s:%s root@%s:%s" % (filename_host,upload_file_uri, remote_host,file_dir)
    logger.info("cmd == %s" % (cmd))
    ret = exec_cmd(cmd=cmd)
    if ret != None and ret[0] == 0:
        return True
    return False

def delete_upload_files(target_hosts,upload_file_uri):
    logger.info("delete_upload_files target_hosts == %s upload_file_uri == %s" %(target_hosts,upload_file_uri))
    filename_host = get_hostname()
    for filename_host in target_hosts:
        cmd = "rm -fr %s" % (upload_file_uri)
        logger.info("cmd == %s" % (cmd))
        if is_port_open(host=filename_host, port=22):
            ret = _exec_cmd(cmd=cmd, remote_host=filename_host, ssh_port=22)

    return None

def delete_upload_file_info(target_hosts,upload_file_uri):
    logger.info("delete_upload_file_info target_hosts == %s upload_file_uri == %s" %(target_hosts,upload_file_uri))
    filename_host = get_hostname()
    for filename_host in target_hosts:
        cmd = "rm -fr %s" % (upload_file_uri)
        logger.info("cmd == %s" % (cmd))
        if is_port_open(host=filename_host, port=22):
            ret = _exec_cmd(cmd=cmd, remote_host=filename_host, ssh_port=22)

    return None

def task_loaded_file_share_service_upload_file_shares(sender, file_share_group_file_id,file_share_group_file_name,file_share_group_dn):

    ctx = context.instance()
    zone_deploy = ctx.zone_deploy
    if zone_deploy == const.DEPLOY_TYPE_EXPRESS:
        local_hostname = get_hostname()
        if local_hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_0):
            target_hostname = local_hostname.replace(const.DESKTOP_SERVER_HOSTNAME_0, const.DESKTOP_SERVER_HOSTNAME_1)

        if local_hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_1):
            target_hostname = local_hostname.replace(const.DESKTOP_SERVER_HOSTNAME_1, const.DESKTOP_SERVER_HOSTNAME_0)

        upload_file_uri = "%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, file_share_group_file_name)
        # check where host is filename in
        target_hosts = get_target_host_list(ctx)
        logger.info("target_hosts == %s" %(target_hosts))
        filename_host = check_filename_host(target_hosts, upload_file_uri)
        logger.info("upload_file_uri [%s] is in target_host [%s]" % (upload_file_uri,filename_host))

        # rsync upload_file_uri
        if filename_host in target_hosts:
            target_hosts.remove(filename_host)
        ret = rsync_upload_files_to_target_hosts_from_filename_host(filename_host,target_hosts,const.DOWNLOAD_SOFTWARE_BASE_URI,upload_file_uri)
        if ret < 0:
            return -1

    source_path = "%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, file_share_group_file_name)
    path = APIFileShare.dn_to_path(file_share_group_dn)
    destination_path = "%s/%s" % (path, file_share_group_file_name)

    destination_path = format_file_share_unicode_param(destination_path)
    file_share_group_file_name = format_file_share_unicode_param(file_share_group_file_name)
    ret = APIFileShare.upload_file_to_remote_ftp_server(ctx,file_share_group_file_name,destination_path)
    logger.info("upload_file_to_remote_ftp_server ret == %s" %(ret))

    upload = False
    if ret:
        upload = True

    if not upload:
        logger.info("upload localhost [%s] to remote-ftp [%s] failed" % (source_path, destination_path))
        if zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            target_hosts = get_target_host_list(ctx)
            delete_upload_files(target_hosts, upload_file_uri)
            delete_upload_file_info(target_hosts, "/mnt/nasdata/*_info")
        else:
            os.system("rm -fr /mnt/nasdata/%s" % (file_share_group_file_name))
            os.system("rm -fr /mnt/nasdata/*_info")

        return -1
    else:
        logger.info("upload localhost [%s] to remote-ftp [%s] successfully" % (source_path, destination_path))

        # scp -r /mnt/nasdata/pitrix-deb.20210106.tar.gz root@10.11.12.19:/mnt/nasdata/test/
        file_path = '/mnt/nasdata/%s' %(file_share_group_file_name)
        dir_path = '/mnt/nasdata%s' %(APIFileShare.dn_to_path(file_share_group_dn))
        ret = APIFileShare.scp_file_to_remote_cloned_instance(ctx,file_path,dir_path)
        logger.info("scp_file_to_remote_cloned_instance ret == %s" %(ret))

        if zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            target_hosts = get_target_host_list(ctx)
            delete_upload_files(target_hosts, upload_file_uri)
            delete_upload_file_info(target_hosts, "/mnt/nasdata/*_info")
        else:
            os.system("rm -fr /mnt/nasdata/%s" % (file_share_group_file_name))
            os.system("rm -fr /mnt/nasdata/*_info")

        return 0

def task_loaded_file_share_service_download_file_shares(sender,
                                                        file_share_group_file_id,
                                                        file_share_group_file_name,
                                                        file_share_group_dn,
                                                        file_share_group_file_size):

    ctx = context.instance()
    download = False
    path = APIFileShare.dn_to_path(file_share_group_dn)
    source_path = "%s/%s" % (path, file_share_group_file_name)
    destination_path = "%s%s/%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI, path, file_share_group_file_name)

    # check remote_cloned_instance /mnt/nasdata/ront/***.txt is exist or not
    localhost_cache = APIFileShare.check_remote_cloned_instance_mnt_nasdata_file_exist_status(ctx, destination_path,file_share_group_file_size)
    logger.info("check_remote_cloned_instance_mnt_nasdata_file_exist_status localhost_cache == %s" %(localhost_cache))

    if localhost_cache:
        download = True
    else:
        path = format_file_share_unicode_param(path)
        file_share_group_file_name = format_file_share_unicode_param(file_share_group_file_name)
        ret = APIFileShare.get_remote_ftp_server_file_to_remote_cloned_instance_mnt_nasdata(ctx, path,file_share_group_file_name)
        logger.info("get_remote_ftp_server_file_to_remote_cloned_instance_mnt_nasdata ret == %s" % (ret))

        if ret:
            file_path = '/mnt/nasdata/%s' %(file_share_group_file_name)
            dir_path = '/mnt/nasdata%s' %(APIFileShare.dn_to_path(file_share_group_dn))

            file_path = format_file_share_unicode_param(file_path)
            dir_path = format_file_share_unicode_param(dir_path)
            download = APIFileShare.refresh_remote_cloned_instance_mnt_nasdata_file(ctx,file_path,dir_path)

    if not download:
        logger.error("download remote ftp [%s] to remote_cloned_instance [%s] failed" % (source_path, destination_path))
        return -1
    else:
        logger.info("download remote ftp [%s] to remote_cloned_instance [%s] successfully" % (source_path, destination_path))
        return 0

def task_delete_loaded_file_share_service_files(sender, file_share_group_file_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0
    file_share_group_files = ret

    for file_share_group_file_id, file_share_group_file in file_share_group_files.items():
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
        file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
        file_share_group_dn = file_share_group_file["file_share_group_dn"]

        # recycle bin create a record of deleted file
        # If the same name needs to be renamed, add a time stamp suffix.
        ret = ctx.pgm.get_file_share_group_files(file_share_group_file_name=file_share_group_file_name,
                                                 trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_ACTIVE)
        if ret:
            file_share_group_file_name = APIFileShare.rename_filename(filename=file_share_group_file_name,
                                                                      suffix_string="Delete_At")
            file_share_group_file_dn = "cn=%s,%s" % (file_share_group_file_name, file_share_group_dn)

        new_file_share_group_file_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP_FILE, ctx.checker)
        update_info = dict(
            file_share_group_file_id=new_file_share_group_file_id,
            file_share_group_id=file_share_group_file["file_share_group_id"],
            file_share_group_file_name=file_share_group_file_name,
            file_share_group_file_alias_name=file_share_group_file.get("file_share_group_file_alias_name", ''),
            description=file_share_group_file.get("description", ''),
            file_share_group_file_size=file_share_group_file["file_share_group_file_size"],
            transition_status='',
            file_share_group_dn=file_share_group_dn,
            file_share_group_file_dn=file_share_group_file_dn,
            trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_ACTIVE,
            trashed_time=get_current_time(),
            create_time=get_current_time()
        )

        if not ctx.pg.insert(dbconst.TB_FILE_SHARE_GROUP_FILE, update_info):
            logger.error("recycle bin create a record of deleted file for [%s] to db failed" % (update_info))
            return -1

        # check recycle_bin_dir if or not exist in remote ftp server
        recycle_bin_dir_path = const.FILE_SHARE_SERVICE_FTP_SERVER_RECYCLES_BIN_DIR
        recycle_bin_dir_path = format_file_share_unicode_param(recycle_bin_dir_path)

        ret = APIFileShare.check_remote_ftp_server_file_share_dir(ctx, dir_path=recycle_bin_dir_path)
        logger.info("check_remote_ftp_server_file_share_dir ret == %s" %(ret))
        if ret:
            ret = APIFileShare.create_remote_ftp_server_file_share_dir(ctx, recycle_bin_dir_path)
            if ret:
                logger.error("create_remote_ftp_server_file_share_dir [%s] failed" % (recycle_bin_dir_path))
                delete_file_share_group_file_dn(new_file_share_group_file_id)
                return -1

        # rename_remote_ftp_server_file_share_file in remote ftp server
        file_path = "%s" % (APIFileShare.dn_to_path(file_share_group_file["file_share_group_file_dn"]))
        new_file_path = "%s/%s" % (const.FILE_SHARE_SERVICE_FTP_SERVER_RECYCLES_BIN_DIR, file_share_group_file_name)

        # format_file_share_unicode_param
        file_path = format_file_share_unicode_param(file_path)
        new_file_path = format_file_share_unicode_param(new_file_path)
        file_share_group_file_name = format_file_share_unicode_param(file_share_group_file_name)

        ret = APIFileShare.rename_remote_ftp_server_file_share_file(ctx,
                                                                    source_path=file_path,
                                                                    destination_path=new_file_path,
                                                                    file_share_group_file_id=file_share_group_file_id,
                                                                    action_type=const.FILE_SHARE_SUFFIX_STRING_DELETE)
        logger.info("rename_remote_ftp_server_file_share_file ret == %s" %(ret))
        if not ret:
            logger.error("rename [%s] to [%s] failed" % (file_path,new_file_path))
            delete_file_share_group_file_dn(new_file_share_group_file_id)
            return -1
        else:
            logger.info("rename [%s] to [%s] successfully" %(file_path,new_file_path))

    return 0

def task_restore_loaded_file_share_service_recycles(sender, file_share_group_file_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0
    file_share_group_files = ret

    for file_share_group_file_id, file_share_group_file in file_share_group_files.items():

        file_share_group_dn = file_share_group_file["file_share_group_dn"]
        file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]

        # create new file_share_group_file record
        ret = create_new_file_share_group_file(sender,file_share_group_file,file_share_group_dn,file_share_group_file_dn,file_share_group_file_name)
        if ret < 0:
            return -1
        new_file_share_group_file_id = ret
        ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=new_file_share_group_file_id)
        if not ret:
            logger.error("no found new file_share_group_file %s" % (new_file_share_group_file_id))
            continue
        for _,file in ret.items():
            file_share_group_dn = file["file_share_group_dn"]
            file_share_group_file_dn = file["file_share_group_file_dn"]

        # check new_dir_path if or not exist in remote ftp server
        new_dir_path = "%s" % (APIFileShare.dn_to_path(file_share_group_dn))

        # format_file_share_unicode_param
        new_dir_path = format_file_share_unicode_param(new_dir_path)

        ret = APIFileShare.check_remote_ftp_server_file_share_dir(ctx, dir_path=new_dir_path)
        if ret:
            ret = APIFileShare.create_remote_ftp_server_file_share_dir(ctx, dir_path=new_dir_path)
            if ret:
                logger.error("create_remote_ftp_server_file_share_dir [%s] failed" % (new_dir_path))
                return -1

        # rename_remote_ftp_server_file_share_file in remote ftp server
        file_path = "%s/%s" % (const.FILE_SHARE_SERVICE_FTP_SERVER_RECYCLES_BIN_DIR, file_share_group_file_name)
        new_file_path = "%s" % (APIFileShare.dn_to_path(file_share_group_file_dn))

        # format_file_share_unicode_param
        file_path = format_file_share_unicode_param(file_path)
        new_file_path = format_file_share_unicode_param(new_file_path)

        ret = APIFileShare.rename_remote_ftp_server_file_share_file(ctx,
                                                                    source_path=file_path,
                                                                    destination_path=new_file_path,
                                                                    file_share_group_file_id=file_share_group_file_id,
                                                                    action_type=const.FILE_SHARE_SUFFIX_STRING_RESTORE)
        logger.info("rename_remote_ftp_server_file_share_file ret == %s" %(ret))
        if not ret:
            logger.error("rename [%s] to [%s] failed" % (file_path, new_file_path))
            delete_file_share_group_file_dn(new_file_share_group_file_id)
            return -1
        else:
            logger.info("rename [%s] to [%s] successfully" %(file_path,new_file_path))

    return 0

def task_delete_permanently_loaded_file_share_service_recycles(sender, file_share_group_file_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0
    file_share_group_files = ret

    for file_share_group_file_id, file_share_group_file in file_share_group_files.items():
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]

        # check if or not exist remote ftp server file
        file_path = "%s/%s" % (const.FILE_SHARE_SERVICE_FTP_SERVER_RECYCLES_BIN_DIR, file_share_group_file_name)

        # format_file_share_unicode_param
        file_path = format_file_share_unicode_param(file_path)

        ret = APIFileShare.check_remote_ftp_server_file_share_file(ctx,file_path=file_path,file_share_group_file_name=file_share_group_file_name)
        logger.info("check_remote_ftp_server_file_share_file ret == %s" %(ret))
        if ret:
            # delete file in remote ftp server
            ret = APIFileShare.delete_remote_ftp_server_file_share_file(ctx,
                                                                        file_path=file_path,
                                                                        file_share_group_file_id=file_share_group_file_id,
                                                                        action_type=const.FILE_SHARE_SUFFIX_STRING_DELETE)

            logger.info("delete_remote_ftp_server_file_share_file ret == %s" % (ret))
            if ret:
                logger.error("Permanently deleted [%s] failed" % (file_path))
                return -1
            else:
                logger.info("Permanently deleted [%s] successfully" % (file_path))

    return 0

def task_empty_loaded_file_share_service_recycles(sender, file_share_group_file_id):

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0
    file_share_group_files = ret

    for file_share_group_file_id, file_share_group_file in file_share_group_files.items():
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]

        # check if or not exist remote ftp server file
        file_path = "%s/%s" % (const.FILE_SHARE_SERVICE_FTP_SERVER_RECYCLES_BIN_DIR, file_share_group_file_name)

        # format_file_share_unicode_param
        file_path = format_file_share_unicode_param(file_path)

        ret = APIFileShare.check_remote_ftp_server_file_share_file(ctx,file_path=file_path,file_share_group_file_name=file_share_group_file_name)
        logger.info("check_remote_ftp_server_file_share_file ret == %s" %(ret))
        if ret:
            # delete file in remote ftp server
            ret = APIFileShare.delete_remote_ftp_server_file_share_file(ctx,
                                                                        file_path=file_path,
                                                                        file_share_group_file_id=file_share_group_file_id,
                                                                        action_type=const.FILE_SHARE_SUFFIX_STRING_DELETE)

            logger.info("delete_remote_ftp_server_file_share_file ret == %s" % (ret))
            if ret:
                logger.error("Permanently empty deleted [%s] failed" % (file_path))
                return -1
            else:
                logger.info("Permanently empty deleted [%s] successfully" % (file_path))
    return 0

def task_change_file_in_loaded_file_share_service_group(sender,file_share_group_file_id,file_share_group_file, new_file_share_group_dn,change_type,file_save_method='',repeat_file_ids=[]):

    ctx = context.instance()
    file_share_group_file_dn = file_share_group_file['file_share_group_file_dn']
    file_share_group_file_name = file_share_group_file['file_share_group_file_name']
    if not file_save_method:
        ret = create_new_file_share_group_file_record(file_share_group_file, new_file_share_group_dn, file_save_method,repeat_file_ids)
        if ret < 0:
            return -1
        new_file_share_group_file_dn = ret

        ret = change_file_in_loaded_file_share_service_group_execute_comand(file_share_group_file_dn, new_file_share_group_file_dn,change_type,file_share_group_file_name,file_share_group_file_id)
        if ret < 0:
            return -1

    elif const.SOURCE_FILE_SAVE_METHOD_SAVE == file_save_method:
        ret = create_new_file_share_group_file_record(file_share_group_file, new_file_share_group_dn, file_save_method,repeat_file_ids)
        if ret < 0:
            return -1
        new_file_share_group_file_dn = ret

        ret = change_file_in_loaded_file_share_service_group_execute_comand(file_share_group_file_dn, new_file_share_group_file_dn,change_type,file_share_group_file_name,file_share_group_file_id)
        if ret < 0:
            return -1

    elif const.SOURCE_FILE_SAVE_METHOD_OVERWRITE == file_save_method:
        ret = delete_old_file_share_group_file_record(file_share_group_file_id, file_share_group_file_name,new_file_share_group_dn, repeat_file_ids)
        if ret < 0:
            return -1

        ret = create_new_file_share_group_file_record(file_share_group_file, new_file_share_group_dn,file_save_method,repeat_file_ids)
        if ret < 0:
            return -1
        new_file_share_group_file_dn = ret

        ret = change_file_in_loaded_file_share_service_group_execute_comand(file_share_group_file_dn, new_file_share_group_file_dn,change_type,file_share_group_file_name,file_share_group_file_id)
        if ret < 0:
            return -1
    else:
        logger.error("file_save_method  %s is invalid" %(file_save_method))
        return -1

    return 0

def change_file_in_loaded_file_share_service_group_execute_comand(file_share_group_file_dn,new_file_share_group_file_dn,change_type,file_share_group_file_name,file_share_group_file_id):

    ctx = context.instance()
    file_path = "%s" % (APIFileShare.dn_to_path(file_share_group_file_dn))
    new_file_path = "%s" % (APIFileShare.dn_to_path(new_file_share_group_file_dn))

    # format_file_share_unicode_param
    file_path = format_file_share_unicode_param(file_path)
    new_file_path = format_file_share_unicode_param(new_file_path)

    # execute_comand: copy or move
    if const.FILE_SHARE_CHANGE_TYPE_MOVE == change_type:
        ret = APIFileShare.rename_remote_ftp_server_file_share_file(ctx,
                                                                    source_path=file_path,
                                                                    destination_path=new_file_path,
                                                                    file_share_group_file_id=file_share_group_file_id,
                                                                    action_type=const.FILE_SHARE_SUFFIX_STRING_MOVE)
        logger.info("rename_remote_ftp_server_file_share_file ret == %s" %(ret))
        if not ret:
            logger.error("mv [%s] to [%s] failed" % (file_path, new_file_path))
            return -1
        else:
            logger.info("mv [%s] to [%s] successfully" % (file_path, new_file_path))
            return 0

    elif const.FILE_SHARE_CHANGE_TYPE_COPY == change_type:
        file_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI,APIFileShare.dn_to_path(file_share_group_file_dn))
        new_file_path = "%s%s" % (const.DOWNLOAD_SOFTWARE_BASE_URI,APIFileShare.dn_to_path(new_file_share_group_file_dn))
        ret = APIFileShare.cp_file_share_dir(ctx,file_path, new_file_path)
        if not ret:
            logger.error("cp [%s] to [%s] failed" % (file_path, new_file_path))
            return -1
        else:
            logger.info("cp [%s] to [%s] successfully" % (file_path, new_file_path))
            return 0

    else:
        logger.error("change_type %s is invalid" %(change_type))
        return -1

def task_resource_create_instance(sender, desktop_config):

    ctx = context.instance()
    ret = ctx.res.resource_create_instance(sender["zone"], desktop_config=desktop_config,platform=const.PLATFORM_TYPE_QINGCLOUD)
    logger.info("resource_create_instance ret == %s" % (ret))
    if not ret:
        logger.error("resource create instance fail %s " % desktop_config)
        return -1
    instance_id = ret

    return instance_id

def task_wait_express_create_file_share_service_done(sender,
                                                     file_share_service_id,
                                                     network_id,
                                                     desktop_server_instance_id,
                                                     private_ip,
                                                     file_share_service_name,
                                                     vnas_disk_size,
                                                     vnas_id,
                                                     limit_rate,
                                                     limit_conn,
                                                     fuser,
                                                     fpw):

    ctx = context.instance()
    with ResComm.transition_status(dbconst.TB_FILE_SHARE_SERVICE, file_share_service_id, const.FILE_SHARE_SERVICE_STATUS_CREATING):
        desktop_config = {'usbredir': 1,
                          'hostname': '',
                          'clipboard': 1,
                          'login_passwd': const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                          'qxl_number': 1,
                          'graphics_protocol': 'vnc',
                          'instance_name': file_share_service_name,
                          'image_id': const.FILE_SHARE_SERVICE_FTP_SERVER_DEFAULT_IMAGE_ID,
                          'instance_class': 0,
                          'filetransfer': 1,
                          'usb3_bus': 'nec-xhci',
                          'volumes': [],
                          'memory': 2048,
                          'gpu': 0,
                          'cpu': 2,
                          'gpu_class': 0,
                          'login_mode': 'passwd',
                          'vxnets':[network_id],
                          'os_disk_size':100

                          }
        ret = task_resource_create_instance(sender, desktop_config)
        if ret < 0:
            logger.error("Task create instance fail:%s " % (file_share_service_id))
            return -1
        instance_id = ret

        #change instance_name
        ret = task_resource_modify_instance_attributes(sender, instance_id,instance_name=file_share_service_name)
        if ret < 0:
            logger.error("Task resource_modify_instance_attributes fail:%s " % (instance_id))
            return -1
        instance_id = ret

        ret = update_file_share_service(sender,file_share_service_id,file_share_service_instance_id=instance_id)
        if ret < 0:
            logger.error("update_file_share_service fail %s " % file_share_service_id)
            return -1

        #
        time.sleep(30)

        #Check the file_share_service private_ip
        private_ip = ctx.pgm.get_file_share_service_private_ip(file_share_service_ids=file_share_service_id)
        logger.info("file_share_service host private_ip == %s" %(private_ip))
        if not private_ip:
            logger.error("file_share_service %s no found private_ip" % file_share_service_id)
            return -1

        ret = configure_express_file_share_service_instance(remote_host=private_ip,limit_rate=limit_rate,limit_conn=limit_conn,fuser=fuser,fpw=fpw)
        if not ret:
            return -1

        return 0

def task_wait_express_load_file_share_service_done(sender,
                                                 file_share_service_id,
                                                 network_id,
                                                 desktop_server_instance_id,
                                                 private_ip,
                                                 file_share_service_name,
                                                 vnas_disk_size,
                                                 vnas_id,
                                                 limit_rate,
                                                 limit_conn,
                                                 fuser,
                                                 fpw):

    ctx = context.instance()
    with ResComm.transition_status(dbconst.TB_FILE_SHARE_SERVICE,file_share_service_id,const.FILE_SHARE_SERVICE_STATUS_IMPORTING):
        desktop_config = {'usbredir': 1,
                          'hostname': '',
                          'clipboard': 1,
                          'login_passwd': const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                          'qxl_number': 1,
                          'graphics_protocol': 'vnc',
                          'instance_name': file_share_service_name,
                          'image_id': const.FILE_SHARE_SERVICE_FTP_SERVER_DEFAULT_IMAGE_ID,
                          'instance_class': 0,
                          'filetransfer': 1,
                          'usb3_bus': 'nec-xhci',
                          'volumes': [],
                          'memory': 2048,
                          'gpu': 0,
                          'cpu': 2,
                          'gpu_class': 0,
                          'login_mode': 'passwd',
                          'vxnets': [network_id],
                          'os_disk_size': 100

                          }
        ret = task_resource_create_instance(sender, desktop_config)
        if ret < 0:
            logger.error("Task create instance fail:%s " % (file_share_service_id))
            return -1
        instance_id = ret

        # change instance_name
        ret = task_resource_modify_instance_attributes(sender, instance_id, instance_name=file_share_service_name)
        if ret < 0:
            logger.error("Task resource_modify_instance_attributes fail:%s " % (instance_id))
            return -1
        instance_id = ret

        ret = update_loaded_file_share_service(sender, file_share_service_id, file_share_service_instance_id=instance_id)
        if ret < 0:
            logger.error("update_loaded_file_share_service fail %s " % file_share_service_id)
            return -1

        #Check the file_share_service HOST IP supports accounts that can access services
        loaded_clone_instance_ip = ctx.pgm.get_file_share_service_loaded_clone_instance_ip(file_share_service_ids=file_share_service_id)
        logger.info("get_file_share_service_loaded_clone_instance_ip host loaded_clone_instance_ip == %s" %(loaded_clone_instance_ip))
        if not loaded_clone_instance_ip:
            logger.error("file_share_service %s no found loaded_clone_instance_ip" % file_share_service_id)
            return -1

        ret = configure_express_file_share_service_instance(remote_host=loaded_clone_instance_ip,limit_rate=limit_rate,limit_conn=limit_conn,fuser=fuser,fpw=fpw)
        if not ret:
            return -1

        # task_refresh_loaded_file_share_service
        global g_number
        g_number = const.FILE_SHARE_MAX_REFRESH_COUNT
        ret = task_refresh_loaded_file_share_service(sender,
                                                     file_share_service_id=file_share_service_id,
                                                     base_dn=const.FILE_SHARE_GROUP_ROOT_BASE_DN,
                                                     root_folder=const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR
                                                     )
        if ret < 0:
            logger.error("task_refresh_loaded_file_share_service fail:%s " % (file_share_service_id))
            return -1

        ret = task_refresh_loaded_file_share_service_local_file(sender, file_share_service_id=file_share_service_id)
        if ret < 0:
            logger.error("task_refresh_loaded_file_share_service_local_file fail:%s " % (file_share_service_id))
            return -1

        return 0

def ssh_keygen_cmd(remote_host):

    # ssh-keygen -f "/root/.ssh/known_hosts" -R "172.31.45.133"
    cmd = 'ssh-keygen -f "/root/.ssh/known_hosts" -R "%s"' %(remote_host)
    ret = exec_cmd(cmd=cmd,timeout=300,suppress_log=False)
    if ret != None and ret[0] == 0:
        return True
    return False

def mkdir_pitrix_conf_cmd(remote_host):

    # mkdir -p /pitrix/conf
    cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S mkdir -p /pitrix/conf'" %(
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
    remote_host,
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD)
    logger.info("cmd == %s" %(cmd))
    ret = exec_cmd(cmd=cmd,timeout=300,suppress_log=False)
    if ret != None and ret[0] == 0:
        return True
    return False

def chmod_pitrix_cmd(remote_host):

    # chmod -R 777 /pitrix
    cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S chmod -R 777 /pitrix'" % (
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
    remote_host,
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD)
    logger.info("cmd == %s" %(cmd))
    ret = exec_cmd(cmd=cmd,timeout=300,suppress_log=False)
    if ret != None and ret[0] == 0:
        return True
    return False

def scp_pitrix_conf_cmd(remote_host):

    # scp -r /pitrix/conf/configure_vsftp ubuntu@%s:/pitrix/conf
    cmd = "sshpass -p '%s' scp -r /pitrix/conf/configure_vsftp ubuntu@%s:/pitrix/conf" % (const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,remote_host)
    logger.info("cmd == %s" %(cmd))
    ret = exec_cmd(cmd=cmd,timeout=300,suppress_log=False)
    if ret != None and ret[0] == 0:
        return True
    return False

def express_configure_vsftp_cmd(remote_host,ftp_username,ftp_password):

    # /pitrix/conf/configure_vsftp/configure_vsftp.sh
    cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S /bin/bash /pitrix/conf/configure_vsftp/configure_vsftp.sh -u %s -w %s -m virtual'" %(
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
    remote_host,
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
    ftp_username,
    ftp_password)

    ret = exec_cmd(cmd=cmd,timeout=300,suppress_log=True)
    if ret != None and ret[0] == 0:
        return True
    return False

def dpkg_apache2_deb_cmd(remote_host):

    # dpkg -i --force-all /pitrix/conf/configure_vsftp/apache2_deb/*deb
    cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S dpkg -i --force-all /pitrix/conf/configure_vsftp/apache2_deb/*deb'" %(
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
    remote_host,
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD)
    logger.info("cmd == %s" %(cmd))
    ret = exec_cmd(cmd=cmd,timeout=300,suppress_log=True)
    if ret != None and ret[0] == 0:
        return True
    return False

def express_configure_apache_cmd(remote_host):

    # ln -fs /mnt/nasdata /var/www/html/file
    cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S ln -fs /mnt/nasdata /var/www/html/file'" %(
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
    remote_host,
    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD)
    logger.info("cmd == %s" %(cmd))
    ret = exec_cmd(cmd=cmd,timeout=300,suppress_log=True)
    if ret != None and ret[0] == 0:
        return True
    return False

def configure_express_file_share_service_instance(remote_host=None,limit_rate=0, limit_conn=0,fuser=None,fpw=None):

    ctx = context.instance()
    ftp_username = fuser
    ftp_password = get_base64_password(fpw)

    ret = ssh_keygen_cmd(remote_host)
    if not ret:
        logger.error("ssh_keygen_cmd failed")
        return False

    ret = mkdir_pitrix_conf_cmd(remote_host)
    if not ret:
        logger.error("mkdir_pitrix_conf_cmd failed")
        return False

    ret = chmod_pitrix_cmd(remote_host)
    if not ret:
        logger.error("chmod_pitrix_cmd failed")
        return False

    ret = scp_pitrix_conf_cmd(remote_host)
    if not ret:
        logger.error("scp_pitrix_conf_cmd failed")
        return False

    ret = express_configure_vsftp_cmd(remote_host,ftp_username,ftp_password)
    if not ret:
        logger.error("express_configure_vsftp_cmd failed")
        return False

    limit_rate = int(limit_rate) * 1024 * 1024
    ret = APIFileShare.modify_vsfpd_limit_rate(ctx,limit_rate)
    if not ret:
        logger.error("modify_vsfpd_limit_rate failed")
        return False

    ret = APIFileShare.modify_vsfpd_limit_conn(ctx,limit_conn)
    if not ret:
        logger.error("modify_vsfpd_limit_conn failed")
        return False

    ret = APIFileShare.restart_vsftpd_service(ctx)
    if not ret:
        logger.error("restart_vsftpd_service failed")
        return False

    ret = dpkg_apache2_deb_cmd(remote_host)
    if not ret:
        logger.error("dpkg_apache2_deb_cmd failed")
        return False

    ret = express_configure_apache_cmd(remote_host)
    if not ret:
        logger.error("express_configure_apache_cmd failed")
        return False

    return True

def task_wait_modify_file_share_service_done(sender,file_share_service_id,limit_rate,limit_conn):
    ctx = context.instance()

    with ResComm.transition_status(dbconst.TB_FILE_SHARE_SERVICE, file_share_service_id,const.FILE_SHARE_SERVICE_STATUS_MODIFYING):

            ret = task_modify_file_share_service(sender,
                                                 file_share_service_id=file_share_service_id,
                                                 limit_rate=limit_rate,
                                                 limit_conn=limit_conn)
            if ret < 0:
                logger.error("Task modify_file_share_service fail:%s " % (file_share_service_id))
                return -1

            modify_file_share_service_limit_rate_and_limit_conn(file_share_service_id, limit_rate, limit_conn)

    return 0

def task_modify_file_share_service(sender,file_share_service_id,limit_rate=0,limit_conn=0):

    ctx = context.instance()
    # modify_vsfpd_limit_rate
    # limit_rate default is xxMB
    # 1MB=1024 * 1024B
    limit_rate = int(limit_rate) * 1024 * 1024
    ret = APIFileShare.modify_vsfpd_limit_rate(ctx,limit_rate)
    if not ret:
        logger.error("modify_vsfpd_limit_rate failed")
        return -1

    # modify_vsfpd_limit_conn
    limit_conn = int(limit_conn)
    ret = APIFileShare.modify_vsfpd_limit_conn(ctx, limit_conn)
    if not ret:
        logger.error("modify_vsfpd_limit_conn failed")
        return -1

    # restart_vsftpd_service
    ret = APIFileShare.restart_vsftpd_service(ctx)
    if not ret:
        logger.error("restart_vsftpd_service failed")
        return -1

    return 0

def modify_file_share_service_limit_rate_and_limit_conn(file_share_service_id,limit_rate,limit_conn):

    ctx = context.instance()
    file_share_service_info = {
                    "limit_rate": limit_rate,
                    "limit_conn":limit_conn,
                    "status_time": get_current_time()
                    }
    logger.info("batch_update file_share_service_info == %s" %(file_share_service_info))
    if not ctx.pg.batch_update(dbconst.TB_FILE_SHARE_SERVICE, {file_share_service_id: file_share_service_info}):
        logger.error("modify file share service update DB fail: %s, %s" % (file_share_service_id, file_share_service_info))
        return -1

    return 0





