
from constants import (
    CHANNEL_API,
    CHANNEL_SESSION,
    CHANNEL_INTERNAL,
    CHECK_PLATFROM,
    ADMIN_ROLES,
    PLATFROM_CITRIX,
    ACTION_CREATE_CITRIX_POLICY,    
    ACTION_DESCRIBE_CITRIX_POLICY ,    
    ACTION_DELETE_CITRIX_POLICY,
    ACTION_MODIFY_CITRIX_POLICY, 
    ACTION_RENAME_CITRIX_POLICY,
    ACTION_REFRESH_CITRIX_POLICY,
    ACTION_SET_CITRIX_POLICY_PRIORITY,
    ACTION_DESCRIBE_CITRIX_POLICY_FILTER,
    ACTION_ADD_CITRIX_POLICY_FILTER,
    ACTION_MODIFY_CITRIX_POLICY_FILTER,
    ACTION_DELETE_CITRIX_POLICY_FILTER,   
    ACTION_CONFIG_CITRIX_POLICY_ITEM ,
    ACTION_DESCRIBE_CITRIX_POLICY_ITEM ,
    ACTION_DESCRIBE_CITRIX_POLICY_CONFIG ,
)

CITRIX_POLICY_API_ACL = {
              ACTION_CREATE_CITRIX_POLICY: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_CONFIG_CITRIX_POLICY_ITEM: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_DESCRIBE_CITRIX_POLICY: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_DESCRIBE_CITRIX_POLICY_ITEM: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },              
              ACTION_DESCRIBE_CITRIX_POLICY_CONFIG: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_DELETE_CITRIX_POLICY: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_MODIFY_CITRIX_POLICY: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_RENAME_CITRIX_POLICY: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },                
              ACTION_REFRESH_CITRIX_POLICY: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },                                      
              ACTION_SET_CITRIX_POLICY_PRIORITY: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_DESCRIBE_CITRIX_POLICY_FILTER: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_ADD_CITRIX_POLICY_FILTER: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_MODIFY_CITRIX_POLICY_FILTER: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },
              ACTION_DELETE_CITRIX_POLICY_FILTER: {
                  CHANNEL_API: ADMIN_ROLES,
                  CHANNEL_SESSION: ADMIN_ROLES,
                  CHANNEL_INTERNAL: ADMIN_ROLES,
                  CHECK_PLATFROM: PLATFROM_CITRIX
               },                                                    
              }