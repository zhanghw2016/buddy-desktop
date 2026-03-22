'''
Created on 2012-10-17

@author: yunify
'''
import context
import os
from log.logger import logger
from utils.misc import get_current_time,exec_cmd,get_current_timestamp,redefine_format_timestamp
from utils.net import get_hostname

def check_pitrix_log_size():

    cmd = "du -s /pitrix/log | awk  '{print $1}'"
    ret = exec_cmd(cmd=cmd)
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def check_clean_up_log():

    current_hostname = get_hostname()
    # clean up /tmp/sidud6cceqt2knk6kw1adw73pqm4746f6p2
    os.system("rm -fr /tmp/sid*")

    #  move /pitrix/log/ to vnas /mnt/nasdata/
    ret = check_pitrix_log_size()
    if not ret:
        return None
    pitrix_log_size = ret
    if int(pitrix_log_size) > 1048576:
        logger.info("pitrix_log_size [%s]KB  greater 1048576KB" %(pitrix_log_size))
        # log_wf_name_str = "%s-pitrix.log.wf-%s.tar.gz" % (current_hostname,redefine_format_timestamp(get_current_timestamp()))
        # log_name_str = "%s-pitrix.log-%s.tar.gz" % (current_hostname, redefine_format_timestamp(get_current_timestamp()))

        # tar_log_wf_cmd = 'cd /pitrix/log && find . -name "*.log.wf.[0-9]" | xargs tar -zcvf %s;' %(log_wf_name_str)
        # tar_log_cmd = 'cd /pitrix/log && find . -name "*.log.[0-9]" | xargs tar -zcvf %s;' %(log_name_str)
        # mv_cmd = 'mv /pitrix/log/*tar.gz /mnt/nasdata/'
        rm_log_wf_cmd = 'rm -fr /pitrix/log/*.log.wf.[0-9]'
        rm_log_cmd = 'rm -fr /pitrix/log/*.log.[0-9]'

        # logger.info("tar_log_wf_cmd == %s" %(tar_log_wf_cmd))
        # os.system(tar_log_wf_cmd)
        #
        # logger.info("tar_log_cmd == %s" % (tar_log_cmd))
        # os.system(tar_log_cmd)

        # logger.info("mv_cmd == %s" % (mv_cmd))
        # os.system(mv_cmd)

        logger.info("rm_log_wf_cmd == %s" % (rm_log_wf_cmd))
        os.system(rm_log_wf_cmd)

        logger.info("rm_log_cmd == %s" % (rm_log_cmd))
        os.system(rm_log_cmd)

    else:
        return None

    return None
