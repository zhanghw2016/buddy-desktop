
from connection import CitrixConnection
from log.logger import logger
from error.error import Error
from citrix import const as Const
from resource_job import ResourceJob
from common import unicode_to_string

class CitrixResource():
        
    def __init__(self, zone, conn, http_socket_timeout=120):

        self.zone = zone
        self.conn = CitrixConnection(zone, conn, http_socket_timeout=http_socket_timeout)
        if not self.conn:
            logger.error("create qingcloud connection fail %s" % (self.zone, conn))
            return None

        self.job = ResourceJob(self.conn)
        if not self.job:
            logger.error("QCResrouce Job create fail %s" % self.config)
            return None

        self.resource_action_map = {
            # job
            Const.ACTION_DESCRIBE_COMPUTER_CATALOGS: self.conn.describe_computer_catalogs,
            Const.ACTION_CREATE_COMPUTER_CATALOG: self.conn.create_computer_catalog,
            Const.ACTION_MODIFY_COMPUTER_CATALOG: self.conn.modify_computer_catalog,
            Const.ACTION_DELETE_COMPUTER_CATALOG: self.conn.delete_computer_catalog,
            Const.ACTION_UPDATE_CATALOG_MASTER_IMAGE: self.conn.update_catalog_master_image,
    
            Const.ACTION_DESCRIBE_DELIVERY_GROUPS: self.conn.describe_delivery_groups,
            Const.ACTION_CREATE_DELIVERY_GROUP: self.conn.create_delivery_group,
            Const.ACTION_MODIFY_DELIVERY_GROUP: self.conn.modify_delivery_group,
            Const.ACTION_DELETE_DELIVERY_GROUP: self.conn.delete_delivery_group,
            Const.ACTION_ATTACH_COMPUTER_TO_DELIVERY_GROUP: self.conn.attach_computer_to_delivery_group,
            Const.ACTION_DETACH_COMPUTER_FROM_DELIVERY_GROUP: self.conn.detach_computer_from_delivery_group,
            Const.ACTION_ATTACH_USER_TO_DELIVERY_GROUP: self.conn.attach_user_to_delivery_group,
            Const.ACTION_DETACH_USER_FROM_DELIVERY_GROUP: self.conn.detach_user_from_delivery_group,
            Const.ACTION_RESET_USER_TO_DELIVERY_GROUP: self.conn.reset_users_to_delivery_group,
            Const.ACTION_SET_DELIVERY_GROUP_MODE: self.conn.set_delivery_group_mode,
            
            Const.ACTION_DESCRIBE_COMPUTERS: self.conn.describe_computers,
            Const.ACTION_CREATE_COMPUTER: self.conn.create_computer,
            Const.ACTION_DELETE_COMPUTER: self.conn.delete_computer,
            Const.ACTION_START_COMPUTER: self.conn.start_computer,
            Const.ACTION_STOP_COMPUTER: self.conn.stop_computer,
            Const.ACTION_RESTART_COMPUTER: self.conn.restart_computer,
            Const.ACTION_ATTACH_COMPUTER_TO_USER: self.conn.attach_computer_to_user, 
            Const.ACTION_DETACH_COMPUTER_FROM_USER: self.conn.detach_computer_from_user,
            Const.ACTION_SET_COMPUTER_MODE: self.conn.set_computer_mode,
            Const.ACTION_RELOAD_IMAGE: self.conn.reload_image,
            Const.ACTION_STOP_BROKER_SESSION: self.conn.stop_broker_session,
            # app
            Const.ACTION_ADD_COMPUTER: self.conn.add_computer,
            Const.ACTION_DELETE_APP_COMPUTER: self.conn.delete_app_computer,
            Const.ACTION_DESCRIBE_APP_STARTMEMU: self.conn.describe_app_start_memu, 
            Const.ACTION_CREATE_BROKER_APP: self.conn.create_broker_app,
            Const.ACTION_MODIFY_BROKER_APP: self.conn.modify_broker_app,
            Const.ACTION_ADD_BROKER_APP: self.conn.add_broker_app,
            Const.ACTION_REMOVE_BROKER_APP: self.conn.remove_broker_app,
            Const.ACTION_DESCRIBE_BROKER_APPS: self.conn.describe_broker_apps,
            Const.ACTION_NEW_BROKER_FOLDER: self.conn.new_broker_folder,
            Const.ACTION_REMOVE_BROKER_FOLDER: self.conn.remove_broker_folder,
            Const.ACTION_DESCRIBE_BROKER_FOLDER: self.conn.describe_broker_folder,
            Const.ACTION_DESCRIBE_BROKER_APP_GROUPS: self.conn.describe_broker_app_groups,
            Const.ACTION_ADD_BROKER_APP_GROUP: self.conn.add_broker_app_group,
            Const.ACTOPN_CREATE_BROKER_APP_GROUP: self.conn.create_broker_app_group,
            Const.ACTOPN_DELETE_BROKER_APP_GROUP: self.conn.delete_broker_app_group,
	    #citrixpolicy
            Const.ACTION_CREATE_CITRIX_POLICY:self.conn.resource_create_citrix_policy,
            Const.ACTION_CONFIG_CITRIX_POLICY_ITEM:self.conn.resource_config_citrix_policy_item,
            Const.ACTION_DESCRIBE_CITRIX_POLICY_ITEM:self.conn.resource_describe_citrix_policy_items,            
            Const.ACTION_DELETE_CITRIX_POLICY:self.conn.resource_delete_citrix_policy,
            Const.ACTION_MODIFY_CITRIX_POLICY:self.conn.resource_modify_citrix_policy,
            Const.ACTION_RENAME_CITRIX_POLICY:self.conn.resource_rename_citrix_policy,
            Const.ACTION_DESCRIBE_CITRIX_POLICY:self.conn.resource_describe_citrix_policies,
            Const.ACTION_SET_CITRIX_POLICY_PRIORITY: self.conn.resource_set_citrix_policy_priority,
            Const.ACTION_DESCRIBE_CITRIX_POLICY_FILTER: self.conn.resource_describe_citrix_policy_filters,
            Const.ACTION_ADD_CITRIX_POLICY_FILTER: self.conn.resource_add_citrix_policy_filter,
            Const.ACTION_MODIFY_CITRIX_POLICY_FILTER: self.conn.resource_modify_citrix_policy_filter,
            Const.ACTION_DELETE_CITRIX_POLICY_FILTER: self.conn.resource_delete_citrix_policy_filter,        			
        }
        
        self.describe_map = {
            Const.ACTION_DESCRIBE_COMPUTER_CATALOGS: "catalog_set",
            Const.ACTION_DESCRIBE_DELIVERY_GROUPS: "broker_desktop_group_set",
            Const.ACTION_DESCRIBE_COMPUTERS: "broker_machine_set",
            Const.ACTION_DESCRIBE_APP_STARTMEMU: "broker_app_startmenu_set",
            Const.ACTION_DESCRIBE_BROKER_APPS: "app_set",
            Const.ACTION_DESCRIBE_BROKER_APP_GROUPS: "broker_app_group_set",
            Const.ACTION_DESCRIBE_CITRIX_POLICY: "policy_set",
            Const.ACTION_DESCRIBE_CITRIX_POLICY_ITEM: "policy_item_set",
            Const.ACTION_DESCRIBE_CITRIX_POLICY_FILTER: "policy_filter_set",
            Const.ACTION_CONFIG_CITRIX_POLICY_ITEM: "policy_error_set",		
            Const.ACTION_ADD_CITRIX_POLICY_FILTER: "policy_error_set",    
            Const.ACTION_MODIFY_CITRIX_POLICY_FILTER: "policy_error_set",    
            Const.ACTION_DELETE_CITRIX_POLICY_FILTER: "policy_error_set",    	
        }

    def handle_resource(self, action, directive):
        
        if action not in self.resource_action_map:
            logger.error("handle instance no found instance map : %s, %s" % (action, directive))
            return None

        body = directive.get("body")
        
        ret = self.resource_action_map[action](body)

        if isinstance(ret, Error):
            logger.error("action %s return error : %s, %s" % (action, body, ret))
            return None

        if not ret:
            logger.error("action %s return None : %s, %s" % (action, body, ret))
            return None

        if ret["ret_code"] != 0:
            logger.error("action %s return error : %s, %s" % (action, body, ret))
            return None
        else:
            if action in self.describe_map:
                data_key = self.describe_map[action]
                ret_value = ret.get(data_key, [])
                return ret_value
            else:
                return ret

    def resource_wait_job_done(self, job_id, interval=Const.JOB_INTERVAL_5S):
    
        ret = self.job.wait_job_done(job_id, interval=interval)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (job_id, ret))
            return None
        
        return job_id

    def resource_describe_computer_catalogs(self, catalog_names=None, verbose=0):
        
        directive = {}
        body = {}

        if catalog_names:
            if not isinstance(catalog_names, list):
                catalog_names = [catalog_names]

            body["catalog_names"] = catalog_names
        
        if verbose:
            body["verbose"] = verbose
        
        directive["body"] = body
        action = Const.ACTION_DESCRIBE_COMPUTER_CATALOGS
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("describe computer catalogs fail %s" % directive)
            return None

        catalog_set = ret
        
        catalogs = {}
        for catalog in catalog_set:
            name = catalog["name"].encode("utf-8")
            if "desktop_dn" in catalog:
                catalog["desktop_dn"] = catalog["desktop_dn"].replace('DC=','dc=').replace('CN=','cn=').replace('OU=','ou=')
            if "provisioning_type" in catalog:
                catalog["provision_type"] = catalog["provisioning_type"]
                del catalog["provisioning_type"]
            
            catalogs[name] = catalog
        
        return catalogs

    def resource_create_computer_catalog(self, config):

        if not config or "catalog_name" not in config:
            logger.error("create computer catalog no found catalog name % " % config)
            return None

        catalog_name = config["catalog_name"]
        
        directive = {}
        directive["body"] = config
        action = Const.ACTION_CREATE_COMPUTER_CATALOG
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("create computer catalogs fail %s" % directive)
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        ret = self.job.wait_job_done(job_id, timeout= 3600, interval=Const.JOB_INTERVAL_10S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return catalog_name

    def resource_update_catalog_master_image(self, catalog_name, hosting_unit, new_base_image):
        
        directive = {}
        
        body = {
                "catalog_name": catalog_name,
                "hosting_unit": hosting_unit,
                "new_base_image": new_base_image
                }
                
        directive["body"] = body
        action = Const.ACTION_UPDATE_CATALOG_MASTER_IMAGE
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("update computer catalogs image fail %s" % directive)
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        ret = self.job.wait_job_done(job_id, timeout= 3600, interval=Const.JOB_INTERVAL_10S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return catalog_name

    def resource_modify_computer_catalog(self, catalog_name, modify_data):
        
        directive = {}
        body = {}
        if not modify_data:
            return None

        body["catalog_name"] = catalog_name
        body.update(modify_data)
        
        if "gpu" in modify_data:
            modify_data["gpu_class"] = modify_data["gpu"]
        
        directive["body"] = body
        action = Const.ACTION_MODIFY_COMPUTER_CATALOG
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return catalog_name
    
    def resource_delete_computer_catalog(self, catalog_name):

        directive = {}
        directive["body"] = {
            "catalog_name": catalog_name,
            }
        action = Const.ACTION_DELETE_COMPUTER_CATALOG
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        ret = self.job.wait_job_done(job_id, timeout= 3600, interval=Const.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return catalog_name   
    
    def resource_describe_delivery_groups(self, delivery_group_names=None):
        
        directive = {}
        body = {}
        if delivery_group_names and not isinstance(delivery_group_names, list):
            delivery_group_names = [delivery_group_names]

        if delivery_group_names:
            body["delivery_group_names"] = delivery_group_names
        
        directive["body"] = body
        action = Const.ACTION_DESCRIBE_DELIVERY_GROUPS

        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        delivery_group_set = ret
        delivery_groups = {}
        for delivery_group in delivery_group_set:
            delivery_group_name = delivery_group["name"].encode("utf-8")
            delivery_groups[delivery_group_name] = delivery_group
        return delivery_groups

    def resource_create_delivery_group(self, delivery_group_name, delivery_group_type, desktop_kind, description=None, delivery_type=None):
        
        directive = {}
        body = {
            "delivery_group_name": delivery_group_name,
            "session_type": delivery_group_type,
            "desktop_kind": desktop_kind
            }
        if description:
            body["description"] = description
        
        body["delivery_type"] = delivery_type if delivery_type else "DesktopsOnly"
            
        directive["body"] = body
        action = Const.ACTION_CREATE_DELIVERY_GROUP
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        
        return delivery_group_name

    def resource_modify_delivery_group(self, delivery_group_name, new_delivery_group_name=None, description=None):
        
        directive = {}
        if not new_delivery_group_name and not description:
            return delivery_group_name

        body = {
            "delivery_group_name": delivery_group_name,
            }
        if new_delivery_group_name:
            body["new_delivery_group_name"] = new_delivery_group_name

        if description:
            body["description"] = description

        directive["body"] = body
        action = Const.ACTION_MODIFY_DELIVERY_GROUP
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            return None

        return new_delivery_group_name

    def resource_delete_delivery_group(self, delivery_group_name):
        
        directive = {}
        body = {
            "delivery_group_name": delivery_group_name,
            }

        directive["body"] = body
        action = Const.ACTION_DELETE_DELIVERY_GROUP
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("delete delivery group fail %s" % delivery_group_name)
            return None
    
        return delivery_group_name

    def resource_attach_computer_to_delivery_group(self, delivery_group_name, compute_info):
        
        directive = {}
        
        machine_names = []
        for hostname, user_name in compute_info.items():

            machine_info = {
                "machine": hostname,
                "users": user_name
                }
            
            machine_names.append(machine_info)
            
        body = {
                "delivery_group_name": delivery_group_name,
                "machine_user_names": machine_names
                }

        directive["body"] = body
        action = Const.ACTION_ATTACH_COMPUTER_TO_DELIVERY_GROUP
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return delivery_group_name

    def resource_detach_computer_from_delivery_group(self, delivery_group_name, machine_names):
        
        directive = {}
        
        if not isinstance(machine_names, list):
            machine_names = [machine_names]
        
        body = {
            "delivery_group_name": delivery_group_name,
            "machine_names": machine_names
            }

        directive["body"] = body
        action = Const.ACTION_DETACH_COMPUTER_FROM_DELIVERY_GROUP
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return delivery_group_name

    def resource_attach_user_to_delivery_group(self, delivery_group_name, user_names):
        
        directive = {}
        
        if not isinstance(user_names, list):
            user_names = [user_names]
        
        body = {
            "delivery_group_name": delivery_group_name,
            "user_names": user_names
            }

        directive["body"] = body
        action = Const.ACTION_ATTACH_USER_TO_DELIVERY_GROUP
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return delivery_group_name

    def resource_detach_user_from_delivery_group(self, delivery_group_name, user_names):
        
        directive = {}
        
        if not isinstance(user_names, list):
            user_names = [user_names]
        
        body = {
            "delivery_group_name": delivery_group_name,
            "user_names": user_names
            }

        directive["body"] = body
        action = Const.ACTION_DETACH_USER_FROM_DELIVERY_GROUP
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return delivery_group_name

    def resource_reset_users_to_delivery_group(self, delivery_group_name, user_names, desktop_kind):
        
        directive = {}
        
        if not isinstance(user_names, list):
            user_names = [user_names]
        
        body = {
                "delivery_group_name": delivery_group_name,
                "delivery_group_usernames": user_names,
                "desktop_kind": desktop_kind
                }

        directive["body"] = body
        action = Const.ACTION_RESET_USER_TO_DELIVERY_GROUP
        
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return delivery_group_name

    def resource_set_delivery_group_mode(self, delivery_group_name, mode):
    
        directive = {}

        body = {}
        body["delivery_group_name"] = delivery_group_name
        
        computer_mode = 'True'
        if mode == Const.DG_STATUS_NORMAL:
            computer_mode = 'False'
        
        body["mode"] = computer_mode
        
        directive["body"] = body
        action = Const.ACTION_SET_DELIVERY_GROUP_MODE
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        
        return delivery_group_name

    def resource_describe_computers(self, catalog_names=None, machine_names=None, deliverygroup_names=None, offset=None, limit=None):
        
        directive = {}
        
        if machine_names and not isinstance(machine_names, list):
            machine_names = [machine_names]
        
        if catalog_names and not isinstance(catalog_names, list):
            catalog_names = [catalog_names]
        
        if deliverygroup_names and not isinstance(deliverygroup_names, list):
            deliverygroup_names = [deliverygroup_names]

        body = {}
        if catalog_names:
            body["catalog_names"] = catalog_names
        
        if machine_names:
            body["machine_names"] = machine_names
        
        if deliverygroup_names:
            body["deliverygroup_names"] = deliverygroup_names

        offset = offset if offset is not None else 0
        limit = limit if limit else 250
        machines = {}
        while True:
            
            body["offset"] = offset
            body["limit"] = limit
            directive["body"] = body
            action = Const.ACTION_DESCRIBE_COMPUTERS
            ret = self.handle_resource(action, directive)
            if ret is None:
                logger.error("handle action %s fail %s" % (action, directive))
                return None
    
            machines_set = ret
            
            for machine in machines_set:
                machine_name = machine["hosted_machine_name"].encode("utf-8")
                if not machine_name:
                    continue
                machines[machine_name] = machine
            
            if len(machines_set) < limit:
                break
            else:
                offset = offset + limit
                if offset >= 65535:
                    break
        
        return machines
    
    def resource_create_computer(self, catalog_name):
        
        directive = {}
        
        body = {}
        body["catalog_name"] = catalog_name

        directive["body"] = body
        action = Const.ACTION_CREATE_COMPUTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("create computer fail %s" % directive)
            return None
        
        instance_name = ret.get("machine_name")
        if not instance_name:
            logger.error("create computer no instance name %s" % ret)
            return None
        
        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        return (instance_name, job_id)

    def resource_stop_computer(self, machine_name):
        
        directive = {}

        body = {}
        body["machine_name"] = machine_name
        
        directive["body"] = body
        action = Const.ACTION_STOP_COMPUTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        ret = self.job.wait_job_done(job_id, interval=Const.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return machine_name

    def resource_start_computer(self, machine_name):
    
        directive = {}

        body = {}
        body["machine_name"] = machine_name
        
        directive["body"] = body
        action = Const.ACTION_START_COMPUTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        ret = self.job.wait_job_done(job_id, interval=Const.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return machine_name
    
    def resource_terminate_computer(self, catalog_name, machine_name):
        
        directive = {}

        body = {}
        body["catalog_name"] = catalog_name
        body["machine_name"] = machine_name
        
        directive["body"] = body
        action = Const.ACTION_DELETE_COMPUTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        ret = self.job.wait_job_done(job_id, interval=Const.JOB_INTERVAL_10S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return machine_name

    def resource_restart_computer(self, machine_name):
        
        directive = {}

        body = {}
        body["machine_name"] = machine_name
        
        directive["body"] = body
        action = Const.ACTION_RESTART_COMPUTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        ret = self.job.wait_job_done(job_id, interval=Const.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return machine_name

    def resource_attach_computer_to_user(self, machine_name, user_name):
        
        directive = {}

        body = {}
        body["machine_name"] = machine_name
        body["user_name"] = user_name
        
        directive["body"] = body
        action = Const.ACTION_ATTACH_COMPUTER_TO_USER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return machine_name

    def resource_detach_computer_from_user(self, machine_name, user_name):
        
        directive = {}

        body = {}
        body["machine_name"] = machine_name
        body["user_name"] = user_name
        
        directive["body"] = body
        action = Const.ACTION_DETACH_COMPUTER_FROM_USER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return machine_name

    def resource_set_computer_mode(self, machine_name, desktop_kind, mode):
    
        directive = {}

        body = {}
        body["machine_name"] = machine_name
        body["desktop_kind"] = desktop_kind
        
        computer_mode = True
        if mode == Const.DG_STATUS_NORMAL:
            computer_mode = False
        
        body["mode"] = computer_mode
        
        directive["body"] = body
        action = Const.ACTION_SET_COMPUTER_MODE
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        
        return machine_name

    def resource_reload_image(self, image_id):
    
        directive = {}

        body = {}
        body["image_id"] = image_id
        
        directive["body"] = body
        action = Const.ACTION_RELOAD_IMAGE
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action %s handle no return resource %s, ret %s" % (action, directive, ret))
            return None

        ret = self.job.wait_job_done(job_id, interval=Const.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return image_id

    def resource_stop_broker_session(self, session_uid):
        directive = {}

        body = {}
        body["session_uid"] = session_uid

        directive["body"] = body
        action = Const.ACTION_STOP_BROKER_SESSION
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return False
        if ret.get("ret_code", -1) != 0:
            return False

        return True
    # app

    def resource_add_computer(self, catalog_name, machine_name, machine_id, machine_sid, host_unit):
        directive = {}

        body = {}
        body["catalog_name"] = catalog_name
        body["machine_name"] = machine_name
        body["machine_id"] = machine_id
        body["machine_sid"] = machine_sid
        body["host_unit"] = host_unit

        directive["body"] = body
        action = Const.ACTION_ADD_COMPUTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret

    def resource_delete_app_computer(self, machine_name):
        directive = {}

        body = {}
        body["machine_name"] = machine_name

        directive["body"] = body
        action = Const.ACTION_DELETE_APP_COMPUTER

        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret

    def resource_describe_app_start_memu(self, machine_name):
        directive = {}

        body = {}
        body["machine_name"] = machine_name

        directive["body"] = body
        action = Const.ACTION_DESCRIBE_APP_STARTMEMU
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        
        app_startmenus = {}
        
        for startmenu in ret:
            displayname = startmenu["displayname"]
            app_startmenus[displayname] = startmenu

        return app_startmenus
    
    def resource_describe_broker_apps(self, app_names=None, delivery_group_uids=None, app_group_uids=None, index_uid=False):
        directive = {}

        body = {}
        if app_names:
            if not isinstance(app_names, list):
                app_names = [app_names]

            body["app_names"] = app_names

        if not body and delivery_group_uids:
            
            if not isinstance(delivery_group_uids, list):
                delivery_group_uids = [delivery_group_uids]

            body["delivery_group_uids"] = delivery_group_uids
        
        if not body and app_group_uids:
            if not isinstance(app_group_uids, list):
                app_group_uids = [app_group_uids]
            
            body["app_group_uids"] = app_group_uids

        directive["body"] = body
        action = Const.ACTION_DESCRIBE_BROKER_APPS
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        broker_apps = {}
        for app in ret:
            app = unicode_to_string(app)
            app_name = app["app_name"]
            all_desktopgroup_uids = app.get("all_desktopgroup_uids", [])
            
            if all_desktopgroup_uids:
                all_desktopgroup_uids = all_desktopgroup_uids.split(",")
            app["all_desktopgroup_uids"] = all_desktopgroup_uids if all_desktopgroup_uids else []
            
            all_appgroup_uids = app.get("all_appgroup_uids", [])
            if all_appgroup_uids:
                all_appgroup_uids = all_appgroup_uids.split(",")
            app["all_appgroup_uids"] = all_appgroup_uids if all_appgroup_uids else []
            
            if "app_publishname" in app:
                app["normal_display_name"] = app["app_publishname"]
            
            app["admin_display_name"] = app["app_name"]
            
            broker_app_uid = str(app["app_uid"])
            
            if index_uid:
                broker_apps[broker_app_uid] = app
            else:
                broker_apps[app_name] = app
        
        return broker_apps

    def resource_create_broker_app(self, delivery_group_name, machine_name, app_data):
        
        directive = {}

        body = {}
        body["delivery_group_name"] = delivery_group_name
        body["machine_name"] = machine_name
        
        body.update(app_data)
        directive["body"] = body
        action = Const.ACTION_CREATE_BROKER_APP
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret

    def resource_modify_broker_app(self, app_uid, admin_display_name=None, normal_display_name=None, description=None):
        
        directive = {}

        body = {"app_uid": int(app_uid)}
        if admin_display_name:
            body["admin_display_name"] = admin_display_name
        
        if normal_display_name:
            body["normal_display_name"] = normal_display_name
        
        if description:
            body["description"] = description
        
        directive["body"] = body
        action = Const.ACTION_MODIFY_BROKER_APP

        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret

    def resource_add_broker_app(self, app_name, delivery_group_name=None, app_group_name=None):
        directive = {}

        body = {}
        if delivery_group_name:
            body["delivery_group_name"] = delivery_group_name
        
        if app_group_name:
            body["app_group_name"] = app_group_name

        body["app_name"] = app_name

        directive["body"] = body
        action = Const.ACTION_ADD_BROKER_APP
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret

    def resource_remove_broker_app(self, app_names, delivery_group_uid = None, app_group_uid=None):
        directive = {}
        
        if not isinstance(app_names, list):
            app_names = [app_names]
        
        body = {"app_names": app_names}
        if delivery_group_uid:
            body["delivery_group_uid"] = delivery_group_uid
        
        if app_group_uid:
            body["app_group_uid"] = app_group_uid

        directive["body"] = body
        action = Const.ACTION_REMOVE_BROKER_APP
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret
    
    def resource_new_broker_folder(self, session_uid):
        directive = {}

        body = {}
        body["session_uid"] = session_uid

        directive["body"] = body
        action = Const.ACTION_DESCRIBE_APP_STARTMEMU
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return False
        if ret.get("ret_code", -1) != 0:
            return False

        return True
    
    def resource_remove_broker_folder(self, session_uid):
        directive = {}

        body = {}
        body["session_uid"] = session_uid

        directive["body"] = body
        action = Const.ACTION_DESCRIBE_APP_STARTMEMU
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return False
        if ret.get("ret_code", -1) != 0:
            return False

        return True

    def resource_describe_broker_folder(self, session_uid):
        directive = {}

        body = {}
        body["session_uid"] = session_uid

        directive["body"] = body
        action = Const.ACTION_DESCRIBE_APP_STARTMEMU
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return False
        if ret.get("ret_code", -1) != 0:
            return False

        return True

    def resource_describe_broker_app_groups(self, app_group_names=None, delivery_group_uids=None, index_uid=False):

        directive = {}

        body = {}
        
        if app_group_names and not isinstance(app_group_names, list):
            app_group_names = [app_group_names]
        if app_group_names:
            body["app_group_names"] = app_group_names
        
        if not body and delivery_group_uids:
            body["delivery_group_uids"] = delivery_group_uids

        directive["body"] = body
        action = Const.ACTION_DESCRIBE_BROKER_APP_GROUPS
        ret = self.handle_resource(action, directive)

        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        broker_app_groups = {}
        for app_group in ret:
            app_group = unicode_to_string(app_group)

            associated_deliverygroup_uids = app_group.get("associated_deliverygroup_uids", [])
            
            if associated_deliverygroup_uids:
                associated_deliverygroup_uids = associated_deliverygroup_uids.split(",")
            app_group["associated_deliverygroup_uids"] = associated_deliverygroup_uids if associated_deliverygroup_uids else []
            
            if index_uid:
                app_group_uid = str(app_group["app_group_uid"])
                broker_app_groups[app_group_uid] = app_group
            else:
                app_group_name = unicode_to_string(app_group["app_group_name"])
                broker_app_groups[app_group_name] = app_group

        return broker_app_groups

    def resource_create_broker_app_group(self, app_group_name, description=None):

        directive = {}

        body = {}
        body["app_group_name"] = app_group_name
        if description:
            body["description"] = description

        directive["body"] = body
        action = Const.ACTOPN_CREATE_BROKER_APP_GROUP
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret

    def resource_delete_broker_app_group(self, app_group_name, delivery_group_name=None):

        directive = {}

        body = {}
        body["app_group_name"] = app_group_name
        if delivery_group_name:
            body["delivery_group_name"] = delivery_group_name

        directive["body"] = body
        action = Const.ACTOPN_DELETE_BROKER_APP_GROUP
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret

    def resource_add_broker_app_group(self, app_group_name, delivery_group_name):

        directive = {}

        body = {}
        body["app_group_name"] = app_group_name
        body["delivery_group_name"] = delivery_group_name

        directive["body"] = body
        action = Const.ACTION_ADD_BROKER_APP_GROUP
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None

        return ret

    def resource_create_citrix_policy(self, citrix_policy):

        directive = {}
        body = {
                "citrix_policy_name": citrix_policy["citrix_policy_name"]
                }        
        if citrix_policy["description"]:
            body["description"] = citrix_policy["description"]
        if citrix_policy["policy_state"] is not None:
            body["policy_state"] = citrix_policy["policy_state"]  
        directive["body"] = body
        action = Const.ACTION_CREATE_CITRIX_POLICY
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        if ret.get("ret_code", -1) != 0:
            return None
        pol_priority = ret.get("pol_priority")
        user_priority = ret.get("user_priority")
        com_priority = ret.get("com_priority")
        if not pol_priority or not user_priority or not com_priority:
            logger.error("action %s handle no return policy_priority  ret %s" % (action, ret))
            return None
        priority = {}
        priority["pol_priority"] = pol_priority
        priority["user_priority"] = user_priority
        priority["com_priority"] = com_priority
        return priority


    def resource_describe_citrix_policies(self, citrix_policy_names=None):        
        directive = {}
        body = {}
        if citrix_policy_names and not isinstance(citrix_policy_names, list):
            citrix_policy_names = [citrix_policy_names]
        if citrix_policy_names:
            body["citrix_policy_names"] = citrix_policy_names        
        directive["body"] = body
        action = Const.ACTION_DESCRIBE_CITRIX_POLICY
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None        
        policy_set = ret
        citrix_policies = {}
        for policy in policy_set:
            policy_name = policy["citrix_policy_name"].encode("utf-8")
            citrix_policies[policy_name] = policy
        return citrix_policies

    def resource_config_citrix_policy_item(self, citrix_policy_name,policy_items):

        directive = {}
        citrix_policy_items = []
        for item in policy_items:
            item_info = {
                "item_name": item["pol_item_name"],
                "item_type": item["pol_item_type"],
                "itme_state": item["pol_item_state"],
                "item_value": item["pol_item_value"]               
                }           
            citrix_policy_items.append(item_info)           
        body = {
                "citrix_policy_name": citrix_policy_name,
                "policy_items": citrix_policy_items
                }
        directive["body"] = body
        action = Const.ACTION_CONFIG_CITRIX_POLICY_ITEM
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("create policy item fail %s" % directive)
            return None

        policy_item_error_set = ret
        policy_item_error_list = {}
        logger.error("policy_item_error_set %s" % policy_item_error_set)
        for policy_item in policy_item_error_set:
            policy_item_name = policy_item["item_name"].encode("utf-8")
            policy_item_error_list[policy_item_name] = policy_item["item_error"]
        return policy_item_error_list

    def resource_describe_citrix_policy_items(self, citrix_policy_name):

        directive = {}
        body = {
                "citrix_policy_name": citrix_policy_name,
                }
        directive["body"] = body
        action = Const.ACTION_DESCRIBE_CITRIX_POLICY_ITEM
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        policy_item_set = ret
        policy_item_list = {}
        for policy_item in policy_item_set:
            policy_item_name = policy_item["pol_item_name"].encode("utf-8")
            policy_item_list[policy_item_name] = policy_item
        return policy_item_list

    def resource_delete_citrix_policy(self, citrix_policy_name):

        directive = {}
        body = {
                "citrix_policy_name": citrix_policy_name,
                }
        directive["body"] = body
        action = Const.ACTION_DELETE_CITRIX_POLICY
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("delte policy fail %s" % directive)
            return None
        if ret.get("ret_code", -1) != 0:
            return None                
        return citrix_policy_name
    
    def resource_modify_citrix_policy(self, citrix_policy):

        directive = {}
        body = {
                "citrix_policy_name": citrix_policy["citrix_policy_name"]
                }        
        if citrix_policy["description"]:
            body["description"] = citrix_policy["description"]
        if citrix_policy["policy_state"] is not None:
            body["policy_state"] = citrix_policy["policy_state"]            

        directive["body"] = body
        action = Const.ACTION_MODIFY_CITRIX_POLICY
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        if ret.get("ret_code", -1) != 0:
            return None

        return True    
    
    def resource_rename_citrix_policy(self, citrix_policy):

        directive = {}
        body = {
                "citrix_policy_old_name": citrix_policy["citrix_policy_old_name"],
                "citrix_policy_new_name": citrix_policy["citrix_policy_new_name"]
                }        
        directive["body"] = body
        action = Const.ACTION_RENAME_CITRIX_POLICY
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        if ret.get("ret_code", -1) != 0:
            return None
        return True       

    def resource_set_citrix_policy_priority(self, citrix_policy_name=None,policy_priority=None):

        directive = {}
        body = {}
        if citrix_policy_name:
            body["citrix_policy_name"] = citrix_policy_name
        if policy_priority:
            body["policy_priority"] = policy_priority        
        directive["body"] = body
        action = Const.ACTION_SET_CITRIX_POLICY_PRIORITY
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("set policy fail %s" % directive)
            return None
        if ret.get("ret_code", -1) != 0:
            return None                
        return citrix_policy_name

    def resource_add_citrix_policy_filter(self, citrix_policy_name=None,policy_filters=None):

        directive = {}
        citrix_policy_filters = []
        for filter in policy_filters:
            filter_info = {
                "pol_filter_name": filter["pol_filter_name"],
                "pol_filter_type": filter["pol_filter_type"],
                "pol_filter_value": filter["pol_filter_value"],
                "pol_filter_state": filter["pol_filter_state"],    
                "pol_filter_mode": filter["pol_filter_mode"],             
                }            
            citrix_policy_filters.append(filter_info)           
        body = {
                "citrix_policy_name": citrix_policy_name,
                "policy_filters": citrix_policy_filters
                }
        directive["body"] = body
        action = Const.ACTION_ADD_CITRIX_POLICY_FILTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("add policy filter fail %s" % directive)
            return None
        
        policy_filter_error_set = ret
        policy_filter_error_list = {}
        logger.error("policy_filter_error_set %s" % policy_filter_error_set)
        for policy_filter in policy_filter_error_set:
            policy_filter_name = policy_filter["item_name"].encode("utf-8")
            policy_filter_error_list[policy_filter_name] = policy_filter["item_error"]
        return policy_filter_error_list

    def resource_modify_citrix_policy_filter(self, citrix_policy_name=None,policy_filters=None):

        directive = {}
        citrix_policy_filters = []
        for filter in policy_filters:
            filter_info = {
                "pol_filter_name": filter["pol_filter_name"],
                "pol_filter_type": filter["pol_filter_type"],
                "pol_filter_value": filter["pol_filter_value"],
                "pol_filter_state": filter["pol_filter_state"],    
                "pol_filter_mode": filter["pol_filter_mode"],             
                }            
            citrix_policy_filters.append(filter_info)           
        body = {
                "citrix_policy_name": citrix_policy_name,
                "policy_filters": citrix_policy_filters
                }
        directive["body"] = body
        action = Const.ACTION_MODIFY_CITRIX_POLICY_FILTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("modify policy filter fail %s" % directive)
            return None
        policy_filter_error_set = ret
        policy_filter_error_list = {}
        logger.error("policy_filter_error_set %s" % policy_filter_error_set)
        for policy_filter in policy_filter_error_set:
            policy_filter_name = policy_filter["item_name"].encode("utf-8")
            policy_filter_error_list[policy_filter_name] = policy_filter["item_error"]
        return policy_filter_error_list

    def resource_delete_citrix_policy_filter(self, citrix_policy_name,policy_filters=None):
        directive = {}
        citrix_policy_filters = []
        for filter in policy_filters:
            filter_info = {
                "pol_filter_name": filter["pol_filter_name"],
                "pol_filter_type": filter["pol_filter_type"],
                }            
            citrix_policy_filters.append(filter_info)           
        body = {
                "citrix_policy_name": citrix_policy_name,
                "policy_filters": citrix_policy_filters
                }
        directive["body"] = body
        action = Const.ACTION_DELETE_CITRIX_POLICY_FILTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("delte policy filter fail %s" % directive)
            return None
        policy_filter_error_set = ret
        policy_filter_error_list = {}
        logger.error("policy_filter_error_set %s" % policy_filter_error_set)
        for policy_filter in policy_filter_error_set:
            policy_filter_name = policy_filter["item_name"].encode("utf-8")
            policy_filter_error_list[policy_filter_name] = policy_filter["item_error"]
        return policy_filter_error_list

    def resource_describe_citrix_policy_filters(self, citrix_policy_name=None):

        directive = {}
        body = {}
        if citrix_policy_name:
            body["citrix_policy_name"] = citrix_policy_name        
        directive["body"] = body
        action = Const.ACTION_DESCRIBE_CITRIX_POLICY_FILTER
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle action %s fail %s" % (action, directive))
            return None
        policy_filter_set = ret
        policy_filter_list = {}
        for policy_filter in policy_filter_set:
            policy_filter_name = policy_filter["pol_filter_name"].encode("utf-8")
            policy_filter_list[policy_filter_name] = policy_filter
        return policy_filter_list
		

