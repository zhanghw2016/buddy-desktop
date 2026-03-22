
class DesktopAgentContext():
    ''' thread context for vdi server 
    '''
    def __init__(self):
        # postgresql
        self.pg = None
        self.pgm = None
        
        # memcache client
        self.mcclient = None
        self.mcm = None

        # zone config
        self.zones = None
        self.zone_users = None
        self.zone_builder = None
        self.zone_checker = None
        self.zone_deploy = None
        self.res = None
        
    def __getattr__(self, attr):
        # get conf short cut
        try:
            pass
        
        except: 
            pass
        
        return None
        
g_agent_ctx = DesktopAgentContext()
def instance():

    global g_agent_ctx
    return g_agent_ctx
