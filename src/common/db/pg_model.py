'''
Created on 2012-5-6

@author: yunify
'''
from db.pg_models.desktop_pg_model import DesktopPGModel
from db.pg_models.user_pg_model import UserPGModel
from db.pg_models.resource_pg_model import ResourcePGModel
from db.pg_models.resource_user_pg_model import ResourceUserPGModel
from db.pg_models.desktop_group_pg_model import DesktopGroupPGModel
from db.pg_models.dispatch_pg_model import DispatchPGModel
from db.pg_models.image_pg_model import ImagePGModel
from db.pg_models.nic_pg_model import NicPGModel
from db.pg_models.scheduler_pg_model import SchedulerPGModel
from db.pg_models.disk_pg_model import DiskPGModel
from db.pg_models.network_pg_model import NetworkPGModel
from db.pg_models.delivery_group_pg_model import DeliveryGroupPGModel
from db.pg_models.snapshot_pg_model import SnapshotPGModel
from db.pg_models.system_pg_model import SystemPGModel
from db.pg_models.license_model import LicensePGModel
from db.pg_models.policy_group_pg_model import PolicyGroupPGModel
from db.pg_models.security_policy_pg_model import SecurityPolicyPGModel
from db.pg_models.zone_pg_model import ZonePGModel
from db.pg_models.auth_pg_model import AuthPGModel
from db.pg_models.password_prompt_pg_model import PasswordPromptPGModel
from db.pg_models.terminal_pg_model import TerminalPGModel
from db.pg_models.terminal_group_pg_model import TerminalGroupPGModel
from db.pg_models.module_custom_pg_model import ModuleCustomPGModel
from db.pg_models.system_custom_pg_model import SystemCustomPGModel
from db.pg_models.component_version_pg_model import ComponentVersionPGModel
from db.pg_models.desktop_service_management_pg_model import DesktopServiceManagementPGModel
from db.pg_models.apply_approve_pg_model import ApplyApprovePGModel
from db.pg_models.workflow_pg_model import WorkflowPGModel
from db.pg_models.file_share_pg_model import FileSharePGModel
from db.pg_models.guest_pg_model import GuestPGModel
from db.pg_models.local_user_pg_model import LocalUserPGModel
from db.pg_models.desktop_maintainer_pg_model import DesktopMaintainerPGModel
from db.pg_models.citrix_policy_pg_model import CitrixPolicyPGModel
class PGModel():
    ''' PostgreSQL model for complicated requests '''

    def __init__(self, pg):
        self.pg = pg
        # additional models
        self.models = []

        for cls in [DesktopPGModel, UserPGModel, ResourcePGModel, DesktopGroupPGModel, 
                    DispatchPGModel, ImagePGModel, NicPGModel, SchedulerPGModel, 
                    DiskPGModel, NetworkPGModel, DeliveryGroupPGModel, SnapshotPGModel, 
                    SystemPGModel, LicensePGModel, PolicyGroupPGModel,CitrixPolicyPGModel, SecurityPolicyPGModel,
                    ZonePGModel, AuthPGModel, PasswordPromptPGModel, ResourceUserPGModel,
                    TerminalPGModel,TerminalGroupPGModel,ModuleCustomPGModel,SystemCustomPGModel,ComponentVersionPGModel,
                    DesktopServiceManagementPGModel,ApplyApprovePGModel,WorkflowPGModel,FileSharePGModel, GuestPGModel, LocalUserPGModel,
                    DesktopMaintainerPGModel]:

            self.models.append(cls(pg, self))

        self.attr_cache = {}
        self.instance_hypervisors_cache = {}

    def __getattr__(self, attr):
        ''' get object from extension models '''
        if attr in self.attr_cache:
            return self.attr_cache[attr]
        
        for model in self.models:
            if hasattr(model, attr):
                obj = getattr(model, attr)
                self.attr_cache[attr] = obj
                return obj
            
        return None
