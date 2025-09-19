# 🛠 pykasm

**pykasm** is a Python library for executing Assembly (ASM) code directly from Python scripts, allowing low-level integration with system calls and native libraries.

The goal is to provide a bridge between **Python** and **Assembly**, enabling developers to explore optimizations, manipulate memory, and execute machine instructions in a controlled manner.

---

## 📦 Installation

You can install via **pip** (after publication on PyPI):

```bash
pip install pykasm
```

💻 Examples

1️⃣ X86 Linux Example

```python
##################################
#      X86 Linux Example         #
##################################

import pykasm
import ctypes

libc = ctypes.CDLL(None)
puts = libc.puts
puts.argtypes = [ctypes.c_char_p]
puts.restype = ctypes.c_int

msg_buf = ctypes.create_string_buffer(b"Hello, World")
msg_addr = ctypes.addressof(msg_buf)

puts_addr = ctypes.cast(puts, ctypes.c_void_p).value

asm_code = (
    f"mov rdi, {msg_addr};\n"
    f"mov rax, {puts_addr};\n"
    "call rax;\n"
    "ret"
)

pykasm.run_asm(asm_code)
```

2️⃣ X86 Windows Example

```python
################################## 
#      X86 Windows Example       # 
##################################

import pykasm
import ctypes

msvcrt = ctypes.CDLL("msvcrt.dll")
puts = msvcrt.puts
puts.argtypes = [ctypes.c_char_p]
puts.restype = ctypes.c_int

kernel32 = ctypes.WinDLL("kernel32.dll")
ExitProcess = kernel32.ExitProcess
ExitProcess.argtypes = [ctypes.c_uint]
ExitProcess.restype = None

msg_buf = ctypes.create_string_buffer(b"Hello, World!\n")
msg_addr = ctypes.addressof(msg_buf)

puts_addr = ctypes.cast(puts, ctypes.c_void_p).value
exitprocess_addr = ctypes.cast(ExitProcess, ctypes.c_void_p).value

asm_code = (
    f"mov rcx, {msg_addr}; "
    f"mov rax, {puts_addr}; "
    "call rax; "
    "mov rcx, 0; "
    f"mov rax, {exitprocess_addr}; "
    "call rax; "
)

pykasm.run_asm(asm_code)
```

2️⃣ ARM64 Android Example

```python
##################################
#     ARM64 Android Example      #
##################################

import pykasm
import ctypes

libc = ctypes.CDLL(None)
puts = libc.puts
puts.argtypes = [ctypes.c_char_p]
puts.restype = ctypes.c_int

_exit = libc.exit
_exit.argtypes = [ctypes.c_int]
_exit.restype = None

msg_buf = ctypes.create_string_buffer(b"Hello, World")
msg_addr = ctypes.addressof(msg_buf)

puts_addr = ctypes.cast(puts, ctypes.c_void_p).value
exit_addr = ctypes.cast(_exit, ctypes.c_void_p).value

def mov_imm64(reg, val):
    parts = [
        (val >> 0) & 0xFFFF,
        (val >> 16) & 0xFFFF,
        (val >> 32) & 0xFFFF,
        (val >> 48) & 0xFFFF,
    ]

    asm = []

    asm.append(f'movz {reg}, #{parts[0]}')

    if parts[1]: asm.append(f'movk {reg}, #{parts[1]}')
    if parts[2]: asm.append(f'movk {reg}, #{parts[2]}')
    if parts[3]: asm.append(f'movk {reg}, #{parts[3]}')

    return "\n".join(asm)

asm_code = '\n'.join([
    mov_imm64('x0', msg_addr),
    mov_imm64('x16', puts_addr),
    "blr x16",
    "mov x0, #0",
    mov_imm64('x16', exit_addr),
    "blr x16",
    "ret",
])

pykasm.run_asm(asm_code)
```