'''
Created on 2013-01-09

@author: yunify
'''

# ---------------------------------------------
#       Constants for Memcached key prefix
# ---------------------------------------------
MC_KEY_PREFIX_ROOT = "Pitrix"

# ---------------------------------------------
#       the key prefix for user login session key
# ---------------------------------------------
MC_KEY_PREFIX_SESSOIN_KEY = "%s.SessionKey" % MC_KEY_PREFIX_ROOT
MC_KEY_PREFIX_SESSOIN_KEY_LIST = "%s.SessionKeyList" % MC_KEY_PREFIX_ROOT

# ---------------------------------------------
#       the key prefix for service status
# ---------------------------------------------
MC_KEY_PREFIX_SERVER_STATUS = "%s.ServerStatus" % MC_KEY_PREFIX_ROOT

# ---------------------------------------------
#       the key prefix for guest monitor
# ---------------------------------------------
MC_KEY_PREFIX_PROCESS_MONITOR = "%s.ProcessMonitor" % MC_KEY_PREFIX_ROOT
MC_KEY_PREFIX_INSTALLED_PROTRAM = "%s.InstalledProgram" % MC_KEY_PREFIX_ROOT

# ---------------------------------------------
#       Expires time for Memcached key
# ---------------------------------------------
MC_EXPIRES_TIME = {
    MC_KEY_PREFIX_SESSOIN_KEY: 21600,
    MC_KEY_PREFIX_SESSOIN_KEY_LIST: 21600,
    MC_KEY_PREFIX_SERVER_STATUS: 21600,
    MC_KEY_PREFIX_PROCESS_MONITOR: 3600,
    MC_KEY_PREFIX_INSTALLED_PROTRAM: 3600,
}
