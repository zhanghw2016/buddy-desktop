
from constants import (

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
from request.consolidator.base.base_request_builder import BaseRequestBuilder
from log.logger import logger

class SnapshotRequestBuilder(BaseRequestBuilder):

    def describe_desktop_snapshots(self,
                                   zone,
                                   snapshots=None,
                                   desktop_resource=None,
                                   resource_id=None,
                                   snapshot_type=None,
                                   snapshot_time=None,
                                   root_id=None,
                                   status=None,
                                   verbose=0,
                                   snapshot_name=None,
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
        action = ACTION_VDI_DESCRIBE_DESKTOP_SNAPSHOTS
        body = {}
        body["zone"] = zone
        if snapshots:
            body['snapshots'] = snapshots
        if desktop_resource:
            body['desktop_resource'] = desktop_resource
        if resource_id:
            body['resource_id'] = resource_id
        if snapshot_time:
            body['snapshot_time'] = snapshot_time
        if snapshot_type is not None:
            body["snapshot_type"] = snapshot_type
        if root_id:
            body["root_id"] = root_id
        if status:
            body["status"] = status
        if snapshot_name:
            body["snapshot_name"] = snapshot_name
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

    def create_desktop_snapshots(self,
                                 zone,
                                 resources=None,
                                 snapshot_group=None,
                                 snapshot_name=None,
                                 is_full=0,
                                 **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS
        body = {}
        body["zone"] = zone
        if resources:
            body['resources'] = resources
        if snapshot_group:
            body['snapshot_group'] = snapshot_group
        if snapshot_name:
            body["snapshot_name"] = snapshot_name
        body["is_full"] = is_full
        return self._build_params(action, body)

    def modify_desktop_snapshot_attributes(self,
                                           zone,
                                           snapshot,
                                           snapshot_name=None,
                                           description=None,
                                           **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_SNAPSHOT_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body["snapshot"] = snapshot

        if snapshot_name:
            body['snapshot_name'] = snapshot_name

        if description:
            body['description'] = description

        return self._build_params(action, body)

    def delete_desktop_snapshots(self,
                                 zone,
                                 snapshots=None,
                                 snapshot_group_snapshots=None,
                                 **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DESKTOP_SNAPSHOTS

        body = {}
        body["zone"] = zone
        if snapshots:
            body['snapshots'] = snapshots
        if snapshot_group_snapshots:
            body['snapshot_group_snapshots'] = snapshot_group_snapshots

        return self._build_params(action, body)

    def apply_desktop_snapshots(self,
                                zone,
                                snapshots=None,
                                snapshot_group_snapshots=None,
                                resources=None,
                                ymd=None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_APPLY_DESKTOP_SNAPSHOTS

        body = {}
        body["zone"] = zone
        if snapshots:
            body['snapshots'] = snapshots
        if snapshot_group_snapshots:
            body['snapshot_group_snapshots'] = snapshot_group_snapshots
        if resources:
            body['resources'] = resources
        if ymd is not None:
            body['ymd'] = ymd

        return self._build_params(action, body)

    def describe_snapshot_groups(self,
                                 zone,
                                 snapshot_groups=None,
                                 status=None,
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
        action = ACTION_VDI_DESCRIBE_SNAPSHOT_GROUPS

        body = {}
        body["zone"] = zone
        if snapshot_groups:
            body['snapshot_groups'] = snapshot_groups
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

    def create_snapshot_group(self,
                              zone,
                              snapshot_group_name,
                              description=None,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_SNAPSHOT_GROUP

        body = {}
        body["zone"] = zone
        body['snapshot_group_name'] = snapshot_group_name
        if description:
            body["description"] = description

        return self._build_params(action, body)

    def modify_snapshot_group(self,
                              zone,
                              snapshot_group,
                              snapshot_group_name=None,
                              description=None,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_SNAPSHOT_GROUP

        body = {}
        body["zone"] = zone
        body['snapshot_group'] = snapshot_group
        if snapshot_group_name:
            body["snapshot_group_name"] = snapshot_group_name
        if description:
            body["description"] = description

        return self._build_params(action, body)

    def delete_snapshot_groups(self,
                               zone,
                               snapshot_groups,
                               is_delete_backup_resource=0,
                               **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_SNAPSHOT_GROUPS

        body = {}
        body["zone"] = zone
        body['snapshot_groups'] = snapshot_groups
        body['is_delete_backup_resource'] = is_delete_backup_resource

        return self._build_params(action, body)

    def add_resource_to_snapshot_group(self,
                                       zone,
                                       snapshot_group,
                                       resources,
                                       **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ADD_RESOURCE_TO_SNAPSHOT_GROUP

        body = {}
        body["zone"] = zone
        body['snapshot_group'] = snapshot_group
        body["resources"] = resources

        return self._build_params(action, body)

    def delete_resource_from_snapshot_group(self,
                                            zone,
                                            snapshot_group,
                                            resources,
                                            **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_RESOURCE_FROM_SNAPSHOT_GROUP

        body = {}
        body["zone"] = zone
        body['snapshot_group'] = snapshot_group
        body["resources"] = resources

        return self._build_params(action, body)

    def describe_snapshot_group_snapshots(self,
                                          zone,
                                          snapshot_group_snapshots,
                                          status=None,
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
        action = ACTION_VDI_DESCRIBE_SNAPSHOT_GROUP_SNAPSHOTS

        body = {}
        body["zone"] = zone
        body['snapshot_group_snapshots'] = snapshot_group_snapshots
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

