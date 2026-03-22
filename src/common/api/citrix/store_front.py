import os
import constants as const
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from common import (
    _get_dir_index,
    _get_file_number,
    _clean_connection_file,
    _rsync_connect_file
)
from api.citrix.store_front_cookie import StoreFrontCookie
from requests.exceptions import ConnectionError
import api.user.resource_user as ResUser 
from utils.json import json_dump, json_load
class ZoneStoreFront:

    def __init__(self, ctx, zone_id, citrix_conn, auth_service):
        
        self.ctx = ctx
        self.zone_id=zone_id
        self.citrix_connection = citrix_conn
        self.auth_service = auth_service
        self.base_url = None
        self.base_url_list = None
        self.host = None
        self.ns_flag =None 
        self.init_zone_store_front()

    def init_zone_store_front(self):

        try:
            ns_flag = self.citrix_connection["support_netscaler"]
            if ns_flag is None:
                return None
            self.base_url_list=[]
            base_url=None
            if ns_flag ==0:   
                storefront_uri = self.citrix_connection["storefront_uri"]
                if not storefront_uri:
                    return None                
                if storefront_uri[:2]=="[{":               
                    storefront_uri=json_load(storefront_uri)
                if not storefront_uri:
                    return None

                if isinstance(storefront_uri ,list):
                    for uri_data in storefront_uri:
                        sf_uri = uri_data["sf_uri"]
                        sf_port = uri_data["sf_port"]
                        base_url,host=self.init_store_front_info(sf_uri,sf_port,ns_flag)
                        sf_data={}
                        sf_data["base_url"]=base_url
                        sf_data["host"]=host    
                        self.base_url_list.append(sf_data)     
     
                    self.base_url=self.base_url_list[0]["base_url"]
                    self.host=self.base_url_list[0]["host"]         
                        
                else:
                    storefront_port = self.citrix_connection["storefront_port"]             
                    if not storefront_port:
                        return None
                    base_url,host=self.init_store_front_info(storefront_uri,storefront_port,ns_flag)
                    sf_data={}
                    sf_data["base_url"]=base_url
                    sf_data["host"]=host    
                    self.base_url_list.append(sf_data) 
                    self.base_url=base_url
                    self.host=host           
              
            else:      
                
                netscaler_uri = self.citrix_connection["netscaler_uri"]
                if not netscaler_uri:
                    return None
                if netscaler_uri[:2]=="[{":               
                    netscaler_uri=json_load(netscaler_uri)
                if not netscaler_uri:
                    return None

                if isinstance(netscaler_uri ,list):
                    for uri_data in netscaler_uri:
                        ns_uri = uri_data["ns_uri"]
                        ns_port = uri_data["ns_port"]
                        base_url,host=self.init_store_front_info(ns_uri,ns_port,ns_flag)
                        ns_data={}
                        ns_data["base_url"]=base_url
                        ns_data["host"]=host    
                        self.base_url_list.append(ns_data)     
     
                    self.base_url=self.base_url_list[0]["base_url"]
                    self.host=self.base_url_list[0]["host"]         
                        
                else:
                    netscaler_port = self.citrix_connection["netscaler_port"]
                    if not netscaler_port:
                        return None   
                    base_url,host=self.init_store_front_info(netscaler_uri,netscaler_port,ns_flag)
                    ns_data={}
                    ns_data["base_url"]=base_url
                    ns_data["host"]=host    
                    self.base_url_list.append(ns_data) 
                    self.base_url=base_url
                    self.host=host                

            self.ns_flag = ns_flag
        except Exception,e:
            logger.error("init sf zone info with Exception:%s" % e)
            self.base_url=None
            self.host=None   
            return Error(ErrorCodes.STOREFRONT_INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_STOREFRONT_CONFIG_ERROR)
    def init_store_front_info(self,_uri,_port,ns_flag=0):

        if "://" in _uri:
            base_index1 = _uri.index("://")
            protocol=_uri[:base_index1] 
            _uri = _uri[base_index1+3:]             
        else :
            protocol="http" 

        if ns_flag==0:
            if "/" in _uri:
                base_index = _uri.index("/")
            else:
                base_index = len(_uri) - 1
    
            host = _uri[:base_index]
            uri = _uri[base_index:]
    
            if protocol=="http":
                if _port != 80:
                    _uri = "%s:%s%s" % (host, _port,uri)            
                if "http://" in _uri:
                    base_url = _uri
                else:
                    base_url = "http://%s" % _uri       
            else:            
                if _port != 443:
                    _uri = "%s:%s%s" % (host, _port,uri)    
                if "https://" in _uri:
                    base_url = _uri
                else:
                    base_url = "https://%s" % _uri         
        else:
            if "://" in _uri:
                base_index1 = _uri.index("://")
                _uri = _uri[base_index1+3:] 
    
            if "/" in _uri:
                base_index = _uri.index("/")
            else:
                base_index = len(_uri) - 1
    
            host = _uri[:base_index]
            uri = _uri[base_index:]
             
            _uri = "%s:%s%s" % (host, _port,uri)    

            if "https://" in _uri:
                base_url = _uri
            else:
                base_url = "https://%s" % _uri             
        return base_url,host
    
    def get_store_fornt_cookie(self, zsf, cookie=None):

        sf_cookie = StoreFrontCookie(self.ctx, zsf, cookie)
        if not sf_cookie:
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                             ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, cookie)
        
        if not sf_cookie.check_store_front_cookie(cookie):
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                             ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, cookie)
        
        return sf_cookie

    def create_storefront_connect_files(self, desktop_id, sf_ica):

        if not sf_ica:
            return False

        if not os.path.isdir(const.STOREFRONT_CONNECT_FILE_DIR):
            os.system("mkdir -p %s" % const.STOREFRONT_CONNECT_FILE_DIR)
            os.system("chmod 777 %s" % const.STOREFRONT_CONNECT_FILE_DIR)

        brokers = []
        broker={}
        broker["ui_type"] = "storefront"
        broker["desktop_id"] = desktop_id
        conn_file = "%s.ica" % desktop_id

        if desktop_id.startswith(const.RES_DESKTOP):
            desktop_id_context = desktop_id.split('-')[1]
            desktop_id_prefix = desktop_id_context[0:2]
        else:
            desktop_id_prefix = 'random'

        path = "%s/%s" % (const.STOREFRONT_CONNECT_FILE_DIR, desktop_id_prefix)
        if not os.path.exists(path):
            os.mkdir(path)

        conn_file_path = "%s/%s" % (path, conn_file)

        try:
            with open(conn_file_path, "w") as f:
                contents = sf_ica
                f.writelines(contents)
        except Exception, e:
            logger.error("write file [%s] failed, [%s]" % (conn_file_path, e))
            return False

        broker["connect_file_uri"] = "%s/%s/%s" % (const.STOREFRONT_CONNECT_FILE_BASE_URI, desktop_id_prefix, conn_file)
        status = self.ctx.pgm.get_desktop_service_management_vnas_server_status()
        if status == const.SERVICE_STATUS_INVAILD or self.ctx.zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            _rsync_connect_file(self.ctx,conn_file_path,path)

        brokers.append(broker)
        return brokers

    def unassign_desktop(self, sf_cookie, assign_uri, user_id, ica_uri):

        hostname = sf_cookie.assign_desktop_url(assign_uri)
        if hostname is None:
            return Error(ErrorCodes.STOREFRONT_ASSIGN_DESKTOP_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_ERROR)

        desktops = self.ctx.pgm.get_desktop_by_hostnames(hostname, zone_id=self.zone_id)
        if not desktops:
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                       ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, hostname)

        desktop = desktops[hostname]
        if not desktop:
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                       ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, hostname)        
        desktop_id = desktop["desktop_id"]              
        delivery_group_name=desktop["delivery_group_name"]                                 
        if not delivery_group_name:
            return Error(ErrorCodes.STOREFRONT_DLV_NAME_ERROR,
                       ErrorMsg.ERR_MSG_STOREFRONT_DLV_NAME_MISSING_ERROR, hostname)    

        ret = ResUser.add_user_to_resource(self.ctx, desktop_id, user_id)
        if isinstance(ret, Error):
            return ret

        ret = self.download_storefront_desktop_ica(sf_cookie, ica_uri, delivery_group_name, desktop_id)
        return ret

    def assign_desktop(self, sf_cookie, ica_uri, desktop_id):

        desktops = self.ctx.pgm.get_desktops(desktop_id)
        if not desktops:
            logger.error("desktop [%s] no found" % desktop_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_id)

        desktop = desktops[desktop_id]
        delivery_group_name=desktop["delivery_group_name"] 
        hostname=desktop["hostname"]  
        if not delivery_group_name:
            return Error(ErrorCodes.STOREFRONT_DLV_NAME_ERROR,
                       ErrorMsg.ERR_MSG_STOREFRONT_DLV_NAME_MISSING_ERROR, hostname)  
        ret = self.download_storefront_desktop_ica(sf_cookie, ica_uri, delivery_group_name, desktop_id)
        return ret

    def storefront_get_ica(self, zsf, cookie, assign, ica_uri, user_id, desktop_id=None, assign_uri=None):

        ret = self.get_store_fornt_cookie(zsf, cookie)
        if isinstance(ret, Error):
            return ret
        sf_cookie = ret

        if assign == 0:
            ret = self.unassign_desktop(sf_cookie, assign_uri, user_id, ica_uri)               
        elif assign==1:
            ret = self.assign_desktop(sf_cookie,ica_uri, desktop_id)
        elif assign==2:
            delivery_group_name = assign_uri
            if not delivery_group_name:
                return Error(ErrorCodes.STOREFRONT_DLV_NAME_ERROR,
                       ErrorMsg.ERR_MSG_STOREFRONT_DLV_NAME_MISSING_ERROR, desktop_id)  
            index1 = ica_uri.find('ca/')
            index2 = ica_uri.find('.ica')
            desktop_id = ica_uri[index1+3:index2]
            ret = self.download_storefront_desktop_ica(sf_cookie, ica_uri, delivery_group_name, desktop_id)
        elif assign==3:
            app_mode = "app"
            index1 = ica_uri.find('ca/')
            index2 = ica_uri.find('.ica')
            desktop_id = ica_uri[index1+3:index2]
            ret = self.download_storefront_desktop_ica(sf_cookie, ica_uri, app_mode, desktop_id)  
        return ret

    def get_storefront_desktoplist(self, zsf, cookie):

        try:            
            ret = self.get_store_fornt_cookie(zsf, cookie)
            if isinstance(ret, Error):
                return ret
            sf_cookie = ret
            ret = sf_cookie.resources_list()
            if isinstance(ret, Error):
                return ret
    
            res_assignlist, res_unassignlist, res_randomlist,res_applist = ret
            #first list database    
            assignlist ={}
            if not res_assignlist:
                res_assignlist = []
            
            for sf_desktop in res_assignlist:
                sf_desktop_hostname = sf_desktop['desktop_host_name']
                sf_dlv_group_name = sf_desktop['delivery_group_name']
                if not sf_desktop_hostname or not sf_dlv_group_name:
                    logger.error("sf desktop %s no found delviery group %s info" % (sf_desktop_hostname, sf_dlv_group_name))
                    continue                
                assignlist[sf_desktop_hostname.lower()] = sf_desktop
            return assignlist, res_unassignlist, res_randomlist,res_applist

        except ConnectionError as e:
            logger.error("storefront except : %s" % e)
            return Error(ErrorCodes.STOREFRONT_CONNECTION_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_CONNECTION_ERROR,self.zone_id)

    def download_storefront_desktop_ica(self, sf_cookie, ica_uri, dlv_name, desktop_id):

        status_uri = ica_uri.replace("LaunchIca","GetLaunchStatus")
        status_uri = status_uri[:-4]
        ret = sf_cookie.resources_get_lanch_status(status_uri)
        if isinstance(ret, Error):
                return ret                        
        sf_ica = sf_cookie.resources_launch_ica(ica_uri,dlv_name)
        if sf_ica is None:
            return Error(ErrorCodes.STOREFRONT_NOTFOUND_ICA_ERROR,
                         ErrorMsg.ERR_MSG_STOREFRONT_NOTFOUND_ICA_ERROR)
        ret = self.create_storefront_connect_files(desktop_id, sf_ica)
        if ret is None:
            return Error(ErrorCodes.STOREFRONT_DOWNLOAD_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_DOWNLOAD_ICA_ERROR)
        return ret

    def create_token_storefront_login(self, zsf, user_name, password,sf_uris):

        ret = self.get_store_fornt_cookie(zsf)
        if isinstance(ret, Error):
            return ret
        
        sf_cookie = ret
        auth_domain = self.auth_service["domain"]
        citrix_username = "%s@%s" % (user_name ,auth_domain)
        if self.ns_flag==0:
            for item in zsf.base_url_list:                    
                zsf.base_url=item["base_url"]
                zsf.host=item["host"]
                if sf_uris and zsf.base_url in sf_uris.keys():
                    store_login_cookie=sf_uris[zsf.base_url]
                    return store_login_cookie
                try:
                    sf_med = sf_cookie.get_auth_methods()
                    if isinstance(sf_med, Error):
                        logger.error(" %s get_auth_methods failed" % zsf.base_url)
                        continue
                    store_login_cookie = sf_cookie.post_credentials_auth_login(citrix_username, password)
                    if store_login_cookie is None:
                        logger.error("storeset failed")
                        continue
                    if sf_uris is not None:
                        sf_uris[zsf.base_url]=store_login_cookie
                    return store_login_cookie
                except ConnectionError as e:
                    logger.error("storefront except : %s" % e)
                    continue
                except Exception, e:
                    logger.error("storefront except : %s" % e)
                    continue                    
                    #return Error(ErrorCodes.STOREFRONT_CONNECTION_ERROR, ErrorMsg.ERR_MSG_STOREFRONT_CONNECTION_ERROR,self.zone_id)                        
                  
            return Error(ErrorCodes.STOREFRONT_LOGIN_ERROR, 
                                 ErrorMsg.ERR_MSG_STOREFRONT_LOGIN_ERROR)
        else:
            for item in zsf.base_url_list:                    
                zsf.base_url=item["base_url"]
                zsf.host=item["host"]
                if sf_uris and zsf.base_url in sf_uris.keys():
                    store_login_cookie=sf_uris[zsf.base_url]
                    return store_login_cookie                
                try:
                    store_login_cookie=sf_cookie.ns_storefront_login(user_name, password)   
                    if store_login_cookie is None:
                        logger.error("netscaler storefront failed")
                        continue
                    if sf_uris:
                        sf_uris[zsf.base_url]=store_login_cookie
                    return store_login_cookie                 
                except ConnectionError as e:
                    logger.error("storefront except : %s" % e)
                    continue                    

            return Error(ErrorCodes.STOREFRONT_LOGIN_ERROR, 
                             ErrorMsg.ERR_MSG_STOREFRONT_LOGIN_ERROR)  

