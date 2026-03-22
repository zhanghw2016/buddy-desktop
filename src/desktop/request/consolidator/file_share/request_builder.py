
from constants import (

    # file_share
    ACTION_VDI_DESCRIBE_FILE_SHARE_GROUPS,
    ACTION_VDI_CREATE_FILE_SHARE_GROUP,
    ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ATTRIBUTES,
    ACTION_VDI_RENAME_FILE_SHARE_GROUP,
    ACTION_VDI_DELETE_FILE_SHARE_GROUPS,
    ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ZONE_USER,

    ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILES,
    ACTION_VDI_UPLOAD_FILE_SHARE_GROUP_FILES,
    ACTION_VDI_DOWNLOAD_FILE_SHARE_GROUP_FILES,
    ACTION_VDI_MODIFY_FILE_SHARE_GROUP_FILE_ATTRIBUTES,
    ACTION_VDI_DELETE_FILE_SHARE_GROUP_FILES,
    ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY,

    ACTION_VDI_DESCRIBE_FILE_SHARE_CAPACITY,
    ACTION_VDI_CHANGE_FILE_IN_FILE_SHARE_GROUP,
    ACTION_VDI_DESCRIBE_FILE_SHARE_RECYCLES,
    ACTION_VDI_RESTORE_FILE_SHARE_RECYCLES,
    ACTION_VDI_DELETE_PERMANENTLY_FILE_SHARE_RECYCLES,
    ACTION_VDI_EMPTY_FILE_SHARE_RECYCLES,

    ACTION_VDI_CREATE_FILE_SHARE_SERVICE,
    ACTION_VDI_LOAD_FILE_SHARE_SERVICE,
    ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICES,
    ACTION_VDI_MODIFY_FILE_SHARE_SERVICE_ATTRIBUTES,
    ACTION_VDI_DELETE_FILE_SHARE_SERVICES,
    ACTION_VDI_REFRESH_FILE_SHARE_SERVICE,
    ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICE_VNAS,
    ACTION_VDI_RESET_FILE_SHARE_SERVICE_PASSWORD,

)
from request.consolidator.base.base_request_builder import BaseRequestBuilder
from log.logger import logger

class FileShareRequestBuilder(BaseRequestBuilder):

    def describe_file_share_groups(self,
                                   zone,
                                   base_dn=None,
                                   file_share_groups=None,
                                   file_share_group_name=None,
                                   description=None,
                                   show_location=None,
                                   scope=None,
                                   search_word=None,
                                   offset=None,
                                   limit=None,
                                   verbose=0,
                                   reverse=0,
                                   sort_key=None,
                                   is_and=1,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_FILE_SHARE_GROUPS
        body = {}
        body["zone"] = zone
        if base_dn:
            body['base_dn'] = base_dn
        if file_share_groups:
            body['file_share_groups'] = file_share_groups
        if file_share_group_name:
            body['file_share_group_name'] = file_share_group_name
        if description:
            body['description'] = description
        if show_location:
            body['show_location'] = show_location
        if scope:
            body['scope'] = scope
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

    def create_file_share_group(self,
                                zone,
                                file_share_service,
                                file_share_group_name,
                                show_location=None,
                                scope=None,
                                base_dn=None,
                                description=None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_FILE_SHARE_GROUP
        body = {}
        body["zone"] = zone
        body["file_share_service"] = file_share_service
        body["file_share_group_name"] = file_share_group_name
        if show_location:
            body["show_location"] = show_location
        if scope:
            body["scope"] = scope
        if base_dn:
            body["base_dn"] = base_dn
        if description:
            body["description"] = description

        return self._build_params(action, body)

    def modify_file_share_group_attributes(self,
                                           zone,
                                           file_share_groups,
                                           show_location=None,
                                           description=None,
                                           **params):

        action = ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body["file_share_groups"] = file_share_groups
        if show_location:
            body["show_location"] = show_location
        if description:
            body["description"] = description

        return self._build_params(action, body)

    def rename_file_share_group(self,
                                zone,
                                file_share_groups,
                                file_share_group_dn,
                                new_name,
                                **params):

        action = ACTION_VDI_RENAME_FILE_SHARE_GROUP
        body = {}
        body["zone"] = zone
        body["file_share_groups"] = file_share_groups
        body["file_share_group_dn"] = file_share_group_dn
        body["new_name"] = new_name

        return self._build_params(action, body)

    def delete_file_share_groups(self,
                                 zone,
                                 file_share_groups,
                                 **params):

        action = ACTION_VDI_DELETE_FILE_SHARE_GROUPS
        body = {}
        body["zone"] = zone
        body["file_share_groups"] = file_share_groups

        return self._build_params(action, body)

    def modify_file_share_group_zone_user(self,
                                          zone,
                                          file_share_groups,
                                          scope,
                                          zone_users=None,
                                          **params):

        action = ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ZONE_USER
        body = {}
        body["zone"] = zone
        body["file_share_groups"] = file_share_groups
        body["scope"] = scope
        if zone_users:
            body["zone_users"] = zone_users

        return self._build_params(action, body)

    def describe_file_share_group_files(self,
                                        zone,
                                        file_share_group_files=None,
                                        file_share_groups=None,
                                        search_word=None,
                                        offset=None,
                                        limit=None,
                                        verbose=0,
                                        reverse=0,
                                        sort_key=None,
                                        is_and=1,
                                        **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILES
        body = {}
        body["zone"] = zone
        if file_share_group_files:
            body['file_share_group_files'] = file_share_group_files
        if file_share_groups:
            body['file_share_groups'] = file_share_groups
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

    def upload_file_share_group_files(self,
                                      zone,
                                      file_share_groups,
                                      upload_files,
                                      file_share_service=None,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_UPLOAD_FILE_SHARE_GROUP_FILES
        body = {}
        body["zone"] = zone
        body["file_share_groups"] = file_share_groups
        body["upload_files"] = upload_files
        if file_share_service is not None:
            body["file_share_service"] = file_share_service

        return self._build_params(action, body)

    def download_file_share_group_files(self,
                                        zone,
                                        file_share_group_files,
                                       **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DOWNLOAD_FILE_SHARE_GROUP_FILES
        body = {}
        body["zone"] = zone
        body["file_share_group_files"] = file_share_group_files

        return self._build_params(action, body)

    def modify_file_share_group_file_attributes(self,
                                                zone,
                                                file_share_group_files,
                                                file_share_group_file_alias_name,
                                                description=None,
                                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_FILE_SHARE_GROUP_FILE_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body["file_share_group_files"] = file_share_group_files
        body["file_share_group_file_alias_name"] = file_share_group_file_alias_name
        if description:
            body["description"] = description

        return self._build_params(action, body)

    def delete_file_share_group_files(self,
                                      zone,
                                      file_share_group_files,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_FILE_SHARE_GROUP_FILES
        body = {}
        body["zone"] = zone
        body["file_share_group_files"] = file_share_group_files

        return self._build_params(action, body)

    def describe_file_share_group_file_download_history(self,
                                                        zone,
                                                        file_share_group_files=None,
                                                        search_word=None,
                                                        offset=None,
                                                        limit=None,
                                                        verbose=0,
                                                        reverse=0,
                                                        sort_key=None,
                                                        is_and=1,
                                                        **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY
        body = {}
        body["zone"] = zone
        if file_share_group_files:
            body['file_share_group_files'] = file_share_group_files
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

    def describe_file_share_capacity(self,
                                     zone,
                                     vnas_node_dir,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_FILE_SHARE_CAPACITY
        body = {}
        body["zone"] = zone
        body["vnas_node_dir"] = vnas_node_dir

        return self._build_params(action, body)

    def change_file_in_file_share_group(self,
                                        zone,
                                        file_share_group_files,
                                        new_file_share_group_dn,
                                        change_type,
                                        file_save_method=None,
                                        **params):

        action = ACTION_VDI_CHANGE_FILE_IN_FILE_SHARE_GROUP
        body = {}
        body["zone"] = zone
        body['file_share_group_files'] = file_share_group_files
        body['new_file_share_group_dn'] = new_file_share_group_dn
        body['change_type'] = change_type
        if file_save_method:
            body['file_save_method'] = file_save_method

        return self._build_params(action, body)

    def describe_file_share_recycles(self,
                                     zone,
                                     file_share_group_files=None,
                                     search_word=None,
                                     offset=None,
                                     limit=None,
                                     verbose=0,
                                     reverse=0,
                                     sort_key=None,
                                     is_and=1,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_FILE_SHARE_RECYCLES
        body = {}
        body["zone"] = zone
        if file_share_group_files:
            body['file_share_group_files'] = file_share_group_files
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

    def restore_file_share_recycles(self,
                                    zone,
                                    file_share_group_files=None,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_RESTORE_FILE_SHARE_RECYCLES
        body = {}
        body["zone"] = zone
        body['file_share_group_files'] = file_share_group_files

        return self._build_params(action, body)

    def delete_permanently_file_share_recycles(self,
                                               zone,
                                               file_share_group_files=None,
                                               **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_PERMANENTLY_FILE_SHARE_RECYCLES
        body = {}
        body["zone"] = zone
        body['file_share_group_files'] = file_share_group_files

        return self._build_params(action, body)

    def empty_file_share_recycles(self,
                                  zone,
                                  **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_EMPTY_FILE_SHARE_RECYCLES
        body = {}
        body["zone"] = zone

        return self._build_params(action, body)

    def create_file_share_service(self,
                                  zone,
                                  file_share_service_name,
                                  network_id,
                                  fuser,
                                  fpw,
                                  scope,
                                  is_sync,
                                  limit_rate=None,
                                  limit_conn=None,
                                  vnas_disk_size=None,
                                  vnas_id=None,
                                  private_ip=None,
                                  description=None,
                                  max_download_file_size=None,
                                  max_upload_size_single_file=None,
                                  **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_FILE_SHARE_SERVICE
        body = {}
        body["zone"] = zone
        body["file_share_service_name"] = file_share_service_name
        body["network_id"] = network_id
        body["fuser"] = fuser
        body["fpw"] = fpw
        body["scope"] = scope
        body["is_sync"] = is_sync
        if limit_rate is not None:
            body["limit_rate"] = limit_rate
        if limit_conn is not None:
            body["limit_conn"] = limit_conn
        if vnas_disk_size:
            body["vnas_disk_size"] = vnas_disk_size
        if vnas_id:
            body["vnas_id"] = vnas_id
        if private_ip:
            body["private_ip"] = private_ip
        if description:
            body["description"] = description
        if max_download_file_size is not None:
            body["max_download_file_size"] = max_download_file_size
        if max_upload_size_single_file is not None:
            body["max_upload_size_single_file"] = max_upload_size_single_file

        return self._build_params(action, body)

    def load_file_share_service(self,
                                     zone,
                                     file_share_service_name,
                                     private_ip,
                                     fuser,
                                     fpw,
                                     scope,
                                     is_sync,
                                     description=None,
                                     max_download_file_size=None,
                                     max_upload_size_single_file=None,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_LOAD_FILE_SHARE_SERVICE
        body = {}
        body["zone"] = zone
        body["file_share_service_name"] = file_share_service_name
        body["private_ip"] = private_ip
        body["fuser"] = fuser
        body["fpw"] = fpw
        body["scope"] = scope
        body["is_sync"] = is_sync
        if description:
            body["description"] = description
        if max_download_file_size is not None:
            body["max_download_file_size"] = max_download_file_size
        if max_upload_size_single_file is not None:
            body["max_upload_size_single_file"] = max_upload_size_single_file

        return self._build_params(action, body)

    def describe_file_share_services(self,
                                     zone,
                                     file_share_services=None,
                                     file_share_service_name=None,
                                     status=None,
                                     search_word=None,
                                     offset=None,
                                     limit=None,
                                     verbose=0,
                                     reverse=0,
                                     sort_key=None,
                                     is_and=1,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICES
        body = {}
        body["zone"] = zone
        if file_share_services:
            body['file_share_services'] = file_share_services
        if file_share_service_name:
            body['file_share_service_name'] = file_share_service_name
        if status:
            body['status'] = status
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

    def modify_file_share_service_attributes(self,
                                             zone,
                                             file_share_services,
                                             file_share_service_name,
                                             fuser,
                                             fpw,
                                             is_sync=0,
                                             limit_rate=None,
                                             limit_conn=None,
                                             description=None,
                                             scope=None,
                                             max_download_file_size=None,
                                             max_upload_size_single_file=None,
                                             **params):

        action = ACTION_VDI_MODIFY_FILE_SHARE_SERVICE_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body["file_share_services"] = file_share_services
        body["file_share_service_name"] = file_share_service_name
        body["fuser"] = fuser
        body["fpw"] = fpw
        body["is_sync"] = is_sync
        if limit_rate is not None:
            body["limit_rate"] = limit_rate
        if limit_conn is not None:
            body["limit_conn"] = limit_conn
        if description:
            body["description"] = description
        if scope:
            body["scope"] = scope
        if max_download_file_size is not None:
            body["max_download_file_size"] = max_download_file_size
        if max_upload_size_single_file is not None:
            body["max_upload_size_single_file"] = max_upload_size_single_file

        return self._build_params(action, body)

    def delete_file_share_services(self,
                                   zone,
                                   file_share_services=None,
                                   force_delete=0,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_FILE_SHARE_SERVICES
        body = {}
        body["zone"] = zone
        body['file_share_services'] = file_share_services
        if force_delete is not None:
            body['force_delete'] = force_delete

        return self._build_params(action, body)

    def refresh_file_share_service(self,
                                   zone,
                                   file_share_services=None,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_REFRESH_FILE_SHARE_SERVICE
        body = {}
        body["zone"] = zone
        body['file_share_services'] = file_share_services

        return self._build_params(action, body)

    def describe_file_share_service_vnas(self,
                                         zone,
                                         vnas=None,
                                         vnas_name=None,
                                         status=None,
                                         search_word=None,
                                         offset=None,
                                         limit=None,
                                         verbose=0,
                                         reverse=0,
                                         sort_key=None,
                                         is_and=1,
                                         **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICE_VNAS
        body = {}
        body["zone"] = zone
        if vnas:
            body['vnas'] = vnas
        if vnas_name:
            body['vnas_name'] = vnas_name
        if status:
            body['status'] = status
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

    def reset_file_share_service_password(self,
                                          file_share_services,
                                          fuser,
                                          fpw,
                                          **params):
        action = ACTION_VDI_RESET_FILE_SHARE_SERVICE_PASSWORD
        body = {}
        body['file_share_services'] = file_share_services
        body['fuser'] = fuser
        body['fpw'] = fpw

        return self._build_params(action, body)




