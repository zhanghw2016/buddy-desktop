import context
from log.logger import logger
import constants as const
import db.constants as dbconst
from error.error import Error
from resource_workflow import ResourceWorkflow


def update_workflow_return(workflow_id, api_return, result):
    
    ctx = context.instance()
    update_info = {}
    if api_return:
        update_info["api_return"] = api_return

    if result:
        update_info["result"] = result
        
    if not ctx.pg.batch_update(dbconst.TB_WORKFLOW, {workflow_id: update_info}):
        logger.error("update newly workflow status for [%s] db failed" % (update_info))
        return -1

    return

def do_workflow_actions(sender, workflow):
    
    ctx = context.instance()
    workflow_model_id = workflow["workflow_model_id"]
    workflow_id = workflow["workflow_id"]
    ResWorkflow = ResourceWorkflow(ctx, workflow_id, workflow_model_id)
    
    for _ in range(ResWorkflow.get_api_action_count()):
        
        curr_action = ResWorkflow.get_current_action()
        if not curr_action:
            break

        ResWorkflow.set_workflow_status(workflow_id, curr_action, const.STATUS_EXECUTING)

        ret = ResWorkflow.handle_resource_workflow(sender, curr_action)
        if ret < 0:
            ResWorkflow.set_workflow_status(workflow_id, curr_action, status=const.WORKFLOW_STATUS_FAIL)
            return -1
        
        ResWorkflow.done_current_action()
    
    ResWorkflow.set_workflow_status(workflow_id, "", status = const.WORKFLOW_STATUS_SUCCESS)

    return 0

def task_execute_workflow(sender, workflow_id):
    
    ctx = context.instance()

    workflow = ctx.pgm.get_workflow(workflow_id)
    if not workflow:
        logger.error("task execute workflow %s fail" % workflow_id)
        return -1
    
    ret = do_workflow_actions(sender, workflow)
    if isinstance(ret, Error):
        logger.error("do workflow action fail %s" % workflow_id)
        return -1

    return 0
