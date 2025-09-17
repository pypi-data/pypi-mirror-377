import signal
import json
import logging
import os
import sys
import tempfile
import traceback

from codemie_tools.data_management.file_system.container.connections import (
    ARouter,
    ADealer,
    Dealer,
    Router,
    timeout,
)
from codemie_tools.data_management.file_system.container.jupyter import RuntimeOutputTraceback
from codemie_tools.data_management.file_system.container.mappings import check_and_write_mapping
from codemie_tools.data_management.file_system.container.runtime import (
    SESSION_ID_FLAG,
    PORT_FLAG,
    ROOTFS_PATH_FLAG,
    SHUTDOWN_TIMEOUT,
)

logger = logging.getLogger(__name__)


def _send_error_and_exit(port: int, session_id: str, msg: str):
    with Dealer(port, f"error-{session_id}".encode()) as dealer:
        dealer.send_msg(
            RuntimeOutputTraceback(
                type="error",
                content=msg,
                traceback="".join(traceback.format_exc()),
            )
            .model_dump_json()
            .encode()
        )
    os._exit(1)


def reap_children(signum, frame):
    while True:
        try:
            # Reap all children that have exited (Processs zombies)
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
            logger.debug(f"Collected process zombie pid={pid} with status={status}")
        except ChildProcessError:
            break


signal.signal(signal.SIGCHLD, reap_children)


class Container:
    def __init__(self):
        self.rootfs: str | None = None

    async def _handler(self, router: ARouter, code: str, child_pid: int, session_id: str):
        while True:
            identity, payload = await router.arecv_msg()
            if identity == f"error-{session_id}".encode():
                error_dict: dict = json.loads(payload)
                raise RuntimeError(json.dumps(error_dict))

            elif identity == f"result-{session_id}".encode():
                return payload

            elif identity == f"send_code-{session_id}".encode():
                port = int(payload.decode())
                with ADealer(port, b"code") as dealer:
                    await dealer.asend_msg(code.encode())

            elif identity == f"write_mapping-{session_id}".encode():
                uid = os.getuid()
                gid = os.getgid()

                check_and_write_mapping(child_pid, uid, gid)
                port = int(payload.decode())

                with ADealer(port, b"1") as dealer:
                    await dealer.asend_msg(b"written")

            else:
                return

    async def _unshare(self, port: int, session_id: str):
        try:
            os.unshare(os.CLONE_NEWUSER)
        except Exception as e:
            _send_error_and_exit(
                port, session_id, f"Syscall unshare os.CLONE_NEWUSER restricted. Err: {str(e)}"
            )

        router = Router.create()

        with Dealer(port, f"write_mapping-{session_id}".encode()) as dealer:
            dealer.send_msg(f"{router.port}".encode())

        _, _ = router.recv_msg()
        del router

        try:
            os.unshare(os.CLONE_NEWPID | os.CLONE_NEWNS)
        except Exception as e:
            _send_error_and_exit(
                port,
                session_id,
                f"Syscall unshare os.CLONE_NEWPID | os.CLONE_NEWNS restricted. Err: {str(e)}",
            )

    @timeout(SHUTDOWN_TIMEOUT * 2)
    async def run(self, code: str, session_id: str):
        """
        Host process
        ├─ fork -> Child A (host PID X)
        │  └─ Child A: unshare(CLONE_NEWUSER)
        │     └─ [Important: Host writes UID/GID mappings for Child A]
        │          to /proc/ChildA_PID/uid_map and /proc/ChildA_PID/gid_map
        │
        │     └─ fork -> Inner PID 1 in the new user namespace (UID: 0, PID: 1)
        │          └─ exec runtime.py

        codemie  | first fork uid 1001 pid: 2844
        codemie  | before unshare uid 1001 pid: 2844
        codemie  | after unshare uid 65534 pid: 2844
        codemie  | lock child_pid: 2844
        codemie  | main porcess uid 1001 child_pid 2844 main_pid: 2805
        codemie  | writed mappings child_pid 2844 uid 1001 main_pid: 2805
        codemie  | unlock child_pid: 2844
        codemie  | second fork uid 0 pid: 1
        """

        self.rootfs = tempfile.mkdtemp(prefix="container_root_")

        router = ARouter.create()
        port = router.port

        pid = os.fork()
        if pid == 0:
            await self._unshare(port, session_id)

            pid = os.fork()
            if pid == 0:
                script_path = os.path.abspath(__file__)
                script_dir = os.path.dirname(script_path)
                script_path = os.path.join(script_dir, "runtime.py")

                new_argv = [
                    sys.executable,
                    script_path,
                    PORT_FLAG,
                    str(port),
                    ROOTFS_PATH_FLAG,
                    self.rootfs,
                    SESSION_ID_FLAG,
                    session_id,
                ]

                try:
                    os.execve(sys.executable, new_argv, {})
                except Exception as e:
                    _send_error_and_exit(
                        port, session_id, f"Syscall execve restricted. Err: {str(e)}"
                    )

            else:
                os.waitpid(pid, 0)
                os._exit(0)

        else:
            try:
                return await self._handler(router, code, pid, session_id)
            except RuntimeError:
                raise
            except Exception as e:
                raise RuntimeError(
                    RuntimeOutputTraceback(
                        type="error",
                        content=f"Main handler got unexpected error: {str(e)}",
                        traceback="".join(traceback.format_exc()),
                    ).model_dump_json(),
                )
            finally:
                try:
                    del router
                except Exception:
                    pass
