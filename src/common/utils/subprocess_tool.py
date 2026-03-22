import sys

import os
import types
import traceback
import gc
import signal
import errno
import time
import fcntl
from time import time as _time

def setNonBlocking(fd):
    """Make a fd non-blocking."""
    flag = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)
    flag = fcntl.fcntl(fd, fcntl.F_GETFL)
    
# Exception classes used by this module.
class SubprocessError(Exception): pass

# Exception classes used by this module.
class CalledProcessError(Exception):
    """This exception is raised when a process run by check_call() or
    check_output() returns a non-zero exit status.
    The exit status will be stored in the returncode attribute;
    check_output() will also store the output in the output attribute.
    """
    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)


class TimeoutExpired(SubprocessError):
    """This exception is raised when the timeout expires while waiting for a
    child process.
    """
    def __init__(self, cmd, timeout, output=None):
        self.cmd = cmd
        self.timeout = timeout
        self.output = output

    def __str__(self):
        return ("Command '%s' timed out after %s seconds" % 
                (self.cmd, self.timeout))

import select
_has_poll = hasattr(select, 'poll')
import fcntl
import pickle

# When select or poll has indicated that the file is writable,
# we can write up to _PIPE_BUF bytes without risk of blocking.
# POSIX defines PIPE_BUF as >= 512.
_PIPE_BUF = getattr(select, 'PIPE_BUF', 512)


__all__ = ["Popen", "PIPE", "STDOUT", "call", "check_call",
           "check_output", "CalledProcessError"]

try:
    MAXFD = os.sysconf("SC_OPEN_MAX")
except:
    MAXFD = 256

_active = []

def _cleanup():
    for inst in _active[:]:
        res = inst._internal_poll(_deadstate=sys.maxint)
        if res is not None:
            try:
                _active.remove(inst)
            except ValueError:
                # This can happen if two threads create a new Popen instance.
                # It's harmless that it was already removed, so ignore.
                pass

PIPE = -1
STDOUT = -2


def _eintr_retry_call(func, *args):
    while True:
        try:
            return func(*args)
        except (OSError, IOError) as e:
            if e.errno == errno.EINTR:
                continue
            raise


def call(*popenargs, **kwargs):
    """Run command with arguments.  Wait for command to complete, then
    return the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    retcode = call(["ls", "-l"])
    """
    return Popen(*popenargs, **kwargs).wait()


def check_call(*popenargs, **kwargs):
    """Run command with arguments.  Wait for command to complete.  If
    the exit code was zero then return, otherwise raise
    CalledProcessError.  The CalledProcessError object will have the
    return code in the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    check_call(["ls", "-l"])
    """
    retcode = call(*popenargs, **kwargs)
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd)
    return 0


def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd, output=output)
    return output


def list2cmdline(seq):
    """
    Translate a sequence of arguments into a command line
    string, using the same rules as the MS C runtime:

    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.
    """

    # See
    # http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    # or search http://msdn.microsoft.com for
    # "Parsing C++ Command-Line Arguments"
    result = []
    needquote = False
    for arg in seq:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


class Popen(object):
    _child_created = False  # Set here since __del__ checks it

    def __init__(self, args, bufsize=0, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=False, shell=False,
                 cwd=None, env=None, universal_newlines=False,
                 startupinfo=None, creationflags=0):
        """Create new Popen instance."""
        _cleanup()

        if not isinstance(bufsize, (int, long)):
            raise TypeError("bufsize must be an integer")

        # POSIX
        if startupinfo is not None:
            raise ValueError("startupinfo is only supported on Windows "
                             "platforms")
        if creationflags != 0:
            raise ValueError("creationflags is only supported on Windows "
                             "platforms")

        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.universal_newlines = universal_newlines

        # Input and output objects. The general principle is like
        # this:
        #
        # Parent                   Child
        # ------                   -----
        # p2cwrite   ---stdin--->  p2cread
        # c2pread    <--stdout---  c2pwrite
        # errread    <--stderr---  errwrite
        #
        # On POSIX, the child objects are file descriptors.  On
        # Windows, these are Windows file handles.  The parent objects
        # are file descriptors on both platforms.  The parent objects
        # are None when not using PIPEs. The child objects are None
        # when not redirecting.

        (p2cread, p2cwrite,
         c2pread, c2pwrite,
         errread, errwrite), to_close = self._get_handles(stdin, stdout, stderr)

        try:
            self._execute_child(args, executable, preexec_fn, close_fds,
                                cwd, env, universal_newlines,
                                startupinfo, creationflags, shell, to_close,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite)
        except Exception:
            # Preserve original exception in case os.close raises.
            exc_type, exc_value, exc_trace = sys.exc_info()

            for fd in to_close:
                try:
                    os.close(fd)
                except EnvironmentError:
                    pass

            raise exc_type, exc_value, exc_trace

        if p2cwrite is not None:
            self.stdin = os.fdopen(p2cwrite, 'wb', bufsize)
        if c2pread is not None:
            if universal_newlines:
                self.stdout = os.fdopen(c2pread, 'rU', bufsize)
            else:
                self.stdout = os.fdopen(c2pread, 'rb', bufsize)
        if errread is not None:
            if universal_newlines:
                self.stderr = os.fdopen(errread, 'rU', bufsize)
            else:
                self.stderr = os.fdopen(errread, 'rb', bufsize)


    def _translate_newlines(self, data):
        data = data.replace("\r\n", "\n")
        data = data.replace("\r", "\n")
        return data


    def __del__(self, _maxint=sys.maxint):
        # If __init__ hasn't had a chance to execute (e.g. if it
        # was passed an undeclared keyword argument), we don't
        # have a _child_created attribute at all.
        if not self._child_created:
            # We didn't get to successfully create a child process.
            return
        # In case the child hasn't been waited on, check if it's done.
        self._internal_poll(_deadstate=_maxint)
        if self.returncode is None and _active is not None:
            # Child is still running, keep us alive until we can wait on it.
            _active.append(self)


    def communicate(self, input=None, timeout=None):
        """Interact with process: Send data to stdin.  Read data from
        stdout and stderr, until end-of-file is reached.  Wait for
        process to terminate.  The optional input argument should be a
        string to be sent to the child process, or None, if no data
        should be sent to the child.

        communicate() returns a tuple (stdout, stderr)."""

        # Optimization: If we are only using one pipe, or no pipe at
        # all, using select() or threads is unnecessary.
        if timeout is None and [self.stdin, self.stdout, self.stderr].count(None) >= 2:
            stdout = None
            stderr = None
            if self.stdin:
                if input:
                    try:
                        self.stdin.write(input)
                    except IOError as e:
                        if e.errno != errno.EPIPE and e.errno != errno.EINVAL:
                            raise
                self.stdin.close()
            elif self.stdout:
                stdout = _eintr_retry_call(self.stdout.read)
                self.stdout.close()
            elif self.stderr:
                stderr = _eintr_retry_call(self.stderr.read)
                self.stderr.close()
            self.wait()
        else:
            if timeout is not None:
                endtime = _time() + timeout
            else:
                endtime = None

            try:
                stdout, stderr = self._communicate(input, endtime, timeout)
            finally:
                pass

            self.wait(timeout=self._remaining_time(endtime))

        return (stdout, stderr)


    def poll(self):
        return self._internal_poll()

    def _remaining_time(self, endtime):
        """Convenience for _communicate when computing timeouts."""
        if endtime is None:
            return None
        else:
            return endtime - _time()

    def _check_timeout(self, endtime, orig_timeout):
        """Convenience for checking if a timeout has expired."""
        if endtime is None:
            return
        if _time() > endtime:
            raise TimeoutExpired(self.args, orig_timeout)

    #
    # POSIX methods
    #
    def _get_handles(self, stdin, stdout, stderr):
        """Construct and return tuple with IO objects:
        p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
        """
        to_close = set()
        p2cread, p2cwrite = None, None
        c2pread, c2pwrite = None, None
        errread, errwrite = None, None

        if stdin is None:
            pass
        elif stdin == PIPE:
            p2cread, p2cwrite = self.pipe_cloexec()
            to_close.update((p2cread, p2cwrite))
        elif isinstance(stdin, int):
            p2cread = stdin
        else:
            # Assuming file-like object
            p2cread = stdin.fileno()

        if stdout is None:
            pass
        elif stdout == PIPE:
            c2pread, c2pwrite = self.pipe_cloexec()
            to_close.update((c2pread, c2pwrite))
        elif isinstance(stdout, int):
            c2pwrite = stdout
        else:
            # Assuming file-like object
            c2pwrite = stdout.fileno()

        if stderr is None:
            pass
        elif stderr == PIPE:
            errread, errwrite = self.pipe_cloexec()
            to_close.update((errread, errwrite))
        elif stderr == STDOUT:
            if c2pwrite is not None:
                errwrite = c2pwrite
            else: # child's stdout is not set, use parent's stdout
                errwrite = sys.__stdout__.fileno()
        elif isinstance(stderr, int):
            errwrite = stderr
        else:
            # Assuming file-like object
            errwrite = stderr.fileno()

        return (p2cread, p2cwrite,
                c2pread, c2pwrite,
                errread, errwrite), to_close


    def _set_cloexec_flag(self, fd, cloexec=True):
        try:
            cloexec_flag = fcntl.FD_CLOEXEC
        except AttributeError:
            cloexec_flag = 1

        old = fcntl.fcntl(fd, fcntl.F_GETFD)
        if cloexec:
            fcntl.fcntl(fd, fcntl.F_SETFD, old | cloexec_flag)
        else:
            fcntl.fcntl(fd, fcntl.F_SETFD, old & ~cloexec_flag)


    def pipe_cloexec(self):
        """Create a pipe with FDs set CLOEXEC."""
        # Pipes' FDs are set CLOEXEC by default because we don't want them
        # to be inherited by other subprocesses: the CLOEXEC flag is removed
        # from the child's FDs by _dup2(), between fork() and exec().
        # This is not atomic: we would need the pipe2() syscall for that.
        r, w = os.pipe()
        self._set_cloexec_flag(r)
        self._set_cloexec_flag(w)
        return r, w


    def _close_fds(self, but):
        if hasattr(os, 'closerange'):
            os.closerange(3, but)
            os.closerange(but + 1, MAXFD)
        else:
            for i in xrange(3, MAXFD):
                if i == but:
                    continue
                try:
                    os.close(i)
                except:
                    pass


    def _execute_child(self, args, executable, preexec_fn, close_fds,
                       cwd, env, universal_newlines,
                       startupinfo, creationflags, shell, to_close,
                       p2cread, p2cwrite,
                       c2pread, c2pwrite,
                       errread, errwrite):
        """Execute program (POSIX version)"""

        if isinstance(args, types.StringTypes):
            args = [args]
        else:
            args = list(args)

        if shell:
            args = ["/bin/sh", "-c"] + args
            if executable:
                args[0] = executable

        if executable is None:
            executable = args[0]

        def _close_in_parent(fd):
            os.close(fd)
            to_close.remove(fd)

        # For transferring possible exec failure from child to parent
        # The first char specifies the exception type: 0 means
        # OSError, 1 means some other error.
        errpipe_read, errpipe_write = self.pipe_cloexec()
        try:
            try:
                gc_was_enabled = gc.isenabled()
                # Disable gc to avoid bug where gc -> file_dealloc ->
                # write to stderr -> hang.  http://bugs.python.org/issue1336
                gc.disable()
                try:
                    self.pid = os.fork()
                except:
                    if gc_was_enabled:
                        gc.enable()
                    raise
                self._child_created = True
                if self.pid == 0:
                    # Child
                    try:
                        # Close parent's pipe ends
                        if p2cwrite is not None:
                            os.close(p2cwrite)
                        if c2pread is not None:
                            os.close(c2pread)
                        if errread is not None:
                            os.close(errread)
                        os.close(errpipe_read)

                        # When duping fds, if there arises a situation
                        # where one of the fds is either 0, 1 or 2, it
                        # is possible that it is overwritten (#12607).
                        if c2pwrite == 0:
                            c2pwrite = os.dup(c2pwrite)
                        if errwrite == 0 or errwrite == 1:
                            errwrite = os.dup(errwrite)

                        # Dup fds for child
                        def _dup2(a, b):
                            # dup2() removes the CLOEXEC flag but
                            # we must do it ourselves if dup2()
                            # would be a no-op (issue #10806).
                            if a == b:
                                self._set_cloexec_flag(a, False)
                            elif a is not None:
                                os.dup2(a, b)
                        _dup2(p2cread, 0)
                        _dup2(c2pwrite, 1)
                        _dup2(errwrite, 2)

                        # Close pipe fds.  Make sure we don't close the
                        # same fd more than once, or standard fds.
                        closed = { None }
                        for fd in [p2cread, c2pwrite, errwrite]:
                            if fd not in closed and fd > 2:
                                os.close(fd)
                                closed.add(fd)

                        if cwd is not None:
                            os.chdir(cwd)

                        if preexec_fn:
                            preexec_fn()

                        # Close all other fds, if asked for - after
                        # preexec_fn(), which may open FDs.
                        if close_fds:
                            self._close_fds(but=errpipe_write)

                        if env is None:
                            os.execvp(executable, args)
                        else:
                            os.execvpe(executable, args, env)

                    except:
                        exc_type, exc_value, tb = sys.exc_info()
                        # Save the traceback and attach it to the exception object
                        exc_lines = traceback.format_exception(exc_type,
                                                               exc_value,
                                                               tb)
                        exc_value.child_traceback = ''.join(exc_lines)
                        os.write(errpipe_write, pickle.dumps(exc_value))

                    # This exitcode won't be reported to applications, so it
                    # really doesn't matter what we return.
                    os._exit(255)

                # Parent
                if gc_was_enabled:
                    gc.enable()
            finally:
                # be sure the FD is closed no matter what
                os.close(errpipe_write)

            # Wait for exec to fail or succeed; possibly raising exception
            data = _eintr_retry_call(os.read, errpipe_read, 1048576)
            pickle_bits = []
            while data:
                pickle_bits.append(data)
                data = _eintr_retry_call(os.read, errpipe_read, 1048576)
            data = "".join(pickle_bits)
        finally:
            if p2cread is not None and p2cwrite is not None:
                _close_in_parent(p2cread)
            if c2pwrite is not None and c2pread is not None:
                _close_in_parent(c2pwrite)
            if errwrite is not None and errread is not None:
                _close_in_parent(errwrite)

            # be sure the FD is closed no matter what
            os.close(errpipe_read)

        if data != "":
            try:
                _eintr_retry_call(os.waitpid, self.pid, 0)
            except OSError as e:
                if e.errno != errno.ECHILD:
                    raise
            child_exception = pickle.loads(data)
            raise child_exception


    def _handle_exitstatus(self, sts, _WIFSIGNALED=os.WIFSIGNALED,
            _WTERMSIG=os.WTERMSIG, _WIFEXITED=os.WIFEXITED,
            _WEXITSTATUS=os.WEXITSTATUS):
        # This method is called (indirectly) by __del__, so it cannot
        # refer to anything outside of its local scope.
        if _WIFSIGNALED(sts):
            self.returncode = -_WTERMSIG(sts)
        elif _WIFEXITED(sts):
            self.returncode = _WEXITSTATUS(sts)
        else:
            # Should never happen
            raise RuntimeError("Unknown child exit status!")


    def _internal_poll(self, _deadstate=None, _waitpid=os.waitpid,
            _WNOHANG=os.WNOHANG, _os_error=os.error, _ECHILD=errno.ECHILD):
        """Check if child process has terminated.  Returns returncode
        attribute.

        This method is called by __del__, so it cannot reference anything
        outside of the local scope (nor can any methods it calls).

        """
        if self.returncode is None:
            try:
                pid, sts = _waitpid(self.pid, _WNOHANG)
                if pid == self.pid:
                    self._handle_exitstatus(sts)
            except _os_error as e:
                if _deadstate is not None:
                    self.returncode = _deadstate
                if e.errno == _ECHILD:
                    # This happens if SIGCLD is set to be ignored or
                    # waiting for child processes has otherwise been
                    # disabled for our process.  This child is dead, we
                    # can't get the status.
                    # http://bugs.python.org/issue15756
                    self.returncode = 0
        return self.returncode


    def _try_wait(self, wait_flags):
        try:
            (pid, sts) = _eintr_retry_call(os.waitpid, self.pid, wait_flags)
        except OSError as e:
            if e.errno != errno.ECHILD:
                raise
            # This happens if SIGCLD is set to be ignored or waiting
            # for child processes has otherwise been disabled for our
            # process.  This child is dead, we can't get the status.
            pid = self.pid
            sts = 0
        return (pid, sts)

    def wait(self, timeout=None, endtime=None):
        """Wait for child process to terminate.  Returns returncode
        attribute."""
        if self.returncode is not None:
            return self.returncode

        # endtime is preferred to timeout.  timeout is only used for
        # printing.
        if endtime is not None or timeout is not None:
            if endtime is None:
                endtime = _time() + timeout
            elif timeout is None:
                timeout = self._remaining_time(endtime)

        if endtime is not None:
            # Enter a busy loop if we have a timeout.  This busy loop was
            # cribbed from Lib/threading.py in Thread.wait() at r71065.
            delay = 0.0005 # 500 us -> initial delay of 1 ms
            while True:
                (pid, sts) = self._try_wait(os.WNOHANG)
                assert pid == self.pid or pid == 0
                if pid == self.pid:
                    self._handle_exitstatus(sts)
                    break
                remaining = self._remaining_time(endtime)
                if remaining <= 0:
                    raise TimeoutExpired(self.args, timeout)
                delay = min(delay * 2, remaining, .05)
                time.sleep(delay)
        elif self.returncode is None:
            (pid, sts) = self._try_wait(0)
            self._handle_exitstatus(sts)
        return self.returncode

    def _communicate(self, input, endtime, orig_timeout):
        if self.stdin:
            # Flush stdio buffer.  This might block, if the user has
            # been writing to .stdin in an uncontrolled fashion.
            self.stdin.flush()
            if not input:
                self.stdin.close()

        if _has_poll:
            stdout, stderr = self._communicate_with_poll(input, endtime,
                                                         orig_timeout)
        else:
            stdout, stderr = self._communicate_with_select(input, endtime,
                                                         orig_timeout)

        self.wait(timeout=self._remaining_time(endtime))

        # All data exchanged.  Translate lists into strings.
        if stdout is not None:
            stdout = ''.join(stdout)
        if stderr is not None:
            stderr = ''.join(stderr)

        # Translate newlines, if requested.  We cannot let the file
        # object do the translation: It is based on stdio, which is
        # impossible to combine with select (unless forcing no
        # buffering).
        if self.universal_newlines and hasattr(file, 'newlines'):
            if stdout:
                stdout = self._translate_newlines(stdout)
            if stderr:
                stderr = self._translate_newlines(stderr)

        self.wait()
        return (stdout, stderr)


    def _communicate_with_poll(self, input, endtime, orig_timeout):
        stdout = None # Return
        stderr = None # Return
        fd2file = {}
        fd2output = {}

        poller = select.poll()
        def register_and_append(file_obj, eventmask):
            poller.register(file_obj.fileno(), eventmask)
            fd2file[file_obj.fileno()] = file_obj

        def close_unregister_and_remove(fd):
            poller.unregister(fd)
            fd2file[fd].close()
            fd2file.pop(fd)

        if self.stdin and input:
            register_and_append(self.stdin, select.POLLOUT)

        select_POLLIN_POLLPRI = select.POLLIN | select.POLLPRI
        if self.stdout:
            register_and_append(self.stdout, select_POLLIN_POLLPRI)
            fd2output[self.stdout.fileno()] = stdout = []
        if self.stderr:
            register_and_append(self.stderr, select_POLLIN_POLLPRI)
            fd2output[self.stderr.fileno()] = stderr = []

        input_offset = 0
        while fd2file:
            timeout = self._remaining_time(endtime)
            if timeout is not None and timeout < 0:
                raise TimeoutExpired(self.args, orig_timeout)
            try:
                ready = poller.poll(timeout)
            except select.error as e:
                if e.args[0] == errno.EINTR:
                    continue
                raise
            self._check_timeout(endtime, orig_timeout)

            for fd, mode in ready:
                if mode & select.POLLOUT:
                    chunk = input[input_offset : input_offset + _PIPE_BUF]
                    try:
                        input_offset += os.write(fd, chunk)
                    except OSError as e:
                        if e.errno == errno.EPIPE:
                            close_unregister_and_remove(fd)
                        else:
                            raise
                    else:
                        if input_offset >= len(input):
                            close_unregister_and_remove(fd)
                elif mode & select_POLLIN_POLLPRI:
                    data = os.read(fd, 4096)
                    if not data:
                        close_unregister_and_remove(fd)
                    fd2output[fd].append(data)
                else:
                    # Ignore hang up or errors.
                    close_unregister_and_remove(fd)

        return (stdout, stderr)


    def _communicate_with_select(self, input, endtime, orig_timeout):
        read_set = []
        write_set = []
        stdout = None # Return
        stderr = None # Return

        if self.stdin and input:
            write_set.append(self.stdin)
        if self.stdout:
            read_set.append(self.stdout)
            stdout = []
        if self.stderr:
            read_set.append(self.stderr)
            stderr = []

        input_offset = 0
        while read_set or write_set:
            timeout = self._remaining_time(endtime)
            if timeout is not None and timeout < 0:
                raise TimeoutExpired(self.args, orig_timeout)
            try:
                (rlist, wlist, xlist) = \
                    select.select(self._read_set, self._write_set, [],
                                  timeout)
            except select.error as e:
                if e.args[0] == errno.EINTR:
                    continue
                raise

            # According to the docs, returning three empty lists indicates
            # that the timeout expired.
            if not (rlist or wlist or xlist):
                raise TimeoutExpired(self.args, orig_timeout)
            # We also check what time it is ourselves for good measure.
            self._check_timeout(endtime, orig_timeout)

            if self.stdin in wlist:
                chunk = input[input_offset : input_offset + _PIPE_BUF]
                try:
                    bytes_written = os.write(self.stdin.fileno(), chunk)
                except OSError as e:
                    if e.errno == errno.EPIPE:
                        self.stdin.close()
                        write_set.remove(self.stdin)
                    else:
                        raise
                else:
                    input_offset += bytes_written
                    if input_offset >= len(input):
                        self.stdin.close()
                        write_set.remove(self.stdin)

            if self.stdout in rlist:
                data = os.read(self.stdout.fileno(), 1024)
                if data == "":
                    self.stdout.close()
                    read_set.remove(self.stdout)
                stdout.append(data)

            if self.stderr in rlist:
                data = os.read(self.stderr.fileno(), 1024)
                if data == "":
                    self.stderr.close()
                    read_set.remove(self.stderr)
                stderr.append(data)

        return (stdout, stderr)


    def send_signal(self, sig):
        """Send a signal to the process
        """
        os.kill(self.pid, sig)

    def terminate(self):
        """Terminate the process with SIGTERM
        """
        self.send_signal(signal.SIGTERM)

    def kill(self):
        """Kill the process with SIGKILL
        """
        self.send_signal(signal.SIGKILL)
