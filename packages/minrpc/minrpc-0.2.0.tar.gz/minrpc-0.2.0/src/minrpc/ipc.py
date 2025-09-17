"""
IPC utilities.
"""

import os
import subprocess
import sys

from .connection import Connection

win = sys.platform == 'win32'

if win:
    from .windows import Handle
else:
    from .posix import Handle


__all__ = [
    'create_ipc_connection',
    'spawn_subprocess',
    'prepare_subprocess_ipc',
]


def create_ipc_connection():
    """
    Create a connection that can be used for IPC with a subprocess.

    Return (local_connection, remote_recv_handle, remote_send_handle).
    """
    local_recv, _remote_send = Handle.pipe()
    _remote_recv, local_send = Handle.pipe()
    remote_recv = _remote_recv.dup_inheritable()
    remote_send = _remote_send.dup_inheritable()
    conn = Connection.from_fd(local_recv.detach_fd(),
                              local_send.detach_fd())
    return conn, remote_recv, remote_send


def spawn_subprocess(argv, **Popen_args):
    """
    Spawn a subprocess and pass to it two IPC handles.

    You can use the keyword arguments to pass further arguments to
    Popen, which is useful for example, if you want to redirect STDIO
    streams.

    Return (ipc_connection, process).
    """
    conn, remote_recv, remote_send = create_ipc_connection()
    args = argv + [str(int(remote_recv)), str(int(remote_send))]
    with open(os.devnull, 'w+') as devnull:
        for stream in ('stdout', 'stderr', 'stdin'):
            # Check whether it was explicitly disabled (`False`) rather than
            # simply not specified (`None`)?
            if Popen_args.get(stream) is False:
                Popen_args[stream] = devnull
        proc = subprocess.Popen(args, close_fds=False, **Popen_args)
    # wait for subprocess to confirm that all handles are closed:
    if conn.recv() != 'ready':
        raise RuntimeError
    return conn, proc


def prepare_subprocess_ipc(args):
    """
    Prepare this process for IPC with its parent. Close all the open handles
    except for the STDIN/STDOUT/STDERR and the IPC handles. Return a
    :class:`Connection` to the parent process.
    """
    handles = [Handle(int(arg)) for arg in args]
    recv_fd = handles[0].detach_fd()
    send_fd = handles[1].detach_fd()
    conn = Connection.from_fd(recv_fd, send_fd)
    conn.send('ready')
    return conn
