
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
    ACTION_VDI_RESET_FILE_SHARE_SERVICE_PASSWORD
)
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import FileShareRequestBuilder

class FileShareRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(FileShareRequestChecker, self).__init__(sender, checker)
        self.builder = FileShareRequestBuilder(sender)

        self.handler_map = {
                                ACTION_VDI_DESCRIBE_FILE_SHARE_GROUPS: self.describe_file_share_groups,
                                ACTION_VDI_CREATE_FILE_SHARE_GROUP: self.create_file_share_group,
                                ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ATTRIBUTES: self.modify_file_share_group_attributes,
                                ACTION_VDI_RENAME_FILE_SHARE_GROUP: self.rename_file_share_group,
                                ACTION_VDI_DELETE_FILE_SHARE_GROUPS: self.delete_file_share_groups,
                                ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ZONE_USER: self.modify_file_share_group_zone_user,

                                ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILES: self.describe_file_share_group_files,
                                ACTION_VDI_UPLOAD_FILE_SHARE_GROUP_FILES: self.upload_file_share_group_files,
                                ACTION_VDI_DOWNLOAD_FILE_SHARE_GROUP_FILES: self.download_file_share_group_files,
                                ACTION_VDI_MODIFY_FILE_SHARE_GROUP_FILE_ATTRIBUTES: self.modify_file_share_group_file_attributes,
                                ACTION_VDI_DELETE_FILE_SHARE_GROUP_FILES: self.delete_file_share_group_files,
                                ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: self.describe_file_share_group_file_download_history,

                                ACTION_VDI_DESCRIBE_FILE_SHARE_CAPACITY: self.describe_file_share_capacity,
                                ACTION_VDI_CHANGE_FILE_IN_FILE_SHARE_GROUP: self.change_file_in_file_share_group,
                                ACTION_VDI_DESCRIBE_FILE_SHARE_RECYCLES: self.describe_file_share_recycles,
                                ACTION_VDI_RESTORE_FILE_SHARE_RECYCLES: self.restore_file_share_recycles,
                                ACTION_VDI_DELETE_PERMANENTLY_FILE_SHARE_RECYCLES: self.delete_permanently_file_share_recycles,
                                ACTION_VDI_EMPTY_FILE_SHARE_RECYCLES: self.empty_file_share_recycles,

                                ACTION_VDI_CREATE_FILE_SHARE_SERVICE: self.create_file_share_service,
                                ACTION_VDI_LOAD_FILE_SHARE_SERVICE: self.load_file_share_service,
                                ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICES: self.describe_file_share_services,
                                ACTION_VDI_MODIFY_FILE_SHARE_SERVICE_ATTRIBUTES: self.modify_file_share_service_attributes,
                                ACTION_VDI_DELETE_FILE_SHARE_SERVICES: self.delete_file_share_services,
                                ACTION_VDI_REFRESH_FILE_SHARE_SERVICE: self.refresh_file_share_service,
                                ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICE_VNAS: self.describe_file_share_service_vnas,
                                ACTION_VDI_RESET_FILE_SHARE_SERVICE_PASSWORD: self.reset_file_share_service_password,
            }

    def describe_file_share_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'file_share_group_name','description','search_word','sort_key','base_dn'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['file_share_groups','show_location','scope'],
                                  filter_params=[]):
            return None

        return self.builder.describe_file_share_groups(**directive)

    def create_file_share_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "file_share_group_name","file_share_service"],
                                  str_params=["zone", "file_share_service","file_share_group_name","scope","description","base_dn"],
                                  integer_params=[],
                                  list_params=["show_location"],
                                  json_params=[],
                                  filter_params=[]):
            return None

        return self.builder.create_file_share_group(**directive)

    def modify_file_share_group_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "file_share_groups"],
                                  str_params=["zone","file_share_groups","description"],
                                  integer_params=[],
                                  list_params=["show_location"],
                                  filter_params=[]):
            return None

        return self.builder.modify_file_share_group_attributes(**directive)

    def rename_file_share_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "file_share_groups","file_share_group_dn","new_name"],
                                  str_params=["zone","file_share_groups","file_share_group_dn","new_name"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.rename_file_share_group(**directive)

    def delete_file_share_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "file_share_groups"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['file_share_groups'],
                                  filter_params=[]):
            return None

        return self.builder.delete_file_share_groups(**directive)

    def modify_file_share_group_zone_user(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone","file_share_groups","scope"],
                                  str_params=["file_share_groups","scope"],
                                  integer_params=[],
                                  list_params=[],
                                  json_params=["zone_users"]
                                  ):
            return None

        return self.builder.modify_file_share_group_zone_user(**directive)

    def describe_file_share_group_files(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['file_share_group_files','file_share_groups'],
                                  filter_params=[]):
            return None

        return self.builder.describe_file_share_group_files(**directive)

    def upload_file_share_group_files(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'file_share_groups',"file_share_service"],
                                  integer_params=[],
                                  list_params=[],
                                  json_params=["upload_files"],
                                  filter_params=[]):
            return None

        return self.builder.upload_file_share_group_files(**directive)

    def download_file_share_group_files(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_group_files"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['file_share_group_files'],
                                  filter_params=[]):
            return None

        return self.builder.download_file_share_group_files(**directive)

    def modify_file_share_group_file_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_group_files","file_share_group_file_alias_name"],
                                  str_params=["zone",'file_share_group_files','file_share_group_file_alias_name','description'],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.modify_file_share_group_file_attributes(**directive)

    def delete_file_share_group_files(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_group_files"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['file_share_group_files'],
                                  filter_params=[]):
            return None

        return self.builder.delete_file_share_group_files(**directive)

    def describe_file_share_group_file_download_history(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_group_files"],
                                  str_params=["zone",'file_share_group_files','search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.describe_file_share_group_file_download_history(**directive)

    def describe_file_share_capacity(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'vnas_node_dir'],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.describe_file_share_capacity(**directive)

    def change_file_in_file_share_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone","file_share_group_files", 'new_file_share_group_dn','change_type'],
                                  str_params=['zone','new_file_share_group_dn','change_type','file_save_method'],
                                  list_params=['file_share_group_files']):
            return None

        return self.builder.change_file_in_file_share_group(**directive)

    def describe_file_share_recycles(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['file_share_group_files'],
                                  filter_params=[]):
            return None

        return self.builder.describe_file_share_recycles(**directive)

    def restore_file_share_recycles(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_group_files"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['file_share_group_files'],
                                  filter_params=[]):
            return None

        return self.builder.restore_file_share_recycles(**directive)

    def delete_permanently_file_share_recycles(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_group_files"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['file_share_group_files'],
                                  filter_params=[]):
            return None

        return self.builder.delete_permanently_file_share_recycles(**directive)

    def empty_file_share_recycles(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.empty_file_share_recycles(**directive)

    def create_file_share_service(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "file_share_service_name","network_id","fuser","fpw","is_sync","scope"],
                                  str_params=["zone", "file_share_service_name","network_id","private_ip",
                                              "description","vnas_disk_size","vnas_id","fuser","fpw","scope"],
                                  integer_params=['limit_rate','limit_conn',"is_sync","max_download_file_size","max_upload_size_single_file"],
                                  list_params=[],
                                  json_params=[],
                                  filter_params=[]):
            return None

        return self.builder.create_file_share_service(**directive)

    def load_file_share_service(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "file_share_service_name","private_ip","fuser","fpw","is_sync","scope"],
                                  str_params=["zone", "file_share_service_name","private_ip","fuser","fpw","description","scope"],
                                  integer_params=["is_sync","max_download_file_size","max_upload_size_single_file"],
                                  list_params=[],
                                  json_params=[],
                                  filter_params=[]):
            return None

        return self.builder.load_file_share_service(**directive)

    def describe_file_share_services(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'file_share_service_name','search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['file_share_services','status'],
                                  filter_params=[]):
            return None

        return self.builder.describe_file_share_services(**directive)

    def modify_file_share_service_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_services","file_share_service_name","fuser","fpw"],
                                  str_params=["zone",'file_share_services','file_share_service_name','description','scope',"fuser","fpw"],
                                  integer_params=['limit_rate','limit_conn','is_sync','max_download_file_size','max_upload_size_single_file'],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.modify_file_share_service_attributes(**directive)

    def delete_file_share_services(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_services"],
                                  str_params=["zone"],
                                  integer_params=['force_delete'],
                                  list_params=['file_share_services'],
                                  filter_params=[]):
            return None

        return self.builder.delete_file_share_services(**directive)

    def refresh_file_share_service(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","file_share_services"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['file_share_services'],
                                  filter_params=[]):
            return None

        return self.builder.refresh_file_share_service(**directive)

    def describe_file_share_service_vnas(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['vnas','status'],
                                  filter_params=[]):
            return None

        return self.builder.describe_file_share_service_vnas(**directive)

    def reset_file_share_service_password(self, directive):

        if not self._check_params(directive,
                                  required_params=['fuser', 'fpw','file_share_services'],
                                  str_params=['fuser', 'fpw','file_share_services']):
            return None

        fuser = directive["fuser"]
        fpw = directive["fpw"]
        if not self._check_user_password(fpw, fuser):
            return None

        return self.builder.reset_file_share_service_password(**directive)





