"""Runtime proxy helpers shared by CLI, UI, and AsyncDamru."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path, PureWindowsPath
from urllib.parse import urlparse

from .proxy import resolve_system_proxy


def is_windows() -> bool:
    return sys.platform == "win32"


def is_wsl_linux() -> bool:
    if is_windows() or platform.system() != "Linux":
        return False
    try:
        release = platform.uname().release.lower()
        if "microsoft" in release or "wsl" in release:
            return True
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return False


def configured_wsl_distro() -> str:
    env_distro = os.environ.get("DAMRU_WSL_DISTRO")
    if env_distro:
        return env_distro
    try:
        from . import config

        return config.WSL_DISTRO
    except Exception:
        return "Ubuntu"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def to_wsl_path(value: str) -> str:
    if re.match(r"^[A-Za-z]:[\\/]", value):
        p = PureWindowsPath(value)
        drive = p.drive.rstrip(":").lower()
        rest = "/".join(p.parts[1:])
        return f"/mnt/{drive}/{rest}"
    return value


def resolve_ssh_identity_file() -> str | None:
    try:
        from pathlib import Path
        local_key = Path.home() / ".ssh" / "id_rsa"
        if local_key.is_file():
            return str(local_key)
    except Exception:
        pass
    try:
        from pathlib import Path
        admin_key = Path("C:/Users/Administrator/.ssh/id_rsa")
        if admin_key.is_file():
            return str(admin_key)
    except Exception:
        pass
    return None


def create_secure_temp_key(original_key_path: str) -> str | None:
    import tempfile
    import shutil
    import getpass
    try:
        temp_dir = tempfile.gettempdir()
        temp_key_path = os.path.join(temp_dir, f"id_rsa_temp_{os.getpid()}_{hash(original_key_path) & 0xffffffff}")
        if os.path.exists(temp_key_path):
            try:
                os.remove(temp_key_path)
            except Exception:
                pass
        shutil.copy2(original_key_path, temp_key_path)
        username = os.environ.get("USERNAME")
        if not username or username.endswith("$"):
            username = "SYSTEM"
        subprocess.run(["icacls", temp_key_path, "/inheritance:r"], capture_output=True, text=True)
        subprocess.run(["icacls", temp_key_path, "/grant:r", f"{username}:(F)"], capture_output=True, text=True)
        return temp_key_path
    except Exception:
        return None


def linux_cmd(script: str, root_user: bool = False, ssh_key_path: str = None) -> list[str]:
    vm_ssh_host = os.environ.get("DAMRU_VM_SSH_HOST")
    if vm_ssh_host:
        encoded = base64.b64encode(script.encode("utf-8")).decode("ascii")
        inner = f"printf %s {encoded} | base64 -d | bash"
        wrapped = f"sudo bash -lc {shlex.quote(inner)}" if root_user else f"bash -lc {shlex.quote(inner)}"
        cmd = ["ssh", "-o", "StrictHostKeyChecking=no"]
        if ssh_key_path:
            cmd.extend(["-i", ssh_key_path])
        cmd.extend([f"administrator@{vm_ssh_host}", wrapped])
        return cmd

    if is_windows():
        encoded = base64.b64encode(script.encode("utf-8")).decode("ascii")
        wrapped = f"printf %s {encoded} | base64 -d | bash"
        cmd = ["wsl", "-d", configured_wsl_distro()]
        if root_user:
            cmd.extend(["-u", "root"])
        cmd.extend(["--", "bash", "-lc", wrapped])
        return cmd
    return ["bash", "-lc", script]


def linux_run(script: str, timeout: int = 30, root_user: bool = False) -> subprocess.CompletedProcess[str]:
    key_path = resolve_ssh_identity_file()
    temp_key = None
    if key_path and is_windows():
        temp_key = create_secure_temp_key(key_path)
    try:
        return subprocess.run(
            linux_cmd(script, root_user=root_user, ssh_key_path=temp_key or key_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
    finally:
        if temp_key and os.path.exists(temp_key):
            try:
                os.remove(temp_key)
            except Exception:
                pass


def proxy_bridge_upstream(proxy: str | None, http_proxy: str | None = None) -> str | None:
    value = (http_proxy or proxy or "").strip()
    if not value or "://" not in value:
        return None
    parsed = urlparse(value)
    scheme = (parsed.scheme or "").lower()
    if scheme in {"http", "https"}:
        return value if parsed.username is not None else None
    if scheme in {"socks5", "socks5h"}:
        return value
    return None


def _bridge_alive(port: int, *, root_user: bool) -> bool:
    vm_ssh_host = os.environ.get("DAMRU_VM_SSH_HOST")
    if vm_ssh_host:
        # Remote VM: check locally on the VM to bypass external firewall blocks
        probe = linux_run(
            f"timeout 1 bash -c '</dev/tcp/127.0.0.1/{port}' >/dev/null 2>&1",
            timeout=5,
            root_user=root_user,
        )
        return probe.returncode == 0
    else:
        import socket
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1.0):
                return True
        except Exception:
            return False


def android_proxy_host_from_route(route_text: str) -> str:
    match = re.search(r"\bvia\s+(\d+\.\d+\.\d+\.\d+)\b", route_text or "")
    if match:
        return match.group(1)
    src = re.search(r"\bsrc\s+(\d+)\.(\d+)\.(\d+)\.\d+\b", route_text or "")
    if src:
        return f"{src.group(1)}.{src.group(2)}.{src.group(3)}.1"
    return "127.0.0.1"


def ensure_proxy_bridge(upstream: str) -> int:
    digest = hashlib.sha256(upstream.encode("utf-8")).hexdigest()[:12]
    port = 18000 + (int(digest[:6], 16) % 3000)
    runtime_dir = "/home/damru/runtime/proxy-bridges" if is_windows() or is_wsl_linux() else str(Path.home() / ".cache" / "damru" / "proxy-bridges")
    config_path = f"{runtime_dir}/{digest}.json"
    log_path = f"{runtime_dir}/{digest}.log"
    script_path = repo_root() / "damru" / "proxy_bridge.py"
    linux_script = to_wsl_path(str(script_path)) if is_windows() else str(script_path)
    root_user = is_windows() or is_wsl_linux()
    config = json.dumps({"upstream": upstream, "listen_host": "0.0.0.0", "listen_port": port})
    config_b64 = base64.b64encode(config.encode("utf-8")).decode("ascii")

    if not _bridge_alive(port, root_user=root_user):
        write_cmd = (
            f"umask 077; mkdir -p {shlex.quote(runtime_dir)}; "
            f"printf %s {shlex.quote(config_b64)} | base64 -d > {shlex.quote(config_path)}; "
            f"chmod 600 {shlex.quote(config_path)}"
        )
        write = linux_run(write_cmd, timeout=30, root_user=root_user)
        if write.returncode != 0:
            raise RuntimeError((write.stderr or write.stdout or "failed to write proxy bridge config").strip())
        vm_ssh_host = os.environ.get("DAMRU_VM_SSH_HOST")
        if vm_ssh_host:
            start_cmd = (
                f"setsid -f /home/administrator/env/bin/python3 -m damru.proxy_bridge --config {shlex.quote(config_path)} "
                f"> {shlex.quote(log_path)} 2>&1 < /dev/null"
            )
        else:
            start_cmd = (
                f"setsid -f python3 {shlex.quote(linux_script)} --config {shlex.quote(config_path)} "
                f"> {shlex.quote(log_path)} 2>&1 < /dev/null"
            )
        start = linux_run(start_cmd, timeout=30, root_user=root_user)
        if start.returncode != 0:
            raise RuntimeError((start.stderr or start.stdout or "failed to start proxy bridge").strip())
        deadline = time.time() + 20
        while time.time() < deadline:
            if _bridge_alive(port, root_user=root_user):
                break
            time.sleep(1.5 if vm_ssh_host else 0.25)
        else:
            raise RuntimeError("proxy bridge did not become ready")
    return port


def resolve_android_proxy(proxy: str | None = None, http_proxy: str | None = None, route_text: str = "") -> str | None:
    upstream = proxy_bridge_upstream(proxy, http_proxy)
    if upstream:
        port = ensure_proxy_bridge(upstream)
        return f"{android_proxy_host_from_route(route_text)}:{port}"
    return resolve_system_proxy(proxy=proxy, http_proxy=http_proxy)
