'''
Created on 2012-5-5

@author: yunify
'''

class Context():
    ''' thread dispatch_context '''
    def __init__(self):
        pass
        
g_ctx = Context()
def instance():
    ''' get dispatch_context '''
    global g_ctx
    return g_ctx
