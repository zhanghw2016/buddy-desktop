
import db.constants as dbconst
class PolicyGroupPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_policy_groups(self, policy_group_ids=None, extras=[dbconst.TB_POLICY_GROUP_RESOURCE,
                                                               dbconst.TB_POLICY_GROUP_POLICY
                                                               ]):

        conditions = {}
        
        if policy_group_ids:
            conditions["policy_group_id"] = policy_group_ids

        policy_group_set = self.pg.base_get(dbconst.TB_POLICY_GROUP, conditions)
        if not policy_group_set:
            return None

        policy_groups = {}
        for policy_group in policy_group_set:
            policy_group_id = policy_group["policy_group_id"]
            policy_groups[policy_group_id] = policy_group
        
        if dbconst.TB_POLICY_GROUP_RESOURCE in extras:
            
            policy_group_resource_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_RESOURCE, conditions)
            if policy_group_resource_set:

                for pg_resource in policy_group_resource_set:
                    policy_group_id = pg_resource["policy_group_id"]
                    if policy_group_id not in policy_groups:
                        continue
                    
                    policy_group = policy_groups[policy_group_id]
                    
                    if "resources" not in policy_group:                   
                        policy_group["resources"] = []
                    
                    policy_group["resources"].append(pg_resource)
                    
        if dbconst.TB_POLICY_GROUP_POLICY:
            
            policy_group_policy_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_POLICY, conditions)
            if policy_group_policy_set:
                
                for pg_policy in policy_group_policy_set:

                    policy_group_id = pg_policy["policy_group_id"]
                    if policy_group_id not in policy_groups:
                        continue
                    
                    policy_group = policy_groups[policy_group_id]
                    
                    if "policys" not in policy_group:                   
                        policy_group["policys"] = []
                    
                    policy_group["policys"].append(pg_policy)
                    
        return policy_groups
    
    def get_policy_group(self, policy_group_id):
        
        conditions = {"policy_group_id": policy_group_id}

        policy_group_set = self.pg.base_get(dbconst.TB_POLICY_GROUP, conditions)
        if not policy_group_set:
            return None

        return policy_group_set[0]

    def get_policy_group_policy(self, policy_group_id, policy_ids=None, ignore_base=True):

        conditions = {"policy_group_id": policy_group_id}
        if policy_ids:
            conditions["policy_id"] = policy_ids

        policy_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_POLICY, conditions)
        if not policy_set:
            return None
        policys = {}
        for policy in policy_set:
            policy_id = policy["policy_id"]
            if ignore_base and policy["is_base"]:
                continue
            policys[policy_id] = policy
        
        return policys

    def get_base_policy(self, policy_group_id):

        conditions = {"policy_group_id": policy_group_id, "is_base": 1}
        policy_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_POLICY, conditions)
        if not policy_set:
            return None

        base_policy = policy_set[0]

        return base_policy["policy_id"]

    def get_policy_group_resource(self, policy_group_id=None, resource_ids=None, is_apply=None, policy_group_type=None):

        conditions = {}
        if policy_group_id:
            conditions["policy_group_id"] = policy_group_id
        
        if resource_ids:
            conditions["resource_id"] = resource_ids
        
        if is_apply:
            conditions["is_apply"] = is_apply
        
        if policy_group_type:
            conditions["policy_group_type"] = policy_group_type
        
        resource_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_RESOURCE, conditions)
        if not resource_set:
            return None

        resources = {}
        for resource in resource_set:
            resource_id = resource["resource_id"]
            resources[resource_id] = resource

        return resources

    def get_group_resource(self, resource_ids, is_lock=None):

        conditions = {"resource_id": resource_ids}
        if is_lock is not None:
            conditions["is_lock"] = is_lock
        
        resource_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_RESOURCE, conditions)
        if not resource_set:
            return None

        group_resources = {}
        for resource in resource_set:
            policy_group_id = resource["policy_group_id"]
            resource_id = resource["resource_id"]
            if policy_group_id not in group_resources:
                group_resources[policy_group_id] = []
            group_resources[policy_group_id].append(resource_id)

        return group_resources

    def get_group_resources(self, resource_ids, is_lock=None):
        
        if not resource_ids:
            return None
        
        conditions = {"resource_id": resource_ids}
        if is_lock is not None:
            conditions["is_lock"] = is_lock
        
        resource_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_RESOURCE, conditions)
        if not resource_set:
            return None

        group_resources = []
        for resource in resource_set:
            resource_id = resource["resource_id"]
            group_resources.append(resource_id)

        return group_resources

    def get_resource_policy(self, resource_ids):
        
        if not resource_ids:
            return None
        
        conditions = {"resource_id": resource_ids}
        resource_set = self.pg.base_get(dbconst.TB_POLICY_GROUP_RESOURCE, conditions)
        if not resource_set:
            return None

        policy_resources = {}
        for resource in resource_set:
            resource_id = resource["resource_id"]
            policy_resources[resource_id] = resource

        return policy_resources

    def get_resource_group_policy(self, resource_group_id=None, policy_group_id=None, policy_group_type=None):
        
        conditions = {}
        if resource_group_id:
            conditions["resource_group_id"] = resource_group_id
        
        if policy_group_id:
            conditions["policy_group_id"] = policy_group_id

        policy_set = self.pg.base_get(dbconst.TB_POLICY_RESOURCE_GROUP, conditions)
        if not policy_set:
            return None

        resource_group_policy = {}
        for policy in policy_set:
            policy_group_id = policy["policy_group_id"]
            policy_group_type = policy["policy_group_type"]
            
            resource_group_policy[policy_group_type] = policy_group_id

        return resource_group_policy

    def get_policy_resource_group(self, policy_group_id=None):
        
        conditions = {}
        if policy_group_id:
            conditions["policy_group_id"] = policy_group_id

        policy_set = self.pg.base_get(dbconst.TB_POLICY_RESOURCE_GROUP, conditions)
        if not policy_set:
            return None

        resource_group_policy = {}
        for policy in policy_set:
            resource_group_id = policy["resource_group_id"]
            
            resource_group_policy[resource_group_id] = policy

        return resource_group_policy
    
    def get_policy_resource_groups(self, resource_group_type=None, policy_group_id=None):
        
        conditions = {}
        if policy_group_id:
            conditions["policy_group_id"] = policy_group_id
        
        if resource_group_type:
            conditions["resource_group_type"] = resource_group_type

        policy_set = self.pg.base_get(dbconst.TB_POLICY_RESOURCE_GROUP, conditions)
        if not policy_set:
            return None

        resource_group_policy = {}
        for policy in policy_set:
            resource_group_id = policy["resource_group_id"]
            
            resource_group_policy[resource_group_id] = policy

        return resource_group_policy

