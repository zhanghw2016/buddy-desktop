
from connection import DesktopConnection
from log.logger import logger
import constants as const
from vdi import const as Dconst
from resource_job import ResourceJob
import copy
import time

class DesktopResource():

    def __init__(self, zone, conn, http_socket_timeout=120):

        self.zone = zone
        self.conn = DesktopConnection(zone, conn, http_socket_timeout=http_socket_timeout)
        if not self.conn:
            logger.error("create qingcloud connection fail %s" % (self.zone, conn))
            return None
        self.job = ResourceJob(self.conn)
        if not self.job:
            logger.error("QCResrouce Job create fail %s" % self.config)
            return None

    def resource_wait_desktop_jobs_done(self, job_ids, timeout=Dconst.WAIT_JOB_TIMEOUT, interval=Dconst.CHECK_JOB_INTERVAL):
    
        job_status = {}
        
        if not isinstance(job_ids, list):
            job_ids = [job_ids]
        
        check_job_ids = copy.deepcopy(job_ids)
        end_time = time.time() + timeout
        while time.time() < end_time:
            if not check_job_ids:
                return job_status

            ret = self.conn.describe_jobs(check_job_ids)
            if not ret or ret.get("ret_code") != 0:
                logger.error("describe desktop job fail %s" % ret)
                return job_status

            job_set = ret["desktop_job_set"]
            for job in job_set:
                status = job["status"]
                job_id = job["job_id"]
                if status in [const.JOB_STATUS_FAIL, const.JOB_STATUS_SUCC]:
                    job_status[job_id] = status
                    check_job_ids.remove(job_id)

            time.sleep(interval)
        
        if check_job_ids:
            for job_id in check_job_ids:
                job_status[job_id] = const.JOB_STATUS_TIMEOUT
        
        return job_status
    
    def resource_describe_desktop_tasks(self, job_ids):
        
        if not isinstance(job_ids, list):
            job_ids = [job_ids]
        
        ret = self.conn.describe_task(job_ids)
        if not ret or ret.get("ret_code") != 0:
            return None
        
        desktop_task_set = ret["desktop_task_set"]
        desktop_tasks = {}
        
        for desktop_task in desktop_task_set:
            job_id = desktop_task["job_id"]
            desktop_tasks[job_id] = desktop_task
            
        return desktop_tasks

    def check_ret_code(self, action, ret):

        if not ret or ret["ret_code"] != 0:
            logger.error("action %s, return %s" % (action, ret))
            return False
            
        return True

    def resource_describe_desktops(self, desktop_ids):
        
        if not isinstance(desktop_ids, list):
            desktop_ids = [desktop_ids]
        
        ret = self.conn.describe_desktops(desktop_ids)
        if not self.check_ret_code(const.ACTION_VDI_DESCRIBE_DESKTOPS, ret):
            return None

        desktop_set = ret["desktop_set"]
        desktops = {}
        
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            desktops[desktop_id] = desktop
        
        return desktops
         
    def resource_start_desktops(self, desktop_group_id=None, desktop_ids=None):

        if not desktop_group_id and not desktop_ids:
            return None
        
        body = {}
        if desktop_group_id:
            body["desktop_group"] = desktop_group_id
        
        if desktop_ids:
            body["desktops"] = desktop_ids
        
        ret = self.conn.start_desktops(body)
        if not self.check_ret_code(const.ACTION_VDI_START_DESKTOPS, ret):
            logger.error("start desktop return None %s" % desktop_group_id)
            return None

        return ret

    def resource_restart_desktops(self, desktop_group_id=None, desktop_ids=None):

        if not desktop_group_id and not desktop_ids:
            return None
        
        body = {}
        if desktop_group_id:
            body["desktop_group"] = desktop_group_id
        
        if desktop_ids:
            body["desktops"] = desktop_ids
        
        ret = self.conn.restart_desktops(body)
        if not self.check_ret_code(const.ACTION_VDI_RESTART_DESKTOPS, ret):
            return None

        return ret
    
    def resource_stop_desktops(self, desktop_group_id=None, desktop_ids=None):
    
        if not desktop_group_id and not desktop_ids:
            return None
        
        body = {}
        if desktop_group_id:
            body["desktop_group"] = desktop_group_id
        
        if desktop_ids:
            body["desktops"] = desktop_ids
        
        ret = self.conn.stop_desktops(body)
        if not self.check_ret_code(const.ACTION_VDI_STOP_DESKTOPS, ret):
            return None

        return ret

    def resource_modify_desktop_group_attributes(self, desktop_group_id, desktop_count=None, desktop_image=None):
        
        if not desktop_count and not desktop_image:
            return None
        
        body = {"desktop_group": desktop_group_id}
        if desktop_count is not None:
            body["desktop_count"] = desktop_count
        
        if desktop_image:
            body["desktop_image"] = desktop_image
            
        ret = self.conn.modify_desktop_group_attributes(body)
        if not self.check_ret_code(const.ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES, ret):
            return None

        return ret

    def resource_modify_desktop_group_status(self, desktop_group_id, status):

        body = {"desktop_group": desktop_group_id, "status": status}
        ret = self.conn.modify_desktop_group_status(body)
        if not self.check_ret_code(const.ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS, ret):
            return None

        return ret
    
    def resource_apply_desktop_group(self, desktop_group_id):

        body = {"desktop_group": desktop_group_id}
        ret = self.conn.apply_desktop_group(body)
        if not self.check_ret_code(const.ACTION_VDI_APPLY_DESKTOP_GROUP, ret):
            return None
        
        return ret

    def resource_create_desktop_group(self, param):

        ret = self.conn.create_desktop_group(param)
        if not self.check_ret_code(const.ACTION_VDI_CREATE_DESKTOP_GROUP, ret):
            return None
            
        return ret

    def resource_create_app_desktop_group(self, param):

        ret = self.conn.create_app_desktop_group(param)
        if not self.check_ret_code(const.ACTION_VDI_CREATE_APP_DESKTOP_GROUP, ret):
            return None

        return ret

    def resource_add_desktop_to_delivery_group(self, param):
        
        ret = self.conn.add_desktop_to_delivery_group(param)
        if not self.check_ret_code(const.ACTION_VDI_ADD_DESKTOP_TO_DELIVERY_GROUP, ret):
            return None

        return ret
    
    def resource_create_desktop_snapshots(self, snapshot_group_id=None, resource_ids=None,is_full=0):

        if not snapshot_group_id and not resource_ids:
            return None

        body = {}
        if snapshot_group_id:
            body["snapshot_group"] = snapshot_group_id

        if resource_ids:
            body["resources"] = resource_ids

        if is_full is not None:
            body["is_full"] = is_full

        ret = self.conn.create_desktop_snapshots(body)
        if not self.check_ret_code(const.ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS, ret):
            return None

        return ret

    def resource_delete_desktop_snapshots(self, snapshots):

        ret = self.conn.delete_desktop_snapshots(snapshots)
        if not self.check_ret_code(const.ACTION_VDI_DELETE_DESKTOP_SNAPSHOTS, ret):
            return None
        
        job_id = ret["job_id"]
        return job_id
    
    def resource_add_user_to_delivery_group(self, param):

        ret = self.conn.add_user_to_delivery_group(param)
        if not self.check_ret_code(const.ACTION_VDI_ADD_USER_TO_DELIVERY_GROUP, ret):
            return None
        
        return ret

    def resource_del_user_from_delivery_group(self, param):

        ret = self.conn.add_user_to_delivery_group(param)
        if not self.check_ret_code(const.ACTION_VDI_DEL_USER_FROM_DELIVERY_GROUP, ret):
            return None
        
        return ret

    def resource_detach_user_from_desktop(self, param):

        ret = self.conn.detach_user_from_desktop(param)
        if not self.check_ret_code(const.ACTION_VDI_DETACH_USER_FROM_DESKTOP, ret):
            return None
        
        return ret

    def resource_delete_desktops(self, param):

        ret = self.conn.delete_desktops(param)
        if not self.check_ret_code(const.ACTION_VDI_DELETE_DESKTOPS, ret):
            return None
        
        return ret

    def resource_delete_desktop_from_delivery_group(self, param):


        ret = self.conn.delete_desktop_from_delivery_group(param)
        if not self.check_ret_code(const.ACTION_VDI_DEL_DESKTOP_FROM_DELIVERY_GROUP, ret):
            return None
        
        return ret

    def resource_detach_desktop_from_delivery_group_user(self, param):

 
        ret = self.conn.detach_desktop_from_delivery_group_user(param)
        if not self.check_ret_code(const.ACTION_VDI_DETACH_DESKTOP_FROM_DELIVERY_GROUP_USER, ret):
            return None
        
        return ret

    def resource_describe_auth_users(self, auth_service_id, user_names=None, base_dn=None, search_name=None, scope=1, global_search=None):
        
        if user_names and not isinstance(user_names, list):
            user_names = [user_names]
        
        ret = self.conn.describe_auth_users(auth_service_id, user_names, base_dn, search_name, scope, global_search)
        if not self.check_ret_code(const.ACTION_VDI_DESCRIBE_AUTH_USERS, ret):
            return None
        
        return ret
        

    def resource_create_auth_user(self, auth_service_id, user_info):
        
        ret = self.conn.create_auth_user(auth_service_id, user_info)
        if not self.check_ret_code(const.ACTION_VDI_CREATE_AUTH_USER, ret):
            return None
        
        return ret
    
    def resource_modify_auth_user_attributes(self, auth_service_id, user_info):
        
        ret = self.conn.modify_auth_user_attributes(auth_service_id, user_info)
        if not self.check_ret_code(const.ACTION_VDI_MODIFY_AUTH_USER_ATTRIBUTES, ret):
            return None
        
        return ret

    def resource_reset_auth_user_password(self, auth_service_id, user_name, password):
        
        ret = self.conn.reset_auth_user_password(auth_service_id, user_name, password)
        if not self.check_ret_code(const.ACTION_VDI_RESET_AUTH_USER_PASSWORD, ret):
            return None
        
        return ret
        

    def resource_set_auth_user_status(self, auth_service_id, user_names, status):
        
        ret = self.conn.set_auth_user_status(auth_service_id, user_names, status)
        if not self.check_ret_code(const.ACTION_VDI_SET_AUTH_USER_STATUS, ret):
            return None
        
        return ret

    def resource_delete_auth_users(self, auth_service_id, user_names):
        
        if user_names and not isinstance(user_names, list):
            user_names = [user_names]
        
        ret = self.conn.delete_auth_users(auth_service_id, user_names)
        if not self.check_ret_code(const.ACTION_VDI_DELETE_AUTH_USERS, ret):
            return None
        
        return ret
        

    def resource_refresh_auth_service(self, auth_service_id, base_dn):
        ret = self.conn.refresh_auth_service(auth_service_id, base_dn)
        if not self.check_ret_code(const.ACTION_VDI_REFRESH_AUTH_SERVICE, ret):
            return None
        
        return ret

    def resource_describe_auth_ous(self, auth_service_id, base_dn,ou_names,scope, syn_desktop):
        ret = self.conn.resource_describe_auth_ous(auth_service_id, base_dn, ou_names,scope, syn_desktop)
        if not self.check_ret_code(const.ACTION_VDI_DESCRIBE_AUTH_OUS, ret):
            return None
        
        return ret

    def resource_create_auth_ou(self, auth_service_id, base_dn, ou_name, description=''):
        ret = self.conn.create_auth_ou(auth_service_id, base_dn, ou_name, description)
        if not self.check_ret_code(const.ACTION_VDI_CREATE_AUTH_OU, ret):
            return None
        
        return ret
            

    def resource_add_auth_user_to_user_group(self, auth_service_id, user_group_dn, user_names):
        
        if user_names and not isinstance(user_names, list):
            user_names = [user_names]

        ret = self.conn.add_auth_user_to_user_group(auth_service_id, user_group_dn, user_names)
        if not self.check_ret_code(const.ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP, ret):
            return None
        
        return ret
            
    
    def resource_remove_auth_user_from_user_group(self, auth_service_id, user_group_dn, user_names):
        ret = self.conn.remove_auth_user_from_user_group(auth_service_id, user_group_dn, user_names)
        if not self.check_ret_code(const.ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP, ret):
            return None
        
        return ret
        
    