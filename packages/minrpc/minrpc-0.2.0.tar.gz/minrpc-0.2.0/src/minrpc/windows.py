"""
Windows specific low level stuff.
"""

import msvcrt
import _winapi


__all__ = [
    'Handle',
]


class Handle(object):

    """
    Wrap a native HANDLE. Close on deletion.
    """

    def __init__(self, handle, own=True):
        """Store a native HANDLE (int)."""
        self.handle = handle
        self.own = own

    @classmethod
    def from_fd(cls, fd, own):
        """Create a :class:`Handle` instance from a file descriptor (int)."""
        handle = msvcrt.get_osfhandle(fd)
        return cls(handle, own)

    @classmethod
    def pipe(cls):
        """
        Create a unidirectional pipe.

        Return a pair (recv, send) of :class:`Handle`s.
        """
        # use _winapi.CreatePipe on windows, just like subprocess.Popen
        # does when requesting PIPE streams. This is the easiest and most
        # reliable method I have tested so far:
        recv, send = _winapi.CreatePipe(None, 0)
        return cls(recv), cls(send)

    def __int__(self):
        """Get the underlying handle."""
        return int(self.handle)

    def __del__(self):
        """Close the handle."""
        self.close()

    def __enter__(self):
        """Enter `with` context."""
        return self

    def __exit__(self, *exc_info):
        """Close the handle."""
        self.close()

    def close(self):
        """Close the handle."""
        if self.own and self.handle is not None:
            _winapi.CloseHandle(self.handle)
            self.handle = None

    def detach_fd(self):
        """
        Open a file descriptor for the HANDLE and release ownership.

        Closing the file descriptor will also close the handle.
        """
        fd = msvcrt.open_osfhandle(self.handle, 0)
        self.handle = None
        return fd

    def dup_inheritable(self):
        """Point this handle to ."""
        # new handles are created uninheritable by default, but they can be
        # made inheritable on duplication:
        current_process = _winapi.GetCurrentProcess()
        dup = _winapi.DuplicateHandle(
            current_process,                # source process
            self.handle,                    # source handle
            current_process,                # target process
            0,                              # desired access
            True,                           # inheritable
            _winapi.DUPLICATE_SAME_ACCESS,  # options
        )
        return self.__class__(dup)
