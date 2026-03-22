import datetime
import time
import socket
import logging.handlers
import context
from db.constants import TB_USER_LOGIN_RECORD, TB_DESKTOP_LOGIN_RECORD, TB_SYSLOG_SERVER
from constants import SYSLOG_SERVER_STATUS_ACTINE, SYSLOG_SERVER_STATUS_PUSHING
from log.logger import logger
from common import build_filter_conditions

SYSLOG_PUSH_MODE_UDP = "UDP"
SYSLOG_PUSH_MODE_TCP = "TCP"

def push_user_login_record():

    ctx = context.instance()
    
    now = datetime.datetime.today()
    today = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    oneday = datetime.timedelta(days=1) 
    yesterday = today - oneday  

    try:
        req = {
            "create_time": [yesterday, today],
            "sender":{
                "role": "global_admin",
                "console_id": "USER_CONSOLE_ADMIN"
                }
            }
        filter_conditions = build_filter_conditions(req, TB_USER_LOGIN_RECORD)

        limit = 1000
        total_count = ctx.pg.get_count(TB_USER_LOGIN_RECORD, filter_conditions)
        offset = 0

        user_login_record_result = []
        while total_count-limit>0:
            user_login_record_set = ctx.pg.get_by_filter(TB_USER_LOGIN_RECORD, 
                                                         filter_conditions, 
                                                         offset=offset, 
                                                         limit=limit)
            if user_login_record_set is None:
                logger.error("describe user login record failed , condition: [%s]" % filter_conditions)
                return None
            for _,record in user_login_record_set.items():
                create_time = record.get("create_time").strftime("%Y-%m-%d %H:%M:%S")
                syslog_str = "%s,%s,%s,%s,%s" % (record.get("user_name"), record.get("client_ip"), create_time, record.get("status"), record.get("errmsg"))
                user_login_record_result.append(syslog_str)

            offset = offset + limit
            total_count = total_count - limit
        else:
            limit = total_count
            user_login_record_set = ctx.pg.get_by_filter(TB_USER_LOGIN_RECORD, 
                                                         filter_conditions, 
                                                         offset=offset, 
                                                         limit=limit)
            if user_login_record_set is None:
                logger.error("describe user login record failed , condition: [%s]" % filter_conditions)
                return None
            for _,record in user_login_record_set.items():
                create_time = record.get("create_time").strftime("%Y-%m-%d %H:%M:%S")
                syslog_str = "%s,%s,%s,%s,%s" % (record.get("user_name"), record.get("client_ip"), create_time, record.get("status"), record.get("errmsg"))
                user_login_record_result.append(syslog_str)

        return user_login_record_result
    except Exception,e:
        logger.error("push syslog with exception: %s" % e)
        return None

def push_desktop_login_record():
    ctx = context.instance()
    
    now = datetime.datetime.today()
    today = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    oneday = datetime.timedelta(days=1) 
    yesterday = today - oneday  

    try:
        req = {
            "connect_time": [yesterday, today],
            "sender":{
                "role": "global_admin",
                "console_id": "USER_CONSOLE_ADMIN"
                }
            }
        filter_conditions = build_filter_conditions(req, TB_DESKTOP_LOGIN_RECORD)

        limit = 1000
        total_count = ctx.pg.get_count(TB_DESKTOP_LOGIN_RECORD, filter_conditions)
        offset = 0

        desktop_login_record_result = []
        while total_count-limit>0:
            desktop_login_record_set = ctx.pg.get_by_filter(TB_DESKTOP_LOGIN_RECORD, 
                                                            filter_conditions, 
                                                            offset=offset, 
                                                            limit=limit)
            if desktop_login_record_set is None:
                logger.error("describe desktop login record failed , condition: [%s]" % filter_conditions)
                return None
            for _,record in desktop_login_record_set.items():
                desktop = ctx.pgm.get_desktop(desktop_id=record.get("desktop_id"))
                desktop_ip = ""
                if desktop:
                    desktop_nics = desktop.get("nics", {})
                    for _,nic in desktop_nics.items():
                        desktop_ip = nic.get("private_ip", "")
                        if desktop_ip:
                            break
                connect_time = record.get("connect_time").strftime("%Y-%m-%d %H:%M:%S")
                syslog_str = "%s,%s,%s,%s" % (record.get("user_name"), record.get("desktop_id"), desktop_ip, connect_time)
                desktop_login_record_result.append(syslog_str)

            offset = offset + limit
            total_count = total_count - limit
        else:
            limit = total_count
            desktop_login_record_set = ctx.pg.get_by_filter(TB_DESKTOP_LOGIN_RECORD, 
                                                            filter_conditions, 
                                                            offset=offset, 
                                                            limit=limit)
            if desktop_login_record_set is None:
                logger.error("describe desktop login record failed , condition: [%s]" % filter_conditions)
                return None
            for _,record in desktop_login_record_set.items():
                desktop = ctx.pgm.get_desktop(desktop_id=record.get("desktop_id"))
                desktop_ip = ""
                if desktop:
                    desktop_nics = desktop.get("nics", {})
                    for _,nic in desktop_nics.items():
                        desktop_ip = nic.get("private_ip", "")
                        if desktop_ip:
                            break
                connect_time = record.get("connect_time").strftime("%Y-%m-%d %H:%M:%S")
                syslog_str = "%s,%s,%s,%s" % (record.get("user_name"), record.get("desktop_id"), desktop_ip, connect_time)
                desktop_login_record_result.append(syslog_str)

        return desktop_login_record_result
    except Exception,e:
        logger.error("push syslog with exception: %s" % e)
        return None

def push_desktop_user_map_recode():
    ctx = context.instance()
    
    desktop_user_map_result = []
    desktop_users = ctx.pgm.get_resource_user_maps(resource_type="desktop")
    if desktop_users is None:
        return desktop_user_map_result

    for desktop_user in desktop_users:
        user_name = desktop_user.get("user_name")
        desktop_id = desktop_user.get("resource_id")
        desktop_ip = ""
        desktop = ctx.pgm.get_desktop(desktop_id=desktop_id)
        if desktop:
            desktop_nics = desktop.get("nics", {})
            for _,nic in desktop_nics.items():
                desktop_ip = nic.get("private_ip", "")
                if desktop_ip:
                    break
        if user_name and desktop_ip:
            record = "%s,%s" % (user_name, desktop_ip)
            desktop_user_map_result.append(record)
    
    return desktop_user_map_result


my_logger = logging.getLogger("MyLogger")
my_logger.setLevel(logging.INFO)
my_logger_handler = None;

def push_syslog(syslog_host, syslog_port, syslog_mode):
    
    global my_logger
    global my_logger_handler

    user_login_record_result = push_user_login_record()
    desktop_login_record_result = push_desktop_login_record()
    desktop_user_map_result = push_desktop_user_map_recode()

    if user_login_record_result:
        for user_login_record in user_login_record_result:
            if my_logger_handler is None:
                if syslog_mode.upper() == SYSLOG_PUSH_MODE_UDP:
                    my_logger_handler = logging.handlers.SysLogHandler(address=(syslog_host, syslog_port), socktype=socket.SOCK_DGRAM)
                    my_logger.addHandler(my_logger_handler)
                elif syslog_mode.upper() == SYSLOG_PUSH_MODE_TCP:
                    my_logger_handler = logging.handlers.SysLogHandler(address=(syslog_host, syslog_port), socktype=socket.SOCK_STREAM)
                    my_logger.addHandler(my_logger_handler)

            if syslog_mode.upper() == SYSLOG_PUSH_MODE_TCP:
                user_login_record = user_login_record + "\n"
            my_logger.info(user_login_record)

    time.sleep(3)
    if desktop_login_record_result:
        for desktop_login_record in desktop_login_record_result:
            if syslog_mode.upper() == SYSLOG_PUSH_MODE_UDP:
                my_logger_handler = logging.handlers.SysLogHandler(address=(syslog_host, syslog_port), socktype=socket.SOCK_DGRAM)
                my_logger.addHandler(my_logger_handler)
            elif syslog_mode.upper() == SYSLOG_PUSH_MODE_TCP:
                my_logger_handler = logging.handlers.SysLogHandler(address=(syslog_host, syslog_port), socktype=socket.SOCK_STREAM)
                my_logger.addHandler(my_logger_handler)

            if syslog_mode.upper() == SYSLOG_PUSH_MODE_TCP:
                desktop_login_record = desktop_login_record + "\n"
            my_logger.info(desktop_login_record)

    time.sleep(3)
    if desktop_user_map_result:
        for desktop_user_map_record in desktop_user_map_result:
            if syslog_mode.upper() == SYSLOG_PUSH_MODE_UDP:
                my_logger_handler = logging.handlers.SysLogHandler(address=(syslog_host, syslog_port), socktype=socket.SOCK_DGRAM)
                my_logger.addHandler(my_logger_handler)
            elif syslog_mode.upper() == SYSLOG_PUSH_MODE_TCP:
                my_logger_handler = logging.handlers.SysLogHandler(address=(syslog_host, syslog_port), socktype=socket.SOCK_STREAM)
                my_logger.addHandler(my_logger_handler)

            if syslog_mode.upper() == SYSLOG_PUSH_MODE_TCP:
                desktop_user_map_record = desktop_user_map_record + "\n"
            my_logger.info(desktop_user_map_record)

    return 0

def update_syslog_server_status(syslog_server_id, status):
    ctx = context.instance()

    attrs = {}

    if status:
        attrs["status"] = status

    try:
        if not ctx.pg.update(TB_SYSLOG_SERVER, syslog_server_id, attrs):
            logger.error("modify syslog server [%s] failed." % (attrs))

        return syslog_server_id
    except Exception,e:
        logger.error("modify syslog server with Exception: %s" % e)

def goto_next_minute(minute):
    for i in range(0,60):
        cur_time = time.localtime()
        if minute != cur_time.tm_min:
            return
        else:
            time.sleep(1)

def push_syslogs():
    ctx = context.instance()

    hour = None
    minute = None
    syslog_servers = None
    syslog_server_id = None
    condition={"status": SYSLOG_SERVER_STATUS_ACTINE}

    try:
        cur_time = time.localtime()

        syslog_servers = ctx.pg.base_get(TB_SYSLOG_SERVER, condition, limit=100)
        if not syslog_servers:
            return 0

        for syslog_server in syslog_servers:
            try:
                runtime = syslog_server["runtime"]
                _hour, _minute = runtime.split(":")
                hour = int(_hour)
                minute = int(_minute)
                if cur_time.tm_hour != hour:
                    continue
                if cur_time.tm_min != minute:
                    continue

                syslog_host = syslog_server["host"]
                syslog_port = syslog_server["port"]
                syslog_mode = syslog_server["protocol"]
                syslog_server_id = syslog_server["syslog_server_id"]

                update_syslog_server_status(syslog_server_id, SYSLOG_SERVER_STATUS_PUSHING)
                push_syslog(syslog_host, syslog_port, syslog_mode)
                goto_next_minute(minute)
                update_syslog_server_status(syslog_server_id, SYSLOG_SERVER_STATUS_ACTINE)
            except Exception,e:
                logger.error("push syslog with exception: %s" % e)
                if syslog_server_id:
                    update_syslog_server_status(syslog_server_id, SYSLOG_SERVER_STATUS_ACTINE)

    except Exception,e:
        logger.error("push syslogs with excepton: %s" % e)
        if syslog_server_id:
            update_syslog_server_status(syslog_server_id, SYSLOG_SERVER_STATUS_ACTINE)

    return 0
