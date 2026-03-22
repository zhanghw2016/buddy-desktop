'''
Created on 2012-5-5

@author: yunify
'''

from utils.global_conf import get_desktop_conf
from constants import DESKTOP_SERVER_ATTR
from utils.misc import explode_array

g_desktop_conf = None
g_desktop_attr = None

class DesktopContext():

    def __init__(self):
        # postgresql
        self.pg = None
        self.pgm = None
        # program pid
        self.pid = None
        # uuid check
        self.checker = None
        # memcache client
        self.mcclient = None
        self.mcm = None
        # third auth object
        self.auth = None
        
        # zone config
        self.zone_builder = None
        self.zone_checker = None
        self.zones = None
        self.zone_users = None
        self.zone_deploy = None
        self.zone_storefronts={}
        self.auth_radius = {}
        self.api_limits = {}
        # user
        self.admin_users = {}


        self.res = None
        self.system_custom_set = None
        self.module_type_set = None
        # license
        self.license = None

    def __getattr__(self, attr):
        # get conf short cut

        global g_desktop_conf
        global g_desktop_attr
        try:
            if attr in DESKTOP_SERVER_ATTR:
                if g_desktop_attr is None:
                
                    g_desktop_attr = get_desktop_conf()
                    if not g_desktop_attr:
                        return None
                    
                    cpu_range = g_desktop_attr.get("cpu_range")
                    if cpu_range:
                        g_desktop_attr["cpu_range"] = explode_array(cpu_range, is_integer=True)
                    
                    memory_range = g_desktop_attr.get("memory_range")
                    if memory_range:
                        g_desktop_attr["memory_range"] = explode_array(memory_range, is_integer=True)

                    express_instance_class = g_desktop_attr.get("express_instance_class")
                    if express_instance_class is not None:
                        g_desktop_attr["express_instance_class"] = explode_array(express_instance_class, is_integer=True)

                return g_desktop_attr.get(attr)

        except:
            pass
        
        return None

g_desktop_ctx = DesktopContext()
def instance():
    ''' get desktop server context '''
    global g_desktop_ctx
    return g_desktop_ctx
