import context
from log.logger import logger
import constants as const
import db.constants as dbconst
import dispatch_resource.desktop_common as DeskComm

def set_task_security_policy_apply(security_policy_id, is_apply):

    ctx = context.instance()

    if not ctx.pg.batch_update(dbconst.TB_SECURITY_POLICY, {security_policy_id: {"is_apply": is_apply}}):
        return -1

    return 0

def set_task_policy_group_apply(policy_group_id, is_apply, resource_ids=None):

    ctx = context.instance()
    update_resource = {}
    if not resource_ids:
        resource_ids = []

    for resource_id in resource_ids:
        conditions = dict(
                          policy_group_id=policy_group_id, 
                          resource_id=resource_id)

        update_resource = {"is_apply": is_apply}
        if not ctx.pg.base_update(dbconst.TB_POLICY_GROUP_RESOURCE, conditions, update_resource):
            logger.error("set task policy group apply fail %s" % update_resource)
            return -1
    
    ret = ctx.pgm.get_policy_group_policy(policy_group_id)
    if ret:
        policy_ids = ret.keys()
        ret = ctx.pgm.get_security_policys(policy_ids, 1)
        if ret:
            update_policy = {}
            for policy_id in ret.keys():
                update_policy[policy_id] = {"is_apply": is_apply}
            if not ctx.pg.batch_update(dbconst.TB_SECURITY_POLICY, update_policy):
                logger.error("set task policy group apply fail %s" % update_policy)
                return -1

    if not ctx.pg.batch_update(dbconst.TB_POLICY_GROUP, {policy_group_id: {"is_apply": is_apply}}):
        logger.error("set task policy group apply fail %s" % policy_group_id)
        return -1

    return 0

def apply_security_policy(sender, security_group_id, resource_ids):
    
    ctx = context.instance()
    
    if not resource_ids:
        resource_ids = []
    
    instance_ids = []
    if resource_ids:
        desktop_instance = ctx.pgm.get_desktop_instance(resource_ids)
        if not desktop_instance:
            return 0

        instance_ids = desktop_instance.values()
        instances = DeskComm.get_instances(sender, instance_ids, status=[const.INST_STATUS_RUN, const.INST_STATUS_SUSP, const.INST_STATUS_STOP])
        if not instances:
            return 0
        instance_ids = instances.keys()
    
    if len(instance_ids) <= const.APPLY_SECURITY_INSTANCE_COUNT:
        ret = ctx.res.resource_apply_security_group(sender["zone"], security_group_id, instance_ids)
        if not ret:
            logger.error("apply security policy fail %s" % ret)
            return -1
    else:
        hyper_instances = {}
        for instance_id, instance in instances.items():
            host_machine = instance["host_machine"]
            if host_machine not in hyper_instances:
                hyper_instances[host_machine] = []
            
            hyper_instances[host_machine].append(instance_id)
        
        for _, _instance_ids in hyper_instances.items():
            ret = ctx.res.resource_apply_security_group(sender["zone"], security_group_id, _instance_ids)
            if not ret:
                logger.error("apply security policy fail %s" % ret)
                return -1

    return 0

def get_security_group_resource(sender, security_group_id):
    
    ctx = context.instance()
    ret = ctx.res.resource_describe_security_groups(sender["zone"], security_group_id)
    if not ret:
        logger.error("resource_describe_security_group fail %s" % security_group_id)
        return None

    security_group = ret[security_group_id]
    resources = security_group["resources"]
    resource_ids = []
    for resource in resources:
        
        resource_id = resource["resource_id"]
        resource_type = resource["resource_type"]
        if resource_type != "instance":
            continue
        resource_ids.append(resource_id)
    
    desktop_resource = ctx.pgm.get_instance_desktop(resource_ids)
    if not desktop_resource:
        return None

    return desktop_resource.values()

def check_resource_remove_security_group(sender, policy_group_id):
    
    ctx = context.instance()
    remove_resources = ctx.pgm.get_policy_group_resource(policy_group_id, is_apply=const.APPLY_TYPE_REMOVE)
    if not remove_resources:
        return 0
    
    desktop_ids = remove_resources.keys()
    
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        return 0

    instance_ids = desktop_instance.values()
    
    if len(instance_ids) <= const.APPLY_SECURITY_INSTANCE_COUNT:
        ret = ctx.res.resource_remove_security_group(sender["zone"], instance_ids)
        if not ret:
            logger.error("remove security group fail %s" % instance_ids)
            return -1
    else:
        instances = DeskComm.get_instances(sender, instance_ids)
        hyper_instances = {}
        for instance_id, instance in instances.items():
            host_machine = instance["host_machine"]
            if host_machine not in hyper_instances:
                hyper_instances[host_machine] = []
            
            hyper_instances[host_machine].append(instance_id)
        
        for _, instance_ids in hyper_instances.itemms():
            ret = ctx.res.resource_remove_security_group(sender["zone"], instance_ids)
            if not ret:
                logger.error("resource remove security group fail %s" % instance_ids)
                continue

    ret = ctx.pgm.get_policy_group_resource(resource_ids=desktop_ids)
    if ret:
        ctx.pg.base_delete(dbconst.TB_POLICY_GROUP_RESOURCE, {"resource_id": ret.keys()})
    
    ret = set_task_policy_group_apply(policy_group_id, 0)
    if ret < 0:
        logger.error("set policy group apply fail %s" % policy_group_id)
        return -1
    
    return 0

def check_resource_apply_security_group(sender, policy_group_id):
    
    ctx = context.instance()

    apply_resources = ctx.pgm.get_policy_group_resource(policy_group_id, is_apply=const.APPLY_TYPE_APPLY)
    if not apply_resources:
        return 0
    
    desktop_ids = apply_resources.keys()
    
    security_group_id = ctx.pgm.get_base_policy(policy_group_id)
    if not security_group_id:
        logger.error("policy group no found base policy id %s" % policy_group_id)
        return -1

    ret = apply_security_policy(sender, security_group_id, desktop_ids)
    if ret < 0:
        logger.error("apply security policy fail %s, %s" % (policy_group_id, desktop_ids))
        return -1

    ret = set_task_policy_group_apply(policy_group_id, 0, desktop_ids)
    if ret < 0:
        logger.error("set policy group apply fail %s" % policy_group_id)
        return -1

    return 0

def check_secuirty_policy_apply(sender, policy_group_id):
    
    ctx = context.instance()
    
    policy_group = ctx.pgm.get_policy_group(policy_group_id)
    if not policy_group:
        logger.error("no found policy group %s" % policy_group_id)
        return -1
    
    # apply security group
    base_policy_id = ctx.pgm.get_base_policy(policy_group_id)

    ret = ctx.pgm.get_security_policy(base_policy_id)
    if not ret:
        return 0
    
    security_group = ret
    if security_group["is_apply"] == 0 and policy_group["is_apply"] == 0:
        return 0
    
    resources = ctx.pgm.get_policy_group_resource(policy_group_id)
    if not resources:
        resources = {}
    
    resource_ids = resources.keys()
    ret = apply_security_policy(sender, base_policy_id, resource_ids)
    if ret < 0:
        logger.error("apply security policy fail %s" % base_policy_id)
        return -1

    ret = set_task_security_policy_apply(base_policy_id, 0)
    if ret < 0:
        logger.error("set policy group apply fail %s" % base_policy_id)
        return -1
    
    return 0

def task_apply_security_rule_set(sender, security_rule_set_id):

    ctx = context.instance()
    ret = ctx.res.resource_describe_security_groups(sender["zone"], security_rule_set_id, const.UUID_TYPE_SECURITY_POLICY_SGRS)
    if not ret:
        logger.error(" resource no found security rule set %s" % security_rule_set_id)
        return -1
    security_rule_set = ret[security_rule_set_id]
    
    is_apply = security_rule_set["is_applied"]
    if is_apply == 0:
        ret = ctx.res.resource_apply_security_group_ruleset(sender["zone"], security_rule_set_id)
        if not ret:
            logger.error("apply security policy rule set fail %s" % security_rule_set_id)
            return -1

    ret = set_task_security_policy_apply(security_rule_set_id, 0)
    if ret < 0:
        logger.error("set policy group apply fail %s" % security_rule_set_id)
        return -1
    
    return 0

def task_apply_security_policy(sender, policy_group_id):

    # resource leave security group
    ctx = context.instance()

    ret = ctx.pgm.get_policy_group(policy_group_id)
    if not ret:
        logger.error("task no found security policy %s" % policy_group_id)
        return -1
    policy_group = ret

    if "zone" in sender:
        sender["zone"] = policy_group["zone"]
    
    ret = check_resource_remove_security_group(sender, policy_group_id)
    if ret < 0:
        logger.error("resource remove security group fail %s" % policy_group_id)
        return -1

    ret = check_resource_apply_security_group(sender, policy_group_id)
    if ret < 0:
        logger.error("resource apply security group fail %s" % policy_group_id)
        return -1

    # apply security group
    ret = check_secuirty_policy_apply(sender, policy_group_id)
    if ret < 0:
        logger.error("check resource apply security group fail %s" % policy_group_id)
        return -1

    set_task_policy_group_apply(policy_group_id, 0)

    return 0

def task_apply_security_ipset(sender, security_ipset_id):
    
    ctx = context.instance()

    ret = ctx.res.resource_describe_security_group_ipsets(sender["zone"], security_ipset_id)
    if ret:
        ret = ctx.res.resource_apply_security_ipset(sender["zone"], security_ipset_id)
        if not ret:
            logger.error("apply security policy fail %s" % ret)
            return -1

    if not ctx.pg.batch_update(dbconst.TB_SECURITY_IPSET, {security_ipset_id: {"is_apply": 0}}):
        return -1

    return 0

def set_desktop_to_policy_resource(sender, desktop_id, policy_group_id, is_apply=None):
    
    ctx = context.instance()
    
    existed_resources = {}
    ret = ctx.pgm.get_policy_group_resource(resource_ids=desktop_id, policy_group_type=const.POLICY_TYPE_SECURITY)
    if not ret:
        existed_resources = {}
        
    policy_resource = existed_resources.get(desktop_id)
    if policy_resource and policy_resource["policy_group_id"] != policy_group_id:
        conditions = {"resource_id": desktop_id, "policy_group_type": const.POLICY_TYPE_SECURITY}
        update_info = {"policy_group_id": policy_group_id, "is_apply": is_apply if is_apply else 0}
        if not ctx.pg.base_update(dbconst.TB_POLICY_GROUP_RESOURCE, conditions, update_info):
            logger.error("update resource is_apply to policy group insert db fail %s, %s" % (update_info, conditions))
            return -1

    if not policy_resource:
        update_info = {"policy_group_id": policy_group_id,
                       "resource_id": desktop_id,
                       "status": const.POLICY_STATUS_ENABLED,
                       "policy_group_type": const.POLICY_TYPE_SECURITY,
                       "is_apply": is_apply if is_apply else 0
                       }

        if not ctx.pg.batch_insert(dbconst.TB_POLICY_GROUP_RESOURCE, {desktop_id: update_info}):
            return -1

    if is_apply:
        task_apply_security_policy(sender, policy_group_id)
    
    return 0

def check_desktop_security_group(desktop_id=None, delivery_group_id = None, desktop_group_id=None):
    
    ctx = context.instance()
    
    sec_policy_id = None
    desktop = {}
    if desktop_id:
        ret = ctx.pgm.get_desktop(desktop_id)
        if not ret:
            logger.error("check desktop security group no found desktop %s" % desktop_id)
            return None
        desktop = ret

        ret = ctx.pgm.get_policy_group_resource(resource_ids=desktop_id, policy_group_type=const.POLICY_TYPE_SECURITY)
        if ret:
            policy_resource = ret[desktop_id]
            sec_policy_id = policy_resource["policy_group_id"]
            return sec_policy_id

    if not delivery_group_id:
        delivery_group_id = desktop.get("delivery_group_id")
    
    if not desktop_group_id:
        desktop_group_id = desktop.get("desktop_group_id")
    
    if delivery_group_id:
        ret = ctx.pgm.get_resource_group_policy(delivery_group_id, policy_group_type=const.POLICY_TYPE_SECURITY)
        if ret:
            sec_policy_id = ret[const.POLICY_TYPE_SECURITY]
            return sec_policy_id
    
    if desktop_group_id:
        ret = ctx.pgm.get_resource_group_policy(desktop_group_id, policy_group_type=const.POLICY_TYPE_SECURITY)
        if ret:
            sec_policy_id = ret[const.POLICY_TYPE_SECURITY]
            return sec_policy_id
    
    return sec_policy_id
