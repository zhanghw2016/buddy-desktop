'''
Created on 2012-5-9

@author: yunify
'''


from constants import (
    TIMEOUT_DESKTOP_SERVER_REQUEST,
    ACTION_VDI_CHECK_DESKTOP_USER_SESSION,
    SERVER_TYPE_PUSH_SERVER,
    SERVER_TYPE_VDI_SERVER,
    TOPIC_TYPE_JOB,
    TOPIC_TYPE_MONITOR,
    GET_TOPIC_JOB_SUB_TYPE,
    TOPIC_TYPE_EVENT,
    REQ_PUBLISH,
    REQUEST_TYPE_DESKTOP_SERVER,
    SERVER_TYPE_VDI_TERMINAL_SERVER,
    PUSH_SERVER_PORT
    )
from base_client import BaseClient, ReqLetter
from utils.json import json_dump, json_load
from utils.net import get_listening_url
from log.logger import logger
from utils.net import is_port_open
import context
from common import get_target_host_list

g_base_client = None
def send_desktop_server_request(req, need_reply=True,timeout=TIMEOUT_DESKTOP_SERVER_REQUEST):
    ''' send desktop server request '''
    global g_base_client
    if g_base_client == None:
        g_base_client = BaseClient(use_sock_pool = True)
    # send request to desktop server
    letter = ReqLetter(get_listening_url(SERVER_TYPE_VDI_SERVER), json_dump(req))
    if not need_reply:
        return g_base_client.send(letter, 0, timeout)
    rep = json_load(g_base_client.send(letter, 0, timeout))
    if rep is None:
        logger.error("receive reply failed on [%s]" % SERVER_TYPE_VDI_SERVER)
        return None
    return rep

def check_session(user_id, sid, zone):
    ''' check session '''
    logger.debug("checking session [%s, %s]" % (user_id, sid))
    
    # send request
    req = {"type":"internal",
           "params":{"action": ACTION_VDI_CHECK_DESKTOP_USER_SESSION,
                     "sk": sid,
                     "zone": zone},
           }

    # send request
    rep = send_desktop_server_request(req)
    if rep == None or rep['ret_code'] != 0:
        logger.error("check user session [%s] failed" % sid)
        return False
    
    return rep.get('user_id') == user_id

def send_terminal_server_request(req, need_reply=True):
    logger.info("send_terminal_server_request req == %s" %(req))
    ''' send desktop server request '''
    req.update({"type": REQUEST_TYPE_DESKTOP_SERVER})
    global g_base_client
    if g_base_client == None:
        g_base_client = BaseClient(use_sock_pool = True)
    # send request to desktop server
    letter = ReqLetter(get_listening_url(SERVER_TYPE_VDI_TERMINAL_SERVER), json_dump(req))
    if not need_reply:
        return g_base_client.send(letter, 0, TIMEOUT_DESKTOP_SERVER_REQUEST)
    rep = json_load(g_base_client.send(letter, 0, TIMEOUT_DESKTOP_SERVER_REQUEST))
    if rep is None:
        logger.error("receive reply failed on [%s]" % SERVER_TYPE_VDI_SERVER)
        return None
    return rep

def send_push_server_request(req, need_reply=True, listen_ip=None):
    ''' send push server request '''
    global g_base_client
    if g_base_client == None:
        g_base_client = BaseClient(use_sock_pool = True)

    # send request to desktop server
    letter = ReqLetter(get_listening_url(SERVER_TYPE_PUSH_SERVER, listen_ip=listen_ip), json_dump(req))
    if not need_reply:
        return g_base_client.send(letter, 0, TIMEOUT_DESKTOP_SERVER_REQUEST)
    rep = json_load(g_base_client.send(letter, 0, TIMEOUT_DESKTOP_SERVER_REQUEST))
    if rep is None:
        logger.error("receive reply failed on [%s]" % SERVER_TYPE_PUSH_SERVER)
        return None
    return rep

def send_all_push_server_request(req, need_reply=True):
    ''' send push server request '''
    global g_base_client
    if g_base_client == None:
        g_base_client = BaseClient(use_sock_pool = True)

    # send request to desktop server
    rep = None
    ret = None
    ctx = context.instance()
    # push_servers = ctx.pgm.get_desktop_services()
    # if push_servers is None:
    #     logger.error("get desktop push server error.")
    #     return None
    target_hosts = get_target_host_list(ctx)

    for push_server_ip in target_hosts:

        letter = ReqLetter(get_listening_url(SERVER_TYPE_PUSH_SERVER, listen_ip=push_server_ip), json_dump(req))
        if not need_reply:
            ret = g_base_client.send(letter, 0, TIMEOUT_DESKTOP_SERVER_REQUEST)
        else:
            ret = json_load(g_base_client.send(letter, 0, TIMEOUT_DESKTOP_SERVER_REQUEST))
        if ret is not None:
            rep = ret

    return rep

def push_topic_job(data):
    ''' push topic type: job '''
    try:
        req = {"action": REQ_PUBLISH,
               "subscriber": data.pop("user_id"),
               "topic_type": TOPIC_TYPE_JOB,
               "topic_sub_type": GET_TOPIC_JOB_SUB_TYPE[data.get("job_action")],
               "data": data
               }
        return send_all_push_server_request(req, need_reply=False)
    except Exception, e:
        logger.error("push topic job with Exception: %s" % e)
        return None

def push_topic_monitor(user_id, topic_sub_type, data):
    ''' push topic type: monitor '''
    try:
        req = {"action": REQ_PUBLISH,
               "subscriber": user_id,
               "topic_type": TOPIC_TYPE_MONITOR,
               "topic_sub_type": topic_sub_type,
               "data": data
               }
        return send_all_push_server_request(req, need_reply=False)
    except Exception, e:
        logger.error("push topic monitor with Exception: %s" % e)
        return None

def push_topic_event(user_id, topic_sub_type, data):
    ''' push topic type: event '''
    try:
        req = {"action": REQ_PUBLISH,
               "subscriber": user_id,
               "topic_type": TOPIC_TYPE_EVENT,
               "topic_sub_type": topic_sub_type,
               "data": data
               }
        return send_all_push_server_request(req, need_reply=False)
    except Exception, e:
        logger.error("push topic monitor with Exception: %s" % e)
        return None



