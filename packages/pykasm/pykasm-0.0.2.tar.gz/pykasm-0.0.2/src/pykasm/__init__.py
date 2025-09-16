import platform
import ctypes
from . import utils
import sys
import os

if "PYASM_UTILS_k83bC67" not in os.environ:
    utils.build_env()

    print("You don't have the environment created. So, it was created, open the environment variables and check if it has been created, and if it has been created, restart your device so that the code works.")

    exit(0)

system = platform.system()

try:
    env = eval(os.environ["PYASM_UTILS_k83bC67"].replace("\\", "/"))
except:
    pass

keystone_dir = env[0]

keystone_path = env[1]

libpyasm_path = env[2]

if system == "Linux":
    env_var = "LD_LIBRARY_PATH"
elif system == "Darwin":
    env_var = "DYLD_LIBRARY_PATH"
elif system == "Windows":
    env_var = "PATH"
else:
    raise RuntimeError(f'Unsupported system: {system}')
    
paths_add = [
    os.path.dirname(libpyasm_path),
    keystone_dir
]

current_paths = os.environ.get(env_var, '').split(os.pathsep)
new_paths = [temp for temp in paths_add if temp and temp not in current_paths]
os.environ[env_var] = os.pathsep.join(new_paths + current_paths)

ctypes.CDLL(keystone_path, mode=ctypes.RTLD_GLOBAL)

if hasattr(ctypes, "RTLD_GLOBAL") and hasattr(sys, "setdlopenflags"):
    sys.setdlopenflags(ctypes.RTLD_GLOBAL)

lib = ctypes.CDLL(libpyasm_path)

lib._asm_.argtypes = (ctypes.c_char_p,)
lib._asm_.resttype = ctypes.c_long

def run_asm(code: str) -> int:
    return lib._asm_(code.encode('utf-8'))
