import os

if not os.path.exists(r"Moon\dlls\PySGL.dll") or not os.path.exists(r"Moon\src\PySGL.cpp"):
    os.system(r'python PySGL\build.py')


DLL_OUTPUT_PATH = r"dll\Moon.dll"

DLL_FOUND_PATH = r"Moon/dlls/Moon.dll"
DLL_LOCAL_FOUND_PATH = r"./dlls/Moon.dll"
DLL_MODULE_FOUND_PATH = r"../dlls/Moon.dll"

if os.name != 'nt':  # Only for Windows
    from colorama import Fore
    print(f"[ {Fore.RED}Err{Fore.RESET} ] Moon framework is not support ({os.name}) system.")
