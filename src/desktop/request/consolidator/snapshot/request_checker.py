
from constants import (
    ALL_PLATFORMS,

    # snapshot
    ACTION_VDI_DESCRIBE_DESKTOP_SNAPSHOTS,
    ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS,
    ACTION_VDI_MODIFY_DESKTOP_SNAPSHOT_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_SNAPSHOTS,
    ACTION_VDI_APPLY_DESKTOP_SNAPSHOTS,
    ACTION_VDI_DESCRIBE_SNAPSHOT_GROUPS,
    ACTION_VDI_CREATE_SNAPSHOT_GROUP,
    ACTION_VDI_MODIFY_SNAPSHOT_GROUP,
    ACTION_VDI_DELETE_SNAPSHOT_GROUPS,
    ACTION_VDI_ADD_RESOURCE_TO_SNAPSHOT_GROUP,
    ACTION_VDI_DELETE_RESOURCE_FROM_SNAPSHOT_GROUP,
    ACTION_VDI_DESCRIBE_SNAPSHOT_GROUP_SNAPSHOTS,
)
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import SnapshotRequestBuilder

class SnapshotRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(SnapshotRequestChecker, self).__init__(sender, checker)
        self.builder = SnapshotRequestBuilder(sender)

        self.handler_map = {
                            ACTION_VDI_DESCRIBE_DESKTOP_SNAPSHOTS: self.describe_desktop_snapshots,
                            ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS: self.create_desktop_snapshots,
                            ACTION_VDI_MODIFY_DESKTOP_SNAPSHOT_ATTRIBUTES: self.modify_desktop_snapshot_attributes,
                            ACTION_VDI_DELETE_DESKTOP_SNAPSHOTS: self.delete_desktop_snapshots,
                            ACTION_VDI_APPLY_DESKTOP_SNAPSHOTS: self.apply_desktop_snapshots,
                            ACTION_VDI_DESCRIBE_SNAPSHOT_GROUPS: self.describe_snapshot_groups,
                            ACTION_VDI_CREATE_SNAPSHOT_GROUP: self.create_snapshot_group,
                            ACTION_VDI_MODIFY_SNAPSHOT_GROUP: self.modify_snapshot_group,
                            ACTION_VDI_DELETE_SNAPSHOT_GROUPS: self.delete_snapshot_groups,
                            ACTION_VDI_ADD_RESOURCE_TO_SNAPSHOT_GROUP: self.add_resource_to_snapshot_group,
                            ACTION_VDI_DELETE_RESOURCE_FROM_SNAPSHOT_GROUP: self.delete_resource_from_snapshot_group,
                            ACTION_VDI_DESCRIBE_SNAPSHOT_GROUP_SNAPSHOTS: self.describe_snapshot_group_snapshots
            }

    def describe_desktop_snapshots(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", 'resource_id', 'root_id', 'search_word', 'snapshot_name','sort_key'],
                                  integer_params=['snapshot_type', 'verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['snapshots', 'status', 'desktop_resource'],
                                  filter_params=[]):
            return None

        return self.builder.describe_desktop_snapshots(**directive)

    def create_desktop_snapshots(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", 'snapshot_name', 'snapshot_group'],
                                  integer_params=['is_full'],
                                  list_params=['resources'],
                                  filter_params=[]):
            return None

        return self.builder.create_desktop_snapshots(**directive)

    def modify_desktop_snapshot_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "snapshot"],
                                  str_params=["zone", 'snapshot', 'snapshot_name', 'description'],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.modify_desktop_snapshot_attributes(**directive)

    def delete_desktop_snapshots(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["snapshots", "snapshot_group_snapshots"],
                                  filter_params=[]):
            return None

        return self.builder.delete_desktop_snapshots(**directive)

    def apply_desktop_snapshots(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "ymd"],
                                  integer_params=[],
                                  list_params=["snapshots", "snapshot_group_snapshots", "resources"],
                                  filter_params=[]):
            return None

        return self.builder.apply_desktop_snapshots(**directive)

    def describe_snapshot_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse", "is_and"],
                                  list_params=["snapshot_groups", "status"],
                                  filter_params=[]):
            return None

        return self.builder.describe_snapshot_groups(**directive)

    def create_snapshot_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", 'snapshot_group_name'],
                                  str_params=["zone", 'snapshot_group_name', "description"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.create_snapshot_group(**directive)

    def modify_snapshot_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", 'snapshot_group'],
                                  str_params=["zone", 'snapshot_group', 'snapshot_group_name', "description"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.modify_snapshot_group(**directive)

    def delete_snapshot_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", 'snapshot_groups'],
                                  str_params=["zone"],
                                  integer_params=["is_delete_backup_resource"],
                                  list_params=["snapshot_groups"],
                                  filter_params=[]):
            return None

        return self.builder.delete_snapshot_groups(**directive)

    def add_resource_to_snapshot_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", 'snapshot_group', 'resources'],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["resources"],
                                  filter_params=[]):
            return None

        return self.builder.add_resource_to_snapshot_group(**directive)

    def delete_resource_from_snapshot_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", 'snapshot_group', 'resources'],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["resources"],
                                  filter_params=[]):
            return None

        return self.builder.delete_resource_from_snapshot_group(**directive)

    def describe_snapshot_group_snapshots(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","snapshot_group_snapshots"],
                                  str_params=["zone", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse", "is_and"],
                                  list_params=["snapshot_group_snapshots", "status"],
                                  filter_params=[]):
            return None

        return self.builder.describe_snapshot_group_snapshots(**directive)
