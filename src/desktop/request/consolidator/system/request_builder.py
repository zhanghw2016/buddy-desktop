
from constants import (
    ACTION_VDI_DESCRIBE_NOTICE_PUSHS,
    ACTION_VDI_CREATE_NOTICE_PUSH,
    ACTION_VDI_MODIFY_NOTICE_PUSH_ATTRIBUTES,
    ACTION_VDI_DELETE_NOTICE_PUSHS,
    ACTION_VDI_MODIFY_NOTICE_PUSH_ZONE_USER,
    ACTION_VDI_SET_USER_NOTICE_READ,

    # software
    ACTION_VDI_DESCRIBE_SOFTWARES,
    ACTION_VDI_UPLOAD_SOFTWARES,
    ACTION_VDI_DOWNLOAD_SOFTWARES,
    ACTION_VDI_DELETE_SOFTWARES,
    ACTION_VDI_CHECK_SOFTWARE_VNAS_NODE_DIR,
)
from request.consolidator.base.base_request_builder import BaseRequestBuilder

class SystemRequestBuilder(BaseRequestBuilder):

    def describe_notice_pushs(self, 
                               notices=None,
                               notice_type=None,
                               notice_level=None,
                               status = None,
                               scope=None,
                               reverse = None,
                               sort_key = None,
                               offset = 0,
                               limit = 20,
                               search_word = None,
                               verbose = 0,
                               **params
                               ):

        action = ACTION_VDI_DESCRIBE_NOTICE_PUSHS
        body = {}
        
        if notices:
            body["notices"] = notices
        
        if notice_type:
            body["notice_type"] = notice_type
        
        if status:
            body["status"] = status
            
        if scope:
            body["scope"] = scope
        
        if notice_level:
            body["notice_level"] = notice_level
        
        if reverse:
            body["reverse"] = reverse
        
        if sort_key:
            body["sort_key"] = sort_key
        
        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit

        if search_word:
            body["search_word"] = search_word
        
        if verbose is not None:
            body["verbose"] = verbose
         
        return self._build_params(action, body)

    def create_notice_push(self,
                            title,
                            content,
                            scope=None,
                            notice_type=None,
                            notice_level=None,
                            expired_time=None,
                            execute_time=None,
                            force_read=None,
                            **params
                            ):

        action = ACTION_VDI_CREATE_NOTICE_PUSH

        body = {"title": title, "content": content}

        if notice_type:
            body["notice_type"] = notice_type
        
        if scope:
            body["scope"] = scope    
        
        if notice_level:
            body["notice_level"] = notice_level

        if expired_time:
            body["expired_time"] = expired_time
        
        if execute_time:
            body["execute_time"] = execute_time
        
        if force_read is not None:
            body["force_read"] = force_read

        return self._build_params(action, body)

    def modify_notice_push_attributes(self,
                                       notice,
                                       title = None,
                                       content = None,
                                       notice_level=None,
                                       expired_time=None,
                                       execute_time = None,
                                       is_permanent = None,
                                       force_read=None,
                                       **params):

        action = ACTION_VDI_MODIFY_NOTICE_PUSH_ATTRIBUTES
        body = {
            "notice": notice,
            }
        if title:
            body["title"] = title
        if content:
            body["content"] = content
        
        if notice_level:
            body["notice_level"] = notice_level
        
        if expired_time:
            body["expired_time"] = expired_time
        
        if execute_time:
            body["execute_time"] = execute_time
        
        if is_permanent is not None:
            body["is_permanent"] = int(is_permanent)
        
        if force_read is not None:
            body["force_read"] = force_read
            
        return self._build_params(action, body)
    
    def delete_notice_pushs(self,
                             notices,
                             **params
                             ):

        action = ACTION_VDI_DELETE_NOTICE_PUSHS
        body = {"notices": notices}
        return self._build_params(action, body)

    def modify_notice_push_zone_user(self,
                                  notice,
                                  zone_users,
                                  scope=None,
                                  **params
                                  ):

        action = ACTION_VDI_MODIFY_NOTICE_PUSH_ZONE_USER
        body = {"notice": notice, "zone_users": zone_users}
        if scope:
            body["scope"] = scope

        return self._build_params(action, body)

    def set_user_notice_read(self,
                                  notice,
                                  user_id,
                                  **params
                                  ):

        action = ACTION_VDI_SET_USER_NOTICE_READ
        body = {"notice": notice, "user_id": user_id}

        return self._build_params(action, body)

    def describe_softwares(self,
                           zone,
                           softwares=None,
                           software_name=None,
                           software_size=None,
                           verbose=0,
                           search_word=None,
                           offset=None,
                           limit=20,
                           sort_key=None,
                           reverse=0,
                           is_and=1,
                           **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_SOFTWARES
        body = {}
        body["zone"] = zone
        if softwares:
            body['softwares'] = softwares
        if software_name:
            body['software_name'] = software_name
        if software_size:
            body['software_size'] = software_size
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if verbose is not None:
            body['verbose'] = int(verbose)
        if reverse == 0:
            body['reverse'] = 0
        else:
            body['reverse'] = 1
        if sort_key:
            body["sort_key"] = sort_key
        if is_and == 0:
            body['is_and'] = 0
        else:
            body['is_and'] = 1

        return self._build_params(action, body)

    def upload_softwares(self,
                         zone,
                         software_name,
                         software_size,
                         is_system_custom_logo=None,
                         **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_UPLOAD_SOFTWARES
        body = {}
        body["zone"] = zone
        body["software_name"] = software_name
        body["software_size"] = software_size
        if is_system_custom_logo:
            body["is_system_custom_logo"] = is_system_custom_logo

        return self._build_params(action, body)

    def download_softwares(self,
                           zone,
                           softwares,
                           **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DOWNLOAD_SOFTWARES
        body = {}
        body["zone"] = zone
        body["softwares"] = softwares

        return self._build_params(action, body)

    def delete_softwares(self,
                         zone,
                         softwares,
                         **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_SOFTWARES

        body = {}
        body["zone"] = zone
        body["softwares"] = softwares

        return self._build_params(action, body)

    def check_software_vnas_node_dir(self,
                                    zone,
                                    vnas_node_dir,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CHECK_SOFTWARE_VNAS_NODE_DIR

        body = {}
        body["zone"] = zone
        body["vnas_node_dir"] = vnas_node_dir

        return self._build_params(action, body)
