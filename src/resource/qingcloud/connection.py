
import random
import sys
import time
import uuid
from .auth import QuerySignatureAuthHandler
from base_connection import HttpConnection, HTTPRequest
from utils.json import json_load, json_dump
from utils.misc import filter_out_none
from qingcloud import const as const
from consolidator import RequestChecker
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error

from copy import deepcopy
from utils.misc import local_ts
import ssl
ssl._create_default_https_context=ssl._create_unverified_context

NA = 'NA'
STEPS = {
    '5m': 300,
    '15m': 900,
    '30m': 1800,
    '1h': 3600,
    '2h': 7200,
    '1d': 24 * 3600,
}

class QingCloudConnection(HttpConnection):

    """ Public connection to qingcloud service
    """
    req_checker = RequestChecker()

    def __init__(self, zone, conn, pool=None, expires=None,
                 retry_time=3, http_socket_timeout=60, debug=False, owner=None):
        """
        @param qy_access_key_id - the access key id
        @param qy_secret_access_key - the secret access key
        @param zone - the zone id to access
        @param host - the host to make the connection to
        @param port - the port to use when connect to host
        @param protocol - the protocol to access to web server, "http" or "https"
        @param pool - the connection pool
        @param retry_time - the retry_time when message send fail
        """
        if not conn:
            logger.error("qingcloud api connection config error.")
            return None

        qy_access_key_id = conn.get("qy_access_key_id")
        if not qy_access_key_id:
            qy_access_key_id = conn.get("access_key_id")

        qy_secret_access_key = conn.get("qy_secret_access_key")
        if not qy_secret_access_key:
            qy_secret_access_key = conn.get("secret_access_key")
        
        host = conn["host"]
        port = conn["port"]
        protocol = conn["protocol"]
        
        self.owner = owner
        # Set default zone
        self.zone = zone
        # Set retry times
        self.retry_time = retry_time

        super(QingCloudConnection, self).__init__(
            qy_access_key_id, qy_secret_access_key, host, port, protocol,
            pool, expires, http_socket_timeout, debug)

        self._auth_handler = QuerySignatureAuthHandler(self.host,
                                                       self.qy_access_key_id, self.qy_secret_access_key)

    def send_request(self, action, body, url="/iaas/", verb="GET"):
        """ Send request
        """

        request = body
        request['action'] = action
        request.setdefault('zone', self.zone)
        if self.debug:
            print(json_dump(request))
            sys.stdout.flush()

        if self.expires:
            request['expires'] = self.expires

        retry_time = 0
        while retry_time < self.retry_time:
            # Use binary exponential backoff to desynchronize client requests
            next_sleep = random.random() * (2 ** retry_time)
            try:
                response = self.send(verb, url, request)
                if response.status == 200:
                    resp_str = response.read()
                    if type(resp_str) != str:
                        resp_str = resp_str.decode()

                    if self.debug:
                        print(resp_str)
                        sys.stdout.flush()
                    
                    result = json_load(resp_str) if resp_str else None
                    if not result:
                        logger.error("send request failure: %s, %s" % (action, body))
                    return result
            except Exception, e:
                logger.error("send request exception : %s, %s, %s" % (e, action, body))
                if retry_time < self.retry_time - 1:
                    self._get_conn(self.host, self.port)
                else:
                    return None

            time.sleep(next_sleep)
            retry_time += 1

    def _gen_req_id(self):
        return uuid.uuid4().hex

    def build_http_request(self, verb, url, base_params, auth_path=None,
                           headers=None, host=None, data=""):
        params = {}
        for key, values in base_params.items():
            if values is None:
                continue
            if isinstance(values, list):
                for i in range(1, len(values) + 1):
                    if isinstance(values[i - 1], dict):
                        for sk, sv in values[i - 1].items():
                            if isinstance(sv, dict) or isinstance(sv, list):
                                sv = json_dump(sv)
                            params['%s.%d.%s' % (key, i, sk)] = sv
                    else:
                        params['%s.%d' % (key, i)] = values[i - 1]
            else:
                params[key] = values
        
        _host = host if host else self.host
        return HTTPRequest(verb, self.protocol, headers, _host, self.port,
                           url, params, auth_path, data)

    def return_param_invaild(self, action, param):
        logger.error("param error : %s, %s" % (action, param))
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, (action, param))

    # error
    def check_res_error(self, ret, body):

        if not ret:
            logger.error("API Response is None: %s " % (body))
            return True

        if ret["ret_code"] != 0:
            logger.error("%s, %s" % (ret, body))
            return True

        return False

    def describe_gpus(self, param):
        """ Describe gpus.
        @param jobs: the IDs of job you want to describe.
        @param status: valid values include pending, working, failed, successful.
        @param job_action: the action of job you want to describe.
        @param resource_ids: the handle_resource id of job you want to describe
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        """
        action = const.ACTION_DESCRIBE_GPUS
        valid_keys = ["status", 'offset', 'limit']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=["offset", "limit"],
                                             list_params=["jobs"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_jobs(self, param):
        """ Describe jobs.
        @param jobs: the IDs of job you want to describe.
        @param status: valid values include pending, working, failed, successful.
        @param job_action: the action of job you want to describe.
        @param resource_ids: the handle_resource id of job you want to describe
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        """
        action = const.ACTION_DESCRIBE_JOBS
        valid_keys = ['jobs', 'status', 'job_action', "resource_ids", 'offset', 'limit']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=["offset", "limit"],
                                             list_params=["jobs"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_images(self, param):
        """ Describe images filtered by condition.
        @param images: an array including IDs of the images you want to list.
                       No ID specified means list all.
        @param os_family: os family, windows/debian/centos/ubuntu.
        @param processor_type: supported processor types are `64bit` and `32bit`.
        @param status: valid values include pending, available, deleted, ceased.
        @param visibility: who can see and use this image. Valid values include public, private.
        @param provider: who provide this image, self, system.
        @param verbose: the number to specify the verbose level,
                        larger the number, the more detailed information will be returned.
        @param search_word: the search word.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        """

        action = const.ACTION_DESCRIBE_IMAGES
        valid_keys = ['images', 'os_family', 'processor_type', 'status', 'visibility', "ui_type",
                      'provider', 'verbose', 'search_word', 'offset', 'limit', 'owner', "sort_key"]
        body = filter_out_none(param, valid_keys)            

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[
                                                 "offset", "limit", "verbose"],
                                             list_params=["images"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def capture_instance(self, param):
        """ Capture an instance and make it available as an image for reuse.
        @param instance: ID of the instance you want to capture.
        @param image_name: short name of the image.
        """
        action = const.ACTION_CAPTURE_INSTANCE
        valid_keys = ['instance', 'image_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['instance'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_images(self, param):
        """ Delete one or more images whose provider is `self`.
        @param images: ID of the images you want to delete.
        """
        action = const.ACTION_DELETE_IMAGES
        valid_keys = ['images']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['images'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_image_attributes(self, param):
        """ Modify image attributes.
        @param image: the ID of image whose attributes you want to modify.
        @param image_name: Name of the image. It's a short name for the image
                           that more meaningful than image id.
        @param description: The detailed description of the image.
        """
        action = const.ACTION_MODIFY_IMAGE_ATTRIBUTES
        valid_keys = ['image', 'image_name', 'description']
        
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['image'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)
    
    def lease_desktop(self, param):

        action = const.ACTION_LEASE
        valid_keys = ['resources']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[
                                                 'resources']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)
    
    def describe_instances(self, param):
        """ Describe instances filtered by conditions
        @param instances : the array of IDs of instances
        @param image_id : ID of the image which is used to launch this instance.
        @param instance_type: The instance type.
                              See: https://docs.qingcloud.com/api/common/includes/instance_type.html
        @param status : Status of the instance, including pending, running, stopped, terminated.
        @param verbose: the number to specify the verbose level, larger the number, the more detailed information will be returned.
        @param search_word: the combined search column.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        @param tags : the array of IDs of tags.
        """
        action = const.ACTION_DESCRIBE_INSTANCES
        valid_keys = ['instances', 'image_id', 'instance_type', 'status',
                      'search_word', 'verbose', 'offset', 'limit', 'owner']
        body = filter_out_none(param, valid_keys)
        
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[
                                                 'offset', 'limit', 'verbose'],
                                             list_params=[
                                                 'instances', 'status', 'tags']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_instances_with_monitors(self, param):
        ''' Action:DescribeInstancesWithMonitors
            @param zone - which availability zone the request will be send to.
            @param instances : the array of IDs of instances            
            @param owner : the id of user whose instances you want to describe.
            @param search_word: search word column.
            @param offset: the starting offset of the returning results.
            @param limit: specify the number of the returning results.
            @param sort_key: Only supported cpu,memory,disk-os-xx
            @param reverse: reverse 0 True, 1 False

        '''
        action = const.ACTION_DESCRIBE_INSTANCES_WITH_MONITORS

        valid_keys = ['instances', 'search_word',
                      'sort_key', 'reverse', 'offset', 'limit', "verbose"]
        body = filter_out_none(param, valid_keys)
        
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[
                                                 'offset', 'limit', 'verbose'],
                                             list_params=[
                                                 'instances', 'status']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def run_instances(self, param):
        """ Create one or more instances.
        @param image_id : ID of the image you want to use, "img-12345"
        @param instance_type: What kind of instance you want to launch.
                              See: https://docs.qingcloud.com/api/common/includes/instance_type.html
        @param cpu: cpu core number.
        @param memory: memory size in MB.
        @param instance_name: a meaningful short name of instance.
        @param count : The number of instances to launch, default 1.
        @param vxnets : The IDs of vxnets the instance will join.
        @param security_group: The ID of security group that will apply to instance.
        @param login_mode: ssh login mode, "keypair" or "passwd"
        @param login_keypair: login keypair id
        @param login_passwd: login passwd
        @param need_newsid: Whether to generate new SID for the instance (True) or not
                            (False). Only valid for Windows instance; Silently ignored
                            for Linux instance.
        @param volumes: the IDs of volumes you want to attach to newly created instance,
                        parameter only affected when count = 1.
        @param need_userdata: Whether to enable userdata feature. 1 for enable, 0 for disable.
        @param userdata_type: valid type is either 'plain' or 'tar'
        @param userdata_value: base64 encoded string for type 'plain'; attachment id for type 'tar'
        @param userdata_path: path of metadata and userdata.string file to be stored
        @param instance_class: 0 is performance; 1 is high performance
        """
        action = const.ACTION_RUN_INSTANCES
        valid_keys = ['image_id', 'instance_type', 'cpu', 'memory', 'count',
                      'instance_name', 'vxnets', 'security_group', 'login_mode',
                      'login_keypair', 'login_passwd', 'need_newsid',
                      'volumes', 'need_userdata', 'userdata_type',
                      'userdata_value', 'userdata_path', 'instance_class',"gpu","gpu_class",
                      'hostname',"usbredir", "filetransfer", "clipboard", "graphics_protocol", 
                      "os_disk_size", "place_group_id", "cpu_model", "cpu_topology", "qxl_number",
                      "usb3_bus"
                      ]
        body = filter_out_none(param, valid_keys)
        if "graphics_protocol" not in body:
            body["graphics_protocol"] = "spice"
        
        if "hypervisor" not in body:
            body["hypervisor"] = "kvm"

        if "ivshmem" in param:
            ivshmem = param["ivshmem"]
            if ivshmem:
                if not isinstance(ivshmem,list):
                    body["ivshmem"] = [ivshmem]
                else:
                    body["ivshmem"] = ivshmem
        
        if not self.req_checker.check_params(body,
                                             required_params=['image_id'],
                                             integer_params=['count', 'cpu', 'memory', 'need_newsid',
                                                             'need_userdata', 'instance_class',"gpu","gpu_class", "usbredir", "filetransfer", "clipboard", "qxl_number", "os_disk_size"],
                                             list_params=['volumes', "ivshmem"],
                                             str_params=["usb3_bus"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def clone_instances(self, param):
        """ Clone instances  by instance_id
        @param instances : the IDs of instances you want to clone from
        @param vxnets : The IDs of vxnets the instance will join. like : instance_id|vxnet_id|ip_addr
        """
        action = const.ACTION_CLONE_INSTANCES
        valid_keys = ['instances', 'vxnets']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=["instances"],
                                             list_params=["instances",'vxnets']):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def terminate_instances(self, param):
        """ Terminate one or more instances.
        @param instances : An array including IDs of the instances you want to terminate.
        """
        action = const.ACTION_TERMINATE_INSTANCES
        valid_keys = ['instances']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['instances'],
                                             integer_params=[],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def stop_instances(self, param):
        """ Stop one or more instances.
        @param instances : An array including IDs of the instances you want to stop.
        @param force: False for gracefully shutdown and True for forcibly shutdown.
        """
        action = const.ACTION_STOP_INSTANCES
        valid_keys = ['instances', "force"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['instances'],
                                             integer_params=['force'],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def restart_instances(self, param):
        """ Restart one or more instances.
        @param instances : An array including IDs of the instances you want to restart.
        """

        action = const.ACTION_RESTART_INSTANCES
        valid_keys = ['instances']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['instances'],
                                             integer_params=[],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def start_instances(self, param):
        """ Start one or more instances.
        @param instances : An array including IDs of the instances you want to start.
        """
        action = const.ACTION_START_INSTANCES
        valid_keys = ['instances']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['instances'],
                                             integer_params=[],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def reset_instances(self, param):
        """ Reset one or monre instances to its initial state.
        @param login_mode: login mode, only supported for linux instance, valid values are "keypair", "passwd".
        @param login_passwd: if login_mode is "passwd", should be specified.
        @param login_keypair: if login_mode is "keypair", should be specified.
        @param instances : an array of instance ids you want to reset.
        @param need_newsid: Whether to generate new SID for the instance (True) or not
                            (False). Only valid for Windows instance; Silently ignored
                            for Linux instance.
        """
        action = const.ACTION_RESET_INSTANCES
        valid_keys = ['instances', 'login_mode',
                      'login_passwd', 'login_keypair', 'need_newsid']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['instances'],
                                             integer_params=['need_newsid'],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def resize_instances(self, param):
        """ Resize one or more instances
        @param instances: the IDs of the instances you want to resize.
        @param instance_type: defined by qingcloud.
                              See: https://docs.qingcloud.com/api/common/includes/instance_type.html
        @param cpu: cpu core number.
        @param memory: memory size in MB.
        """
        action = const.ACTION_RESIZE_INSTANCES
        valid_keys = ['instances', 'instance_type', 'cpu', 'memory', "gpu"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['instances'],
                                             integer_params=['cpu', 'memory', 'gpu'],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_instance_attributes(self, param):
        """ Modify instance attributes.
        @param instance:  the ID of instance whose attributes you want to modify.
        @param instance_name: Name of the instance. It's a short name for the instance
                              that more meaningful than instance id.
        @param description: The detailed description of the handle_resource.
        """
        action = const.ACTION_MODIFY_INSTANCE_ATTRIBUTES
        valid_keys = ['instance', 'instance_name', 'description', 'usbredir', 'clipboard', 'filetransfer', 'qxl_number']
        body = filter_out_none(param, valid_keys)
        if "ivshmem" in param:
            ivshmem = param["ivshmem"]
            if ivshmem:
                
                if not isinstance(ivshmem,list):
                    body["ivshmem"] = [ivshmem]
                else:
                    body["ivshmem"] = ivshmem

        if not self.req_checker.check_params(body,
                                             required_params=['instance'],
                                             integer_params=['usbredir', 'clipboard', 'filetransfer', 'qxl_number'],
                                             list_params=["ivshmem"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_brokers(self, param):
        ''' Action:CreateBrokers
            @param directive : the dictionary of params
        '''
        action = const.ACTION_CREATE_BROKERS
        valid_keys = ['instances', 'plugin', "is_token"]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=["instances"],
                                             integer_params=["plugin", "is_token"],
                                             list_params=["instances"]):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_brokers(self, param):
        ''' Action:DeleteBrokers
            @param directive : the dictionary of params
        '''
        action = const.ACTION_DELETE_BROKERS
        valid_keys = ['instances']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=["instances"],
                                             list_params=["instances"]):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_volumes(self, param):
        """ Describe volumes filtered by conditions
        @param volumes : the array of IDs of volumes.
        @param volume_type : the type of volume, 0 is high performance, 1 is high capacity
        @param instance_id: ID of the instance that volume is currently attached to, if has.
        @param status: pending, available, in-use, deleted.
        @param search_word: the combined search column.
        @param verbose: the number to specify the verbose level, larger the number, the more detailed information will be returned.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        @param tags : the array of IDs of tags.
        """
        action = const.ACTION_DESCRIBE_VOLUMES
        valid_keys = ['volumes', 'instance_id', 'search_word', "status",
                      'volume_type', 'verbose', 'offset', 'limit', 'tags', 'owner']
        body = filter_out_none(param, valid_keys)
        
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[
                                                 'offset', 'limit', 'verbose'],
                                             list_params=[
                                                 'volumes', 'status', 'tags']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_volumes(self, param):
        """ Create one or more volumes.
        @param size : the size of each volume. Unit is GB.
        @param volume_name : the short name of volume
        @param volume_type : the type of volume, 0 is high performance, 1 is high capacity
        @param count : the number of volumes to create.
        """
        action = const.ACTION_CREATE_VOLUMES
        valid_keys = ['size', 'volume_name', 'volume_type', 'count']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['size'],
                                             integer_params=['size', 'count'],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_volumes(self, param):
        """ Delete one or more volumes.
        @param volumes : An array including IDs of the volumes you want to delete.
        """
        action = const.ACTION_DELETE_VOLUMES
        valid_keys = ['volumes']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['volumes'],
                                             integer_params=[],
                                             list_params=['volumes']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def attach_volumes(self, param):
        """ Attach one or more volumes to same instance
        @param volumes : an array including IDs of the volumes you want to attach.
        @param instance : the ID of instance the volumes will be attached to.
        """
        action = const.ACTION_ATTACH_VOLUMES
        valid_keys = ['volumes', 'instance']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['volumes', 'instance'],
                                             integer_params=[],
                                             list_params=['volumes']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def detach_volumes(self, param):
        """ Detach one or more volumes from same instance.
        @param volumes : An array including IDs of the volumes you want to attach.
        @param instance : the ID of instance the volumes will be detached from.
        """

        action = const.ACTION_DETACH_VOLUMES
        valid_keys = ['volumes', 'instance']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['volumes', 'instance'],
                                             integer_params=[],
                                             list_params=['volumes']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def resize_volumes(self, param):
        """ Extend one or more volumes' size.
        @param volumes: The IDs of the volumes you want to resize.
        @param size : The new larger size of the volumes, unit is GB
        """
        action = const.ACTION_RESIZE_VOLUMES
        valid_keys = ['volumes', 'size']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['volumes', 'size'],
                                             integer_params=['size'],
                                             list_params=['volumes']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_volume_attributes(self, param):
        """ Modify volume attributes.
        @param volume:  the ID of volume whose attributes you want to modify.
        @param volume_name: Name of the volume. It's a short name for
                            the volume that more meaningful than volume id.
        @param description: The detailed description of the handle_resource.
        """
        action = const.ACTION_MODIFY_VOLUME_ATTRIBUTES
        valid_keys = ['volume', 'volume_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['volume'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_security_groups(self, param):

        action = const.ACTION_DESCRIBE_SECURITY_GROUPS
        valid_keys = ['security_groups', 'security_group_name', 'search_word', "group_type", "owner","default",
                      'verbose', 'offset', 'limit']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['offset', 'limit', 'verbose'],
                                             list_params=['security_groups']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_security_group(self, param):
        """ Create a new security group without any rule.
        @param security_group_name: the name of the security group you want to create.
        """
        action = const.ACTION_CREATE_SECURITY_GROUP
        valid_keys = ['security_group_name', "description", "security_group_rulesets", "group_type"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_security_group_attributes(self, param):

        action = const.ACTION_MODIFY_SECURITY_GROUP_ATTRIBUTES
        valid_keys = ['security_group', 'security_group_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_security_groups(self, param):

        action = const.ACTION_DELETE_SECURITY_GROUPS
        valid_keys = ['security_groups']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_groups'],
                                             integer_params=[],
                                             list_params=['security_groups']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def rollback_security_group(self, param):
        action = const.ACTION_ROLLBACK_SECURITY_GROUP
        valid_keys = ['security_group', "security_group_snapshot"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def remove_security_group(self, param):
        '''
            @param instances: the IDs of the instances you want to remove their security groups.
        '''
        action = const.ACTION_REMOVE_SECURITY_GROUP
        valid_keys = ["instances"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['instances'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def apply_security_group(self, param):

        action = const.ACTION_APPLY_SECURITY_GROUP
        valid_keys = ['security_group', 'instances', "nics"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group'],
                                             integer_params=[],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)
        return self.send_request(action, body)

    def describe_security_group_rules(self, param):

        action = const.ACTION_DESCRIBE_SECURITY_GROUP_RULES
        valid_keys = ['security_group', 'security_group_rules', 'direction', "owner",
                      'offset', 'limit']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['direction', 'offset', 'limit'],
                                             list_params=['security_group_rules']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_security_group_and_ruleset(self, param):
        ''' @param security_group: the ID of the security group whose rulesets you want to describe.
                or the ID of the security group ruleset whose security groups you want to describe.
            @param owner: the ID of user whose security group rules you want to describe.
            @param offset: the starting offset of the returning results.
            @param limit: specify the number of the returning results.
        '''
        action = const.ACTION_DESCRIBE_SECURITY_GROUP_AND_RULESET
        valid_keys = ['security_group', 'offset', 'limit']

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['offset', 'limit'],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def add_security_group_rulesets(self, param):
        '''
            @param security_group: the ID of the security group whose rules you
                                      want to add.
            @param security_group_rulesets: a list of ID of the security group rulesets
                                        you want to add.
        '''
        action = const.ACTION_ADD_SECURITY_GROUP_RULESETS
        valid_keys = ['security_group', 'security_group_rulesets']

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['security_group_rulesets']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def remove_security_group_rulesets(self, param):
        '''
            @param security_group: the ID of security_group which you want to delete
                                 security group rulesets from.
            @param security_group_rulesets: the IDs of security group rulesets
                                     you want to delete.
        '''
        action = const.ACTION_REMOVE_SECURITY_GROUP_RULESETS
        valid_keys = ['security_group', 'security_group_rulesets']

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['security_group_rulesets']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def add_security_group_rules(self, param):

        action = const.ACTION_ADD_SECURITY_GROUP_RULES
        valid_keys = ['security_group', 'rules']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group', 'rules'],
                                             integer_params=[],
                                             list_params=['rules']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_security_group_rules(self, param):

        action = const.ACTION_DELETE_SECURITY_GROUP_RULES
        valid_keys = ['security_group_rules']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[
                                                 'security_group_rules'],
                                             integer_params=[],
                                             list_params=[
                                                 'security_group_rules']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_security_group_rule_attributes(self, param):
        """ Modify security group rule attributes.
        @param security_group_rule: the ID of the security group rule whose attributes you
                                    want to update.
        @param priority: priority [0 - 100].
        @param security_group_rule_name: name of the rule.
        @param rule_action: "accept" or "drop".
        @param direction: 0 for inbound; 1 for outbound.
        @param protocol: supported protocols are "icmp", "tcp", "udp", "gre".
        @param val1: for "icmp" protocol, this field is "icmp type";
                     for "tcp/udp", it's "start port", empty means all.
        @param val2: for "icmp" protocol, this field is "icmp code";
                     for "tcp/udp", it's "end port", empty means all.
        @param val3: ip network, e.g "1.2.3.0/24"
        """
        action = const.ACTION_MODIFY_SECURITY_GROUP_RULE_ATTRIBUTES
        valid_keys = ['security_group_rule', 'priority', 'security_group_rule_name',
                      'rule_action', 'direction', 'protocol', 'val1', 'val2', 'val3', "disabled"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group_rule'],
                                             integer_params=['priority'],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def apply_security_group_ruleset(self, param):
        '''
            @param security_group_ruleset: the ID of the security group ruleset 
                                that you want to apply to instances.
        '''
        action = const.ACTION_APPLY_SECURITY_GROUP_RULESET
        valid_keys = ['security_group_ruleset']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group_ruleset'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_security_group_ipsets(self, param):

        action = const.ACTION_DESCRIBE_SECURITY_GROUP_IPSETS
        valid_keys = ['security_group_ipsets', 'ipset_type', "owner",
                      'security_group_ipset_name',
                      'offset', 'limit']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['ipset_type', 'offset', 'limit'],
                                             list_params=['security_group_rules']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_security_group_ipset(self, param):
        """ Create security group ipset.
        @param ipset_type: 0 for ip; 1 for port
        @param val: such as 192.168.1.0/24 or 10000-15000
        @param security_group_ipset_name: the name of the security group ipsets
        """
        action = const.ACTION_CREATE_SECURITY_GROUP_IPSET
        valid_keys = ['security_group_ipset_name', 'ipset_type', 'val']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['ipset_type', 'val'],
                                             integer_params=['ipset_type'],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_security_group_ipsets(self, param):

        action = const.ACTION_DELETE_SECURITY_GROUP_IPSETS
        valid_keys = ['security_group_ipsets']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group_ipsets'],
                                             integer_params=[],
                                             list_params=['security_group_ipsets']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_security_group_ipset_attributes(self, param):
        """ Modify security group ipset attributes.
        @param security_group_ipset: the ID of the security group ipset whose attributes you
                                    want to update.
        @param security_group_ipset_name: name of the ipset.
        @param description: The detailed description of the handle_resource.
        @param val1: for "ip", this field is like:  192.168.1.0/24
                     for "port", this field is like: 10000-15000
        """
        action = const.ACTION_MODIFY_SECURITY_GROUP_IPSET_ATTRIBUTES
        valid_keys = ['security_group_ipset', 'security_group_ipset_name',
                      'description', 'val']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group_ipset'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def apply_security_group_ipsets(self, param):
        '''
            @param directive : the dictionary of params
        '''
        action = const.ACTION_APPLY_SECURITY_GROUP_IPSETS
        valid_keys = ['security_group_ipsets']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group_ipsets'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_security_group_snapshots(self, param):
        
        action = const.ACTION_DESCRIBE_SECURITY_GROUP_SNAPSHOTS
        valid_keys = ['security_group', 'offset', 'limit', "security_group_snapshots"]
        body = filter_out_none(param, valid_keys)   
        if not self.req_checker.check_params(body,
                                  required_params=["zone"],
                                  str_params=["zone", "security_group"],
                                  integer_params=["offset", "limit"],
                                  list_params=["security_group_snapshots"],
                                  filter_params=[]):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_security_group_snapshot(self, param):

        action = const.ACTION_CREATE_SECURITY_GROUP_SNAPSHOT

        valid_keys = ['security_group', 'name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_security_group_snapshots(self, param):
        action = const.ACTION_DELETE_SECURITY_GROUP_SNAPSHOTS
    
        valid_keys = ['security_group_snapshots']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['security_group_snapshots'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_snapshots(self, param):
        """ Describe snapshots filtered by condition.
        @param snapshots: an array including IDs of the snapshots you want to list.
                          No ID specified means list all.
        @param resource_id: filter by resource ID.
        @param snapshot_type: filter by snapshot type. 0: incremantal snapshot, 1: full snapshot.
        @param root_id: filter by snapshot root ID.
        @param status: valid values include pending, available, suspended, deleted, ceased.
        @param verbose: the number to specify the verbose level,
                        larger the number, the more detailed information will be returned.
        @param search_word: the search word.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        @param tags : the array of IDs of tags.
        """
        action = const.ACTION_DESCRIBE_SNAPSHOTS
        valid_keys = ['snapshots', 'resource_id', 'snapshot_type', 'root_id', 'status',
                      'verbose', 'search_word', 'offset', 'limit', 'tags', 'owner']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[
                                                 "offset", "limit", "verbose", "snapshot_type"],
                                             list_params=["snapshots", "tags"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_snapshots(self, param):
        """ Create snapshots.
        @param resources: the IDs of resources you want to create snapshot for, the supported resource types are instance/volume.
        @param snapshot_name: the name of the snapshot.
        @param is_full: whether to create a full snapshot. 0: determined by the system. 1: should create full snapshot.
        """
        action = const.ACTION_CREATE_SNAPSHOTS
        valid_keys = ['resources', 'snapshot_name', 'is_full']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["resources"],
                                             integer_params=["is_full"],
                                             list_params=["resources"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_snapshots(self, param):
        """ Delete snapshots.
        @param snapshots: the IDs of snapshots you want to delete.
        """
        action = const.ACTION_DELETE_SNAPSHOTS
        valid_keys = ['snapshots']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["snapshots"],
                                             integer_params=[],
                                             list_params=["snapshots"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def apply_snapshots(self, param):
        """ Apply snapshots.
        @param snapshots: the IDs of snapshots you want to apply.
        """
        action = const.ACTION_APPLY_SNAPSHOTS
        valid_keys = ['snapshots']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["snapshots"],
                                             integer_params=[],
                                             list_params=["snapshots"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_snapshot_attributes(self, param):
        """ Modify snapshot attributes.
        @param snapshot: the ID of snapshot whose attributes you want to modify.
        @param snapshot_name: the new snapshot name.
        @param description: the new snapshot description.
        """        
        action = const.ACTION_MODIFY_SNAPSHOT_ATTRIBUTES
        valid_keys = ['snapshot', 'snapshot_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["snapshot"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def capture_instance_from_snapshot(self, param):
        """ Capture instance from snapshot.
        @param snapshot: the ID of snapshot you want to export as an image, this snapshot should be created from an instance.
        @param image_name: the image name.
        """
        action = const.ACTION_CAPTURE_INSTANCE_FROM_SNAPSHOT
        valid_keys = ['snapshot', 'image_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["snapshot"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_volume_from_snapshot(self, param):
        """ Create volume from snapshot.
        @param snapshot: the ID of snapshot you want to export as an volume, this snapshot should be created from a volume.
        @param volume_name: the volume name.
        """
        action = const.ACTION_CREATE_VOLUME_FROM_SNAPSHOT
        valid_keys = ['snapshot', 'volume_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["snapshot"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_vxnets(self, param):
        """ Describe vxnets filtered by condition.
        @param vxnets: the IDs of vxnets you want to describe.
        @param verbose: the number to specify the verbose level, larger the number, the more detailed information will be returned.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        @param tags : the array of IDs of tags.
        @param vxnet_type: the vxnet of type you want to describe.
        """
        action = const.ACTION_DESCRIBE_VXNETS
        valid_keys = ['vxnets', 'search_word', 'verbose', 'limit', 'offset',"excluded_vxnets",
                      'tags', 'vxnet_type', 'owner']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['limit', 'offset', 'verbose'],
                                             list_params=['vxnets', 'tags', "excluded_vxnets", 'vxnet_type']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_vxnets(self, param):
        """ Create one or more vxnets.
        @param vxnet_name: the name of vxnet you want to create.
        @param vxnet_type: vxnet type: unmanaged or managed.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        """
        action = const.ACTION_CREATE_VXNETS
        valid_keys = ['vxnet_name', 'vxnet_type', 'count']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['vxnet_type'],
                                             integer_params=[
                                                 'vxnet_type', 'count'],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def join_vxnet(self, param):
        """ One or more instances join the vxnet.
        @param vxnet : the id of vxnet you want the instances to join.
        @param instances : the IDs of instances that will join vxnet.
        """

        action = const.ACTION_JOIN_VXNET
        valid_keys = ['vxnet', 'instances']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['vxnet', 'instances'],
                                             integer_params=[],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def leave_vxnet(self, param):
        """ One or more instances leave the vxnet.
        @param vxnet : The id of vxnet that the instances will leave.
        @param instances : the IDs of instances that will leave vxnet.
        """
        action = const.ACTION_LEAVE_VXNET
        valid_keys = ['vxnet', 'instances']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[
                                                 'vxnet', 'instances'],
                                             integer_params=[],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_vxnets(self, param):
        """ Delete one or more vxnets.
        @param vxnets: the IDs of vxnets you want to delete.
        """
        action = const.ACTION_DELETE_VXNETS
        valid_keys = ['vxnets']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['vxnets'],
                                             integer_params=[],
                                             list_params=['vxnets']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_vxnet_attributes(self, param):
        """ Modify vxnet attributes
        @param vxnet: the ID of vxnet you want to modify its attributes.
        @param vxnet_name: the new name of vxnet.
        @param description: The detailed description of the handle_resource.
        """
        action = const.ACTION_MODIFY_VXNET_ATTRIBUTES
        valid_keys = ['vxnet', 'vxnet_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['vxnet'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_vxnet_instances(self, param):
        """ Describe instances in vxnet.
        @param vxnet: the ID of vxnet whose instances you want to describe.
        @param image: filter by image ID.
        @param instances: filter by instance ID.
        @param instance_type: filter by instance type
                              See: https://docs.qingcloud.com/api/common/includes/instance_type.html
        @param status: filter by status
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        """
        action = const.ACTION_DESCRIBE_VXNET_INSTANCES
        valid_keys = ['vxnet', 'instances', 'image', 'instance_type', 'status',
                      'limit', 'offset']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['vxnet'],
                                             integer_params=['limit', 'offset'],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_vxnet_resources(self, param):
        """ Describe instances in vxnet.
        @param vxnet: the ID of vxnet whose instances you want to describe.
        @param image: filter by image ID.
        @param instances: filter by instance ID.
        @param instance_type: filter by instance type
                              See: https://docs.qingcloud.com/api/common/includes/instance_type.html
        @param status: filter by status
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        """
        action = const.ACTION_DESCRIBE_VXNET_RESOURCES
        valid_keys = ['vxnet', 'instances', 'image', 'instance_type', 'status',
                      'limit', 'offset']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['vxnet'],
                                             integer_params=['limit', 'offset'],
                                             list_params=['instances']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_routers(self, param):
        """ Describe routers filtered by condition.
        @param routers: the IDs of the routers you want to describe.
        @param vxnet: the ID of vxnet you want to describe.
        @param verbose: the number to specify the verbose level, larger the number, the more detailed information will be returned.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        @param tags : the array of IDs of tags.
        """
        action = const.ACTION_DESCRIBE_ROUTERS
        valid_keys = ['routers', 'vxnet', 'status', 'verbose', 'search_word',"mode",
                      'limit', 'offset', 'tags', 'owner']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['limit', 'offset', 'verbose'],
                                             list_params=['routers', 'tags']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_routers(self, param):
        """ Create one or more routers.
        @param router_name: the name of the router.
        @param security_group: the ID of the security_group you want to apply to router.
        @param count: the count of router you want to create.
        @param vpc_network: VPC IP addresses range, currently support "192.168.0.0/16" or "172.16.0.0/16", required in zone pek3a.
        """
        action = const.ACTION_CREATE_ROUTERS
        valid_keys = ['count', 'router_name', 'security_group', 'vpc_network', "router_type"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['count'],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_routers(self, param):
        """ Delete one or more routers.
        @param routers: the IDs of routers you want to delete.
        """
        action = const.ACTION_DELETE_ROUTERS
        valid_keys = ['routers']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['routers'],
                                             integer_params=[],
                                             list_params=['routers']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def update_routers(self, param):
        """ Update one or more routers.
        @param routers: the IDs of routers you want to update.
        """
        action = const.ACTION_UPDATE_ROUTERS
        valid_keys = ['routers']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['routers'],
                                             integer_params=[],
                                             list_params=['routers']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def join_router(self, param):
        """ Connect vxnet to router.
        @param vxnet: the ID of vxnet that will join the router.
        @param router: the ID of the router the vxnet will join.
        @param ip_network: the ip network in CSI format.
        @param manager_ip: can be provided if DHCP feature is enabled.
        @param dyn_ip_start: starting IP that allocated from DHCP server.
        @param dyn_ip_end: ending IP that allocated from DHCP server.
        @param features: the feature the vxnet will enable in the router.
                         1 - dhcp server.
        """
        action = const.ACTION_JOIN_ROUTER
        valid_keys = ['vxnet', 'router', 'ip_network', 'manager_ip',
                      'dyn_ip_start', 'dyn_ip_end', 'features']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['vxnet', 'router', 'ip_network'],
                                             integer_params=['features'],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def leave_router(self, param):
        """ Disconnect vxnets from router.
        @param vxnets: the IDs of vxnets that will leave the router.
        @param router: the ID of the router the vxnet will leave.
        """
        action = const.ACTION_LEAVE_ROUTER
        valid_keys = ['router', 'vxnets']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['vxnets', 'router'],
                                             integer_params=[],
                                             list_params=['vxnets']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_router_attributes(self, param):
        """ Modify router attributes.
        @param router: the ID of router you want to modify its attributes.
        @param vxnet: the ID of vxnet whose feature you want to modify.
        @param eip: the eip.
        @param security_group: the ID of the security_group you want to apply to router.
        @param router_name: the name of the router.
        @param description: the description of the router.
        @param features: the features of vxnet you want to re-define. 1: enable DHCP; 0: disable DHCP
        @param dyn_ip_start: starting IP that allocated from DHCP server
        @param dyn_ip_end: ending IP that allocated from DHCP server
        """
        action = const.ACTION_MODIFY_ROUTER_ATTRIBUTES
        valid_keys = ['router', 'vxnet', 'eip', 'security_group', 'features',
                      'router_name', 'description', 'dyn_ip_start', 'dyn_ip_end']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['router'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_router_vxnets(self, param):
        """ Describe vxnets in router.
        @param router: filter by router ID.
        @param vxnet: filter by vxnet ID.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        """
        action = const.ACTION_DESCRIBE_ROUTER_VXNETS
        valid_keys = ['router', 'vxnet', 'limit', 'offset', 'owner']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[
                                                 'limit', 'offset'],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def get_monitoring_data(self, param):
        """ Get handle_resource monitoring data.
        @param handle_resource: the ID of handle_resource, can be instance_id, volume_id, eip_id or router_id.
        @param meters: list of metering types you want to get.
                       If handle_resource is instance, meter can be "cpu", "disk-os", "memory",
                       "disk-%s" % attached_volume_id, "if-%s" % vxnet_mac_address.
                       If handle_resource is volume, meter should be "disk-%s" % volume_id.
                       If handle_resource is eip, meter should be "traffic".
                       If handle_resource is router, meter can be "vxnet-0" and joint vxnet ID.
        @param step: The metering time step, valid steps: "5m", "15m", "30m", "1h", "2h", "1d".
        @param start_time: the starting UTC time, in the format YYYY-MM-DDThh:mm:ssZ.
        @param end_time: the ending UTC time, in the format YYYY-MM-DDThh:mm:ssZ.
        """
        action = const.ACTION_GET_MONITOR
        valid_keys = ['resource', 'meters', 'step', 'start_time', 'end_time']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[
                                                 'resource', 'meters', 'step', 'start_time', 'end_time'],
                                             integer_params=[],
                                             list_params=['meters']
                                             ):
            return self.return_param_invaild(action, body)
        
        decompress = body.get("decompress", False)
        start_time = body.get("start_time")
        end_time = body.get("end_time")
        step = body.get("step")
        resp = self.send_request(action, body)
        if resp and resp.get('meter_set') and decompress:
            p = MonitorProcessor(resp['meter_set'], start_time, end_time, step)
            resp['meter_set'] = p.decompress_monitoring_data()
        return resp
    
    def send_desktop_message(self, param):
        """ Create volume from snapshot.
        @param base64_message: base64 format message
        """
        action = const.ACTION_SEND_VDI_GUEST_MESSAGE
        valid_keys = ['instances', 'base64_message']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["instances", "base64_message"],
                                             integer_params=[],
                                             list_params=["instances"]):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)
    
    def send_desktop_hot_keys(self, param):
        """ Create volume from snapshot.
        @param base64_message: base64 format message
        """
        action = const.ACTION_SEND_VDI_GUEST_KEYS
        valid_keys = ['instances', 'keys', 'timeout', 'time_step']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["instances", "keys"],
                                             integer_params=['timeout', 'time_step'],
                                             list_params=["instances"]):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_nics(self, param):

        action = const.ACTION_DESCRIBE_NICS
        valid_keys = ['nics', 'instances', 'vxnets', 'offset', "limit", "status","search_word", "owner"]
        body = filter_out_none(param, valid_keys)
        
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['offset', "limit"],
                                             list_params=['instances', 'vxnets', 'nics', "status"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_nics(self, param):

        action = const.ACTION_CREATE_NICS

        valid_keys = ['vxnet', 'count', 'private_ips', 'nic_name']
        body = filter_out_none(param, valid_keys)
        if "count" in body:
            body["count"] = str(body["count"])
        
        if not self.req_checker.check_params(body,
                                             required_params=['vxnet'],
                                             integer_params=[],
                                             str_params=["count"],
                                             list_params=['private_ips']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_nics(self, param):

        action = const.ACTION_DELETE_NICS
        valid_keys = ['nics']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['nics'],
                                             integer_params=[],
                                             list_params=["nics"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def attach_nics(self, param):

        action = const.ACTION_ATTACH_NICS
        valid_keys = ['nics', 'instance']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['nics', 'instance'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def detach_nics(self, param):

        action = const.ACTION_DETACH_NICS
        valid_keys = ['nics']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['nics'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_nic_attributes(self, param):

        action = const.ACTION_MODIFY_NIC_ATTRIBUTES
        valid_keys = ['nic', "private_ip"]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['nic'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_zones(self, param):

        action = const.ACTION_DESCRIBE_ZONES
        valid_keys = ['zones', "status", "region"]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['zones']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_access_keys(self, param):

        action = const.ACTION_DESCRIBE_ACCESS_KEYS
        valid_keys = ['access_keys', 'status', 'offset', 'limit']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=["offset", "limit"],
                                             list_params=['access_keys',"status"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_users(self, param):

        action = const.ACTION_DESCRIBE_USERS
        valid_keys = ['users', 'status', 'offset', 'limit']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=["offset", "limit"],
                                             list_params=['users',"status"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_keypairs(self, param):
        action = const.ACTION_DESCRIBE_SSH_KEY_PAIRS
        valid_keys = ['owner', 'keypair_name', 'keypairs']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['owner', 'keypair_name'],
                                             str_params=['access_keys',"status"],
                                             list_params=['keypairs']):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_keypair(self, param):
        action = const.ACTION_CREATE_SSH_KEY_PAIR
        valid_keys = ['owner', 'keypair_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['owner', 'keypair_name'],
                                             str_params=['access_keys',"status"]):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def get_resource_limit(self, param):

        action = const.ACTION_GET_RESOURCE_LIMIT
        valid_keys = ['zone']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['zone'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)
    
    def describe_place_groups(self, param):

        action = const.ACTION_DESCRIBE_PLACE_GROUPS
        valid_keys = ['place_groups', "status"]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['place_groups']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_rdb_attributes(self, param):
        """ Modify rdb attributes.
        @param rdb: the ID of rdb whose attributes you want to modify.
        @param rdb_name: the new rdb name.
        @param description: the new rdb description.
        """
        action = const.ACTION_MODIFY_RDB_ATTRIBUTES
        valid_keys = ['rdb', 'rdb_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["rdb"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_cache_attributes(self, param):
        """ Modify cache attributes.
        @param cache: the ID of cache whose attributes you want to modify.
        @param cache_name: the new cache name.
        @param description: the new cache description.
        """
        action = const.ACTION_MODIFY_CACHE_ATTRIBUTES
        valid_keys = ['cache', 'cache_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["cache"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_s2server_attributes(self, param):
        """ Modify s2server attributes.
        @param s2server: the ID of s2server whose attributes you want to modify.
        @param s2_server_name: the new s2server name.
        @param description: the new s2server description.
        """
        action = const.ACTION_MODIFY_S2SERVER_ATTRIBUTES
        valid_keys = ['s2_server', 's2_server_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["s2_server"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_loadbalancer_attributes(self, param):
        """ Modify loadbalancer attributes.
        @param loadbalancer: the ID of loadbalancer whose attributes you want to modify.
        @param loadbalancer_name: the new loadbalancer name.
        @param description: the new loadbalancer description.
        """
        action = const.ACTION_MODIFY_LOADBALANCER_ATTRIBUTES
        valid_keys = ['loadbalancer', 'loadbalancer_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["loadbalancer"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_rdbs(self, param):

        action = const.ACTION_DESCRIBE_RDBS
        valid_keys = ['rdbs','verbose']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['rdbs']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_clusters(self, param):

        action = const.ACTION_DESCRIBE_CLUSTERS
        valid_keys = ['clusters','verbose']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['clusters']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_caches(self, param):

        action = const.ACTION_DESCRIBE_CACHES
        valid_keys = ['caches']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['caches']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_loadbalancers(self, param):

        action = const.ACTION_DESCRIBE_LOADBALANCERS
        valid_keys = ['loadbalancers','verbose']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['loadbalancers'],
                                             integer_params=[],
                                             list_params=['loadbalancers']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_loadbalancer_backends(self, param):

        action = const.ACTION_DESCRIBE_LOADBALANCER_BACKENDS
        valid_keys = ['loadbalancer_listener']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['loadbalancer_listener'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_s2servers(self, param):

        action = const.ACTION_DESCRIBE_S2SERVERS
        valid_keys = ['verbose','s2_servers']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['s2_servers'],
                                             integer_params=[],
                                             list_params=['s2_servers']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_s2_groups(self, param):

        action = const.ACTION_DESCRIBE_S2_GROUPS
        valid_keys = [
            'owner','s2_groups', 'group_types', 'account_name', 'search_word',
            'verbose', 'offset', 'limit',
        ]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['offset', 'limit', 'verbose'],
                                             list_params=['s2_groups', 'group_types'],
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_s2_account(self, param):

        action = const.ACTION_CREATE_S2_ACCOUNT
        valid_keys = [
            'account_type', 'account_name', 'smb_name', 'smb_passwd',
            'nfs_ipaddr', 's2_groups', 'opt_parameters', 'description',
        ]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['s2_groups'],
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_s2_accounts(self, param):

        action = const.ACTION_DESCRIBE_S2_ACCOUNTS
        valid_keys = [
            's2_accounts', 'account_types', 'account_name', 'search_word',
            'verbose', 'offset', 'limit',
        ]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=["limit", "offset", "verbose"],
                                             list_params=["s2_accounts", "account_types"],
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def update_s2_servers(self, param):

        action = const.ACTION_UPDATE_S2_SERVERS
        valid_keys = [
            's2_servers',
        ]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=["s2_servers"],
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def poweroff_s2_servers(self, param):

        action = const.ACTION_POWEROFF_S2_SERVERS
        valid_keys = [
            's2_servers',
        ]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=["s2_servers"],
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def poweron_s2_servers(self, param):

        action = const.ACTION_POWERON_S2_SERVERS
        valid_keys = [
            's2_servers',
        ]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=["s2_servers"],
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_s2_server(self, param):
        """ Create S2 server

        :param vxnet: the ID of vxnet.
        :param service_type: valid values is vsan or vnas.
        :param s2_server_name: the name of s2 server.
        :param s2_server_type: valid values includes 0, 1, 2, 3.
        :param private_ip: you may specify the ip address of this server.
        :param description: the detailed description of the resource.
        :param s2_class: valid values includes 0, 1.
        """
        action = const.ACTION_CREATE_S2_SERVER
        valid_keys = [
            'vxnet', 'service_type', 's2_server_name', 's2_server_type',
            'private_ip', 'description', 's2_class',
        ]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=["s2_server_type", "s2_class"],
                                             list_params=[],
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_s2_shared_target(self, param):
        """ Create S2 shared target

        :param s2_server_id: the ID of s2 server.
        :param export_name: the name of shared target.
        :param target_type: valid values includes 'ISCSI', 'FCoE','NFS' and 'SMB'.
        :param description: the detailed description of the resource.
        :param volumes: the IDs of volumes will be attached as backstore.
        :param initiator_names: specify client IQN, available in vsan.
        """
        action = const.ACTION_CREATE_S2_SHARED_TARGET
        valid_keys = [
            's2_server_id', 'export_name', 'target_type',
            'description', 'volumes', 'initiator_names',
        ]
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=['volumes', 'initiator_names'],
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_cluster_attributes(self, param):
        """ Modify cluster attributes.
        @param cluster: the ID of cluster whose attributes you want to modify.
        @param name: the new cluster name.
        @param description: the new cluster description.
        """
        action = const.ACTION_MODIFY_CLUSTER_ATTRIBUTES
        valid_keys = ['cluster', 'name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["cluster"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_tags(self, param):

        """ Describe tags filtered by condition
        @param tags: IDs of the tags you want to describe.
        @param resources: IDs of the resources.
        @param verbose: the number to specify the verbose level, larger the number, the more detailed information will be returned.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        """

        action = const.ACTION_DESCRIBE_TAGS
        valid_keys = ['tags', 'search_word',
                      'verbose', 'offset', 'limit', 'owner', 'resources']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['offset', 'limit', 'verbose'],
                                             list_params=['tags', 'resources']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_tag(self, param):

        """ Create a tag.
        @param tag_name: the name of the tag you want to create.
        """
        action = const.ACTION_CREATE_TAG
        valid_keys = ['tag_name','color']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['tag_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def attach_tags(self, param):

        """ Attach one or more tags to resources.
        @param resource_tag_pairs: the pair of resource and tag.
        it's a list-dict, such as:
        [{
        'tag_id': 'tag-hp55o9i5',
        'resource_type': 'instance',
        'resource_id': 'i-5yn6js06'
        }]
        """
        action = const.ACTION_ATTACH_TAGS
        valid_keys = ['resource_tag_pairs','selectedData']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=['resource_tag_pairs'],
                                             integer_params=[],
                                             list_params=['resource_tag_pairs','selectedData']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def get_quota_left(self, param):

        """ get quota left filtered by condition.
        @resource_types:resource types array ID
        @param owner: an user ID you want to list quotas.
        @param verbose: the number to specify the verbose level,
                        larger the number, the more detailed information will be returned.
        @param search_word: the search word.
        @param offset: the starting offset of the returning results.
        @param limit: specify the number of the returning results.
        @param tags : the array of IDs of tags.
        """
        action = const.ACTION_GET_QUOTA_LEFT
        valid_keys = ['resource_types','owner']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=["resource_types","owner"],
                                             integer_params=["offset", "limit", "verbose"],
                                             list_params=['resource_types']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

class MonitorProcessor(object):
    """ Process monitoring data.
    """

    def __init__(self, raw_meter_set, start_time, end_time, step):
        self.raw_meter_set = raw_meter_set
        self.start_time = local_ts(start_time)
        self.end_time = local_ts(end_time)
        self.step = STEPS.get(step)

    def _is_invalid(self, value):
        if isinstance(value, list):
            return any(v == NA for v in value)
        else:
            return value == NA

    def _get_empty_item(self, sample_item):
        """ Return empty item which is used as supplemental data.
        """
        if isinstance(sample_item, list):
            return [None] * len(sample_item)
        else:
            return None

    def _fill_vacancies(self, value, from_ts, to_ts):
        ret = []
        t = from_ts
        while t < to_ts:
            ret.append([t, value])
            t += self.step
        return ret

    def _decompress_meter_data(self, data):
        """ Decompress meter data like:
            [
                [1391854500, 3],  # first item with timestamp
                4,                # normal value
                [200, 3],         # [timestamp_offset, value]
                NA,               # Not Avaliable
                ....
            ]
        """
        if not data or not self.step or not self.start_time:
            return data

        empty_item = self._get_empty_item(data[0][1])
        first_time = data[0][0]
        decompress_data = self._fill_vacancies(
            empty_item, self.start_time, first_time)

        decompress_data.append(data[0])
        t = first_time + self.step
        for item in data[1:]:
            if self._is_invalid(item):
                item = empty_item

            # sometimes item like [timestamp_offset, value]
            elif isinstance(item, list) and len(item) > 1:
                if not isinstance(empty_item, list) or isinstance(item[1], list):
                    t -= self.step
                    decompress_data += self._fill_vacancies(
                        empty_item, t + self.step, t + item[0])
                    t += item[0]
                    item = item[1]

            decompress_data.append([t, item])
            t += self.step

        return decompress_data

    def decompress_monitoring_data(self):
        """ Decompress instance/eip/volume monitoring data.
        """
        meter_set = deepcopy(self.raw_meter_set)
        for meter in meter_set:
            data = meter['data']
            if not data:
                continue
            meter['data'] = self._decompress_meter_data(data)
        return meter_set

