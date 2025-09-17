import os
import sys
import time
from colorama import Fore

# Константа для отображения зеленой галочки успешного выполнения
SUCCES = f'[{Fore.GREEN}✔{Fore.RESET}]'


# Загрузка свойств сборки из файла конфигурации
def get_build_properties(properties_file_path: str) -> dict:
    properties = {}
    with open(properties_file_path, "r") as f:
        print(f"{Fore.CYAN}Initing{Fore.RESET}: {Fore.BLACK}Properties file detected{Fore.RESET} {SUCCES}")
        print(f"  |-> path: {Fore.YELLOW}'{properties_file_path}'{Fore.RESET}")
        content = f.read()
        print(f"  |-> data <\n{Fore.YELLOW}{content}{Fore.RESET}>\n")
        print(f"{Fore.CYAN}Initing{Fore.RESET}: {Fore.BLACK}Start loading...{Fore.RESET}")

        # Парсинг файла конфигурации построчно
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            if '=' not in line:
                continue
            key_value = line.split('#')[0].strip()
            key, value = key_value.split("=")
            properties[key.strip()] = value.strip()[1:-1]

        print(f"{Fore.CYAN}Initing{Fore.RESET}: {Fore.BLACK}Properties file loaded{Fore.RESET} {SUCCES}\n\n")
    return properties

# Функция сборки отдельного файла в DLL
def build_file(file_path: str, dlls_path: str, compiler_path: str, sfml_include_path: str, sfml_lib_path: str):
    # Получение имени файла и расширения
    file_name, file_extension = os.path.splitext(file_path)
    # Извлечение только имени файла без пути
    base_name = os.path.basename(file_name)
    
    
    print(f"{Fore.BLUE}Building{Fore.RESET}: {Fore.BLACK}{file_name}{Fore.RESET}")
    print(f"  |-> target: {Fore.GREEN}{file_extension}{Fore.RESET}")
    print(f"  |-> out target: {Fore.BLACK}.dll{Fore.RESET}")
    print(f"  |-> compiler: {Fore.YELLOW}{compiler_path}{Fore.RESET}")
    print(f"  |-> output_path: {Fore.YELLOW}{dlls_path}{Fore.RESET}")
    print(f"  |-> sfml_include_path: {Fore.MAGENTA}{sfml_include_path}{Fore.RESET}")
    print(f"  |-> sfml_lib_path: {Fore.MAGENTA}{sfml_lib_path}{Fore.RESET}")

    print('\n')

    # Формирование и выполнение команды компиляции
    print(f"{Fore.BLUE}Building{Fore.RESET}: Executing command...")
    print(f"  |-> {Fore.YELLOW}{compiler_path} -shared -o {dlls_path}/{base_name}.dll {file_path} -static -static-libstdc++ -static-libgcc -I {sfml_include_path} -L {sfml_lib_path} -lsfml-graphics-s -lsfml-window-s -lsfml-system-s -DSFML_STATIC -lopengl32 -lgdi32 -lwinmm -ldinput8 -lfreetype{Fore.RESET}")
    try:
        start_time = time.time()
        os.system(f"{compiler_path} -shared -o {dlls_path}/{base_name}.dll {file_path} -static \
-static-libstdc++ -static-libgcc \
-I {sfml_include_path} -L {sfml_lib_path} \
-DSFML_STATIC \
-lsfml-audio-s -lsfml-graphics-s -lsfml-window-s -lsfml-system-s \
-lopenal32 -lflac -lvorbisenc -lvorbisfile -lvorbis -logg \
-lopengl32 -lgdi32 -lwinmm -lfreetype")
        
        print(f"{Fore.BLUE}Building{Fore.RESET}: Builded {Fore.BLACK}{file_name}{Fore.RESET} {round(time.time() - start_time, 2)}ms {SUCCES}")
    except:
        ...

# Получение списка файлов в указанной директории
def get_builded_files(path: str):
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            files.append(file)
    return files

# Основная функция сборки проекта
def build():
    start_time = time.time()
    # Загрузка настроек сборки
    properties = get_build_properties(r"Moon\build.properties")
    
    # Получение списка всех файлов
    all_files = get_builded_files(properties["BUILD_FILES_PATH"])

    # Фильтрация файлов, которые нужно собрать (начинаются с "BUILDED")
    builded_files = list(filter(lambda x: x[0:7] == "BUILDED", all_files))
    
    print(f"{Fore.CYAN}Initing{Fore.RESET}: Founded [{Fore.BLACK}{len(all_files)}{Fore.RESET}] files")
    for file in all_files:
        if file in builded_files:
            print(f"  |-> <{Fore.GREEN}need build{Fore.RESET}> {Fore.YELLOW}{file}{Fore.RESET}")
        else:
            print(f"  |->              {Fore.YELLOW}{file}{Fore.RESET} ")
        
        
    print(f"\n{Fore.CYAN}Initing{Fore.RESET}: {Fore.BLACK}Start building...{Fore.RESET}")

    # Получение путей из конфигурации
    SFML_INCLUDE_PATH = properties["SFML_INCLUDE_PATH"]
    SFML_LIB_PATH = properties["SFML_LIB_PATH"]
    COMPILER_PATH = "g++" if properties["COMPILER_PATH"] == "global" else properties["COMPILER_PATH"]
    BUILD_FILES_PATH = properties["BUILD_FILES_PATH"]
    DLLS_FILES_PATH = properties["DLLS_FILES_PATH"]

    print(f"{Fore.BLUE}Building{Fore.RESET}: Generating builded file...")
    file = open(BUILD_FILES_PATH+"/Moon.cpp", 'w', encoding="utf-8")
    for bf in builded_files:
        
            fp = BUILD_FILES_PATH + "/" + bf
            print(fp)
            bff = open(fr"{fp}", 'r', encoding="utf-8")
            file.write(bff.read())
            bff.close()
        
    file.close()

    # Сборка файла
    build_file(BUILD_FILES_PATH + "/" + "Moon.cpp", DLLS_FILES_PATH, COMPILER_PATH, SFML_INCLUDE_PATH, SFML_LIB_PATH)

    # Удаление временного файла
    # os.remove(BUILD_FILES_PATH + "/" + "BUILD.cpp")
    # print(f"{Fore.BLUE}Building{Fore.RESET}: Deleting file... {SUCCES}")

    print(f"{Fore.BLUE}Building{Fore.RESET}: Building finished {round(time.time() - start_time, 2)}ms {SUCCES}")
    
    

if __name__ == "__main__":
    build()