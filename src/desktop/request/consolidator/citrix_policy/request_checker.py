
from constants import (
    ACTION_CREATE_CITRIX_POLICY,
    ACTION_CONFIG_CITRIX_POLICY_ITEM ,
    ACTION_DESCRIBE_CITRIX_POLICY ,
    ACTION_DESCRIBE_CITRIX_POLICY_ITEM ,
    ACTION_DESCRIBE_CITRIX_POLICY_CONFIG ,
    ACTION_DELETE_CITRIX_POLICY,
    ACTION_MODIFY_CITRIX_POLICY, 
    ACTION_RENAME_CITRIX_POLICY,
    ACTION_REFRESH_CITRIX_POLICY,  
    ACTION_SET_CITRIX_POLICY_PRIORITY,
    ACTION_DESCRIBE_CITRIX_POLICY_FILTER,
    ACTION_ADD_CITRIX_POLICY_FILTER,
    ACTION_MODIFY_CITRIX_POLICY_FILTER,
    ACTION_DELETE_CITRIX_POLICY_FILTER,     

)

from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import CitrixPolicyRequestBuilder

class CitrixPolicyRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(CitrixPolicyRequestChecker, self).__init__(sender, checker)
        self.builder = CitrixPolicyRequestBuilder(sender)

        self.handler_map = {
            ACTION_CREATE_CITRIX_POLICY: self.create_citrix_policy,
            ACTION_CONFIG_CITRIX_POLICY_ITEM: self.config_citrix_policy_item,
            ACTION_DESCRIBE_CITRIX_POLICY: self.describe_citrix_policy,
            ACTION_DESCRIBE_CITRIX_POLICY_ITEM: self.describe_citrix_policy_item,
            ACTION_DESCRIBE_CITRIX_POLICY_CONFIG: self.describe_citrix_policy_item_config,
            ACTION_DELETE_CITRIX_POLICY: self.delete_citrix_policy,
            ACTION_MODIFY_CITRIX_POLICY: self.modify_citrix_policy,
            ACTION_RENAME_CITRIX_POLICY: self.rename_citrix_policy, 
            ACTION_REFRESH_CITRIX_POLICY: self.refresh_citrix_policy,                    
            ACTION_SET_CITRIX_POLICY_PRIORITY: self.set_citrix_policy_priority,
            ACTION_DESCRIBE_CITRIX_POLICY_FILTER: self.describe_citrix_policy_filter,
            ACTION_ADD_CITRIX_POLICY_FILTER: self.add_citrix_policy_filter,
            ACTION_MODIFY_CITRIX_POLICY_FILTER: self.modify_citrix_policy_filter,
            ACTION_DELETE_CITRIX_POLICY_FILTER: self.delete_citrix_policy_filter,            
            }
    

    def create_citrix_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_name"],
                                  str_params=["zone", "citrix_policy_name", "description"],
                                  integer_params=["policy_state"]
                                  ):
            return None

        return self.builder.create_citrix_policy(**directive)

    def config_citrix_policy_item(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_name","citrix_policy_id","policy_items"],
                                  str_params=["zone", "citrix_policy_name", "citrix_policy_id"],
                                  list_params=[],
                                  json_params=["policy_items"]
                                  ):
            return None

        return self.builder.config_citrix_policy_item(**directive)


    def describe_citrix_policy_item_config(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "col1", "col2", "col3", "search_word","pol_id"],
                                  integer_params=[]
                                  
                                  ):
            return None

        return self.builder.describe_citrix_policy_item_config(**directive)

    def describe_citrix_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone","search_word","citrix_policy_names","citrix_policy_ids"],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None
        return self.builder.describe_citrix_policy(**directive)

    def describe_citrix_policy_item(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_id"],
                                  str_params=["zone", "citrix_policy_id"]):
            return None

        return self.builder.describe_citrix_policy_item(**directive)

    def delete_citrix_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_name","citrix_policy_id"],
                                  str_params=["zone", "citrix_policy_name","citrix_policy_id"],
                                  list_params=[]
                                  ):
            return None

        return self.builder.delete_citrix_policy(**directive)
    
    def modify_citrix_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_name","citrix_policy_id"],
                                  str_params=["zone", "citrix_policy_name","citrix_policy_id", "description"],
                                  integer_params=["policy_state"],
                                  list_params=[]
                                  ):
            return None
        
        return self.builder.modify_citrix_policy(**directive)    

    def rename_citrix_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_id","citrix_policy_old_name","citrix_policy_new_name"],
                                  str_params=["zone", "citrix_policy_id","citrix_policy_old_name","citrix_policy_new_name"],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None
        
        return self.builder.rename_citrix_policy(**directive)    


    def refresh_citrix_policy(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "sync_type"],
                                  str_params=["zone", "sync_type","citrix_policy_name","citrix_policy_id"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.refresh_citrix_policy(**directive)
      
    def set_citrix_policy_priority(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_name","citrix_policy_id","policy_priority"],
                                  str_params=["zone", "citrix_policy_name","citrix_policy_id","policy_priority"],
                                  list_params=[]
                                  ):
            return None

        return self.builder.set_citrix_policy_priority(**directive)
    

    def add_citrix_policy_filter(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_name","citrix_policy_id","policy_filters"],
                                  str_params=["zone", "citrix_policy_name", "citrix_policy_id"],
                                  list_params=[],
                                  json_params=["policy_filters"]
                                  ):
            return None

        return self.builder.add_citrix_policy_filter(**directive)

    def modify_citrix_policy_filter(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_name","citrix_policy_id","policy_filters"],
                                  str_params=["zone", "citrix_policy_name", "citrix_policy_id"],
                                  list_params=[],
                                  json_params=["policy_filters"]
                                  ):
            return None

        return self.builder.modify_citrix_policy_filter(**directive)



    def describe_citrix_policy_filter(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_id", "citrix_policy_name"],
                                  str_params=["zone", "citrix_policy_id", "citrix_policy_name"]):
            return None

        return self.builder.describe_citrix_policy_filter(**directive)

    def delete_citrix_policy_filter(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "citrix_policy_name","citrix_policy_id","policy_filters"],
                                  str_params=["zone", "citrix_policy_name", "citrix_policy_id"],
                                  list_params=[],
                                  json_params=["policy_filters"]
                                  ):
            return None

        return self.builder.delete_citrix_policy_filter(**directive)


    
