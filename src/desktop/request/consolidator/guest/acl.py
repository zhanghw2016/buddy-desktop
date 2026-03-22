
from constants import (
    CHANNEL_API,
    CHANNEL_SESSION,
    CHANNEL_INTERNAL,
    CHECK_PLATFROM,
    ALL_PLATFORMS,
    ALL_ROLES,
    USER_ROLE_GLOBAL_ADMIN
)
import constants as const


GUEST_API_ACL = {
            const.ACTION_VDI_SEND_DESKTOP_MESSAGE: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_SEND_DESKTOP_NOTIFY: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_SEND_DESKTOP_HOT_KEYS: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_SEND_DESKTOP_NOTIFY: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_CHECK_DESKTOP_AGENT_STATUS: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_LOGIN_DESKTOP: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_LOGOFF_DESKTOP: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_ADD_DESKTOP_ACTIVE_DIRECTORY: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_DESCRIBE_SPICE_INFO: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_MODIFY_GUEST_SERVER_CONFIG: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_DESCRIBE_GUEST_PROCESSES: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_DESCRIBE_GUEST_PROGRAMS: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            const.ACTION_VDI_GUEST_JSON_RCP: {
                  CHANNEL_API: ALL_ROLES,
                  CHANNEL_SESSION: ALL_ROLES,
                  CHANNEL_INTERNAL: ALL_ROLES,
                  CHECK_PLATFROM: ALL_PLATFORMS
               },
            # desktop maintainer
            const.ACTION_VDI_CREATE_DESKTOP_MAINTAINER: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_MODIFY_DESKTOP_MAINTAINER_ATTRIBUTES: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_DELETE_DESKTOP_MAINTAINERS: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_DESCRIBE_DESKTOP_MAINTAINERS: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_GUEST_CHECK_DESKTOP_MAINTAINER: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_APPLY_DESKTOP_MAINTAINER: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_ATTACH_RESOURCE_TO_DESKTOP_MAINTAINER: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_DETACH_RESOURCE_FROM_DESKTOP_MAINTAINER: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_RUN_GUEST_SHELL_COMMAND: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_DESCRIBE_GUEST_SHELL_COMMANDS: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
            const.ACTION_VDI_GUEST_CHECK_SHELL_COMMAND: {
                CHANNEL_API: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_SESSION: USER_ROLE_GLOBAL_ADMIN,
                CHANNEL_INTERNAL: USER_ROLE_GLOBAL_ADMIN,
                CHECK_PLATFROM: ALL_PLATFORMS
            },
        }

