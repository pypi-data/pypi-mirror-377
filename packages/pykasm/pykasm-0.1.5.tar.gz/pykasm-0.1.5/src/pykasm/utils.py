from ._bin import *
import subprocess
import platform
import base64
import os

inp = None
_rt = None
trys = 1

class EnvironmentError(Exception):
    def __init__(self, message='Error creating environment.'):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f'EnvironmentError:\n    {self.message}'

def _raise(ex):
    raise ex

def is_android():
    return (
        "ANDROID_ROOT" in os.environ
        or "ANDROID_DATA" in os.environ
        or "android" in platform.release().lower()
    )

def find_abs_path(frac, rt="/" if platform.system() == "Linux" else "C:/" if platform.system() == "Windows" else "/data/data/" if is_android() else _raise(OSError("unsupported os."))):
    global inp
    global _rt

    _rt = rt + '/'

    if is_android() and inp == None:
        inp = input("What is the package you are using on your Android? : ")

        _rt += inp

    norm_frac = os.path.normpath(frac)

    for root, dirs, files in os.walk(_rt):
        for d in dirs:
            current = os.path.join(root, d)

            if current.endswith(norm_frac):
                return os.path.abspath(current)

        for f in files:
            current = os.path.join(root, f)

            if current.endswith(norm_frac):
                return os.path.abspath(current)

    return

def build_envp(self):
    global _rt
    global trys

    _os = platform.system()
    arch = platform.machine().lower()
    release = platform.release().lower()

    pos_0 = None
    pos_1 = None
    pos_2 = None
    pos_3 = None
    pos_4 = None

    if _os == "Linux":
        pos_3 = "/pyasm/rasm/lib/"
        pos_4 = "/pyasm/lib/"

        if arch in ("aarch64", "arm64"):
            pos_0 = "/pykasm/rasm/keystone/lbuild/llvm/lib/"
            pos_1 = "/pykasm/rasm/keystone/lbuild/llvm/lib/libarm64keystone.so.0"
            pos_2 = "/pykasm/lib/arm64pyasm.so"
        else:
            pos_0 = "/pykasm/rasm/keystone/lbuild/llvm/lib/"
            pos_1 = "/pykasm/rasm/keystone/lbuild/llvm/lib/libamd64keystone.so.0"
            pos_2 = "/pykasmlib/amd64pyasm.so"
    elif _os == "Windows":
        pos_0 = "/pykasm/rasm/keystone/winbuild/llvm/lib/"
        pos_1 = "/pykasm/rasm/keystone/winbuild/llvm/lib/keystone.dll"
        pos_2 = "/pykasm/lib/pyasm.dll"
    else:
        raise OSError(f"System {_os} not automatically supported. Configure manually.")
    
    pos_0_n = find_abs_path(pos_0)
    pos_1_n = find_abs_path(pos_1)
    pos_2_n = find_abs_path(pos_2)
    pos_3_n = find_abs_path(pos_3)
    pos_4_n = find_abs_path(pos_4)

    if any(item is None for item in [pos_0_n, pos_1_n, pos_2_n, pos_3_n, pos_4_n]):
        if trys < 2:
            trys += 1

            if arch in ("aarch64", "arm64"):
                open(os.path.join(_rt, pos_1), 'wb').write(base64.b64decode(arm64keystone))
                open(os.path.join(_rt, pos_2), 'wb').write(base64.b64decode(arm64pyasm))
                open(os.path.join(_rt, pos_3, 'libarm64rasm.so'), 'wb').write(base64.b64decode(arm64rasm))
            else:
                if _os == "Windows":
                    open(os.path.join(_rt, pos_1), 'wb').write(base64.b64decode(win64keystone))
                    open(os.path.join(_rt, pos_2), 'wb').write(base64.b64decode(win64pyasm))
                    open(os.path.join(_rt, pos_3, 'rasm.dll'), 'wb').write(base64.b64decode(win64rasm))
                else:
                    open(os.path.join(_rt, pos_1), 'wb').write(base64.b64decode(amd64keystone))
                    open(os.path.join(_rt, pos_2), 'wb').write(base64.b64decode(amd64pyasm))
                    open(os.path.join(_rt, pos_3, 'libamd64rasm.so'), 'wb').write(base64.b64decode(amd64rasm))

            self()
        else:
            raise FileNotFoundError("One or some of the important files from this library were not found to be used.")

    VAR_NAME = "PYASM_UTILS_k83bC67"
    VAR_VALUE = f"""["{pos_0_n}","{pos_1_n}","{pos_2_n}"]"""
    VAR_NAME_CONFIG = "LD_LIBRARY_PATH"
    VAR_VALUE_CONFIG = f"{pos_3_n}:{pos_4_n}:$LD_LIBRARY_PATH"

    if _os == "Windows":
        subprocess.run(["setx", VAR_NAME, VAR_VALUE], shell=True)
    elif _os == "Linux" or _os == "Darwin" or _os == "Linux" and "android" in platform.release().lower():
        shell_config = os.path.expanduser("~/.bashrc")

        if os.environ.get("SHELL", "").endswith("zsh"):
            shell_config = os.path.expanduser("~/.zshrc")

        with open(shell_config, "a") as f:
            f.write(f"\nexport {VAR_NAME_CONFIG}='{VAR_VALUE_CONFIG}'\n")

        shell_config = os.path.expanduser("~/.bashrc")

        if os.environ.get("SHELL", "").endswith("zsh"):
            shell_config = os.path.expanduser("~/.zshrc")

        with open(shell_config, "a") as f:
            f.write(f"\nexport {VAR_NAME}='{VAR_VALUE}'\n")
    else:
        raise OSError(f"System {_os} not automatically supported. Configure manually.")

def build_env():
    build_envp(build_envp)