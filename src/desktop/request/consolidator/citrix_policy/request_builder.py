
from constants import (
    ACTION_CONFIG_CITRIX_POLICY_ITEM ,
    ACTION_DESCRIBE_CITRIX_POLICY_ITEM ,
    ACTION_DESCRIBE_CITRIX_POLICY_CONFIG ,
    ACTION_DESCRIBE_CITRIX_POLICY ,
    ACTION_CREATE_CITRIX_POLICY,
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
from request.consolidator.base.base_request_builder import BaseRequestBuilder

class CitrixPolicyRequestBuilder(BaseRequestBuilder):
    ''' API request builder '''

    def create_citrix_policy(self, 
                                 zone,
                                 citrix_policy_name ,
                                 description = None,
                                 policy_state=None,
                                 **params
                                 ):
        action = ACTION_CREATE_CITRIX_POLICY
        body = {"zone": zone, "citrix_policy_name": citrix_policy_name}        
        if description:
            body["description"] = description
        if policy_state is not None:
            body["policy_state"] = policy_state                    
        return self._build_params(action, body)

    def config_citrix_policy_item(self,
                              zone,
                              citrix_policy_name,
                              citrix_policy_id,
                              policy_items,
                              **params
                              ):
        action = ACTION_CONFIG_CITRIX_POLICY_ITEM
        body = {"zone": zone, "citrix_policy_id": citrix_policy_id, "citrix_policy_name": citrix_policy_name,"policy_items":policy_items}
        return self._build_params(action, body)

    def describe_citrix_policy_item_config(self, 
                                       zone,
                                       col1=None,
                                       col2=None,
                                       col3=None,
                                       search_word=None,
                                       pol_id=None,                                    
                                       **params
                                       ):

        action = ACTION_DESCRIBE_CITRIX_POLICY_CONFIG
        body = {"zone": zone}
        if col1 is not None:
            body["col1"] = col1
        if col2 is not None:
            body["col2"] = col2       
        if col3 is not None:
            body["col3"] = col3
        if search_word is not None:
            body["search_word"] = search_word                    
        if pol_id is not None:
            body["pol_id"] = pol_id        
        return self._build_params(action, body)


    def describe_citrix_policy(self, 
                                       zone,
                                       citrix_policy_names=None,
                                       citrix_policy_ids=None,
                                       search_word=None,
                                       **params
                                       ):

        action = ACTION_DESCRIBE_CITRIX_POLICY
        body = {"zone": zone}
        if citrix_policy_names is not None:
            body["citrix_policy_names"] = citrix_policy_names        
        if search_word is not None:
            body["search_word"] = search_word   
        if citrix_policy_ids is not None:
            body["search_word"] = citrix_policy_ids          
        return self._build_params(action, body)

    def describe_citrix_policy_item(self, 
                                       zone,
                                       citrix_policy_id,
                                       **params
                                       ):

        action = ACTION_DESCRIBE_CITRIX_POLICY_ITEM
        body = {"zone": zone,"citrix_policy_id": citrix_policy_id}
        return self._build_params(action, body)


    def delete_citrix_policy(self, zone,
                            citrix_policy_name,
                            citrix_policy_id,
                            **params
                            ):

        action = ACTION_DELETE_CITRIX_POLICY
        body = {"zone": zone, "citrix_policy_name": citrix_policy_name,"citrix_policy_id":citrix_policy_id}        
        return self._build_params(action, body)

    def modify_citrix_policy(self, zone,
                            citrix_policy_name,
                            citrix_policy_id,
                            description = None,
                            policy_state=None,
                            **params
                            ):

        action = ACTION_MODIFY_CITRIX_POLICY
        body = {"zone": zone,"citrix_policy_name": citrix_policy_name, "citrix_policy_id":citrix_policy_id}
        if description is not None:
            body["description"] = description
        if policy_state is not None:
            body["policy_state"] = policy_state                    
        return self._build_params(action, body)

    def rename_citrix_policy(self, zone,
                            citrix_policy_id,
                            citrix_policy_old_name,
                            citrix_policy_new_name,
                            **params
                            ):

        action = ACTION_RENAME_CITRIX_POLICY
        body = {"zone": zone,"citrix_policy_id":citrix_policy_id,"citrix_policy_old_name": citrix_policy_old_name, "citrix_policy_new_name":citrix_policy_new_name}
        return self._build_params(action, body)
    
    
    def refresh_citrix_policy(self,
                                   zone,                               
                                   sync_type,
                                   citrix_policy_name=None,
                                   citrix_policy_id=None,                                   
                                   **params):

        action = ACTION_REFRESH_CITRIX_POLICY
        body = {"zone": zone, "sync_type": sync_type}
        if citrix_policy_name is not None:
            body["citrix_policy_name"] = citrix_policy_name        
        if citrix_policy_id is not None:
            body["citrix_policy_id"] = citrix_policy_id             
        return self._build_params(action, body)
    
    def set_citrix_policy_priority(self, zone,
                            citrix_policy_name,
                            citrix_policy_id,
                            policy_priority,
                            **params
                            ):

        action = ACTION_SET_CITRIX_POLICY_PRIORITY
        body = {"zone": zone,"citrix_policy_name": citrix_policy_name, "citrix_policy_id":citrix_policy_id,"policy_priority":policy_priority}            
        return self._build_params(action, body)    

    def add_citrix_policy_filter(self,
                              zone,
                              citrix_policy_name,
                              citrix_policy_id,
                              policy_filters,
                              **params
                              ):

        action = ACTION_ADD_CITRIX_POLICY_FILTER
        body = {"zone": zone, "citrix_policy_id": citrix_policy_id, "citrix_policy_name": citrix_policy_name,"policy_filters":policy_filters}
        return self._build_params(action, body)
    
    def modify_citrix_policy_filter(self,
                              zone,
                              citrix_policy_name,
                              citrix_policy_id,
                              policy_filters,
                              **params
                              ):

        action = ACTION_MODIFY_CITRIX_POLICY_FILTER
        body = {"zone": zone, "citrix_policy_id": citrix_policy_id, "citrix_policy_name": citrix_policy_name,"policy_filters":policy_filters}
        return self._build_params(action, body)

    def describe_citrix_policy_filter(self, 
                                       zone,
                                       citrix_policy_name,
                                       citrix_policy_id,
                                       **params
                                       ):

        action = ACTION_DESCRIBE_CITRIX_POLICY_FILTER
        body = {"zone": zone,"citrix_policy_id": citrix_policy_id,"citrix_policy_name":citrix_policy_name}
        return self._build_params(action, body)

    def delete_citrix_policy_filter(self,
                              zone,
                              citrix_policy_name,
                              citrix_policy_id,
                              policy_filters,
                              **params
                              ):

        action = ACTION_DELETE_CITRIX_POLICY_FILTER
        body = {"zone": zone, "citrix_policy_id": citrix_policy_id, "citrix_policy_name": citrix_policy_name,"policy_filters":policy_filters}
        return self._build_params(action, body)    