import time
import requests
import context
import constants as const
from log.logger import logger
from utils.net import is_port_open
from utils.json import json_dump, json_load
from utils.id_tool import UUID_TYPE_VDHOST_REQUEST, get_uuid
from send_request import send_desktop_server_request
import db.constants as dbconst

def _wait_desktop_job(job_id, zone, timeout=120, interval=3):
    ''' wait desktop server job '''
    end_time = time.time() + timeout

    while time.time() < end_time:

        req = {
        "type":"internal",
        "params":{"action": const.ACTION_VDI_DESCRIBE_DESKTOP_JOBS,
                  "jobs": [job_id],
                  "zone": zone
                },
        }
        ret = send_desktop_server_request(req)
        if ret.get("ret_code", -1) != 0:
            logger.error("wait job timeout.[%s][%s]" % (ret, job_id))
            return -1

        job_set = ret["desktop_job_set"]
        if not job_set:
            logger.error("describe jobs none.[%s][%s]" % (ret, job_id))
            return -1

        job = job_set[0]
        status = job["status"]

        if status in [const.JOB_STATUS_PEND, const.JOB_STATUS_WORKING]:
            time.sleep(interval)
            continue

        if status in [const.JOB_STATUS_SUCC]:
            return 0
        else:
            logger.error("jobs status fail.[%s][%s]" % (status, job_id))
            return -1

    return -1

def _check_private_ips(desktop_ips):
    active_ips = []
    for desktop_ip in desktop_ips:
        ret = is_port_open(desktop_ip, const.VDHOST_SERVER_DEFAULT_PORT)
        if ret:
            active_ips.append(desktop_ip)
    if len(active_ips) == 0:
        return None
    return active_ips


def add_active_directory(req):
    ctx = context.instance()
    desktop_ips = req.get("desktop_ips")
    if not desktop_ips:
        logger.error("desktop_ips is null.")
        return -1

    active_ips = _check_private_ips(desktop_ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return -1;

    desktop_id = req.get("desktop_id")
    hostnames = ctx.pgm.get_desktop_name(desktop_ids=[desktop_id])
    if not hostnames:
        logger.error("hostname is null.")
        return -1;
    hostname = hostnames[desktop_id]

    server_ip = active_ips[0]
    request_url = "http://%s:%s/api" % (server_ip, const.VDHOST_SERVER_DEFAULT_PORT)
    request = {
        "action": req.get("action"),
        "hostname": hostname
        }
    request_id = get_uuid(UUID_TYPE_VDHOST_REQUEST, 
                          None, 
                          long_format=True)
    request.update({"request_id": request_id})
    request.update(req["params"])

    end_time = time.time() + const.REQUEST_VDHOST_SERVER_ADD_AD_TIMEOUT
    while time.time() < end_time:
        try:
            rep = requests.post(request_url, data=json_dump(request))
            logger.info("post rep status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            if rep.status_code == 200:
                response = json_load(rep.text)
                if response:
                    ret_code = response["ret_code"]
                    if ret_code == 0:
                        return 0
            time.sleep(10)
        except Exception,e:
            logger.error("request vdhost server with exception: %s" % e)
            return -1
    return -1

def desktop_login(req):
    ctx = context.instance()
    desktop_id = req.get("desktop_id")
    desktop_ips = req.get("desktop_ips")
    if not desktop_ips:
        logger.error("desktop_ips is null.")
        return -1

    active_ips = _check_private_ips(desktop_ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return -1;

    server_ip = active_ips[0]
    request_url = "http://%s:%s/api" % (server_ip, const.VDHOST_SERVER_DEFAULT_PORT)
    request = {
        "action": req.get("action"),
        "login_str":  json_dump(req["params"])
        }
    request_id = get_uuid(UUID_TYPE_VDHOST_REQUEST, 
                          None, 
                          long_format=True)
    request.update({"request_id": request_id})

    # wait spice connect
    '''
    spice_connect = 0
    end_time = time.time() + const.REQUEST_VDHOST_SERVER_SSO_TIMEOUT
    while time.time() < end_time:
        try:
            connect_status = ctx.pgm.get_spice_connect_status(desktop_id)
            if connect_status == 0:
                time.sleep(1)
                continue
            else:
                spice_connect = 1
                break
        except Exception,e:
            logger.error("wait spice connect with Exception: %s" % e)

    if spice_connect == 0:
        logger.info("spice client is not connected.")
        return 0
    '''

    end_time = time.time() + const.REQUEST_VDHOST_SERVER_SSO_TIMEOUT
    while time.time() < end_time:
        lock_screen = 1
        try:
            # check login status
            login_status_request = {
                "action": const.REQUEST_VDHOST_GET_LOGIN_STATUS,
                "request_id": get_uuid(UUID_TYPE_VDHOST_REQUEST, None, long_format=True)
                }
            rep = requests.post(request_url, data=json_dump(login_status_request))
            logger.info("post login_status_request status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            try:
                login_status_response = json_load(rep.text)
                ret_code = login_status_response["ret_code"]
                if ret_code == 0:
                    lock_screen = login_status_response["lock_screen"]
                    if lock_screen == 0:
                        return 0
            except Exception,e:
                logger.error("request vdhost server with exception: %s" % e)

            # send ctrl+alt+delete to desktop server
            if lock_screen > 0:
                zone = ctx.pgm.get_desktop_zone(desktop_id)
                desktop_image_id = ctx.pgm.get_desktop_image_id(desktop_id)
                os_version = ctx.pgm.get_desktop_image_os_version(desktop_image_id)
                logger.info("os_version == %s" %(os_version))
                if const.OS_VERSION_WINDOWS10 == os_version:
                    desktop_req = {"type": "internal",
                                   "params": {
                                       "action": const.ACTION_VDI_SEND_DESKTOP_HOT_KEYS,
                                       "desktop_ids": [desktop_id],
                                       "keys": const.DESKTOP_HOT_KEY_CTRL,
                                       "zone": zone},
                                   }
                elif const.OS_VERSION_WINDOWS7 == os_version:
                    desktop_req = {"type": "internal",
                                   "params": {
                                       "action": const.ACTION_VDI_SEND_DESKTOP_HOT_KEYS,
                                       "desktop_ids": [desktop_id],
                                       "keys": const.DESKTOP_HOT_KEY_CTRL_ALT_DELETE,
                                       "zone": zone},
                                   }

                else:
                    desktop_req = {"type": "internal",
                                   "params": {
                                       "action": const.ACTION_VDI_SEND_DESKTOP_HOT_KEYS,
                                       "desktop_ids": [desktop_id],
                                       "keys": const.DESKTOP_HOT_KEY_CTRL_ALT_DELETE,
                                       "zone": zone},
                                   }
                logger.info("desktop_req == %s" % (desktop_req))
                flag = None
                for _ in range(0, 3):
                    desktop_rep = send_desktop_server_request(desktop_req)
                    if desktop_rep.get("ret_code", -1) != 0:
                        logger.error("send desktop server request [%s] fail" % req)
                        return -1
                    job_id = desktop_rep.get("job_id", "")
                    if len(job_id) == 0:
                        logger.error("return value without [job_id]")
                        return -1
                    # wait desktop server job
                    ret = _wait_desktop_job(job_id, zone, timeout=30, interval=1)
                    if ret < 0:
                        logger.error("wait desktop server job [%s] error" % job_id)
                        continue
                    if ret == 0:
                        flag = 1
                        break
                if flag is None:
                    logger.error("send ACTION_VDI_SEND_DESKTOP_HOT_KEYS error.")
                    return -1

            # send login request
            logger.info("desktop_login request: [ %s ]" % request)
            rep = requests.post(request_url, data=json_dump(request))
            logger.info("post desktop_login status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            if rep.status_code == 200:
                response = json_load(rep.text)
                if response:
                    ret_code = response["ret_code"]
                    if ret_code == 0:
                        time.sleep(5)
                        # check login is successful
                        rep = requests.post(request_url, data=json_dump(login_status_request))
                        logger.info("check login is successful status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
                        try:
                            login_status_response = json_load(rep.text)
                            ret_code = login_status_response["ret_code"]
                            if ret_code == 0:
                                lock_screen = login_status_response["lock_screen"]
                                if lock_screen == 0:
                                    return 0
                        except Exception,e:
                            logger.error("request vdhost server with exception: %s" % e)
            time.sleep(3)
        except Exception,e:
            logger.error("request vdhost server with exception: %s" % e)
            return -1
    return -1


def send_desktop_notify(req):

    desktop_ips = req.get("desktop_ips")
    if not desktop_ips:
        logger.error("desktop_ips is null.")
        return -1

    active_ips = _check_private_ips(desktop_ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return -1;

    server_ip = active_ips[0]
    request_url = "http://%s:%s/api" % (server_ip, const.VDHOST_SERVER_DEFAULT_PORT)
    request = {
        "action": req.get("action")
        }
    request_id = get_uuid(UUID_TYPE_VDHOST_REQUEST, 
                          None, 
                          long_format=True)
    request.update({"request_id": request_id})
    request.update(req["params"])
    logger.info("send_desktop_notify request: [ %s ]" % request)

    end_time = time.time() + const.REQUEST_VDHOST_SEND_NOTIFY_TIMEOUT
    while time.time() < end_time:
        try:
            rep = requests.post(request_url, data=json_dump(request))
            logger.info("post rep status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            if rep.status_code == 200:
                response = json_load(rep.text)
                if response:
                    ret_code = response["ret_code"]
                    if ret_code == 0:
                        return 0
            time.sleep(10)
        except Exception,e:
            logger.error("request vdhost server with exception: %s" % e)
            return -1
    return -1


def logoff(req):
    
    desktop_ips = req.get("desktop_ips")
    if not desktop_ips:
        logger.error("desktop_ips is null.")
        return -1

    active_ips = _check_private_ips(desktop_ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return -1;

    server_ip = active_ips[0]
    request_url = "http://%s:%s/api" % (server_ip, const.VDHOST_SERVER_DEFAULT_PORT)
    request = {
        "action": req.get("action")
        }
    request_id = get_uuid(UUID_TYPE_VDHOST_REQUEST, 
                          None, 
                          long_format=True)
    request.update({"request_id": request_id})
    logger.info("logoff request: [ %s ]" % request)

    end_time = time.time() + const.REQUEST_VDHOST_SEND_NOTIFY_TIMEOUT
    while time.time() < end_time:
        try:
            rep = requests.post(request_url, data=json_dump(request))
            logger.info("post rep status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            if rep.status_code == 200:
                response = json_load(rep.text)
                if response:
                    ret_code = response["ret_code"]
                    if ret_code == 0:
                        return 0
            time.sleep(10)
        except Exception,e:
            logger.error("request vdhost server with exception: %s" % e)
            return -1
    return -1


def modify_server_config(req):
    
    desktop_ips = req.get("desktop_ips")
    if not desktop_ips:
        logger.error("desktop_ips is null.")
        return -1

    active_ips = _check_private_ips(desktop_ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return -1;

    server_ip = active_ips[0]
    request_url = "http://%s:%s/api" % (server_ip, const.VDHOST_SERVER_DEFAULT_PORT)
    request = {
        "action": req.get("action"),
        "guest_server_config":  req["params"].get("guest_server_config", {})
        }
    request_id = get_uuid(UUID_TYPE_VDHOST_REQUEST, 
                          None, 
                          long_format=True)
    request.update({"request_id": request_id})
    logger.info("modify_server_config request: [ %s ]" % request)

    end_time = time.time() + const.REQUEST_VDHOST_SEND_NOTIFY_TIMEOUT
    while time.time() < end_time:
        try:
            rep = requests.post(request_url, data=json_dump(request))
            logger.info("post rep status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            if rep.status_code == 200:
                response = json_load(rep.text)
                if response:
                    ret_code = response["ret_code"]
                    if ret_code == 0:
                        return 0
            time.sleep(10)
        except Exception,e:
            logger.error("request vdhost server with exception: %s" % e)
            return -1
    return -1

def apply_desktop_maintainer(req):

    ctx = context.instance()
    desktop_ips = req.get("desktop_ips")
    if not desktop_ips:
        logger.error("desktop_ips is null.")
        return -1

    active_ips = _check_private_ips(desktop_ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return -1;

    desktop_id = req.get("desktop_id")
    hostnames = ctx.pgm.get_desktop_name(desktop_ids=[desktop_id])
    if not hostnames:
        logger.error("hostname is null.")
        return -1;
    hostname = hostnames[desktop_id]

    server_ip = active_ips[0]
    request_url = "http://%s:%s/api" % (server_ip, const.VDHOST_SERVER_DEFAULT_PORT)
    request = {
        "action": req.get("action"),
        "hostname": hostname,
        "desktop_ips": req.get("desktop_ips"),
        "desktop_id": req.get("desktop_id")
        }
    request_id = get_uuid(UUID_TYPE_VDHOST_REQUEST,
                          None,
                          long_format=True)
    request.update({"request_id": request_id})
    request.update(req["json_detail"])

    logger.info("apply_desktop_maintainer request: [ %s ]" % request)
    end_time = time.time() + const.REQUEST_VDHOST_SERVER_APPLY_DESKTOP_MAINTAINER_TIMEOUT
    while time.time() < end_time:
        try:
            rep = requests.post(request_url, data=json_dump(request))
            logger.info("post rep status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            if rep.status_code == 200:
                response = json_load(rep.text)
                if response:
                    ret_code = response["ret_code"]
                    if ret_code == 0:
                        return 0
            time.sleep(10)
        except Exception,e:
            logger.error("request vdhost server with exception: %s" % e)
            return -1
    return -1

def run_guest_shell_command(req):

    ctx = context.instance()
    desktop_ips = req.get("desktop_ips")
    if not desktop_ips:
        logger.error("desktop_ips is null.")
        return -1

    active_ips = _check_private_ips(desktop_ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return -1;

    desktop_id = req.get("desktop_id")
    hostnames = ctx.pgm.get_desktop_name(desktop_ids=[desktop_id])
    if not hostnames:
        logger.error("hostname is null.")
        return -1;
    hostname = hostnames[desktop_id]

    server_ip = active_ips[0]
    request_url = "http://%s:%s/api" % (server_ip, const.VDHOST_SERVER_DEFAULT_PORT)
    request = {
        "action": req.get("action"),
        "hostname": hostname,
        "desktop_ips": req.get("desktop_ips"),
        "desktop_id": req.get("desktop_id")
        }
    request_id = get_uuid(UUID_TYPE_VDHOST_REQUEST,
                          None,
                          long_format=True)
    request.update({"request_id": request_id})
    request.update(req["params"])

    logger.info("run_guest_shell_command request: [ %s ]" % request)
    end_time = time.time() + const.REQUEST_VDHOST_SERVER_RUN_GUEST_SHELL_COMMAND_TIMEOUT
    while time.time() < end_time:
        try:
            rep = requests.post(request_url, data=json_dump(request))
            logger.info("post rep status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            if rep.status_code == 200:
                response = json_load(rep.text)
                if response:
                    ret_code = response["ret_code"]
                    if ret_code == 0:
                        return rep.text
            time.sleep(10)
        except Exception,e:
            logger.error("request vdhost server with exception: %s" % e)
            return -1
    return -1

def update_guest_shell_command(guest_shell_command_id, command_response):

    ctx = context.instance()
    condition = {"guest_shell_command_id": guest_shell_command_id}
    update_info = {"command_response": command_response}

    if not ctx.pg.base_update(dbconst.TB_GUEST_SHELL_COMMAND, condition, update_info):
        logger.error("update guest shell command for [%s] to db failed" % (update_info))
        return -1

    return 0




