class Context():
    ''' thread context for the service '''
    def __init__(self):
        # postgresql
        self.pg = None
        self.pgm = None
        
        # program pid
        self.pid = None
        
        # config info
        self.conf = None

    def __getattr__(self, attr):
        # get conf short cut
        try:
            pass
        except:
            pass

        return None

g_ctx = Context()


def instance():
    ''' get context '''
    global g_ctx
    return g_ctx
