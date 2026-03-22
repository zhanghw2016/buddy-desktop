'''
Created on 2012-12-26

@author: yunify
'''
import time
import os
from constants import (
    SPICE_CONNECT_FILE_DIR,
    STOREFRONT_CONNECT_FILE_DIR,
    CLEAN_DESKTOP_CONNECTION_FILE_RUN_TIME
)
from log.logger import logger

def clean_desktop_connection_file():
    cur_time = time.localtime()
    if cur_time.tm_hour != CLEAN_DESKTOP_CONNECTION_FILE_RUN_TIME:
        return None

    # clean spice connect files
    for dirpath, _, filenames in os.walk(SPICE_CONNECT_FILE_DIR):
        for file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            os.remove(file_path)

    # clean citrix store front conection files
    for dirpath, _, filenames in os.walk(STOREFRONT_CONNECT_FILE_DIR):
        for file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            os.remove(file_path)

    return None
