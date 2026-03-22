
import requests
from log.logger import logger
import json
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import urllib
import re
import random
import base64
import HTMLParser
class StoreFrontCookie:

    def __init__(self, ctx, zone_store_front, cookie=None):

        self.ctx = ctx

        self.csrf_token = None
        self.cookies = {}
        self.headers = {}
        self.ica_file = None
        self.naac=None
        self.authcookie=None
        self.ctxs_authid =None          
        self.zsf = zone_store_front
        if cookie:
            self.init_storefront_cookie(cookie)
    
    def check_store_front_cookie(self, cookie=None):
        
        if not self.zsf.base_url:
            return False
        
        if cookie:
            if not self.cookies:
                return False
            
            if not self.csrf_token:
                return False
        
        if not self.zsf.host:
            return False
        
        return True

    def init_storefront_cookie(self, cookie):

        cookietmp = cookie.replace('@',';') 
        self.cookies = cookietmp

        array = re.split(';',cookietmp)
        tokenValue = ""
        for arr in array:
            if arr.find('CsrfToken') >= 0:
                tokenValue = arr
                break
        if tokenValue =="" or tokenValue is None:
            return None 
        index1=tokenValue.index('=')
        token=tokenValue[index1+1:]
        self.csrf_token = token

        return None

    def byteify(self, inputdic):

        if isinstance(inputdic, dict):
            return {self.byteify(key): self.byteify(value) for key, value in inputdic.iteritems()}
        elif isinstance(inputdic, list):
            return [self.byteify(element) for element in inputdic]
        elif isinstance(inputdic, unicode):
            return inputdic.encode('utf-8')
        else:
            return inputdic

    def get_cookie_string(self, cookies):

        cookie_str = ""
        if cookies is None or len(cookies) == 0:
            return cookie_str

        for k, v in cookies.items():
            if len(cookie_str) == 0:
                cookie_str = "%s=%s;" % (k, v)
            else:
                cookie_str = cookie_str + "%s=%s;" % (k, v)
        if len(cookie_str) > 0:
            cookie_str = cookie_str[:-1]
        return cookie_str

    # build request headers
    def build_request_headers(self, uri):

        url = "%s%s" % (self.zsf.base_url, uri)
        logger.debug("base_url %s,zone %s" %(url,self.zsf.zone_id))
        # build headers
        self.headers["Host"] = self.zsf.host
        self.headers["Accept"] = "application/xml, text/xml, */*; q=0.01"
        self.headers["Accept-Language"] = "en-us,en;q=0.7,fr;q=0.3"
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["X-Requested-With"] = "XMLHttpRequest"
        self.headers["X-Citrix-IsUsingHTTPS"] = "No"
        if self.zsf.base_url.find("https://")>=0:
            self.headers["X-Citrix-IsUsingHTTPS"] = "Yes"
        else:
            self.headers["X-Citrix-IsUsingHTTPS"] = "No"        
        self.headers["Referer"] = self.zsf.base_url + "/"
        self.headers["Connection"] = "keep-alive"
        self.headers["Pragma"] = "no-cache"
        self.headers["Cache-Control"] = "no-cache"
        self.headers["User-Agent"] = "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"

        return url

    # /Home/KeepAlive
    def keepalive(self):

        url = self.build_request_headers("/Home/KeepAlive")
        self.headers["Accept"] = "text/plain, */*; q=0.01"
        self.headers["Csrf-Token"] = self.csrf_token   
        self.headers["Cookie"] = self.cookies            
        response = requests.head(url, headers = self.headers,timeout=10)
        if response.status_code == 200 and response.reason == "OK":
            return 0
        else:
            return -1
    # /Home/Configuration
    def home_configuration(self):
        try:
            if self.zsf.ns_flag==0:
                url = self.build_request_headers(uri="/Home/Configuration")
                response = requests.post(url, headers=self.headers, verify=False,timeout=10)
                if response.status_code==200 and response.reason=="OK":
                    return 0
                else:
                    return -1       
            else:
                url = self.build_request_headers(uri="/Home/Configuration")
                self.headers["Cookie"] = self.cookies
                response = requests.post(url, headers=self.headers, verify=False,timeout=10)
                if response.status_code==200 and response.reason=="OK":
                    cookies = requests.utils.dict_from_cookiejar(response.cookies)
                    self.cookies=self.get_cookie_string(cookies)
                    self.csrf_token = cookies["CsrfToken"]   
                    return 0
                else:
                    return -1
        except Exception, e:
            logger.error("response [%s] " % e)
            return -1
        
    # /Authentication/GetAuthMethods
    def get_auth_methods(self):
        try:
            if self.zsf.ns_flag==0:
                url = self.build_request_headers("/Authentication/GetAuthMethods")
                response = requests.post(url, headers = self.headers,timeout=10)
                if response.text.find("PostCredentialsAuth") < 0:
                    logger.error("store havn't PostCredentials method" )
                    return Error(ErrorCodes.STOREFRONT_INTERNAL_ERROR, 
                                 ErrorMsg.ERR_MSG_STOREFRONT_CONFIG_ERROR)
                return 0
            else:
                url = self.build_request_headers(uri="/Authentication/GetAuthMethods")
                self.cookies=self.cookies+";"+self.naac
                self.authcookie=self.cookies
                self.headers["Cookie"] = self.cookies
                self.headers["Csrf-Token"] = self.csrf_token 
                response = requests.post(url, headers=self.headers,verify=False,timeout=10)
                if response.status_code!=200 or response.reason!="OK" or response.text.find("CitrixAGBasic")<0:
                    logger.error("store netscaler get_auth_methods CitrixAGBasic error" )
                    return Error(ErrorCodes.STOREFRONT_INTERNAL_ERROR, 
                                 ErrorMsg.ERR_MSG_STOREFRONT_CONFIG_ERROR)
                else:
                    return 0
        except Exception, e:
            logger.error("response [%s] " % e)
            return Error(ErrorCodes.STOREFRONT_INTERNAL_ERROR, 
             ErrorMsg.ERR_MSG_STOREFRONT_CONFIG_ERROR)
    # /PostCredentialsAuth/Login
    def post_credentials_auth_login(self, username, password):

        try:
            html_parser = HTMLParser.HTMLParser()
            password=html_parser.unescape(password)
            password = urllib.quote(password.encode('utf-8'), '')
            url = self.build_request_headers("/PostCredentialsAuth/Login?username=%s&password=%s" % (username, password))
            response = requests.post(url, headers = self.headers,timeout=10)
            logger.debug("response [%s] " % response.text)
            if response.text.find("loginfailed") >= 0:
                logger.error("loginfailed")
                return None
            else:
                self.cookies = requests.utils.dict_from_cookiejar(response.cookies)
                cookie_strtmp = self.get_cookie_string(self.cookies) 
                cookie_str=cookie_strtmp.replace(';','@')
                return cookie_str
        except Exception, e:
            logger.error("[%s]" % e)
            return None         
    # /Resources/List
    def resources_list(self):
        try:
            url = self.build_request_headers("/Resources/List")
            self.headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
            self.headers["Content-Type"] = "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"
            self.headers["Csrf-Token"] = self.csrf_token           
            cookie_str = self.cookies       
            if self.zsf.ns_flag=="1":
                if cookie_str.find("CtxsAuthId") <0:
                    cookie_str =cookie_str +";CtxsAuthId="+self.ctxs_authid 
                    self.cookies=cookie_str         
    
            self.headers["Cookie"] = self.cookies
            response = requests.post(url, headers = self.headers,verify=False,timeout=10) 
            logger.debug("response [%s] " % response.text)
            if response.text.find("\"unauthorized\":true") >= 0:
                logger.error("unauthorized error")
                return Error(ErrorCodes.STOREFRONT_GETDESKTOPLIST_UNAUTHORIZE_ERROR,
                             ErrorMsg.ERR_MSG_STOREFRONT_GETDESKTOPLIST_UNAUTHORIZE_ERROR)
    
            if response.status_code != 200 or response.text.find("resources")<0:
                return Error(ErrorCodes.STOREFRONT_GETDESKTOPLIST_NODESKTOP_ERROR,
                                 ErrorMsg.ERR_MSG_STOREFRONT_GETDESKTOPLIST_NODESKTOP_ERROR)
            rslist = json.loads(response.text)
            if rslist is None:
                return Error(ErrorCodes.STOREFRONT_GETDESKTOPLIST_NODESKTOP_ERROR,
                                 ErrorMsg.ERR_MSG_STOREFRONT_GETDESKTOPLIST_NODESKTOP_ERROR)
    
            if "resources" not in rslist :
                logger.error("[%s] not resources in this rslist" % response.text)
                return Error(ErrorCodes.STOREFRONT_GETDESKTOPLIST_NODESKTOP_ERROR,
                                 ErrorMsg.ERR_MSG_STOREFRONT_GETDESKTOPLIST_NODESKTOP_ERROR)  
            res_assignlist = []
            res_unassignlist=[]
            res_randomlist=[]
            res_applist=[]
            resource_set = self.byteify(rslist["resources"])
            if len(resource_set) == 0:
                return res_assignlist, res_unassignlist, res_randomlist,res_applist
            for sf_res in resource_set:                     
                res = {}
                if "isdesktop" in sf_res:
                    
                    if sf_res["isdesktop"] and "desktopassignmenttype" in sf_res:
        
                        if sf_res["desktopassignmenttype"]=="assign-on-first-use" :
                            res["launch_url"] ="/"+sf_res["launchurl"]
                            res["assigndesktopurl"] ="/"+sf_res["assigndesktopurl"]
                            res["delivery_group_name"]= sf_res["name"].encode("utf-8")
                            res_unassignlist.append(res)
        
                        elif sf_res["desktopassignmenttype"]=="assigned":                    
                            if "desktophostname" not in sf_res:
                                logger.error("invalid sf_res")
                                continue    
                            res["desktop_host_name"] = sf_res["desktophostname"].encode("utf-8")
                            res["launch_url"] ="/"+sf_res["launchurl"]
                            res["delivery_group_name"]= sf_res["name"].encode("utf-8")
                            res_assignlist.append(res)
        
                        elif sf_res["desktopassignmenttype"]=="shared" :                             
                            res["launch_url"] ="/"+sf_res["launchurl"]
                            res["delivery_group_name"]= sf_res["name"].encode("utf-8")
                            res_randomlist.append(res)                           
                else:
                    res["launch_url"] ="/"+sf_res["launchurl"]
                    icon_url="/"+sf_res["iconurl"]
                    res["app_name"]= sf_res["name"].encode("utf-8")
                    res["icon_data"]=self.resources_get_icon(icon_url)
                    res_applist.append(res)
            return res_assignlist, res_unassignlist, res_randomlist,res_applist
        except Exception, e:
            logger.error("[%s]" % e)
            return Error(ErrorCodes.STOREFRONT_GETDESKTOPLIST_NODESKTOP_ERROR,
                                 ErrorMsg.ERR_MSG_STOREFRONT_GETDESKTOPLIST_ERROR)   
    # /Resources/GetLaunchStatus
    def resources_get_lanch_status(self,uri):
        try:
            url = self.build_request_headers(uri)
            self.headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
            self.headers["Content-Type"] = "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"
            self.headers["Csrf-Token"] = self.csrf_token
            self.headers["Cookie"] = self.cookies
            response = requests.post(url, headers = self.headers,verify=False,timeout=10)
            if response.status_code != 200:
                logger.error("self.csrf_token:%s,self.cookies  : %s" % (self.csrf_token, self.cookies))
                return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_GETSTATUS_ICA_ERROR)
            logger.debug("response [%s] " % response.text)    
            rsstatus = self.byteify(json.loads(response.text))
                
            if "status" not in rsstatus :
                return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_GETSTATUS_ICA_ERROR)
            if rsstatus["status"]=="retry":
                logger.error("[%s] is retry" % response.text)
                return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_GETSTATUS_ICA_RETRY_ERROR)                
            elif rsstatus["status"]=="failure":
                logger.error("[%s] is failure" % response.text)
                if rsstatus["errorId"]=="UnavailableDesktop":
                    return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                             ErrorMsg.ERR_MSG_STOREFRONT_ASSIGN_NO_DESKTOP_ERROR)             
                elif rsstatus["errorId"]=="NoMoreActiveSessions":
                    return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_NOMOREACTIVE_SESSION_ERROR)   
                elif rsstatus["errorId"]=="AppRemoved":
                    return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_NOT_FOUND_ERROR)      
                elif rsstatus["errorId"]=="NotLicensed":
                    return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_LICENSE_ERROR)   
                elif rsstatus["errorId"]=="CouldNotConnectToWorkstation":
                    return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_UNCONN_ERROR)     
                elif rsstatus["errorId"]=="WorkstationInMaintenance":
                    return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_ASSIGN_DESKTOP_INMAINT_ERROR)   
                else:
                    return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_OTHER_ASSIGN_DESKTOP_ERROR)                                                              
            elif rsstatus["status"]=="success":                
                return True
            else :
                return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_GETSTATUS_ICA_ERROR)
        except Exception, e:
            logger.error("[%s]" % e)
            return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_GETSTATUS_ICA_ERROR)
    # /Resources/LanchIca
    def resources_launch_ica(self,uri,desktoptitle):
        try:
            if self.csrf_token and self.cookies  :
                url = self.build_request_headers(uri)
          
                url = url + "?CsrfToken="+self.csrf_token
                if desktoptitle!="app":
                    url = url + "&displayNameDesktopTitle=" + desktoptitle
       
                self.headers["Cookie"] = self.cookies
                lanchidnum=random.randint(100000000000,199999999999)
                if self.zsf.ns_flag==1:
                    url = url + "&IsUsingHttps=Yes"
                    url = url + "&launchId="+str(lanchidnum)                
                    self.headers["isGatewaySession"]=True;
                response = requests.get(url, headers=self.headers,verify=False,timeout=10)                       
                if response.status_code != 200:          
                    logger.error("self.csrf_token:%s,self.cookies  : %s" % (self.csrf_token, self.cookies))  
                    return None
                logger.debug("response [%s] " % response.text)            
                return response.text
            else:
                logger.error("self.csrf_token:%s,self.cookies  : %s" % (self.csrf_token, self.cookies))  
                return None
        except Exception, e:
            logger.error("[%s]" % e)
            return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_GETSTATUS_ICA_ERROR)    
    def resources_get_icon(self,uri):
        try:
            url = self.build_request_headers(uri)
            self.headers["Accept"] = "image/webp,*/*"
            self.headers["Cookie"] = self.cookies
            response = requests.get(url, headers = self.headers,stream=True,verify=False,timeout=10)
            if response.status_code != 200 and response.status_code != 304:
                logger.error("self.csrf_token:%s,self.cookies  : %s" % (self.csrf_token, self.cookies))  
                return None
            
            basestring=None
            basestring=base64.b64encode(response.content) 
            return basestring
        except Exception, e:
            logger.error("[%s]" % e)
            return Error(ErrorCodes.STOREFRONT_GET_STATUS_ICA_ERROR, 
                         ErrorMsg.ERR_MSG_STOREFRONT_GETSTATUS_ICA_ERROR)  		
    # /Resources/LanchIca
    def assign_desktop_url(self,uri):
        try:
            url = self.build_request_headers(uri)
            self.headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
            self.headers["Content-Type"] = "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"
            self.headers["Csrf-Token"] = self.csrf_token                                        
            self.headers["Cookie"] = self.cookies    
            response = requests.post(url, headers = self.headers,verify=False,timeout=10)
            if response.status_code != 200:
                logger.error("self.csrf_token:%s,self.cookies : %s" % (self.csrf_token,self.cookies))  
                return None
            logger.debug("response [%s] " % response.text)
            rsassign = self.byteify(json.loads(response.text))
            if rsassign is None :
                logger.error("self.csrf_token:%s,self.cookies : %s" % (self.csrf_token,self.cookies))  
                return None
            if "hostName" not in rsassign or "status" not in rsassign or rsassign["status"] != "success":
                logger.error("[%s] is not success" % response.text)
                return None
            return rsassign["hostName"]
        except Exception, e:
            logger.error("[%s]" % e)
            return None
           
    def ns_storefront_login(self,user_name,password): 
        
        if self.netscaler_login(user_name, password) is None:
            return None
        if self.home_configuration()<0:
            return None       
        ret=self.get_auth_methods()
        if isinstance(ret, Error):
            return None
        ret=self.gatewayAuth_login()
        if isinstance(ret, Error):
            return None

        return ret       

    
    def netscaler_login(self, username, password):
        try:           
            if "://" in self.zsf.base_url:
                base_index1 = self.zsf.base_url.index("://")
                _uri = self.zsf.base_url[base_index1+3:] 
            if "/" in _uri:
                base_index = _uri.index("/")
            else:
                base_index = len(_uri) - 1
    
            uritmp = "https://"+_uri[0:base_index]
    
            uri="/cgi/login"
            self.build_request_headers(uri )
            self.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
            self.headers["Referer"] = uritmp + "/vpn/index.html"
            url=uritmp+uri
            logindata= {}
            logindata['login'] = username
            logindata['passwd'] = password
            response = requests.post(url, data=logindata,headers=self.headers, verify=False,timeout=10)             
            if response.status_code!=200:
                logger.error("netscaler_login failed")
                return None
            cookies = requests.utils.dict_from_cookiejar(response.cookies)
            self.cookies=self.get_cookie_string(cookies)
            logger.debug("cookies [%s] " % self.cookies)
            if  self.cookies.find("NSC_AAAC")<0:
                return None
            self.naac=self.cookies
            return 0
        except Exception, e:
            logger.error("[%s]" % e)
            return None

    def gatewayAuth_login(self):
        try:         
            url = self.build_request_headers(uri="/GatewayAuth/Login")
            self.headers["Cookie"] = self.cookies
            self.headers["Csrf-Token"] = self.csrf_token
            response = requests.post(url, headers=self.headers,verify=False,timeout=10)    
            if response.status_code!=200 or response.reason!="OK" or response.text.find("success")<0 or response.text.find("CitrixAGBasic")<0:
                logger.error("store netscaler gatewayAuth_login error" )
                return Error(ErrorCodes.STOREFRONT_INTERNAL_ERROR, 
                             ErrorMsg.ERR_MSG_STOREFRONT_LOGIN_GATEWAYAUTH_ERROR)     
                       
            cookies = requests.utils.dict_from_cookiejar(response.cookies)
            cookie_strtmp = self.get_cookie_string(cookies) 
            cookie_strtmp+=";"+self.cookies
            cookie_str=cookie_strtmp.replace(';','@')  
            logger.debug("cookie_str [%s] " % cookie_str)                          
            return cookie_str 
        except Exception, e:
            logger.error("[%s]" % e)
            return Error(ErrorCodes.STOREFRONT_INTERNAL_ERROR, 
                             ErrorMsg.ERR_MSG_STOREFRONT_LOGIN_GATEWAYAUTH_ERROR)    
