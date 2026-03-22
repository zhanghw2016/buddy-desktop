'''
Created on 2012-7-19

@author: yunify
'''

g_logger_name = None
def set_logger_name(logger_name):
    # set program logger name
    global g_logger_name
    g_logger_name = logger_name
    return

# get static logger name
def get_logger_name():
    global g_logger_name
    if not g_logger_name:
        return "run_script"
    return g_logger_name 


