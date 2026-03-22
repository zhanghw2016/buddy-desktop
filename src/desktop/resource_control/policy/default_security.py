from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from common import (
    is_citrix_platform
)
from utils.misc import get_current_time
import resource_control.policy.security_policy as SecurityPolicy
import resource_control.policy.policy_group as PolicyGroup

def load_default_security_policy(sender, policy_group_id):

    zone_id = sender["zone"]
    ctx = context.instance()
    ret = ctx.pgm.get_policy_group(policy_group_id)
    if not ret:
        return None

    policy_group = ret

    ret = ctx.pgm.get_default_security_policy(zone_id)
    if not ret:
        return None

    security_policy = ret
    security_policy_id = security_policy["security_policy_id"]
    sender = {"zone": zone_id}
    ret = PolicyGroup.add_policy_to_policy_group(sender, policy_group, security_policy_id)
    if isinstance(ret, Error):
        return ret

    return None

def init_default_policy_group(zone_id):
    
    ctx = context.instance()
    
    if not ctx.enable_default_policy:
        return None
    
    zone = ctx.pgm.get_zone(zone_id, extras=[])
    if not zone:
        return None
    
    if zone["status"] != const.ZONE_STATUS_ACTIVE:
        return None

    ret = ctx.pgm.get_default_policy_group(zone_id)
    if ret:
        return ret

    ret = register_default_policy_group(zone_id)
    if isinstance(ret, Error) or not ret:
        return ret

    policy_group = ret
   
    # init security policy
    ret = register_default_security_policy(zone_id)
    if isinstance(ret, Error) or not ret:
        return ret
    security_policy = ret
    
    security_policy_id = security_policy["security_policy_id"]
    sender = {"zone": zone_id}

    ret = PolicyGroup.add_policy_to_policy_group(sender, policy_group, security_policy_id)
    if isinstance(ret, Error):
        return ret
    
    policy_group_id = policy_group["policy_group_id"]

    ret = SecurityPolicy.apply_security_policy(sender, security_policy_id)
    if isinstance(ret, Error):
        return ret

    ret = PolicyGroup.apply_policy_group(sender, policy_group_id)
    if isinstance(ret, Error):
        return ret

    return policy_group

def register_default_policy_group(zone_id):
    
    ctx = context.instance()
    policy_info = {
                    "policy_group_type": const.POLICY_TYPE_SECURITY,
                    "policy_group_name": "DefaultPolicyGroup-%s" % zone_id,
                    "description": '',
                    "is_default": 1
                    }

    sender = {"zone": zone_id}
    ret = PolicyGroup.register_policy_group(sender, policy_info)
    if isinstance(ret, Error):
        return ret

    ret = ctx.pgm.get_default_policy_group(zone_id)
    if not ret:
        logger.error("init default policy group fail %s" % zone_id)
        return None

    return ret

def register_default_security_policy(zone_id):
    
    ctx = context.instance()
  
    sender = {"zone": zone_id}
    security_policy_name = "DefaultPolicy-%s" % zone_id
    
    ret = ctx.pgm.get_default_security_policy(zone_id)
    if ret:
        return ret

    ret = SecurityPolicy.create_security_poilcy(sender, security_policy_name)
    if isinstance(ret, Error):
        return ret

    security_policy_id = ret

    if not ctx.pg.batch_update(dbconst.TB_SECURITY_POLICY, {security_policy_id: {"is_default" : 1}}):
        logger.error("update resource is_apply to policy group insert db fail %s" % security_policy_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = build_default_security_rules(sender)
    if isinstance(ret, Error) or not ret:
        logger.error("build default security rule fail %s" % zone_id)
        SecurityPolicy.delete_security_policys(sender, security_policy_id)
        return ret

    security_rules = ret

    security_policy = ctx.pgm.get_security_policy(security_policy_id)
    if not security_policy:
        logger.error("no found security policy %s" % security_policy_id)
        return None

    ret = SecurityPolicy.create_security_rules(sender["zone"], security_policy, security_rules)
    if isinstance(ret, Error):
        SecurityPolicy.delete_security_policys(sender, security_policy_id)
        return ret

    return security_policy

def build_default_security_rules(sender):
    
    ret = register_default_security_ipset(sender)
    if isinstance(ret, Error) or not ret:
        return ret

    default_ipsets = ret

    security_rules = []
    for direction in [0, 1]:
        for ipset_config, ipset_id in default_ipsets.items():
            rule_info = {
                "security_rule_name": const.DEFAULT_IPSET_RULE_NAME,
                "priority": 1,
                "action": "accept",
                }
            if ipset_config in const.IPSET_TCP:
                protocol = "tcp"
            else:
                protocol = "udp"
            rule_info["protocol"] = protocol
            rule_info["val1"] = ipset_id
            rule_info["direction"] = direction
            security_rules.append(rule_info)

    return security_rules

def get_default_ipset_config(sender):
    
    ctx = context.instance()
    zone_id = sender["zone"]
    
    support_ipset_list = []
    
    platform = const.PLATFROM_QINGDESKTOP
    if is_citrix_platform(ctx, zone_id):
        platform = const.PLATFROM_CITRIX
        
    # get platfrom config
    platfrom_ipset = const.IPSET_PLATFORM_PORT_CONFIG.get(platform)
    if platfrom_ipset:
        support_ipset_list.extend(platfrom_ipset)
    
    # get auth service config
    auth_service = ctx.pgm.get_zone_auth(zone_id)
    if not auth_service:
        return support_ipset_list
    
    auth_service_type = auth_service["auth_service_type"]
    platfrom_ipset = const.IPSET_PLATFORM_PORT_CONFIG.get(auth_service_type)
    if platfrom_ipset:
        support_ipset_list.extend(platfrom_ipset)
    
    return support_ipset_list

def register_default_security_ipset(sender):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_security_ipsets(is_default=1, zone_id=sender["zone"])
    if ret:
        ipset_configs = {}
        for ipset_id, ipset in ret.items():
            ipset_config_key = ipset["ipset_config_key"]
            ipset_configs[ipset_config_key] = ipset_id

        return ipset_configs

    ipset_configs = get_default_ipset_config(sender)
    if not ipset_configs:
        logger.error("no found default ipset config")
        return None

    ipset_vals = ctx.pgm.get_default_security_ipset_port(ipset_configs)
    if not ipset_vals:
        logger.error(" no found defualt ipset port %s" % ipset_configs)
        return None

    ipset_ids = {}
    ipset_type = const.IPSET_TYPE_PORT
    for ipset_config in ipset_configs:
        security_ipset_name = const.DEFAULT_IPSET_NAMES.get(ipset_config)
        if not security_ipset_name:
            security_ipset_name = const.DEFAULT_IPSET_NAME
        
        val = ipset_vals.get(ipset_config)
        if not val:
            continue

        ret = ctx.res.resource_create_security_group_ipset(sender["zone"], ipset_type, val, security_ipset_name)
        if not ret:
            logger.error("resource create default security ipset fail %s, %s, %s" % (security_ipset_name, ipset_type, val))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED, "ipset")

        security_ipset_id = ret
        ipset_ids[ipset_config] = security_ipset_id
    
        security_ipset_info = dict(
                                  security_ipset_id = security_ipset_id,
                                  ipset_type = ipset_type,
                                  security_ipset_name = security_ipset_name if security_ipset_name else '',
                                  val = val,
                                  description = '',
                                  create_time = get_current_time(),
                                  is_apply = 0,
                                  is_default = 1,
                                  ipset_config_key = ipset_config,
                                  zone = sender["zone"]                              
                                  )
        # register desktop group
        if not ctx.pg.insert(dbconst.TB_SECURITY_IPSET, security_ipset_info):
            logger.error("insert newly created security ipset for [%s] to db failed" % (security_ipset_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return ipset_ids