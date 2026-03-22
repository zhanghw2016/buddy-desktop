from constants import(
    SCHETASK_TYPE_RESTART_DG,
    SCHETASK_TYPE_START_DG,
    SCHETASK_TYPE_STOP_DG,
    SCHETASK_TYPE_MODIFY_DG_COUNT,
    SCHETASK_TYPE_AUTO_SNAPSHOT,
)

import db.constants as dbconst
import resource.desktop_group as DesktopGroupTask
import resource.delivery_group as DeliveryGroupTask
import resource.snapshot as SnapshotTask
from constants import SCHETASK_TYPE_UPDATE_DESKTOP_IMAGE


def handle_scheduler_task(scheduler_task):

    task_type = scheduler_task["task_type"]
    resource_type = scheduler_task["resource_type"]

    if task_type in [SCHETASK_TYPE_RESTART_DG, SCHETASK_TYPE_START_DG, SCHETASK_TYPE_STOP_DG]:
        
        if resource_type == dbconst.RESTYPE_DELIVERY_GROUP:
            return DeliveryGroupTask.task_handle_delivery_groups(scheduler_task)
        elif resource_type == dbconst.RESTYPE_DESKTOP_GROUP:
            return DesktopGroupTask.task_handle_desktop_groups(scheduler_task)

    elif task_type in [SCHETASK_TYPE_MODIFY_DG_COUNT, SCHETASK_TYPE_UPDATE_DESKTOP_IMAGE]:
        return DesktopGroupTask.task_handle_desktop_groups(scheduler_task)
        
    elif task_type == SCHETASK_TYPE_AUTO_SNAPSHOT:
        return SnapshotTask.task_handle_auto_snapshot(scheduler_task)
    else:
        return None
    