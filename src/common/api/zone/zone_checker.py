from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import constants as const
from utils.json import json_dump
import db.constants as dbconst

class ZoneChecker():
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def get_zone_info(self, zone_id):

        if not self.ctx.zones or zone_id not in self.ctx.zones:
            return Error(ErrorCodes.INTERNAL_ERROR, 
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

        return self.ctx.zones[zone_id]

    def dict_to_list(self, dict_data):
        
        list_data = []
        
        for data, value in dict_data.items():
            if value:
                value = "%s|%s" % (data, value)
            list_data.append(value)

        return list_data

    def get_zone_platform(self, zone_id, platform=None):
        
        ret = self.get_zone_info(zone_id)
        if isinstance(ret, Error):
            return ret
        zone = ret
        if platform:
            if platform != zone.platform:
                return False
            return True
        else:
            return zone.platform

    def get_resource_limit(self, zone_id, key=None):

        if not self.ctx.zones or zone_id not in self.ctx.zones:
            if not key:
                return Error(ErrorCodes.INTERNAL_ERROR, 
                             ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
            else:
                return None

        resource_limit = self.ctx.zones[zone_id].resource_limit
        if not key:
            return resource_limit
        else:
            return resource_limit.get(key)

    def check_managed_resource(self, zone_id, managed_resources, is_update=False):
        
        if not managed_resources:
            return Error(ErrorCodes.INTERNAL_ERROR, 
                         ErrorMsg.ERR_MSG_CITIRX_MANAGED_RESOURCE_NO_CONFIG)
        
        if not isinstance(managed_resources, list):
            managed_resources = [managed_resources]

        ret = self.get_resource_limit(zone_id)
        if isinstance(ret, Error):
            return ret
        resource_limit = ret

        ret = self.get_zone_platform(zone_id, const.PLATFORM_TYPE_CITRIX)
        if not ret:
            return False
        
        new_managed_resource = []
        for managed_resource in managed_resources:
            if managed_resource not in resource_limit["managed_resource"]:
                new_managed_resource.append(managed_resource)
        
        if not new_managed_resource:
            return True
        if is_update:
            new_managed_resource.extend(resource_limit["managed_resource"])
            update_info = {
                            "managed_resource": json_dump(new_managed_resource)
                           }
            if not self.ctx.pg.batch_update(dbconst.TB_ZONE_CITRIX_CONNECTION, {zone_id: update_info}):
                logger.error("update managed resource %s fail" % update_info)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
            
            self.ctx.zone_builder.load_zone(zone_id)
        else:
                return Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                         ErrorMsg.ERR_MSG_UNSUPPORTED_MANAGED_RESOURCE, managed_resources)
        return True

    def check_cpu_memory_pairs(self, zone_id, cpu, memory, is_update=False):

        ret = self.get_resource_limit(zone_id)
        if isinstance(ret, Error):
            return ret
        resource_limit = ret

        cpu_memory_pair = "%s|%s" % (cpu, memory)
        cpu_memory_pairs = resource_limit["cpu_memory_pairs"]
        if cpu_memory_pair in cpu_memory_pairs:
            return True

        if is_update:
            cpu_memory_pairs.append(cpu_memory_pair)
            update_info = {
                            "cpu_memory_pairs": json_dump(cpu_memory_pairs)
                           }
            if not self.ctx.pg.batch_update(dbconst.TB_ZONE_RESOURCE_LIMIT, {zone_id: update_info}):
                logger.error("update cpu memory pairs %s fail" % update_info)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
            
            self.ctx.zone_builder.load_zone(zone_id)
        else:
            logger.error("check cpu memory %s fail" % cpu_memory_pair)
            return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                         ErrorMsg.ERR_MSG_CPU_MEMORY_INVAILD, cpu_memory_pair)

        return True
            
    def check_disk_size(self, zone_id, disk_size):
        
        ret = self.get_resource_limit(zone_id)
        if isinstance(ret, Error):
            return ret
        resource_limit = ret

        disk_sizes = resource_limit["disk_size"]
        if disk_size < disk_sizes[0] or disk_size > disk_sizes[1]:
            logger.error("disk size %s exceed limit" % (disk_size))
            return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                         ErrorMsg.ERR_MSG_DISK_SIZE_EXCEEDS_DISK_LIMIT, (disk_size, disk_sizes))

        return True
    
    def check_instance_class(self, zone_id, instance_class, is_update=False):
        
        ret = self.get_resource_limit(zone_id)
        if isinstance(ret, Error):
            return ret
        resource_limit = ret

        instance_classes = resource_limit["instance_class"]
        if instance_class in instance_classes:
            return True

        if is_update:
            instance_classes.append(instance_class)
            update_info = {
                            "insstance_class": json_dump(instance_classes)
                           }
            if not self.ctx.pg.batch_update(dbconst.TB_ZONE_RESOURCE_LIMIT, {zone_id: update_info}):
                logger.error("update instance class %s fail" % update_info)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

            self.ctx.zone_builder.load_zone(zone_id)
        else:
            logger.error("check instance class %s fail" % instance_class)
            return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                         ErrorMsg.ERR_MSG_INSTANCE_CLASS_INVAILD, instance_class)

        return True

    def check_network_type(self, zone_id, network_type):

        ret = self.get_resource_limit(zone_id)
        if isinstance(ret, Error):
            return ret
        resource_limit = ret

        network_types = resource_limit["network_type"]
        if not isinstance(network_types, list):
            network_types = [network_types]
        
        if network_type in network_types:
            return True
        else:
            logger.error("check network type %s fail" % network_type)
            return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                         ErrorMsg.ERR_MSG_UNSUPPORTED_NETWORK_TYPE, network_type)



