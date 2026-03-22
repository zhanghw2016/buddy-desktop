
from connection import QingCloudConnection
from log.logger import logger
from error.error import Error
import constants as const
from qingcloud import const as qconst
import time
from resource_job import ResourceJob
import copy
class QCResource():

    def __init__(self, ctx, zone, conn, http_socket_timeout=120, retry_time=3):
        
        self.zone = zone
        
        self.conn = QingCloudConnection(zone, conn, http_socket_timeout=http_socket_timeout, retry_time=retry_time)
        if not self.conn:
            logger.error("create qingcloud connection fail %s" % (self.zone, conn))
            return None

        self.ctx = ctx
        self.job = ResourceJob(self.conn)
        if not self.job:
            logger.error("QCResrouce Job create fail %s" % self.config)
            return None

        self.resource_action_map = {
            # job
            qconst.ACTION_DESCRIBE_JOBS: self.conn.describe_jobs,
            # instance
            qconst.ACTION_LEASE: self.conn.lease_desktop,
            qconst.ACTION_DESCRIBE_INSTANCES: self.conn.describe_instances,
            qconst.ACTION_RUN_INSTANCES: self.conn.run_instances,
            qconst.ACTION_CLONE_INSTANCES: self.conn.clone_instances,
            qconst.ACTION_TERMINATE_INSTANCES: self.conn.terminate_instances,
            qconst.ACTION_RESTART_INSTANCES: self.conn.restart_instances,
            qconst.ACTION_START_INSTANCES: self.conn.start_instances,
            qconst.ACTION_STOP_INSTANCES: self.conn.stop_instances,
            qconst.ACTION_MODIFY_INSTANCE_ATTRIBUTES: self.conn.modify_instance_attributes,
            qconst.ACTION_RESIZE_INSTANCES: self.conn.resize_instances,
            qconst.ACTION_CREATE_BROKERS: self.conn.create_brokers,
            qconst.ACTION_DELETE_BROKERS: self.conn.delete_brokers,
            qconst.ACTION_DESCRIBE_GPUS: self.conn.describe_gpus,

            # volume
            qconst.ACTION_DESCRIBE_VOLUMES: self.conn.describe_volumes,
            qconst.ACTION_CREATE_VOLUMES: self.conn.create_volumes,
            qconst.ACTION_DELETE_VOLUMES: self.conn.delete_volumes,
            qconst.ACTION_ATTACH_VOLUMES: self.conn.attach_volumes,
            qconst.ACTION_DETACH_VOLUMES: self.conn.detach_volumes,
            qconst.ACTION_RESIZE_VOLUMES: self.conn.resize_volumes,
            qconst.ACTION_MODIFY_VOLUME_ATTRIBUTES: self.conn.modify_volume_attributes,
            # image
            qconst.ACTION_DESCRIBE_IMAGES: self.conn.describe_images,
            qconst.ACTION_CAPTURE_INSTANCE: self.conn.capture_instance,
            qconst.ACTION_DELETE_IMAGES: self.conn.delete_images,
            qconst.ACTION_MODIFY_IMAGE_ATTRIBUTES: self.conn.modify_image_attributes,
            # nics
            qconst.ACTION_DESCRIBE_NICS: self.conn.describe_nics,
            qconst.ACTION_CREATE_NICS: self.conn.create_nics,
            qconst.ACTION_DELETE_NICS: self.conn.delete_nics,
            qconst.ACTION_MODIFY_NIC_ATTRIBUTES: self.conn.modify_nic_attributes,
            qconst.ACTION_ATTACH_NICS: self.conn.attach_nics,
            qconst.ACTION_DETACH_NICS: self.conn.detach_nics,
            # vxnet
            qconst.ACTION_DESCRIBE_VXNETS: self.conn.describe_vxnets,
            qconst.ACTION_CREATE_VXNETS: self.conn.create_vxnets,
            qconst.ACTION_DELETE_VXNETS: self.conn.delete_vxnets,
            qconst.ACTION_JOIN_VXNET: self.conn.join_vxnet,
            qconst.ACTION_LEAVE_VXNET: self.conn.leave_vxnet,
            qconst.ACTION_MODIFY_VXNET_ATTRIBUTES: self.conn.modify_vxnet_attributes,
            qconst.ACTION_DESCRIBE_VXNET_INSTANCES: self.conn.describe_vxnet_instances,
            qconst.ACTION_DESCRIBE_VXNET_RESOURCES: self.conn.describe_vxnet_resources,
            # router
            qconst.ACTION_DESCRIBE_ROUTERS: self.conn.describe_routers,
            qconst.ACTION_DESCRIBE_ROUTER_VXNETS: self.conn.describe_router_vxnets,
            qconst.ACTION_JOIN_ROUTER: self.conn.join_router,
            qconst.ACTION_LEAVE_ROUTER: self.conn.leave_router,
            # monitor 
            qconst.ACTION_GET_MONITOR: self.conn.get_monitoring_data,
            qconst.ACTION_DESCRIBE_INSTANCES_WITH_MONITORS: self.conn.describe_instances_with_monitors,
            # vdi
            qconst.ACTION_SEND_VDI_GUEST_MESSAGE: self.conn.send_desktop_message,
            qconst.ACTION_SEND_VDI_GUEST_KEYS: self.conn.send_desktop_hot_keys,
            
            # security group
            qconst.ACTION_DESCRIBE_SECURITY_GROUPS: self.conn.describe_security_groups,
            qconst.ACTION_CREATE_SECURITY_GROUP: self.conn.create_security_group,
            qconst.ACTION_MODIFY_SECURITY_GROUP_ATTRIBUTES: self.conn.modify_security_group_attributes,
            qconst.ACTION_APPLY_SECURITY_GROUP: self.conn.apply_security_group,
            qconst.ACTION_DELETE_SECURITY_GROUPS: self.conn.delete_security_groups,
            qconst.ACTION_REMOVE_SECURITY_GROUP: self.conn.remove_security_group,
            qconst.ACTION_ROLLBACK_SECURITY_GROUP: self.conn.rollback_security_group,
            # rule
            qconst.ACTION_DESCRIBE_SECURITY_GROUP_RULES: self.conn.describe_security_group_rules,
            qconst.ACTION_ADD_SECURITY_GROUP_RULES: self.conn.add_security_group_rules,
            qconst.ACTION_DELETE_SECURITY_GROUP_RULES: self.conn.delete_security_group_rules,
            qconst.ACTION_MODIFY_SECURITY_GROUP_RULE_ATTRIBUTES: self.conn.modify_security_group_rule_attributes,
            
            # ipset
            qconst.ACTION_DESCRIBE_SECURITY_GROUP_IPSETS: self.conn.describe_security_group_ipsets,
            qconst.ACTION_CREATE_SECURITY_GROUP_IPSET: self.conn.create_security_group_ipset,
            qconst.ACTION_DELETE_SECURITY_GROUP_IPSETS: self.conn.delete_security_group_ipsets,
            qconst.ACTION_MODIFY_SECURITY_GROUP_IPSET_ATTRIBUTES: self.conn.modify_security_group_ipset_attributes,
            qconst.ACTION_APPLY_SECURITY_GROUP_IPSETS: self.conn.apply_security_group_ipsets,
            
            # rule set
            qconst.ACTION_APPLY_SECURITY_GROUP_RULESET: self.conn.apply_security_group_ruleset,
            qconst.ACTION_DESCRIBE_SECURITY_GROUP_AND_RULESET: self.conn.describe_security_group_and_ruleset,
            qconst.ACTION_ADD_SECURITY_GROUP_RULESETS: self.conn.add_security_group_rulesets,
            qconst.ACTION_REMOVE_SECURITY_GROUP_RULESETS: self.conn.remove_security_group_rulesets,
            
            qconst.ACTION_DESCRIBE_SECURITY_GROUP_SNAPSHOTS: self.conn.describe_security_group_snapshots,
            qconst.ACTION_CREATE_SECURITY_GROUP_SNAPSHOT: self.conn.create_security_group_snapshot,
            qconst.ACTION_DELETE_SECURITY_GROUP_SNAPSHOTS: self.conn.delete_security_group_snapshots,

            # snapshot
            qconst.ACTION_CREATE_SNAPSHOTS: self.conn.create_snapshots,
            qconst.ACTION_DELETE_SNAPSHOTS: self.conn.delete_snapshots,
            qconst.ACTION_APPLY_SNAPSHOTS: self.conn.apply_snapshots,
            qconst.ACTION_DESCRIBE_SNAPSHOTS: self.conn.describe_snapshots,
            qconst.ACTION_MODIFY_SNAPSHOT_ATTRIBUTES: self.conn.modify_snapshot_attributes,
            qconst.ACTION_CAPTURE_INSTANCE_FROM_SNAPSHOT: self.conn.capture_instance_from_snapshot,
            qconst.ACTION_CREATE_VOLUME_FROM_SNAPSHOT: self.conn.create_volume_from_snapshot,
            
            # zone
            qconst.ACTION_DESCRIBE_ZONES: self.conn.describe_zones,
            qconst.ACTION_GET_RESOURCE_LIMIT: self.conn.get_resource_limit,
            qconst.ACTION_DESCRIBE_PLACE_GROUPS: self.conn.describe_place_groups,
            qconst.ACTION_DESCRIBE_ACCESS_KEYS: self.conn.describe_access_keys,
            qconst.ACTION_DESCRIBE_USERS: self.conn.describe_users,

            # ssh keypair
            qconst.ACTION_DESCRIBE_SSH_KEY_PAIRS: self.conn.describe_keypairs,
            qconst.ACTION_CREATE_SSH_KEY_PAIR: self.conn.create_keypair,

            # desktop_service_management
            qconst.ACTION_MODIFY_RDB_ATTRIBUTES: self.conn.modify_rdb_attributes,
            qconst.ACTION_MODIFY_CACHE_ATTRIBUTES: self.conn.modify_cache_attributes,
            qconst.ACTION_MODIFY_S2SERVER_ATTRIBUTES: self.conn.modify_s2server_attributes,
            qconst.ACTION_MODIFY_LOADBALANCER_ATTRIBUTES: self.conn.modify_loadbalancer_attributes,
            qconst.ACTION_DESCRIBE_RDBS: self.conn.describe_rdbs,
            qconst.ACTION_DESCRIBE_CLUSTERS: self.conn.describe_clusters,
            qconst.ACTION_DESCRIBE_CACHES: self.conn.describe_caches,
            qconst.ACTION_DESCRIBE_LOADBALANCERS: self.conn.describe_loadbalancers,
            qconst.ACTION_DESCRIBE_LOADBALANCER_BACKENDS: self.conn.describe_loadbalancer_backends,
            qconst.ACTION_DESCRIBE_S2SERVERS: self.conn.describe_s2servers,
            qconst.ACTION_MODIFY_CLUSTER_ATTRIBUTES: self.conn.modify_cluster_attributes,

            # s2
            qconst.ACTION_DESCRIBE_S2_GROUPS: self.conn.describe_s2_groups,
            qconst.ACTION_CREATE_S2_ACCOUNT: self.conn.create_s2_account,
            qconst.ACTION_DESCRIBE_S2_ACCOUNTS: self.conn.describe_s2_accounts,
            qconst.ACTION_UPDATE_S2_SERVERS: self.conn.update_s2_servers,
            qconst.ACTION_CREATE_S2_SERVER: self.conn.create_s2_server,
            qconst.ACTION_CREATE_S2_SHARED_TARGET: self.conn.create_s2_shared_target,
            qconst.ACTION_POWEROFF_S2_SERVERS: self.conn.poweroff_s2_servers,
            qconst.ACTION_POWERON_S2_SERVERS: self.conn.poweron_s2_servers,

            # tag
            qconst.ACTION_DESCRIBE_TAGS: self.conn.describe_tags,
            qconst.ACTION_CREATE_TAG: self.conn.create_tag,
            qconst.ACTION_ATTACH_TAGS: self.conn.attach_tags,

            # quota
            qconst.ACTION_GET_QUOTA_LEFT: self.conn.get_quota_left,

        }

        self.action_return_key ={
            qconst.ACTION_DESCRIBE_INSTANCES: "instance_set",
            qconst.ACTION_RUN_INSTANCES: "instances",
            qconst.ACTION_CLONE_INSTANCES: "instances",
            qconst.ACTION_DESCRIBE_VOLUMES: "volume_set",
            qconst.ACTION_CREATE_VOLUMES: "volumes",
            qconst.ACTION_DESCRIBE_IMAGES: "image_set",
            qconst.ACTION_CAPTURE_INSTANCE: "image_id",
            qconst.ACTION_DESCRIBE_NICS: "nic_set",
            qconst.ACTION_CREATE_NICS: "nics",
            qconst.ACTION_DESCRIBE_VXNETS: "vxnet_set",
            qconst.ACTION_CREATE_VXNETS: "vxnets",
            qconst.ACTION_DESCRIBE_VXNET_INSTANCES: "instance_set",
            qconst.ACTION_DESCRIBE_VXNET_RESOURCES: "vxnet_resource_set",
            qconst.ACTION_GET_MONITOR: "meter_set",
            qconst.ACTION_DESCRIBE_INSTANCES_WITH_MONITORS: "instance_set",
            qconst.ACTION_CREATE_BROKERS: "brokers",
            qconst.ACTION_CREATE_SECURITY_GROUP: "security_group_id",
            qconst.ACTION_DESCRIBE_SNAPSHOTS: "snapshot_set",
            qconst.ACTION_CREATE_SNAPSHOTS: 'snapshots',
            qconst.ACTION_CAPTURE_INSTANCE_FROM_SNAPSHOT: 'image_id',
            qconst.ACTION_CREATE_VOLUME_FROM_SNAPSHOT: 'volume_id',
            qconst.ACTION_DESCRIBE_SECURITY_GROUPS: "security_group_set",
            qconst.ACTION_CREATE_SECURITY_GROUP: "security_group_id", 
            qconst.ACTION_DESCRIBE_SECURITY_GROUP_RULES: "security_group_rule_set",
            qconst.ACTION_DESCRIBE_SECURITY_GROUP_AND_RULESET: "security_groups_or_rulesets_set",
            qconst.ACTION_ADD_SECURITY_GROUP_RULES: "security_group_rules",
            qconst.ACTION_DESCRIBE_SECURITY_GROUP_IPSETS: "security_group_ipset_set",
            qconst.ACTION_CREATE_SECURITY_GROUP_IPSET: "security_group_ipset_id",
            qconst.ACTION_DESCRIBE_ZONES: "zone_set",
            qconst.ACTION_DESCRIBE_PLACE_GROUPS: "place_group_set",
            qconst.ACTION_DESCRIBE_ROUTERS: "router_set",
            qconst.ACTION_DESCRIBE_RDBS: "rdb_set",
            qconst.ACTION_DESCRIBE_CLUSTERS: "cluster_set",
            qconst.ACTION_DESCRIBE_CACHES: "cache_set",
            qconst.ACTION_DESCRIBE_LOADBALANCERS: "loadbalancer_set",
            qconst.ACTION_DESCRIBE_LOADBALANCER_BACKENDS: "loadbalancer_backend_set",
            qconst.ACTION_DESCRIBE_S2SERVERS: "s2_server_set",
            qconst.ACTION_DESCRIBE_S2_GROUPS: "s2_group_set",
            qconst.ACTION_DESCRIBE_S2_ACCOUNTS: "s2_account_set",
            qconst.ACTION_CREATE_S2_ACCOUNT: "s2_account_id",
            qconst.ACTION_DESCRIBE_ACCESS_KEYS: "access_key_set",
            qconst.ACTION_DESCRIBE_USERS: "user_set",
            qconst.ACTION_DESCRIBE_SSH_KEY_PAIRS: "keypair_set",
            qconst.ACTION_CREATE_SSH_KEY_PAIR: "keypair_id",
            qconst.ACTION_DESCRIBE_TAGS: "tag_set",
            qconst.ACTION_CREATE_TAG: "tag_id",
            qconst.ACTION_ATTACH_TAGS: "tag_id",
            qconst.ACTION_CREATE_S2_SERVER: "s2_server",
            qconst.ACTION_CREATE_S2_SHARED_TARGET: "s2_shared_target",
            qconst.ACTION_GET_QUOTA_LEFT: "quota_left_set",
        }
        self.SEARCH_RES_DESCRIBE_ACTION = {
            qconst.SEARCH_RES_INST_TYPE: qconst.ACTION_DESCRIBE_INSTANCES,
            qconst.SEARCH_RES_VOLUME_TYPE: qconst.ACTION_DESCRIBE_VOLUMES,
            qconst.SEARCH_RES_IMAGE_TYPE: qconst.ACTION_DESCRIBE_IMAGES,
            qconst.SEARCH_RES_NIC_TYPE: qconst.ACTION_DESCRIBE_NICS,
            qconst.SEARCH_RES_SNAPSHOT_TYPE: qconst.ACTION_DESCRIBE_SNAPSHOTS,
        }

        self.SEARCH_RES_ID = {
            qconst.SEARCH_RES_INST_TYPE: "instance_id",
            qconst.SEARCH_RES_VOLUME_TYPE: "volume_id",
            qconst.SEARCH_RES_IMAGE_TYPE: "image_id",
            qconst.SEARCH_RES_NIC_TYPE: "nic_id",
            qconst.SEARCH_RES_SNAPSHOT_TYPE: "snapshot_id"
        }

    def search_nics(self, search_word, retries=qconst.RES_ACTION_RETRIES):
        
        nics = {}
        body = {"search_word": search_word, "limit": const.MAX_LIMIT_PARAM, "offset": 0}      
        while True:
            ret = self.conn.describe_nics(body)
            if isinstance(ret, Error):
                logger.error("search nics return error : %s" % body)
                return None

            if self.conn.check_res_error(ret, body):
                if ret is None:
                    retries -= 1
                    if retries == 0:
                        logger.error("try describe volume fail[%s], retry[%s]" % (body, retries))
                        return None
                else:
                    return None

                time.sleep(qconst.RES_ACTION_RETRY_INTERVAL)
            else:
                nic_set = ret["nic_set"]
                total_count = ret["total_count"]
                if not nic_set:
                    return nics
    
                for nic in nic_set:
                    nic_id = nic["nic_id"]
                    nics[nic_id] = nic
                
                offset = body.get("offset", 0)
                limit = body.get("limit", 100)

                offset = offset + limit
    
                if offset > total_count:
                    return nics
    
                body["offset"] = offset  
                
                time.sleep(qconst.JOB_INTERVAL_3S)

    def try_search_resource(self, res_type, search_word, retries=qconst.RES_ACTION_RETRIES):
        
        if not search_word:
            return None
        
        if isinstance(search_word, list):
            search_word = search_word[0]
        
        if res_type == qconst.SEARCH_RES_NIC_TYPE:
            return self.search_nics(search_word)
        
        action = self.SEARCH_RES_DESCRIBE_ACTION.get(res_type)
        if not action:
            return None

        body = {"search_word": search_word, "limit": 1}
        while True:
            ret = self.resource_action_map[action](body)
            if isinstance(ret, Error):
                logger.error("search %s send request return error: %s" % (res_type, body))
                return None

            if self.conn.check_res_error(ret, body):
                if ret is None:
                    retries -= 1
                    if retries == 0:
                        logger.error("retry search %s fail[%s]" % (res_type, body))
                        return None
                else:
                    return None
    
                time.sleep(qconst.RES_ACTION_RETRY_INTERVAL)
    
            else:
                set_key = self.action_return_key.get(action, None)
                if not set_key:
                    return None
                    
                resource_set = ret.get(set_key)
                # maybe, run instance request no receive
                if resource_set is None:
                    return None
                
                if not resource_set:
                    return {}
                
                resource_ids = []
                for resource in resource_set:
                    resource_key = self.SEARCH_RES_ID.get(res_type)
                    if not resource_key:
                        return None
                
                    resource_id = resource.get(resource_key)
                    resource_ids.append(resource_id)
                
                return resource_ids

    def search_resource(self, action, search_word, retry_create):

        res_type = None
        # instance
        if action in qconst.SEARCH_TYPE_INST:
            res_type = qconst.SEARCH_RES_INST_TYPE
        # volume
        elif action in qconst.SEARCH_TYPE_VOL:
            res_type = qconst.SEARCH_RES_VOLUME_TYPE
        # image
        elif action in qconst.SEARCH_TYPE_IMG:
            res_type = qconst.SEARCH_RES_IMAGE_TYPE
        # snapshot
        elif action in qconst.SEARCH_TYPE_SNAPSHOT:
            res_type = qconst.SEARCH_RES_SNAPSHOT_TYPE
        # nic
        elif action in qconst.SEARCH_TYPE_NIC:
            res_type = qconst.SEARCH_RES_NIC_TYPE
        else:
            logger.error("search action %s, no found resource type" % action)
            return None

        ret = self.try_search_resource(res_type, search_word)
        if ret:
            return ret
        
        if ret is None:
            logger.error("action %s, no search any resource" % action)
            return None

        if action not in qconst.RETRY_CREATE:
            retry_create = False
            return None

        if not retry_create:
            retry_create = True
        else:
            retry_create = False
        
        return None

    def search_job(self, job_action, resource_ids, retries=qconst.RES_ACTION_RETRIES):
    
        if not isinstance(resource_ids, list):
            resource_ids = [resource_ids]

        while True:
            body = {
                'job_action': job_action,
                'resource_ids': resource_ids,
                'limit': 1
                }
            ret = self.conn.describe_jobs(body)
            if self.conn.check_res_error(ret, body):
                if ret is None:
                    retries -= 1
                    if retries == 0:
                        logger.error("describe job [%s] fail, retries: %s" % (resource_ids, retries))
                        return None
                else:
                    return None
    
                time.sleep(qconst.RES_ACTION_RETRY_INTERVAL)
            else:
                job_set = ret.get("job_set")
                if not job_set:
                    logger.error("describe no found jobs : %s" % body)
                    return None

                job = job_set[0]
                job_id = job["job_id"]
                jobs = self.ctx.pgm.get_resource_jobs(job_id)
                if not jobs:
                    logger.error("search job by describe resource done %s, %s, %s" % (job_action, resource_ids, job_id))
                    return job_id

                return None
    
    # handle instance, return (job_id, resource_id)
    def handle_resource(self, action, directive, retries=qconst.RES_ACTION_RETRIES, return_all=False):
        
        if action not in self.resource_action_map:
            logger.error("handle instance no found instance map : %s, %s" % (action, directive))
            return None

        body = directive.get("body")
        retry_create = False
        while True:

            ret = self.resource_action_map[action](body)
            if isinstance(ret, Error):
                logger.error("action %s send request return error %s, %s" % (action, body, ret))
                return None

            # maybe send request timeout, need search action job
            if not ret:
                if action in qconst.SERACH_ACTIONS:
                    search = directive.get("search")
                    if not search:
                        logger.error("handle resource return None, no found search: %s" % directive)
                        return None
    
                    resource_ids = search.get("resource_ids")
                    search_word = search.get("search_word")
                    if not resource_ids and not search_word:
                        logger.error("handle resource return None, no found search word or no resource ids: %s" % search)
                        return None

                    # run instance, only search hostname to get instance
                    if not resource_ids:
                        search_ret = self.search_resource(action, search_word, retry_create)
                        if not search_ret and not retry_create:
                            return None
    
                        if search_ret:
                            resource_ids = search_ret
                        elif retry_create:
                            time.sleep(qconst.RES_ACTION_RETRY_INTERVAL)
                            continue
                        else:
                            logger.error("no search resource ids %s" % (action, search_word))
                            return None

                    if action in qconst.JOB_ACTIONS:
                        # search job by action and resource_id
                        ret = self.search_job(action, resource_ids)
                        if not ret:
                            logger.error("search action job fail : %s, %s" % (action, resource_ids))
                            return None
        
                        job_id = ret
                        return (resource_ids, job_id)
                    else:
                        return (resource_ids, None)

                elif action not in qconst.DESCRIBE_ACTIONS:
                    return None
                    
            else:
                if ret["ret_code"] != 0:
                    logger.error("action %s return error : %s, %s" % (action, body, ret))
                    if action not in qconst.RETRY_ACTIONS:
                        return None
                else:
                    if return_all:
                        return ret
                    
                    data_key = self.action_return_key.get(action, None)
                    if data_key:
                        ret_value = ret[data_key]
                    else:
                        ret_value = None

                    if action in qconst.JOB_ACTIONS:
                        job_id = ret.get("job_id")
                        return (ret_value, job_id)
                    else:
                        return (ret_value, None)

            retries -= 1
            if retries <= 0:
                logger.error("action %s retry fail: %s" % (action, body))
                return None

            time.sleep(qconst.RES_ACTION_RETRY_INTERVAL)

        return None
    
    def resource_wait_job_done(self, job_id, interval=qconst.JOB_INTERVAL_20S):
    
        ret = self.job.wait_job_done(job_id, interval=interval)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (job_id, ret))
            return None
        
        return job_id

    # instances
    def resource_search_instances(self, search_word=None, status=None):

        instances = {}

        action = qconst.ACTION_DESCRIBE_INSTANCES
        body = {}
        if search_word and search_word.startswith('i-'):
            body["instances"] = [search_word]
            if status:
                body["status"] = status
            directive = {}
            directive["body"] = body
            
            ret = self.handle_resource(action, directive)
            if ret is None:
                return None
            
            (instance_set, _) = ret
            for instance in instance_set:
                instance_id = instance["instance_id"]
                if instance_id in instances:
                    continue
                instances[instance_id] = instance
        else:
            
            limit = const.MAX_LIMIT_PARAM
            offset = 0
            while True:
                body = {"limit": limit, "offset": offset}
                if search_word:
                    body["search_word"] = search_word

                if status:
                    body["status"] = status
                directive = {}
                directive["body"] = body
    
                ret = self.handle_resource(action, directive, return_all=True)
                if ret is None:
                    return None
                
                total_count = ret["total_count"]
                
                instance_set = ret["instance_set"]
                for instance in instance_set:
                    instance_id = instance["instance_id"]
                    if instance_id in instances:
                        continue
                    instances[instance_id] = instance

                if total_count <= offset:
                    return instances
                
                offset = offset + limit

        return instances 

    # instances
    def resource_lease_desktop(self, instance_ids):

        instances = {}
        
        if not instance_ids:
            return instances

        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]

        action = qconst.ACTION_LEASE

        directive = {}
        body = {"resources": instance_ids}
        directive["body"] = body
        
        ret = self.handle_resource(action, directive)
        logger.error("sssss %s, %s" % (ret, body))
        if ret is None:
            return None

        return instance_ids

    # instances
    def resource_describe_instances(self, instance_ids, status=None):

        instances = {}
        
        if not instance_ids:
            return instances

        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]

        action = qconst.ACTION_DESCRIBE_INSTANCES
        for i in xrange(0, len(instance_ids), const.MAX_LIMIT_PARAM):
            end = i + const.MAX_LIMIT_PARAM
            if end > len(instance_ids):
                end = len(instance_ids)

            inst_ids = instance_ids[i:end]
            directive = {}
            body = {"instances": inst_ids, "limit": const.MAX_LIMIT_PARAM, "offset": 0}
            if status:
                body["status"] = status
            directive["body"] = body

            ret = self.handle_resource(action, directive)
            if ret is None:
                return None

            (instance_set, _) = ret
            for instance in instance_set:
                instance_id = instance["instance_id"]
                if instance_id in instances:
                    continue
                instances[instance_id] = instance

        return instances 

    def resource_run_instance(self, config):

        if not config:
            logger.error("run instance no config")
            return None
        
        directive = {}
        directive["body"] = config
        hostname = config.get("hostname")
        if hostname:
            search = {"search_word": hostname}
            directive["search"] = search
        action = qconst.ACTION_RUN_INSTANCES

        ret = self.handle_resource(action, directive)

        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        (instance_ids, job_id) = ret

        if not instance_ids or not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        instance_id = instance_ids[0]
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return instance_id

    def resource_clone_instances(self, user_id,resource_id, vxnet_id,private_ip=None):

        if resource_id and not isinstance(resource_id, list):
            resource_id = [resource_id]

        if not private_ip:
            vxnets_list = resource_id[0] + "|" + vxnet_id
            config = { "owner":user_id,"instances": resource_id,"vxnets":[vxnets_list]}
        else:
            vxnets_list = resource_id[0] + "|" + vxnet_id + "|" + private_ip
            config = {"owner": user_id, "instances": resource_id, "vxnets": [vxnets_list]}

        directive = {}
        directive["body"] = config
        action = qconst.ACTION_CLONE_INSTANCES

        ret = self.handle_resource(action, directive)

        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        (instance_ids, job_id) = ret
        if not instance_ids or not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        instance_id = instance_ids[0]
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return instance_id

    def resource_terminate_instances(self, instance_id):

        directive = {}
        directive["body"] = {"instances": [instance_id]}
        directive["search"] = {"resource_ids": instance_id}
        action = qconst.ACTION_TERMINATE_INSTANCES
        ret = self.handle_resource(action, directive)
        if not ret:
            action = qconst.ACTION_DESCRIBE_INSTANCES
            directive = {}
            body = {"instances": [instance_id]}
            directive["body"] = body
            ret = self.handle_resource(action, directive)
            if ret is None:
                return None
            (instance_set, _) = ret
            for instance in instance_set:
                instance_id = instance["instance_id"]
                status = instance["status"]
                if status in [const.INST_STATUS_CEASED, const.INST_STATUS_TERM]:
                    logger.info(" resource [%s] has already been deleted" % (instance_id))
                    return instance_id
                else:
                    logger.error("handle resource action :TerminateInstances fail  %s" % (instance_id))
                    return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return instance_id
        
    def resource_start_instances(self, instance_id):

        directive = {}
        directive["body"] = {"instances": [instance_id]}
        directive["search"] = {"resource_ids": instance_id}
        action = qconst.ACTION_START_INSTANCES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return instance_id
    
    def resource_restart_instances(self, instance_id):

        directive = {}
        directive["body"] = {"instances": [instance_id]}
        directive["search"] = {"resource_ids": instance_id}
        action = qconst.ACTION_RESTART_INSTANCES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return instance_id

    def resource_stop_instances(self, instance_id):

        directive = {}
        directive["body"] = {"instances": [instance_id]}
        directive["search"] = {"resource_ids": instance_id}
        action = qconst.ACTION_STOP_INSTANCES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return instance_id

    def resource_resize_instances(self, instance_id, config):
        
        modify_info = copy.deepcopy(config)
        directive = {}
        directive["body"] = modify_info
        
        if directive["body"]:
            directive["body"]["instances"] = [instance_id]
            
        directive["search"] = {"resource_ids": instance_id}
        
        action = qconst.ACTION_RESIZE_INSTANCES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return instance_id

    def resource_modify_instance_attributes(self, instance_id, config):
        
        directive = {}
        body = {"instance": instance_id}
        modify_key = ["ivshmem", "usbredir", "clipboard", "filetransfer", "qxl_number", "instance_name", "description"]
        for key in modify_key:
            if key not in config:
                continue
            body[key] = config[key]
        if not body:
            return None

        directive["body"] = body
        action = qconst.ACTION_MODIFY_INSTANCE_ATTRIBUTES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return instance_id

    # gpus
    def resource_describe_gpus(self, gpu_class=None, status=[const.GPU_STATUS_AVAIL]):
        
        offset = 0
        limit = const.MAX_LIMIT_PARAM
        action = qconst.ACTION_DESCRIBE_GPUS
        gpus = []
        while True:
            directive = {}
            body = {"status": status, "offset":offset, "limit":limit}
            directive["body"] = body
            ret = self.handle_resource(action, directive, return_all=True)
            if ret is None:
                logger.error("handle nic resource fail %s" % body)
                return None

            gpu_set = ret["gpu_set"]
            for gpu in gpu_set:
                if gpu_class is not None:
                    if gpu["gpu_class"] != gpu_class:
                        continue
                gpus.append(gpu)

            total_count = ret["total_count"]
            if total_count <= offset:
                return gpus
            
            offset = offset + limit

    def resource_create_brokers(self, instance_id, is_token=0):

        directive = {}
        body = {"instances": [instance_id]}
        if is_token:
            body["is_token"] = is_token
        directive["body"] = body
        action = qconst.ACTION_CREATE_BROKERS
        ret = self.handle_resource(action, directive)
        if ret is None:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        (broker, _) = ret
        return broker

    def resource_delete_brokers(self, instance_ids):

        directive = {}
        body = {"instances": instance_ids}
        directive["body"] = body
        action = qconst.ACTION_DELETE_BROKERS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        return ret

    # volume
    def resource_describe_volumes(self, volume_ids, status=None):
        
        volumes = {}
        if not volume_ids:
            return volumes

        if not isinstance(volume_ids, list):
            volume_ids = [volume_ids]
        
        if status and not isinstance(status, list):
            status = [status]
        
        action = qconst.ACTION_DESCRIBE_VOLUMES
        for i in xrange(0, len(volume_ids), const.MAX_LIMIT_PARAM):
            end = i + const.MAX_LIMIT_PARAM
            if end > len(volume_ids):
                end = len(volume_ids)
            vol_ids = volume_ids[i:end]

            directive = {}
            body = {"volumes": vol_ids, "limit": const.MAX_LIMIT_PARAM, "offset": 0}
            if status:
                body["status"] = status
            
            directive["body"] = body
            ret = self.handle_resource(action, directive)
            if ret is None:
                logger.error("handle resource action :%s fail  %s" % (action, directive))
                return None
            (volume_set, _) = ret
            for volume in volume_set:
                volume_id = volume["volume_id"]
                volumes[volume_id] = volume

        return volumes
    
    def resource_create_volume(self, size, volume_type, volume_name):
        
        directive = {}
        body = {
            "size": size,
            "volume_type": volume_type,
            "volume_name": volume_name
        }
        directive["body"] = body
        search = {"search_word": volume_name}
        directive["search"] = search
        
        action = qconst.ACTION_CREATE_VOLUMES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (volume_ids, job_id) = ret
        if not volume_ids or not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        volume_id = volume_ids[0]
        return volume_id
    
    def resource_delete_volumes(self, volume_ids):

        directive = {}
        if not volume_ids:
            return volume_ids
                
        body = {"volumes": volume_ids}
        directive["body"] = body
        search = {"resource_ids": volume_ids}
        directive["search"] = search
        action = qconst.ACTION_DELETE_VOLUMES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return volume_ids
    
    def resource_resize_volumes(self, volume_ids, size):
        
        if not isinstance(volume_ids, list):
            volume_ids = [volume_ids]
        directive = {}
        body = {
            "volumes": volume_ids,
            "size": size
        }
        directive["body"] = body
        search = {"resource_ids": volume_ids}
        directive["search"] = search
        action = qconst.ACTION_RESIZE_VOLUMES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None
        
        return volume_ids
    
    def resource_attach_volumes(self, volume_ids, instance_id):
        directive = {}
        body = {
            "volumes": volume_ids,
            "instance": instance_id
        }
        directive["body"] = body
        resource_ids = []
        resource_ids.extend(volume_ids)
        resource_ids.append(instance_id)
        search = {"resource_ids": resource_ids}
        directive["search"] = search
        action = qconst.ACTION_ATTACH_VOLUMES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return volume_ids
    
    def resource_detach_volumes(self, volume_ids, instance_id):
        directive = {}
        body = {
            "volumes": volume_ids,
            "instance": instance_id
        }
        directive["body"] = body
        resource_ids = []
        resource_ids.extend(volume_ids)
        resource_ids.append(instance_id)
        search = {"resource_ids": resource_ids}
        directive["search"] = search
        action = qconst.ACTION_DETACH_VOLUMES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return volume_ids
    
    def resource_modify_volume_attributes(self, volume_id, body):

        directive = {}
        if "volume" not in body:
            body.update({"volume": volume_id})

        directive["body"] = body
        action = qconst.ACTION_MODIFY_VOLUME_ATTRIBUTES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return volume_id
    
    # image
    def resource_describe_images(self, user_id, image_ids=None, status=None, req=None):

        if image_ids and not isinstance(image_ids, list):
            image_ids = [image_ids]
        
        if status and not isinstance(status, list):
            status = [status]
        
        images = {}
        if image_ids:
            
            for i in xrange(0, len(image_ids), const.MAX_LIMIT_PARAM):
                end = i + const.MAX_LIMIT_PARAM
                if end > len(image_ids):
                    end = len(image_ids)
                img_ids = image_ids[i:end]
                
                directive = {}
                body = {"images": img_ids, "offset":0, "limit": const.MAX_LIMIT_PARAM}
                if status:
                    body["status"] = status
                body["sort_key"] = "image_name"
                directive["body"] = body
                action = qconst.ACTION_DESCRIBE_IMAGES
                ret = self.handle_resource(action, directive)
                if not ret:
                    logger.error("handle resource action :%s fail  %s" % (action, directive))
                    continue
                
                image_set, _ = ret
                for image in image_set:
                    image_id = image["image_id"]
                    images[image_id] = image
            
            return images

        elif req is not None:
            
            offset = 0
            limit = const.MAX_LIMIT_PARAM
            if status:
                req["status"] = status
            req["owner"] = user_id

            while True:
                req["offset"] = offset
                req["limit"] = limit
                directive = dict(body = req)

                action = qconst.ACTION_DESCRIBE_IMAGES
                ret = self.handle_resource(action, directive, return_all=True)
                if not ret:
                    logger.error("handle resource action :%s fail  %s" % (action, directive))
                    return None
    
                total_count = ret["total_count"]
                image_set = ret["image_set"]
                if not image_set:
                    return images
                
                for image in image_set:
                    image_id = image["image_id"]
                    images[image_id] = image

                if total_count <= offset:
                    return images
            
                offset = offset + limit
        return images
        
    
    def resource_capture_instance(self, instance_id, image_name):

        directive = {}
        body = {
            "image_name": image_name,
            "instance": instance_id
        }
        directive["body"] = body
        search = {"resource_ids": instance_id}
        directive["search"] = search
        action = qconst.ACTION_CAPTURE_INSTANCE
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (image_id, job_id) = ret
        if not job_id or not image_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_60S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return image_id
    
    def resource_delete_images(self, image_ids):

        directive = {}
        if not isinstance(image_ids, list):
            image_ids = [image_ids]
        
        body = {
            "images": image_ids
        }
        directive["body"] = body
        search = {"resource_ids": image_ids}
        directive["search"] = search
        
        action = qconst.ACTION_DELETE_IMAGES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return image_ids
    
    def resource_modify_image_attributes(self, image_id, config):

        directive = {}
        if config:
            config.update({"image": image_id})
        else:
            return None
        
        directive["body"] = config
        action = qconst.ACTION_MODIFY_IMAGE_ATTRIBUTES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return image_id
    
    # nics
    def resource_describe_nics(self, nic_ids=None, vxnet_ids=None, status=None, user_id=None):

        if not nic_ids and not vxnet_ids:
            return None
        if nic_ids and not isinstance(nic_ids, list):
            nic_ids = [nic_ids]
        if status and not isinstance(status, list):
            status = [status]
        if vxnet_ids and not isinstance(vxnet_ids, list):
            vxnet_ids = [vxnet_ids]
        
        action = qconst.ACTION_DESCRIBE_NICS
        nics = {}
        if nic_ids is not None:
            for i in xrange(0, len(nic_ids), const.MAX_LIMIT_PARAM):
                end = i + const.MAX_LIMIT_PARAM
                if end > len(nic_ids):
                    end = len(nic_ids)
                n_ids = nic_ids[i:end]

                directive = {}
                body = {"nics": n_ids, "offset": 0, "limit": const.MAX_LIMIT_PARAM}
                if user_id:
                    body["owner"] = user_id
                if vxnet_ids:
                    body["vxnets"] = vxnet_ids
                if status:
                    body["status"] = status
                directive["body"] = body
                ret = self.handle_resource(action, directive)
                if ret is None:
                    logger.error("handle resource action :%s fail  %s" % (action, directive))
                    return None
                
                (nic_set, _) = ret
                for nic in nic_set:
                    nic_id = nic["nic_id"]
                    nics[nic_id] = nic
    
            return nics

        elif vxnet_ids:
            offset = 0
            limit = const.MAX_LIMIT_PARAM
            while True:
                directive = {}
                body = {"vxnets": vxnet_ids, "offset":offset, "limit":limit}
                if user_id:
                    body["owner"] = user_id

                if status:
                    body["status"] = status

                directive["body"] = body
                ret = self.handle_resource(action, directive, return_all=True)
                if ret is None:
                    logger.error("handle nic resource fail %s" % body)
                    return None

                nic_set = ret["nic_set"]
                for nic in nic_set:
                    nic_id = nic["nic_id"]
                    nics[nic_id] = nic

                total_count = ret["total_count"]
                if total_count <= offset:
                    return nics
                offset = offset + limit
        
        return None
    
    def resource_create_nics(self, vxnet_id, nic_name, nic_count=1, private_ips=None):
    
        directive = {}
        nic_ids = []
        
        if not nic_name:
            nic_name = vxnet_id
        
        if private_ips and not isinstance(private_ips, list):
            private_ips = [private_ips]
        
        if private_ips:
            for i in xrange(0, len(private_ips), const.MAX_LIMIT_PARAM):
                end = i + const.MAX_LIMIT_PARAM
                if end > len(private_ips):
                    end = len(private_ips)
                _ips = private_ips[i:end]
            
                body = {
                    'vxnet': vxnet_id,
                    'count': len(_ips),
                    'private_ips': _ips,
                    'nic_name': nic_name
                }
                directive["body"] = body
                search = {"search_word": nic_name}
                directive["search"] = search
                action = qconst.ACTION_CREATE_NICS
                ret = self.handle_resource(action, directive)
                if not ret:
                    logger.error("handle resource action :%s fail  %s" % (action, directive))
                    return None
                
                (nics, _) = ret
                
                for nic in nics:
                    nic_id = nic["nic_id"]
                    nic_ids.append(nic_id)
        else:
            if not nic_count:
                nic_count = 1
                
            body = {
                'vxnet': vxnet_id,
                'count': nic_count,
                'nic_name': nic_name
            }

            directive["body"] = body
            search = {"search_word": nic_name}
            directive["search"] = search
            action = qconst.ACTION_CREATE_NICS
            ret = self.handle_resource(action, directive)
            if not ret:
                logger.error("handle resource action :%s fail  %s" % (action, directive))
                return None
            
            (nics, _) = ret
            
            for nic in nics:
                nic_id = nic["nic_id"]
                nic_ids.append(nic_id)

        return nic_ids
    
    def resource_delete_nics(self, nic_ids):

        for i in xrange(0, len(nic_ids), const.MAX_LIMIT_PARAM):
            end = i + const.MAX_LIMIT_PARAM
            if end > len(nic_ids):
                end = len(nic_ids)
    
            n_ids = nic_ids[i:end]
            directive = {}
            body = {'nics': n_ids}
            directive["body"] = body
            action = qconst.ACTION_DELETE_NICS
            ret = self.handle_resource(action, directive)
            if not ret:
                logger.error("handle resource action :%s fail  %s" % (action, directive))
                return None
        
        return nic_ids
    
    def resource_attach_nics(self, instance_id, nic_ids):
        directive = {}
        body = {
            "nics": nic_ids,
            "instance": instance_id
        }
        directive["body"] = body
        search = {"resource_ids": instance_id}
        directive["search"] = search
        action = qconst.ACTION_ATTACH_NICS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return nic_ids

    def resource_detach_nics(self, nic_ids):
        directive = {}
        body = {
            "nics": nic_ids,
        }
        directive["body"] = body     
        action = qconst.ACTION_DETACH_NICS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return nic_ids
    
    # vxnet
    def resource_describe_vxnets(self, vxnet_ids=None, vxnet_type=None):
        
        if not vxnet_ids and not vxnet_type:
            return None
        if vxnet_ids and not isinstance(vxnet_ids, list):
            vxnet_ids = [vxnet_ids]
        if vxnet_type and not isinstance(vxnet_type, list):
            vxnet_type = [vxnet_type]

        action = qconst.ACTION_DESCRIBE_VXNETS
        vxnets = {}
        if vxnet_ids:
            for i in xrange(0, len(vxnet_ids), const.MAX_LIMIT_PARAM):
                end = i + const.MAX_LIMIT_PARAM
                if end > len(vxnet_ids):
                    end = len(vxnet_ids)
                des_ids = vxnet_ids[i:end]

                directive = {}
                body = {"vxnets": des_ids, "limit":const.MAX_LIMIT_PARAM, "offset": 0, "verbose": 1}
                if vxnet_type:
                    body["vxnet_type"] = vxnet_type
                directive["body"] = body
                (ret, _) = self.handle_resource(action, directive)
                if not ret:
                    logger.error("handle resource action :%s fail  %s" % (action, directive))
                    continue

                vxnet_set = ret
                for vxnet in vxnet_set:
                    vxnet_id = vxnet["vxnet_id"]
                    vxnets[vxnet_id] = vxnet
                return vxnets

        else:
            directive = {}

            offset = 0
            limit = const.MAX_LIMIT_PARAM
            excluded_vxnets=[]
            excluded_vxnets.append('vxnet-0')

            while True:
                body = {"vxnet_type": vxnet_type, "limit":limit, "offset": offset, "excluded_vxnets": excluded_vxnets}
                directive = {}
                directive["body"] = body
    
                ret = self.handle_resource(action, directive, return_all=True)
                if ret is None:
                    return None
                
                total_count = ret["total_count"]
                
                vxnet_set = ret["vxnet_set"]
                for vxnet in vxnet_set:
                    vxnet_id = vxnet["vxnet_id"]
                    if vxnet_id in vxnets:
                        continue
                    vxnets[vxnet_id] = vxnet

                if total_count <= offset:
                    return vxnets
                
                offset = offset + limit
        
        return vxnets

    def resource_create_vxnets(self, vxnet_type, vxnet_name):
        directive = {}
        body = {
            'vxnet_name': vxnet_name,
            "vxnet_type": vxnet_type
        }
        directive["body"] = body
        search = {"search_word": vxnet_name}
        directive["search"] = search
        action = qconst.ACTION_CREATE_VXNETS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (vxnet_ids, _) = ret
        if not vxnet_ids:
            return None

        return vxnet_ids[0]
    
    def resource_delete_vxnets(self, vxnet_ids):
        
        if not isinstance(vxnet_ids, list):
            vxnet_ids = [vxnet_ids]
        action = qconst.ACTION_DELETE_VXNETS
        for i in xrange(0, len(vxnet_ids), const.MAX_LIMIT_PARAM):
            end = i + const.MAX_LIMIT_PARAM
            if end > len(vxnet_ids):
                end = len(vxnet_ids)
    
            v_ids = vxnet_ids[i:end]
            directive = {}
            body = {'vxnets': v_ids}
            directive["body"] = body
            ret = self.handle_resource(action, directive)
            if not ret:
                logger.error("handle resource action :%s fail  %s" % (action, directive))
                continue

        return vxnet_ids

    def resource_describe_routers(self, owner, router_ids=None):
        directive = {}
    
        routers = {}
        if router_ids and not isinstance(router_ids, list):
            router_ids = [router_ids]
        
        body = {"mode": 0, "status": ["active"], "owner": owner}
        if router_ids:
            body["routers"] = router_ids
    
        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_ROUTERS
        (ret,_) = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
    
        router_set = ret
        for router in router_set:
            router_id = router["router_id"]
            routers[router_id] = router
        return routers

    def resource_describe_managed_networks(self, router_id, owner):
        directive = {}
       
        offset = 0
        limit = const.MAX_LIMIT_PARAM
        vxnets = {}
        
        while True:

            body = {"router": router_id, "owner": owner, "limit":limit, "offset": offset}
            directive["body"] = body
            action = qconst.ACTION_DESCRIBE_ROUTER_VXNETS
            ret = self.handle_resource(action, directive, return_all=True)
            if ret is None:
                return None
        
            total_count = ret["total_count"]
        
            router_vxnet_set = ret
            for vxnet in router_vxnet_set:
                vxnet_id = vxnet["vxnet_id"]
                vxnets[vxnet_id] = vxnet
            
            if total_count <= offset:
                return vxnets
                
            offset = offset + limit
            
        return vxnets

    def resource_join_router(self, vxnet_id, router_id, ip_network):

        directive = {}
        body = {
            'vxnet': vxnet_id,
            "router": router_id,
            "ip_network": ip_network,
        }
        directive["body"] = body
        search = {"resource_ids": vxnet_id}
        directive["search"] = search
        action = qconst.ACTION_JOIN_ROUTER
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s" % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return vxnet_id

    def resource_leave_router(self, router_id, vxnet_ids):
        directive = {}
        if not isinstance(vxnet_ids, list):
            vxnet_ids = [vxnet_ids]
        body = {
            'vxnets': vxnet_ids,
            "router": router_id,
        }
        directive["body"] = body
        search = {"resource_ids": vxnet_ids}
        directive["search"] = search
        action = qconst.ACTION_LEAVE_ROUTER
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return vxnet_ids
    
    def resource_modify_vxnet_attributes(self, vxnet_id, vxnet_name=None, description=None):
        
        directive = {}
        body = {
            'vxnet': vxnet_id,
            "vxnet_name": vxnet_name,
            "description": description
        }
        directive["body"] = body
        action = qconst.ACTION_MODIFY_VXNET_ATTRIBUTES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        return vxnet_id
    
    def resource_describe_vxnet_instances(self, vxnet_id, instance_ids):
        instances = {}
        if not instance_ids:
            logger.error("try describe instances no found instance ids")
            return None
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
        
        action = qconst.ACTION_DESCRIBE_VXNET_INSTANCES
        for i in xrange(0, len(instance_ids), const.MAX_LIMIT_PARAM):
            end = i + const.MAX_LIMIT_PARAM
            if end > len(instance_ids):
                end = len(instance_ids)
    
            inst_ids = instance_ids[i:end]
            directive = {}
            body = {"instances": inst_ids, 'vxnet': vxnet_id}
            directive["body"] = body
            ret = self.handle_resource(action, directive)
            if not ret:
                logger.error("handle resource action :%s fail  %s" % (action, directive))
                continue
            
            (instance_set, _) = ret
            for instance in instance_set:
                instance_id = instance["instance_id"]
                if instance_id in instances:
                    continue

                instances[instance_id] = instance
        return instances 

    def resource_describe_vxnet_resources(self, vxnet_id):
        resources = {}
        
        action = qconst.ACTION_DESCRIBE_VXNET_RESOURCES

        directive = {}
        body = {'vxnet': vxnet_id}
        directive["body"] = body
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return resources
        
        (resource_set, _) = ret
        for resource in resource_set:
            resource_id = resource["resource_id"]
            if resource_id in resources:
                continue

            resources[resource_id] = resource

        return resources 

    def resource_get_monitoring_data(self, resource, meters, step, start_time, end_time, decompress=1):
        
        directive = {}
        body = {
            'resource': resource,
            "meters": meters,
            "step": step,
            "start_time": start_time,
            "end_time": end_time,
            "decompress": decompress,
        }
        action = qconst.ACTION_GET_MONITOR
        directive["body"] = body
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        (meter_set, _) = ret
        return meter_set

    def resource_describe_instances_with_monitors(self, instance_ids):
        instances = {}
        
        if not instance_ids:
            logger.error("try describe instances no found instance ids")
            return None
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
            
        action = qconst.ACTION_DESCRIBE_INSTANCES_WITH_MONITORS
        for i in xrange(0, len(instance_ids), const.MAX_LIMIT_PARAM):
            end = i + const.MAX_LIMIT_PARAM
            if end > len(instance_ids):
                end = len(instance_ids)
    
            inst_ids = instance_ids[i:end]
            directive = {}
            body = {"instances": inst_ids}
            directive["body"] = body
            ret = self.handle_resource(action, directive)
            if not ret:
                continue

            (instance_set, _) = ret
            for instance in instance_set:
                instance_id = instance["instance_id"]
                if instance_id in instances:
                    continue

                instances[instance_id] = instance

        return instances 
    
    def resource_send_desktop_message(self, instance_ids, base64_message):
        
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
        
        directive = {}
        body = {
            'instances': instance_ids,
            "base64_message": base64_message,
        }
        directive["body"] = body
        action = qconst.ACTION_SEND_VDI_GUEST_MESSAGE
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return instance_ids
    
    def resource_send_desktop_hot_keys(self, instance_ids, keys, timeout, time_step):
        
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
        directive = {}
        body = {
            'instances': instance_ids,
            "keys": keys,
            "timeout": timeout,
            "time_step": time_step
        }
        directive["body"] = body
        action = qconst.ACTION_SEND_VDI_GUEST_KEYS
        ret = self.handle_resource(action, directive, return_all=True)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        job_id = ret.get("job_id")
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return instance_ids
    
    # snapshot
    def resource_describe_snapshots(self, snapshot_ids):
        
        snapshots = {}
        if not snapshot_ids:
            return snapshots
        if not isinstance(snapshot_ids, list):
            snapshot_ids = [snapshot_ids]
        
        action = qconst.ACTION_DESCRIBE_SNAPSHOTS
        for i in xrange(0, len(snapshot_ids), const.MAX_LIMIT_PARAM):
            end = i + const.MAX_LIMIT_PARAM
            if end > len(snapshot_ids):
                end = len(snapshot_ids)

            snap_ids = snapshot_ids[i:end]
            directive = {}
            body = {"snapshots": snap_ids, "limit": const.MAX_LIMIT_PARAM, "offset": 0}
            directive["body"] = body

            ret = self.handle_resource(action, directive)
            if ret is None:
                return None
            (snapshot_set, _) = ret
            for snapshot in snapshot_set:
                snapshot_id = snapshot["snapshot_id"]
                if snapshot_id in snapshots:
                    continue
                snapshots[snapshot_id] = snapshot

        return snapshots

    def resource_create_snapshots(self, resource_ids, snapshot_name, is_full=0):

        directive = {}
        if not isinstance(resource_ids, list):
            resource_ids = [resource_ids]
        
        body = {
            "resources": resource_ids,
            "snapshot_name": snapshot_name,
            "is_full": is_full
        }
        directive["body"] = body
        search = {"search_word": snapshot_name}
        directive["search"] = search
        
        action = qconst.ACTION_CREATE_SNAPSHOTS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (snapshot_ids, job_id) = ret
        if not snapshot_ids or not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
    
        return (snapshot_ids, job_id)


    def resource_delete_snapshots(self, snapshot_ids):

        directive = {}
        if not isinstance(snapshot_ids, list):
            snapshot_ids = [snapshot_ids]

        body = {
            "snapshots": snapshot_ids
        }
        directive["body"] = body
        search = {"resource_ids": snapshot_ids}
        directive["search"] = search

        action = qconst.ACTION_DELETE_SNAPSHOTS
        ret = self.handle_resource(action, directive)
        if not ret:
            action = qconst.ACTION_DESCRIBE_SNAPSHOTS
            directive = {}
            body = {"snapshots": snapshot_ids}
            directive["body"] = body
            ret = self.handle_resource(action, directive)
            if ret is None:
                return None
            (snapshot_set, _) = ret
            for snapshot in snapshot_set:
                snapshot_id = snapshot["snapshot_id"]
                status = snapshot["status"]
                if status in [const.INST_STATUS_CEASED, const.SNAPSHOT_STATUS_DELETED]:
                    logger.info(" resource [%s] has already been deleted" % (snapshot_id))
                    return snapshot_id
                else:
                    logger.error("handle resource action :DeleteSnapshots fail  %s" % (snapshot_id))
                    return None

        (_, job_id) = ret

        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return snapshot_ids
    
    def resource_modify_snapshot_attributes(self, snapshot_id, snapshot_name=None, description=None):

        directive = {}
        
        body = {'snapshot': snapshot_id}
        if snapshot_name is not None:
            body["snapshot_name"] = snapshot_name
            
        if description is not None:
            body["description"] = description
        
        if not body:
            return None

        directive["body"] = body
        action = qconst.ACTION_MODIFY_SNAPSHOT_ATTRIBUTES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return snapshot_id

    def resource_apply_snapshots(self, snapshot_ids):

        directive = {}
        if not isinstance(snapshot_ids, list):
            snapshot_ids = [snapshot_ids]
        
        directive["body"] = {"snapshots": snapshot_ids}
        action = qconst.ACTION_APPLY_SNAPSHOTS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        if not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return snapshot_ids

    def resource_capture_instance_from_snapshot(self, snapshot_id, image_name):

        directive = {}
        
        directive["body"] = {"snapshot": snapshot_id, "image_name": image_name}
        search = {"search_workd": image_name}
        directive["search"] = search
        action = qconst.ACTION_CAPTURE_INSTANCE_FROM_SNAPSHOT
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        (image_ids, job_id) = ret
        
        if not image_ids or not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return image_ids[0]

    def resource_create_volume_from_snapshot(self, snapshot_id, volume_name):

        directive = {}
        directive["body"] = {"snapshot": snapshot_id, "volume_name": volume_name}
        search = {"search_workd": volume_name}
        directive["search"] = search
        action = qconst.ACTION_CREATE_VOLUME_FROM_SNAPSHOT
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (volume_ids, job_id) = ret
        if not volume_ids or not job_id:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None
        
        ret = self.job.wait_job_done(job_id, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s" % (action, ret))
            return None

        return volume_ids[0]

    def resource_describe_zones(self, zone_ids=None, status=None, region=None, retries=qconst.RES_ACTION_RETRIES):

        zones = {}

        if zone_ids and not isinstance(zone_ids, list):
            zone_ids = [zone_ids]
        
        if status and not isinstance(status, list):
            status = [status]
        
        action = qconst.ACTION_DESCRIBE_ZONES
        directive = {}
        body = {"limit": const.MAX_LIMIT_PARAM, "offset": 0}
        if zone_ids:
            body["zones"] = zone_ids
        
        if status:
            body["status"] = status
        
        if region:
            body["region"] = region
        
        directive["body"] = body

        ret = self.handle_resource(action, directive, retries=retries)
        if ret is None:
            return None
    
        (zone_set, _) = ret
        for zone in zone_set:
            zone_id = zone["zone_id"]
            zones[zone_id] = zone

        return zones

    def resource_describe_access_keys(self, zone_ids=None, access_keys=None):

        access_key_sets = {}
        if zone_ids and not isinstance(zone_ids, list):
            zone_ids = [zone_ids]

        if access_keys and not isinstance(access_keys, list):
            access_keys = [access_keys]

        action = qconst.ACTION_DESCRIBE_ACCESS_KEYS
        directive = {}
        body = {"limit": const.MAX_LIMIT_PARAM, "offset": 0}
        if zone_ids:
            body["zones"] = zone_ids

        if access_keys:
            body["access_keys"] = access_keys

        directive["body"] = body
        ret = self.handle_resource(action, directive)
        if ret is None:
            return None

        (access_key_set, _) = ret
        for access_key in access_key_set:
            access_key_id = access_key["access_key_id"]
            access_key_sets[access_key_id] = access_key

        return access_key_sets

    def resource_describe_users(self, zone_ids=None, users=None):

        user_sets = {}
        if zone_ids and not isinstance(zone_ids, list):
            zone_ids = [zone_ids]

        if users and not isinstance(users, list):
            users = [users]

        action = qconst.ACTION_DESCRIBE_USERS
        directive = {}
        body = {"limit": const.MAX_LIMIT_PARAM, "offset": 0}
        if zone_ids:
            body["zones"] = zone_ids

        if users:
            body["users"] = users

        directive["body"] = body
        ret = self.handle_resource(action, directive)
        if ret is None:
            return None

        (user_set, _) = ret
        for user in user_set:
            user_id = user["user_id"]
            user_sets[user_id] = user

        return user_sets

    def resource_describe_keypairs(self, zone_ids, owner, keypair_name):
    
        keypair_sets = {}
        if zone_ids and not isinstance(zone_ids, list):
            zone_ids = [zone_ids]

        action = qconst.ACTION_DESCRIBE_SSH_KEY_PAIRS
        directive = {}
        body = {"limit": const.MAX_LIMIT_PARAM, "offset": 0}
        if zone_ids:
            body["zones"] = zone_ids
        if owner:
            body["owner"] = owner
        if keypair_name:
            body["keypair_name"] = keypair_name

        directive["body"] = body
        ret = self.handle_resource(action, directive)
        if ret is None:
            return None

        (keypair_set, _) = ret
        for keypair in keypair_set:
            keypair_id = keypair["keypair_id"]
            keypair_sets[keypair_id] = keypair

        return keypair_sets

    def resource_create_keypair(self, zone_ids, owner, keypair_name):
        
        if zone_ids and not isinstance(zone_ids, list):
            zone_ids = [zone_ids]

        action = qconst.ACTION_CREATE_SSH_KEY_PAIR
        directive = {}
        body = {"limit": const.MAX_LIMIT_PARAM, "offset": 0}
        if zone_ids:
            body["zones"] = zone_ids
        if owner:
            body["owner"] = owner
        if keypair_name:
            body["keypair_name"] = keypair_name

        directive["body"] = body
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("action handle no return resource %s, %s " % (action, directive))
            return None

        (keypair_id,_) = ret
        return keypair_id

    def resource_get_resource_limit(self, zone):
        
        action = qconst.ACTION_GET_RESOURCE_LIMIT
        directive = {}
        body = {"zone": zone}
        
        directive["body"] = body
        ret = self.handle_resource(action, directive, return_all=True)
        if ret is None:
            return None
        
        return ret["resource_limits"]

    def resource_describe_place_groups(self, place_group_ids=None, status=None):
        
        action = qconst.ACTION_DESCRIBE_PLACE_GROUPS
        directive = {}
        body = {}
        place_groups = {}
        if place_group_ids:
            if not isinstance(place_group_ids, list):
                place_group_ids = [place_group_ids]
            
            body["place_groups"] = place_group_ids
        
        if status:
            if not isinstance(status, list):
                status = [status]
    
            body["status"] = status
        
        directive["body"] = body
        ret = self.handle_resource(action, directive)
        if ret is None:
            return None
        
        (place_group_set, _) = ret
        for place_group in place_group_set:
            place_group_id = place_group["place_group_id"]
            place_groups[place_group_id] = place_group
        
        return place_groups

    # security
    def resource_describe_security_groups(self, user_id, security_group_ids=None, group_type=None, is_default=None):
        
        security_groups = {}
        
        if security_group_ids:
            if not isinstance(security_group_ids, list):
                security_group_ids = [security_group_ids]

            action = qconst.ACTION_DESCRIBE_SECURITY_GROUPS
            for i in xrange(0, len(security_group_ids), const.MAX_LIMIT_PARAM):
                end = i + const.MAX_LIMIT_PARAM
                if end > len(security_group_ids):
                    end = len(security_group_ids)
            
                sec_ids = security_group_ids[i:end]
                directive = {}
                body = {"security_groups": sec_ids, "limit": const.MAX_LIMIT_PARAM, "offset": 0, "verbose": 1}
                if group_type:
                    body["group_type"] = group_type
                directive["body"] = body
                ret = self.handle_resource(action, directive)
                if ret is None:
                    return None
            
                (security_group_set, _) = ret
                for security_group in security_group_set:
                    security_group_id = security_group["security_group_id"]   
                    security_groups[security_group_id] = security_group
        else:
        
            action = qconst.ACTION_DESCRIBE_SECURITY_GROUPS
            offset = 0
            limit = const.MAX_LIMIT_PARAM
            while True:
                directive = {}
                body = {"offset":offset, "limit":limit}

                if group_type:
                    body["group_type"] = group_type

                if is_default is not None:
                    body["default"] = 1

                body["owner"] = user_id
                body["verbose"] = 1
                directive["body"] = body
                ret = self.handle_resource(action, directive, return_all=True)
                if ret is None:
                    logger.error("handle ipset resource fail %s" % body)
                    return None

                security_group_set = ret["security_group_set"]
                for security_group in security_group_set:
                    security_group_id = security_group["security_group_id"]
                    security_groups[security_group_id] = security_group

                total_count = ret["total_count"]
                if total_count <= offset:
                    return security_groups
                offset = offset + limit

        return security_groups
    
    def resource_create_security_group(self, security_group_name, group_type=None):

        directive = {}
        body = {"security_group_name": security_group_name}
        
        if group_type == const.SEC_POLICY_TYPE_SGRS:
            body["group_type"] = group_type
        
        directive["body"] = body
        action = qconst.ACTION_CREATE_SECURITY_GROUP
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        (security_group_id, _) = ret
        return security_group_id

    def resource_modify_security_group_attributes(self, security_group_id, security_group_name=None, description=None):

        directive = {}
        body = {"security_group": security_group_id}

        if security_group_name is not None:
            body["security_group_name"] = security_group_name
        
        if description is not None:
            body["description"] = description
        
        directive["body"] = body
        action = qconst.ACTION_MODIFY_SECURITY_GROUP_ATTRIBUTES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return security_group_id

    def resource_delete_security_groups(self, security_group_ids):
        
        directive = {}
        
        if not isinstance(security_group_ids, list):
            security_group_ids = [security_group_ids]
        
        body = {"security_groups": security_group_ids}
        directive["body"] = body
        action = qconst.ACTION_DELETE_SECURITY_GROUPS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        return security_group_ids

    def resource_remove_security_group(self, instance_ids):

        directive = {}
        
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
        
        body = {"instances": instance_ids}
        directive["body"] = body
        action = qconst.ACTION_REMOVE_SECURITY_GROUP
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        ret = self.job.wait_job_done(job_id, timeout = qconst.WAIT_JOB_TIMEOUT_600, interval=qconst.JOB_INTERVAL_3S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s, %s" % (action, ret, job_id))
            return None

        return instance_ids

    def resource_rollback_security_group(self, security_group_id, security_group_snapshot_id):
        directive = {}

        body = {"security_group": security_group_id, "security_group_snapshot": security_group_snapshot_id}
        directive["body"] = body
        action = qconst.ACTION_ROLLBACK_SECURITY_GROUP
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        return security_group_id

    def resource_apply_security_group(self, security_group_id, instance_ids=None):

        directive = {}
        body = {"security_group": security_group_id}
        if instance_ids:
            body["instances"] = instance_ids

        directive["body"] = body
        action = qconst.ACTION_APPLY_SECURITY_GROUP
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        (_, job_id) = ret
        ret = self.job.wait_job_done(job_id, timeout = qconst.WAIT_JOB_TIMEOUT_3600, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s, %s" % (action, ret, job_id))
            return None

        return security_group_id
    
    def resource_describe_security_group_rules(self, user_id, security_group_id=None, security_group_rule_ids=None,  direction=None ):
        
        security_group_rules = {}
        action = qconst.ACTION_DESCRIBE_SECURITY_GROUP_RULES
        
        if security_group_rule_ids and not isinstance(security_group_rule_ids, list):
            security_group_rule_ids = [security_group_rule_ids]

        if security_group_rule_ids:
            for i in xrange(0, len(security_group_rule_ids), const.MAX_LIMIT_PARAM):
                end = i + const.MAX_LIMIT_PARAM
                if end > len(security_group_rule_ids):
                    end = len(security_group_rule_ids)
            
                rule_ids = security_group_rule_ids[i:end]
                directive = {}
                body = {"security_group_rules": rule_ids, "limit": const.MAX_LIMIT_PARAM, "offset": 0}
                if security_group_id:
                    body["security_group"] = security_group_id
                if direction is not None:
                    body["direction"] = direction
    
                directive["body"] = body
                ret = self.handle_resource(action, directive)
                if ret is None:
                    return None
            
                (security_group_rule_set, _) = ret
                for security_group_rule in security_group_rule_set:
                    security_group_rule_id = security_group_rule["security_group_rule_id"]
                    security_group_rules[security_group_rule_id] = security_group_rule

        elif security_group_id:
    
            offset = 0
            limit = const.MAX_LIMIT_PARAM
            while True:
                directive = {}
                body = {"security_group": security_group_id, "offset":offset, "limit":limit}
                body["owner"] = user_id
                directive["body"] = body
                ret = self.handle_resource(action, directive, return_all=True)
                if ret is None:
                    logger.error("handle nic resource fail %s" % body)
                    return None

                security_group_rule_set = ret["security_group_rule_set"]
                for security_group_rule in security_group_rule_set:
                    security_group_rule_id = security_group_rule["security_group_rule_id"]
                    security_group_rules[security_group_rule_id] = security_group_rule

                total_count = ret["total_count"]
                if total_count <= offset:
                    return security_group_rules
                offset = offset + limit

        return security_group_rules
    
    def resource_add_security_group_rules(self, security_group_id, rules):
        
        if not isinstance(rules, list):
            rules = [rules]
        
        directive = {}
        body = {"security_group": security_group_id, "rules": rules}
        for rule in rules:
            if "security_rule_name" in rule:
                rule["security_group_rule_name"] = rule["security_rule_name"]
                del rule["security_rule_name"]
        
        directive["body"] = body
        action = qconst.ACTION_ADD_SECURITY_GROUP_RULES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        security_group_rule_ids, _ = ret
        
        return security_group_rule_ids
    
    def resource_delete_security_group_rules(self, security_group_rule_ids):
        
        directive = {}
        
        if not isinstance(security_group_rule_ids, list):
            security_group_rule_ids = [security_group_rule_ids]
        
        body = {"security_group_rules": security_group_rule_ids}
        directive["body"] = body
        action = qconst.ACTION_DELETE_SECURITY_GROUP_RULES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        return security_group_rule_ids
    
    def resource_modify_security_group_rule_attributes(self, security_group_rule_id, config):
        
        directive = {}
        body = {"security_group_rule": security_group_rule_id}
        
        if "security_rule_name" in config:
            security_rule_name = config["security_rule_name"]
            del config["security_rule_name"]
            config["security_group_rule_name"] = security_rule_name
        
        body.update(config)
        
        directive["body"] = body
        action = qconst.ACTION_MODIFY_SECURITY_GROUP_RULE_ATTRIBUTES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
    
        return security_group_rule_id
    
    def resource_describe_security_group_ipsets(self, user_id, security_group_ipset_ids=None, ipset_type=None, req=None):

        security_group_ipsets = {}
        
        if security_group_ipset_ids:

            if not isinstance(security_group_ipset_ids, list):
                security_group_ipset_ids = [security_group_ipset_ids]
            
            action = qconst.ACTION_DESCRIBE_SECURITY_GROUP_IPSETS
            for i in xrange(0, len(security_group_ipset_ids), const.MAX_LIMIT_PARAM):
                end = i + const.MAX_LIMIT_PARAM
                if end > len(security_group_ipset_ids):
                    end = len(security_group_ipset_ids)
            
                ipset_ids = security_group_ipset_ids[i:end]
                directive = {}
                body = {"security_group_ipsets": ipset_ids, "limit": const.MAX_LIMIT_PARAM, "offset": 0}
                if ipset_type:
                    body["ipset_type"] = ipset_type
    
                directive["body"] = body
                ret = self.handle_resource(action, directive)
                if ret is None:
                    return None
            
                (security_group_ipset_set, _) = ret
                for security_group_ipset in security_group_ipset_set:
                    security_group_ipset_id = security_group_ipset["security_group_ipset_id"]
                    security_group_ipsets[security_group_ipset_id] = security_group_ipset
        else:
            action = qconst.ACTION_DESCRIBE_SECURITY_GROUP_IPSETS
            offset = 0
            limit = const.MAX_LIMIT_PARAM
            while True:
                directive = {}
                body = {"offset":offset, "limit":limit}
                body["owner"] = user_id
                directive["body"] = body
                ret = self.handle_resource(action, directive, return_all=True)
                if ret is None:
                    logger.error("handle ipset resource fail %s" % body)
                    return None

                ipset_set = ret["security_group_ipset_set"]
                for ipset in ipset_set:
                    security_group_ipset_id = ipset["security_group_ipset_id"]
                    security_group_ipsets[security_group_ipset_id] = ipset

                total_count = ret["total_count"]
                if total_count <= offset:
                    return security_group_ipsets
                offset = offset + limit

        return security_group_ipsets
    
    def resource_create_security_group_ipset(self, ipset_type, val, security_group_ipset_name=None):
        
        directive = {}
        body = {"ipset_type": ipset_type, "val": val}
        if security_group_ipset_name:
            body["security_group_ipset_name"] = security_group_ipset_name

        directive["body"] = body
        action = qconst.ACTION_CREATE_SECURITY_GROUP_IPSET
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        (security_group_ipset_id, _) = ret
        return security_group_ipset_id
    
    def resource_delete_security_group_ipsets(self, security_group_ipset_ids):
        
        directive = {}
        
        if not isinstance(security_group_ipset_ids, list):
            security_group_ipset_ids = [security_group_ipset_ids]
        
        body = {"security_group_ipsets": security_group_ipset_ids}
        directive["body"] = body
        action = qconst.ACTION_DELETE_SECURITY_GROUP_IPSETS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        return security_group_ipset_ids
    
    def resource_modify_security_group_ipset_attributes(self, security_group_ipset_id, security_group_ipset_name, description, val):
        
        directive = {}
        body = {"security_group_ipset": security_group_ipset_id}
        if security_group_ipset_name:
            body["security_group_ipset_name"] = security_group_ipset_name
        
        if description:
            body["description"] = description
        
        if val:
            body["val"] = val
        
        directive["body"] = body
        action = qconst.ACTION_MODIFY_SECURITY_GROUP_IPSET_ATTRIBUTES
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
    
        return security_group_ipset_id

    def resource_apply_security_ipset(self, security_group_ipset_id):

        directive = {}
        
        if not isinstance(security_group_ipset_id, list):
            security_group_ipset_id = [security_group_ipset_id]
        
        body = {"security_group_ipsets": security_group_ipset_id}

        directive["body"] = body
        action = qconst.ACTION_APPLY_SECURITY_GROUP_IPSETS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        (_, job_id) = ret
        ret = self.job.wait_job_done(job_id, timeout = qconst.WAIT_JOB_TIMEOUT_3600, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s, %s" % (action, ret, job_id))
            return None

        return security_group_ipset_id

    def resource_describe_security_group_and_ruleset(self, security_group_id):

        security_group_rulesets = {}
        directive = {}
        body = {"security_group": security_group_id}

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_SECURITY_GROUP_AND_RULESET
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None
        
        security_group_ruleset,_ = ret
        
        for ruleset in security_group_ruleset:
            ruleset_id = ruleset["group_id"]
            security_group_rulesets[ruleset_id] = ruleset
            
        return security_group_rulesets

    def resource_add_security_group_rulesets(self, security_group_id, security_group_ruleset_ids):

        directive = {}
        body = {"security_group": security_group_id, "security_group_rulesets": security_group_ruleset_ids}

        directive["body"] = body
        action = qconst.ACTION_ADD_SECURITY_GROUP_RULESETS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return security_group_id

    def resource_remove_security_group_rulesets(self, security_group_id, security_group_ruleset_ids):

        directive = {}
        body = {"security_group": security_group_id, "security_group_rulesets": security_group_ruleset_ids}

        directive["body"] = body
        action = qconst.ACTION_REMOVE_SECURITY_GROUP_RULESETS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return security_group_id

    def resource_apply_security_group_ruleset(self, security_group_ruleset_id):

        directive = {}
        body = {"security_group_ruleset": security_group_ruleset_id}

        directive["body"] = body
        action = qconst.ACTION_APPLY_SECURITY_GROUP_RULESET
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return security_group_ruleset_id

    def resource_create_security_group_snapshot(self, security_group_id, name):
    
        directive = {}
        body = {"security_group": security_group_id, "name": name}

        directive["body"] = body
        action = qconst.ACTION_CREATE_SECURITY_GROUP_SNAPSHOT
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return security_group_id

    def resource_delete_security_group_snapshots(self, security_group_snapshot_ids):

        directive = {}
        body = {"security_group_snapshots": security_group_snapshot_ids}

        directive["body"] = body
        action = qconst.ACTION_DELETE_SECURITY_GROUP_SNAPSHOTS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return security_group_snapshot_ids

    def resource_describe_rdbs(self, service_id):

        rdb_sets = {}
        directive = {}
        body = {"rdbs": [service_id],"verbose":1}

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_RDBS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        rdb_set, _ = ret
        for rdbset in rdb_set:
            rdb_id = rdbset["rdb_id"]
            rdb_sets[rdb_id] = rdbset

        return rdb_sets

    def resource_describe_clusters(self, service_id):

        cluster_sets = {}
        directive = {}
        body = {"clusters": [service_id],"verbose":1}

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_CLUSTERS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        cluster_set, _ = ret
        for clusterset in cluster_set:
            cluster_id = clusterset["cluster_id"]
            cluster_sets[cluster_id] = clusterset

        return cluster_sets

    def resource_describe_caches(self, service_id):

        cache_sets = {}
        directive = {}
        body = {"caches": [service_id]}

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_CACHES

        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        cache_set, _ = ret
        for cacheset in cache_set:
            cache_id = cacheset["cache_id"]
            cache_sets[cache_id] = cacheset

        return cache_sets

    def resource_describe_loadbalancers(self, service_id):

        loadbalancer_sets = {}
        directive = {}

        body = {"loadbalancers": [service_id],"verbose":2}
        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_LOADBALANCERS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        loadbalancer_set, _ = ret
        for loadbalancerset in loadbalancer_set:
            loadbalancer_id = loadbalancerset["loadbalancer_id"]
            loadbalancer_sets[loadbalancer_id] = loadbalancerset

        return loadbalancer_sets

    def resource_describe_loadbalancer_backends(self, service_id):

        loadbalancer_backend_sets = {}
        directive = {}

        body = {"loadbalancer_listener": service_id,"offset":0,"limit":const.MAX_LIMIT_PARAM}
        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_LOADBALANCER_BACKENDS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        loadbalancer_backend_set, _ = ret
        for loadbalancer_backendset in loadbalancer_backend_set:
            loadbalancer_backend_id = loadbalancer_backendset["loadbalancer_backend_id"]
            loadbalancer_backend_sets[loadbalancer_backend_id] = loadbalancer_backendset

        return loadbalancer_backend_sets

    def resource_describe_nics_with_private_ip(self, private_ip):

        nic_sets = {}
        directive = {}
        body = {
                "status":["in-use","available"],
                "search_word":private_ip
                }

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_NICS

        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        nic_set, _ = ret
        for nicset in nic_set:
            nic_id = nicset["nic_id"]
            nic_sets[nic_id] = nicset

        return nic_sets

    def resource_describe_instances_by_search_word(self,user_id,req=None):

        instances = {}
        if req is not None:
            # req["owner"] = user_id
            directive = dict(body=req)
            action = qconst.ACTION_DESCRIBE_INSTANCES
            ret = self.handle_resource(action, directive)
            if ret is None:
                return None

            (instance_set, _) = ret
            for instance in instance_set:
                instance_id = instance["instance_id"]
                if instance_id in instances:
                    continue
                instances[instance_id] = instance

        return instances

    def resource_describe_s2servers(self, user_id,service_id):

        s2_server_sets = {}
        directive = {}
        body = {"owner":user_id,"verbose":1,"s2_servers": [service_id]}

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_S2SERVERS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        s2_server_set, _ = ret
        for s2_serverset in s2_server_set:
            s2_server_id = s2_serverset["s2_server_id"]
            s2_server_sets[s2_server_id] = s2_serverset

        return s2_server_sets

    def resource_modify_cluster_attributes(self, user_id, service_type, service_id, service_name,description=None):

        directive = {}
        action = qconst.ACTION_MODIFY_CLUSTER_ATTRIBUTES
        config = dict(
            cluster=service_id,
            name=service_name,
            description=description if description else '',
            owner=user_id
        )
        directive["body"] = config
        action = action

        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return service_id

    def resource_modify_cache_attributes(self, user_id, service_type, service_id, service_name,description=None):

        directive = {}
        action = qconst.ACTION_MODIFY_CACHE_ATTRIBUTES
        config = dict(
            cache=service_id,
            cache_name=service_name,
            description=description if description else '',
            owner=user_id
        )
        directive["body"] = config
        action = action

        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return service_id

    def resource_modify_rdb_attributes(self, user_id, service_type, service_id, service_name,description=None):

        directive = {}
        action = qconst.ACTION_MODIFY_RDB_ATTRIBUTES
        config = dict(
            rdb=service_id,
            rdb_name=service_name,
            description=description if description else '',
            owner=user_id
        )
        directive["body"] = config
        action = action

        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return service_id

    def resource_modify_s2server_attributes(self, user_id, service_type, service_id, service_name,description=None):

        directive = {}
        action = qconst.ACTION_MODIFY_S2SERVER_ATTRIBUTES
        config = dict(
            s2_server=service_id,
            s2_server_name=service_name,
            description=description if description else '',
            owner=user_id
        )
        directive["body"] = config
        action = action

        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return service_id

    def resource_modify_loadbalancer_attributes(self, user_id, service_type, service_id, service_name,description=None):

        directive = {}
        action = qconst.ACTION_MODIFY_LOADBALANCER_ATTRIBUTES
        config = dict(
            loadbalancer=service_id,
            loadbalancer_name=service_name,
            description=description if description else '',
            owner=user_id
        )
        directive["body"] = config
        action = action

        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return service_id

    def resource_describe_s2_accounts(self, user_id,search_word):

        s2_account_sets = {}
        directive = {}
        body = {"owner":user_id,"offset":0,"limit":100,"verbose":1,"search_word": search_word}

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_S2_ACCOUNTS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        s2_account_set, _ = ret
        for s2_account in s2_account_set:
            account_id = s2_account["account_id"]
            s2_account_sets[account_id] = s2_account

        return s2_account_sets

    def resource_describe_s2_groups(self, user_id,group_types):

        s2_group_sets = {}
        directive = {}
        body = {"owner":user_id,"offset":0,"limit":100,"verbose":1,"group_types": group_types}

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_S2_GROUPS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        s2_group_set, _ = ret
        for s2_group in s2_group_set:
            s2_group_id = s2_group["group_id"]
            s2_group_sets[s2_group_id] = s2_group

        return s2_group_sets

    def resource_create_s2_account(self, user_id,account_name,account_type,nfs_ipaddr,s2_group,opt_parameters,s2_groups):

        directive = {}
        body = {"owner":user_id,
                "account_name":account_name,
                "account_type":account_type,
                "nfs_ipaddr":nfs_ipaddr,
                "s2_group": s2_group,
                "opt_parameters": opt_parameters,
                "s2_groups": s2_groups
                }

        directive["body"] = body
        action = qconst.ACTION_CREATE_S2_ACCOUNT
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (s2_account_id,_) = ret
        return s2_account_id

    def resource_update_s2_servers(self, user_id,s2_servers):

        directive = {}

        if not isinstance(s2_servers, list):
            s2_servers = [s2_servers]

        body = {"owner":user_id,"s2_servers": s2_servers}

        directive["body"] = body
        action = qconst.ACTION_UPDATE_S2_SERVERS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        ret = self.job.wait_job_done(job_id, timeout=qconst.WAIT_JOB_TIMEOUT_3600, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s, %s" % (action, ret, job_id))
            return None

        return s2_servers

    def resource_poweroff_s2_servers(self, user_id, s2_servers):

        directive = {}

        if not isinstance(s2_servers, list):
            s2_servers = [s2_servers]

        body = {"owner": user_id, "s2_servers": s2_servers}

        directive["body"] = body
        action = qconst.ACTION_POWEROFF_S2_SERVERS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        ret = self.job.wait_job_done(job_id, timeout=qconst.WAIT_JOB_TIMEOUT_3600, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s, %s" % (action, ret, job_id))
            return None

        return s2_servers

    def resource_poweron_s2_servers(self, user_id, s2_servers):

        directive = {}

        if not isinstance(s2_servers, list):
            s2_servers = [s2_servers]

        body = {"owner": user_id, "s2_servers": s2_servers}

        directive["body"] = body
        action = qconst.ACTION_POWERON_S2_SERVERS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (_, job_id) = ret
        ret = self.job.wait_job_done(job_id, timeout=qconst.WAIT_JOB_TIMEOUT_3600, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s, %s" % (action, ret, job_id))
            return None

        return s2_servers

    def resource_describe_tags(self, user_id,search_word):

        tag_sets = {}
        directive = {}
        body = {"owner":user_id,"offset":0,"limit":100,"verbose":1,"search_word": search_word}

        directive["body"] = body
        action = qconst.ACTION_DESCRIBE_TAGS
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        tag_set, _ = ret
        for tag in tag_set:
            tag_id = tag["tag_id"]
            tag_sets[tag_id] = tag

        return tag_sets

    def resource_create_tag(self, user_id,color,tag_name):

        directive = {}
        body = {"owner":user_id,"tag_name": tag_name,"color":color}

        directive["body"] = body
        action = qconst.ACTION_CREATE_TAG
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (tag_id,_) = ret

        return tag_id

    def resource_attach_tags(self, user_id,resource_tag_pairs,selectedData):

        directive = {}
        body = {"owner":user_id,"resource_tag_pairs": resource_tag_pairs,"selectedData":selectedData}

        directive["body"] = body
        action = qconst.ACTION_ATTACH_TAGS
        ret = self.handle_resource(action, directive, return_all=True)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        return ret

    def resource_create_s2_server(self,user_id,vxnet_id,s2_server_name,s2_class):

        directive = {}

        body = {"owner":user_id,
                "vxnet": vxnet_id,
                "service_type":'vnas',
                "s2_server_name":s2_server_name,
                "s2_server_type":0,
                "description":'this is file_share_vnas',
                "s2_class":s2_class}

        directive["body"] = body
        action = qconst.ACTION_CREATE_S2_SERVER
        logger.info("action == %s directive == %s" %(action,directive))
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (s2_server, job_id) = ret
        ret = self.job.wait_job_done(job_id, timeout=qconst.WAIT_JOB_TIMEOUT_3600, interval=qconst.JOB_INTERVAL_5S)
        if ret < 0:
            logger.error("action %s job fail or timeout: %s, %s" % (action, ret, job_id))
            return None

        return s2_server

    def resource_create_s2_shared_target(self,user_id,vxnet,s2_server_id,target_type,export_name_nfs,export_name,volumes):

        directive = {}

        body = {"owner":user_id,
                "vxnet": vxnet,
                "s2_server_id":s2_server_id,
                "target_type":target_type,
                "export_name_nfs":export_name_nfs,
                "export_name":export_name,
                "volumes":volumes}

        directive["body"] = body
        action = qconst.ACTION_CREATE_S2_SHARED_TARGET
        logger.info("action == %s directive == %s" %(action,directive))
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        (s2_shared_target,_) = ret

        return s2_shared_target

    def resource_get_quota_left(self, user_id,resource_type):

        directive = {}
        body = {"owner":user_id,"resource_types": [resource_type]}

        directive["body"] = body
        action = qconst.ACTION_GET_QUOTA_LEFT
        ret = self.handle_resource(action, directive)
        if not ret:
            logger.error("handle resource action :%s fail  %s" % (action, directive))
            return None

        quota_left_set, _ = ret

        return quota_left_set

