from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet
import socket

RADIUS_CONFIG = "pitrix-desktop-common/common/conf/radius"

def check_radius_token(radius_service, user_name, token):
    
    host = radius_service["host"]
    port = radius_service["port"]
    secret = radius_service["secret"]
    identifier = radius_service["identifier"]
    acct_session = radius_service["acct_session"]
    
    try:
        srv = Client(server = host, secret = secret, dict = Dictionary(RADIUS_CONFIG))
        radreq = srv.CreateAuthPacket(code = pyrad.packet.AccessRequest, User_Name = user_name)

        radreq["User-Password"] = radreq.PwCrypt(token)
        radreq["NAS-IP-Address"] = host
        radreq["NAS-Port"] = port
        radreq["Service-Type"] = "Login-User"
        if identifier:
            radreq["NAS-Identifier"] = identifier
        
        if acct_session:
            radreq["Acct-Session-Id"] = acct_session

        reply = srv.SendPacket(radreq)
        if reply is None or reply.code is None :
            logger.error("radius send packet fail")
            return Error(ErrorCodes.RADIUS_CONNECT_CHECK_ERROR,
                         ErrorMsg.ERR_MSG_RADIUS_CONNECT_ERROR)

        if reply.code == pyrad.packet.AccessAccept:
            return True
        elif reply.code == pyrad.packet.AccessReject:
            logger.error("radius Access Reject")
            return Error(ErrorCodes.RADIUS_CHECK_REJECT_ERROR,
                         ErrorMsg.ERR_MSG_RADIUS_CHECK_REJECT,user_name)
        else:
            logger.error("radius other code%s"%reply.code)
            return Error(ErrorCodes.RADIUS_CHECK_OTHER_ERROR,
                         ErrorMsg.ERR_MSG_RADIUS_CHECK_OTHER_ERROR)

    except pyrad.client.Timeout:
        logger.error("radius connect timeout")
        return Error(ErrorCodes.RADIUS_CONNECT_CHECK_ERROR,
                         ErrorMsg.ERR_MSG_RADIUS_CONNECT_ERROR)

    except socket.error as error:
        logger.error("Network error:"+ error[1])
        return Error(ErrorCodes.RADIUS_CONNECT_CHECK_ERROR,
                     ErrorMsg.ERR_MSG_RADIUS_CONNECT_ERROR)
    except Exception, e:
        logger.error("radius check error %s"%e)
        return Error(ErrorCodes.RADIUS_CHECK_OTHER_ERROR,
                         ErrorMsg.ERR_MSG_RADIUS_CHECK_OTHER_ERROR)

def check_user_group_auth_radius(user_id):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_user_group(user_id)
    if not ret:
        return None
    
    user_group_ids = ret
    
    ret = ctx.pgm.get_radius_users(user_ids = user_group_ids)
    if not ret:
        return None
    
    for _, radius_user in ret.items():
        if radius_user["check_radius"]:
            return radius_user
    
    return ret.values()[0]
    
def get_user_auth_radius(desktop_user):
    
    ctx = context.instance()

    user_name = desktop_user["user_name"]
    auth_service_id = desktop_user["auth_service_id"]

    auth_radius = ctx.pgm.get_auth_radius(auth_service_id)
    if not auth_radius:
        return None

    ou_dn = auth_radius["ou_dn"]
    if not ou_dn:
        ou_dn = None

    ret = ctx.auth.get_auth_users(auth_service_id, ou_dn, user_name)
    if not ret:
        return None

    return auth_radius
    
def check_radius_user(desktop_user):
    
    ctx = context.instance()
    user_id = desktop_user["user_id"]
    
    
    ret = get_user_auth_radius(desktop_user)
    if not ret:
        return None
    
    auth_radius = ret

    radius_user = ctx.pgm.get_radius_user(user_id)
    if not radius_user:
        radius_user = check_user_group_auth_radius(user_id)
        if not radius_user:
            return None
    
    if auth_radius["status"] != const.SERVICE_STATUS_CONN_ACTIVE or not auth_radius["enable_radius"]:
        return None
    
    if radius_user["check_radius"]:
        return auth_radius
    else:
        return None

