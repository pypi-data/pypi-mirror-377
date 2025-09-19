from ._bin import *
import subprocess
import platform
import tempfile
import base64
import os

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

_rt = None
trys = 0

if platform.system() == "Linux":
    _rt = "/"
elif platform.system() == "Windows":
    _rt = "C:/"
elif is_android():
    inp = input('What is the name of the package of the app you are using? : ')

    _rt = os.path.join('/data/data/', inp)
else:
    raise OSError("unsupported os.")

_dir = os.path.join(os.path.expanduser("~"), ".pykasm_cache")

def make_files(rt, mode='w'):
    directory = os.path.dirname(rt)

    os.makedirs(directory, exist_ok=True)

    return open(rt, mode)

def find_abs_path(frac):
    global _rt
    global _dir

    norm_frac = os.path.normpath(frac)

    search_bases = [
        _rt,
        _dir
    ]

    for base in search_bases:
        for root, dirs, files in os.walk(base):
            for d in dirs:
                current = os.path.join(root, d)
                if current.endswith(norm_frac):
                    return os.path.abspath(current)

            for f in files:
                current = os.path.join(root, f)
                if current.endswith(norm_frac):
                    return os.path.abspath(current)

    return None

def build_env():
    global _rt
    global trys
    global _dir

    _os = platform.system()
    arch = platform.machine().lower()
    release = platform.release().lower()

    pos_0 = None
    pos_1 = None
    pos_2 = None
    pos_3 = None
    pos_4 = None

    if _os == "Linux":
        pos_3 = "/pykasm/rasm/lib/"
        pos_4 = "/pykasm/lib/"

        if arch in ("aarch64", "arm64"):
            pos_0 = "/pykasm/rasm/keystone/lbuild/llvm/lib/"
            pos_1 = "/pykasm/rasm/keystone/lbuild/llvm/lib/libarm64keystone.so.0"
            pos_2 = "/pykasm/lib/arm64pyasm.so"
        else:
            pos_0 = "/pykasm/rasm/keystone/lbuild/llvm/lib/"
            pos_1 = "/pykasm/rasm/keystone/lbuild/llvm/lib/libamd64keystone.so.0"
            pos_2 = "/pykasm/lib/amd64pyasm.so"
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
                with make_files(os.path.join(_dir, pos_1.lstrip(os.sep)), 'wb') as f:
                    f.write(base64.b64decode(arm64keystone))
                with make_files(os.path.join(_dir, pos_2.lstrip(os.sep)), 'wb') as f:
                    f.write(base64.b64decode(arm64pyasm))
                with make_files(os.path.join(_dir, pos_3.lstrip(os.sep), 'libarm64rasm.so'), 'wb') as f:
                    f.write(base64.b64decode(arm64rasm))
            else:
                if _os == "Windows":
                    with make_files(os.path.join(_dir, pos_1.lstrip(os.sep)), 'wb') as f:
                        write(base64.b64decode(win64keystone))
                    with make_files(os.path.join(_dir, pos_2.lstrip(os.sep)), 'wb') as f:
                        f.write(base64.b64decode(win64pyasm))
                    with make_files(os.path.join(_dir, pos_3.lstrip(os.sep), 'rasm.dll'), 'wb') as f:
                        f.write(base64.b64decode(win64rasm))
                else:
                    with make_files(os.path.join(_dir, pos_1.lstrip(os.sep)), 'wb') as f:
                        f.write(base64.b64decode(amd64keystone))
                    with make_files(os.path.join(_dir, pos_2.lstrip(os.sep)), 'wb') as f:
                        f.write(base64.b64decode(amd64pyasm))
                    with make_files(os.path.join(_dir, os.path.join(pos_3, 'libamd64rasm.so').lstrip(os.sep)), 'wb') as f:
                        f.write(base64.b64decode(amd64rasm))

            os.system(f'ls {_dir}')

            build_env()
        else:
            raise FileNotFoundError("One or some of the important files from this library were not found to be used.")

    if any(item is None for item in [pos_0_n, pos_1_n, pos_2_n, pos_3_n, pos_4_n]):
        VAR_NAME = "PYASM_UTILS_k83bC67"
        VAR_VALUE = f"""["{pos_0_n}","{pos_1_n}","{pos_2_n}"]"""
    
        VAR_NAME_CONFIG = "LD_LIBRARY_PATH"
        VAR_VALUE_CONFIG = f"{pos_3_n}:{pos_4_n}:$LD_LIBRARY_PATH"
    else:
        pass
    
    if _os == "Windows":
        subprocess.run(["setx", VAR_NAME, VAR_VALUE], shell=True)
    elif _os == "Linux" or _os == "Darwin" or _os == "Linux" and "android" in platform.release().lower():
        shell_config = os.path.expanduser("~/.bashrc")

        if os.environ.get("SHELL", "").endswith("zsh"):
            shell_config = os.path.expanduser("~/.zshrc")

        with open(shell_config, "a") as f:
            f.write(f"\nexport {VAR_NAME_CONFIG}={VAR_VALUE_CONFIG}\n")

        shell_config = os.path.expanduser("~/.bashrc")

        if os.environ.get("SHELL", "").endswith("zsh"):
            shell_config = os.path.expanduser("~/.zshrc")

        with open(shell_config, "a") as f:
            f.write(f"\nexport {VAR_NAME}='{VAR_VALUE}'\n")
    else:
        raise OSError(f"System {_os} not automatically supported. Configure manually.")