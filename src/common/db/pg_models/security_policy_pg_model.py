
import db.constants as dbconst
import constants as const

class SecurityPolicyPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_security_policys(self, security_policy_ids=None, is_apply=None, security_policy_type=None, policy_mode=None):

        conditions = {}
        
        if security_policy_ids:
            conditions["security_policy_id"] = security_policy_ids
        
        if security_policy_type:
            conditions["security_policy_type"] = security_policy_type
        
        if is_apply is not None:
            conditions["is_apply"] = is_apply
        
        if policy_mode:
            conditions["policy_mode"] = policy_mode

        security_policy_set = self.pg.base_get(dbconst.TB_SECURITY_POLICY, conditions)
        if not security_policy_set:
            return None

        security_policys = {}
        for security_policy in security_policy_set:
            security_policy_id = security_policy["security_policy_id"]
            
            security_policys[security_policy_id] = security_policy
            
        return security_policys

    def get_security_policy(self, security_policy_id, is_apply=None):

        conditions = {}
        conditions["security_policy_id"] = security_policy_id

        if is_apply is not None:
            conditions["is_apply"] = is_apply

        security_policy_set = self.pg.base_get(dbconst.TB_SECURITY_POLICY, conditions)
        if not security_policy_set:
            return None
            
        return security_policy_set[0]

    def get_default_security_policy(self, zone_id):

        conditions = {"zone": zone_id, "is_default": 1}

        security_policy_set = self.pg.base_get(dbconst.TB_SECURITY_POLICY, conditions)
        if not security_policy_set:
            return None

        return security_policy_set[0]

    def get_share_security_policys(self, security_policy_id, zone_id=None):

        conditions = {"share_policy_id": security_policy_id, "security_policy_type": const.SEC_POLICY_TYPE_SAHRE}
        if zone_id:
            conditions["zone"] = zone_id
        
        security_policy_set = self.pg.base_get(dbconst.TB_SECURITY_POLICY, conditions)
        if not security_policy_set:
            return None
        
        slave_policys = {}
        for security_policy in security_policy_set:
            
            security_policy_id = security_policy["security_policy_id"]
            slave_policys[security_policy_id] = security_policy
    
        return slave_policys

    def get_share_security_rules(self, security_rule_ids, security_policy_id):

        conditions = {"share_rule_id": security_rule_ids, "security_rule_type": const.SEC_POLICY_TYPE_SAHRE, "security_policy_id": security_policy_id}
        
        security_rule_set = self.pg.base_get(dbconst.TB_SECURITY_RULE, conditions)
        if not security_rule_set:
            return None
        
        slave_rules = {}
        for security_rule in security_rule_set:
            
            security_rule_id = security_rule["security_rule_id"]
            slave_rules[security_rule_id] = security_rule
    
        return slave_rules

    def get_default_policy_group(self, zone_id, policy_group_type=const.POLICY_TYPE_SECURITY):

        conditions = {"zone": zone_id, "is_default": 1, "policy_group_type": policy_group_type}

        policy_group_set = self.pg.base_get(dbconst.TB_POLICY_GROUP, conditions)
        if not policy_group_set:
            return None

        return policy_group_set[0]
    
    def get_security_rules(self, security_rule_ids=None, security_policy_ids=None):
        
        conditions = {}
        if security_rule_ids:
            conditions["security_rule_id"] = security_rule_ids
        
        if security_policy_ids:
            conditions["security_policy_id"] = security_policy_ids
        
        security_rule_set = self.pg.base_get(dbconst.TB_SECURITY_RULE, conditions)
        if not security_rule_set:
            return None
            
        security_rules = {}
        for security_rule in security_rule_set:
            security_rule_id = security_rule["security_rule_id"]
            security_rules[security_rule_id] = security_rule

        return security_rules

    def get_security_policy_groups(self, security_policy_ids):

        conditions = {}
        conditions["policy_id"] = security_policy_ids
        policy_group_policy_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_POLICY, conditions)
        if not policy_group_policy_set:
            return None

        policy_group_ids = []
        for _policy in policy_group_policy_set:
            policy_group_id = _policy["policy_group_id"]
            if policy_group_id in policy_group_ids:
                continue
                
            policy_group_ids.append(policy_group_id)
        
        policy_groups = {}
        conditions = {"policy_group_id": policy_group_ids}
        policy_group_set = self.pg.base_get(dbconst.TB_POLICY_GROUP, conditions)
        if not policy_group_set:
            return None
        
        for policy_group in policy_group_set:
            policy_group_id = policy_group["policy_group_id"]
            policy_groups[policy_group_id] = policy_group
            
        return policy_groups

    def get_default_security_ipsets(self, zone_id):
        
        conditions = {"zone": zone_id, "is_default": 1}
        
        security_ipset_set = self.pg.base_get(dbconst.TB_SECURITY_IPSET, conditions)
        if not security_ipset_set:
            return None

        security_ipsets = {}
        for security_ipset in security_ipset_set:
            ipset_config_key = security_ipset["ipset_config_key"]
            security_ipsets[ipset_config_key] = security_ipset

        return security_ipsets

    def get_security_ipsets(self, security_ipset_ids=None, is_apply=None, is_default=None, zone_id=None):
        
        conditions = {}
        if security_ipset_ids:
            conditions["security_ipset_id"] = security_ipset_ids
        
        if is_apply is not None:
            conditions["is_apply"] = is_apply
        
        if is_default is not None:
            conditions["is_default"] = is_default
        
        if zone_id is not None:
            conditions["zone"] = zone_id
        
        security_ipset_set = self.pg.base_get(dbconst.TB_SECURITY_IPSET, conditions)
        if not security_ipset_set:
            return None

        security_ipsets = {}
        for security_ipset in security_ipset_set:
            security_ipset_id = security_ipset["security_ipset_id"]
            security_ipsets[security_ipset_id] = security_ipset

        return security_ipsets
    
    def get_security_policy_by_ipset(self, ipset_ids):
        
        if not isinstance(ipset_ids, list):
            ipset_ids = [ipset_ids]
        
        sql = "select security_policy_id, val1, val3 from security_rule where val1 " \
          "in %%s  or val3 in %%s limit %s" % (const.MAX_LIMIT_PARAM)

        ipset_set = self.pg.execute_sql(sql, [tuple(ipset_ids),tuple(ipset_ids)])
        if not ipset_set:
            return None
        
        security_policy_ids = []
        for ipset in ipset_set:
            security_policy_id = ipset["security_policy_id"]
            if security_policy_id not in security_policy_ids:
                security_policy_ids.append(security_policy_id)
        
        return security_policy_ids
