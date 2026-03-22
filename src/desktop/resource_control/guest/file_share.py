'''
Created on 2018-5-16

@author: yunify
'''

from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
import api.user.user as APIUser

from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
)

from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    PUBLIC_COLUMNS
)
import api.file_share.file_share as APIFileShare
from db.data_types import SearchType
import random
import os

def format_file_share_group(sender, file_share_group_set):

    ctx = context.instance()

    zone_id = sender.get("zone_id")
    file_share_groups = {}
    zone_infos = ctx.pgm.get_zones()

    for file_share_group_id, file_share_group in file_share_group_set.items():

        desktop_users = {}
        ret = ctx.pgm.get_file_share_group_user(file_share_group_ids=file_share_group_id)
        if ret:
            user_ids = ret.keys()
            user_column = ["user_name", "user_id", "user_dn"]
            user_group_column = ["user_group_name", "user_group_id", "user_group_dn"]
            ret = ctx.pgm.get_user_and_user_group(user_ids, user_column, user_group_column)
            if ret:
                desktop_users = ret
        if APIUser.is_global_admin_user(sender):
            file_share_group_zones = ctx.pgm.get_file_share_group_zone(file_share_group_ids=file_share_group_id)
            if file_share_group_zones:
                for zone_id, file_share_group_zone in file_share_group_zones.items():

                    zone = zone_infos.get(zone_id)
                    if zone:
                        file_share_group_zone["zone_name"] = zone["zone_name"]

                    user_scope = file_share_group_zone["user_scope"]
                    file_share_group_zone["scope"] = user_scope
                    del file_share_group_zone["user_scope"]
                    if user_scope == const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES:
                        continue

                    file_share_group_users = ctx.pgm.get_file_share_group_user(file_share_group_ids=file_share_group_id, zone_id=zone_id)

                    if not file_share_group_users:
                        file_share_group_users = {}

                    for user_id, file_share_group_user in file_share_group_users.items():

                        desktop_user = desktop_users.get(user_id)
                        if desktop_user:
                            file_share_group_user.update(desktop_user)

                    file_share_group_zone["user_ids"] = file_share_group_users.values()

                file_share_group["zone_scope"] = file_share_group_zones.values()

            file_share_groups[file_share_group_id] = file_share_group

        elif APIUser.is_console_admin_user(sender) or APIUser.is_normal_user(sender):

            file_share_group_zones = ctx.pgm.get_file_share_group_zone(file_share_group_ids=file_share_group_id)
            if file_share_group_zones:
                for zone_id, file_share_group_zone in file_share_group_zones.items():

                    zone = zone_infos.get(zone_id)
                    if zone:
                        file_share_group_zone["zone_name"] = zone["zone_name"]

                    user_scope = file_share_group_zone["user_scope"]
                    file_share_group_zone["scope"] = user_scope
                    del file_share_group_zone["user_scope"]
                    if user_scope == const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES:
                        continue

                    file_share_group_users = ctx.pgm.get_file_share_group_user(file_share_group_ids=file_share_group_id, zone_id=zone_id)
                    if not file_share_group_users:
                        file_share_group_users = {}

                    for user_id, file_share_group_user in file_share_group_users.items():

                        desktop_user = desktop_users.get(user_id)
                        if desktop_user:
                            file_share_group_user.update(desktop_user)

                    file_share_group_zone["user_ids"] = file_share_group_users.values()

                file_share_group["zone_scope"] = file_share_group_zones.values()
            file_share_groups[file_share_group_id] = file_share_group

    return file_share_groups

def format_file_share_group_file_count(sender, file_share_group_set):

    ctx = context.instance()

    for file_share_group_id, file_share_group in file_share_group_set.items():
        file_share_group_name = file_share_group.get("file_share_group_name")
        file_total_count = 0
        file_total_size = 0
        file_share_group_files = ctx.pgm.get_file_share_group_files(file_share_group_ids=file_share_group_id,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
        if file_share_group_files:
            file_total_count = len(file_share_group_files.keys())
            for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
                file_share_group_file_size = file_share_group_file.get("file_share_group_file_size",0)
                file_total_size = file_total_size + file_share_group_file_size

        # build info
        path = APIFileShare.dn_to_path(file_share_group["file_share_group_dn"])
        flag_id = sender.get("flag_id",file_share_group_id)
        id = file_share_group_id
        name = format_file_share_unicode_param(file_share_group_name)
        utc_time = file_share_group.get("create_time")

        # utc time to local time
        import datetime
        local_time = (utc_time + datetime.timedelta(hours=0)).strftime("%Y-%m-%d %H:%M:%S")

        dn = file_share_group.get("file_share_group_dn")

        file_share_group_set[file_share_group_id]["file_total_count"] = file_total_count
        file_share_group_set[file_share_group_id]["file_total_size"] = file_total_size
        file_share_group_set[file_share_group_id]["path"] = path
        file_share_group_set[file_share_group_id]["flag_id"] = flag_id
        file_share_group_set[file_share_group_id]["id"] = id
        file_share_group_set[file_share_group_id]["name"] = name
        file_share_group_set[file_share_group_id]["ctime"] = local_time
        file_share_group_set[file_share_group_id]["dn"] = dn
        file_share_group_set[file_share_group_id]["isdir"] = 1
        file_share_group_set[file_share_group_id]["gid"] = ''
        file_share_group_set[file_share_group_id]["uri"] = ''
        file_share_group_set[file_share_group_id]["size"] = file_total_size
        file_share_group_set[file_share_group_id]["alias_name"] = ""

        # delete unuse info
        zone_scope = file_share_group.get("zone_scope")
        if zone_scope:
            del file_share_group_set[file_share_group_id]["zone_scope"]
        del file_share_group_set[file_share_group_id]["update_time"]
        del file_share_group_set[file_share_group_id]["show_location"]
        del file_share_group_set[file_share_group_id]["scope"]
        del file_share_group_set[file_share_group_id]["file_share_group_dn"]
        del file_share_group_set[file_share_group_id]["file_share_service_id"]
        del file_share_group_set[file_share_group_id]["trashed_status"]
        del file_share_group_set[file_share_group_id]["trashed_time"]
        del file_share_group_set[file_share_group_id]["create_time"]

    return file_share_group_set

def format_file_share_group_user(sender, file_share_group_set):

    ctx = context.instance()
    user_id = sender["owner"]
    zone_id = sender["zone"]
    file_share_group_ids = file_share_group_set.keys()

    for file_share_group_id, file_share_group in file_share_group_set.items():

        # get all_roles
        ret = ctx.pgm.get_file_share_group_zones(zone_ids=zone_id,file_share_group_ids=file_share_group_id,user_scope=const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES)
        if ret:
            continue

        # get part_roles user
        file_share_group_dn = file_share_group["file_share_group_dn"]
        file_share_group_users = ctx.pgm.search_file_share_group_users(user_id=user_id,file_share_group_dn=file_share_group_dn)
        if file_share_group_users:
            continue

        del file_share_group_set[file_share_group_id]

    return file_share_group_set

def get_file_share_groups_info(sender, req):

    ctx = context.instance()
    filter_conditions = build_filter_conditions(req, dbconst.TB_FILE_SHARE_GROUP)
    file_share_group_ids = req.get("file_share_groups")
    if file_share_group_ids:
        file_share_group_group_dn = ctx.pgm.get_file_share_group_dn_by_file_share_group_id(file_share_group_ids=file_share_group_ids)
        filter_conditions["base_dn"] = file_share_group_group_dn
    else:
        filter_conditions["base_dn"] = const.FILE_SHARE_GROUP_ROOT_BASE_DN

    file_share_group_ids = None

    show_location = req.get("show_location")
    if show_location:
        filter_conditions["show_location"] = SearchType(show_location)

    filter_conditions["trashed_status"] = const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_FILE_SHARE_GROUP]

    logger.info("filter_conditions == %s" %(filter_conditions))

    file_share_group_set = ctx.pg.get_by_filter(dbconst.TB_FILE_SHARE_GROUP, filter_conditions, display_columns,
                                                sort_key=get_sort_key(dbconst.TB_FILE_SHARE_GROUP, req.get("sort_key")),
                                                reverse=get_reverse(req.get("reverse")),
                                                offset=req.get("offset", 0),
                                                limit=req.get("limit", DEFAULT_LIMIT),
                                                )

    if file_share_group_set is None:
        logger.error("describe file share group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format file_share_group_set
    format_file_share_group(sender, file_share_group_set)

    # format file_share_group_set
    if not APIUser.is_global_admin_user(sender):
        format_file_share_group_user(sender, file_share_group_set)

    # # format file_share_group_set
    format_file_share_group_file_count(sender, file_share_group_set)

    return file_share_group_set

def check_file_share_group_zone_scope(sender, file_share_group_id=None):

    ctx = context.instance()
    zone_id = sender["zone"]
    user_id = sender["owner"]
    scope_file_share_group_ids = []

    # get all_roles
    ret = ctx.pgm.get_file_share_group_zones(file_share_group_ids=file_share_group_id,user_scope=const.FILE_SHARE_GROUP_ZONE_SCOPE_ALL_ROLES)
    if ret:
        scope_file_share_group_ids.extend(ret.keys())

    # get part_roles user
    ret = ctx.pgm.get_file_share_group_users(file_share_group_ids=file_share_group_id, user_ids=user_id)
    if ret:
        scope_file_share_group_ids.extend(ret)

    if not scope_file_share_group_ids:
        return None

    return scope_file_share_group_ids

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

def URLencode(sStr):

    return sStr.replace('%', '%25').replace('#', '%23').replace('&', '%26').replace('+', '%2B').replace('?', '%3F').replace(':', '%3A').replace('@', '%40')

def format_file_share_group_file(sender, file_share_group_file_set,verbose):

    ctx = context.instance()

    # get download_file_ip
    download_file_ip = None
    download_file_ip = APIFileShare.get_file_share_apache2_http_ip(ctx)

    # get fuser and fpw
    fuser = ctx.pgm.get_file_share_service_fuser()
    fpw = ctx.pgm.get_file_share_service_fpw()

    if verbose:
        for file_share_group_file_id, file_share_group_file in file_share_group_file_set.items():

            file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
            file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
            path = APIFileShare.dn_to_path(file_share_group_file_dn)
            path = URLencode(path)
            fuser = URLencode(fuser)

            # #http://192.168.13.178/file/bangong/test01.1.2.png
            # format_download_file_uri = "http://%s/file%s" % (download_file_ip,path)
            # format_download_file_uri = format_file_share_unicode_param(format_download_file_uri)

            #ftp://192.168.13.178
            download_file_uri = "ftp://%s" % (download_file_ip)
            download_cmd = "get %s %s" %(path,file_share_group_file_name)

            # ftp_chinese_encoding_rules
            ftp_chinese_encoding_rules = APIFileShare.get_ftp_chinese_encoding_rules(ctx)

            # utc time
            utc_time = file_share_group_file.get("create_time")

            # utc time to local time
            import datetime
            local_time = (utc_time + datetime.timedelta(hours=0)).strftime("%Y-%m-%d %H:%M:%S")

            file_share_group_file_set[file_share_group_file_id]["download_file_exist"] = 1
            file_share_group_file_set[file_share_group_file_id]["path"] = path
            file_share_group_file_set[file_share_group_file_id]["fuser"] = fuser
            file_share_group_file_set[file_share_group_file_id]["fpw"] = fpw
            file_share_group_file_set[file_share_group_file_id]["download_cmd"] = download_cmd
            file_share_group_file_set[file_share_group_file_id]["flag_id"] = sender.get("flag_id",random.randint(1,65535))
            file_share_group_file_set[file_share_group_file_id]["gid"] = file_share_group_file.get("file_share_group_id", '')
            file_share_group_file_set[file_share_group_file_id]["alias_name"] = file_share_group_file.get("file_share_group_file_alias_name",'')
            file_share_group_file_set[file_share_group_file_id]["name"] = format_file_share_unicode_param(file_share_group_file_name)
            file_share_group_file_set[file_share_group_file_id]["id"] = file_share_group_file_id
            file_share_group_file_set[file_share_group_file_id]["ctime"] = local_time
            file_share_group_file_set[file_share_group_file_id]["size"] = file_share_group_file.get("file_share_group_file_size", '')
            file_share_group_file_set[file_share_group_file_id]["dn"] = file_share_group_file.get("file_share_group_file_dn", '')
            file_share_group_file_set[file_share_group_file_id]["uri"] = download_file_uri
            file_share_group_file_set[file_share_group_file_id]["isdir"] = 0
            file_share_group_file_set[file_share_group_file_id]["ftp_chinese_encoding_rules"] = ftp_chinese_encoding_rules

            # delete unuse info
            del file_share_group_file_set[file_share_group_file_id]["transition_status"]
            del file_share_group_file_set[file_share_group_file_id]["file_share_group_file_dn"]
            del file_share_group_file_set[file_share_group_file_id]["trashed_time"]
            del file_share_group_file_set[file_share_group_file_id]["trashed_status"]
            del file_share_group_file_set[file_share_group_file_id]["create_time"]

    else:
        for file_share_group_file_id, file_share_group_file in file_share_group_file_set.items():
            file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
            path = APIFileShare.dn_to_path(file_share_group_file_dn)
            file_share_group_file_set[file_share_group_file_id]["path"] = path

    return file_share_group_file_set

def format_file_share_group_file_user(sender, file_share_group_file_set,file_share_group_ids):

    ctx = context.instance()
    if not file_share_group_ids:
        return None

    if file_share_group_ids and not isinstance(file_share_group_ids,list):
        file_share_group_ids = [file_share_group_ids]

    file_share_group_id = file_share_group_ids[0]
    ret = check_file_share_group_zone_scope(sender, file_share_group_id)
    if not ret:
        file_share_group_file_set.clear()

    return file_share_group_file_set

def get_file_share_group_files_info(sender, req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_FILE_SHARE_GROUP_FILE)
    file_share_group_ids = req.get("file_share_groups")
    if file_share_group_ids:
        filter_conditions["file_share_group_id"] = file_share_group_ids

    file_share_group_file_ids = req.get("file_share_group_files")
    if file_share_group_file_ids:
        filter_conditions["file_share_group_file_id"] = file_share_group_file_ids

    filter_conditions["trashed_status"] = const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_FILE_SHARE_GROUP_FILE]

    logger.info("filter_conditions == %s" %(filter_conditions))
    file_share_group_file_set = ctx.pg.get_by_filter(dbconst.TB_FILE_SHARE_GROUP_FILE, filter_conditions,
                                                     display_columns,
                                                     sort_key=get_sort_key(dbconst.TB_FILE_SHARE_GROUP_FILE,req.get("sort_key")),
                                                     reverse=get_reverse(req.get("reverse")),
                                                     offset=req.get("offset", 0),
                                                     limit=req.get("limit",MAX_LIMIT),
                                                     )

    if file_share_group_file_set is None:
        logger.error("describe file share group file failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format download_file_share_group_file_set
    verbose = 1
    format_file_share_group_file(sender, file_share_group_file_set, verbose)

    if not APIUser.is_global_admin_user(sender):
        # format file_share_group_file_set
        format_file_share_group_file_user(sender, file_share_group_file_set,file_share_group_ids)

    return file_share_group_file_set

def create_component_upgrade_package_root_dir(component_upgrade_package_root_dir):
    if not os.path.exists(component_upgrade_package_root_dir):
        os.system("mkdir -p %s && chmod -R 777 %s" %(component_upgrade_package_root_dir,component_upgrade_package_root_dir))
        return True
    return True

def is_file_exist(component_upgrade_package_url):

    if not os.path.exists(component_upgrade_package_url):
        return False
    return True

def format_component_version(sender, component_version_set,verbose):

    ctx = context.instance()

    desktop_server_instance_ip = APIFileShare.get_desktop_server_instance_ip()
    logger.info("desktop_server_instance_ip == %s" %(desktop_server_instance_ip))

    if verbose:
        for component_id, component_version in component_version_set.items():

            filename = component_version["filename"]
            component_type = component_version["component_type"]

            component_upgrade_package_url = "%s/%s" % (const.COMPONENT_TYPE_FILE_SHARE_TOOLS_DIR, filename)
            component_upgrade_package_root_dir = "%s" % (const.COMPONENT_TYPE_FILE_SHARE_TOOLS_DIR)
            create_component_upgrade_package_root_dir(component_upgrade_package_root_dir)

            if is_file_exist(component_upgrade_package_url):
                component_upgrade_package_exist = 1
            else:
                component_upgrade_package_exist = 0

            # format component_upgrade_package_url
            # example:
            # http://192.168.13.172/softwares/mnt/nasdata/qingcloud_file_share_tools/qingcloud-file-share-tools-upgrade-2.1.0-202101151201-1-g9c07c72.exe
            component_upgrade_package_url = "/softwares%s/%s" % (const.COMPONENT_TYPE_FILE_SHARE_TOOLS_DIR, filename)

            component_version_set[component_id]["component_upgrade_package_url"] = component_upgrade_package_url
            component_version_set[component_id]["component_upgrade_package_exist"] = component_upgrade_package_exist
            component_version_set[component_id]["desktop_server_instance_ip"] = desktop_server_instance_ip

    return component_version_set

def get_file_share_tools_component_version_info(sender, req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_COMPONENT_VERSION)

    filter_conditions["component_type"] = const.COMPONENT_TYPE_FILE_SHARE_TOOLS

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_COMPONENT_VERSION]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_COMPONENT_VERSION]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_COMPONENT_VERSION]

    logger.info("filter_conditions == %s" %(filter_conditions))
    component_version_set = ctx.pg.get_by_filter(dbconst.TB_COMPONENT_VERSION, filter_conditions,
                                                 display_columns,
                                                 sort_key=get_sort_key(dbconst.TB_COMPONENT_VERSION,req.get("sort_key")),
                                                 reverse=get_reverse(req.get("reverse")),
                                                 offset=req.get("offset", 0),
                                                 limit=req.get("limit",MAX_LIMIT),
                                                 )

    if component_version_set is None:
        logger.error("describe component version failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format component_version_set
    format_component_version(sender, component_version_set,verbose=1)

    return component_version_set
