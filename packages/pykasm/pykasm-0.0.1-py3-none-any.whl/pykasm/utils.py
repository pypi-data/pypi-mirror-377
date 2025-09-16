import subprocess
import platform
import os

def find_abs_path(frac, rt="/" if platform.system() == "Linux" else "C:/"):
    norm_frac = os.path.normpath(frac)

    for root, dirs, files in os.walk(rt):
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

    pos_0 = None
    pos_1 = None
    pos_2 = None

    if _os == "Linux":
        pos_0 = "/pyasm/rasm/keystone/lbuild/llvm/lib/"
        pos_1 = "/pyasm/rasm/keystone/lbuild/llvm/lib/libkeystone.so.0"
        pos_2 = "/pyasm/lib/libpyasm.so"
    elif _os == "Windows":
        pos_0 = "/pyasm/rasm/keystone/winbuild/llvm/lib/"
        pos_1 = "/pyasm/rasm/keystone/winbuild/llvm/lib/keystone.dll"
        pos_2 = "/pyasm/lib/pyasm.dll"
    else:
        raise OSError(f"System {_os} not automatically supported. Configure manually.")

    VAR_NAME = "PYASM_UTILS_k83bC67"
    VAR_VALUE = f"""["{find_abs_path(pos_0)}","{find_abs_path(pos_1)}","{find_abs_path(pos_2)}"]"""

    if _os == "Windows":
        subprocess.run(["setx", VAR_NAME, VAR_VALUE], shell=True)
    elif _os == "Linux" or _os == "Darwin":
        shell_config = os.path.expanduser("~/.bashrc")

        if os.environ.get("SHELL", "").endswith("zsh"):
            shell_config = os.path.expanduser("~/.zshrc")

        with open(shell_config, "a") as f:
            f.write(f"\nexport {VAR_NAME}='{VAR_VALUE}'\n")
    else:
        raise OSError(f"System {_os} not automatically supported. Configure manually.")