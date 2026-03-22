# -*- coding: utf-8 -*-
from constants import EN, ZH_CN

ERR_MSG_API_NOT_SUPPORT_IN_CURRENT_VERSION = {EN: "API not support in current version",
                                              ZH_CN: u"API在当前版本不支持"}
# database
ERR_MSG_DATABASE_OPERATION_EXCEPTION = {EN: "database operation exception",
                                        ZH_CN: u"数据库操作异常"}
ERR_MSG_DATABASE_DATE_NOT_FOUND = {EN: "data not in database",
                                        ZH_CN: u"数据不存在"}
# ad server
ERR_MSG_AUTH_SERVER_OPERATION_EXCEPTION = {EN: "auth server operation exception",
                                         ZH_CN: u"认证服务器操作异常"}
ERR_MSG_AUTH_SERVER_CONFIG_ERROR = {EN: "auth server configure exception",
                                         ZH_CN: u"认证服务器配置异常"}
#system config
ERR_MSG_MODIFY_SYSTEM_CONDIF_ERROR = {EN: "modify system config failed",
                                  ZH_CN: u"修改系统配置失败"}
ERR_MSG_DESCRIBE_SYSTEM_CONDIF_ERROR = {EN: "describe system config failed",
                                  ZH_CN: u"获取系统配置失败"}
ERR_MSG_SYSTEM_CONDIF_KEY_NOT_EXISTS_ERROR = {EN: "system config key is not exist",
                                  ZH_CN: u"系统配置项不存在"}
# system log
ERR_MSG_ADD_SYSTEM_LOG_ERROR = {EN: "add system log failed",
                                  ZH_CN: u"添加系统日志失败"}
ERR_MSG_GET_SYSTEM_LOG_ERROR = {EN: "get system log failed",
                                  ZH_CN: u"获取系统日志失败"}
ERR_MSG_SYSLOG_SERVER_CREATE_ERROR = {EN: "create syslog server failed",
                                  ZH_CN: u"创建系统日志服务失败"}
ERR_MSG_SYSLOG_SERVER_MODIFY_ERROR = {EN: "modify syslog server failed",
                                  ZH_CN: u"修改系统日志服务失败"}
ERR_MSG_SYSLOG_SERVER_DELETE_ERROR = {EN: "delete syslog server failed",
                                  ZH_CN: u"删除系统日志服务失败"}
ERR_MSG_SYSLOG_SERVER_HAVE_EXIST_ERROR = {EN: "syslog server have exist",
                                  ZH_CN: u"系统日志服务已经存在"}
ERR_MSG_SYSLOG_SERVER_NOT_EXIST_ERROR = {EN: "syslog server not exist",
                                  ZH_CN: u"系统日志服务不存在"}
ERR_MSG_SYSLOG_SERVER_RUNTIME_ERROR = {EN: "syslog server have the same runtime",
                                  ZH_CN: u"该runtime被其他系统日志服务占用"}
#apply and approve
ERR_MSG_CREATE_APPLY_FORM_ERROR = {EN: "create apply form failed",
                                  ZH_CN: u"创建申请单失败"}
ERR_MSG_CREATE_REPEAT_APPLY_FORM_ERROR = {EN: "repeat create apply form",
                                  ZH_CN: u"重复创建申请单"}
ERR_MSG_NORMAL_USER_CANT_DELETE_APPLY_FORM = {EN: "normal user %s cant delete apply form",
                                  ZH_CN: u"普通用户%s不能删除申请单"}
ERR_MSG_DELETE_APPLY_FORM_ERROR = {EN: "delete apply form %s failed",
                                  ZH_CN: u"删除申请单 %s 失败"}
ERR_MSG_DELETE_APPLY_FORM_NOT_CREATE_STATUS_ERROR = {EN: "delete apply form not created status failed",
                                  ZH_CN: u"删除申请单非created状态"}
ERR_MSG_DESCRIBE_APPLY_FORM_ERROR = {EN: "describe apply form failed",
                                  ZH_CN: u"查询申请单失败"}
ERR_MSG_APPLY_FORM_NOT_EXISTED_ERROR = {EN: "apply form %s not existed, please delete this apply form",
                                  ZH_CN: u"申请单 %s 不存在，建议删除该申请单"}
ERR_MSG_MODIFY_APPLY_FORM_ERROR = {EN: "modify apply form %s failed",
                                  ZH_CN: u"修改申请单 %s 失败"}
ERR_MSG_APPLY_FORM_PERMISSION_ERROR = {EN: "apply form permission error",
                                  ZH_CN: u"申请单相关操作权限失败"}
ERR_MSG_APPLY_FORM_STATUS_ERROR = {EN: "apply form status error, operation failed",
                                  ZH_CN: u"申请单状态错误，操作失败"}
ERR_MSG_DEAL_APPLY_FORM_STATUS_ERROR = {EN: "deal apply form error",
                                  ZH_CN: u"处理申请单失败"}
ERR_MSG_DEAL_APPLY_RESOURCE_TYPE_ERROR = {EN: "apply form type error",
                                  ZH_CN: u"申请资源类型错误"}
ERR_MSG_DEAL_APPLY_UNLOCK_RESOURCE_ERROR = {EN: "unlock error",
                                  ZH_CN: u"解锁失败"}

#apply group
ERR_MSG_APPLY_GROUP_NAME_EXISTED_ERROR = {EN: "apply group name %s is existed",
                                  ZH_CN: u"申请组名称 %s 已经存在"}
ERR_MSG_APPLY_GROUP_FORM_NO_FOUND = {EN: "apply group %s no found",
                                  ZH_CN: u"申请组 %s 不存在"}
ERR_MSG_CREATE_APPLY_GROUP_FORM_ERROR = {EN: "create apply group form failed",
                                  ZH_CN: u"创建申请组失败"}
ERR_MSG_CREATE_APPLY_GROUP_FORM_EXISTED_ERROR = {EN: "apply group %s is existed",
                                  ZH_CN: u"申请组 %s 已经存在"}
ERR_MSG_MODIFY_APPLY_GROUP_FORM_ERROR = {EN: "modify apply group form error",
                                  ZH_CN: u"修改申请组失败"}
ERR_MSG_DELETE_APPLY_GROUP_FORM_ERROR = {EN: "delete apply group form  %s error",
                                  ZH_CN: u"删除申请组 %s 失败"}
ERR_MSG_INSERT_APPLY_GROUP_USER_FORM_ERROR = {EN: "insert apply group user form error",
                                  ZH_CN: u"添加申请组用户失败"}
ERR_MSG_REMOVE_APPLY_GROUP_USER_FORM_ERROR = {EN: "remove apply group user form error",
                                  ZH_CN: u"移除申请组用户失败"}
ERR_MSG_INSERT_APPLY_GROUP_RESOURCE_FORM_ERROR = {EN: "insert apply group resource form error",
                                  ZH_CN: u"添加申请组资源失败"}
ERR_MSG_REMOVE_APPLY_GROUP_RESOURCE_FORM_ERROR = {EN: "remove apply group resource form error",
                                  ZH_CN: u"移除申请组资源失败"}
ERR_MSG_REMOVE_DELETE_APPLY_GROUP_HAVE_USER_ERROR = {EN: "apply group have user, can not delete",
                                  ZH_CN: u"申请组中存在用户，不允许删除"}
ERR_MSG_REMOVE_DELETE_APPLY_GROUP_HAVE_RESOURCE_ERROR = {EN: "apply group have resource, can not delete",
                                  ZH_CN: u"申请组中存在资源，不允许删除"}
ERR_MSG_INSERT_APPLY_GROUP_USER_FORM_FAILED = {EN: "user %s in user group %s in the apply group, repeated additions are not allowed",
                                  ZH_CN: u"用户只能有申请角色或审批角色中的一种,该用户 %s 已经添加到申请组中用户组 %s，不允许重复添加"}
ERR_MSG_INSERT_APPLY_GROUP_USER_GROUP_FORM_FAILED = {EN: "user group %s user %s in the approve group, repeated additions are not allowed",
                                  ZH_CN: u"用户只能有申请角色或审批角色中的一种,该用户组 %s 中的用户 %s 已经添加到审批组，不允许重复添加"}
ERR_MSG_USER_EXISTED_IN_APPLY_GROUP = {EN: "user %s existed in apply group",
                                  ZH_CN: u"用户 %s 已经加入申请组"}
ERR_MSG_USER_GROUP_EXISTED_IN_APPLY_GROUP = {EN: "user group %s existed in apply group",
                                  ZH_CN: u"用户组 %s 已经加入申请组"}
ERR_MSG_RESOURCE_EXISTED_IN_APPLY_GROUP = {EN: "resource %s existed in apply group",
                                  ZH_CN: u"资源 %s 已经加入申请组"}
#approve group
ERR_MSG_APPROVE_GROUP_NAME_EXISTED_ERROR = {EN: "approve group name %s is existed",
                                  ZH_CN: u"审批组名称 %s 已经存在"}
ERR_MSG_APPROVE_GROUP_FORM_NO_FOUND = {EN: "approve group %s no found",
                                  ZH_CN: u"审批组 %s 不存在"}
ERR_MSG_CREATE_APPROVE_GROUP_FORM_ERROR = {EN: "create approve group form failed",
                                  ZH_CN: u"创建审批组失败"}
ERR_MSG_CREATE_APPROVE_GROUP_FORM_EXISTED_ERROR = {EN: "approve group %s is existed",
                                  ZH_CN: u"审批组 %s 已经存在"}
ERR_MSG_MODIFY_APPROVE_GROUP_FORM_ERROR = {EN: "modify approve group form error",
                                  ZH_CN: u"修改审批组失败"}
ERR_MSG_DELETE_APPROVE_GROUP_FORM_ERROR = {EN: "delete approve group form error",
                                  ZH_CN: u"删除审批组失败"}
ERR_MSG_INSERT_APPROVE_GROUP_USER_FORM_ERROR = {EN: "insert approve group user form error",
                                  ZH_CN: u"添加审批组用户失败"}
ERR_MSG_REMOVE_APPROVE_GROUP_USER_FORM_ERROR = {EN: "remove approve group user form error",
                                  ZH_CN: u"移除审批组用户失败"}
ERR_MSG_MAP_APPLY_GROUP_AND_APPROVE_GROUP_ERROR = {EN: "map apply group and approve error",
                                  ZH_CN: u"关联申请组和审批组失败"}
ERR_MSG_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP_ERROR = {EN: "unmap apply group and approve error",
                                  ZH_CN: u"取消关联申请组和审批组失败"}
ERR_MSG_USER_NOT_IN_APPROVE_GROUP = {EN: "user not in approve group",
                                  ZH_CN: u"用户不在审批组"}
ERR_MSG_INSERT_APPROVE_GROUP_USER_FORM_ERROR = {EN: "insert approve group user form error",
                                  ZH_CN: u"添加审批组用户失败"}
ERR_MSG_USER_EXISTED_IN_APPROVE_GROUP = {EN: "user %s existed in approve group",
                                  ZH_CN: u"用户 %s 已经加入审批组"}
ERR_MSG_INSERT_APPROVE_GROUP_USER_FORM_FAILED = {EN: "user %s in user group %s in the approve group, repeated additions are not allowed",
                                  ZH_CN: u"用户只能有申请角色或审批角色中的一种,该用户 %s 已经添加到审批组中用户组 %s，不允许重复添加"}
ERR_MSG_INSERT_APPROVE_GROUP_USER_GROUP_FORM_FAILED = {EN: "user group %s user %s in the apply group, repeated additions are not allowed",
                                  ZH_CN: u"用户只能有申请角色或审批角色中的一种,该用户组 %s 中的用户 %s 已经添加到申请组，不允许重复添加"}
ERR_MSG_APPLY_GROUP_MAPED_OTHER_APPROVE_GROUP = {EN: "apply group %s maped other approve group %s",
                                  ZH_CN: u"申请组 %s 已经关联了其他审批组 %s"}
# component version
ERR_MSG_DESCRIBE_COMPONENT_VERSION_ERROR = {EN: "describe component version info error",
                                            ZH_CN: u"查询组件版本信息失败"}
ERR_MSG_UPDATE_COMPONENT_VERSION_ERROR = {EN: "update component version info error",
                                          ZH_CN: u"更新组件版本信息失败"}

# desktop group
ERR_MSG_INSTANCE_CLASS_NO_FOUND_CORRESPONDING_DISK_TYPE = {EN: "instance_class %s no found corresponding disk_type",
                                    ZH_CN: u"主机类型 %s 没有发现对应的硬盘类型"}
ERR_MSG_NO_DESKTOP_IN_DESKTOP_GROUP = {EN: "no desktop in desktop group %s",
                                  ZH_CN: u"桌面组%s没有桌面"}
ERR_MSG_UNSUPPORTED_NETWORK_TYPE = {EN: "unspport network type %s",
                                  ZH_CN: u"不支持网络类型 %s"}
ERR_MSG_DESKTOP_STAUTS_DISMATCH = {EN: "destkop %s status %s dismatch",
                              ZH_CN: u"桌面 %s 需要状态 %s 才可以操作"}
ERR_MSG_NO_ENOUGH_GPU_COUNT = {EN: "no enough gpu count, only left %s gpus",
                                  ZH_CN: u"没有足够的GPU资源，只剩余 %s 个"}
ERR_MSG_UNSUPPORTED_DESKTOP_GROUP_MODE = {EN: "illegal desktop group mode %s, only support 'normal', 'maint'",
                                  ZH_CN: u"非法的桌面组模式 %s，仅支持 'normal', 'maint'"}
ERR_MSG_UNSUPPORTED_DESKTOP_GROUP_USER_STATUS = {EN: "illegal desktop group user status %s, only support 'active', 'disabled'",
                                  ZH_CN: u"非法的桌面组用户状态 %s，仅支持 'active', 'disabled'"}
ERR_MSG_DESKTOP_GROUP_STATUS_DISMATCH = {EN: "The desktop group is in maintenance state, please switch to normal state first",
                                  ZH_CN: u"桌面组正在处于维护状态 ，请先切换到正常状态"}
ERR_MSG_ILLEGAL_OS_DISK_SIZE = {EN: "illegal os disk size  %s ",
                             ZH_CN: u"非法系统盘大小 %s ，取值在区间 [50, 100]"}

ERR_MSG_VDI_DESKTOP_NETWORK_MISSING_PARAMETER = {EN: "network config missing parameter",
                         ZH_CN: u"网络的配置缺少参数"}
ERR_MSG_UNSUPPORTED_DESKTOP_GROUP_TYPE = {EN: "illegal desktop group type %s, only support 'personal', 'random','static'",
                                  ZH_CN: u"非法的桌面组类型 %s，仅支持 'personal','random','static', 'citrix'"}
ERR_MSG_DESKTOP_GROUP_TYPE_DISMATCH_PLATFORM = {EN: "platform desktop group type %s dismatch",
                                  ZH_CN: u"平台的桌面组类型 %s 不匹配"}
ERR_MSG_DESKTOP_GROUP_TYPE_DISMATCH = {EN: "desktop group type %s dismatch",
                                  ZH_CN: u"桌面组类型 %s 不匹配"}
ERR_MSG_DESKTOP_COUNT_EXCEEDS_MAXIMUM_LIMIT = {EN: "desktop count %s exceeds the maximum limit.",
                                                ZH_CN: u"桌面数量 %s 超出允许的最大限制"}
ERR_MSG_ILLEGAL_INSTANCE_CLASS = {EN: "Illegal instance class  %s",
                                  ZH_CN: u"非法的桌面主机类型 %s"}
ERR_MSG_DESKTOP_GROUP_NEED_APPLY = {EN: "desktop group %s  need apply",
                          ZH_CN: u"桌面组 %s 需要应用修改"}
ERR_MSG_DESKTOP_HAS_UPDATE_CANT_START= {EN: "desktop %s has update, cant start",
                          ZH_CN: u"桌面 %s 有更新, 不能启动"}
ERR_MSG_NO_FOUND_DESKTOP_IN_DESKTOP_GROUP = {EN: "no found desktop %s  in desktop group",
                          ZH_CN: u"没有找到桌面 %s 的桌面组"}
ERR_MSG_NO_FOUND_USER_IN_DESKTOP_GROUP = {EN: "in desktop group %s ，no found user %s ",
                          ZH_CN: u"在桌面组 %s ,没有找到用户 %s "}
ERR_MSG_ONLY_NEED_RANDOM_DESKTOP_GROUP = {EN: "desktop group %s is not random",
                          ZH_CN: u"桌面组 %s 不是随机桌面组"}
ERR_MSG_NO_ENOUGH_DESKTOP = {EN: "no enough desktop in desktop group %s ",
                          ZH_CN: u"桌面组 %s 没有足够的桌面"}
ERR_MSG_HAS_RANDOM_DESKTOP = {EN: "user %s has desktop in desktop group %s ",
                          ZH_CN: u"用户 %s 有桌面组 %s 的随机桌面"}
ERR_MSG_ILLEGAL_CPU = {EN: "illegal cpu cores  %s ",
                           ZH_CN: u"非法的CPU核心数 %s "}
ERR_MSG_ILLEGAL_MEMORY_SIZE = {EN: "illegal memory size  %s MB ",
                               ZH_CN: u"非法的内存大小 %s MB "}

ERR_MSG_MODIFY_MODE_NEED_IS_APPLY = {EN: "modify mode, need to apply desktop group %s ",
                               ZH_CN: u"修改桌面组 %s 模式，需要先应用修改"}
ERR_MSG_NO_FOUND_DESKTOP_GROUP = {EN: "no found desktop group %s ",
                               ZH_CN: u"没有找到桌面组 %s "}
ERR_MSG_ADD_COMPUTE_TO_DESKTOP_GROUP_FAILED = {EN: "add compute %s to desktop group %s fail",
                               ZH_CN: u"添加应用服务器 %s 到桌面组 %s 失败 "}
ERR_MSG_HAS_RESOURCE_IN_DESKTOP_GROUP = {EN: "desktop group %s has resource %s ,dont delete",
                               ZH_CN: u"桌面组 %s 有资源 %s ,不能删除"}
ERR_MSG_DESKTOP_GROUP_USING_THE_IMAGE = {EN: "desktop group %s  are using the image %s ",
                              ZH_CN: u"桌面组 %s 正在使用镜像 %s "}
ERR_MSG_DESKTOP_IMAGE_IN_TRANS_STATUS = {EN: "desktop image %s  in trasn status ",
                              ZH_CN: u"桌面镜像 %s 任务尚未结束，请稍后处理 "}
ERR_MSG_ILLEGAL_GPU_COUNT = {EN: "illegal gpu count  %s ",
                             ZH_CN: u"非法的 GPU 个数  %s "}
ERR_MSG_ILLEGAL_GPU_CLASS_VALUE = {EN: "illegal gpu class value  %s , value range %s",
                                   ZH_CN: u"非法的 GPU CLASS 值 %s ， 正确值为 %s"}
ERR_MSG_ILLEGAL_HOST_NAME = {EN: "illegal host name  %s ",
                             ZH_CN: u"非法的主机名格式 %s "}
ERR_MSG_ILLEGAL_DESKTOP_GROUP_NAME = {EN: "illegal desktop group name  %s ",
                             ZH_CN: u"非法的桌面组名格式 %s "}
ERR_MSG_DESKOTP_HOSTNAME_ALREADY_EXISTED = {EN: "destkop hostname %s already existed",
                             ZH_CN: u"桌面计算机名称 %s 已经存在"}
ERR_MSG_MAX_GPU_COUNT = {EN: "You can only attach %s gpu for each instance",
                         ZH_CN: u"每台主机最多绑定 %s 个GPU资源"}
ERR_MSG_ILLEGAL_IVSHMEM_CONFIG = {EN: "no found ivshmem config",
                         ZH_CN: u"没有找到ivshmem配置 "}
ERR_MSG_DESKTOP_DN_CONFIG = {EN: "no found desktop dn config",
                         ZH_CN: u"没有找到组织单元路径 "}
ERR_MSG_VOLUME_IN_USED_CANT_DELETE = {EN: "volume %s in-use, cant to delete",
                              ZH_CN: u"硬盘 %s 正在使用, 不能删除"}
ERR_MSG_VOLUME_SIZE_NEED_GT_ORIG_SIZE = {EN: "modify volume %s  size need greater than the original size",
                              ZH_CN: u"修改硬盘 %s 大小需要大于原有大小"}
ERR_MSG_SEND_GUEST_MESSAGE_ERROR = {EN: "send guest message error",
                              ZH_CN: u"发送桌面主机消息失败"}
ERR_MSG_CREATE_CONN_FILE_ERROR = {EN: "create connection file error",
                              ZH_CN: u"创建连接文件失败"}
ERR_MSG_UNSUPPORTED_DELIVERY_GROUP_TYPE = {EN: "illegal delivery group type %s, only support 'SingleSession', 'MultiSession'",
                                  ZH_CN: u"非法的交付组类型 %s，仅支持 'SingleSession','MultiSession'"}
ERR_MSG_UNSUPPORTED_CITRIX_ALLOC_TYPE = {EN: "illegal allocation type %s, only support 'Static', 'Random'",
                                  ZH_CN: u"非法的计算机目录类型 %s，仅支持 'Static','Random'"}
ERR_MSG_HIDE_MODE_VALUE_ERROR = {EN: "hide mode %s, only support 0, 1",
                                  ZH_CN: u"非法的参数值 %s，仅支持 0, 1"}
ERR_MSG_UNSUPPORTED_CITRIX_DELIVERY_TYPE = {EN: "illegal delivery type %s, only support 'DesktopsOnly', 'DesktopsAndApps'",
                                  ZH_CN: u"非法的交付类型 %s，仅支持 'DesktopsOnly', 'DesktopsAndApps'"}
ERR_MSG_RESOURCE_LIMIT_NO_CONFIG = {EN: "resource limit no config",
                                  ZH_CN: u"没有 resource limit 配置"}
ERR_MSG_DESKTOP_LIMIT_NO_CONFIG = {EN: "desktop limit no config",
                                  ZH_CN: u"没有 desktop limit 配置"}
ERR_MSG_RESOURCE_LIMIT_NO_ZONE_CONFIG = {EN: "resource limit no zone %s config",
                                  ZH_CN: u"没有 zone %s 的 resource limit 配置"}
ERR_MSG_NO_FOUND_ZONE_INFO = {EN: "no found zone %s info",
                                  ZH_CN: u"没有找到zone %s 信息"}
ERR_MSG_ZONE_STATUS_DISABLE = {EN: "zone %s status is not active",
                                  ZH_CN: u"Zone %s 状态非活跃"}
ERR_MSG_ZONE_CONFIG_EXISTED = {EN: "zone %s config existed",
                                  ZH_CN: u"Zone %s 配置已经存在"}
ERR_MSG_ZONE_CONFIG_NOT_EXISTED = {EN: "zone %s config not existed",
                                  ZH_CN: u"Zone %s 配置不存在"}
ERR_MSG_NO_FOUND_ZONE_CONFIG = {EN: "no found zone config",
                                  ZH_CN: u"没有找到 zone 配置"}
ERR_MSG_ZONE_CONFIG_DISK_TYPE_DISMATCH = {EN: "zone %s config disk type %s dismatch",
                                  ZH_CN: u"Zone %s 配置数据盘类型 %s 不匹配"}
ERR_MSG_ZONE_CONFIG_DISK_SIZE_DISMATCH = {EN: "zone %s config disk size %s dismatch",
                                  ZH_CN: u"Zone %s 配置数据盘大小 %s 不匹配"}
ERR_MSG_ZONE_RESOURCE_LIMIT_NO_FOUND = {EN: "zone %s resource limit no found",
                                  ZH_CN: u"Zone %s resource limit 没有找到"}
ERR_MSG_ZONE_CONFIG_NO_FOUND_CITRIX_AREA = {EN: "zone %s config no found citrix area",
                                  ZH_CN: u"Zone %s 配置没有找到 citrix 托管资源配置"}
ERR_MSG_GROUP_NO_FOUND_MANAGED_RESOURCE = {EN: "group %s no found managed resource",
                                  ZH_CN: u"桌面组 %s 没有发现托管资源"}
ERR_MSG_ZONE_CONFIG_PLACE_GROUP_DISMATCH = {EN: "zone %s config place group %s dismatch",
                                  ZH_CN: u"Zone %s 配置安置组 %s 不匹配"}
ERR_MSG_ZONE_CONFIG_CPU_MEMORY_DISMATCH = {EN: "zone %s config CPU/MEMORY %s dismatch",
                                  ZH_CN: u"Zone %s 配置CPU/内存 %s 不匹配"}
ERR_MSG_ZONE_CONFIG_GPU_COUNT_DISMATCH = {EN: "zone %s config gpu count %s dismatch",
                                  ZH_CN: u"Zone %s 配置GPU %s 不匹配"}
ERR_MSG_ZONE_CONFIG_NETWORK_TYPE_DISMATCH = {EN: "zone %s config network type %s dismatch",
                                  ZH_CN: u"Zone %s 配置网络 %s 不匹配"}
# scheduler
ERR_MSG_ILLEGAL_SCHEDULER_PARAMETER = {
    EN: "illegal scheduler parameter %s ",
    ZH_CN: u"非法的定时器参数 %s ",
}
ERR_MSG_ADD_SCHEDULER_TASKS_FAILED = {
    EN: "add scheduler tasks failed",
    ZH_CN: u"添加定时器任务失败",
}
ERR_MSG_ACTIVATE_SCHEDULER_TASK_FAILED = {
    EN: "activate scheduler task failed",
    ZH_CN: u"启用定时器任务失败",
}
ERR_MSG_INACTIVATE_SCHEDULER_TASK_FAILED = {
    EN: "inactivate scheduler task failed",
    ZH_CN: u"暂停定时器任务失败",
}
ERR_MSG_EXECUTING_SCHEDULER_TASK_FAILED = {
    EN: "executing scheduler task %s failed",
    ZH_CN: u"执行定时器任务 %s 失败",
}
ERR_MSG_SCHEDULER_HAVE_MAXIMUN_TASK_LIMIT = {
    EN: "one scheduler can only have %s tasks at most",
    ZH_CN: u"一个定时器最多只能设置 %s个任务",
}
ERR_MSG_UNSUPPORTED_TASK_TYPE = {EN: "illegal scheduler task type %s",
                                  ZH_CN: u"非法的定时任务类型 %s"}
ERR_MSG_SCHEDULER_ADD_TASK_NO_TASK_PARAM = {
    EN: "add scheduler %s task no task param",
    ZH_CN: u"添加定时任务 %s ，没有指定任务参数",
}

ERR_MSG_SCHEDULER_HAS_TASK_INCLUDE_DESKTOP = {
    EN: "scheduler %s has task include desktop %s",
    ZH_CN: u"定时任务 %s 中，已经有任务包含了桌面 %s ",
}
ERR_MSG_SCHEDULER_HAS_TASK_INCLUDE_DESKTOP_GROUP = {
    EN: "scheduler %s has task include desktop group %s ",
    ZH_CN: u"定时任务 %s 中，已经有任务包含了桌面组 %s ",
}
ERR_MSG_SCHEDULER_TASK_STILL_EXECUTING = {
    EN: "scheduler task  %s  is still executing",
    ZH_CN: u"定时器任务 %s 仍在执行中",
}
ERR_MSG_SCHEDULER_TASK_STATUS_DISMATCH = {
    EN: "scheduler task %s status dismatch %s",
    ZH_CN: u"定时器任务 %s 状态不匹配 %s",
}
ERR_MSG_SCHEDULER_TASK_RESOURCE_TYPE_DISMATCH = {
    EN: "scheduler task resource type dismatch %s",
    ZH_CN: u"定时器资源类型不匹配 %s",
}
ERR_MSG_SCHEDULER_TASK_NO_RESOURCE_TYPE = {
    EN: "scheduler task %s no resource type",
    ZH_CN: u"定时器任务 %s 没有资源类型",
}
ERR_MSG_RESOURCE_TYPE_DISMATCH = {
    EN: "resource %s type dismatch scheduler task %s, %s",
    ZH_CN: u"定时器任务 %s 和资源 %s 的类型不匹配 %s",
}

ERR_MSG_RESOURCE_ALREADY_EXISTED_SCHEDULER_TASK = {
    EN: "resource %s already existed in scheduler task %s",
    ZH_CN: u"资源 %s 已经在定时器任务 %s 中存在",
}
ERR_MSG_RESOURCE_NOT_IN_SCHEDULER_TASK = {
    EN: "resource %s not in scheduler task %s",
    ZH_CN: u"资源 %s 不在定时器任务 %s 中",
}
ERR_MSG_START_SCHEDULER_TASK_FAIL = {
    EN: "start scheduler task %s fail ",
    ZH_CN: u"启动定时器任务%s失败",
}
ERR_MSG_STOP_SCHEDULER_TASK_FAIL = {
    EN: "stop scheduler task %s fail ",
    ZH_CN: u"停止定时器任务%s失败",
}
ERR_MSG_TASK_TYPE_NO_SUPPORTED = {
    EN: "task type %s no supported",
    ZH_CN: u"定时器任务类型 %s不支持",
}
ERR_MSG_RENEW_SCHEDULER_TASK_FAIL = {
    EN: "renew scheduler task fail %s",
    ZH_CN: u"更新定时器任务 %s 失败",
}
ERR_MSG_EXECUTE_SCHEDULER_TASK_FAIL = {
    EN: "execute scheduler task fail %s",
    ZH_CN: u"执行定时器任务 %s 失败",
}
ERR_MSG_TASK_RESOURCE_NO_DESKTOP_COUNT= {
    EN: "task %s resource no desktop count",
    ZH_CN: u"更改桌面组桌面个数任务资源类型 %s缺少个数参数",
}
ERR_MSG_TASK_RESOURCE_NO_DESKTOP_IMAGE= {
    EN: "task %s resource no desktop image",
    ZH_CN: u"更改桌面组镜像任务资源类型 %s缺少个数参数",
}
ERR_MSG_TASK_RESOURCE_NO_IS_FULL_PARAMETER= {
    EN: "task %s resource no is_full parameter",
    ZH_CN: u"自动备份任务资源类型 %s缺少备份类型参数",
}
# request
ERR_MSG_ILLEGAL_PARAMETER_FORMAT = {EN: "parameter %s 's format is illegal",
                                    ZH_CN: u"参数 %s 的格式非法"}
ERR_MSG_PARAMETER_SHOULD_NOT_BE_NEGATIVE = {EN: "parameter %s should not be negative",
                                            ZH_CN: u"参数 %s 不能为负数"}
ERR_MSG_PARAMETER_SHOULD_BE_LIST = {EN: "parameter %s should be list",
                                    ZH_CN: u"参数 %s 应该为列表"}

ERR_MSG_PARAMETER_SHOULD_BE_UTCTIME = {EN: "parameter %s should be UTC time format: [YYYY-MM-DDThh:mm:ssZ]",
                                       ZH_CN: u"参数 %s 应该为UTC时间格式: [YYYY-MM-DDThh:mm:ssZ]"}
ERR_MSG_PARAMETER_SHOULD_BE_STR = {EN: "parameter %s should be string",
                                       ZH_CN: u"参数 %s 应该为字符串"}
ERR_MSG_PARAMETER_VALUE_TOO_LONG = {EN: "parameter %s 's value length can not exceed  %s ",
                                    ZH_CN: u"参数 %s 的值长度不能超过 %s "}
ERR_MSG_PARAMETER_SHOULD_NOT_BE_EMPTY = {EN: "parameter %s should not be empty",
                                         ZH_CN: u"参数 %s 不应该为空"}
ERR_MSG_PARAMETER_SHOULD_BE_INTEGER = {EN: "parameter %s should be integer",
                                       ZH_CN: u"参数 %s 应该为整数"}
ERR_MSG_MISSING_PARAMETER = {EN: "missing parameter %s",
                             ZH_CN: u"缺少参数 %s"}
ERR_MSG_ILLEGAL_REQUEST = {EN: "illegal request",
                           ZH_CN: u"非法请求"}
ERR_MSG_INVALID_PARAMETER_VALUE = {EN: "invalid parameter value %s",
                                       ZH_CN: u"非法请求参数值 %s"}
ERR_MSG_UNSUPPORTED_PARAMETER_VALUE = {
    EN: "unsupported parameter %s value %s",
    ZH_CN: u"参数 %s 不支持值 %s",
}
ERR_MSG_UNSUPPORTED_PARAMETER = {
    EN: "unsupported parameter %s",
    ZH_CN: u"不支持的参数 %s",
}
ERR_MSG_CAN_NOT_HANDLE_REQUEST = {EN: "can't handle this request",
                                  ZH_CN: u"无法处理该请求"}

ERR_MSG_API_ACCESS_EXCEED_MAX_LIMIT = {EN: "action %s access exceed max limit",
                                  ZH_CN: u"%s 访问超出最大次数限制"}
ERR_MSG_ILLEGAL_CONSOLE_KEY = {EN: "illegal console key",
                               ZH_CN: u"非法的Console密钥"}
# action
ERR_MSG_TOO_MUCH_PENDING_JOBS = {EN: "too much pending jobs %s, disable new jobs",
                              ZH_CN: u"过多正在执行的任务 %s个， 禁止执行新的任务，请稍候操作"}
ERR_MSG_CREATE_JOB_FAILED = {EN: "create job failed",
                                  ZH_CN: u"创建任务失败"}
ERR_MSG_HANDLE_JOB_FAILED = {EN: "handle job failed %s",
                                  ZH_CN: u"Job处理失败 %s"}
# resource
ERR_MSG_CLOUD_RESOURCE_RETURN_ERROR = {EN: "cloud resource %s return error",
                              ZH_CN: u"后端服务处理 %s 返回异常，请定位分析后再处理"}
ERR_MSG_MODIFY_RESOURCE_ATTRIBUTES_FAILED = {EN: "modify resource %s attributes failed",
                                             ZH_CN: u"修改资源 %s 属性失败"}
ERR_MSG_UPDATE_RESOURCE_FAILED = {EN: "update resource failed",
                                  ZH_CN: u"更新资源失败"}
ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED = {EN: "update cloud %s resource failed",
                                  ZH_CN: u"更新云资源 %s 失败"}
ERR_MSG_CREATE_RESOURCE_FAILED = {EN: "create resource failed",
                                  ZH_CN: u"创建资源失败"}
ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED = {EN: "create cloud resource %s failed",
                                  ZH_CN: u"创建云资源 %s 失败"}
ERR_MSG_DELETE_CLOUD_RESOURCE_FAILED = {EN: "delete cloud resource %s failed",
                                  ZH_CN: u"删除云资源 %s 失败"}
ERR_MSG_RESOURCE_ACCESS_DENIED = {EN: "user %s access denied for resource %s",
                                  ZH_CN: u"用户 %s 拒绝访问资源 %s "}
ERR_MSG_RESOURCE_NOT_FOUND_OR_NOT_SAME = {EN: "resource %s not found or resource type not the same",
                                  ZH_CN: u"资源 %s 没有找到或者资源类型不一致"}
ERR_MSG_DESC_RESOURCE_FAILED = {EN: "describe resource failed",
                                ZH_CN: u"查询资源失败"}
ERR_MSG_DDC_DESC_RESOURCE_FAILED = {EN: "describe ddc resource failed",
                                ZH_CN: u"查询DDC资源失败"}
ERR_MSG_NO_RESOURCE_SPECIFIED = {EN: "no resource specified",
                                 ZH_CN: u"没有指定资源"}
ERR_MSG_RESOURCE_NOT_FOUND = {EN: "resource %s not found",
                              ZH_CN: u"资源 %s 没有找到"}
ERR_MSG_RESOURCE_STATUS_INVAILD = {EN: "resource %s status invaild",
                              ZH_CN: u"资源 %s 状态异常"}
ERR_MSG_CLOUD_RESOURCE_NOT_FOUND = {EN: "cloud resource %s not found",
                              ZH_CN: u"云资源 %s 没有找到"}
ERR_MSG_CLOUD_RESOURCE_STATUS_INVAILD = {EN: "cloud resource %s status invaild",
                              ZH_CN: u"云资源 %s 状态异常"}
ERR_MSG_CLOUD_RESOURCE_IP_RANGE_DISMATCH = {EN: "cloud resource %s IP Range dismatch",
                              ZH_CN: u"云资源 %s IP 范围不匹配"}
ERR_MSG_RESOURCE_ALREADY_EXISTED = {EN: "resource already existed",
                                    ZH_CN: u"资源已存在"}
ERR_MSG_SYSTEM_IMAGE_ALREADY_EXISTED = {EN: "system image %s already existed",
                                    ZH_CN: u"系统镜像 %s 已存在"}
ERR_MSG_IMAGE_SIZE_LESS_THAN_BASE_IMAGE = {EN: "image size less than base image ",
                                  ZH_CN: u"系统镜像不能小于原镜像"}
ERR_MSG_DEFAULT_IMAGE_CANT_BE_DELET_OR_MODIFY = {EN: "default image %s cant be delete or modify",
                                    ZH_CN: u"缺省镜像%s 不能被删除或者修改"}
ERR_MSG_OS_IMAGE_SIZE_DISMATCH = {EN: "os disk size %s with image size %s dismatch",
                                    ZH_CN: u"系统硬盘大小 %s 和镜像 %s 不匹配"}
ERR_MSG_IMAGE_SIZE_FEATURE_CANT_SUPPORT_RESIZE = {EN: "image feature cant support resize image size",
                                    ZH_CN: u"镜像feature不支持更改系统盘大小"}
ERR_MSG_DELETE_RESOURCE_FAILED = {EN: "delete resource failed",
                                  ZH_CN: u"删除资源失败"}
ERR_MSG_USER_HAS_DESKTOP_RESOURCE_CANT_DELETE = {EN: "user %s has desktop resource, cant delete",
                                  ZH_CN: u"用户 %s 有桌面资源,不能删除用户"}
ERR_MSG_USER_IN_DESKTOP_GROUP_RESOURCE_CANT_DELETE = {EN: "user [%s] in desktop group %s, cant delete",
                                                      ZH_CN: u"用户 [%s] 在于桌面组 %s, 不能删除用户"}
ERR_MSG_DELETE_SCOPE_RESOURCE_FAILED = {EN: "delete scope resource[%s] failed",
                                  ZH_CN: u"删除资源[%s]权限失败"}
ERR_MSG_INSTANCE_CREATE_BROKER_FAILED = {EN: "instance %s create broker failed",
                              ZH_CN: u"桌面 %s 创建连接失败"}
ERR_MSG_RESOURCE_NEED_UPDATE = {EN: "resource %s need update",
                              ZH_CN: u"资源 %s 需要先更新"}

ERR_MSG_CREATE_APP_PARAM_ERROR = {EN: "create broker app param error",
                              ZH_CN: u"创建应用程序参数错误"}
ERR_MSG_CITIRX_ALLOC_TYPE_DISMATCH = {EN: "computer catalog type dismatch %s",
                                  ZH_CN: u"计算机目录类型不正确 %s"}
ERR_MSG_CITIRX_DESKTOP_IN_DELIVERY_GROUP = {EN: "citrix desktop %s in delivery group %s",
                                  ZH_CN: u"桌面 %s 在交付组 %s 中，不能删除"}
ERR_MSG_CITIRX_APP_ONLY_SUPPORT_MULTISESSION = {EN: "citrix app only support multisession",
                                  ZH_CN: u"虚拟应用只支持多会话桌面"}
# snapshot
ERR_MSG_SNAPSHOT_NO_DESKTOP_INSTANCE = {EN: "snapshot no desktop instance %s",
                                    ZH_CN: u"桌面 %s 没有主机资源不能备份"}
ERR_MSG_SNAPSHOT_NO_DISK_VOLUME = {EN: "snapshot no disk volume %s",
                                    ZH_CN: u"数据盘 %s 没有硬盘资源不能备份"}
ERR_MSG_RESOURCE_ALREAY_EXISTED_SNAPSHOT_GROUP = {EN: "resource %s has already existed in snapshot group %s",
                                    ZH_CN: u"资源 %s 已经存在于备份组 %s 中"}
ERR_MSG_RESOURCE_NOT_IN_SNAPSHOT_GROUP = {EN: "resource %s not in snapshot group %s",
                                    ZH_CN: u"资源 %s 不存在于备份组 %s 中"}
ERR_MSG_SNAPSHOT_EXCEED_MAX_CHAIN_COUNT = {EN: "snapshot exceed max chain count %s, %s",
                                    ZH_CN: u"超出最大备份链数目 %s, %s"}
ERR_MSG_SNAPSHOT_LIMIT_CONFIG_NO_FOUND = {EN: "snapshot limit no found",
                                    ZH_CN: u"备份资源限制没有配置"}
ERR_MSG_SNAPSHOT_EXCEED_MAX_COUNT = {EN: "single full backup chain snapshot exceed max count %s, %s",
                                    ZH_CN: u"单个全量备份链超出最大备份数目 %s, %s"}
ERR_MSG_CREATE_SNAPSHOT_GROUP_FAILED = {EN: "create snapshot group failed",
                                    ZH_CN: u"创建备份组失败"}
ERR_MSG_CREATE_SNAPSHOT_GROUP_RESOURCE_FAILED = {EN: "create snapshot group resource failed",
                                    ZH_CN: u"创建备份组资源失败"}
ERR_MSG_SNAPSHOT_GROUP_NO_FOUND = {EN: "snapshot group no found %s",
                                    ZH_CN: u"没有发现备份组 %s"}
ERR_MSG_DELETE_SNAPSHOT_GROUP_FAILED = {EN: "delete snapshot group failed %s",
                                    ZH_CN: u"删除备份组失败 %s"}
ERR_MSG_DELETE_SNAPSHOT_GROUP_RESOURCE_FAILED = {EN: "delete snapshot group resource failed %s",
                                    ZH_CN: u"删除备份组资源失败 %s"}
ERR_MSG_DELETE_SNAPSHOT_GROUP_SNAPSHOT_FAILED = {EN: "delete snapshot group snapshot failed %s",
                                    ZH_CN: u"删除备份组备份节点失败 %s"}
ERR_MSG_MODIFY_SNAPSHOT_GROUP_FAILED = {EN: "modify snapshot group failed %s",
                                    ZH_CN: u"修改备份组失败 %s"}
ERR_MSG_DESCRIBE_SNAPSHOT_GROUP_FAILED = {EN: "describe snapshot group failed",
                                    ZH_CN: u"查询备份组失败"}
ERR_MSG_SNAPSHOT_GROUP_RESOURCE_NO_FOUND = {EN: "snapshot group resource no found %s",
                                    ZH_CN: u"没有发现备份组资源 %s"}
ERR_MSG_MODIFY_SNAPSHOT_GROUP_RESOURCE_FAILED = {EN: "modify snapshot group resource failed %s",
                                    ZH_CN: u"修改备份组资源失败 %s"}
ERR_MSG_CREATE_SNAPSHOT_GROUP_SNAPSHOT_FAILED = {EN: "create snapshot group snapshot failed",
                                    ZH_CN: u"备份组备份失败"}
ERR_MSG_DESKTOP_SNAPSHOT_NO_FOUND = {EN: "desktop snapshot no found %s",
                                    ZH_CN: u"没有发现备份 %s"}


# disk
ERR_MSG_DISK_CONFIG_NAME_ALREADY_EXISTED = {EN: "disk config name %s already existed",
                                    ZH_CN: u"硬盘配置前缀 %s 已经存在"}
ERR_MSG_NEED_SPECIFY_VOLUME_COUNT = {EN: "need specify volume deskop",
                             ZH_CN: u"创建硬盘需要指定主机"}
ERR_MSG_CREATE_VOLUME_COUNT_LIMIT = {EN: "at the most, you cant only create %s bucks",
                             ZH_CN: u"硬盘最多一次只能创建 %s 块"}
ERR_MSG_DISK_SIZE_EXCEEDS_DISK_LIMIT = {EN: "disk size %s exceeds the disk limit %s.",
                                                ZH_CN: u"硬盘大小 %s 超出允许的限制范围 %s"}
ERR_MSG_DISK_SIZE_EXCEEDS_MAXIMUM_LIMIT = {EN: "desktop group %s disk size %s exceeds the maximum limit.",
                                                ZH_CN: u"桌面组 %s 硬盘大小 %s 超出允许的最大限制"}
ERR_MSG_DISK_COUNT_EXCEEDS_MAXIMUM_LIMIT = {EN: "desktop group %s disk count exceeds the maximum limit %s .",
                                                ZH_CN: u"硬盘个数超出允许的最大限制 %s "}
ERR_MSG_HP_VOLUME_HAS_SIZE_STEP_LIMIT = {EN: "high performance volume size step should be %s GB",
                                         ZH_CN: u"性能型硬盘容量的步长必须为 %s GB "}
ERR_MSG_HC_VOLUME_HAS_SIZE_STEP_LIMIT = {EN: "high capacity volume size step should be %s GB",
                                         ZH_CN: u"容量型硬盘容量的步长必须为 %s GB"}
ERR_MSG_HP_VOLUME_HAS_MIN_SIZE_LIMIT = {EN: "high performance volume minimum size should be %s GB",
                                        ZH_CN: u"性能型硬盘的最小容量必须为 %s GB"}
ERR_MSG_HC_VOLUME_HAS_MIN_SIZE_LIMIT = {EN: "high capacity volume minimum size should be %s GB",
                                        ZH_CN: u"容量型硬盘的最小容量必须为 %s GB"}
ERR_MSG_HP_VOL_CAN_ONLY_ATTACH_TO_HP_INSTANCE = {EN: "high performance volume %s can only be attached to high performance instance",
                                                 ZH_CN: u"性能型硬盘 %s 只能绑定到性能型主机"}
ERR_MSG_HP_PLUS_VOL_CAN_ONLY_ATTACH_TO_HP_PLUS_INSTANCE = {EN: "high performance plus volume %s can only be attached to high performance plus instance",
                                                           ZH_CN: u"超高性能型硬盘 %s 只能绑定到超高性能型主机"}
ERR_MSG_VOLUME_ALREADY_ATTACH_TO_DESKTOP = {EN: "volume %s already attach to desktop %s",
                                                           ZH_CN: u"硬盘 %s 已经挂载到桌面 %s 上"}
ERR_MSG_DISK_NO_ATTACH_IN_DESKTOP = {EN: "disk %s no attach in desktop",
                                                           ZH_CN: u"硬盘 %s 没有挂载在桌面上"}
ERR_MSG_DISK_NEW_SIZE_SHOULD_LARGER_THAN_OLD_SIZE = {EN: "disk %s 's new size %s GB should larger than the old size %s GB",
                                                       ZH_CN: u"硬盘 %s 的新容量 %s GB 必须大于旧容量 %s GB"}
ERR_MSG_DISK_SIZE_DISMATCH = {EN: "disk size %s not in range %s",
                                            ZH_CN: u"硬盘容量 %s 不在范围%s"}
ERR_MSG_VOLUME_STATUS_NEED_AVAIL = {EN: "volume %s status is not available",
                                                           ZH_CN: u"硬盘 %s 状态需要可用状态"}
ERR_MSG_RESOURCE_IN_TRANSITION_STATUS = {EN: "resource %s is %s, please try later",
                                         ZH_CN: u"资源 %s 正在 %s 中, 请稍候再试"}
ERR_MSG_DISK_STATUS_DISMATCH = {EN: "disk %s status [%s] [%s] dismatch",
                              ZH_CN: u"硬盘 %s 状态 [%s] [%s]不匹配"}
ERR_MSG_SCHETASK_NO_TASK_PARAM = {EN: "schetask %s no specify task param %s",
                                ZH_CN: u"定时任务 %s的资源 %s 没有指定 task param"}
ERR_MSG_SCHETASK_NO_TASK_RESOURCE = {EN: "schetask %s no task resource %s",
                                ZH_CN: u"定时任务 %s 没有任务资源"}
ERR_MSG_DESKTOP_NO_INSTANCE_RESOURCE = {EN: "desktop %s no instance resource",
                                ZH_CN: u"桌面%s没有主机资源"}
ERR_MSG_DISK_NO_VOLUME_RESOURCE = {EN: "disk %s no volume resource",
                                ZH_CN: u"数据盘%s没有硬盘资源"}
# network
ERR_MSG_ILLEGAL_IP_NETWORK = {EN: "illegal IP network %s",
                              ZH_CN: u"非法的IP网络地址 %s"}
ERR_MSG_ILLEGAL_DYN_IP_START_SHOULD_SMALLER_THAT_IP_END = {EN: "DHCP starting IP address %s should be smaller that ending address %s",
                                                           ZH_CN: u"DHCP的起始地址 %s 需要小于终止地址 %s"}
ERR_MSG_ILLEGAL_IP = {EN: "illegal IP address %s",
                      ZH_CN: u"非法的IP地址 %s "}
ERR_MSG_NETWORK_ALREADY_EXISTED = {EN: "network %s already existed ",
                      ZH_CN: u"网络 %s 已经存在"}
ERR_MSG_NEED_ROUTER_CONFIG = {EN: "managed network %s no router config ",
                      ZH_CN: u"私有网络 %s 需要路由器配置"}
ERR_MSG_ROUTER_CONFIG_ERROR = {EN: "managed network router config error",
                      ZH_CN: u"私有网络路由器配置错误"}
ERR_MSG_NETWORK_TYPE_CONFIG_NO_FOUND = {EN: "network type config no found",
                      ZH_CN: u"服务没有配置可用网络类型"}
ERR_MSG_UNSPPORTED_NETWORK_TYPE = {EN: "unsupported network type %s",
                      ZH_CN: u"不支持网络类型 %s"}
ERR_MSG_IP_NETWORK_NO_IN_ROUTER_NETWORK = {EN: "ip network %s not in router network %s",
                      ZH_CN: u"私有网络 %s 不匹配路由器网络 %s"}
ERR_MSG_ILLEGAL_DHCP_IP = {EN: "illegal DHCP IP address",
                           ZH_CN: u"非法的DHCP地址"}
ERR_MSG_ILLEGAL_MANAGER_IP = {EN: "illegal manager IP address",
                              ZH_CN: u"非法的管理地址"}
ERR_MSG_EXCEED_THE_MAX_DESKTOP_COUNT = {EN: "the count to create the desktop is %s",
                              ZH_CN: u"可以创建的桌面数量为 %s"}
ERR_MSG_EXCEED_MAX_VOLUME_COUNT = {EN: "exceed the max volume count limit %s",
                              ZH_CN: u"超过最大允许的硬盘数量 %s"}
ERR_MSG_ALLOC_NETWORK_NIC_FAILED = {EN: "desktop %s alloc network nic failed",
                              ZH_CN: u"桌面 %s 分配网络IP失败"}
ERR_MSG_RESOURCE_IN_THE_SAME_NETWORK = {EN: "resource %s has the same type network %s",
                              ZH_CN: u"资源 %s 已加入相同类型的网络 %s "}
ERR_MSG_DESKTOP_GROUP_HAS_THE_SAME_TYPE_NETWORK = {EN: "desktop group has the same type network %s",
                              ZH_CN: u"桌面组已有相同类型的网络 %s"}
ERR_MSG_NIC_STATUS_IN_USE = {EN: "Nic %s status in use",
                              ZH_CN: u"有网卡 %s 在使用中 "}
ERR_MSG_NETWORK_NIC_ALREADY_EXISTED = {EN: "network ip  %s already existed.",
                                     ZH_CN: u"网络IP %s 已经存在."}
ERR_MSG_NETWORK_NIC_NO_IP_OR_IN_TRANS_STATUS = {EN: "nic %s no ip or in trans status",
                                     ZH_CN: u"网卡 %s 正在获取IP或者网卡正在执行中"}
ERR_MSG_BASE_NETWORK_NOT_EXISTED = {EN: "base network %s not existed.",
                                     ZH_CN: u"基础网络 %s 不存在."}
ERR_MSG_NETWORK_NIC_STAUTS_INUSE = {EN: "network nics %s in used.",
                                     ZH_CN: u"网络IP地址 %s 正在使用"}
ERR_MSG_NETWORK_CONFIG_INUSE_NIC = {EN: "network config %s in-use nic %s",
                                     ZH_CN: u"桌面组IP配置 %s 正在使用网卡 %s"}
ERR_MSG_NETWORK_STATUS_INVAILD = {EN: "network status %s invaild",
                                     ZH_CN: u"网络 %s 状态不可用"}
ERR_MSG_NETWORK_IN_USED = {EN: "network %s in used",
                                     ZH_CN: u"网络 %s 已经被使用"}
ERR_MSG_NETWORK_HAS_RESOURCE_IN_USED = {EN: "network %s has resource in-used",
                                     ZH_CN: u"网络 %s 被资源正在使用"}
ERR_MSG_VDI_DESKTOP_NETWORK_MISSING_PARAMETER = {EN: "desktop group network %s config missing parameter",
                                                 ZH_CN: u"桌面组网络 %s 的配置缺少参数"}
ERR_MSG_DHCP_IP_NOT_IN_NETWORK = {EN: "IP address you provided %s not in IP network %s",
                                  ZH_CN: u"你提供的IP %s 不在网络地址范围 %s 内"}
ERR_MSG_ILLEGAL_START_END_IP_ADDRESS = {EN: "illegal start or end ip address %s, %s",
                                  ZH_CN: u"起始IP地址配置不正确 %s, %s"}
ERR_MSG_NAMING_RULE_EXISTED = {EN: "desktop name %s existed in desktop group",
                                  ZH_CN: u"桌面前缀 %s 已经存在桌面组中"}
ERR_MSG_DESKTOP_GROUP_NAMING_EXISTED = {EN: "desktop group name %s existed in desktop group",
                                  ZH_CN: u"桌面名称 %s 已经存在"}
ERR_MSG_BASE_NETWORK_NO_NIC_AVAIL = {EN: "base network %s no avail nic",
                                ZH_CN: u"基础网络 %s 没有可用网卡"}
ERR_MSG_NETWORK_NO_NIC_AVAIL = {EN: "network %s no avail nic",
                                ZH_CN: u"网络 %s 没有可用网卡"}
ERR_MSG_NETWORK_IPADDR_ALREADY_IN_USE = {EN: "vxnet %s ipaddr %s in use",
                                ZH_CN: u"网络 %s IP地址 %s 在使用中"}
ERR_MSG_NETWORK_CONFIG_START_END_IP_INVAILD = {EN: "network config start/end ip %s - %s invaild",
                                ZH_CN: u"网络配置起始IP地址 %s - %s 不可用"}
ERR_MSG_DESKTOP_GROUP_NO_THIS_NETWORK = {EN: "desktop group %s  no the network %s ",
                                ZH_CN: u"桌面组 %s 没有该网络配置 %s "}

ERR_MSG_CONNECTION_RESOURCE_INVVAILD = {EN: "connection resource network invaild ",
                                ZH_CN: u"连接资源服务异常"}

ERR_MSG_NETWORK_NO_AVAIL_NIC = {EN: "network %s no available IP ",
                                ZH_CN: u"网络 %s 没有可用的IP地址 "}
ERR_MSG_DESKTOP_GROUP_USER_EXISTED = {EN: "user %s has already existed in desktop group %s",
                                ZH_CN: u"用户 %s 已经存在于桌面组 %s 中"}
ERR_MSG_DESKTOP_GROUP_USER_NO_EXISTED = {EN: "user %s has not existed in desktop group %s ",
                                ZH_CN: u"用户 %s 不存在于桌面组 %s 中"}
ERR_MSG_RANDOM_DESKTOP_COUNT_EXCEED_MAX_LIMIT = {EN: "random desktop count %s exceed limit count",
                                ZH_CN: u"随机桌面数 %s 目超过限制"}
ERR_MSG_DESKTOP_HAS_OWNER_OR_DESKTOP_GROUP = {EN: "desktop %s has owner %s or desktop group %s ",
                                ZH_CN: u"桌面 %s 有所属用户 %s 或者属于桌面组 %s "}
ERR_MSG_DESKTOP_HAS_DESKTOP_GROUP = {EN: "desktop %s has desktop group %s ",
                                ZH_CN: u"桌面 %s 属于桌面组 %s "}
ERR_MSG_RANDOM_DESKTOP_NEED_DESKTOP_COUNT = {EN: "random desktop group need desktop count param",
                                ZH_CN: u"随机桌面组需要 desktop_count 参数"}
ERR_MSG_SYSTEM_NETWORK_NEED_IP_RANGE = {EN: "system network %s need start/end ip range",
                              ZH_CN: u"系统网络 %s 需要指定IP范围"}
ERR_MSG_NETWORK_HAS_RESOURCE_USED_IN_ROUTER = {EN: "duplicate IP network %s in router [%s]",
                              ZH_CN: u"网络 %s 被私有网络路由 %s 正在使用"}
# citrix
ERR_MSG_ILLEGAL_CITIRX_AREA = {EN: "illegal citrix area config %s ",
                              ZH_CN: u"非法的Citrix 区域配置 %s"}
ERR_MSG_CITIRX_AREA_NO_CONFIG = {EN: "citrix area no config ",
                              ZH_CN: u"没有Citrix 区域配置"}
ERR_MSG_CITIRX_DESKTOP_CANT_JOIN_DELIVERY = {EN: "desktop %s cant join delivery group ",
                              ZH_CN: u"桌面 %s 不能加入交付组"}
ERR_MSG_STATIC_DELIVERY_GROUP_NEED_ATTACH_USER = {EN: "statci delivery group %s need attach user ",
                              ZH_CN: u"静态交付组 %s 绑定计算机需要有用户"}
ERR_MSG_USER_ALREADY_ATTACH_DESKTOP = {EN: "user %s already attach desktop ",
                              ZH_CN: u"用户 %s 已经和桌面绑定"}
ERR_MSG_USER_NOT_IN_DELIVERY_GROUP = {EN: "user %s not in delivery group %s",
                              ZH_CN: u"用户 %s 不在交付组 %s 中"}
ERR_MSG_DDC_DETACH_DESKTOP_FROM_DELIVERY_GROUP_FAIL = {EN: "DDC detach desktop %s from delivery group %s fail",
                              ZH_CN: u"DDC从交付组 %s 中解绑计算机 %s 失败"}
ERR_MSG_USER_NOT_IN_DELIVERY_GROUP = {EN: "user %s not in delivery group %s",
                              ZH_CN: u"用户%s 不在交付组%s中"}
ERR_MSG_DESKTOP_GROUP_HAS_DESKTOP_RESOURCE = {EN: "desktop group %s has resource, cant delete",
                              ZH_CN: u"桌面组 %s 有桌面资源，不能删除桌面组"}
ERR_MSG_DESKTOP_GROUP_HAS_DESKTOP_RESOURCE_IN_DDC = {EN: "desktop group %s has resource in ddc, cant delete",
                              ZH_CN: u"桌面组 %s 在DDC里有资源未同步，不能删除桌面组"}
ERR_MSG_DDC_DESKTOP_GROUP_HAS_DESKTOP_RESOURCE = {EN: "DDC desktop group %s has resource, cant delete",
                              ZH_CN: u"DDC桌面组 %s 有桌面资源，不能删除桌面组"}
ERR_MSG_DESKTOP_GROUP_HAS_DISK_RESOURCE = {EN: "desktop group %s has resource, cant delete",
                              ZH_CN: u"桌面组 %s 有数据盘资源，不能删除桌面组"}
ERR_MSG_MODIFY_DELIVERY_GROUP_MODE_FAIL = {EN: "modify delivery group %s mode to %s fail",
                              ZH_CN: u"修改交付组 %s 模式 %s 失败"}
ERR_MSG_COMPUTER_NOT_FOUND = {EN: "computer [%s] not found",
                              ZH_CN: u"桌面[%s]不存在"}
# delivery group

ERR_MSG_DELIVERY_GROUP_TYPE_DISMATCH = {EN: "delivery group type dismatch",
                                               ZH_CN: u"交付组类型不匹配"}
ERR_MSG_DELIVERY_GROUP_NAME_ALREADY_EXISTED = {EN: "delivery group name %s already existed ",
                                               ZH_CN: u"交付组名称 %s 已经存在"}
ERR_MSG_DELIVERY_GROUP_NAME_NO_FOUND = {EN: "delivery group name %s no found ",
                                               ZH_CN: u"交付组名称 %s 未找到"}
ERR_MSG_DESKTOP_HAS_OWNER = {EN: "desktop %s has owner %s",
                             ZH_CN: u"桌面 %s 有关联用户 %s"}
ERR_MSG_DESKTOP_NO_IN_DELIVERY_GROUP = {EN: "desktop %s not in delivery group %s",
                             ZH_CN: u"桌面 %s 不在交付组 %s 中"}
ERR_MSG_DESKTOP_ATTACH_USER_FAIL = {EN: "desktop %s attach user %s fail",
                             ZH_CN: u"桌面 %s 绑定用户 %s 失败"}
ERR_MSG_DESKTOP_NO_OWNER = {EN: "desktop %s no owner",
                             ZH_CN: u"桌面 %s 没有关联用户"}
ERR_MSG_DESKTOP_DELIVERY_GROUP_DISMATCH = {EN: "desktop delivery group %s dismatch",
                             ZH_CN: u"桌面 %s 的交付组不匹配"}
ERR_MSG_DESKTOP_ALREADY_ADD_DELIVERY_GROUP = {EN: "desktop %s already add the delivery group %s",
                             ZH_CN: u"桌面 %s 已加入交付组 %s"}
ERR_MSG_USER_ALREADY_ADD_DELIVERY_GROUP = {EN: "user %s already add the delivery group %s",
                             ZH_CN: u"用户 %s 已加入交付组 %s"}
ERR_MSG_LOAD_COMPUTER_CATALOG_NO_PARAM = {EN: "load computer catalog no param %s",
                              ZH_CN: u"加载计算机目录缺少参数 %s"}
ERR_MSG_LOAD_COMPUTER_CATALOG_NO_FOUND_IMAGE = {EN: "load computer catalog no found image %s",
                              ZH_CN: u"加载计算机目镜像不存在 %s"}
ERR_MSG_ATTACH_DESKTOP_TO_DELIVERY_GROUP_FAIL = {EN: "attach desktop %s to delivery group %s fail",
                              ZH_CN: u"加桌面 %s 到交付组 %s失败"}
ERR_MSG_DESKTOP_HAS_SESSION_CONNECT = {EN: "desktop %s has session connect",
                              ZH_CN: u"桌面 %s 有会话连接"}
ERR_MSG_DELIVERY_GROUP_HAVE_NO_COMPUTER = {EN: "delivery group [%s] have no computer",
                              ZH_CN: u"交付组[%s]中没有计算机"}
# image
ERR_MSG_IMAGE_STATUS_IS_NOT_AVAILABLE = {EN: "image %s status is not avail",
                                         ZH_CN: u"镜像 %s 状态不可用"}
ERR_MSG_IMAGE_STATUS_IS_NOT_EDITED = {EN: "image %s status is not editted",
                                         ZH_CN: u"镜像 %s 状态不是编辑状态"}
ERR_MSG_CANT_DELETE_SYSTEM_IMAGE = {EN: "system image %s , cant delete",
                                         ZH_CN: u"系统镜像 %s ,不可删除"}
ERR_MSG_DESKTOP_IMAGE_NO_INSTANCE = {EN: "desktop image %s no instance",
                                         ZH_CN: u"桌面镜像 %s 没有主机"}
ERR_MSG_DESKTOP_GROUP_OR_DESKTOP_USE_IMAGE = {EN: "desktop group or desktop %s is using the image %s",
                                         ZH_CN: u"有桌面组或桌面 %s 正在使用该镜像 %s"}
ERR_MSG_OTHER_IMAGE_USE_IMAGE = {EN: "other desktop image in user the base image %s",
                                         ZH_CN: u"有其他镜像 %s 正在使用系统基础镜像"}
ERR_MSG_PERSONAL_DESKTOP_GROUP_CANT_UPDATE_IMAGE = {EN: "personal desktop group %s cant update image",
                                         ZH_CN: u"专有桌面 %s 不能更新镜像"}
ERR_MSG_SAVE_DESKTOP_CANT_UPDATE_IMAGE = {EN: "static desktop group choose save system disk %s cant update image",
                                         ZH_CN: u"选择保存系统盘策略的静态桌面 %s 不能更新镜像"}
ERR_MSG_DESKTOP_GROUP_IMAGE_INVAILD = {EN: "desktop group image %s invaild",
                                         ZH_CN: u"桌面组镜像 %s 不可用"}
ERR_MSG_DESKTOP_GROUP_PARAM_NEED_OU= {EN: "desktop group need ou config",
                                         ZH_CN: u"桌面组需要配置ou"}
ERR_MSG_IMAGE_UI_TYPE_DISMATCH = {EN: "image %s ui type dismatch",
                              ZH_CN: u"镜像 %s 连接方式不匹配"}
ERR_MSG_IMAGE_NEED_STOP_DESKTOP_FROM_INTERNEL = {EN: "image %s need to stop from desktop ineternel",
                              ZH_CN: u"镜像 %s 需要从桌面内部关机"}
ERR_MSG_MODIFY_USER_DESKTOP_SESSION = {EN: "modify user desktop session failed",
                              ZH_CN: u"修改用户桌面session信息失败"}
ERR_MSG_LOGOUT_USER_DESKTOP_SESSION = {EN: "logout user desktop session failed",
                              ZH_CN: u"注销用户桌面session信息失败"}
# ---------------------------------------------
#       error code messages
# ---------------------------------------------
ERR_CODE_MSG_INVALID_REQUEST_PARAMS = {EN: "InvailidRequestFormat",
                                       ZH_CN: u"消息格式错误"}
ERR_CODE_MSG_INVALID_REQUEST_FORMAT = {EN: "InvailidRequestFormat",
                                       ZH_CN: u"消息格式错误"}

ERR_CODE_MSG_NEED_UPDATE_DESKTOP_STATUS = {EN: "NeedUpdateDesktopStatus",
                                       ZH_CN: u"更新桌面状态"}

ERR_CODE_MSG_INVALID_REQUEST_METHOD = {EN: "InvailidRequestMethod",
                                       ZH_CN: u"请求方法错误"}
ERR_CODE_MSG_AUTH_FAILURE = {EN: "AuthFailure",
                             ZH_CN: u"身份验证失败"}
ERR_CODE_MSG_REQUEST_HAS_EXPIRED = {EN: "RequestHasExpired",
                                    ZH_CN: u"消息已过期"}
ERR_CODE_MSG_PERMISSION_DENIED = {EN: "PermissionDenied",
                                  ZH_CN: u"访问被拒绝"}
ERR_CODE_MSG_CREATE_USER_FAILED = {EN: "create user failed",
                                     ZH_CN: u"创建用户失败"}
ERR_CODE_MSG_DESCRIBE_USER_FAILED = {EN: "describe user failed",
                                     ZH_CN: u"查询用户失败"}
ERR_CODE_MSG_MODIFY_USER_FAILED = {EN: "modify user failed",
                                     ZH_CN: u"修改用户失败"}
ERR_CODE_MSG_LOGIN_FAILED = {EN: "LoginFailed",
                             ZH_CN: u"登录失败"}
ERR_CODE_MSG_SESSION_EXPIRED = {EN: "SessionExpired",
                                ZH_CN: u"登录会话过期"}
ERR_CODE_MSG_ACCESS_TOKEN_EXPIRED = {EN: "AccessTokenExpired",
                                     ZH_CN: u"用户授权过期"}
ERR_CODE_MSG_USER_NOT_FOUND_OR_PASSWD_NOT_MATCHED = {EN: "user or password not matched",
                                                     ZH_CN: u"用户名或密码不匹配"}
ERR_CODE_MSG_RESOURCE_NOT_FOUND = {EN: "ResourceNotFound",
                                   ZH_CN: u"找不到资源"}
ERR_CODE_MSG_SERVER_BUSY = {EN: "ServerBusy",
                            ZH_CN: u"服务器忙"}
ERR_CODE_MSG_INTERNAL_ERROR = {EN: "InternalError",
                               ZH_CN: u"内部错误"}
ERR_CODE_MSG_SERVER_UPDATING = {EN: "ServerUpdating",
                                ZH_CN: u"服务升级中"}
ERR_CODE_MSG_INSUFFICIENT_RESOURCES = {EN: "InsufficientResources",
                                       ZH_CN: u"资源不足"}
ERR_CODE_MSG_RESOURCES_DEPENDENCE = {EN: "ResourceDependence",
                                       ZH_CN: u"资源存在依赖关系"}
ERR_CODE_MSG_STILL_HAS_DEPENDENCY = {EN: "Still has dependency",
                                     ZH_CN: u"存在依赖关系"}
ERR_CODE_MSG_INVALID_API_MODULES = {EN: "Invalid API modules",
                                    ZH_CN: u"无效的API模块"}
# user
ERR_MSG_USER_ALREADY_EXISTED = {EN: "user id already existed",
                                ZH_CN: u"帐号已存在"}
ERR_MSG_ILLEGAL_USERID = {EN: "illegal user id",
                          ZH_CN: u"帐号格式不合法"}
ERR_MSG_ILLEGAL_EMAIL_ADDR = {EN: "illegal email address format",
                              ZH_CN: u"邮件地址格式不合法"}
ERR_MSG_ILLEGAL_PHONE_NUMBER = {EN: "illegal phone number",
                                ZH_CN: u"电话号码不合法"}
ERR_MSG_ILLEGAL_PROTOCOL = {EN: "illegal protocol %s",
                            ZH_CN: u"非法的协议 %s "}
ERR_MSG_ILLEGAL_ACTION = {EN: "illegal action %s, the valid values are [accept, drop]",
                          ZH_CN: u"非法的动作 %s , 有效值为 [accept, drop]"}
ERR_MSG_ILLEGAL_DIRECTION = {EN: "illegal direction %s",
                             ZH_CN: u"非法的防火墙规则作用方向 %s "}
ERR_MSG_ILLEGAL_PRIORITY = {EN: "illegal priority %s, the valid range is [0 - 100]",
                            ZH_CN: u"非法的优先级 %s, 有效范围是 [0 - 100]"}
ERR_MSG_ADMIN_USER_ONLY = {EN: "only allowed by admin user",
                           ZH_CN: u"只允许管理员帐号访问"}
ERR_MSG_GLOBAL_ADMIN_USER_ONLY = {EN: "only allowed by global admin user",
                           ZH_CN: u"只允许全局管理员帐号访问"}
ERR_MSG_SUPER_USER_ONLY = {EN: "only allowed by super user",
                           ZH_CN: u"只允许超级用户访问"}
ERR_MSG_ADMIN_CONSOLE_ONLY = {EN: "only admin console can do it",
                           ZH_CN: u"只允admin控制台访问"}
ERR_MSG_PRIVILEGE_ACCESS_DENIED = {EN: "your privilege can not access this resource",
                                   ZH_CN: u"你的权限无法访问该资源"}
ERR_MSG_PRIVILEGE_CANT_CREATE_DENIED = {EN: "your privilege can not create this resource",
                                   ZH_CN: u"你的权限无法创建该资源"}
ERR_MSG_DESCRIBE_USER_SCOPE_ACTIONS = {EN: "describe user scope action error",
                           ZH_CN: u"查询权限Action失败"}
ERR_MSG_PERMISSION_DENIED_WITH_REASON = {
    EN: "PermissionDenied, reason: %s",
    ZH_CN: u"访问被拒绝，理由： %s ",
}

ERR_MSG_USER_STATUS_NO_ACTIVE = {EN: "user %s status no active",
                          ZH_CN: u"用户 %s 已被禁用"}

ERR_MSG_USER_NOT_FOUND = {EN: "user %s no found",
                          ZH_CN: u"找不到该用户 %s"}
ERR_MSG_DELETE_USER_ERROR = {EN: "delete user failed",
                          ZH_CN: u"删除用户失败"}
ERR_MSG_INSERT_USER_SCOPE_ERROR = {EN: "insert user scope failed",
                              ZH_CN: u"添加用户资源权限失败"}
ERR_MSG_DESCRIBE_USER_SCOPE_ERROR = {EN: "describe user scope failed",
                              ZH_CN: u"获取用户资源权限失败"}
ERR_MSG_MODIFY_USER_SCOPE_ERROR = {EN: "update user scope failed",
                              ZH_CN: u"修改用户资源权限失败"}
ERR_MSG_CLEAR_USER_SCOPE_ERROR = {EN: "clear user scope failed",
                          ZH_CN: u"清理用户资源权限失败"}
ERR_MSG_CLEAR_RESOURCES_ERROR = {EN: "clear resources failed",
                          ZH_CN: u"清理资源失败"}
ERR_MSG_ENABLE_DESKTOP_USER_ERROR = {EN: "enable user failed",
                          ZH_CN: u"无法设置用户状态为有效状态"}
ERR_MSG_DISABLE_DESKTOP_USER_ERROR = {EN: "disable user failed",
                          ZH_CN: u"无法设置用户状态为无效状态"}
ERR_MSG_MODIY_DESKTOP_USER_ROLE_ERROR = {EN: "modify user role failed",
                          ZH_CN: u"修改用户角色失败"}
ERR_MSG_USER_NAME_NOT_FOUND = {EN: "user_name not found.",
                             ZH_CN: u"user_name不存在"}
ERR_MSG_USER_NAME_LENGTH = {EN: "user name length is [4-20] letters.",
                             ZH_CN: u"用户名长度应该[4-20]字符"}
ERR_MSG_USER_NAME_REGULAR = {EN: "user name is made of letter/number/_",
                             ZH_CN: u"用户名只能由字母数字下划线组成"}
ERR_MSG_CONF_EMAIL_FAILED = {EN: "confirm email failed",
                             ZH_CN: u"邮件确认失败"}
ERR_MSG_PASSWD_NOT_MATCHED = {EN: "password not matched",
                              ZH_CN: u"密码不匹配"}
ERR_MSG_USER_PASSWD_NOT_FOUND = {EN: "password not found",
                              ZH_CN: u"password字段不存在"}
ERR_MSG_NOT_STRONG_PASSWD = {EN: "The password should has a length of at least eight characters, and at least one uppercase letter, one lowercase letter and one number.",
                             ZH_CN: u"密码最小长度为8,并且至少包括一个大写字母,一个小写字母以及一个数字"}
ERR_MSG_NOT_STRONG_INST_PASSWD = {EN: "The instance password should has a length of at least eight characters, and at least one uppercase letter, one lowercase letter and one number.",
                                  ZH_CN: u"主机密码最小长度为8,并且至少包括一个大写字母,一个小写字母以及一个数字"}
ERR_MSG_NOT_STRONG_USER_PASSWD = {EN: "The user password should has a length of at least six characters, and at least one letter and one number.",
                                  ZH_CN: u"用户密码最小长度为6,并且至少包括一个字母以及一个数字"}
ERR_MSG_PASSWD_CANT_CONTAIN_USER_NAME = {EN: "password cant contain user name",
                                  ZH_CN: u"用户密码不能包含用户名"}
ERR_MSG_PASSWD_SHOULD_BE_ASCII = {EN: "password should not ASCII",
                                  ZH_CN: u"密码只能包含ASCII字符"}
ERR_MSG_PASSWD_SHOULD_NOT_CANTAIN_SPECIAL_CHARACTER = {EN: "password should not contain special characters",
                                                       ZH_CN: u"密码不能包含特殊字符"}
ERR_MSG_PASSWD_TOO_SIMPLE = {EN: "This is a common password, please reset for your safety",
                             ZH_CN: u"这是一个常见密码, 为了保证安全, 请重新设置"}
ERR_MSG_PASSWD_CONTAIN_SPECIAL_CHARACTORS = {EN: "Password should not contain special characters, can contain only letters or numbers",
                                             ZH_CN: u"密码中不能包含特殊字符, 只能包含大小写字母或者数字"}
ERR_MSG_CHANGE_PASSWD_FAILED = {EN: "change password failed",
                                ZH_CN: u"修改密码失败"}
ERR_MSG_CHANGE_PASSWD_PERMISSION_FAILED = {EN: "user can not modify other user password",
                                ZH_CN: u"用户不能修改别人密码"}
ERR_MSG_CHANGE_EMAIL_FAILED = {EN: "change email failed",
                               ZH_CN: u"修改邮箱失败"}
ERR_MSG_ACCESS_DENIED_FOR_USER = {EN: "access denied for user",
                                  ZH_CN: u"用户已被禁止访问"}
ERR_MSG_AUTH_USER_EXISTED = {EN: "user %s existed in ad",
                                  ZH_CN: u"用户 %s 已存在"}
ERR_MSG_AUTH_USER_NO_FOUND = {EN: "user %s no found in ad",
                                  ZH_CN: u"用户 %s 不存在"}
ERR_MSG_ACCESS_DENIED_FOR_ZONE = {EN: "access denied for zone %s",
                                  ZH_CN: u"zone %s 的访问被禁止"}
ERR_MSG_ACCESS_DENIED_FOR_CONSOLE = {EN: "access denied for console %s",
                                     ZH_CN: u"console %s 的访问被禁止"}
ERR_MSG_RESET_PASSWD_TOO_OFTEN = {EN: "reset password too often",
                                  ZH_CN: u"重置密码过于频繁"}
ERR_MSG_RESET_PASSWD_FAILED = {EN: "user %s reset password failed",
                               ZH_CN: u"用户 %s重置密码失败"}
ERR_MSG_CANNOT_ACCESS_USER = {EN: "cannot access user %s",
                              ZH_CN: u"不允许访问用户 %s "}
ERR_MSG_SEND_CONFIRM_EMAIL_FAILED = {EN: "send confirm email failed",
                                     ZH_CN: u"发送确认邮件失败"}
ERR_MSG_CHANGE_NOTIFY_EMAIL_TOO_OFTEN = {EN: "change notification email too often",
                                         ZH_CN: u"修改通知邮箱过于频繁"}
ERR_MSG_CHANGE_NOTIFY_EMAIL_FAILED = {EN: "change notify email failed",
                                      ZH_CN: u"修改通知邮箱失败"}
ERR_MSG_USERS_NOT_FOUND = {EN: "users %s not found",
                           ZH_CN: u"找不到用户 %s "}
ERR_MSG_USERNAME_CONTAIN_SPECIAL_CHARACTORS = {EN: "user name should not contain special characters, can contain only letters or numbers, or [_-.]",
                                               ZH_CN: u"用户名中不能包含特殊字符, 只能包含大小写字母或者数字, 或者[-_.]"}
ERR_MSG_USER_GROUP_NOT_EXISTED = {EN: "user group id is not exist",
                                      ZH_CN: u"用户组ID不存在"}
ERR_MSG_CREATE_USER_GROUP_ERROR = {EN: "create user group failed",
                                      ZH_CN: u"创建用户组失败"}
ERR_MSG_MODIGY_USER_GROUP_ERROR = {EN: "modify user group failed",
                                      ZH_CN: u"修改用户组失败"}
ERR_MSG_DELETE_USER_GROUP_ERROR = {EN: "delete user groups failed",
                                      ZH_CN: u"删除用户组失败"}
ERR_MSG_DESCRIBE_USER_GROUP_ERROR = {EN: "describe user groups failed",
                                      ZH_CN: u"查询用户组失败"}
ERR_MSG_CHANGE_USER_IN_GROUP_ERROR = {EN: "change user in group failed",
                                      ZH_CN: u"修改用户所在组失败"}
ERR_MSG_USER_NOT_IN_GROUP_ERROR = {EN: "user not in current group",
                                      ZH_CN: u"用户不在当前组"}
ERR_MSG_USER_GROUP_HAVE_SUB_USER_GROUPS = {EN: "user group have sub user group",
                                      ZH_CN: u"用户组下面有子组织"}
ERR_MSG_USER_GROUP_HAVE_SUB_USERS = {EN: "user group have users",
                                      ZH_CN: u"用户组下面有用户"}
ERR_MSG_MODIFY_SUPER_USER_ROLE = {EN: "can not modify super user role",
                                  ZH_CN: u"禁止修改超级管理员角色"}
ERR_MSG_CHECK_USER_SCOPE_RESOURCE_TYPE = {EN: "resource_type parameter missing",
                                          ZH_CN: u"resource_type参数缺失"}
ERR_MSG_CHECK_USER_SCOPE_OPERATION = {EN: "operation is null",
                                      ZH_CN: u"operation参数缺失"}
ERR_MSG_CHECK_USER_SCOPE_ACTION_TYPE_NOT_INT = {EN: "action_type is not integer",
                                                ZH_CN: u"action_type不是整形"}
ERR_MSG_CHECK_USER_SCOPE_ACTION_TYPE_VALUE= {EN: "action_type value not in [0,1,2,3]",
                                             ZH_CN: u"action_type值不在列表[0,1,2,3]中"}
ERR_MSG_RESOURCE_TYPE_NOT_MATCH = {EN: "resource_type not match, resource_id:%s",
                                          ZH_CN: u"resource_type不匹配, resource_id:%s"}
# third auth
ERR_MSG_CREATE_LOGIN_SERVER_FAILED = {EN: "create login server failed",
                                      ZH_CN: u"创建第三方服务器失败"}
ERR_MSG_ILLEGAL_LOGIN_SERVER_TYPE = {EN: "illegal login server authentication type [%s]",
                                     ZH_CN: u"非法的第三方服务认证类型[%s]"}
ERR_MSG_MODIFY_LOGIN_SERVER_ATTRIBUTES_FAILED = {EN: "modify login server attributes failed",
                                                 ZH_CN: u"修改第三方服务器属性失败"}
ERR_MSG_DELETE_LOGIN_SERVER_FAILED = {EN: "delete login server failed",
                                      ZH_CN: u"删除第三方服务器失败"}
ERR_MSG_LOGIN_SERVER_NOT_FOUND = {EN: "the login server [%s] not found",
                                  ZH_CN: u"第三方服务器[%s]不存在"}
ERR_MSG_LOGIN_SERVER_EXISTED = {EN: "the login server is exsited",
                                ZH_CN: u"第三方服务器已存在"}
ERR_MSG_ACCESS_DENIED_FOR_LOGIN_SERVER = {EN: "access denied for login server [%s]",
                                          ZH_CN: u"第三方服务器已被禁止访问"}

ERR_MSG_LOGIN_ACCOUNT_NOT_FOUND = {EN: "the login account %s not found",
                                   ZH_CN: u"第三方认证账户 %s 不存在"}
ERR_MSG_CREATE_LOGIN_ACCOUNT_FAILED = {EN: "create login account failed",
                                       ZH_CN: u"创建认证账户失败"}
ERR_MSG_LOGIN_ACCOUNT_EXISTED = {EN: "login account is exsited",
                                 ZH_CN: u"第三方认证账户已存在"}
ERR_MSG_DELETE_LOGIN_ACCOUNT_FAILED = {EN: "delete login account failed",
                                       ZH_CN: u"删除第三方认证账户失败"}
ERR_MSG_LOGIN_ACCOUNT_VERIFY_FAILED = {EN: "login account verification failed",
                                       ZH_CN: u"第三方账户认证验证错误"}
ERR_MSG_MODIFY_LOGIN_ACCOUNT_ATTRIBUTES_FAILED = {EN: "modify login  attributes failed",
                                                  ZH_CN: u"修改第三方认证账户属性失败"}
ERR_MSG_ACCESS_DENIED_FOR_LOGIN_ACCOUNT = {EN: "access denied for login account [%s]",
                                           ZH_CN: u"第三方账户已被禁止访问"}
ERR_MSG_LOGIN_ACCOUNT_USER_NOT_FOUND = {EN: "the login account user %s not found",
                                        ZH_CN: u"第三方认证账户 %s 不存在"}
ERR_MSG_CREATE_LOGIN_ACCOUNT_USER_FAILED = {EN: "create login account user failed",
                                            ZH_CN: u"创建认证账户失败"}
ERR_MSG_DELETE_LOGIN_ACCOUNT_USER_FAILED = {EN: "delete login account user failed",
                                            ZH_CN: u"删除第三方认证账户用户关系失败"}
ERR_MSG_LOGIN_ACCOUNT_USER_EXISTED = {EN: "the login account user is already existed",
                                      ZH_CN: u"第三方认证账户用户关系已存在"}
ERR_MSG_MODIFY_LOGIN_ACCOUNT_USER_ATTRIBUTES_FAILED = {EN: "modify login account user attributes failed",
                                                       ZH_CN: u"修改第三方认证账户属性失败"}
ERR_MSG_MODIFY_LOGIN_ACCOUNT_NOT_ACTIVE_USER = {EN: "login account has no active user",
                                                ZH_CN: u"第三方认证账户下无可用用户"}
ERR_MSG_CREATE_AUTH_ORGANIZATION_ERROR = {EN: "create auth organization failed",
                                      ZH_CN: u"创建认证服务组织失败"}
ERR_MSG_DESCRIBE_AUTH_ORGANIZATIONS_ERROR = {EN: "describe auth organizations failed",
                                      ZH_CN: u"查询认证服务组织失败"}
ERR_MSG_MODIFY_AUTH_ORGANIZATION_ERROR = {EN: "modify auth organizations failed",
                                      ZH_CN: u"修改认证服务组织失败"}
ERR_MSG_DELETE_AUTH_ORGANIZATIONS_ERROR = {EN: "delete auth organizations failed",
                                      ZH_CN: u"删除认证服务组织失败"}
ERR_MSG_CREATE_AUTH_ORGANIZATION_ERROR = {EN: "create auth organization failed",
                                      ZH_CN: u"创建认证服务组织失败"}
ERR_MSG_DESCRIBE_AUTH_ORGANIZATIONS_ERROR = {EN: "describe auth organizations failed",
                                      ZH_CN: u"查询认证服务组织失败"}
ERR_MSG_MODIFY_AUTH_ORGANIZATION_ERROR = {EN: "modify auth organizations failed",
                                      ZH_CN: u"修改认证服务组织失败"}
ERR_MSG_DELETE_AUTH_ORGANIZATIONS_ERROR = {EN: "delete auth organizations failed",
                                      ZH_CN: u"删除认证服务组织失败"}
ERR_MSG_CREATE_AUTH_USER_ERROR = {EN: "create auth user failed",
                                      ZH_CN: u"创建认证用户失败"}
ERR_MSG_DESCRIBE_AUTH_USERS_ERROR = {EN: "describe auth users failed",
                                      ZH_CN: u"查询认证用户失败"}
ERR_MSG_MODIFY_AUTH_USER_ERROR = {EN: "modify auth users failed",
                                      ZH_CN: u"修改认证用户失败"}
ERR_MSG_DELETE_AUTH_USERS_ERROR = {EN: "delete auth users failed",
                                      ZH_CN: u"删除认证用户失败"}
ERR_MSG_MODIFY_AUTH_USER_PASSWORD_ERROR = {EN: "modify auth user password failed",
                                      ZH_CN: u"修改认证用户密码失败"}
ERR_MSG_CHANGE_AUTH_USER_IN_ORGANIZATION_ERROR = {EN: "modify auth user in organization failed",
                                      ZH_CN: u"修改认证用户所在组织失败"}
ERR_MSG_CREATE_AD_USER_GROUP_ERROR = {EN: "create ad user group failed",
                                      ZH_CN: u"创建AD用户组失败"}
ERR_MSG_MODIFY_AD_USER_GROUP_ERROR = {EN: "modify ad user group failed",
                                      ZH_CN: u"修改AD用户组失败"}
ERR_MSG_DESCRIBE_AD_USER_GROUP_ERROR = {EN: "describe ad user group failed",
                                      ZH_CN: u"查询AD用户组失败"}
ERR_MSG_DELETE_AD_USER_GROUP_ERROR = {EN: "delete ad user group failed",
                                      ZH_CN: u"删除AD用户组失败"}
ERR_MSG_INSERT_AD_USER_TO_GROUP_ERROR = {EN: "insert ad user to user group failed",
                                      ZH_CN: u"将AD用户插入AD用户组失败"}
ERR_MSG_REMOVE_AD_USER_FROM_GROUP_ERROR = {EN: "remove ad user from user group failed",
                                      ZH_CN: u"从AD用户组移除用户失败"}

ERR_MSG_GET_ZONE_FAILED = {EN: "get zone failed",
                           ZH_CN: u"获取zone失败"}
ERR_MSG_CREATE_SESSION_FAILED = {EN: "create session failed",
                                 ZH_CN: u"创建登录会话失败"}
ERR_MSG_DELETE_SESSION_FAILED = {EN: "delete session failed",
                                 ZH_CN: u"删除登录会话失败"}
ERR_MSG_ILLEGAL_TIMESTAMP = {EN: "illegal timestamp format %s",
                             ZH_CN: u"非法的时间格式 %s "}
ERR_MSG_ILLEGAL_TIMESTRING = {EN: "illegal time string format %s",
                              ZH_CN: u"非法的时间字符串 %s "}
ERR_MSG_ILLEGAL_ACCESS_KEY = {EN: "illegal access key %s",
                              ZH_CN: u"非法的API密钥 %s"}
ERR_MSG_ACCESS_KEY_NOT_ACTIVE = {EN: "access key %s is not active",
                                 ZH_CN: u"不可用的API密钥 %s "}
ERR_MSG_SIGNATURE_NOT_MACTCHED = {EN: "signature not matched",
                                  ZH_CN: u"签名不匹配"}
ERR_MSG_PLZ_LOGIN_AGAIN = {EN: "Please login again",
                           ZH_CN: u"请重新登录"}
ERR_MSG_ILLEGAL_CONSOLE = {EN: "illegal console",
                           ZH_CN: u"非法的Console"}
# user verify
ERR_MSG_CREATE_USER_VERIFY_FAILED = {EN: "create user verify failed",
                                     ZH_CN: u'创建认证失败'}
ERR_MSG_USER_VERIFY_EXISTED = {EN: "user verify existed",
                               ZH_CN: u'认证已存在'}
ERR_MSG_MODIFY_USER_VERIFY_FAILED = {EN: "modify user verify failed",
                                     ZH_CN: u'修改认证信息失败'}

# usb policy
ERR_CODE_MSG_CREATE_USB_POLICY_FAILED = {EN: "create usb policy failed",
                                     ZH_CN: u"创建USB策略失败"}
ERR_CODE_MSG_MODIFY_USB_POLICY_FAILED = {EN: "modify usb policy failed",
                                     ZH_CN: u"修改USB策略失败"}
ERR_CODE_MSG_DELETE_USB_POLICY_FAILED = {EN: "delete usb policy failed",
                                     ZH_CN: u"删除USB策略失败"}

# citrix policy
ERR_CODE_MSG_CREATE_CITRIX_POLICY_FAILED = {EN: "create citrix policy failed",
                                     ZH_CN: u"创建citrix策略失败"}
ERR_CODE_MSG_CREATE_CITRIX_POLICY_ITEM_FAILED = {EN: "config citrix policy item failed",
                                     ZH_CN: u"配置citrix item策略失败"}
ERR_CODE_MSG_DESCRIBE_CITRIX_POLICY_ITEM_CONFIG_FAILED = {EN: "describe citrix policy item config failed",
                                     ZH_CN: u"查询citrix item配置策略失败"}
ERR_CODE_MSG_DESCRIBE_CITRIX_POLICY_FAILED = {EN: "describe citrix policy failed",
                                     ZH_CN: u"查询citrix 策略失败"}
ERR_CODE_MSG_DESCRIBE_CITRIX_POLICY_ITEM_FAILED = {EN: "describe citrix policy item failed",
                                     ZH_CN: u"查询citrix item失败"}
ERR_CODE_MSG_DELETE_CITRIX_POLICY_ITEM_FAILED = {EN: "detelte citrix policy  failed",
                                     ZH_CN: u"删除citrix item失败"}
ERR_CODE_MSG_MODIFY_CITRIX_POLICY_FAILED = {EN: "modify citrix policy failed",
                                     ZH_CN: u"修改citrix策略失败"}
ERR_CODE_MSG_DELETE_CITRIX_POLICY_FAILED = {EN: "delete citrix policy failed",
                                     ZH_CN: u"删除citrix策略失败"}

ERR_MSG_CITRIX_POLICY_NAME_ALREADY_EXISTED = {EN: "citrix policy %s already existed ",
                                               ZH_CN: u"Citrix 策略名称 %s 已经存在"}
ERR_MSG_CITRIX_POLICY_ITEM_NAME_ALREADY_EXISTED = {EN: "citrix policy %s already existed ",
                                               ZH_CN: u"Citrix 子策略名称 %s 已经存在"}
ERR_MSG_CITRIX_POLICY_NAME_NO_FOUND = {EN: "citrix policy not found",
                                     ZH_CN: u"未查找到citrix policy"}
# license
ERR_CODE_MSG_LICENSE_OUT_OF_LIMIT = {EN: "out of license limit",
                                     ZH_CN: u"超出license限制"}
ERR_CODE_MSG_UPDATE_LICENSE_ERROR = {EN: "update license failed",
                                     ZH_CN: u"更新license失败"}

# push server
ERR_MSG_PUSH_SERVER_INTERNAL_ERROR = {EN: "push server internal error, [%s]",
                                     ZH_CN: u'push server 内部错误, [%s]'}
ERR_MSG_PUSH_SERVER_URI_ERROR = {EN: "request uri error",
                                     ZH_CN: u'请求URI错误'}
ERR_MSG_PUSH_SERVER_REQUEST_PARAMS_ERROR = {EN: "request parameters error, [%s]",
                                     ZH_CN: u'请求参数错误, [%s]'}
ERR_MSG_PUSH_SERVER_REQUEST_SESSION_ERROR = {EN: "check user session [%s] failed",
                                     ZH_CN: u'检查user session [%s]失败'}
ERR_MSG_PUSH_SERVER_WEBSOCKET_SUBSCRIBE_ERROR = {EN: "subscribe topic failed",
                                     ZH_CN: u'订阅topic失败'}
ERR_MSG_PUSH_SERVER_WEBSOCKET_UNSUBSCRIBE_ERROR = {EN: "unsubscribe topic 失败",
                                     ZH_CN: u'取消订阅topic失败'}

# vdhost server
ERR_MSG_VDHOST_NOT_CONNECT_ERROR = {EN: "vdhost[%s] not connect",
                                     ZH_CN: u'vdhost[%s] 未连接'}
ERR_MSG_VDHOST_UNKNOWK_REQUEST_ERROR = {EN: "unknown request_id [%s]",
                                     ZH_CN: u'未知的 request_id [%s]'}
ERR_MSG_VDHOST_WAIT_RESPONSE_TIMEOUT_ERROR = {EN: "wait request [%s] timeout",
                                     ZH_CN: u'等待请求 [%s] 超时'}
ERR_MSG_VDHOST_SERVER_SEND_REQUEST_ERROR = {EN: "vdhost server send request [%s] exception",
                                     ZH_CN: u'vdhost服务发送请求 [%s] 异常'}
ERR_MSG_VDHOST_SERVER_CREEATE_JOB_ERROR = {EN: "vdhost server create job fail",
                                     ZH_CN: u'vdhost服务创建Job失败'}
ERR_MSG_VDHOST_SERVER_SEND_TO_PULL_SERVER_ERROR = {EN: "vdhost server send internal request to pull server [%s] error",
                                     ZH_CN: u'vdhost服务发送内部pull请求[%s]失败'}
ERR_MSG_VDHOST_HOSTNAME_NOT_FOUND_ERROR = {EN: "vdhost hostname [%s] not found",
                                     ZH_CN: u'vdhost主机名[%s]未找到'}
ERR_MSG_VDHOST_HOSTNAME_NOT_REGISTER_ERROR = {EN: "vdhost hostname [%s] not register",
                                     ZH_CN: u'vdhost主机名[%s]未注册'}

#storefront msg
ERR_MSG_STOREFRONT_LOGIN_ERROR = {EN: "desktop login in failed",
                                     ZH_CN: u'登录失败，请检查用户名密码或请联系管理员检查是否开启云桌面连接'}
ERR_MSG_STOREFRONT_LOGIN_GATEWAYAUTH_ERROR = {EN: "connection gatewayauth login failed",
                                     ZH_CN: u'登录校验失败'}
ERR_MSG_STOREFRONT_CONFIG_ERROR = {EN: "connection login in ,lack config param",
                                     ZH_CN: u'登录桌面，缺少登录的参数，检查连接数据库配置'}
ERR_MSG_STOREFRONT_GETDESKTOPLIST_ERROR = {EN: "connection get  desktop list failed",
                                     ZH_CN: u'登录桌面，获取桌面列表时错误'}
ERR_MSG_STOREFRONT_GETDESKTOPLIST_UNAUTHORIZE_ERROR = {EN: "userpwd unauthorized",
                                     ZH_CN: u'登录桌面，无用户有效token'}
ERR_MSG_STOREFRONT_GETDESKTOPLIST_NODESKTOP_ERROR = {EN: "user no desktop",
                                     ZH_CN: u'登录桌面，用户无桌面'}

ERR_MSG_STOREFRONT_GETSTATUS_ICA_ERROR = {EN: "get connection ica status failed",
                                     ZH_CN: u'获取桌面状态错误，请检查网络配置，如有疑问，请联系管理员'}
ERR_MSG_STOREFRONT_GETSTATUS_ICA_RETRY_ERROR = {EN: "get connection ica status retry",
                                     ZH_CN: u'无法启动桌面，请尝试关机开机桌面，开机以后等待五分钟进行登录'}
ERR_MSG_STOREFRONT_ASSIGN_NO_DESKTOP_ERROR = {EN: "connection assign desktop error",
                                     ZH_CN: u'没有可用桌面，请联系管理员分配桌面'}
ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_NOMOREACTIVE_SESSION_ERROR = {EN: "connection no more active session on desktop",
                                     ZH_CN: u'没有可用的会话，请等待其他会话退出，或重启桌面，或联系管理员检查桌面状态'}
ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_NOT_FOUND_ERROR = {EN: "connection assign desktop is not found error",
                                     ZH_CN: u'启动的资源已不存在，请联系管理员检查桌面状态'}
ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_LICENSE_ERROR = {EN: "connection assign desktop license error",
                                     ZH_CN: u'没有许可证，请联系管理员检查许可证状态'}
ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_UNCONN_ERROR = {EN: "connection assign desktop not connect error",
                                     ZH_CN: u'无法连接到交付组服务器，,请尝试重启桌面解决该问题，如仍未解决，联系管理员检查服务器状态'}
ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_INMAINT_ERROR = {EN: "connection assign desktop inmaint error",
                                     ZH_CN: u'交付组处于维护模式,请联系管理员检查桌面状态'}
ERR_MSG_STOREFRONT_OTHER_ASSIGN_DESKTOP_ERROR = {EN: "connection other desktop error",
                                     ZH_CN: u'连接桌面产生错误,请联系管理员检查桌面状态'}
ERR_MSG_STOREFRONT_DOWNLOAD_ICA_ERROR = {EN: "connection download ica file failed",
                                     ZH_CN: u'桌面连接异常,请尝试重启桌面解决，如有疑问，请联系管理员'}
ERR_MSG_STOREFRONT_NOTFOUND_ICA_ERROR = {EN: "connection not found ica",
                                     ZH_CN: u'桌面连接异常,请尝试重启桌面解决，如有疑问，请联系管理员'}
ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_ERROR = {EN: "connection assign desktop error",
                                     ZH_CN: u'没有可用桌面，请联系管理员分配桌面'}
ERR_MSG_STOREFRONT_TOKEN_MISSING_ERROR = {EN: "connection token missing, please relogin",
                                     ZH_CN: u'storefront Token丢失，请重新登录'}
ERR_MSG_STOREFRONT_DLV_NAME_MISSING_ERROR = {EN: "connection delivery group name missing, please contact administrator",
                                     ZH_CN: u'桌面[%s]无交付组信息，请联系管理员'}
ERR_MSG_STOREFRONT_CONNECTION_ERROR = {EN: "connection connection is error, please contact administrator",
                                     ZH_CN: u'zone[%s]关联的连接信息通信失败，请联系管理员检查是否开启连接'}
#radius msg
ERR_MSG_RADIUS_CHECK_CONFIG_ERROR = {EN: "radius check failed",
                                     ZH_CN: u'检查radius配置'}
ERR_MSG_RADIUS_DATABASE_ERROR = {EN: "radius check failed",
                                     ZH_CN: u'操作radius出现数据库'}
ERR_MSG_RADIUS_CONNECT_ERROR = {EN: "radius connect failed",
                                     ZH_CN: u'连接radius出错'}
ERR_MSG_NO_FOUND_RADIUS_SERVICE = {EN: "no found radius service %s",
                                     ZH_CN: u'未发现radius %s 服务'}
ERR_MSG_RADIUS_CHECK_REJECT = {EN: "radius check %s reject",
                                     ZH_CN: u'用户%s 无法通过校验'}
ERR_MSG_RADIUS_CHECK_OTHER_ERROR = {EN: "radius check have other error",
                                     ZH_CN: u'多因子校验服务器返回其他错误'}

ERR_MSG_ZONE_HAS_RESOURCE_CANT_DELETE = {EN: "zone %s has resource, cant delete",
                                     ZH_CN: u'区域 %s 有资源不能删除'}
###############################
ERR_MSG_LIST_PARAMETER_LENGTH_TOO_LONG = {
    EN: 'list parameter [%s] length too long, it should less than %d',
    ZH_CN: u'列表参数 [%s] 超长，长度应当小于 %d',
}
ERR_MSG_PARAMETER_SHOULD_BE_DICT = {EN: "parameter [%s] should be dict",
                                    ZH_CN: u"参数[%s]应该为字典"}
ERR_MSG_LIST_PARAMETER_LENGTH_TOO_LONG = {
    EN: 'list parameter [%s] length too long, it should less than %d',
    ZH_CN: u'列表参数 [%s] 超长，长度应当小于 %d',
}
ERR_MSG_PORT_SHOULD_BE_INT = {EN: "port [%s] should be integer",
                              ZH_CN: u"端口[%s]应该为整数"}
ERR_MSG_ILLEGAL_PORT_RANGE = {EN: "illegal port range [%s], valid range [0 - 65535]",
                              ZH_CN: u"非法的端口范围[%s], 正确值为[0 - 65535]"}
ERR_MSG_ILLEGAL_ZONE = {EN: "illegal zone [%s]",
                        ZH_CN: u"非法的zone[%s]"}
ERR_MSG_LANG_NOT_SUPPORTED = {EN: "language [%s] not supported",
                              ZH_CN: u"尚未支持该语言:[%s]"}
ERR_MSG_ILLEGAL_GENDER = {EN: "illegal gender [%s]",
                              ZH_CN: u"非法的性别:[%s]"}
ERR_MSG_ILLEGAL_ROLE = {EN: "illegal user role [%s]",
                        ZH_CN: u"非法的用户角色[%s]"}
ERR_MSG_ILLEGAL_STR_LENGTH = {EN: "illegal string %s length [%s]",
                        ZH_CN: u"字符 %s 长度超过限制[%s]"}
# security
ERR_MSG_POLICY_GROUP_TYPE_UNSUPPORTED = {EN: "unsupport policy group type %s",
                      ZH_CN: u"不支持策略组类型 %s"}
ERR_MSG_POLICY_GROUP_RULESET_EXCEED_MAX_LIMIT = {EN: "ruleset exceed max limit",
                      ZH_CN: u"ruleset超过策略组限制,最大值为5"}
ERR_MSG_POLICY_GROUP_TYPE_DISMATCH_RESOURCE = {EN: "policy group type %s dont match resource %s",
                      ZH_CN: u"策略组类型 %s 和资源 %s 不匹配"}
ERR_MSG_POLICY_GROUP_TYPE_DISMATCH_POLICY = {EN: "policy group type %s dont match policy %s",
                      ZH_CN: u"策略组类型 %s 和策略 %s 不匹配"}

ERR_MSG_POLICY_ALREADY_EXISTED_IN_POLICY_GROUP = {EN: "policy %s already existed in policy group %s",
                                    ZH_CN: u"策略 %s 已经存在策略组 %s 中"}
ERR_MSG_POLICY_NOT_EXISTED_IN_POLICY_GROUP = {EN: "policy %s not existed in policy group %s",
                                    ZH_CN: u"策略 %s 不在策略组 %s 中"}
ERR_MSG_RESOURCE_ALREADY_EXISTED_IN_POLICY_GROUP = {EN: "resource %s already existed in policy group %s",
                                    ZH_CN: u"资源 %s 已经存在策略组 %s 中"}
ERR_MSG_SHARE_SECURITY_POLICY_CANT_APPLY = {EN: "share security policy %s cant apply",
                                    ZH_CN: u"该策略 %s 不能应用修改"}
ERR_MSG_RESOURCE_NOT_EXISTED_IN_POLICY_GROUP = {EN: "resource %s not existed in policy group %s",
                                    ZH_CN: u"资源 %s 不在策略组 %s 中"}
ERR_MSG_SECURITY_RULES_NOT_IN_UNIQUE_SECURITY_GROUP = {EN: "security rules %s not in unique policy group",
                                    ZH_CN: u"安全规则 %s 不在同一个安全组中"}
ERR_MSG_SECURITY_RULES_REMOVE = {EN: "security rules %s remove error",
                                    ZH_CN: u"安全规则 %s 删除失败"}
ERR_MSG_NO_FOUND_DEFAULT_SECURITY_GROUP = {EN: "no found default security group",
                                    ZH_CN: u"没有发现缺省安全组"}
ERR_MSG_UNSUPPORTED_POLICY_GROUP_TYPE = {EN: "unsupported policy group type %s, only supported %s",
                                    ZH_CN: u"不支持策略组类型%s,只支持 %s"}
ERR_MSG_SECURITY_POLICY_NO_BASE_POLICY = {EN: "policy group no base security policy %s",
                                    ZH_CN: u"安全策略组没有基本策略 %s"}
ERR_MSG_POLICY_GROUP_HAS_RESOURCE_CANT_DELETE = {EN: "policy group %s has resource in using",
                                    ZH_CN: u"安全策略组%s有资源正在使用"}
ERR_MSG_SHARE_POLICY_ADMIN_CANT_DELETE = {EN: "policy group %s has resource in using",
                                    ZH_CN: u"安全策略组%s有共享策略不能删除"}
ERR_MSG_DEFAULT_POLICY_GROUP_CANT_DELETE = {EN: "default policy group %s cant delete",
                                    ZH_CN: u"缺省策略组%s不能删除"}
ERR_MSG_SECURITY_POLICY_CANT_APPLY_RESOURCE = {EN: "policy group %s cant apply resource %s",
                                    ZH_CN: u"安全策略组%s 不能应用资源 %s"}
ERR_MSG_ZONE_ALREADY_EXISTED = {EN: "zone %s has already existed",
                                    ZH_CN: u"区域 %s 已经存在"}
ERR_MSG_ZONE_NAME_ALREADY_EXISTED = {EN: "zone_name %s has already existed",
                                    ZH_CN: u"区域名称 %s 已经存在"}

ERR_MSG_ZONE_HAS_NETWORK_CANT_SET_TYPE = {EN: "zone %s has network, cant set network tpye",
                                    ZH_CN: u"区域 %s 有网络在使用，无法更改类型"}
ERR_MSG_SECURITY_POLICY_IN_USED = {EN: "security policy %s in using, cant delete",
                                    ZH_CN: u"安全策略 %s 正在使用，无法删除"}
ERR_MSG_SLAVE_SECURITY_POLICY_CANT_DELETE = {EN: "slave security policy %s cant delete",
                                    ZH_CN: u"共享区域策略 %s 直接无法删除"}
ERR_MSG_SECURITY_POLICY_NEED_APPLY = {EN: "security policy %s need apply",
                                    ZH_CN: u"安全策略 %s 需要应用修改，再做操作"}
ERR_MSG_SECURITY_IPSET_IN_USED = {EN: "security ipset %s in using, cant delete",
                                    ZH_CN: u"IP端口集合 %s 正在使用，无法删除"}
ERR_MSG_INSTANCE_CLASS_INVAILD = {EN: "instance class %s invaild",
                                  ZH_CN: u"桌面主机类型 %s 不匹配"}
ERR_MSG_DISK_SIZE_INVAILD = {EN: "disk size %s invaild",
                                  ZH_CN: u"数据盘大小 %s 不匹配"}
ERR_MSG_CPU_CORE_INVAILD = {EN: "CPU core %s invaild",
                                  ZH_CN: u"CPU 核心数 %s 不匹配"}
ERR_MSG_MEMORY_SIZE_INVAILD = {EN: "memory size %s invaild",
                                  ZH_CN: u"内存大小 %s 不匹配"}
ERR_MSG_CPU_MEMORY_INVAILD = {EN: "CPU/memory pair %s invaild",
                                  ZH_CN: u"CPU/内存 配置%s 不匹配"}
ERR_MSG_ZONE_PLACE_GROUP_DISMATCH = {EN: "zone %s place group %s dismatch",
                                  ZH_CN: u"Zone %s 配置安置组 %s 不匹配"}
ERR_MSG_ZONE_NETWORK_TYPE_INVAILD = {EN: "network type %s invaild",
                                  ZH_CN: u"网络配置 %s 不匹配"}
ERR_MSG_ZONE_CITRIX_CONNECTION_HOST_ALREADY_EXISTED = {EN: "zone_citrix_connection host %s already existed",
                                    ZH_CN: u"Citrix服务配置 Citrix IP地址 %s 已经存在其他活跃的Citrix服务配置"}
ERR_MSG_ZONE_CITRIX_CONNECTION_SF_ALREADY_EXISTED = {EN: "zone_citrix_connection storefront_uri %s already existed",
                                    ZH_CN: u"Citrix服务配置 StoreFront 的链接地址 %s 已经存在其他区域配置"}
# ad
ERR_MSG_CREATE_AUTH_SERVICE_CONN_FAIL = {EN: "create auth service conn faiil [%s] ",
                                     ZH_CN: u'创建认证服务连接 [%s] 失败'}
###############################
ERR_MSG_USER_EXISTED_IN_DESKTOP = {EN: "user %s existed in desktop system",
                                  ZH_CN: u"用户 %s 已存在桌面系统中"}

ERR_MSG_ZONE_HAS_RESOURCE_CANT_DELETE = {EN: "zone %s has resource. cant delte",
                                  ZH_CN: u"区域%s 有资源无法删除"}

ERR_MSG_USER_EXISTED_IN_AD = {EN: "user %s existed in auth service",
                                  ZH_CN: u"%s 已存在认证服务中"}
ERR_MSG_THE_SAME_OU_CANT_EXISTED_THE_SAME_REAL_NAME = {EN: "the same ou cant existed the same displayname",
                                  ZH_CN: u" 相同目录下已存在姓名 %s"}
ERR_MSG_USER_GROUP_EXISTED_IN_AD = {EN: "user %s has the same user group",
                                  ZH_CN: u"%s 和用户组重名"}
ERR_MSG_NEED_OU_DN = {EN: "need ou dn",
                                  ZH_CN: u"需要指定ou dn"}
ERR_MSG_GLOBAL_USER_EXISTED_IN_AD = {EN: "global user %s existed",
                                  ZH_CN: u"已存在超级管理员 %s"}
ERR_MSG_USER_NOT_EXISTED_IN_AD = {EN: "user %s no existed in ad",
                                  ZH_CN: u"用户 %s AD域中不存在"}
ERR_MSG_AUTH_SERVICE_NO_FOUND = {EN: "auth service %s no found",
                                  ZH_CN: u"认证服务 %s 没有找到"}
ERR_MSG_CANT_MODIFY_AUTH_SERVICE_DOMAIN = {EN: "cant modify auth service domain",
                                  ZH_CN: u"不能修改认证服务domain"}
ERR_MSG_AUTH_SERVICE_NO_FOUND_RESOURCE = {EN: "auth service no found resoruce %s",
                                  ZH_CN: u"认证服务 没有找到 %s"}
ERR_MSG_AUTH_SERVICE_BASE_DN_EXISTED = {EN: "auth service base dn %s existed",
                                  ZH_CN: u"认证服务根组织单元配置%s冲突 "}
ERR_MSG_AUTH_SERVICE_STATUS_INVAILD = {EN: "auth service %s status invaild",
                                  ZH_CN: u"认证服务 %s 状态不可用"}
ERR_MSG_AUTH_SERVICE_PARAM_ERROR = {EN: "auth service param config error",
                                  ZH_CN: u"认证服务 参数配置错误"}
ERR_MSG_AUTH_SERVICE_BASE_DN_NO_FOUND = {EN: "auth service base dn %s no found",
                                  ZH_CN: u"认证服务组织单元%s没有找到"}
ERR_MSG_AUTH_SERVICE_CONN_ERROR = {EN: "auth service config conn error",
                                  ZH_CN: u"认证服务 连接错误"}
ERR_MSG_AUTH_SERVICE_NO_FOUND_USER = {EN: "auth service %s no found user %s",
                                  ZH_CN: u"认证服务 %s 没有找到用户 %s"}
ERR_MSG_NEW_NAME_EXISTED = {EN: "new name %s existed",
                                  ZH_CN: u"新名称 %s 已经存在"}
# zone
ERR_MSG_ZONE_PLATFORM_INVAILD = {EN: "zone platform %s invaild",
                                  ZH_CN: u"zone的平台类型%s不可用"}
ERR_MSG_ZONE_HAS_AUTH_SERVICE = {EN: "zone %s already has auth service",
                                  ZH_CN: u"区域 %s 已配置认证服务器"}
ERR_MSG_ZONE_STATUS_INVAILD = {EN: "zone status %s invaild",
                                  ZH_CN: u"zone状态%s不可用"}
ERR_MSG_ZONE_NETWORK_NEED_ROUTER = {EN: "zone %s network need router",
                                  ZH_CN: u"zone %s 网络需要路由器"}
# user
ERR_MSG_USER_DOMAIN_NAME_INVAILD = {EN: "user domain name %s invaild",
                                  ZH_CN: u"用户名 %s 不可用"}
ERR_MSG_USER_DOMAIN_NO_FOUND = {EN: "user domain %s no found",
                                  ZH_CN: u"认证域 %s 未找到"}
ERR_MSG_DOMAIN_INFO_DISMATCH = {EN: "user zone %s dismatch",
                                  ZH_CN: u" 域 %s 和用户不匹配"}
ERR_MSG_ZONE_PARAM_MISS = {EN: "zone param miss",
                                  ZH_CN: u" 缺少区域参数"}
ERR_MSG_REQUEST_NEED_ZONE_ID= {EN: "request need zone id",
                                  ZH_CN: u" 请求需要zoneID"}               
ERR_MSG_USER_NO_FOUND= {EN: "user %s no found",
                                  ZH_CN: u"用户%s不存在"}
ERR_MSG_USER_ERROR_TIME_EXCEED_LIMIT= {EN: "user error time exceed limit",
                                  ZH_CN: u"错误次数超过限制"}
ERR_MSG_USER_NAME_CONFLICT= {EN: "user name %s conflict, please getting help to adminnistrator",
                                  ZH_CN: u"用户名%s冲突，请使用 用户名@域服务器认证域"}
ERR_MSG_USER_CANT_ACCESS_ZONE= {EN: "user %s cant access zone %s",
                                  ZH_CN: u"用户%s没有权限访问区域 %s"}
ERR_MSG_NO_AVAIL_ZONE= {EN: "user %s no avail zone",
                                  ZH_CN: u"用户%s没有可见区域"}
ERR_MSG_ZONE_NO_CONFIG_AUTH_SERVICE= {EN: "zone %s no config auth service",
                                  ZH_CN: u"区域%s 未配置认证服务"}
ERR_MSG_ZONE_AUTH_SERVICE_IN_USED= {EN: "auth service in used %s",
                                  ZH_CN: u"认证服务作为根路径正在使用%s"}
ERR_MSG_AUTH_SERVICE_IS_BUSY= {EN: "auth service %s is busy",
                                  ZH_CN: u"认证服务%s 正忙，请稍后"}
ERR_MSG_REFRESH_AUTH_OUS_DN_FAIL= {EN: "auth service base dn %s error",
                                  ZH_CN: u"用户组织刷新DN %s 异常"}
ERR_MSG_AUTH_BASE_DN_ILLEGEL= {EN: "auth service base dn %s illegel",
                                  ZH_CN: u"用户认证DN %s 非法"}
ERR_MSG_AUTH_SERVICE_ABNORMAL= {EN: "auth service status abnormal",
                                  ZH_CN: u"认证服务器异常"}
ERR_MSG_AUTH_SERVICE_READONLY= {EN: "auth service %s status read-ony",
                                  ZH_CN: u"认证服务器 %s 只读"}
ERR_MSG_AUTH_SERVICE_CANT_MODIFY_PASSWORD= {EN: "auth service %s cant modify password",
                                  ZH_CN: u"认证服务器 %s 不允许修改密码"}
ERR_MSG_OU_HAS_RESOURCE_CANT_DELETE= {EN: "ou %s has resource, cant delete",
                                  ZH_CN: u"组织单元 %s 被使用或者有用户信息，不能删除"}
ERR_MSG_CITIRX_MANAGED_RESOURCE_NO_CONFIG = {EN: "managed resource no config ",
                              ZH_CN: u"没有配置托管资源"}
ERR_MSG_UNSUPPORTED_MANAGED_RESOURCE = {EN: "unsupported managed resource %s",
                                  ZH_CN: u"不支持托管资源 %s"}
ERR_MSG_ZONE_NO_FOUND_STOREFRONT_CONFIG = {EN: "zone %s no found storefront config",
                                  ZH_CN: u"区域 %s 没有发现StoreFront配置"}
ERR_MSG_AUTH_SERVICE_GET_OUS_FAIL = {EN: "auth service %s get ous %s fail",
                                  ZH_CN: u"认证服务 %s 查询组织单元 %s 失败"}
ERR_MSG_AUTH_SERVICE_HAS_ZONE_IN_USED = {EN: "auth service %s has zone in used",
                                  ZH_CN: u"认证服务 %s 正在被区域使用"}
ERR_MSG_NOTICE_PUSH_SCOPE_DISMATCH = {EN: "notice push scope %s diamtch",
                                  ZH_CN: u"通告推送 %s 可见范围不匹配"}
ERR_MSG_NOTICE_PUSH_TYPE_DISMATCH_USER_ROLE = {EN: "cant create notice, type %s",
                                  ZH_CN: u"用户角色禁止创建该类型 %s 的公告"}
ERR_MSG_NOTICE_TYPE_IS_PUBLIC = {EN: "notice %s type is public",
                                  ZH_CN: u"公告 %s 类型是所有人可见，不能设置可见范围"}

ERR_MSG_NOTICE_STATUS_EXPIRED = {EN: "notice %s status is expried",
                                  ZH_CN: u"公告 %s 已经失效"}
ERR_MSG_NOTICE_OWNER_DISMATCH = {EN: "notice %s owner dismatch",
                                  ZH_CN: u"没有权限更改公告 %s属性"}

ERR_MSG_NOTICE_NO_FOUND_ZONE_USER_CONFIG = {EN: "notice %s no found zone user config",
                                  ZH_CN: u"公告 %s没有区域和用户配置"}
ERR_MSG_AUTH_SERVICE_RADIUS_DISABLE = {EN: "auth service %s need enable radius",
                                  ZH_CN: u"认证服务%s需要启用二次认证"}
ERR_MSG_NO_FOUND_ZONE_USER= {EN: "no found zone %s user %s",
                                  ZH_CN: u"区域 %s 没有找到用户 %s"}
ERR_MSG_RADIUS_USER_EXISTED= {EN: "radius existed user %s",
                                  ZH_CN: u"用户 %s 已存在"}

ERR_MSG_RADIUS_NEED_CONFIG_AUTH_SERVICE= {EN: "radius %s need config auth service",
                                          ZH_CN: u"Radius %s 需要配置认证服务"}

ERR_MSG_PASSWORD_PROMPT_QUESTRION_EXIST_ERROR = {EN: "password prompt question have exist",
                                                  ZH_CN: u"密码提示问题已经存在"}
ERR_MSG_CREATE_PASSWORD_PROMPT_QUESTRION_ERROR = {EN: "create password prompt question error",
                                                  ZH_CN: u"创建密码提示问题失败"}
ERR_MSG_MODIFY_PASSWORD_PROMPT_QUESTRION_ERROR = {EN: "modify password prompt question error",
                                                  ZH_CN: u"修改密码提示问题失败"}
ERR_MSG_DELETE_PASSWORD_PROMPT_QUESTRION_ERROR = {EN: "delete password prompt question error",
                                                  ZH_CN: u"删除密码提示问题失败"}
ERR_MSG_DESCRIBE_PASSWORD_PROMPT_QUESTRION_ERROR = {EN: "describe password prompt question error",
                                                  ZH_CN: u"查询密码提示问题失败"}
ERR_MSG_PASSWORD_PROMPT_QUESTRION_HAVE_USER_ANSWER_ERROR = {EN: "password prompt question have user answer error",
                                                  ZH_CN: u"密码提示问题已经有用户答案"}
ERR_MSG_CREATE_PASSWORD_PROMPT_ANSWER_ERROR = {EN: "create password prompt answer error",
                                                  ZH_CN: u"创建密码提示问题的答案失败"}
ERR_MSG_MODIFY_PASSWORD_PROMPT_ANSWER_ERROR = {EN: "modify password prompt answer error",
                                                  ZH_CN: u"修改密码提示问题的答案失败"}
ERR_MSG_DELETE_PASSWORD_PROMPT_ANSWER_ERROR = {EN: "delete password prompt answer error",
                                                  ZH_CN: u"删除密码提示问题的答案失败"}
ERR_MSG_CHECK_PASSWORD_PROMPT_ANSWER_ERROR = {EN: "check password prompt answer error",
                                                  ZH_CN: u"比对密码提示问题的答案失败"}
ERR_MSG_RESET_PASSWORD_FLAG_ERROR = {EN: "set zone user reset password flag error",
                                                  ZH_CN: u"设置重置密码标志位失败"}
ERR_MSG_SET_SECURITY_QUESTION_FLAG_ERROR = {EN: "set desktop user security_question flag error",
                                                  ZH_CN: u"设置用户安全问题标志位失败"}
ERR_MSG_ADMIN_CAN_NOT_USE_PASSWORD_PROMPT_ERROR = {EN: "admin can not use password prompt",
                                                  ZH_CN: u"admin用户不能使用密码提示问题找回密码"}
ERR_MSG_AUTH_SERVICE_HOST_CANT_THE_SAME = {EN: "auth service cant has the same host %s",
                                                  ZH_CN: u"认证服务器地址 %s 已存在"}
ERR_MSG_ZONE_NO_FOUND_AUTH_SERVICE = {EN: "zone %s no found auth service",
                                  ZH_CN: u"区域 %s没有配置认证服务"}
ERR_MSG_RADIUS_HAS_AUTH_SERVICE_IN_USED = {EN: "radius %s has auth service in-used",
                                  ZH_CN: u"radius %s 正在被认证服务使用"}

ERR_MSG_STOPRE_FRONT_CREATE_BORKER_FAIL = {EN: " %s storefront create broker fail",
                                 ZH_CN: u"%s创建ICA连接检查失败"}
ERR_MSG_NEED_RADIUS_CHECK = {EN: "user %s need radius check",
                             ZH_CN: u"用户 %s 需要radius验证"}
ERR_MSG_AUTH_SERVICE_HAS_RADIUS = {EN: "auth service %s has radius service",
                                  ZH_CN: u"认证服务 %s 已关联radius认证"}
ERR_MSG_AUTH_SERVICE_NO_RADIUS = {EN: "auth service %s has not radius service",
                                  ZH_CN: u"认证服务 %s 未关联radius认证"}

ERR_MSG_ZONE_CONFIG_ERROR = {EN: "zone %s config error",
                                  ZH_CN: u"区域  %s 配置错误"}
ERR_MSG_ZONE_CONFIG_ACCOUNT_USER_ID_ERROR = {EN: "account_user_id %s config error",
                                  ZH_CN: u"云平台账户 ID %s 配置错误"}
ERR_MSG_ZONE_CONFIG_ACCOUNT_USER_ID_IS_NOT_ADMIN_USER = {EN: "account_user_id %s is not admin user",
                                  ZH_CN: u"云平台账户 ID %s 不是管理员用户"}

# terminal
ERR_MSG_TERMINAL_STATUS_DISMATCH = {EN: "terminal %s status %s dismatch",
                              ZH_CN: u"終端 %s 需要状态 %s 才可以操作"}
ERR_MSG_CREATE_TERMINAL_GROUP_FAILED = {EN: "create terminal group failed",
                                    ZH_CN: u"创建终端组失败"}
ERR_MSG_TERMINAL_GROUP_NAME_ALREADY_EXISTED = {EN: "terminal group name %s already existed",
                             ZH_CN: u"终端组名称 %s 已经存在"}
ERR_MSG_TERMINAL_GROUP_NO_FOUND = {EN: "terminal group no found %s",
                                    ZH_CN: u"没有发现终端组 %s"}
ERR_MSG_MODIFY_TERMINAL_GROUP_FAILED = {EN: "modify terminal group failed %s",
                                    ZH_CN: u"修改终端组失败 %s"}
ERR_MSG_DELETE_TERMINAL_GROUP_RESOURCE_FAILED = {EN: "delete terminal group resource failed %s",
                                    ZH_CN: u"删除终端组终端失败 %s"}
ERR_MSG_DELETE_TERMINAL_GROUP_FAILED = {EN: "delete terminal group failed %s",
                                    ZH_CN: u"删除终端组失败 %s"}
ERR_MSG_TERMINAL_NO_FOUND = {EN: "terminal no found %s",
                                    ZH_CN: u"没有发现终端 %s"}
ERR_MSG_TERMINAL_ALREAY_EXISTED_TERMINAL_GROUP = {EN: "terminal %s has already existed in terminal group %s",
                                    ZH_CN: u"终端 %s 已经存在于终端组 %s 中"}
ERR_MSG_ADD_TERMINAL_GROUP_TERMINAL_FAILED = {EN: "add terminal group terminal failed",
                                    ZH_CN: u"添加终端组终端失败"}
ERR_MSG_TERMINAL_NOT_IN_TERMINAL_GROUP = {EN: "terminal %s not in terminal group %s",
                                    ZH_CN: u"终端 %s 不存在于终端组 %s 中"}
ERR_MSG_DELETE_TERMINAL_GROUP_TERMINAL_FAILED = {EN: "delete terminal group terminal %s failed",
                                    ZH_CN: u"删除终端组终端 %s 失败"}
ERR_MSG_MODIFY_TERMINAL_FAILED = {EN: "modify terminal failed %s",
                                    ZH_CN: u"修改终端失败 %s"}

# terminal server
ERR_MSG_TERMINAL_NOT_CONNECT_ERROR = {EN: "terminal [%s] not connect",
                                     ZH_CN: u'terminal[%s] 未连接'}
ERR_MSG_TERMINAL_SERVER_SEND_REQUEST_ERROR = {EN: "terminal server send request [%s] exception",
                                     ZH_CN: u'terminal服务发送请求 [%s] 异常'}
ERR_MSG_TERMINAL_UNKNOWK_REQUEST_ERROR = {EN: "unknown request_id [%s]",
                                     ZH_CN: u'未知的 request_id [%s]'}
ERR_MSG_TERMINAL_WAIT_RESPONSE_TIMEOUT_ERROR = {EN: "wait request [%s] timeout",
                                     ZH_CN: u'等待请求 [%s] 超时'}
ERR_MSG_TERMINAL_REGISTER_FAILED = {EN: "terminal [%s] register failed",
                                     ZH_CN: u'终端 [%s] 注册失败'}

# module custom
ERR_MSG_CREATE_MODULE_CUSTOM_FAILED = {EN: "create module custom failed",
                                    ZH_CN: u"创建功能定制失败"}
ERR_MSG_CREATE_MODULE_CUSTOM_CONFIG_FAILED = {EN: "create module custom config failed",
                                    ZH_CN: u"创建功能定制配置失败"}
ERR_MSG_MODIFY_MODULE_CUSTOM_CONFIG_FAILED = {EN: "modify module custom config failed %s",
                                    ZH_CN: u"修改功能定制失败 %s"}
ERR_MSG_MODULE_CUSTOM_CONFIG_COUNT= {
    EN: "modify module custom config %s missing number parameter",
    ZH_CN: u"更改功能定制 %s缺少个数参数",
}
ERR_MSG_CREATE_MODULE_CUSTOM_USER_FAILED = {EN: "create module custom user failed",
                                    ZH_CN: u"创建功能定制用户失败"}
ERR_MSG_MODIFY_MODULE_CUSTOM_USER_FAILED = {EN: "modify module custom user failed %s",
                                    ZH_CN: u"修改功能定制用户失败 %s"}
ERR_MSG_CUSTOM_NAME_ALREADY_EXISTED = {EN: "custom name %s already existed",
                             ZH_CN: u"功能定制名称 %s 已经存在"}
ERR_MSG_MODIFY_MODULE_CUSTOM_FAILED = {EN: "modify module custom failed %s",
                                    ZH_CN: u"修改功能定制失败 %s"}
ERR_MSG_MODULE_CUSTOM_NO_FOUND = {EN: "module custom no found %s",
                                    ZH_CN: u"没有发现功能定制 %s"}
ERR_MSG_DELETE_MODULE_CUSTOM_FAILED = {EN: "delete module custom failed %s",
                                    ZH_CN: u"删除功能定制失败 %s"}
ERR_MSG_DELETE_MODULE_CUSTOM_USER_FAILED = {EN: "delete module custom user failed %s",
                                    ZH_CN: u"删除功能定制用户失败 %s"}
ERR_MSG_DELETE_MODULE_CUSTOM_CONFIG_FAILED = {EN: "delete module custom config failed %s",
                                    ZH_CN: u"删除功能定制配置失败 %s"}
ERR_MSG_DELETE_MODULE_CUSTOM_ZONE_FAILED = {EN: "delete module custom zone failed %s",
                                    ZH_CN: u"删除功能定制失败 %s"}

# system custom
ERR_MSG_MODIFY_SYSTEM_CUSTOM_CONFIG_FAILED = {EN: "modify system custom config failed %s",
                                    ZH_CN: u"修改系统定制失败 %s"}
ERR_MSG_SYSTEM_CUSTOM_CONFIG_COUNT= {
    EN: "modify system custom config %s missing number parameter",
    ZH_CN: u"更改系统定制 %s缺少个数参数",
}
ERR_MSG_CREATE_SYSTEM_CUSTOM_FAILED = {EN: "create system custom failed",
                                    ZH_CN: u"创建系统定制失败"}
ERR_MSG_CREATE_SYSTEM_CUSTOM_CONFIG_FAILED = {EN: "create system custom config failed",
                                    ZH_CN: u"创建系统定制配置失败"}
ERR_MSG_MODIFY_SYSTEM_CUSTOM_FAILED = {EN: "modify system custom failed %s",
                                    ZH_CN: u"修改系统定制失败 %s"}

# desktop service management
ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND = {EN: "desktop service management no found %s",
                                    ZH_CN: u"没有发现服务管理 %s"}
ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED = {EN: "modify desktop service management failed %s",
                                    ZH_CN: u"修改服务管理失败 %s"}
ERR_MSG_DESKTOP_SERVICE_INSTANCE_ALREADY_EXISTED = {EN: "desktop service instance %s already existed",
                                    ZH_CN: u"服务主机 %s 已存在"}
ERR_MSG_DESKTOP_SERVICE_INSTANCE_NO_FOUND = {EN: "desktop service instance %s no found",
                                    ZH_CN: u"服务主机 %s 不存在"}
ERR_MSG_DELETE_DESKTOP_SERVICE_INSTANCE_FAILED = {EN: "delete desktop service instances failed %s",
                                    ZH_CN: u"删除服务主机失败 %s"}
ERR_MSG_DESKTOP_SERVICE_INSTANCE_SERVICE_TYPE_ERRORED = {EN: "service type %s error",
                                    ZH_CN: u"服务组件类型错误 %s"}
ERR_MSG_DESKTOP_SERVICE_INSTANCE_IS_NOT_SERVICE_TYPE = {EN: "instance_id %s is not %s",
                                    ZH_CN: u"服务主机 %s 不是 %s 类型"}
ERR_MSG_CREATE_DESKTOP_SERVICE_MANAGEMENT_FAILED = {EN: "create desktop service management failed",
                                    ZH_CN: u"创建服务组件失败"}
ERR_MSG_ONLY_CITRIX_ZONE_SUPPORT_LOAD_CITRIX_SERVICE_TYPE = {EN: "only citrix zone support load citrix service_type %s",
                                  ZH_CN: u"只有citrix区域支持添加citrix服务组件 %s"}
# workflow
ERR_MSG_NO_FOUND_SERVICE_TYPE_API_ACTION = {EN: "no found service type %s api action %s",
                                  ZH_CN: u"%s没有找到对应的API action %s"}
ERR_MSG_WORKFLOW_SERVICE_TYPE_NOT_FOUND = {EN: "workflow service type %s no found",
                                  ZH_CN: u"没有找到工作流服务 %s"}
ERR_MSG_WORKFLOW_STATUS_DISMATCH = {EN: "workflow %s status %s dismatch",
                                  ZH_CN: u"工作流  %s状态 与 %s 不匹配"}
ERR_MSG_WORKFLOW_MODEL_REQUIRED_PARAM_DISMATCH = {EN: "workflow model param %s dismatch",
                                  ZH_CN: u"工作流 模板参数不匹配"}
ERR_MSG_WORKFLOW_REQUEST_ACTION_CANT_MATCH = {EN: "workflow request action %s cant match",
                                  ZH_CN: u"工作流 请求类型 %s不匹配"}

ERR_MSG_NO_FOUND_WORKFLOW_MODEL_HEAD_ACTION = {EN: "no found workflow model %s head action",
                                  ZH_CN: u"workflow模板 %s 没有head action"}
ERR_MSG_API_ACTION_PARAM_DISMATCH = {EN: "api action %s lose param %s",
                                  ZH_CN: u"Action %s缺少参数 %s"}


# workflow
ERR_MSG_COMPONENT_NO_FOUND = {EN: "no found component %s upgrade bin",
                                  ZH_CN: u"没有找到组件 %s 升级包"}

# file share
ERR_MSG_CANNOT_MOVE_CURRENT_GROUP_OF_THE_FILE = {EN: "Cannot move [%s] to the current group of the file",
                                  ZH_CN: u"不能移动文件 [%s] 到文件当前的文件夹."}
ERR_MSG_FILE_SHARE_GROUP_NAME_ALREADY_EXISTED = {EN: "file share group name %s already existed",
                             ZH_CN: u"共享文件夹 %s 已经存在"}
ERR_MSG_FILE_SHARE_GROUP_NO_FOUND = {EN: "file share group %s no found",
                                  ZH_CN: u"共享文件夹 %s 没有找到"}
ERR_MSG_REFRESH_FILE_SHARE_GROUP_DN_FAIL= {EN: "refresh file share group base dn %s error",
                                  ZH_CN: u"共享文件夹刷新 %s 异常"}
ERR_MSG_FILE_SHARE_GROUP_HAS_RESOURCE_CANT_DELETE= {EN: "file share group %s has resource, cant delete",
                                  ZH_CN: u"共享文件夹 %s 有文件资源，不能删除"}
ERR_MSG_FILE_SHARE_GROUP_FILE_NO_FOUND = {EN: "file share group file %s no found",
                                  ZH_CN: u"共享文件夹文件 %s 没有找到"}
ERR_MSG_NO_FOUND_FILE_IN_THE_RECYCLE = {EN: "no found file %s in the recycle",
                                  ZH_CN: u"回收站里没有找到删除的文件 %s"}
ERR_MSG_NO_DELETEED_FILES_IN_THE_RECYCLE = {EN: "No deleted files in the recycle",
                                  ZH_CN: u"回收站里没有删除的文件"}
ERR_MSG_ACTIVE_STATUS_FILE_SHARE_SERVICE_ALREADY_EXISTED = {EN: "file share service %s already existed",
                             ZH_CN: u"文件服务器 %s 已经存在,只允许创建一个文件服务器"}
ERR_MSG_ACTIVE_STATUS_FILE_SHARE_SERVICE_CANT_DELETE= {EN: "active status file share service %s , cant delete",
                                  ZH_CN: u"激活状态的文件服务器 %s ，不能删除"}
ERR_MSG_FILE_SHARE_SERVICE_NO_FOUND = {EN: "file share service %s no found",
                                  ZH_CN: u"文件服务器 %s 没有找到"}
ERR_MSG_NO_FOUND_ACTIVE_FILE_SHARE_SERVICE = {EN: "no found actived file share service",
                                  ZH_CN: u"没有找到激活的文件服务器"}
ERR_MSG_FILE_SHARE_SERVICE_CANT_USE = {EN: "file share service cant use",
                                  ZH_CN: u"文件服务器不可用"}
ERR_MSG_FILE_SHARE_GROUP_SHOW_LOCATION_ERROR = {EN: "show_location %s error",
                                  ZH_CN: u"访问入口 %s 有误"}
ERR_MSG_FILE_SHARE_VOLUME_SIZE_QUOTA_EXCEEDED = {EN: "QuotasExceeded, you only have [%s GB] high performance volume size quota left currently",
                             ZH_CN: u"存储硬盘配额不足，只剩 [%s GB]硬盘可用"}
ERR_MSG_FILE_SHARE_INSTANCE_QUOTA_EXCEEDED = {EN: "QuotasExceeded, you only have %s instance quota left currently",
                             ZH_CN: u"主机配额不足，只剩 %s 个主机可用"}
ERR_MSG_FILE_SHARE_S2_SERVER_QUOTA_EXCEEDED = {EN: "QuotasExceeded, you only have %s s2_server quota left currently",
                             ZH_CN: u"共享存储vNAS配额不足，只剩 %s 个共享存储vNAS可用"}

ERR_MSG_NO_FOUND_IMAGE_UBUNTU_SERVER_160405_ERROR = {EN: "image Ubuntu Server 16.04.5 LTS 64bit [%s] is not found in iaas console currently",
                             ZH_CN: u"创建文件服务器所需要的iaas后台系统镜像Ubuntu Server 16.04.5 [%s] 没有找到"}

ERR_MSG_LOCALHOST_CANT_CONNECT_NETWORK = {EN: "localhost cant connect network %s",
                             ZH_CN: u"本地服务主机无法连接网络 %s, 请选择其他可用网络"}

ERR_MSG_CREATE_BROKER_APP_RESOURCE_FAILED = {EN: "create broker app resource %s failed",
                                  ZH_CN: u"创建虚拟应用(DDC) %s 失败"}
ERR_MSG_DETACH_BROKER_APP_INVAILD_PARAMS = {EN: "detach broker app invaild param %s",
                                  ZH_CN: u"解绑虚拟应用参数错误 %s"}
ERR_MSG_DETACH_BROKER_APP_NO_FOUND_GROUP = {EN: "broker app no found group %s",
                                  ZH_CN: u"虚拟应用没有发现组 %s"}

ERR_MSG_BROKER_APP_MUST_BE_IN_A_GROUP = {EN: "broker app must be in a group %s",
                                  ZH_CN: u"虚拟应用至少需要在一个交付组或者应用组中%s"}
ERR_MSG_NO_FOUND_APP_INSTANCE_SERVER = {EN: "no found app instance server %s",
                                  ZH_CN: u"没有找到应用服务器%s"}
ERR_MSG_APP_NAME_EXISTED = {EN: "broker app name %s existed",
                              ZH_CN: u"应用程序名称 %s已存在"}
ERR_MSG_APP_GROUP_NAME_EXISTED = {EN: "broker app group name %s existed",
                              ZH_CN: u"应用程序组名称 %s已存在"}

ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_IP_ERROR = {EN: "Load file share service FTP IP address connection failed",
                                  ZH_CN: u"文件共享服务  文件服务器IP地址连接失败"}
ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_USERNAME_PASSWORD_ERROR = {EN: "Load file share service FTP username or password error",
                                  ZH_CN: u"文件共享服务  文件服务器密码错误"}
ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_PUT_FAIL = {EN: "Load file share service FTP put failed",
                                  ZH_CN: u"文件共享服务  文件服务器没有上传权限"}
ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_GET_FAIL = {EN: "Load file share service FTP get failed",
                                  ZH_CN: u"文件共享服务  文件服务器没有下载权限"}
ERR_MSG_LOAD_FILE_SHARE_SERVICE_FTP_DELETE_FAIL = {EN: "Load file share service FTP delete failed",
                                  ZH_CN: u"文件共享服务  文件服务器没有删除权限"}

ERR_MSG_CREATE_FILE_SHARE_GROUP_FAILED = {EN: "550 Create directory operation failed.",
                                    ZH_CN: u"创建共享文件夹失败.当前文件夹下,该FTP用户账号没有创建文件夹的权限."}
ERR_MSG_RENAME_FILE_SHARE_GROUP_FAILED = {EN: "550 Permission denied.",
                                    ZH_CN: u"共享文件夹重命名失败."}
ERR_MSG_NO_DELETE_FILE_SHARE_GROUP_FAILED = {EN: "delete file share group  [%s] failed",
                                  ZH_CN: u"共享文件夹 [%s] 删除失败"}
ERR_MSG_RESET_FILE_SHARE_SERVICE_PASSWORD_FAILED = {EN: "file share service login user %s reset password failed",
                               ZH_CN: u"文件共享服务登录用户 %s重置密码失败"}
ERR_MSG_LOADED_FILE_SHAER_SERVICE_NOT_SUPPORT_PASSWORD_RESET = {EN: "the loaded server does not support password reset.",
                                    ZH_CN: u"导入的文件共享服务器不支持重置密码."}

#desktop maintainer
ERROR_MSG_CREATE_DESKTOP_MAINTAINER_ERROR = {EN: "create desktop maintainer error",
                                             ZH_CN: u"创建桌面维护信息失败"}
ERROR_MSG_DESKTOP_MAINTAINER_NAME_EXISTED_ERROR = {EN: "desktop maintainer name [%s] is existed.",
                                             ZH_CN: u"桌面维护信息名称 [ %s] 已经存在"}
ERROR_MSG_DESKTOP_MAINTAINER_NO_FOUND_ERROR = {EN: "desktop maintainer [%s] no found",
                                               ZH_CN: u"桌面维护 %s 没有找到"}
ERR_MSG_DESKTOP_MAINTAINER_NO_DESKTOP_INSTANCE = {EN: "desktop no instance %s",
                                                  ZH_CN: u"桌面 %s 没有主机资源"}
ERR_MSG_RESOURCE_ALREAY_EXISTED_DESKTOP_MAINTAINER = {EN: "resource %s has already existed in desktop maintainer %s",
                                                     ZH_CN: u"资源 %s 已经存在于桌面维护组 %s 中"}
ERR_MSG_CREATE_DESKTOP_MAINTAINER_RESOURCE_FAILED = {EN: "create desktop maintainer resource failed",
                                                    ZH_CN: u"创建桌面维护组资源失败"}
ERR_MSG_RESOURCE_NOT_IN_DESKTOP_MAINTAINER = {EN: "resource %s not in desktop maintainer %s",
                                             ZH_CN: u"资源 %s 不存在于桌面维护组 %s 中"}
ERR_MSG_DELETE_DESKTOP_MAINTAINER_RESOURCE_FAILED = {EN: "delete desktop maintainer resource failed %s",
                                                     ZH_CN: u"删除桌面维护组资源失败 %s"}

# WORKFOW
ERROR_MSG_WF_API_ACTION_PARAM_NO_FOUND = {EN: "api action %s param %s no found",
                                             ZH_CN: u"%s 没有找到参数 %s"}

ERROR_MSG_WF_API_ACTION_HANDLE_PARAM_NO_FOUND = {EN: "api action %s param no found",
                                             ZH_CN: u"%s 没有找到参数"}

ERR_MSG_WORKFLOW_MODEL_DISMATCH = {EN: "workflow model %s dismatch",
                              ZH_CN: u"工作流模板%s不匹配"}

ERR_MSG_DESKTOP_NAME_ALREADY_EXISTED_IN_DOMAIN = {EN: "desktop %s already existed in domain",
                              ZH_CN: u"桌面名称 %s 已存在域中，无法加域 "}