
from qingcloud.resource import QCResource
from citrix.resource import CitrixResource
from vdi.resource import DesktopResource
import constants as const
from log.logger import logger
from common import check_citrix_action

class ResourceAdapter():

    def __init__(self, ctx):
    
        self.ctx = ctx
        self.platform = {}

        self.connection = {}
        self.citrix_connection = {}
        self.desktop_connection = {}

    def init_resource_adapter(self):

        for zone_id, zone in self.ctx.zones.items():

            platform = zone.platform
            base_zone = zone.base_zone
            if not base_zone:
                continue
            
            qc_res = QCResource(self.ctx, base_zone, zone.connection)
            if not qc_res:
                logger.error("Qingcloud Connection create fail:%s, %s" % (zone_id, zone.connection))
                return -1

            self.connection[zone_id] = qc_res
            # desktop connection
            desktop_res = DesktopResource(zone_id, zone.desktop_connection)
            if not desktop_res:
                logger.error("desktop Connection create fail:%s" % (zone.desktop_connection))
                return -1
            self.desktop_connection[zone_id] = desktop_res
        
            # init citrix conn
            if platform == const.PLATFORM_TYPE_CITRIX:
                citrix_res = CitrixResource(base_zone, zone.citrix_connection)
                if not citrix_res:
                    logger.error("Qingcloud Connection create fail:%s" % (base_zone, zone.citrix_connection))
                    return None
    
                self.citrix_connection[zone_id] = citrix_res
            
            self.platform[zone_id] = platform
        
        return 0
    
    def get_test_connection(self, base_zone, conn):

        qc_res = QCResource(self.ctx, base_zone, conn, http_socket_timeout=10, retry_time=1)
        if not qc_res:
            logger.error("Qingcloud Temp Connection create fail:%s, %s" % (base_zone,conn))
            return -1

        return qc_res
    
    def get_qc_handler(self, zone_id):

        if zone_id not in self.connection:
            return None
        
        return self.connection[zone_id]

    def get_citrix_handler(self, zone_id):
        
        if zone_id not in self.citrix_connection:
            return None
        
        return self.citrix_connection[zone_id]

    def get_desktop_handler(self, zone_id):
        
        if zone_id not in self.desktop_connection:
            return None
        
        return self.desktop_connection[zone_id]

    # instance

    def resource_search_instances(self, zone, search_word=None, status=None):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None 
        
        return handler.resource_search_instances(search_word, status)

    def resource_describe_instances(self, zone, instance_ids, status=None):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_instances(instance_ids, status)

    def resource_lease_desktop(self, zone, instance_ids):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_lease_desktop(instance_ids)

    def resource_wait_job_done(self, zone, job_id, platform=None):
        
        if not platform:
            platform = self.platform.get(zone)

        if platform == const.PLATFORM_TYPE_CITRIX:
            
            handler = self.get_citrix_handler(zone)
            if not handler:
                return None

            return handler.resource_wait_job_done(job_id)
        else:

            handler = self.get_qc_handler(zone)
            if not handler:
                return None

            return handler.resource_wait_job_done(job_id)
    
    def resource_describe_instances_with_monitors(self, zone, instance_ids):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_instances_with_monitors(instance_ids)

    def resource_create_instance(self, zone, desktop_config, desktop_group_name=None, platform=None):

        if not platform:
            platform = self.platform.get(zone)

        if platform == const.PLATFORM_TYPE_CITRIX:
            
            handler = self.get_citrix_handler(zone)
            if not handler:
                return None
            
            if not desktop_group_name:
                return None
        
            return handler.resource_create_computer(desktop_group_name)
        else:
            handler = self.get_qc_handler(zone)

            if not handler:
                return None
            
            if not desktop_config:
                return None
            
            return handler.resource_run_instance(desktop_config)

    def resource_stop_instances(self, zone, resource, platform=None):

        if check_citrix_action(self.ctx, zone, resource) and platform != const.PLATFORM_TYPE_QINGCLOUD:
            
            handler = self.get_citrix_handler(zone)
            if not handler:
                return None

            resource_name = resource.get("hostname")
            if not resource_name:
                return None
                
            return handler.resource_stop_computer(resource_name)
        
        else:
            handler = self.get_qc_handler(zone)
            if not handler:
                return None
            
            instance_id = resource.get("instance_id")
            if not instance_id:
                return None

            return handler.resource_stop_instances(instance_id)

    def resource_terminate_instances(self, zone, resource, platform=None):

        if not platform:
            platform = self.platform.get(zone)

        if platform == const.PLATFORM_TYPE_CITRIX:
            
            handler = self.get_citrix_handler(zone)
            if not handler:
                return None
            
            machine_name = resource.get("hostname")
            catalog_name = resource.get("desktop_group_name")
            if not machine_name or not catalog_name:
                return None

            desktop_group = self.ctx.pgm.get_desktop_group_by_name(catalog_name, zone=zone)
            if not desktop_group:
                desktop_group = {}
            
            provision_type = desktop_group.get("provision_type", "MCS")

            if provision_type == const.PROVISION_TYPE_MANUAL:
                return handler.resource_delete_app_computer(machine_name)
            else:           
                return handler.resource_terminate_computer(catalog_name, machine_name)
        
        else:
            handler = self.get_qc_handler(zone)
            if not handler:
                return None
            
            instance_id = resource.get("instance_id")
            if not instance_id:
                return None
            return handler.resource_terminate_instances(instance_id)
    
    def resource_restart_instances(self, zone, resource):

        if check_citrix_action(self.ctx, zone, resource):
            
            handler = self.get_citrix_handler(zone)
            if not handler:
                return None
            
            machine_name = resource.get("hostname")
            if not machine_name:
                return None

            return handler.resource_restart_computer(machine_name)
        
        else:
            handler = self.get_qc_handler(zone)
            if not handler:
                return None

            instance_id = resource.get("instance_id")
            if not instance_id:
                return None

            return handler.resource_restart_instances(instance_id)

    def resource_start_instances(self, zone, resource):

        if check_citrix_action(self.ctx, zone, resource):
            
            handler = self.get_citrix_handler(zone)
            if not handler:
                return None

            machine_name = resource.get("hostname")
            if not machine_name:
                return None

            return handler.resource_start_computer(machine_name)
        
        else:
            handler = self.get_qc_handler(zone)
            if not handler:
                return None
            
            instance_id = resource.get("instance_id")
            if not instance_id:
                return None
    
            return handler.resource_start_instances(instance_id)

    def resource_resize_instances(self, zone, instance_id, config):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_resize_instances(instance_id, config)

    def resource_modify_instance_attributes(self, zone, instance_id, config):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_modify_instance_attributes(instance_id, config)

    def resource_describe_gpus(self, zone, gpu_class=None, status=[const.GPU_STATUS_AVAIL]):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_gpus(gpu_class, status)

    def resource_describe_images(self, zone, image_ids=None, status=None, req=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None
    
        return handler.resource_describe_images(user_id, image_ids, status, req)

    def resource_modify_image_attributes(self, zone, image_id, config):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_modify_image_attributes(image_id, config)

    def resource_capture_instance(self, zone, instance_id, image_name):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_capture_instance(instance_id, image_name)

    def resource_delete_images(self, zone, image_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_images(image_id)

    def resource_create_brokers(self, zone, instance_id, is_token=0):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_create_brokers(instance_id, is_token)

    def resource_delete_brokers(self, zone, instance_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_brokers(instance_id)

    def resource_describe_volumes(self, zone, volume_ids, status=None):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_volumes(volume_ids, status)
    
    def resource_create_volume(self, zone, size, volume_type, volume_name):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_create_volume(size, volume_type, volume_name)
    
    def resource_resize_volumes(self, zone, volume_id, size):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_resize_volumes(volume_id, size)

    def resource_delete_volumes(self, zone, volume_ids):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_volumes(volume_ids)

    def resource_attach_volumes(self, zone, volume_ids, instance_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_attach_volumes(volume_ids, instance_id)
    
    def resource_detach_volumes(self, zone, volume_ids, instance_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_detach_volumes(volume_ids, instance_id)
    
    def resource_modify_volume_attributes(self, zone, volume_id, config):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_modify_volume_attributes(volume_id, config)
    
    # vxnet
    def resource_describe_networks(self, zone, network_ids=None, network_type=None):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
    
        return handler.resource_describe_vxnets(network_ids, network_type)

    # vxnet
    def resource_describe_managed_networks(self, zone, router_id):

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
    
        return handler.resource_describe_managed_networks(router_id, user_id)

    def resource_create_vxnets(self, zone, vxnet_type, vxnet_name):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_vxnets(vxnet_type, vxnet_name)

    def resource_modify_vxnet_attributes(self, zone, network_id, vxnet_name=None, description=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_modify_vxnet_attributes(network_id, vxnet_name, description)

    def resource_describe_vxnet_resources(self, zone, network_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_vxnet_resources(network_id)

    def resource_delete_vxnets(self, zone, vxnet_ids):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_vxnets(vxnet_ids)

    def resource_describe_routers(self, zone, router_ids=None):
        
        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_routers(user_id, router_ids)

    def resource_join_router(self, zone, vxnet_id, router_id, ip_network):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_join_router(vxnet_id, router_id, ip_network)
    
    def resource_leave_router(self, zone, router_id, vxnet_id):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_leave_router(router_id, vxnet_id)

    def resource_describe_nics(self, zone, nic_ids=None, network_id=None, status=None, is_owner=True):
        
        user_id = None
        if is_owner:
            user_id = self.ctx.zone_users.get(zone)
            if not user_id:
                logger.error("no found zone user")
                return None

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_nics(nic_ids, network_id, status, user_id)
    
    def resource_create_nics(self, zone, vxnet_id, nic_name, nic_count=1, private_ips=None):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_create_nics(vxnet_id, nic_name, nic_count,  private_ips)
    
    def resource_delete_nics(self, zone, nic_ids):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_nics(nic_ids)

    def resource_attach_nics(self, zone, instance_id, nic_ids):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_attach_nics(instance_id, nic_ids)
    
    def resource_detach_nics(self, zone, nic_ids):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_detach_nics(nic_ids)

    def resource_send_desktop_message(self, zone, instance_ids, base64_message):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_send_desktop_message(instance_ids, base64_message)

    def resource_send_desktop_hot_keys(self, zone, instance_ids, keys, timeout, time_step):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_send_desktop_hot_keys(instance_ids, keys, timeout, time_step)

    # monitor
    def resource_get_monitoring_data(self, zone, resource, meters, step, start_time, end_time, decompress=1):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_get_monitoring_data(resource, meters, step, start_time, end_time, decompress)

    # snapshot
    def resource_describe_snapshots(self, zone, snapshot_ids):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_snapshots(snapshot_ids)

    def resource_create_snapshots(self, zone, resource_ids, snapshot_name, is_full=0):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_snapshots(resource_ids, snapshot_name, is_full)

    def resource_create_desktop_snapshots(self, zone, snapshot_group_id=None, resource_ids=None,is_full=0):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_create_desktop_snapshots(snapshot_group_id, resource_ids,is_full)

    def resource_delete_snapshots(self, zone, snapshot_ids):
    
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_delete_snapshots(snapshot_ids)

    def resource_modify_snapshot_attributes(self, zone, snapshot_id, snapshot_name, description):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_modify_snapshot_attributes(snapshot_id, snapshot_name, description)

    def resource_apply_snapshots(self, zone, snapshot_ids):
    
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_apply_snapshots(snapshot_ids)
    
    def resource_capture_instance_from_snapshot(self, zone, snapshot_id, image_name):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_capture_instance_from_snapshot(snapshot_id, image_name)

    def resource_create_volume_from_snapshot(self, zone, snapshot_id, volume_name):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_volume_from_snapshot(snapshot_id, volume_name)

    def resource_test_describe_zones(self, test_handler, zone_ids=None, status=None, region=None):

        if not test_handler:
            return None

        return test_handler.resource_describe_zones(zone_ids, status, region, retries=1)

    def resource_describe_access_keys(self, test_handler, zone_ids=None,access_keys=None):

        if not test_handler:
            return None

        return test_handler.resource_describe_access_keys(zone_ids, access_keys)

    def resource_describe_users(self, test_handler, zone_ids=None,users=None):

        if not test_handler:
            return None

        return test_handler.resource_describe_users(zone_ids, users)

    def resource_describe_zones(self, zone, zone_ids=None, status=None, region=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_zones(zone_ids, status, region)

    def resource_describe_keypairs(self, zone, owner, keypair_name):
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_keypairs(zone, owner, keypair_name)

    def resource_create_keypair(self, zone, owner, keypair_name):
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_create_keypair(zone, owner, keypair_name)

    def resource_get_resource_limit(self, zone):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_get_resource_limit(zone)

    def resource_describe_place_groups(self, zone, place_group_ids=None, status=None):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_place_groups(place_group_ids, status)

    # citrix
    def resource_describe_delivery_groups(self, zone, delivery_group_names=None):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_delivery_groups(delivery_group_names)

    def resource_create_delivery_group(self, zone, delivery_group_name, delivery_group_type, desktop_kind, description=None, delivery_type=None):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_delivery_group(delivery_group_name, delivery_group_type, desktop_kind, description, delivery_type)

    def resource_modify_delivery_group(self, zone, delivery_group_name, new_delivery_group_name=None, description=None):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_modify_delivery_group(delivery_group_name, new_delivery_group_name, description)

    def resource_delete_delivery_group(self, zone, delivery_group_names):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_delivery_group(delivery_group_names)
    
    def resource_reset_users_to_delivery_group(self, zone, delivery_group_name, user_names, desktop_kind):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_reset_users_to_delivery_group(delivery_group_name, user_names, desktop_kind)

    def resource_set_delivery_group_mode(self, zone, delivery_group_name, mode):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_set_delivery_group_mode(delivery_group_name, mode)

    def resource_describe_computer_catalogs(self, zone, catalog_name=None, verbose=0):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_computer_catalogs(catalog_name,verbose)

    def resource_create_computer_catalog(self, zone, config):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_create_computer_catalog(config)

    def resource_update_catalog_master_image(self, zone, catalog_name, hosting_unit, new_base_image):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_update_catalog_master_image(catalog_name, hosting_unit, new_base_image)
        
    def resource_modify_computer_catalog(self, zone, catalog_name, modify_data):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_modify_computer_catalog(catalog_name, modify_data)

    def resource_delete_computer_catalog(self, zone, catalog_name):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_computer_catalog(catalog_name)

    def resource_attach_computer_to_delivery_group(self, zone, delivery_group_name, compute_info):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_attach_computer_to_delivery_group(delivery_group_name, compute_info)

    def resource_detach_computer_from_delivery_group(self, zone, delivery_group_name, machine_names):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_detach_computer_from_delivery_group(delivery_group_name, machine_names)

    def resource_attach_user_to_delivery_group(self, zone, delivery_group_name, user_names):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_attach_user_to_delivery_group(delivery_group_name, user_names)

    def resource_detach_user_from_delivery_group(self, zone, delivery_group_name, user_names):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_detach_user_from_delivery_group(delivery_group_name, user_names)

    def resource_describe_computers(self, zone, catalog_name=None, machine_names=None, deliverygroup_names=None, offset=None, limit=None):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_computers(catalog_name, machine_names, deliverygroup_names, offset, limit)
    
    def resource_attach_computer_to_user(self, zone, machine_name, user_name):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_attach_computer_to_user(machine_name, user_name)
    
    def resource_detach_computer_from_user(self, zone, machine_name, user_name):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_detach_computer_from_user(machine_name, user_name)

    def resource_set_computer_mode(self, zone, machine_name, desktop_kind, mode):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_set_computer_mode(machine_name, desktop_kind, mode)

    def resource_stop_broker_session(self, zone, session_id):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None

        return handler.resource_stop_broker_session(session_id)

    # security
    def resource_describe_security_groups(self, zone, security_group_ids=None, group_type=None, is_default=None):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None
        
        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_describe_security_groups(user_id, security_group_ids, group_type, is_default)
    
    def resource_create_security_group(self, zone, security_group_name, group_type=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            logger.error("no found qc handler %s" % zone)
            return None
        
        return handler.resource_create_security_group(security_group_name, group_type)

    def resource_modify_security_group_attributes(self, zone, security_group_id, policy_group_name=None, description=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_modify_security_group_attributes(security_group_id, policy_group_name, description)

    def resource_delete_security_groups(self, zone, security_group_ids):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_delete_security_groups(security_group_ids)

    def resource_remove_security_group(self, zone, instance_ids):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_remove_security_group(instance_ids)

    def resource_rollback_security_group(self, zone, security_group_id, security_group_snapshot_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_rollback_security_group(security_group_id, security_group_snapshot_id)

    def resource_apply_security_group(self, zone, security_group_id, instance_ids=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_apply_security_group(security_group_id, instance_ids)
    
    def resource_describe_security_group_rules(self, zone, security_group_id=None, security_group_rule_ids=None, direction=None ):
    
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None
        
        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_describe_security_group_rules(user_id, security_group_id, security_group_rule_ids, direction)
    
    def resource_add_security_group_rules(self, zone, security_group_id, rules):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_add_security_group_rules(security_group_id, rules)
    
    def resource_delete_security_group_rules(self, zone, security_group_rule_ids):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_delete_security_group_rules(security_group_rule_ids)
    
    def resource_modify_security_group_rule_attributes(self, zone, security_group_rule_id, config):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_modify_security_group_rule_attributes(security_group_rule_id, config)
    
    def resource_describe_security_group_ipsets(self, zone, security_group_ipset_ids=None, ipset_type=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None
        
        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_describe_security_group_ipsets(user_id, security_group_ipset_ids, ipset_type)
    
    def resource_create_security_group_ipset(self, zone, ipset_type, val, security_group_ipset_name=None):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_security_group_ipset(ipset_type, val, security_group_ipset_name)
    
    def resource_delete_security_group_ipsets(self, zone, security_group_ipset_ids):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_delete_security_group_ipsets(security_group_ipset_ids)
    
    def resource_modify_security_group_ipset_attributes(self, zone, security_group_ipset_id, security_group_ipset_name, description, val):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_modify_security_group_ipset_attributes(security_group_ipset_id, security_group_ipset_name, description, val)

    def resource_apply_security_ipset(self, zone, security_group_ipset_id):
        
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_apply_security_ipset(security_group_ipset_id)

    def resource_describe_security_group_and_ruleset(self, zone, security_group_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_security_group_and_ruleset(security_group_id)

    def resource_add_security_group_rulesets(self, zone, security_group_id, security_group_ruleset_ids):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_add_security_group_rulesets(security_group_id, security_group_ruleset_ids)

    def resource_remove_security_group_rulesets(self, zone, security_group_id, security_group_ruleset_ids):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_remove_security_group_rulesets(security_group_id, security_group_ruleset_ids)

    def resource_apply_security_group_ruleset(self, zone, security_group_ruleset_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_apply_security_group_ruleset(security_group_ruleset_id)

    def resource_create_security_group_snapshot(self, zone, security_group_id, name):
    
        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_security_group_snapshot(security_group_id, name)

    def resource_delete_security_group_snapshots(self, zone, security_group_snapshot_ids):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_security_group_snapshot(security_group_snapshot_ids)

    def resource_describe_auth_users(self, zone, user_names=None, base_dn=None, search_name=None, scope=1, global_search=None):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_describe_auth_users(auth_service_id, user_names, base_dn, search_name, scope, global_search)
    
    def resource_create_auth_user(self, zone, user_info):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_create_auth_user(auth_service_id, user_info)
    
    def resource_modify_auth_user_attributes(self, zone, user_info):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_modify_auth_user_attributes(auth_service_id, user_info)
    
    def resource_delete_auth_users(self, zone, user_names):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_delete_auth_users(auth_service_id, user_names)

    def resource_reset_auth_user_password(self, zone, user_name, password):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_reset_auth_user_password(auth_service_id, user_name, password)

    def resource_set_auth_user_status(self, zone, user_names, status):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]
        if not isinstance(user_names, list):
            user_names = [user_names]
        
        return handler.resource_set_auth_user_status(auth_service_id, user_names, status)

    def resource_refresh_auth_service(self, zone, base_dn):
        
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_refresh_auth_service(auth_service_id, base_dn)

    def resource_describe_auth_ous(self, zone, base_dn,ou_names, scope=1, syn_desktop=0):
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_describe_auth_ous(auth_service_id, base_dn, ou_names,scope, syn_desktop)

    def resource_create_auth_ou(self, zone, base_dn, ou_name, description=''):
        
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_create_auth_ou(auth_service_id, base_dn, ou_name, description)

    def resource_add_auth_user_to_user_group(self, zone, user_group_dn, user_names):
        
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_add_auth_user_to_user_group(auth_service_id, user_group_dn, user_names)

    def resource_remove_auth_user_from_user_group(self, zone, user_group_dn, user_names):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        zone_auth = self.ctx.pgm.get_auth_zone(zone)
        if not zone_auth:
            return None
        auth_service_id = zone_auth["auth_service_id"]

        return handler.resource_remove_auth_user_from_user_group(auth_service_id, user_group_dn, user_names)


    def resource_describe_rdbs(self, zone,service_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_rdbs(service_id)

    def resource_describe_clusters(self, zone,service_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_clusters(service_id)

    def resource_describe_caches(self, zone,service_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_caches(service_id)

    def resource_describe_loadbalancers(self, zone,service_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_loadbalancers(service_id)

    def resource_describe_loadbalancer_backends(self, zone,service_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_loadbalancer_backends(service_id)

    def resource_describe_nics_with_private_ip(self, zone, private_ip=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_nics_with_private_ip(private_ip)

    def resource_describe_instances_by_search_word(self, zone,req=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_describe_instances_by_search_word(user_id,req)

    def resource_modify_cluster_attributes(self, zone, service_type, service_id,service_name,description=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_modify_cluster_attributes(user_id,service_type, service_id,service_name,description)

    def resource_modify_cache_attributes(self, zone, service_type, service_id,service_name,description=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_modify_cache_attributes(user_id,service_type, service_id,service_name,description)

    def resource_modify_rdb_attributes(self, zone, service_type, service_id,service_name,description=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_modify_rdb_attributes(user_id,service_type, service_id,service_name,description)

    def resource_modify_s2server_attributes(self, zone, service_type, service_id,service_name,description=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_modify_s2server_attributes(user_id,service_type, service_id,service_name,description)

    def resource_modify_loadbalancer_attributes(self, zone, service_type, service_id,service_name,description=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_modify_loadbalancer_attributes(user_id,service_type, service_id,service_name,description)

    # desktop
    
    def resource_describe_desktops(self, zone, desktop_ids):
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_describe_desktops(desktop_ids)
    
    def resource_start_desktops(self, zone, desktop_group_id=None, desktop_ids=None):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_start_desktops(desktop_group_id, desktop_ids)
    
    def resource_restart_desktops(self, zone, desktop_group_id=None, desktop_ids=None):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_restart_desktops(desktop_group_id, desktop_ids)

    def resource_stop_desktops(self, zone, desktop_group_id=None, desktop_ids=None):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_stop_desktops(desktop_group_id, desktop_ids)

    def resource_modify_desktop_group_attributes(self, zone, desktop_group_id, desktop_count=None, desktop_image=None):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_modify_desktop_group_attributes(desktop_group_id, desktop_count, desktop_image)

    def resource_modify_desktop_group_status(self, zone, desktop_group_id, status):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_modify_desktop_group_status(desktop_group_id, status)

    def resource_apply_desktop_group(self, zone, desktop_group_id):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_apply_desktop_group(desktop_group_id)

    def resource_create_desktop_group(self, zone, param):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_create_desktop_group(param)

    def resource_create_app_desktop_group(self, zone, param):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_create_app_desktop_group(param)

    def resource_wait_desktop_jobs_done(self, zone, job_ids):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_wait_desktop_jobs_done(job_ids)
    
    def resource_describe_desktop_tasks(self, zone, job_ids):
        
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_desktop_tasks(job_ids)
    
    def resource_add_desktop_to_delivery_group(self, zone, param):
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
        
        return handler.resource_add_desktop_to_delivery_group(param)
    
    def resource_reload_image(self, zone, image_id):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_reload_image(image_id)

    def resource_add_user_to_delivery_group(self, zone, param):
        
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_add_user_to_delivery_group(param)
        
    def resource_del_user_from_delivery_group(self, zone, param):
        
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_del_user_from_delivery_group(param)
    
    def resource_detach_user_from_desktop(self, zone, param):
        
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_detach_user_from_desktop(param)

    def resource_delete_desktops(self, zone, param):
        
        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_desktops(param)

    def resource_delete_desktop_from_delivery_group(self,zone, param):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None

        return handler.resource_delete_desktop_from_delivery_group(param)
    
    def resource_detach_desktop_from_delivery_group_user(self,zone, param):

        handler = self.get_desktop_handler(zone)
        if not handler:
            return None
    
        return handler.resource_detach_desktop_from_delivery_group_user(param)

    def resource_clone_instances(self,zone,resource_id,vxnet_id,private_ip=None):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_clone_instances(user_id,resource_id, vxnet_id,private_ip)

    def resource_describe_s2_accounts(self,zone,search_word):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_describe_s2_accounts(user_id,search_word)

    def resource_describe_s2_groups(self,zone,group_types):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_describe_s2_groups(user_id,group_types)

    def resource_create_s2_account(self,zone,account_name,account_type,nfs_ipaddr,s2_group,opt_parameters,s2_groups):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_create_s2_account(user_id,account_name,account_type,nfs_ipaddr,s2_group,opt_parameters,s2_groups)

    def resource_update_s2_servers(self,zone,s2_servers):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_update_s2_servers(user_id,s2_servers)

    def resource_poweroff_s2_servers(self, zone, s2_servers):
        # PowerOffS2Servers
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_poweroff_s2_servers(user_id, s2_servers)

    def resource_poweron_s2_servers(self, zone, s2_servers):
        # PowerOnS2Servers
        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_poweron_s2_servers(user_id, s2_servers)

    def resource_describe_tags(self,zone,search_word):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_describe_tags(user_id,search_word)

    def resource_create_tag(self,zone,color,tag_name):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_create_tag(user_id,color,tag_name)

    def resource_attach_tags(self,zone,resource_tag_pairs,selectedData):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_attach_tags(user_id,resource_tag_pairs,selectedData)

    def resource_create_s2_server(self,zone,vxnet_id,s2_server_name,s2_class):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_create_s2_server(user_id,vxnet_id,s2_server_name,s2_class)

    def resource_create_s2_shared_target(self,zone,vxnet,s2_server_id,target_type,export_name_nfs,export_name,volumes):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_create_s2_shared_target(user_id,vxnet,s2_server_id,target_type,export_name_nfs,export_name,volumes)

    def resource_describe_s2servers(self,zone,service_id):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_describe_s2servers(user_id,service_id)

    def resource_get_quota_left(self,zone,resource_type):

        handler = self.get_qc_handler(zone)
        if not handler:
            return None

        if not self.ctx.zone_users:
            logger.error("no config user id in desktop yaml")
            return None

        user_id = self.ctx.zone_users.get(zone)
        if not user_id:
            logger.error("no found zone user")
            return None

        return handler.resource_get_quota_left(user_id,resource_type)

    def resource_add_computer(self, zone, catalog_name, machine_name, machine_id, machine_sid, host_unit):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_add_computer(catalog_name, machine_name, machine_id, machine_sid, host_unit)

    def resource_delete_app_computer(self, zone, machine_name):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_delete_app_computer(machine_name)

    def resource_describe_app_start_memu(self, zone, machine_name):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_app_start_memu(machine_name)
    
    def resource_describe_broker_apps(self, zone, app_names=None, delivery_group_uids=None, app_group_uids=None, index_uid=False):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_broker_apps(app_names, delivery_group_uids, app_group_uids, index_uid)

    def resource_create_broker_app(self, zone, delivery_group_name, hostname, app_data):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_broker_app(delivery_group_name, hostname, app_data)

    def resource_modify_broker_app(self, zone, app_uid, admin_display_name=None, normal_display_name=None, description=None):
        
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_modify_broker_app(app_uid, admin_display_name, normal_display_name, description)

    def resource_add_broker_app(self, zone, app_name, delivery_group_name=None, app_group_name=None):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_add_broker_app(app_name, delivery_group_name, app_group_name)

    def resource_remove_broker_app(self, zone, app_names, delivery_group_uid=None, app_group_uid=None):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_remove_broker_app(app_names, delivery_group_uid, app_group_uid)
    
    def resource_new_broker_folder(self, zone):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_new_broker_folder()
    
    def resource_remove_broker_folder(self, zone):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_remove_broker_folder()

    def resource_describe_broker_folder(self, zone):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_broker_folder()

    def resource_describe_broker_app_groups(self, zone, app_group_names=None, delivery_group_uids=None, index_uid=False):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_describe_broker_app_groups(app_group_names, delivery_group_uids, index_uid)

    def resource_create_broker_app_group(self, zone, app_group_name, description=None):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_create_broker_app_group(app_group_name, description)

    def resource_delete_broker_app_group(self, zone, app_group_name, delivery_group_name=None):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_delete_broker_app_group(app_group_name, delivery_group_name)

    def resource_add_broker_app_group(self, zone, app_group_name, delivery_group_name):

        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        
        return handler.resource_add_broker_app_group(app_group_name, delivery_group_name)

    def resource_create_citrix_policy(self, zone,citrix_policy_names):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_create_citrix_policy(citrix_policy_names)
    	
    def resource_describe_citrix_policies(self, zone,citrix_policy_name=None):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_describe_citrix_policies(citrix_policy_name)
    
    def resource_describe_citrix_policy_items(self, zone,citrix_policy_name):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_describe_citrix_policy_items(citrix_policy_name)    

    def resource_describe_citrix_policy_filters(self, zone,citrix_policy_name):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_describe_citrix_policy_filters(citrix_policy_name)    

    def resource_config_citrix_policy_item(self, zone,citrix_policy_name,policy_items):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_config_citrix_policy_item(citrix_policy_name,policy_items)
    
    def resource_delete_citrix_policy(self, zone,citrix_policy_name):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_delete_citrix_policy(citrix_policy_name)

    def resource_modify_citrix_policy(self, zone,citrix_policy):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_modify_citrix_policy(citrix_policy)
 
    def resource_rename_citrix_policy(self, zone,citrix_policy):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_rename_citrix_policy(citrix_policy)    

    def resource_set_citrix_policy_priority(self, zone,citrix_policy_name,policy_priority):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_set_citrix_policy_priority(citrix_policy_name,policy_priority)   

    def resource_delete_citrix_policy_filter(self, zone,citrix_policy_name,citrix_policy_filter):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_delete_citrix_policy_filter(citrix_policy_name,citrix_policy_filter)

    def resource_add_citrix_policy_filter(self, zone,citrix_policy_name,citrix_policy_filters):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_add_citrix_policy_filter(citrix_policy_name,citrix_policy_filters)    
    
    def resource_modify_citrix_policy_filter(self, zone,citrix_policy_name,citrix_policy_filters):
        handler = self.get_citrix_handler(zone)
        if not handler:
            return None
        return handler.resource_modify_citrix_policy_filter(citrix_policy_name,citrix_policy_filters)     		
