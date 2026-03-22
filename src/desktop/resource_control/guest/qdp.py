'''
Created on 2019-5-11

@author: yunify
'''
import os
from log.logger import logger
from constants import (
    QDP_CONNECT_FILE_DIR,
    QDP_CONNECT_FILE_BASE_URI,
    QDP_CONNECT_FILE_DIR_NUMBERS,
)
from resource_control.policy.usb import describe_usb_policy
import context
from common import _rsync_connect_file
import constants as const

def _clean_connection_file(file_name, base_path = QDP_CONNECT_FILE_DIR):

    for dirpath, _, filenames in os.walk(base_path):
        if file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            os.remove(file_path)
            
    return None

g_dir_index = 0
def _get_dir_index():
    global g_dir_index
    if g_dir_index > 0:
        return g_dir_index

    index = 0
    for _, dirnames, _ in os.walk(QDP_CONNECT_FILE_DIR):
        break
    
    for item in dirnames:
        if int(item) >= index:
            index = int(item)

    return index

def _get_file_number(path):

    for _, _, filenames in os.walk(path):
        return len(filenames)

def _get_usb_filter(broker):
    usb_filter = ""
    object_id = broker.get("desktop_group_id")
    if not object_id:
        object_id = broker.get("desktop_id")
    usb_policy_set = describe_usb_policy(condition={"object_id": object_id}, sort_key="priority", offset=0, limit=100)
    flag = 0
    for usb_policy in usb_policy_set:
        _filter = "%s,%s,%s,%s,%d" % (usb_policy["class_id"], usb_policy["vendor_id"], usb_policy["product_id"], usb_policy["version_id"], usb_policy["allow"])
        usb_filter = usb_filter + _filter
        usb_filter = usb_filter + "|"
        flag = flag + 1
    if usb_filter.endswith("|"):
        usb_filter = usb_filter[:len(usb_filter)-1]
    
    if len(usb_filter) < 10:
        usb_filter = "-1,-1,-1,-1,1"
    usb_filter = usb_filter + "\n"
    return usb_filter

def create_qdp_connect_files(desktop_broker):
    ''' create qdp connect files '''
    ctx = context.instance()
    if not desktop_broker:
        logger.error("desktop_brokers is none.")
        return False

    if not os.path.isdir(QDP_CONNECT_FILE_DIR):
        os.system("mkdir -p %s" % QDP_CONNECT_FILE_DIR)
        os.system("chmod 777 %s" % QDP_CONNECT_FILE_DIR)

    brokers = []
    for resource_id, broker in desktop_broker.items():

        desktop_id_context = resource_id.split('-')[1]
        desktop_id_prefix = desktop_id_context[0:2]

        hostnames = ctx.pgm.get_desktop_name(resource_id)
        if not hostnames:
            hostnames = {}

        hostname = hostnames.get(resource_id)

        conn_file = "%s.vv" % (resource_id)

        path = "%s/%s" % (QDP_CONNECT_FILE_DIR, desktop_id_prefix)
        if not os.path.exists(path):
            os.mkdir(path)

        conn_file_path = "%s/%s" % (path, conn_file)

        try:
            with open(conn_file_path, "w") as f:
                contents = ["[qdp]\n"]
                contents.append("type=qdp\n")
                contents.append("host=%s\n" % broker["host"])
                contents.append("port=%s\n" % str(broker["port"]))
                contents.append("fullscreen=%d\n" % broker["full_screen"])
                contents.append("delete-this-file=1\n")
                if broker.get("usb_redirect", 1) == 1:
                    contents.append("enable-usbredir=1\n")
                    contents.append("enable-usb-autoshare=0\n")
                    contents.append("usb-filter=" + _get_usb_filter(broker))
                contents.append("title=%s\n" % (hostname if hostname else resource_id))
                f.writelines(contents)
        except Exception, e:
            logger.error("write file [%s] failed, [%s]" % (conn_file_path, e))
            return False

        broker["connect_file_uri"] = "%s/%s/%s" % (QDP_CONNECT_FILE_BASE_URI, desktop_id_prefix, conn_file)
        status = ctx.pgm.get_desktop_service_management_vnas_server_status()
        if status == const.SERVICE_STATUS_INVAILD or ctx.zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            _rsync_connect_file(ctx, conn_file_path, path)

        brokers.append(broker)

    return brokers
