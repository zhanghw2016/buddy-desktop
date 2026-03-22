'''
Created on 2012-5-5

@author: yunify
'''

from utils.global_conf import get_desktop_conf
from constants import DESKTOP_SERVER_ATTR
g_desktop_conf = None

class DispatchContext():
    ''' thread context for vdi server 
    '''
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

        # resources
        self.resources = None

        self.zone_builder = None
        self.zone_checker = None
        self.zones = None
        self.zone_users = None
        self.zone_deploy = None

        # server conf
        self.server_conf = {}
        
        # third auth object
        self.auth = None

    def __getattr__(self, attr):
        # get conf short cut
        global g_desktop_conf
        try:
                        
            if attr in DESKTOP_SERVER_ATTR:
                desktop_conf = get_desktop_conf()
                if not desktop_conf:
                    return None
                return desktop_conf.get(attr)

        except: 
            pass
        
        return None
        
g_dispatch_ctx = DispatchContext()
def instance():
    ''' get dispatch server context '''
    global g_dispatch_ctx
    return g_dispatch_ctx
