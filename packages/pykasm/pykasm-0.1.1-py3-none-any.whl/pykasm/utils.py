import subprocess
import platform
import os

inp = None

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

def build_env():
    _os = platform.system()
    arch = platform.machine().lower()
    release = platform.release().lower()

    pos_0 = None
    pos_1 = None
    pos_2 = None
    pos_3 = None
    pos_4 = None

    if _os == "Linux":
        pos_3 = "/rasm/lib/"
        pos_4 = "/lib/"

        if arch in ("aarch64", "arm64"):
            pos_0 = "/rasm/keystone/lbuild/llvm/lib/"
            pos_1 = "/rasm/keystone/lbuild/llvm/lib/libarm64keystone.so.0"
            pos_2 = "/lib/arm64pyasm.so"
        else:
            pos_0 = "/rasm/keystone/lbuild/llvm/lib/"
            pos_1 = "/rasm/keystone/lbuild/llvm/lib/libamd64keystone.so.0"
            pos_2 = "/lib/amd64pyasm.so"
    elif _os == "Windows":
        pos_0 = "/rasm/keystone/winbuild/llvm/lib/"
        pos_1 = "/rasm/keystone/winbuild/llvm/lib/keystone.dll"
        pos_2 = "/lib/pyasm.dll"
    else:
        raise OSError(f"System {_os} not automatically supported. Configure manually.")
    
    pos_0 = find_abs_path(pos_0)
    pos_1 = find_abs_path(pos_1)
    pos_2 = find_abs_path(pos_2)
    pos_3 = find_abs_path(pos_3)
    pos_4 = find_abs_path(pos_4)

    if any(item is None for item in [pos_0, pos_1, pos_2, pos_3, pos_4]):
        raise FileNotFoundError("One or some of the important files from this library were not found to be used.")

    VAR_NAME = "PYASM_UTILS_k83bC67"
    VAR_VALUE = f"""["{pos_0}","{pos_1}","{pos_2}"]"""
    VAR_NAME_CONFIG = "LD_LIBRARY_PATH"
    VAR_VALUE_CONFIG = f"{pos_3}:{pos_4}:$LD_LIBRARY_PATH"

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