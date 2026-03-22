'''
Created on 2012-5-6

@author: yunify
'''

import base64
import copy
import datetime
import fcntl
import hashlib
import logging
import os
import random
import math
import re
import shutil
import signal
import stat
import sys
import thread
import threading
import time
import traceback
import crypt
from contextlib import contextmanager
from functools import wraps
from itertools import islice, chain
from contextlib import nested
from M2Crypto.EVP import Cipher as CP

from log.logger import logger
from utils import subprocess_tool as subprocess
from utils.thread_local import get_msg_id, set_flock_name, clear_flock_name

HOME = '/pitrix/'
def get_month_extreme(year, month, is_ts=False):
    _year = to_int(year)
    _month = to_int(month)
    if not _year or not _month:
        raise Exception("invalid year [%s] or month [%s]", year, month)
    else:
        year = _year
        month = _month
    
    head = "%d-%d-1 0:0:0" % (year, month)
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    tail = "%d-%d-1 0:0:0" % (year, month)
    
    head_ts = parse_timestamp(head)
    tail_ts = parse_timestamp(tail)
    if is_ts:
        return (head_ts, tail_ts)
    head_dt = format_timestamp(head_ts)
    tail_dt = format_timestamp(tail_ts)
    return (head_dt, tail_dt)

def get_current_month_extreme(is_ts=True):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    return get_month_extreme(year, month, is_ts)

def get_current_time(to_seconds=True):
    ''' get current datetime '''
    now = datetime.datetime.now()
    if to_seconds:
        return now.replace(microsecond=0)
    return now

def get_current_date():
    ''' year month day hour min second, format is string of pure digital '''
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def parse_time(ts):
    ''' from format string to datetime '''
    return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

def format_time(dt):
    ''' from datetime to format string '''
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_current_timestamp():
    '''' get current timestamp '''
    return int(time.time())

def format_timestamp(ts):
    ''' from timestamp to format string '''
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

def redefine_format_timestamp(ts):
    ''' from timestamp to format string '''
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(ts))

def parse_timestamp(ts, fm="%Y-%m-%d %H:%M:%S"):
    ''' parse format string to timestamp '''
    try:
        ts_s = time.strptime(ts, fm)
        return int(time.mktime(ts_s))
    except ValueError, e:
        logger.warn("parse timestamp [%s] failed: %s" % (ts, e))
        return None
    
def time_to_utc(notice_time):
    
    ltime=time.localtime(notice_time)
    timeStr=time.strftime("%Y-%m-%d %H:%M:%S", ltime)
    return timeStr
    
def get_all_processes(pid, pid_list):
    ''' get pid and its child processes '''
    
    if pid <= 1:
        return
    
    cmd = "ps -o pid --ppid %d --noheaders" % pid
    p = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE)
    try:
        (output, _) = p.communicate(timeout=5)
        if output != None and len(output) > 0:
            for pid_str in output.split("\n")[:-1]:
                get_all_processes(int(pid_str), pid_list)
    except Exception, e:
        logger.warn("get child processes of [%d] failed: %s" % (pid, e))
        pass
    pid_list.append(pid)
    
    try:
        p.wait(timeout=5)
    except:
        pass

def kill_all_processes(pid, child_only=False, pid_list=None):
    ''' kill pid and its child processes '''
    
    if pid_list is None:
        pid_list = []
    
    if pid <= 1:
        return

    logger.debug("killing all processes of [%d]" % pid)
    cmd = "ps -o pid --ppid %d --noheaders" % pid
    p = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE)
    try:
        (output, _) = p.communicate(timeout=5)
        if output != None and len(output) > 0:
            for pid_str in output.split("\n")[:-1]:
                kill_all_processes(int(pid_str), pid_list=pid_list)
    except Exception, e:
        logger.warn("get child processes of [%d] failed: %s" % (pid, e))
        pass
    
    pid_list.append(pid)
    if not child_only:
        try:
            os.kill(pid, signal.SIGKILL)
        except:
            pass
        logger.debug("killed process [%d]" % pid)
        
    try:
        p.wait(timeout=5)
    except:
        pass
        
g_program_pid = -1
def set_program_pid():
    global g_program_pid
    g_program_pid = os.getpid()
    
def get_program_pid():
    global g_program_pid
    return g_program_pid
    
g_exit_program_hook = None
def set_exit_program_hook(hook):
    global g_exit_program_hook
    g_exit_program_hook = hook
    
def exit_program(status=-1):
    ''' exit program cleanly 
        must call set_program_pid when program starts
    '''
    global g_program_pid, g_exit_program_hook
    
    # call hook first to clean service-specific resources
    if g_exit_program_hook:
        g_exit_program_hook()   
    kill_all_processes(g_program_pid, child_only=True)
    
    # this is to prevent program exists too quickly that supervisor will mark it as FATAL
    time.sleep(3)
    os._exit(status)
    
def dump_program_stacks(signal, frame):
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId, ""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    logger.info("\n".join(code))
    
def dump_program_objects(signal, frame):
    timestr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    stat_file = '/tmp/dump.%s.stat' % timestr

    # force collect
    import gc

    # dump object stat info
    # this info can be analyzed by comp_stat.py tool to get an object growth info
    gc.collect()
    logger.info("dumping object stat info to [%s]..." % stat_file)    
    try:
        from utils.json import json_dump
        from collections import defaultdict
        
        stat_info = defaultdict(int)
        for i in gc.get_objects():stat_info[str(type(i))] += 1
        
        with open(stat_file, 'w') as fp:
            fp.write(json_dump(stat_info))
            
        del stat_info
    except Exception, e:
        logger.error("dump object stat info failed: %s" % e)

    return

def exec_cmd_timeout(proc, expect_pids=None):
    # MUST kill all child processes, otherwise children will become zombies
    killed_pids = []
    kill_all_processes(proc.pid, pid_list=killed_pids)
    
    if expect_pids:
        try:
            # double kill, in case the parent pid exits too early
            for pid in expect_pids:
                if pid not in killed_pids:
                    logger.debug("killing missed process [%d]" % pid)
                    kill_all_processes(pid)
                
            proc.wait(5)
        except Exception, e:
            logger.warn("wait for child processes of [%d] to terminate failed: %s" % (proc.pid, e))
            pass
    
def _decode_str(s):
    try:
        return s.decode('utf-8')
    except Exception:
        pass
        
    try:
        return s.decode('gbk')
    except Exception:
        pass
    
    return s.decode('utf-8', "replace")

popen_lock = threading.Lock()

def _exec_cmd(cmd, timeout=0, suppress_warning=False, remote_host=None, suppress_log=False, ssh_port=None,ignore_all_log=None):
    env = {}
    if os.environ.has_key('PYTHONPATH'):
        env['PYTHONPATH'] = os.environ['PYTHONPATH']
    # sometimes python PATH environ may miss /usr/local folder, here we hard code it
    env['PATH'] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    env['HOME'] = HOME
    if os.environ.has_key('LOGGER_NAME'):
        env['LOGGER_NAME'] = os.environ['LOGGER_NAME']
    if os.environ.has_key('LOGGER_DEBUG'):
        env['LOGGER_DEBUG'] = os.environ['LOGGER_DEBUG']
    if os.environ.has_key("MSG_ID"):
        env["MSG_ID"] = os.environ['MSG_ID']
    else:
        # in script environment, msg_id is spread through environ variable
        # so if there is no msg_id, get from thread local and pass it on
        msg_id = get_msg_id()
        if msg_id != "":
            env["MSG_ID"] = msg_id
    
    # remote exec    
    if remote_host:
        _port = ssh_port
        if _port is None:
            from utils.global_conf import get_ssh_port
            _port = get_ssh_port()

        from utils.net import get_hostname
        if remote_host != get_hostname():   
            cmd = "ssh -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' -o ConnectTimeout=2 -o ConnectionAttempts=1 \
-p %d root@%s \"%s\"" % (_port, remote_host, cmd.replace("$", "\$"))

    p = None
    stime = time.time()
    # expect_pids = []
    try:
        # http://bugs.python.org/issue12739
        # When multiple threads create child processes simultaneously and
        # redirect their stdout using subprocess.Popen, at least one thread
        # will stuck on reading the stdout after its child process exited,
        # until all other processes are also exited.
        p = None
        with popen_lock:
            p = subprocess.Popen(cmd, shell=True, env=env, executable="/bin/bash", close_fds=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        # here we have to get all processes before communicate time out
        # because in rare cases, the top process will exit before its children die
        # we need to remember them and kill them all when timeout  
        # get_all_processes(p.pid, expect_pids)
        
        (output, errput) = p.communicate(timeout=30 if not timeout else timeout)
    except:
        # timed out
        etime = time.time()
        if not suppress_log:
            if not suppress_warning:
                logger.warn("cmd [%s] time out. exec_time is [%.3f]s" % (cmd, etime - stime))
            else:
                logger.debug("cmd [%s] time out. exec_time is [%.3f]s" % (cmd, etime - stime))

        # timeout handling
        if p:
            exec_cmd_timeout(p)
            try:
                p.kill()
                p.wait(5)
            except:
                pass
            # exec_cmd_timeout(p, expect_pids)
        return None
        
    etime = time.time()
    ret_code = p.returncode
    output = _decode_str(output.strip()) if output else ""
    errput = _decode_str(errput.strip()) if errput else "" 
    exec_time = etime - stime
    if not suppress_log:
        if ret_code != 0:
            if not suppress_warning:
                logger.warn("cmd [%s] failed: ret[%d] out[%s] err[%s]. exec_time is [%.3f]s" % \
                            (cmd, ret_code, output, errput, exec_time))
    if not ignore_all_log:
        if ret_code != 0:
            if exec_time > 5:
                logger.info("[LONG_TIME_CMD] cmd [%s] failed: ret[%d] out[%s] err[%s]. exec_time is [%.3f]s" % \
                            (cmd, ret_code, output, errput, exec_time))
        else:
            if exec_time > 5:
                logger.info("[LONG_TIME_CMD] cmd [%s] ok: [%s]. exec_time is [%.3f]s" % (cmd, output, exec_time))
                
    try:
        p.wait(timeout=5)
    except:
        pass
    
    logger.debug("cmd [%s] done: ret[%d] out[%s] err[%s]. exec_time is [%.3f]s", cmd, ret_code, output, errput, exec_time)
    return (ret_code, output, errput)

LOCK_HOME = HOME + "/lock"

@contextmanager
def VirtLock():
    with FileLock("%s/virt.lock" % LOCK_HOME):
        try:
            yield
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
        
@contextmanager
def VirtMigrateLock():
    with FileLock("%s/live_migrate.lock" % LOCK_HOME):
        try:
            yield
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
            
@contextmanager
def VirtMigrateTryLock():
    with TryFileLock("%s/live_migrate.lock" % LOCK_HOME) as locked:
        try:
            yield locked
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())

@contextmanager
def IOLock():
    ''' this lock is to serialize all the heavy disk io write operations :
        1) create image
        2) create os disk
        3) migrate volume and image file
    '''
    with FileLock("%s/io.lock" % LOCK_HOME):
        try:
            yield
        except:
            logger.error("yield exits with exception: %s" % traceback.format_exc())
            
def get_libvirtd_pid():
    ret = exec_cmd("supervisorctl pid libvirtd")
    if ret == None or ret[1] == "":
        return None
    return ret[1]
        
def is_libvirtd_crashed():
    ''' check if libvirtd just crashed '''
    pid = get_libvirtd_pid()
    if not pid:
        return True
    
    stime = get_process_stime(pid) 
    if stime <= 0:
        return True
    
    if time.time() - stime < 30:
        return True
    
    return False

def is_virsh_corrupted(err):
    if "virsh: corrupted" in err:
        return True
    return False


def exec_cmd(cmd, timeout=0, suppress_warning=False, remote_host=None, suppress_log=False, virt_retry=True, ssh_port=None):
    # libvirtd has bugs when connected with many clients
    # need to serialize virsh commands to reduce conflicts
    if cmd.startswith("virsh "):
        # since libvirtd may crash, retry until libvirtd gets started again
        retries = 3
        while True:
            # don't serialize long-time virsh operations
            if  cmd.startswith("virsh qemu") or \
                cmd.startswith("virsh save") or \
                cmd.startswith("virsh restore") or \
                cmd.startswith("virsh block") or \
                cmd.startswith("virsh snapshot") or \
                cmd.startswith("virsh migrate"):
                ret = _exec_cmd(cmd, timeout=timeout, suppress_warning=suppress_warning, remote_host=remote_host, ssh_port=ssh_port)
            else:
                with VirtLock():
                    ret = _exec_cmd(cmd, timeout, suppress_warning, remote_host=remote_host, ssh_port=ssh_port)

            if ret != None and (ret[0] == 0 or (remote_host is None 
                                                and not is_libvirtd_crashed() 
                                                and not is_virsh_corrupted(ret[2]))):
                return ret   
                
            if not virt_retry:
                return ret
            
            # if libvirtd gets crashed, retry
            retries -= 1
            if retries == 0:
                return ret
            time.sleep(3)
            logger.info("libvirtd may get crashed, retry cmd [%s]: [No.%d]" % (cmd, retries))

    return _exec_cmd(
        cmd,
        timeout=timeout,
        suppress_warning=suppress_warning,
        remote_host=remote_host,
        suppress_log=suppress_log,
        ssh_port=ssh_port,
    )


def is_command_successful(ret, ignore_ret_code=False):
    if not ret:
        return False

    if ignore_ret_code:
        return True

    return ret[0] == 0


def is_command_failed(ret, ignore_ret_code=False):
    return not is_command_successful(ret, ignore_ret_code=ignore_ret_code)

TMP_HOME = '/tmp/'

def exec_cmd_batch(cmds, timeout=0, suppress_warning=False, suppress_log=False, debug=False):
    ''' execute batch commands, either run them in a single command line or in script file 
        @param cmds - an array of commands, ";" is NOT allowed in command line
        @param debug: output rc code for every cmd
    '''
    
    # if command is short, run directly in command line
    cmd_all = "" if not debug else "set -x;set -e;"
    cmd_all += ";".join(cmds)
    if len(cmd_all) < 128 * 1024:
        return exec_cmd(cmd_all, timeout=timeout, suppress_warning=suppress_warning, suppress_log=suppress_log)
    
    # command is too long, run in script file
    script = "%s/exec_cmd.%d" % (TMP_HOME, random.randint(1, 9999999))
    if os.path.exists(script):
        script = "%s/exec_cmd.%d" % (TMP_HOME, random.randint(1, 9999999))
        if os.path.exists(script):
            logger.error("generate script for cmd [%s] failed" % (cmd_all))
            return None
        
    result = None
    try:
        with open(script, "w") as f:
            f.write("#!/bin/bash\n\n")
            f.write(cmd_all.replace(";", "\n"))
            flush_file(f)
            
        result = exec_cmd("chmod +x %s; %s" % (script, script), timeout=timeout, suppress_warning=suppress_warning, suppress_log=suppress_log)
    except Exception, e:
        logger.error("write script [%s] error: %s", script, e)
        return None
    finally:
        remove_file(script)
    
    return result

def create_file(filename):
    ''' create a file '''
    return append_file(filename, '')

def remove_file(filename, remote_host=None, ssh_port=None, quiet=False):
    if remote_host == None:
        try:
            if os.path.exists(filename):
                os.unlink(filename)
                if not quiet:
                    logger.info("file [%s] exists and is removed" % filename)
        except:
            pass
    else:
        exec_cmd("rm -f %s" % filename, remote_host=remote_host, ssh_port=ssh_port)
        if not quiet:
            logger.info("file [%s] is removed on remote_host [%s]" % (filename, remote_host))
    return

def remove_dir(dirname):

    try:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
            logger.info("dir [%s] exists and is removed" % dirname)
    except:
        pass

def move_file(filename, directory):
    if os.path.exists(filename):
        exec_cmd("mv -f %s %s/" % (filename, directory))
        logger.info("file [%s] is moved to [%s]" % (filename, directory))
    return

def mark_todel(filename):
    try:
        if os.path.exists(filename):
            exec_cmd("mv -f %s %s.todel" % (filename, filename))
            logger.info("file [%s] exists and is removed" % filename)
    except:
        pass
    return

def read_file(file_name, mode='r'):
    ''' read file content '''
    try:
        with open(file_name, mode) as f:
            content = f.read()
    except Exception, e:
        logger.error("read file [%s] failed, [%s]" % (file_name, e))
        return None
    return content

def write_file(file_name, content):
    ''' write file '''
    try:
        with open(file_name, "w") as f:
            f.write("%s" % content)
    except Exception, e:
        logger.error("write file [%s] failed, [%s]" % (file_name, e))
        return False
    return True

def append_file(file_name, content):
    ''' append file '''
    try:
        with open(file_name, "a") as f:
            f.write("%s" % content)
    except Exception, e:
        logger.error("append file [%s] failed, [%s]" % (file_name, e))
        return False
    return True

def modify_conf_file(file_name, replacements):
    '''
    modify a file based on key value map. Append if not exists
    @param file_name: config file, eg: sysctl.conf
    @param replacements: {"foo": "bar"} to update in file
    '''
    content = read_file(file_name)
    with open(file_name, 'w') as outfile:

        new_keys = replacements.keys()

        for line in content.splitlines():

            if not line.strip() or line.strip()[0] == '#':
                outfile.write(line + "\n")
                continue

            try:
                key, val = line.split('=')
                key = key.strip()
                val = val.strip()

            except ValueError:
                outfile.write(line + "\n")
                continue

            try:
                val, comment = val.split('#')
                comment = '# ' + comment.strip()
                val = val.strip()

            except ValueError:
                comment = ''

            if key in replacements.keys():
                val = replacements[key]
                new_keys.remove(key)
                # put together the new line for the output file
                line = '%s=%s' % (key, val)
                if comment:
                    line += " %s" % comment

            outfile.write(line + "\n")

        for key in new_keys:
            outfile.write('%s=%s\n' % (key, replacements[key]))

        outfile.close()
        return 0

    return 1
   
g_flock_lock = threading.RLock()
g_flock_group = {}
@contextmanager
def FileLock(lock_file, timeout=0):
    ''' file lock, used to synchronize multi-process operations
    
    usage:
        with FileLock("my.lock"):
            do something within the lock protection
    
    '''
    global g_flock_lock, g_flock_group 
    lock_name = os.path.basename(lock_file)
    
    # endtime
    etime = time.time() + (timeout if timeout else 99999999999)

    #===========================================================================
    # # lock object handling, if remote calling sets lock object
    # # don't need to do flock to prevent dead lock
    # (name, host) = get_flock_obj()
    # if lock_name in name:
    #     from utils.net import get_hostname
    #     if host == get_hostname():
    #         # set back flock name for recursive usage
    #         for _name in name:
    #             set_flock_name(_name)
    #             
    #         try:
    #             yield
    #         except:
    #             logger.critical("yield exits with exception: %s" % traceback.format_exc())
    #         return
    #===========================================================================

    # get thread lock
    g_flock_lock.acquire()
    if lock_name not in g_flock_group:
        # lock_owner/lock object/reference count of lock applicants
        g_flock_group[lock_name] = [None, threading.Lock(), 0]
    lockv = g_flock_group[lock_name]
    lock_owner = lockv[0]
    
    # if it is recursive locking
    me = thread.get_ident()
    if lock_owner == me:
        g_flock_lock.release()
        try:
            yield
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
        return
    
    thr_lock = lockv[1]
    lockv[2] += 1  # record this thread is acquiring the lock
    g_flock_lock.release()
        
    # inter-thread lock
    thr_locked = False
    while time.time() < etime:
        if thr_lock.acquire(False):
            thr_locked = True
            break
        time.sleep(0.5)

    g_flock_lock.acquire()
    lockv[2] -= 1
    g_flock_lock.release()
    lockv[0] = me
    
    set_flock_name(lock_name)
    
    # inter-process lock
    with open(lock_file, "w") as fp:
        f_locked = False
        while time.time() < etime:
            try:
                fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  
            except:
                # locked by other process
                time.sleep(0.5)
                continue
            
            f_locked = True
            break

        try:
            yield
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())

        if f_locked:
            fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
        
    clear_flock_name(lock_name)
    
    # free it
    lockv[0] = None
    if thr_locked:
        thr_lock.release()
    
    # if we still can get lock, means it is not used by others, clean thread lock
    # lock file is clean by agent according to its mtime
    time.sleep(0.001)
    with TryFileLock(lock_file) as locked:
        if not locked:
            g_flock_lock.acquire()
            if lock_name in g_flock_group:
                lockv = g_flock_group[lock_name]
                # remove entry only if no other threads are acquiring the lock
                if lockv[2] == 0:
                    del g_flock_group[lock_name]
            g_flock_lock.release()
    
    return

def get_resource_lock(key):
    return "%s/%s.lock" % ('/pitrix/run', key)

@contextmanager
def rLock(key):
    ''' handle_resource lock '''
    if isinstance(key, list) or isinstance(key, set):
        if len(key) == 0:
            try:
                yield
            except:
                logger.critical("yield exits with exception: %s" % traceback.format_exc())
        else:
            mgrs = []
            for k in key:
                mgrs.append(FileLock(get_resource_lock(k)))
            
            with nested(*mgrs):
                try:
                    yield
                except:
                    logger.critical("yield operation exits with exception: %s" % traceback.format_exc())
    else:
        with FileLock(get_resource_lock(key)):
            try:
                yield
            except:
                logger.critical("yield operation exits with exception: %s" % traceback.format_exc())

@contextmanager
def TryFileLock(lock_file):
    ''' try file lock 
    @return True if already locked or False is not locked
    '''
    
    global g_flock_lock, g_flock_group 
    lock_name = os.path.basename(lock_file)
    
    # get thread lock
    g_flock_lock.acquire()
    if lock_name not in g_flock_group:
        # lock_owner/lock object/reference count
        g_flock_group[lock_name] = [None, threading.Lock(), 0]
    lockv = g_flock_group[lock_name]
    lock_owner = lockv[0]
    
    # if it is recursive locking
    me = thread.get_ident()
    if lock_owner == me:
        g_flock_lock.release()
        try:
            yield True
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
        return
    
    thr_lock = lockv[1]
    lockv[2] += 1  # record this thread is acquiring the lock
    g_flock_lock.release()

    # inter-thread lock
    if not thr_lock.acquire(False):
        g_flock_lock.acquire()
        lockv[2] -= 1
        g_flock_lock.release()
        try:
            yield True
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
        return
    g_flock_lock.acquire()
    lockv[2] -= 1
    g_flock_lock.release()
    lockv[0] = me
                         
    with open(lock_file, "w") as fp:
        try:
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  
        except:
            # locked by other process
            try:
                yield True
            except:
                logger.critical("yield exits with exception: %s" % traceback.format_exc())
            lockv[0] = None
            thr_lock.release()
            return
        
        try:
            yield False
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
        fcntl.flock(fp.fileno(), fcntl.LOCK_UN) 
        
    # free it
    lockv[0] = None
    thr_lock.release()
    return

def to_int(s, default=0):
    try:
        return int(float(s))
    except:
        return default

def to_float(s, default=0, precision=2):
    try:
        v = float(s)
        
        if precision == 0:
            return int(v)
        
        if precision == 1:
            return float("%0.1f" % v)
        
        if precision == 2:
            return float("%0.2f" % v)
        
        if precision == 3:
            return float("%0.3f" % v)
        
        return v
    except:
        return default

def explode_array(list_str, separator=",", is_integer=False):
    ''' explode list string into array '''
    result = []
    item_list = list_str.split(separator)
    for item in item_list:
        item = item.strip()
        if item != "":
            if is_integer:
                result.append(to_int(item))
            else:
                result.append(item)
    return result

def explode_dict(dict_str, separator=","):
    ''' explode dict string into dict '''
    result = {}
    item_list = dict_str.split(separator)
    for item in item_list:
        item = item.strip()
        if item != "":
            parts = item.split("=")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                if key != "":
                    result[key] = val
    return result

def print_dict(title, dict_obj, level=logging.DEBUG):
    if not isinstance(dict_obj, dict):
        return
    if logger.isEnabledFor(level):
        format_str = title + ":"
        keys = sorted(dict_obj.keys())
        for key in keys:
            format_str += "\n\t* %s: [%s]" % (key, str(dict_obj[key]))
        format_str += "\n"
        logger.log(level, format_str)

def translate_size(size, unit=None):
    '''
    @param size: string of size, eg: 10G
    @return int value of size in unit
    '''

    # if size is a int, return it directly
    value = to_int(size, default=None)

    if value is not None:
        return to_size(value, unit=unit)

    if size[-1] == "K":
        value = int(float(size[:-1])) * 1024
    if size[-1] == "M":
        value = int(float(size[:-1])) * 1024 * 1024
    if size[-1] == "G":
        value = int(float(size[:-1])) * 1024 * 1024 * 1024
    if size[-1] == "T":
        value = int(float(size[:-1])) * 1024 * 1024 * 1024 * 1024

    if value == None:
        return None

    return to_size(value, unit=unit)

def to_size(size, unit=None):
    if unit == "M":
        bsize = size
        size = int(bsize / (1024 * 1024))
        if (size * (1024 * 1024)) != bsize:
            size += 1
    if unit == "G":
        bsize = size
        size = int(bsize / (1024 * 1024 * 1024))
        if (size * (1024 * 1024 * 1024)) != bsize:
            size += 1
    return size

def get_file_mtime(filename, host=None, ssh_port=None):
    try:
        if host is None:
            if os.path.exists(filename):
                return int(os.path.getmtime(filename))
            return None
        
        ret = exec_cmd("stat -c %%Y %s" % filename, remote_host=host, suppress_warning=True, ssh_port=ssh_port)
        if ret == None or ret[0] != 0 or ret[1] == "":
            logger.debug("get mtime of [%s] failed" % filename)
            return None
        return int(ret[1])
    except:
        return None
    
def update_file_mtime(filename, mtime=None):
    ''' update file mtime
        if mtime is None, update to the current time
    '''
    try:
        mtime = mtime if mtime is not None else get_current_timestamp()
        st = os.stat(filename)
        atime = st[stat.ST_ATIME]
        os.utime(filename, (atime, mtime))
        return True
    except:
        logger.error("update file [%s] mtime failed" % filename)
        return False
        
def flush_file(fd):
    # make sure it is written to disk
    if fd:
        fd.flush()
        os.fsync(fd.fileno())  

def get_process_stime(pid):
    ret = exec_cmd("cat /proc/%s/stat | cut -d' ' -f22" % pid)
    if ret == None or ret[1] == "":
        return -1
    JIFFIES = ret[1]
    
    ret = exec_cmd("grep btime /proc/stat | cut -d' ' -f2")
    if ret == None or ret[1] == "":
        return -1
    UPTIME = ret[1]
    
    return int(UPTIME) + (int(JIFFIES) / 100)

        
def get_utf8_value(value):
    if not isinstance(value, str) and not isinstance(value, unicode):
        value = str(value)
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value
    
def decode_utf8(value):
    if isinstance(value, unicode):
        return value

    try:
        return value.decode('utf-8', "replace")
    except Exception, e:
        logger.error("decode utf8 failed, %s" % e)
    return ""

def initialization_calls():
    ''' calls before initialize the threads '''
    # strptime is not thread safe, should be called before initialize the threads
    time.strptime("2012-04-01T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
    datetime.datetime.strptime("2012-04-01T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
    os.chdir("/pitrix/lib")
    return

def initialize_program():
    ''' calls before initialize the program '''
    initialization_calls()
    
    # set pid
    set_program_pid()
    
    # initialize global conf updater
    from utils.global_conf import get_updater
    get_updater()
    return

def drop_page_cache(host=None):
    ''' drop page caches'''
    if not host:
        exec_cmd("sync; echo 1 > /proc/sys/vm/drop_caches")
        return 
    exec_cmd("sync; echo 1 > /proc/sys/vm/drop_caches", remote_host=host)
    return

def atoi(s, default=0):
    if not s:
        return default
    
    result = default
    try:
        result = int(s)
    except:
        return default
    
    return result

def is_link(lnk_file, host=None):
    try:
        if host is None:
            return os.path.islink(lnk_file)
        ret = exec_cmd("stat -c %%F %s" % lnk_file, remote_host=host)
        if ret != None and ret[1] == "symbolic link":
            return True
    except:
        return False
    
def set_link(lnk_file, tgt_file):
    if os.path.lexists(lnk_file):
        os.unlink(lnk_file)
    os.symlink(tgt_file, lnk_file)
    return

def get_link(lnk_file):
    if os.path.islink(lnk_file):
        return os.readlink(lnk_file)
    
def get_split_files(home, prefix):
    files = []
    for f in os.listdir(home):
        matched = re.match(r'%s\d{4}' % prefix, f, re.M)
        if matched:
            files.append(f)
    return sorted(files)
                   
def is_dir_empty(path, excludes=None):
    if not os.path.isdir(path):
        return True
    
    files = os.listdir(path)
    if excludes:
        for _ex in excludes:
            if _ex in files:
                files.remove(_ex)
                
    return files == []

def _ECP(data, key, iv=None):
    ''' encrypt a string 
    
    @param key - secret key, 32 bytes len random string
    @param iv - initial vector, 16 bytes len ransom string
    @param data - the target string
    @return encrypted string in base64
    '''
    if iv is None:
        iv = '\0' * 16
    
    try:
        cipher = CP(''.join(["a", "e", "s", "_", "1", "2", "8", "_", "c", "b", "c"]), key, iv, 1,
                    key_as_bytes=1, d=''.join(["s", "h", "a", "1"]), salt=''.join(["9", "8", "3", "7", "4", "8", "7", "2"]))
        v = cipher.update(data)
        v = v + cipher.final()
        del cipher
    except Exception, e:
        logger.exception("_ECP failed: %s" % e)
        return None
    return v

def _DCP(data, key, iv=None):
    ''' decrypt a string 
    
    @param key - secret key, 32 bytes len random string
    @param iv - initial vector, 16 bytes len ransom string
    @param data - the encrypted string by encrypt_string()
    @return decrypted string
    '''
    if iv is None:
        iv = '\0' * 16
        
    try:
        cipher = CP(''.join(["a", "e", "s", "_", "1", "2", "8", "_", "c", "b", "c"]), key, iv, 0,
                    key_as_bytes=1, d=''.join(["s", "h", "a", "1"]), salt=''.join(["9", "8", "3", "7", "4", "8", "7", "2"]))
        v = cipher.update(data)
        v = v + cipher.final()
        del cipher
    except Exception, e:
        logger.exception("_DCP failed: %s" % e)
        try:
            logger.debug("decrypted string [%s]", encode_string(data))
        except:
            pass
        return None
    return v
       
_MK = ''.join(["T", "M", "0", "N", "A", "j", "y", "B", "C", "K",
                    "4", "t", "b", "c", "I", "L", "e", "u", "5", "t",
                    "i", "0", "l", "Q", "A", "i", "t", "C", "w", "3",
                    "F", "t", "b", "J", "8", "Y", "9", "K", "Y", "l",
                    "R", "M", "a", "E", "x", "T", "o", "p", "q", "8",
                    "y", "d", "o", "2", "x", "h", "B", "4", "K", "s",
                    "Q", "0", "R", "q", "e", "F", "7", "W", "Q", "R",
                    "l", "C", "t", "v", "o", "v", "S", "D", "V", "F",
                    "3", "h", "X", "p", "s", "W", "R", "s", "l", "v",
                    "P", "a", "/", "l", "V", "X", "X", "l", "D", "G",
                    "u", "9", "n", "9", "S", "W", "J", "S", "0", "h",
                    "O", "I", "+", "/", "+", "v", "w", "2", "T", "Z",
                    "2", "W", "1", "8", "R", "b", "T", "S"][17:59])

_MI = ''.join(["K", "1", "H", "4", "9", "p", "4", "/", "9", "1",
                    "m", "o", "0", "N", "0", "=", "c", "e", "3", "k",
                    "o", "o", "g", "3", "c", "s", "u", "W", "Z", "9",
                    "B", "3", "V", "R", "o", "b", "1", "+", "6", "o",
                    "1", "m", "r", "5", "g", "b", "O", "f", "u", "1",
                    "W", "7", "t", "H", "A", "z", "w", "o", "H", "P",
                    "d", "X", "7", "Y", "U", "o", "L", "7", "M", "M",
                    "S", "S", "P", "8", "f", "Z", "w", "2", "u", "G"][31:47])

def M_ECP(msg, to_crypt=True):
    global _K, _I
    if to_crypt:
        m = _ECP(msg, _MK, _MI)
        if m == None:
            return "\0"
        return "\0" + m
    return msg

def M_DCP(msg):
    global _K, _I
    if len(msg) > 1 and msg[0] == "\0":
        return (True, _DCP(msg[1:], _MK, _MI))
    return (False, msg)   

def is_str(value):
    ''' check if value is a string '''
    if (not isinstance(value, str)) and (not isinstance(value, unicode)):
        return False
    return True

def is_integer(value):
    ''' check if value is integer '''
    try:
        _ = int(value)
    except:
        return False
    return True

def is_float(value):
    ''' check if value is float '''
    try:
        _ = float(value)
    except:
        return False
    return True

def get_byte_len(value):
    ''' get string byte length '''
    try:
        if isinstance(value, str):
            return len(value)
        elif isinstance(value, unicode):
            return len(value.encode('utf-8'))
        else:
            return 0
    except:
        return 0

# do not change it!
_ESK = ''.join(["T", "M", "0", "N", "A", "j", "y", "B", "C", "K",
                "4", "t", "b", "c", "I", "L", "N", "u", "5", "t",
                "B", "0", "l", "Z", "A", "i", "t", "M", "w", "3",
                "F", "t", "b", "J", "8", "Y", "9", "K", "Y", "l",
                "R", "M", "d", "V", "x", "T", "o", "p", "q", "8",
                "y", "t", "o", "0", "x", "h", "A", "4", "K", "s",
                "Q", "0", "R", "C", "e", "F", "7", "W", "Q", "R",
                "l", "y", "t", "v", "o", "v", "S", "D", "V", "F",
                "3", "h", "X", "p", "s", "W", "R", "s", "l", "v",
                "8", "k", "a", "l", "V", "X", "X", "l", "D", "G",
                "u", "9", "w", "9", "S", "R", "J", "S", "0", "h",
                "O", "I", "+", "/", "+", "v", "w", "2", "T", "Z",
                "2", "W", "1", "E", "R", "b", "T", "S"][15:57])

def encode_string(s):
    ''' encode a string'''
    return base64.b64encode(_ECP(s, _ESK))

def decode_string(s):
    ''' decode a string '''
    return  _DCP(base64.b64decode(s), _ESK)

def multi_key_sort(items, keys):
    ''' sort items by multiple keys
        example: items = [{'a':5, 'b':5, 'c':1}, {'a':3, 'b':5, 'c':4}, {'a':5, 'b':6, 'c':7}]
                 the result of multi_key_sort(items, ["-a", "b", "c"]) will be:
                 [{'a': 5, 'c': 1, 'b': 5}, {'a': 5, 'c': 7, 'b': 6}, {'a': 3, 'c': 4, 'b': 5}]
    '''
    from operator import itemgetter
    comparers = [ ((itemgetter(k[1:].strip()), -1) if k.startswith('-') else (itemgetter(k.strip()), 1)) for k in keys] 
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        return 0
    return sorted(items, cmp=comparer)

PARAMS_TO_FORMAT = ["passwd", "newpasswd", "oldpasswd", "new_passwd", "old_passwd", "attachment_content", "private_key", "certificate_content",
                    "icp_password", "data", "substances", "register_info", "error_msg", "transition_substance", "user_config", "package_content"]

def format_params(req):
    ''' format request output'''
    if not isinstance(req, dict):
        return None
    
    new_req = copy.deepcopy(req)
    for k, v in new_req.items():
        if isinstance(v, dict):
            for key in v:
                if key in PARAMS_TO_FORMAT:
                    v[key] = "*"
        elif is_str(v):
            if k in PARAMS_TO_FORMAT:
                new_req[k] = "*"
    return new_req

def format_params_ex(req):
    ''' format request output extent '''
    new_req = format_params(req)
    if not new_req:
        return new_req
    for k in new_req:
        if k in PARAMS_TO_FORMAT:
            new_req[k] = "*"
    return new_req

def fuzzy_phone_number(phone_number):
    ''' convert 13800138000 to 138****8000'''
    m = re.match(r'(\d{3})(\d{4})(\d{4})', str(phone_number), re.M)
    if m:
        phone_number = '%s****%s' % (m.group(1), m.group(3))
    return phone_number

def get_md5sum(s):
    ''' get md5sum of a string '''
    return hashlib.md5(s).hexdigest()

def get_columns(d, cols):
    columns = dict([k for k in d.items() if k[0] in cols])
    return columns

def get_keys_by_value(d, v):
    ks = list([k for k in d if d[k] is v])
    return ks

def encode_base64(content):
    try:
        base64str = base64.standard_b64encode(content)
        return base64str
    except Exception, e:
        logger.error('encode base64string error: [%s]' % e)
        return ''

def decode_base64(base64str):
    try:
        decodestr = base64.standard_b64decode(base64str)
        return decodestr
    except Exception, e:
        logger.error('decode base64string error: [%s]' % e)
        return ''

def safe_to_unicode(s):
    try:
        uni_str = s.decode('utf-8')
        return uni_str
    except Exception, e:
        try:
            uni_str = s.decode('gbk')
            return uni_str
        except Exception, e:
            logger.error('safe_to_unicode error: [%s]' % (e))
            return ''


def get_unicode(msg):
    if isinstance(msg, unicode):
        return msg

    import chardet
    _m = None
    try:
        r = chardet.detect(msg)
        _m = msg.decode(r["encoding"])
    except:
        pass

    # Still not unicode
    if not isinstance(_m, unicode):
        return None

    return _m


def strip_xss_chars(s):
    ''' strip xss related chars '''
    return s.strip().replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&#34;").replace("'", "&#39;")

def is_resource_in_white_list(resource_id):
    wl_file = "/pitrix/conf/alert_agent.wl"
    if not os.path.exists(wl_file):
        return False
    ret = exec_cmd("grep %s %s" % (resource_id, wl_file))
    if ret != None and ret[0] == 0:
        return True
    return False

def is_valid_regex(pattern):
    try:
        re.compile(pattern)
    except re.error:
        return False
    return True

def do_async(func, *args, **kargs):
    from threading import Timer
    Timer(1, func, args, kargs).start()
    return
    
# Retry decorator
def retry(tries, delay=3, timeout=60, validator=None):
    '''Retries a function or method until it returns 0,
    usage: 1. retries calling foo(a, b, c)
            retry(3, delay=1, timeout=2)(foo)(a,b,c)

           2. as function decorator to retry time
               @retry(3, delay=1, timeout=2)
               def foo(a, b, c):
                  ...
               when foo(a,b,c) is called, it will be retried
    
    @param tries: max retry times
    @param delay: sleep between retries
    @param timeout: max time retry
    @param validator: function to verify if need to retry
    @return the last output value of the function 
    '''

    if tries < 1:
        raise ValueError("tries must be 1 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")
    
    if validator and not hasattr(validator, '__call__'):
        raise ValueError("validator must be a function")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            tried = 0
            rv = -1
            starttime = time.time()
            while True:
                if tried >= tries:
                    logger.warn("max retry [%d] reached in executing [%s]" % (tries, f.__name__))
                    break
                if time.time() > starttime + timeout:
                    logger.warn("timeout [%d] reached in executing [%s]" % (timeout, f.__name__))
                    break
                try:
                    rv = f(*args, **kwargs)
                    if validator and validator(rv):
                        return rv
                    elif not isinstance(rv, bool) and rv == 0:  # Done on success
                        return 0
                    else:
                        logger.debug("function [%s] returned [%s]" % (f.__name__, rv))
                except Exception, e:
                    logger.exception("hit [%s] in executing [%s]" % (e, f.__name__))

                tried += 1
                time.sleep(delay)
            return rv

        return f_retry
    return deco_retry

def is_list_dict(list_dict):
    ''' the items in list should be dict '''
    if not list_dict:
        return False
    
    if not isinstance(list_dict, list):
        return False
    
    for d in list_dict:
        if not isinstance(d, dict):
            return False
    return True

def get_max_len(items):
    ''' the items should be list '''
    if not items:
        return 0
    
    try:
        if not isinstance(items, (list, tuple)):
            return len(items)
    except:
        return 0
    
    try:
        max_len = len(items[0])
    except:
        max_len = 0
    for i in items[1:]:
        try:
            cur_len = len(i)
        except:
            cur_len = 0
        if cur_len > max_len:
            max_len = cur_len
    return max_len

def fill_str(item, length, val='0', position=0):
    '''
    @param item: the raw string
    @param length: the string length
    @param val: value of filling
    @param position: 0 for head, 1 for tail
    @example: item is '110', length is 5, result is '00110'
    '''
    new_item = item
    try:
        if len(item) >= length:
            raise Exception, ""
        val = "%s" % val
        position = to_int(position)
        if len(val) != 1:
            raise Exception, ""
        diff_len = length - len(item)
        val *= diff_len
        if position:
            new_item = "%s%s" % (item, val)
        else:
            new_item = "%s%s" % (val, item)
    except:
        return item
    return new_item

def binary_to_decimal(bin_str):
    try:
        return int(bin_str, 2)
    except:
        return 0

def decimal_to_binary(number, length=0):
    try:
        ret = bin(number).replace('0b', '')
        _len = length - len(ret)
        if _len > 0:
            ret = "%s%s" % ('0' * _len, ret)
    except:
        return ''
    return ret

def batch(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.next()], batchiter)

def to_utf8(s):
    if is_str(s):
        return s.encode('utf-8')
    return s

def get_lb_node_bandwidth(bandwidth, node_count):

    if node_count <= 0:
        return 0

    return bandwidth / float(node_count)

def log_slow(log, slow_time):
    """ Log slow execution.

    @log: log function, such as logger.warn or custom function
    @slow_time: threshold in seconds
    """
    def _(func):
        @wraps(func)
        def wrapper(*args, **kw):
            start_time = time.time()
            result = func(*args, **kw)
            exec_time = time.time() - start_time
            if exec_time > slow_time:
                log('slow execution: %r (%r, %r) %2.2f sec' % (func.__name__, args, kw, exec_time))
            return result
        return wrapper
    return _

def is_vm_mac(mac):

    return mac and mac.startswith("52:54:")


def is_valid_user_name(user_name):
    if re.match(r'^[A-Za-z0-9_\-\.]*$', user_name):
        return True
    return False

def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    if not s:
        return s
    for code in (
            ("'", '&#39;'),
            ('"', '&#34;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        ):
        s = s.replace(code[1], code[0])
    return s

def to_list(val):
    ''' return list '''
    return list(val) if isinstance(val, (list, tuple, set)) else [val]

def get_vol_id_from_lun_path(lun_path):

    ret = exec_cmd("virsh pool-list|grep 'pool_vol'|awk '{print $1}'")
    if not ret or ret[0] != 0:
        return None
    pools = ret[1].splitlines()
    for pool in pools:
        ret = exec_cmd("virsh vol-list %s --details|grep %s"
                       % (pool, lun_path), suppress_warning=True)
        if ret and ret[0] == 0:
            return pool[5:]

    return None

def get_free_port():
    import socket
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    addr = s.getsockname()
    port = to_int(addr[1])
    s.close()
    return port

def is_valid_path(pathname):

    if re.match(r'^/{1}(((/{1}\.{1})?[a-zA-Z0-9 ]+/?)+)$', pathname):
        return True
    return False

def get_file_md5sum(filepath, timeout=120, remote_host=None, ssh_port=None):
    ret = exec_cmd("md5sum {f}".format(f=filepath), timeout=timeout, remote_host=remote_host, ssh_port=ssh_port)

    if not ret:
        return None

    r, md5sum, _ = ret
    if r == 0:
        return md5sum.split()[0]

    return None


def is_file_existed(filepath, timeout=0, remote_host=None, ssh_port=None):
    ret = exec_cmd("ls {f}".format(f=filepath), timeout=timeout, remote_host=remote_host, suppress_warning=True, ssh_port=ssh_port)

    if not ret:
        return False

    r, _, _ = ret
    if r == 0:
        return True

    return False

def is_bit_set(value, bit):
    return value & (1 << bit) != 0

def set_bit(v, index, x):
    """ set the index:th bit of v to x, and return the new value. """
    mask = 1 << index
    v &= ~mask
    if x:
        v |= mask
    return v

def set_feature_bit(features, feature):
    return set_bit(features, int(math.log(feature, 2)), 1)

def unset_feature_bit(features, feature):
    return set_bit(features, int(math.log(feature, 2)), 0)

def is_dir(dirpath, remote_host=None):
    ''' dir if existent, true is existed '''
    if not remote_host:
        return os.path.isdir(dirpath)
    cmd = "[ -d '%s' ]" % (dirpath)
    ret = exec_cmd(cmd, remote_host=remote_host, suppress_log=True)
    if not ret:
        raise Exception("unknow stat: cmd [%s] in host [%s]"
                        % (cmd, remote_host))
    return 0 == ret[0]

def is_file(fullpath, remote_host=None):
    ''' file if existent, true is existed '''
    if not remote_host:
        return os.path.isfile(fullpath)
    cmd = "[ -f '%s' ]" % (fullpath)
    ret = exec_cmd(cmd, remote_host=remote_host, suppress_log=True)
    if not ret:
        raise Exception("unknow stat: cmd [%s] in host [%s]"
                        % (cmd, remote_host))
    return 0 == ret[0]

def touchpath(fullpath, remote_host=None):
    ''' check health of fullpath, raise exception if error '''
    try:
        # maybe hang
        if not exec_cmd("stat -c %%Y %s" % fullpath,
                        timeout=5,
                        remote_host=remote_host,
                        suppress_log=True):
            raise Exception("get stat failed")
    except Exception, e:
        raise Exception("path [%s] in host [%s] is not health: %s" 
                        % (fullpath, remote_host, e))
    
    return

def is_path_occupied(fullpath, remote_host=None):
    ''' lsof fullpath to check if it is occupied. '''
    # require raise exception if status is ambiguous
    if not is_file(fullpath, remote_host) and not is_dir(fullpath, remote_host):
        logger.info("fullpath [%s] not exists", fullpath)
        return False
    
    cmd = "lsof -nP '%s'" % fullpath
    ret = exec_cmd(cmd, remote_host=remote_host, suppress_log=True)
    if not ret:
        raise Exception("unkown stat: cmd [%s] in host [%s]" 
                        % (cmd, remote_host))
    return 0 == ret[0]

def mkpasswd(pwd):
    salt = ''.join(map(lambda x: './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'[ord(x) % 64], os.urandom(16)))
    _pwd = crypt.crypt(pwd, "$6$%s" % salt)

    return _pwd
def get_file_size(filename, host=None, unit=None, ssh_port=None):
    try:
        size = 0
        if host is None:
            size = os.path.getsize(filename)
        else:
            ret = exec_cmd("stat -c %%s %s" % filename, remote_host=host, ssh_port=ssh_port)
            if ret == None or ret[0] != 0 or ret[1] == "":
                logger.error("get size of [%s] failed" % filename)
                return None
            size = int(ret[1])
        return to_size(size, unit)
    except:
        return None

def filter_out_none(dictionary, keys=None):
    """ Filter out items whose value is None.
        If `keys` specified, only return non-None items with matched key.
    """
    ret = {}
    if keys is None:
        keys = []
    for key, value in dictionary.items():
        if value is None or (keys and key not in keys):
            continue
        ret[key] = value
    return ret


ISO8601 = '%Y-%m-%dT%H:%M:%SZ'
ISO8601_MS = '%Y-%m-%dT%H:%M:%S.%fZ'


def get_ts(ts=None):
    """ Get formatted time
    """
    if not ts:
        ts = time.gmtime()
    return time.strftime(ISO8601, ts)


def parse_ts(ts):
    """ Return as timestamp
    """
    ts = ts.strip()
    try:
        ts_s = time.strptime(ts, ISO8601)
        return time.mktime(ts_s)
    except ValueError:
        try:
            ts_s = time.strptime(ts, ISO8601_MS)
            return time.mktime(ts_s)
        except ValueError:
            return 0


def local_ts(utc_ts):
    ts = parse_ts(utc_ts)
    if ts:
        return ts - time.timezone
    else:
        return 0

def base64_url_decode(inp):
    if sys.version > "3":
        if isinstance(inp, bytes):
            inp = inp.decode()
        return base64.urlsafe_b64decode(inp + '=' * (4 - len(inp) % 4)).decode()
    else:
        return base64.urlsafe_b64decode(str(inp + '=' * (4 - len(inp) % 4)))


def base64_url_encode(inp):
    if sys.version > "3":
        if isinstance(inp, str):
            inp = inp.encode()
        return bytes.decode(base64.urlsafe_b64encode(inp).rstrip(b'='))
    else:
        return base64.urlsafe_b64encode(str(inp)).rstrip(b'=')


def wait_job(conn, job_id, timeout=60):
    """ waiting for job complete (success or fail) until timeout
    """
    def describe_job(job_id):
        ret = conn.describe_jobs([job_id])
        if not ret or not ret.get('job_set'):
            return None
        return ret['job_set'][0]

    deadline = time.time() + timeout
    while time.time() <= deadline:
        time.sleep(2)
        job = describe_job(job_id)
        if not job:
            continue
        if job['status'] not in ('pending', 'working'):
            if conn.debug:
                print('job is %s: %s' % (job['status'], job_id))
                sys.stdout.flush()
            return True

    if conn.debug:
        print('timeout for job: %s' % job_id)
        sys.stdout.flush()
    return False


