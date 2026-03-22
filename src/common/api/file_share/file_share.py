import db.constants as dbconst
import constants as const
from utils.id_tool import UUID_TYPE_DESKTOP_USER
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from log.logger import logger
from utils.misc import get_current_time,exec_cmd,_exec_cmd,get_current_timestamp,redefine_format_timestamp
from utils.net import is_port_open
import copy
import os
from utils.auth import get_base64_password
import chardet
import threading

rename_remote_ftp_server_file_share_file_lock = threading.Lock()
check_remote_ftp_server_file_share_dir_lock = threading.Lock()
check_remote_ftp_server_file_share_file_lock = threading.Lock()
delete_remote_ftp_server_file_share_file_lock = threading.Lock()

def check_nginx_default_server_listen(ctx):

    cmd = "cat /etc/nginx/sites-enabled/vdi-portal |grep default_server | awk '{print $2}'"
    ret = exec_cmd(cmd=cmd)
    (_, output, _) = ret
    logger.info("check_nginx_default_server_listen output == %s" %(output))
    if ret != None and ret[0] == 0:
        return output
    return 80

def check_download_file_uri_port(ctx):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            cmd = "cat /etc/nginx/sites-enabled/vdi-portal-cross-domain |grep default_server | awk '{print $2}'"
            ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
            (_, output, _) = ret
            logger.info("check_download_file_uri_port output == %s" %(output))
            if ret != None and ret[0] == 0:
                return output
    return 80

def format_file_share_gbk_param(ctx,check_param):

    if not check_param:
        return check_param

    # check ftp_chinese_encoding_rules and parameter encoding
    ftp_chinese_encoding_rules = get_ftp_chinese_encoding_rules(ctx)
    encoding = chardet.detect(check_param).get("encoding")

    if const.FTP_SERVER_CHINESE_ENCODING_RULES_ASCII == encoding:
        check_param = check_param
    elif const.FTP_SERVER_CHINESE_ENCODING_RULES_UTF_8 == encoding:
        if const.FTP_SERVER_CHINESE_ENCODING_RULES_GBK == ftp_chinese_encoding_rules:
            check_param = check_param.decode('utf-8').encode('gbk')
        else:
            check_param = check_param

    encoding = chardet.detect(check_param).get("encoding")
    return check_param

def get_file_share_apache2_http_eip(ctx):

    eip_addr = ''
    ret = ctx.pgm.get_file_share_service_eip_addr()
    if ret:
        eip_addr = ret
        return eip_addr

    return eip_addr

def get_file_share_apache2_http_ip(ctx):

    private_ip = ''
    ret = ctx.pgm.get_file_share_service_private_ip()
    if ret:
        private_ip = ret

    return private_ip

def get_file_share_service_loaded_clone_instance_ip(ctx):

    loaded_clone_instance_ip = ''
    ret = ctx.pgm.get_file_share_service_loaded_clone_instance_ip()
    if ret:
        loaded_clone_instance_ip = ret

    return loaded_clone_instance_ip

def get_mnt_node_total_size(ctx,vnas_node_dir):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                cmd = "df -h --block-size=k  %s | awk 'NR==2 {print $2}'" % (vnas_node_dir)
                ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                (_, output, _) = ret
                if ret != None and ret[0] == 0:
                    return output
        return 0

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        df_cmd = "df -h --block-size=k  %s | awk 'NR==2 {print $2}'"  %(vnas_node_dir)
        cmd = 'sshpass -p %s ssh ubuntu@%s "echo %s | sudo -S %s" > /tmp/result' % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        df_cmd
        )
        ret = exec_cmd(cmd=cmd, timeout=30)
        if ret != None and ret[0] == 0:
            cmd = "cat /tmp/result |awk 'NR==1 {print $2}'"
            ret = exec_cmd(cmd=cmd, timeout=30)
            (_, output, _) = ret
            if ret != None and ret[0] == 0:
                return output
        return 0

    else:
        logger.error("invalid zone_deploy [%s]" % (ctx.zone_deploy))
        return False

def get_mnt_node_used_size(ctx,vnas_node_dir):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                cmd = "df -h --block-size=k  %s | awk 'NR==2 {print $3}'" % (vnas_node_dir)
                ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                (_, output, _) = ret
                if ret != None and ret[0] == 0:
                    return output
        return 0

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        # df -h --block-size=k  %s | awk 'NR==2 {print $3}'
        df_cmd = "df -h --block-size=k  %s | awk 'NR==2 {print $3}'"  %(vnas_node_dir)
        cmd = 'sshpass -p %s ssh ubuntu@%s "echo %s | sudo -S %s" > /tmp/result' % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        df_cmd
        )
        ret = exec_cmd(cmd=cmd, timeout=30)
        if ret != None and ret[0] == 0:
            cmd = "cat /tmp/result |awk 'NR==1 {print $3}'"
            ret = exec_cmd(cmd=cmd, timeout=30)
            (_, output, _) = ret
            if ret != None and ret[0] == 0:
                return output
        return 0
    else:
        logger.error("invalid zone_deploy [%s]" % (ctx.zone_deploy))
        return False

def get_mnt_node_remain_size(ctx, vnas_node_dir):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                cmd = "df -h --block-size=k  %s | awk 'NR==2 {print $4}'" % (vnas_node_dir)
                ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                (_, output, _) = ret
                if ret != None and ret[0] == 0:
                    return output
        return 0

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        # df -h --block-size=k  %s | awk 'NR==2 {print $4}'
        df_cmd = "df -h --block-size=k  %s | awk 'NR==2 {print $4}'" % (vnas_node_dir)
        cmd = 'sshpass -p %s ssh ubuntu@%s "echo %s | sudo -S %s" > /tmp/result' % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        df_cmd
        )
        ret = exec_cmd(cmd=cmd, timeout=30)
        if ret != None and ret[0] == 0:
            cmd = "cat /tmp/result |awk 'NR==1 {print $4}'"
            ret = exec_cmd(cmd=cmd, timeout=30)
            (_, output, _) = ret
            if ret != None and ret[0] == 0:
                return output
        return 0

    else:
        logger.error("invalid zone_deploy [%s]" % (ctx.zone_deploy))
        return False

def get_local_desktop_server_mnt_node_remain_size(ctx,vnas_node_dir):

    cmd = "df -h --block-size=k  %s | awk 'NR==2 {print $4}'" %(vnas_node_dir)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def check_download_file_uri(ctx, file_path):

    remote_host = get_file_share_apache2_http_ip(ctx)

    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                cmd = "ls  %s" % (file_path)
                ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
                if ret != None and ret[0] == 0:
                    return True
        return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        # ls  /mnt/nasdata
        cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S ls  /mnt/nasdata'" % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD
        )

        ret = exec_cmd(cmd=cmd, timeout=30)
        if ret != None and ret[0] == 0:
            return True
        return False

    else:
        logger.error("invalid zone_deploy [%s]" %(ctx.zone_deploy))
        return False

def create_file_share_dir(ctx,dir_path):

    cmd = "mkdir -p %s  && chmod 777 %s" %(dir_path,dir_path)
    logger.info("cmd == %s" % (cmd))
    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
            if ret != None and ret[0] == 0:
                return True
    return False

def rm_file_share_dir(ctx,dir_path):

    cmd = "rm -fr  %s" %(dir_path)
    logger.info("cmd == %s" %(cmd))
    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
            if ret != None and ret[0] == 0:
                return True
    return False

def mv_file_share_dir(ctx,source_path,destination_path):

    cmd = "mv %s %s" %(source_path,destination_path)
    logger.info("cmd == %s" % (cmd))
    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22,timeout=6000)
            if ret != None and ret[0] == 0:
                return True
    return False

def cp_file_share_dir(ctx,source_path,destination_path):

    remote_host = get_file_share_apache2_http_ip(ctx)

    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                cmd = "flock x cp -fr  %s %s" % (source_path, destination_path)
                ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
                if ret != None and ret[0] == 0:
                    # chown -Rf virtual:virtual /mnt/nasdata/build-iso-dir-new/Citrix-APIs-BrokerAPP.md
                    cmd = "chown -Rf virtual:virtual %s" % (destination_path)
                    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                    if ret != None and ret[0] == 0:
                        return True
                    return False
            return False
        return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        # flock x cp -fr  %s %s
        cp_cmd = "flock x cp -fr  %s %s" % (source_path, destination_path)
        cmd = 'sshpass -p %s ssh ubuntu@%s "echo %s | sudo -S %s" ' % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        cp_cmd
        )

        ret = exec_cmd(cmd=cmd, timeout=30)
        if ret != None and ret[0] == 0:
            # chown -Rf virtual:virtual /mnt/nasdata/build-iso-dir-new/Citrix-APIs-BrokerAPP.md
            chown_cmd = "chown -Rf virtual:virtual %s" %(destination_path)
            cmd = 'sshpass -p %s ssh ubuntu@%s "echo %s | sudo -S %s" ' % (
            const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
            remote_host,
            const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
            chown_cmd
            )
            ret = exec_cmd(cmd=cmd, timeout=30)
            if ret != None and ret[0] == 0:
                return True
            return False
        return False
    else:
        logger.error("invalid zone_deploy [%s]" % (ctx.zone_deploy))

    return False

def scp_file_share_dir(ctx,source_path):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        cmd = "scp -r %s root@%s:/mnt/nasdata" %(source_path,remote_host)
        logger.info("cmd == %s" % (cmd))
        ret = exec_cmd(cmd=cmd)
        if ret != None and ret[0] == 0:
            return True
    return False

def rm_desktop_server_local_file(ctx,dir_path):

    cmd = "rm -fr  %s" %(dir_path)
    logger.info("cmd == %s" %(cmd))

    ret = exec_cmd(cmd=cmd)
    if ret != None and ret[0] == 0:
        return True
    return False

def dn_to_path(dn):

    path_str = copy.deepcopy(dn)
    path_str = path_str[:path_str.replace('DC=','dc=').index('dc=')-1].replace('ou=','').replace('OU=','').replace('CN=','').replace('cn=','')
    path_list = path_str.split(',')
    path_list.reverse()
    path = '/'
    for path_item in path_list:
        path = path + path_item
        path = path + '/'
    path = path[:len(path)-1]

    return path

def rename_filename(filename,suffix_string="Delete_At"):

    filename_list = filename.split('.')
    for item in filename_list[:]:
        if const.FILE_SHARE_SUFFIX_STRING_DUPLICATE in item:
            filename_list.remove(item)
        elif const.FILE_SHARE_SUFFIX_STRING_DELETE in item:
            filename_list.remove(item)
        elif const.FILE_SHARE_SUFFIX_STRING_RESTORE in item:
            filename_list.remove(item)
        else:
            continue

    filename_list.insert(-1, "%s_%s"%(suffix_string,redefine_format_timestamp(get_current_timestamp())))
    new_filename = ".".join(filename_list)

    return new_filename

def get_desktop_server_instance_id():

    cmd = "cat /etc/hosts | grep 127.0.1.1 | awk '{print $2}'"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_target_host_list(ctx):

    num_of_desktop_server = 0
    ret = ctx.pgm.get_desktop_service_managements(service_type=const.LOADBALANCER_SERVICE_TYPE)
    if ret:
        num_of_desktop_server = len(ret)

    if num_of_desktop_server == 2:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_2
    elif num_of_desktop_server == 4:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_4
    elif num_of_desktop_server == 6:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_6
    elif num_of_desktop_server == 8:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_8
    else:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_2

    return target_host_list

def check_uploaded_file_exist(ctx,file_path):

    cmd = "ls -l %s" %(file_path)
    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
            if ret != None and ret[0] == 0:
                return True
    return False

def search_folder(ctx,root_folder):

    cmd = "ls -l %s | grep ^d | awk '{print $9}'" %(root_folder)
    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
            (_,output,_) = ret
            if ret != None and ret[0] == 0:
                return output
    return 0

def search_folder_file(ctx,root_folder):

    cmd = "ls -l %s | grep ^- | awk '{print $9}'" %(root_folder)
    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
            (_,output,_) = ret
            if ret != None and ret[0] == 0:
                return output
    return 0

def get_folder_file_size(ctx, folder_file):

    cmd = "ls -lh  %s --block-size=k | awk '{print $5}' | sed  's/K//g'" %(folder_file)
    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
            (_,output,_) = ret
            if ret != None and ret[0] == 0:
                if not output:
                    return 0
                return output
    return 0

def check_host_valid(host):

    cmd = "ping %s > ping.log" %(host)
    ret = exec_cmd(cmd=cmd,timeout=3,suppress_log=True)

    cmd = "cat ping.log |grep ttl"
    ret = exec_cmd(cmd=cmd,suppress_log=True)
    (_, output, _) = ret
    if ret != None and ret[0] == 0:
        return True
    return False

def modify_nginx_limit(ctx,limit_rate,limit_conn):

    cmd_limit_rate = "sed -i 's/limit_rate .*m/limit_rate %sm/g' /etc/nginx/sites-available/vdi-portal-cross-domain" %(limit_rate)
    cmd_limit_conn = "sed -i 's/limit_conn one .*/limit_conn one %s;/g' /etc/nginx/sites-available/vdi-portal-cross-domain" %(limit_conn)
    cmd_restart_nginx = "/etc/init.d/nginx restart"
    cmd_modify_nginx_limit = "%s && %s && %s" %(cmd_limit_rate,cmd_limit_conn,cmd_restart_nginx)
    logger.info("cmd_modify_nginx_limit == %s" %(cmd_modify_nginx_limit))
    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        if is_port_open(host=remote_host, port=22):
            ret = _exec_cmd(cmd=cmd_modify_nginx_limit,remote_host=remote_host,ssh_port=22)
            (_,output,_) = ret
            if ret != None and ret[0] == 0:
                return True
    return False

def modify_vsfpd_limit_rate(ctx,limit_rate):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                cmd = "sed -i 's/anon_max_rate=.*/anon_max_rate=%d/g'  /etc/vsftpd.conf" % (limit_rate)
                ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22)
                if ret != None and ret[0] == 0:
                    return True
        return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        # sed -i 's/anon_max_rate=.*/anon_max_rate=%d/g'  /etc/vsftpd.conf
        cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S sed -i 's/anon_max_rate=.*/anon_max_rate=%d/g'  /etc/vsftpd.conf'" % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        limit_rate)

        ret = exec_cmd(cmd=cmd, timeout=300,suppress_log=True)
        if ret != None and ret[0] == 0:
            return True
        return False

    else:
        logger.error("invalid zone_deploy [%s]" %(ctx.zone_deploy))
        return False

def modify_vsfpd_limit_conn(ctx,limit_conn):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                cmd = "sed -i 's/max_per_ip=.*/max_per_ip=%d/g'  /etc/vsftpd.conf" % (limit_conn)
                ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                if ret != None and ret[0] == 0:
                    return True
        return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        # sed -i 's/max_per_ip=.*/max_per_ip=%d/g'  /etc/vsftpd.conf
        cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S sed -i 's/max_per_ip=.*/max_per_ip=%d/g'  /etc/vsftpd.conf'" % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        limit_conn)

        ret = exec_cmd(cmd=cmd, timeout=300,suppress_log=True)
        if ret != None and ret[0] == 0:
            return True
        return False

    else:
        logger.error("invalid zone_deploy [%s]" % (ctx.zone_deploy))
        return False

def restart_vsftpd_service(ctx):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                cmd = "/etc/init.d/vsftpd restart"
                ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22,timeout=300)
                if ret != None and ret[0] == 0:
                    return True
        return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        # /etc/init.d/vsftpd restart
        cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S /etc/init.d/vsftpd restart'" % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD
        )

        ret = exec_cmd(cmd=cmd, timeout=300,suppress_log=True)
        if ret != None and ret[0] == 0:
            return True
        return False

    else:
        logger.error("invalid zone_deploy [%s]" % (ctx.zone_deploy))
    return False

def get_file_share_service_ftp_ip(ctx):

    ftp_ip = ''
    ret = ctx.pgm.get_file_share_service_private_ip()
    if ret:
        ftp_ip = ret

    return ftp_ip

def get_file_share_service_ftp_username(ctx):

    ftp_username = ''
    ret = ctx.pgm.get_file_share_service_fuser()
    if ret:
        ftp_username = ret

    return ftp_username

def get_file_share_service_ftp_password(ctx):

    ftp_password = ''
    ret = ctx.pgm.get_file_share_service_fpw()
    if ret:
        ftp_password = ret

    ftp_password = get_base64_password(ftp_password)

    return ftp_password

def  get_ftp_chinese_encoding_rules(ctx):

    ftp_chinese_encoding_rules = const.FTP_SERVER_CHINESE_ENCODING_RULES_UTF_8
    ret = ctx.pgm.get_file_share_service_ftp_chinese_encoding_rules()
    if ret:
        ftp_chinese_encoding_rules = ret

    return ftp_chinese_encoding_rules

def  get_file_share_service_id(ctx):

    file_share_service_id = ''
    ret = ctx.pgm.get_file_share_service_id()
    if ret:
        file_share_service_id = ret

    return file_share_service_id

def update_file_share_service_ftp_chinese_encoding_rules(ctx,file_share_service_id,ftp_chinese_encoding_rules):

    condition = {"file_share_service_id": file_share_service_id}
    update_info = dict(
        ftp_chinese_encoding_rules=ftp_chinese_encoding_rules,
    )

    if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_SERVICE, condition, update_info):
        logger.error("update file share service for [%s] to db failed" % (update_info))
        return -1

    return 0

def search_remote_ftp_server_folder(ctx,root_folder):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    root_folder = format_file_share_gbk_param(ctx,root_folder)

    exec_script = "%s/search_remote_ftp_server_folder.sh -u %s -w %s -p %s -l %s -d %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                          ftp_username,
                                                                                          ftp_password,
                                                                                          ftp_ip,
                                                                                          const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                          root_folder)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))

    file_share_service_id = get_file_share_service_id(ctx)

    # update file_share_service ftp_chinese_encoding_rules
    cmd = "file -i /pitrix/conf/configure_vsftp/nlist  | grep iso-8859-1"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        if output:
            ftp_chinese_encoding_rules = const.FTP_SERVER_CHINESE_ENCODING_RULES_GBK
            ret = update_file_share_service_ftp_chinese_encoding_rules(ctx, file_share_service_id, ftp_chinese_encoding_rules)

    cmd = "file -i /pitrix/conf/configure_vsftp/nlist  | grep utf-8"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        if output:
            ftp_chinese_encoding_rules = const.FTP_SERVER_CHINESE_ENCODING_RULES_UTF_8
            ret = update_file_share_service_ftp_chinese_encoding_rules(ctx, file_share_service_id,ftp_chinese_encoding_rules)

    cmd = "cat %s/nlist | grep ^d | awk '{print $9}'" %(const.FILE_SHARE_VSFTP_LOCAL_DIR)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def search_remote_ftp_server_folder_file(ctx,root_folder):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    root_folder = format_file_share_gbk_param(ctx,root_folder)

    exec_script = "%s/search_remote_ftp_server_folder.sh -u %s -w %s -p %s -l %s -d %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                ftp_username,
                                                                                                ftp_password,
                                                                                                ftp_ip,
                                                                                                const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                root_folder)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))

    cmd = "cat %s/nlist | grep ^- | awk '{print $9}'" %(const.FILE_SHARE_VSFTP_LOCAL_DIR)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def get_remote_ftp_server_folder_file_size(ctx, folder_file):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    folder_file = format_file_share_gbk_param(ctx,folder_file)

    exec_script = "%s/get_remote_ftp_server_folder_file_size.sh -u %s -w %s -p %s -l %s -d %s -f %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                ftp_username,
                                                                                                ftp_password,
                                                                                                ftp_ip,
                                                                                                const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                folder_file)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))

    cmd = "cat %s/ls_info | awk '{print $5}'" %(const.FILE_SHARE_VSFTP_LOCAL_DIR)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def create_remote_ftp_server_file_share_dir(ctx,dir_path):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    dir_path = format_file_share_gbk_param(ctx,dir_path)

    exec_script = "%s/create_remote_ftp_server_file_share_dir.sh -u %s -w %s -p %s -l %s -d %s -a %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                        ftp_username,
                                                                                                        ftp_password,
                                                                                                        ftp_ip,
                                                                                                        const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                        const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                        dir_path)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))

    cmd = "cat /pitrix/log/install/create_remote_ftp_server_file_share_dir.log | grep 'Failed to change directory.'"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def rename_remote_ftp_server_file_share_dir(ctx,source_path,destination_path):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    source_path = format_file_share_gbk_param(ctx,source_path)
    destination_path = format_file_share_gbk_param(ctx,destination_path)

    exec_script = "%s/rename_remote_ftp_server_file_share_dir.sh -u %s -w %s -p %s -l %s -d %s -s %s -e %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                                ftp_username,
                                                                                                                ftp_password,
                                                                                                                ftp_ip,
                                                                                                                const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                                const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                                source_path,
                                                                                                                destination_path)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))

    cmd = "cat /pitrix/log/install/rename_remote_ftp_server_file_share_dir.log | grep 'Failed to change directory.'"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def rmdir_remote_ftp_server_file_share_dir(ctx,dir_path):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    dir_path = format_file_share_gbk_param(ctx,dir_path)
    exec_script = "%s/rmdir_remote_ftp_server_file_share_dir.sh -u %s -w %s -p %s -l %s -d %s -s %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                        ftp_username,
                                                                                                        ftp_password,
                                                                                                        ftp_ip,
                                                                                                        const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                        const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                        dir_path)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))

    cmd = "cat /pitrix/log/install/rmdir_remote_ftp_server_file_share_dir.log | grep 'Failed to change directory.'"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def rename_remote_ftp_server_file_share_file(ctx,source_path,destination_path,file_share_group_file_id,action_type):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    source_path = format_file_share_gbk_param(ctx,source_path)
    destination_path = format_file_share_gbk_param(ctx,destination_path)

    global rename_remote_ftp_server_file_share_file_lock
    rename_remote_ftp_server_file_share_file_lock.acquire()
    exec_script = "%s/rename_remote_ftp_server_file_share_file.sh -u %s -w %s -p %s -l %s -d %s -s %s -e %s -a %s -t %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                                            ftp_username,
                                                                                                                            ftp_password,
                                                                                                                            ftp_ip,
                                                                                                                            const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                                            const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                                            source_path,
                                                                                                                            destination_path,
                                                                                                                            file_share_group_file_id,
                                                                                                                            action_type)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))
    rename_remote_ftp_server_file_share_file_lock.release()

    cmd = "cat %s/%s_%s_info" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,action_type,file_share_group_file_id)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def check_remote_ftp_server_file_share_dir(ctx,dir_path):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    dir_path = format_file_share_gbk_param(ctx, dir_path)

    global check_remote_ftp_server_file_share_dir_lock
    check_remote_ftp_server_file_share_dir_lock.acquire()
    exec_script = "%s/check_remote_ftp_server_file_share_dir.sh -u %s -w %s -p %s -l %s -d %s -s %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                        ftp_username,
                                                                                                        ftp_password,
                                                                                                        ftp_ip,
                                                                                                        const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                        const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                        dir_path)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))
    check_remote_ftp_server_file_share_dir_lock.release()

    cmd = "cat %s/check_remote_ftp_server_file_share_dir.result" % (const.FILE_SHARE_VSFTP_LOCAL_DIR)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def check_remote_ftp_server_file_share_file(ctx,file_path,file_share_group_file_name):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    file_path = format_file_share_gbk_param(ctx, file_path)

    global check_remote_ftp_server_file_share_file_lock
    check_remote_ftp_server_file_share_file_lock.acquire()
    exec_script = "%s/check_remote_ftp_server_file_share_file.sh -u %s -w %s -p %s -l %s -d %s -f %s -a %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                            ftp_username,
                                                                                                            ftp_password,
                                                                                                            ftp_ip,
                                                                                                            const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                            const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                            file_path,
                                                                                                            file_share_group_file_name)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))
    check_remote_ftp_server_file_share_file_lock.release()

    cmd = "cat %s/check_remote_ftp_server_file_share_file.result" % (const.FILE_SHARE_VSFTP_LOCAL_DIR)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def upload_file_to_remote_ftp_server(ctx,file_share_group_file_name,destination_path):
    logger.info("upload_file_to_remote_ftp_server file_share_group_file_name == %s destination_path == %s" %(file_share_group_file_name,destination_path))
    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    # If you want to send the local 1.htm to the remote host /usr/your, and rename it to 2.htm
    # ftp > put 1.htm /usr/your/2.htm

    destination_path = format_file_share_gbk_param(ctx, destination_path)

    exec_script = "%s/upload_file_to_remote_ftp_server.sh -u %s -w %s -p %s -l %s -d %s -s %s -e %s" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                    ftp_username,
                                                                                                    ftp_password,
                                                                                                    ftp_ip,
                                                                                                    const.DOWNLOAD_SOFTWARE_BASE_URI,
                                                                                                    const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                    file_share_group_file_name,
                                                                                                    destination_path)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))

    cmd = "cat %s/%s_info" %(const.DOWNLOAD_SOFTWARE_BASE_URI,file_share_group_file_name)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def delete_remote_ftp_server_file_share_file(ctx,file_path,file_share_group_file_id,action_type):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    file_path = format_file_share_gbk_param(ctx, file_path)

    global delete_remote_ftp_server_file_share_file_lock
    delete_remote_ftp_server_file_share_file_lock.acquire()
    exec_script = "%s/delete_remote_ftp_server_file_share_file.sh -u %s -w %s -p %s -l %s -d %s -f %s -i %s -t %s" % (const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                                      ftp_username,
                                                                                                                      ftp_password,
                                                                                                                      ftp_ip,
                                                                                                                      const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                                      const.FILE_SHARE_SERVICE_FTP_SERVER_BASE_DIR,
                                                                                                                      file_path,
                                                                                                                      file_share_group_file_id,
                                                                                                                      action_type)
    cmd = ("/bin/bash %s" % (exec_script))
    os.system("%s" % (cmd))
    delete_remote_ftp_server_file_share_file_lock.release()

    cmd = "cat %s/%s_%s_info" %(const.FILE_SHARE_VSFTP_LOCAL_DIR,action_type,file_share_group_file_id)
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return 0

def reset_remote_ftp_server_vsftp_password(ctx,ftp_username,ftp_password):

    exec_script = "/pitrix/conf/configure_vsftp/configure_vsftp.sh -u %s -w %s" %(ftp_username,ftp_password)
    cmd = ("/bin/bash %s" % (exec_script))
    remote_host = get_file_share_apache2_http_ip(ctx)
    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if remote_host:
            if is_port_open(host=remote_host, port=22):
                ret = _exec_cmd(cmd=cmd,remote_host=remote_host,ssh_port=22,suppress_log=True)
                if ret != None and ret[0] == 0:
                    return True
        return False
    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S /bin/bash %s'" % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        exec_script
        )

        ret = exec_cmd(cmd=cmd, timeout=300,suppress_log=True)
        if ret != None and ret[0] == 0:
            return True
        return False
    else:
        logger.error("invalid zone_deploy [%s]" %(ctx.zone_deploy))
        return False

def scp_file_to_remote_ftp_server(ctx, source_path, destination_path):

    remote_host = get_file_share_apache2_http_ip(ctx)
    if remote_host:
        cmd = "scp -r %s root@%s:%s" % (source_path, remote_host,destination_path)
        ret = exec_cmd(cmd=cmd,timeout=1200)
        if ret != None and ret[0] == 0:
            # chown -Rf virtual:virtual /mnt/nasdata/build-iso-dir-new/Citrix-APIs-BrokerAPP.md
            cmd = "chown -Rf virtual:virtual %s" % (destination_path)
            ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
            if ret != None and ret[0] == 0:
                return True
            return False

    return False

def get_remote_ftp_server_file_to_remote_cloned_instance_mnt_nasdata(ctx,ftp_dir_name,file_name):

    ftp_ip = get_file_share_service_ftp_ip(ctx)
    ftp_username = get_file_share_service_ftp_username(ctx)
    ftp_password = get_file_share_service_ftp_password(ctx)

    ftp_dir_name = format_file_share_gbk_param(ctx, ftp_dir_name)
    file_name = format_file_share_gbk_param(ctx, file_name)

    remote_host = get_file_share_service_loaded_clone_instance_ip(ctx)
    if not remote_host:
        return False

    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        cmd = "scp -r /pitrix/conf/configure_vsftp/get_remote_ftp_server_file_share_file.sh root@%s:/pitrix/conf/configure_vsftp/" % (remote_host)
        ret = exec_cmd(cmd=cmd,timeout=60)
        if ret != None and ret[0] == 0:
            cmd = "%s/get_remote_ftp_server_file_share_file.sh -u %s -w %s -p %s -l %s -d %s -f %s" % (
                                                                                                        const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                        ftp_username,
                                                                                                        ftp_password,
                                                                                                        ftp_ip,
                                                                                                        const.DOWNLOAD_SOFTWARE_BASE_URI,
                                                                                                        ftp_dir_name,
                                                                                                        file_name)
            ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22,timeout=600,suppress_warning=True,suppress_log=True,ignore_all_log=True)
            (_,output,_) = ret
            if ret != None and ret[0] == 0:
                return True
            return False
        return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        scp_cmd = "sshpass -p '%s' scp -r /pitrix/conf/configure_vsftp/get_remote_ftp_server_file_share_file.sh ubuntu@%s:/pitrix/conf/configure_vsftp/" % (const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,remote_host)
        ret = exec_cmd(cmd=scp_cmd, timeout=300,suppress_log=False)
        if ret != None and ret[0] == 0:
            get_cmd = "%s/get_remote_ftp_server_file_share_file.sh -u %s -w %s -p %s -l %s -d %s -f %s" % (
                                                                                                        const.FILE_SHARE_VSFTP_LOCAL_DIR,
                                                                                                        ftp_username,
                                                                                                        ftp_password,
                                                                                                        ftp_ip,
                                                                                                        const.DOWNLOAD_SOFTWARE_BASE_URI,
                                                                                                        ftp_dir_name,
                                                                                                        file_name)
            logger.info("get_cmd == %s" %(get_cmd))
            cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
                const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                remote_host,
                const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                get_cmd
            )
            logger.info("cmd == %s" % (cmd))
            ret = exec_cmd(cmd=cmd, timeout=300, suppress_log=False)
            if ret != None and ret[0] == 0:
                return True
            return False
        return False
    else:
        logger.error("invalid zone_deploy [%s]" %(ctx.zone_deploy))
        return False

def get_desktop_server_instance_ip():

    cmd = "cat /etc/hosts | grep vdi0 | awk '{print $1}'"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def scp_file_to_remote_cloned_instance(ctx,file_path,dir_path):

    remote_host = get_file_share_service_loaded_clone_instance_ip(ctx)
    if not remote_host:
        return False

    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        cmd = "chmod -R 777 /mnt/nasdata && mkdir -p %s" % (dir_path)
        ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
        if ret != None and ret[0] == 0:
            cmd = "scp -r %s root@%s:%s" % (file_path, remote_host, dir_path)
            ret = exec_cmd(cmd=cmd)
            if ret != None and ret[0] == 0:
                return True
        return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        chmod_cmd = "chmod -R 777 /mnt/nasdata && mkdir -p %s" % (dir_path)
        cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        chmod_cmd
        )
        ret = exec_cmd(cmd=cmd, timeout=300,suppress_log=False)
        if ret != None and ret[0] == 0:
            scp_cmd = "sshpass -p '%s' scp -r %s ubuntu@%s:%s" % (const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,file_path, remote_host, dir_path)
            logger.info("scp_cmd == %s" %(scp_cmd))
            ret = exec_cmd(cmd=scp_cmd, timeout=300, suppress_log=False)
            if ret != None and ret[0] == 0:
                return True
        return False
    else:
        logger.error("invalid zone_deploy [%s]" %(ctx.zone_deploy))
        return False

def check_remote_cloned_instance_mnt_nasdata_file_exist_status(ctx,destination_path,file_share_group_file_size):

    remote_host = get_file_share_service_loaded_clone_instance_ip(ctx)
    if not remote_host:
        return False

    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        cmd = "stat %s | grep Size | awk -F: '{print $2}' | awk '{print $1}'" % (destination_path)
        ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
        (_,output,_) = ret
        if ret != None and ret[0] == 0:
            output = output.strip()
            file_share_group_file_size = str(file_share_group_file_size).strip()
            if output == file_share_group_file_size:
                return True
            return False
        return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        ls_cmd = "ls %s" % (destination_path)
        cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        remote_host,
        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
        ls_cmd
        )
        ret = exec_cmd(cmd=cmd, timeout=300,suppress_log=False)
        (_, output, _) = ret
        logger.info("output == %s" %(output))
        if ret != None and ret[0] == 0:
            return True
        return False
    else:
        logger.error("invalid zone_deploy [%s]" %(ctx.zone_deploy))
        return False

def refresh_remote_cloned_instance_mnt_nasdata_file(ctx,file_path,dir_path):

    remote_host = get_file_share_service_loaded_clone_instance_ip(ctx)
    if not remote_host:
        return False

    # check ftp_chinese_encoding_rules
    ftp_chinese_encoding_rules = get_ftp_chinese_encoding_rules(ctx)
    if const.FTP_SERVER_CHINESE_ENCODING_RULES_GBK == ftp_chinese_encoding_rules:
        file_path_gbk = file_path.decode('utf-8').encode('gbk')
        file_path_utf8 = file_path

    # check file_path chardet encoding utf-8 or ascii
    file_path_chardet=chardet.detect(file_path)
    encoding = file_path_chardet.get("encoding")
    logger.info("encoding == %s" %(encoding))

    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        if const.FTP_SERVER_CHINESE_ENCODING_RULES_ASCII == encoding:
            cmd = "chmod -R 777 /mnt/nasdata && mkdir -p %s" % (dir_path)
            ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
            if ret != None and ret[0] == 0:
                cmd = "mv %s %s" % (file_path, dir_path)
                ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                if ret != None and ret[0] == 0:
                    return True
        elif const.FTP_SERVER_CHINESE_ENCODING_RULES_UTF_8 == encoding:
            if const.FTP_SERVER_CHINESE_ENCODING_RULES_GBK == ftp_chinese_encoding_rules:
                cmd = "chmod -R 777 /mnt/nasdata && mkdir -p %s" % (dir_path)
                ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                if ret != None and ret[0] == 0:
                    cmd = "mv  %s %s" % (file_path_gbk,file_path_utf8)
                    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                    if ret != None and ret[0] == 0:
                        cmd = "mv %s %s" % (file_path_utf8, dir_path)
                        ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                        if ret != None and ret[0] == 0:
                            return True
            elif const.FTP_SERVER_CHINESE_ENCODING_RULES_UTF_8 == ftp_chinese_encoding_rules:
                cmd = "chmod -R 777 /mnt/nasdata && mkdir -p %s" % (dir_path)
                ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                if ret != None and ret[0] == 0:
                    cmd = "mv %s %s" % (file_path, dir_path)
                    ret = _exec_cmd(cmd=cmd, remote_host=remote_host, ssh_port=22)
                    if ret != None and ret[0] == 0:
                        return True
        else:
            logger.error("invalid encoding [%s]" %(encoding))
            return False

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:
        if const.FTP_SERVER_CHINESE_ENCODING_RULES_ASCII == encoding:
            chmod_cmd = "chmod -R 777 /mnt/nasdata && mkdir -p %s" % (dir_path)
            cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
                const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                remote_host,
                const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                chmod_cmd
            )
            ret = exec_cmd(cmd=cmd, timeout=300, suppress_log=False)
            if ret != None and ret[0] == 0:
                mv_cmd = "mv %s %s" % (file_path, dir_path)
                cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
                    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                    remote_host,
                    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                    mv_cmd
                )
                ret = exec_cmd(cmd=cmd, timeout=300, suppress_log=False)
                if ret != None and ret[0] == 0:
                    return True
        elif const.FTP_SERVER_CHINESE_ENCODING_RULES_UTF_8 == encoding:
            if const.FTP_SERVER_CHINESE_ENCODING_RULES_GBK == ftp_chinese_encoding_rules:
                chmod_cmd = "chmod -R 777 /mnt/nasdata && mkdir -p %s" % (dir_path)
                cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
                    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                    remote_host,
                    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                    chmod_cmd
                )
                ret = exec_cmd(cmd=cmd, timeout=300, suppress_log=False)
                if ret != None and ret[0] == 0:
                    mv_cmd = "mv  %s %s" % (file_path_gbk,file_path_utf8)
                    cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
                        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                        remote_host,
                        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                        mv_cmd
                    )
                    ret = exec_cmd(cmd=cmd, timeout=300, suppress_log=False)
                    if ret != None and ret[0] == 0:
                        mv_cmd = "mv %s %s" % (file_path_utf8, dir_path)
                        cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
                            const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                            remote_host,
                            const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                            mv_cmd
                        )
                        ret = exec_cmd(cmd=cmd, timeout=300, suppress_log=False)
                        if ret != None and ret[0] == 0:
                            return True
            elif const.FTP_SERVER_CHINESE_ENCODING_RULES_UTF_8 == ftp_chinese_encoding_rules:
                chmod_cmd = "chmod -R 777 /mnt/nasdata && mkdir -p %s" % (dir_path)
                cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
                    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                    remote_host,
                    const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                    chmod_cmd
                )
                ret = exec_cmd(cmd=cmd, timeout=300, suppress_log=False)
                if ret != None and ret[0] == 0:
                    mv_cmd = "mv %s %s" % (file_path, dir_path)
                    cmd = "sshpass -p '%s' ssh ubuntu@%s 'echo %s | sudo -S %s'" % (
                        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                        remote_host,
                        const.FILE_SHARE_SERVICE_DEFAULT_LOGIN_PASSWORD,
                        mv_cmd
                    )
                    ret = exec_cmd(cmd=cmd, timeout=300, suppress_log=False)
                    if ret != None and ret[0] == 0:
                        return True
        else:
            logger.error("invalid encoding [%s]" %(encoding))
            return False
    else:
        logger.error("invalid zone_deploy [%s]" %(ctx.zone_deploy))
        return False


