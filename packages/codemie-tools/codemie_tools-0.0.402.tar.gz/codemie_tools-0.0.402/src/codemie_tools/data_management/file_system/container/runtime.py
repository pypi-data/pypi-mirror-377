import asyncio
import os
import sys
import logging
import tempfile
import traceback

from codemie_tools.data_management.file_system.container.connections import (
    ADealer,
    ARouter,
    Dealer,
    timeout,
)
from codemie_tools.data_management.file_system.container.jupyter import (
    Jupyter,
    RuntimeOutput,
    RuntimeOutputTraceback,
)
from codemie_tools.data_management.file_system.container.utils.c_types_util import (
    MountFlags,
    mount,
    umount,
)

logger = logging.getLogger(__name__)

PORT_FLAG = "--port"
ROOTFS_PATH_FLAG = "--rootfs"
SESSION_ID_FLAG = "--session-id"

ROOT_FOLDER = "/root"

SHUTDOWN_TIMEOUT = 20  # Timeout in seconds


class BaseContainerException(RuntimeError):
    def __init__(self, message: str, msg_type: str = "error") -> None:
        self.message = message
        self.msg_type = msg_type
        self.traceback = "".join(traceback.format_exc())
        super().__init__(f"{'type': '{msg_type}', 'content': {message}}")


def raise_exit_code(msg: str, code: int):
    raise BaseContainerException(f"{msg}. errno={code}, strerror=({os.strerror(code)})")


class ContainerRuntime:
    host_volumes_to_mount = [
        "/bin",
        "/sbin",
        "/usr",
        "/lib",
        "/lib64",
        "/venv",
    ]

    rootless_tmp_fs = [
        "/var",
        ROOT_FOLDER,
        "/etc",
    ]

    host_dev_devices = [
        "null",
        "zero",
    ]

    def _setup_environ(self):
        os.environ.clear()
        os.environ["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin"
        os.environ["HOME"] = ROOT_FOLDER

    def _mount_dev(self, dev_folder: str):
        if err := mount("tmpfs", dev_folder, fstype="tmpfs", flags=0, data=f"mode={755}"):
            raise_exit_code("Cannot mount dev folder", err)

        for dev in self.host_dev_devices:
            source = f"/dev/{dev}"
            target = os.path.join(dev_folder, dev)

            if os.path.exists(source):
                try:
                    open(target, "a").close()
                except Exception:
                    raise BaseContainerException(f"Cannot create {target} dev")

                if err := mount(source, target, flags=MountFlags.BIND):
                    raise_exit_code(f"Cannot mount {dev} dev", err)

    def _umount_dev(self, dev_folder: str):
        for dev in self.host_dev_devices:
            target = os.path.join(dev_folder, dev)
            umount(target)
        umount(dev_folder)

    def setup_rootfs(self, rootfs_folder: str):
        if err := mount(None, "/", flags=MountFlags.REC | MountFlags.PRIVATE):
            raise_exit_code("Cannot mount read only root", err)

        for source_folder in self.host_volumes_to_mount:
            target_folder = os.path.join(rootfs_folder, source_folder.lstrip("/"))
            if err := mount(
                source_folder, target_folder, flags=MountFlags.BIND | MountFlags.PRIVATE
            ):
                raise_exit_code(f"Cannot mount {source_folder} to {target_folder}", err)

        for tmp_folder in self.rootless_tmp_fs:
            target_folder = os.path.join(rootfs_folder, tmp_folder.lstrip("/"))
            if err := mount("tmpfs", target_folder, "tmpfs", 0, "mode=755"):
                raise_exit_code(f"Cannot mount tmpfs to {target_folder}", err)

        proc_folder = os.path.join(rootfs_folder, "proc")
        if err := mount("proc", proc_folder, "proc"):
            raise_exit_code("Cannot mount proc to {proc_folder}", err)

        dev_dir = os.path.join(rootfs_folder, "dev")
        self._mount_dev(dev_dir)

        try:
            os.chdir(rootfs_folder)
        except Exception as e:
            raise BaseContainerException(f"Cannot chdir into {rootfs_folder} folder. Err: {str(e)}")

        try:
            os.chroot(".")
        except Exception as e:
            raise BaseContainerException(
                f"Cannot chroot into {rootfs_folder} folder. Err: {str(e)}"
            )

        try:
            os.chdir("/")
        except Exception as e:
            raise ValueError(f"Cannot chdir into new chroot. Err: {str(e)}")

        try:
            self._setup_environ()
        except Exception as e:
            raise ValueError(f"Cannot setup environ. Err: {str(e)}")

    def destroy_rootfs(self, rootfs_folder: str):
        for source_folder in self.host_volumes_to_mount:
            target_folder = os.path.join(rootfs_folder, source_folder.lstrip("/"))
            umount(target_folder)

        for tmp_folder in self.rootless_tmp_fs:
            target_folder = os.path.join(rootfs_folder, tmp_folder.lstrip("/"))
            umount(target_folder)

        self._umount_dev(os.path.join(rootfs_folder, "dev"))
        umount(os.path.join(rootfs_folder, "proc"))
        umount("/")


async def run_code(code: str):
    try:
        with tempfile.TemporaryDirectory(dir="/", prefix="jupyter_") as jupyter_dir:
            async with Jupyter(jupyter_dir) as jupyter:
                if not jupyter.kc:
                    raise RuntimeError("jupyter client could not be started")

                return await jupyter.arun(code)
    except Exception as e:
        raise BaseContainerException(f"Cannot start or execute jupyter kernel. Err: {str(e)}")


@timeout(SHUTDOWN_TIMEOUT)
async def handler(port: int, rootfs: str, session_id: str):
    router = ARouter.create()

    r = ContainerRuntime()
    r.setup_rootfs(rootfs)

    with Dealer(port, f"send_code-{session_id}".encode()) as dealer:
        dealer.send_msg(f"{router.port}".encode())

    while True:
        identity, payload = await router.arecv_msg()
        match identity:
            case b"code":
                code = payload.decode()

                result = await run_code(code)

                with ADealer(port, f"result-{session_id}".encode()) as dealer:
                    await dealer.asend_msg(result.model_dump_json().encode())

                return

            case _:
                raise BaseContainerException(f"Runtime receive unknow command: {identity.decode()}")


if __name__ == "__main__":
    try:
        i = sys.argv.index(PORT_FLAG)
        port = int(sys.argv[i + 1])
    except Exception:
        os._exit(1)

    try:
        i = sys.argv.index(ROOTFS_PATH_FLAG)
        rootfs = sys.argv[i + 1]
    except Exception:
        os._exit(1)
    try:
        i = sys.argv.index(SESSION_ID_FLAG)
        session_id = sys.argv[i + 1]
    except Exception:
        os._exit(1)

    try:
        asyncio.run(handler(port, rootfs, session_id))
    except BaseContainerException as e:
        with Dealer(port, f"error-{session_id}".encode()) as dealer:
            dealer.send_msg(
                RuntimeOutputTraceback(type=e.msg_type, content=e.message, traceback=e.traceback)
                .model_dump_json()
                .encode()
            )

    except asyncio.TimeoutError:
        with Dealer(port, f"error-{session_id}".encode()) as dealer:
            dealer.send_msg(
                RuntimeOutput(type="error", content="Code execution reach a timeout")
                .model_dump_json()
                .encode(),
            )

    except Exception as e:
        with Dealer(port, f"error-{session_id}".encode()) as dealer:
            dealer.send_msg(
                RuntimeOutputTraceback(
                    type="error",
                    content=f"Code execution got unexpected error: {str(e)}",
                    traceback="".join(traceback.format_exc()),
                )
                .model_dump_json()
                .encode(),
            )
    finally:
        os._exit(0)
