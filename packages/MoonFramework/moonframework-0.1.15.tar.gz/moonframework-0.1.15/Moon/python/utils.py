import os
import inspect
import site
import sys
from typing import final, List
from Moon import DLL_FOUND_PATH, DLL_LOCAL_FOUND_PATH, DLL_MODULE_FOUND_PATH
from colorama import Fore

class LibraryLoadError(Exception):
    """Ошибка загрузки нативной библиотеки"""
    pass


def find_library() -> str:
    """
    #### Поиск пути к нативной библиотеке BUILD.dll
    
    ---
    
    :Returns:
        str: Абсолютный путь к библиотеке
        
    ---
    
    :Raises:
        LibraryLoadError: Если библиотека не найдена
    """
    # Получаем информацию о вызывающем файле
    caller_frame = inspect.stack()[1]
    caller_filename = os.path.basename(caller_frame.filename)
    
    # Список возможных путей к библиотеке, в порядке приоритета
    possible_paths: List[str] = [
        DLL_FOUND_PATH,
        DLL_LOCAL_FOUND_PATH,
        DLL_MODULE_FOUND_PATH,
    ]
    print(f"Loader: {caller_filename}")

    # Поиск по указанным путям
    for lib_path in possible_paths:
        if os.path.exists(lib_path):
            print(f"[ {Fore.GREEN}succes{Fore.RESET} ] Library found at: {Fore.YELLOW}'{lib_path}'{Fore.RESET}")
            return lib_path

    # Если не найдено по указанным путям, ищем в директории установки модуля
    print(f"[ {Fore.YELLOW}warning{Fore.RESET} ] Library not found in standard paths, searching in module installation directory...")
    
    # Получаем путь к установленному модулю Moon
    module_path = find_module_installation_path('Moon')
    
    if module_path:
        print(f"\t\tSearching in module path: {Fore.YELLOW}'{module_path}'{Fore.RESET}")
        found_path = recursive_find_library(module_path, caller_filename)
        if found_path:
            return found_path

    # Если не найдено в директории модуля, ищем рекурсивно от текущей директории
    print(f"[ {Fore.YELLOW}warning{Fore.RESET} ] Library not found in module directory, starting recursive search from current directory...")
    
    start_dir = os.getcwd()
    found_path = recursive_find_library(start_dir, caller_filename)
    
    if found_path:
        return found_path

    # Если ни один из путей не сработал
    raise LibraryLoadError(
        f"Moon library (Moon.dll) not found in any of the expected locations: {possible_paths}\n"
        f"Also not found in module installation directory or during recursive search from: {start_dir}"
    )


def find_module_installation_path(module_name: str) -> str:
    """
    Находит путь к установленному модулю
    
    :param module_name: Имя модуля
    :return: Путь к директории модуля или None
    """
    try:
        # Пытаемся импортировать модуль и получить его путь
        module = __import__(module_name)
        module_path = os.path.dirname(os.path.abspath(module.__file__))
        return module_path
    except ImportError:
        # Если модуль не найден через импорт, ищем в site-packages
        pass
    
    # Ищем модуль в директориях site-packages
    for site_dir in site.getsitepackages() + [site.getusersitepackages()]:
        if site_dir and os.path.exists(site_dir):
            module_dir = os.path.join(site_dir, module_name)
            if os.path.exists(module_dir):
                return module_dir
            
            # Проверяем также для case-insensitive систем
            for item in os.listdir(site_dir):
                if item.lower() == module_name.lower():
                    item_path = os.path.join(site_dir, item)
                    if os.path.isdir(item_path):
                        return item_path
    
    # Ищем в sys.path
    for path in sys.path:
        if path and os.path.exists(path):
            module_dir = os.path.join(path, module_name)
            if os.path.exists(module_dir):
                return module_dir
            
            # Case-insensitive поиск
            if os.path.isdir(path):
                for item in os.listdir(path):
                    if item.lower() == module_name.lower():
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            return item_path
    
    return None


def recursive_find_library(start_dir: str, caller_filename: str, max_depth: int = 5) -> str:
    """
    Рекурсивный поиск библиотеки Moon.dll в поддиректориях
    
    :param start_dir: Директория для начала поиска
    :param caller_filename: Имя файла вызывающего кода (для вывода)
    :param max_depth: Максимальная глубина рекурсии
    :return: Путь к найденной библиотеке
    """
    from colorama import Fore
    
    # Ищем файлы с подходящими именами
    target_names = ['Moon.dll', 'libMoon.so', 'libMoon.dylib']
    
    for depth in range(max_depth + 1):
        for root, dirs, files in os.walk(start_dir):
            # Проверяем глубину текущей директории
            current_depth = root[len(start_dir):].count(os.sep)
            if current_depth > depth:
                continue
            
            for file in files:
                if file in target_names:
                    found_path = os.path.join(root, file)
                    print(f"[ {Fore.GREEN}succes{Fore.RESET} ] Library found recursively at: {found_path}")
                    return found_path
        
        # Если на этой глубине не найдено, продолжаем поиск на следующей глубине
    
    return None