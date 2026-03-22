import copy
import context

from common import (
    return_error,
    return_success,
    get_reverse,
    get_sort_key,
    build_filter_conditions,
)
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from log.logger import logger
from resource_control.guest.guest import modify_guest_connect_info
from resource_control.desktop.desktop import get_desktop_id
from resource_control.user.apply_approve import (
    describe_user_in_apply_groups,
    describe_resource_in_apply_groups,
    )
from db.constants import (
    DEFAULT_LIMIT, 
    TB_APPLY
)
from constants import (
    APPLY_TYPE_UNLOCK,
    APPLY_FORM_STATUS_PASSED,
    APPLY_FORM_STATUS_CREATED,
    APPLY_FORM_STATUS_REJECTED
    )
DEFAULT_APPLY_DISPLAY_COLUMNS = ["apply_id", "apply_title", "apply_description", "status", "apply_user_id", "apply_user_name", "apply_real_name",
                                 "approve_user_id", "approve_user_name", "approve_real_name", "resource_group_id", 
                                 "apply_age", "create_time", "start_time", "end_time", "update_time"]

def handle_describe_user_desktop_session(req):
    ctx = context.instance()
    approveEmpId = req.get("approveEmpId")
    if not approveEmpId:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "approveEmpId"))


    # check must parameters
    req["apply_age"] = [1, 99]
    filter_conditions = build_filter_conditions(req, TB_APPLY)
    display_columns = DEFAULT_APPLY_DISPLAY_COLUMNS
    
    if approveEmpId:
        filter_conditions["approve_user_name"] = approveEmpId
    approve_status = req.get("approveState")
    if approve_status:
        approveState = APPLY_FORM_STATUS_PASSED
        if approve_status == "02":
            approveState = APPLY_FORM_STATUS_PASSED
        elif approve_status == "01":
            approveState = APPLY_FORM_STATUS_CREATED
        elif approve_status == "03":
            approveState = APPLY_FORM_STATUS_REJECTED
        filter_conditions["status"] = approveState
    filter_conditions["apply_type"] = APPLY_TYPE_UNLOCK
    
    apply_set = ctx.pg.get_by_filter(TB_APPLY, filter_conditions, display_columns,
                                     sort_key=get_sort_key(TB_APPLY, req.get("sort_key")),
                                     reverse=get_reverse(req.get("reverse")),
                                     offset=0,
                                     limit=DEFAULT_LIMIT)
    if apply_set is None:
        logger.error("describe apply form failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    #format values
    desktops = []
    for apply_id, apply_form in apply_set.items():
        format_apply = {}
        format_apply["apId"] = apply_id
        format_apply["applyUserId"] = apply_form["apply_user_id"]
        format_apply["applyCode"] = apply_form["apply_title"]
        format_apply["applyReason"] = apply_form["apply_description"]
        format_apply["applyDate"] = apply_form["create_time"]
        format_apply["applyEmpId"] = apply_form["apply_user_name"]
        format_apply["applyEmpName"] = apply_form.get("apply_real_name") if apply_form.get("apply_real_name") else apply_form["apply_user_name"]
        format_apply["applyHourage"] = apply_form["apply_age"]
        format_apply["approveUserId"] = apply_form["approve_user_id"]
        format_apply["approveEmpId"] = apply_form["approve_user_name"]
        format_apply["approveEmpName"] = apply_form.get("approve_real_name") if apply_form.get("approve_real_name") else  apply_form["approve_user_name"]
        format_apply["approveState"] = apply_form["status"]
        format_apply["approveDate"] = apply_form["start_time"]
        format_apply["approveDate2"] = apply_form["end_time"]
        format_apply["applyStartDate"] = apply_form["start_time"]
        format_apply["applyEndDate"] = apply_form["end_time"]

        # describe apply group id
        user_in_apply_groups = describe_user_in_apply_groups(apply_form["apply_user_id"])
        if not isinstance(user_in_apply_groups, Error):
            resource_in_apply_groups = describe_resource_in_apply_groups(apply_form["resource_group_id"])
            if not isinstance(resource_in_apply_groups, Error):
                for apply_group_id in user_in_apply_groups:
                    if apply_group_id in resource_in_apply_groups:
                        format_apply["applyGrpId"] = apply_group_id

        # describe computer info
        machines = ctx.res.resource_describe_computers(req["sender"]["zone"], deliverygroup_names=apply_form["resource_group_name"])
        if machines:
            for _,machine in machines.items():
                if machine["assign_user"] != format_apply["applyEmpId"]:
                    continue
                format_apply_item = copy.copy(format_apply)
                format_apply_item["applyDeskId"] = machine["uuid"]
                format_apply_item["deliverGrpId"] = apply_form["resource_group_id"]
                format_apply_item["deliverGrpName"] = apply_form["resource_group_name"]
                format_apply_item["lastLoginDate"] = machine["session_state_changetime"]
                format_apply_item["hostName"] = machine["hosted_machine_name"]
                format_apply_item["hostIp"] = machine["machine_IP"]
                format_apply_item["sessionId"] = machine.get("session_uid")
                format_apply_item["onlineState"] = machine.get("session_status")
                desktops.append(format_apply_item)

    total = len(desktops)
    last_page = 1 if total%10 > 0 else 0
    pages = total/10 + last_page
    pageNo = req.get("pageNo")
    if not pageNo:
        pageNo = 1

    start = 0
    end = total
    if total > 10:
        start = (pageNo-1)*10
        if pageNo < pages:
            end = pageNo*10
        else:
            end = total 

    data_set = desktops[start:end]
    row_id = 0
    for item in data_set:
        row_id = row_id + 1
        item["row_id"] = row_id

    rep = {
        "data_set": data_set,
        "pageNum": pageNo,
        "pageSize": 10,
        "startRow": 0,
        "endRow": row_id-1,
        "total": len(apply_set),
        "pages": pages
        }
    return return_success(req, rep)


def handle_logout_user_desktop_session(req):
    ctx = context.instance()
    session_uid = req.get("workerUid")
    ret = ctx.res.resource_stop_broker_session(req["sender"]["zone"], session_uid)
    if ret is None:
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_LOGOUT_USER_DESKTOP_SESSION))
    rep = {"workerUid": session_uid}
    return return_success(req, rep)


def handle_modify_user_desktop_session(req):
    ctx = context.instance()
    user_name = req.get("applyEmpId")
    if not user_name:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "applyEmpId"))

    delivery_group_name = req.get("deliverGrpName")
    hostname = req.get("hostname")

    machines = []
    if delivery_group_name:
        delivery_group_computers = ctx.res.resource_describe_computers(req["sender"]["zone"], deliverygroup_names=[delivery_group_name])
        if not delivery_group_computers:
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DELIVERY_GROUP_HAVE_NO_COMPUTER, delivery_group_name))
        if hostname:
            if hostname in delivery_group_computers.keys():
                machines.append(delivery_group_computers[hostname])
    else:
        if hostname:
            machine = ctx.res.resource_describe_computers(req["sender"]["zone"], machine_names=[hostname])
            if not machine:
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_COMPUTER_NOT_FOUND, hostname))
            machines.append(machine[hostname])
        else:
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "delivery_group_name,hostname"))

    for machine in machines:
        hostname = machine["hosted_machine_name"]
        values = {}
        values["connect_status"] = int(machine.get("session_state") if machine.get("session_state") else "0")
        if machine.get("assign_user"):
            values["login_user"] = machine["assign_user"]
        else:
            continue
        if machine.get("session_starttime"):
            values["connect_time"] = machine["session_starttime"]
        if machine.get("session_state_changetime"):
            values["disconnect_time"] = machine["session_state_changetime"]
        if machine.get("session_uid"):
            values["session_uid"] = machine["session_uid"]
        desktop_id = get_desktop_id(hostname)
        if not modify_guest_connect_info(desktop_id, hostname, values):
            logger.error("modify guest user desktop_session error")
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                           ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE))

    rep = {"hostname": hostname}
    return return_success(req, rep)
