
import time
from . import portalocker

DEFAULT_TIMEOUT = 5
DEFAULT_CHECK_INTERVAL = 0.25
LOCK_METHOD = portalocker.LOCK_EX | portalocker.LOCK_NB

__all__ = [
    'Lock',
    'AlreadyLocked',
]


class AlreadyLocked(Exception):
    pass


class Lock(object):

    def __init__(
            self, filename, mode='a', truncate=0, timeout=DEFAULT_TIMEOUT,
            check_interval=DEFAULT_CHECK_INTERVAL, fail_when_locked=True):
        '''Lock manager with build-in timeout

        filename -- filename
        mode -- the open mode, 'a' or 'ab' should be used for writing
        truncate -- use truncate to emulate 'w' mode, None is disabled, 0 is
            truncate to 0 bytes
        timeout -- timeout when trying to acquire a lock
        check_interval -- check interval while waiting
        fail_when_locked -- after the initial lock failed, return an error
            or lock the file

        fail_when_locked is useful when multiple threads/processes can race
        when creating a file. If set to true than the system will wait till
        the lock was acquired and then return an AlreadyLocked exception.

        Note that the file is opened first and locked later. So using 'w' as
        mode will result in truncate _BEFORE_ the lock is checked.
        '''

        self.fh = None
        self.filename = filename
        self.mode = mode
        self.truncate = truncate
        self.timeout = timeout
        self.check_interval = check_interval
        self.fail_when_locked = fail_when_locked

        assert 'w' not in mode, 'Mode "w" clears the file before locking'

    def acquire(
            self, timeout=None, check_interval=None, fail_when_locked=None):
        '''Acquire the locked filehandle'''
        if timeout is None:
            timeout = self.timeout
        if timeout is None:
            timeout = 0

        if check_interval is None:
            check_interval = self.check_interval

        if fail_when_locked is None:
            fail_when_locked = self.fail_when_locked

        # If we already have a filehandle, return it
        fh = self.fh
        if fh:
            return fh

        # Get a new filehandler
        fh = self._get_fh()
        try:
            # Try to lock
            fh = self._get_lock(fh)
        except portalocker.LockException as exception:
            # Try till the timeout is 0
            while timeout > 0:
                # Wait a bit
                time.sleep(check_interval)
                timeout -= check_interval

                # Try again
                try:

                    # We already tried to the get the lock
                    # If fail_when_locked is true, then stop trying
                    if fail_when_locked:
                        raise AlreadyLocked(exception)

                    else:  # pragma: no cover
                        # We've got the lock
                        fh = self._get_lock(fh)
                        break

                except portalocker.LockException:
                    pass

            else:
                # We got a timeout... reraising
                raise portalocker.LockException(exception)

        # Prepare the filehandle (truncate if needed)
        fh = self._prepare_fh(fh)

        self.fh = fh
        return fh

    def _get_fh(self):
        '''Get a new filehandle'''
        return open(self.filename, self.mode)

    def _get_lock(self, fh):
        '''
        Try to lock the given filehandle

        returns LockException if it fails'''
        portalocker.lock(fh, LOCK_METHOD)
        return fh

    def _prepare_fh(self, fh, truncate=None):
        '''
        Prepare the filehandle for usage

        If truncate is a number, the file will be truncated to that amount of
        bytes
        '''
        if truncate is None:
            truncate = self.truncate

        if truncate is not None:
            fh.seek(truncate)
            fh.truncate(truncate)

        return fh

    def __enter__(self):
        self.fh = self.acquire()
        return self.fh

    def __exit__(self, type_, value, tb):
        if self.fh:
            self.fh.close()
