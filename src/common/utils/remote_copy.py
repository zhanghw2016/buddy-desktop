'''
Created on 2012-11-9

@author: yunify
'''

import os
import time
from utils.misc import exec_cmd
from log.logger import logger
from utils.global_conf import get_ssh_port
from utils.misc import remove_file, get_file_size, get_link, is_link

FTP_ROOT = "/pitrix"

def rsync_from(source_host, source_file, target_file, timeout=60, sparse=False, compress=False, bwlimit=None, username="root", src_ssh_port=None, exclude=None):
    '''
        @note: this method is INVALID for raw sparse image copy, even sparse is TRUE
    '''

    # use arcfour to boot up speed
    _port = src_ssh_port
    if _port is None:
        _port = get_ssh_port()

    if bwlimit:
        opt = "-q --bwlimit=%s -e 'ssh -p %d -c arcfour' -a" % ((int(bwlimit) / 1024), _port)
    else:
        opt = "-q -e 'ssh -p %d -c arcfour' -a" % _port
    if sparse:
        opt += "S"
    if compress:
        opt += "z"
    if exclude:
        for ptn in exclude:
            opt += " --exclude '%s'" % ptn

    found = False
    retries = 3
    stime = time.time()
    while retries > 0:
        # check if the file exists on remote host
        source_file_size = get_file_size(source_file, host=source_host, ssh_port=src_ssh_port)
        if source_file_size == None:
            logger.error("get size of [%s] failed" % source_file)
            return -1

        # it may fail since target disk is not synced yet
        ret = exec_cmd(
            "rsync {option} {username}@{src_host}:{src_file} {dst_file}".format(
                option=opt,
                username=username,
                src_host=source_host,
                src_file=source_file,
                dst_file=target_file,
            ),
            timeout=timeout,
        )

        # check file size
        if ret is not None and ret[0] == 0:
            target_file_size = get_file_size(target_file)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("rsync_from size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))

        remove_file(target_file)
        time.sleep(3)
        retries -= 1

    if not found:
        logger.error("rsync [%s] from [%s] failed" % (source_file, source_host))
        return -1

    etime = time.time()
    logger.info("rsync [%s] from [%s:%s] OK : size[%s] time[%.3f]" % (target_file, source_host, source_file, source_file_size, etime - stime))
    return 0

def rsync_to(source_file, target_host, target_file, timeout=60, sparse=False, compress=False, bwlimit=None, username="root", dst_ssh_port=None, exclude=None):

    _port = dst_ssh_port
    if _port is None:
        _port = get_ssh_port()

    # use arcfour to boot up speed
    if bwlimit:
        opt = "-q --bwlimit=%s -e 'ssh -p %d -c arcfour' -a" % ((int(bwlimit) / 1024), _port)
    else:
        opt = "-q -e 'ssh -p %d -c arcfour' -a" % _port
    if sparse:
        opt += "S"
    if compress:
        opt += "z"
    if exclude:
        for ptn in exclude:
            opt += " --exclude '%s'" % ptn

    found = False
    retries = 3
    stime = time.time()
    while retries > 0:
        # check if the file exists on remote host
        source_file_size = -1
        if not os.path.isdir(source_file):
            source_file_size = get_file_size(source_file)

            if source_file_size == None:
                logger.error("get size of [%s] failed" % source_file)
                return -1

        # prepare target home
        exec_cmd(
            "mkdir -p {dst_dir} && chmod 755 {dst_dir}".format(
                dst_dir=os.path.dirname(target_file),
            ),
            remote_host=target_host,
            suppress_warning=True,
            ssh_port=dst_ssh_port,
        )

        # it may fail since target disk is not synced yet
        ret = exec_cmd(
            "rsync {option} {src_file} {username}@{dst_host}:{dst_file}".format(
                option=opt,
                src_file=source_file,
                username=username,
                dst_host=target_host,
                dst_file=target_file,
            ),
            timeout=timeout,
        )

        # check file size
        if ret is not None and ret[0] == 0:
            if os.path.isdir(source_file):
                found = True
                break

            target_file_size = get_file_size(target_file, host=target_host, ssh_port=dst_ssh_port)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("rsync_to size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))

        remove_file(target_file, remote_host=target_host, ssh_port=dst_ssh_port)
        time.sleep(3)
        retries -= 1

    if not found:
        logger.error("rsync [%s] to [%s] failed" % (source_file, target_host))
        return -1

    etime = time.time()
    logger.info("rsync [%s] to [%s:%s] OK : size[%s] time[%.3f]" % (source_file, target_host, target_file, source_file_size, etime - stime))
    return 0


def bbcp_to(source_file, target_host, target_file, timeout=60, bwlimit=None):
    '''
        @note: this method is INVALID for raw sparse image copy
    '''

    if bwlimit:
        opt = "-x %s -f -T 'ssh -p %s -x -a -oFallBackToRsh=no %%I -l %%U %%H /usr/bin/bbcp'" % (bwlimit, get_ssh_port())
    else:
        opt = "-f -T 'ssh -p %s -x -a -oFallBackToRsh=no %%I -l %%U %%H /usr/bin/bbcp'" % (get_ssh_port())
        
    if not os.path.exists(source_file):
        logger.error("bbcp [%s] to [%s] failed: not exists" % (source_file, target_host))
        return -1
    
    # for file link
    if is_link(source_file):
        tgt_file = get_link(source_file)
        ret = exec_cmd("ln -s %s %s" % (tgt_file, target_file), remote_host=target_host)
        if ret == None or ret[0] != 0:
            logger.error("bbcp link [%s] to [%s] failed" % (source_file, target_host))
            return -1
        return 0
        
    found = False
    retries = 1
    stime = time.time()
    while retries > 0:
        # check if the file exists on remote host
        source_file_size = get_file_size(source_file)
        if source_file_size < 0:
            logger.error("get size of [%s] failed" % source_file)
            return -1
            
        # prepare target home
        exec_cmd("mkdir -p %s && chmod 755 %s" % (os.path.dirname(target_file), os.path.dirname(target_file)), remote_host=target_host, suppress_warning=True)

        # it may fail since target disk is not synced yet
        ret = exec_cmd("bbcp %s %s root@%s:%s" % (opt, source_file, target_host, target_file),
                       timeout=timeout)
        
        # check file size
        if ret != None and ret[0] == 0:
            target_file_size = get_file_size(target_file, target_host)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("bbcp_to size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))
            
        remove_file(target_file, target_host)
        time.sleep(3)
        retries -= 1
        
    if not found:
        logger.error("bbcp [%s] to [%s] failed" % (source_file, target_host))
        return -1
    
    etime = time.time()
    logger.info("bbcp [%s] to [%s:%s] OK : size[%s] time[%.3f]" % (source_file, target_host, target_file, source_file_size, etime - stime))
    return 0

def scp_to(source_file, target_host, target_file, timeout=60, bwlimit=None):
    '''
        @note: this method is INVALID for raw sparse image copy
    '''

    if bwlimit:
        opt = "-P %s -c arcfour -l %s -o ConnectTimeout=3 -o ConnectionAttempts=1" % (get_ssh_port(), (int(bwlimit) / 128))
    else:
        opt = "-P %s -c arcfour -o ConnectTimeout=3 -o ConnectionAttempts=1" % (get_ssh_port())
        
    if not os.path.exists(source_file):
        logger.error("scp [%s] to [%s] failed: not exists" % (source_file, target_host))
        return -1
    
    # for file link
    if is_link(source_file):
        tgt_file = get_link(source_file)
        ret = exec_cmd("ln -s %s %s" % (tgt_file, target_file), remote_host=target_host)
        if ret == None or ret[0] != 0:
            logger.error("scp link [%s] to [%s] failed" % (source_file, target_host))
            return -1
        return 0
        
    found = False
    retries = 1
    stime = time.time()
    while retries > 0:
        # check if the file exists on remote host
        source_file_size = get_file_size(source_file)
        if source_file_size < 0:
            logger.error("get size of [%s] failed" % source_file)
            return -1
            
        # prepare target home
        exec_cmd("mkdir -p %s && chmod 755 %s" % (os.path.dirname(target_file), os.path.dirname(target_file)), remote_host=target_host, suppress_warning=True)

        # it may fail since target disk is not synced yet
        ret = exec_cmd("scp %s %s root@%s:%s" % (opt, source_file, target_host, target_file),
                       timeout=timeout)
        
        # check file size
        if ret != None and ret[0] == 0:
            target_file_size = get_file_size(target_file, target_host)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("scp_to size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))
            
        remove_file(target_file, target_host)
        time.sleep(3)
        retries -= 1
        
    if not found:
        logger.error("scp [%s] to [%s] failed" % (source_file, target_host))
        return -1
    
    etime = time.time()
    logger.info("scp [%s] to [%s:%s] OK : size[%s] time[%.3f]" % (source_file, target_host, target_file, source_file_size, etime - stime))
    return 0

def ftp_get(source_host, source_file, target_home, timeout=60, bwlimit=None):
    # check if the file exists on remote host
    source_ftp_file = "%s%s" % (FTP_ROOT, source_file)

    target_file = target_home + "/" + os.path.basename(source_file)
    found = False
    retries = 3
    while retries > 0:
        source_file_size = get_file_size(source_ftp_file, source_host)
        if source_file_size < 0:
            logger.error("get size of [%s] failed" % source_ftp_file)
            return -1
        
        # it may fail since target disk is not synced yet
        ret = exec_cmd("cd %s && wget -q %s ftp://%s%s" % (target_home, "" if not bwlimit else "--limit-rate=%s" % bwlimit, source_host, source_file),
                       timeout=timeout)
        
        # check file size
        if ret != None and ret[0] == 0:
            target_file_size = get_file_size(target_file)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("ftp get size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))
            
        remove_file(target_file)
        time.sleep(3)
        retries -= 1
        
    if not found:
        logger.error("ftp get [%s] from [%s] failed" % (source_file, source_host))
        return -1
    return 0

def ftp_put(source_file, target_host, target_home, timeout=60, bwlimit=None):
    dir_name = os.path.dirname(source_file)
    file_name = os.path.basename(source_file)
    target_file = "%s%s/%s" % (FTP_ROOT, target_home, file_name)
    found = False
    retries = 3
    while retries > 0:
        source_file_size = get_file_size(source_file)
        if source_file_size < 0:
            logger.error("get size of [%s] failed" % source_file)
            return -1

        # make sure target_home exists
        exec_cmd("mkdir -p %s && chmod 755 %s" % (os.path.dirname(target_file), os.path.dirname(target_file)), remote_host=target_host, suppress_warning=True)
        
        # it may fail since target disk is not synced yet
        ret = exec_cmd("cd %s && wput -q %s %s ftp://%s%s/" % (dir_name, "" if not bwlimit else "--limit-rate=%s" % bwlimit, file_name, target_host, target_home),
                       timeout=timeout)
        
        # check file size
        if ret != None and ret[0] == 0:
            time.sleep(3)
            target_file_size = get_file_size(target_file, target_host)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("ftp put size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))
            
        remove_file(target_file, target_host)
        time.sleep(3)
        retries -= 1
        
    if not found:
        logger.error("ftp put [%s] to [%s] failed" % (source_file, target_host))
        return -1
    return 0

def zip_to(source_file, target_host, target_file, timeout=60, bwlimit=None):
    '''
        @note: this method is INVALID for raw sparse image copy
    '''
    if not os.path.exists(source_file):
        return 0
    
    # for file link
    if is_link(source_file):
        tgt_file = get_link(source_file)
        ret = exec_cmd("ln -s %s %s" % (tgt_file, target_file), remote_host=target_host)
        if ret == None or ret[0] != 0:
            logger.error("zip link [%s] to [%s] failed" % (source_file, target_host))
            return -1
        return 0
        
    opt = ""
    if bwlimit:
        opt = " pv -q -L %s |" % (bwlimit)

    found = False
    retries = 3
    stime = time.time()
    while retries > 0:
        # check if the file exists on remote host
        source_file_size = get_file_size(source_file)
        if source_file_size < 0:
            logger.error("get size of [%s] failed" % source_file)
            return -1
            
        # prepare target home
        exec_cmd("mkdir -p %s && chmod 755 %s" % (os.path.dirname(target_file), os.path.dirname(target_file)), remote_host=target_host, suppress_warning=True)

        # it may fail since target disk is not synced yet
        ret = exec_cmd("lz4 %s - |%s ssh -p %d -c arcfour root@%s \"lz4 -f -d - %s\"" % (source_file, opt, get_ssh_port(), target_host, target_file),
                       timeout=timeout)
        
        # check file size
        if ret != None and ret[0] == 0:
            target_file_size = get_file_size(target_file, target_host)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("zip_to size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))
            
        remove_file(target_file, target_host)
        time.sleep(3)
        retries -= 1
        
    if not found:
        logger.error("zip [%s] to [%s] failed" % (source_file, target_host))
        return -1
    
    etime = time.time()
    logger.info("zip [%s] to [%s:%s] OK : size[%s] time[%.3f]" % (target_file, target_host, target_file, source_file_size, etime - stime))
    return 0

def zip_from(source_host, source_file, target_file, timeout=60, bwlimit=None):

    opt = ""
    if bwlimit:
        opt = " pv -q -L %s |" % (bwlimit)

    found = False
    retries = 3
    stime = time.time()
    while retries > 0:
        # check if the file exists on remote host
        source_file_size = get_file_size(source_file, source_host)
        if source_file_size < 0:
            logger.error("get size of [%s] failed" % source_file)
            return -1
    
        # it may fail since target disk is not synced yet
        ret = exec_cmd("ssh -p %d -c arcfour root@%s \"lz4 %s -\" |%s lz4 -f -d - %s" % (get_ssh_port(), source_host, source_file, opt, target_file),
                       timeout=timeout)
        
        # check file size
        if ret != None and ret[0] == 0:
            target_file_size = get_file_size(target_file)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("zip_from size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))
            
        remove_file(target_file)
        time.sleep(3)
        retries -= 1
        
    if not found:
        logger.error("zip [%s] from [%s] failed" % (source_file, source_host))
        return -1
    
    etime = time.time()
    logger.info("zip [%s] from [%s:%s] OK : size[%s] time[%.3f]" % (target_file, source_host, source_file, source_file_size, etime - stime))
    return 0

def tar_from(source_host, source_file, target_home, timeout=60, sparse=True, compress=False, bwlimit=None):
    '''
        @note: this is the only method valid for raw sparse image copy (sparse shall be True)
    '''
    
    dir_name = os.path.dirname(source_file)
    file_name = os.path.basename(source_file)
    target_file = "%s/%s" % (target_home, file_name)

    bwopt = ""
    if bwlimit:
        bwopt = " pv -q -L %s |" % (bwlimit)

    opt = ""
    if sparse:
        opt += "S"
    if compress:
        opt += "z"

    found = False
    retries = 3
    stime = time.time()
    while retries > 0:
        # check if the file exists on remote host
        source_file_size = get_file_size(source_file, source_host)
        if source_file_size < 0:
            logger.error("get size of [%s] failed" % source_file)
            return -1
    
        # it may fail since target disk is not synced yet
        ret = exec_cmd("cd %s && ssh -p %d -c arcfour root@%s \"cd %s; tar %scf - %s\" |%s tar %sxf -" % 
                       (target_home, get_ssh_port(), source_host,
                        dir_name, opt, file_name, bwopt, opt),
                       timeout=timeout)
        
        # check file size
        if ret != None and ret[0] == 0:
            target_file_size = get_file_size(target_file)
            if target_file_size == source_file_size:
                found = True
                break
            logger.error("tar_from size mismatch for [%s]: [%s] != [%s]" % (source_file, target_file_size, source_file_size))
            
        remove_file(target_file)
        time.sleep(3)
        retries -= 1
        
    if not found:
        logger.error("tar [%s] from [%s] failed" % (source_file, source_host))
        return -1
    
    etime = time.time()
    logger.info("tar [%s] from [%s:%s] OK : size[%s] time[%.3f]" % (target_file, source_host, source_file, source_file_size, etime - stime))
    return 0
