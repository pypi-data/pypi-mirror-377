import os
import sys
import shutil
import argparse
import time
from datetime import datetime
try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Заглушки для цветов если colorama не установлена
    class Colors:
        RED = YELLOW = GREEN = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
        LIGHTRED_EX = LIGHTYELLOW_EX = LIGHTGREEN_EX = LIGHTCYAN_EX = LIGHTMAGENTA_EX = ""
    Fore = Back = Style = Colors()

def print_color(text, color=Fore.WHITE, style=Style.NORMAL):
    """Печать текста с цветом и стилем"""
    if COLORAMA_AVAILABLE:
        print(f"{style}{color}{text}{Style.RESET_ALL}")
    else:
        print(text)

def print_header(text):
    """Печать заголовка"""
    if COLORAMA_AVAILABLE:
        print(f"\n{Style.BRIGHT}{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.CYAN}{text:^60}{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    else:
        print(f"\n{'=' * 60}")
        print(f"{text:^60}")
        print(f"{'=' * 60}")

def print_success(text):
    """Печать успешного сообщения"""
    print_color(f"✅ {text}", Fore.GREEN, Style.BRIGHT)

def print_warning(text):
    """Печать предупреждения"""
    print_color(f"⚠  {text}", Fore.YELLOW, Style.BRIGHT)

def print_error(text):
    """Печать ошибки"""
    print_color(f"❌ {text}", Fore.RED, Style.BRIGHT)

def print_info(text):
    """Печать информационного сообщения"""
    print_color(f"ℹ️  {text}", Fore.BLUE)

def print_step(text):
    """Печать шага процесса"""
    print_color(f"➡️  {text}", Fore.MAGENTA, Style.BRIGHT)

def parse_arguments():
    """Разбор аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Скрипт сборки PySGL проекта')
    
    parser.add_argument('source_file', help='Исходный Python-файл для сборки')
    parser.add_argument('--output-name', '-o', default=None, 
                       help='Имя выходного исполняемого файла (без расширения)')
    parser.add_argument('--build-dir', '-b', default='build',
                       help='Временная папка для сборки')
    parser.add_argument('--output-dir', '-d', default=None,
                       help='Куда переместить собранный проект')
    parser.add_argument('--clean', '-c', action='store_true',
                       help='Очистить папку сборки перед началом')
    parser.add_argument('--no-dlls', action='store_true',
                       help='Не копировать DLLs')
    parser.add_argument('--python-path', '-p', default=sys.executable,
                       help='Путь к интерпретатору Python (по умолчанию: текущий)')
    parser.add_argument('--data-dir', default=None,
                       help='Каталог с данными (текстуры и т.д.) для копирования в билд')
    parser.add_argument('--no-console', action='store_true',
                       help='Скрыть консоль при запуске exe-файла (Windows)')
    
    return parser.parse_args()

def show_build_configuration(args):
    """Показать конфигурацию сборки и запросить подтверждение"""
    print_header("КОНФИГУРАЦИЯ СБОРКИ")
    
    config_items = [
        ("Исходный файл", args.source_file),
        ("Выходное имя", args.output_name or os.path.basename(args.source_file).split('.')[0]),
        ("Папка сборки", args.build_dir),
        ("Конечная папка", args.output_dir or args.build_dir),
        ("Очистка", "Да" if args.clean else "Нет"),
        ("Копировать DLLs", "Нет" if args.no_dlls else "Да"),
        ("Python интерпретатор", args.python_path),
        ("Каталог данных", args.data_dir or "Не указан"),
        ("Скрыть консоль", "Да" if args.no_console else "Нет"),
        ("Путь к иконке", ICON_PATH),
        ("Дата сборки", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ]
    
    for key, value in config_items:
        if COLORAMA_AVAILABLE:
            print(f"{Style.BRIGHT}{Fore.CYAN}{key:<20}{Style.RESET_ALL} {Fore.WHITE}{value}{Style.RESET_ALL}")
        else:
            print(f"{key:<20} {value}")
    
    print_color("\n" + "=" * 60, Fore.CYAN, Style.BRIGHT)
    
    response = input(f"{Style.BRIGHT}Начать сборку? (y/N): {Style.RESET_ALL}").strip().lower()
    return response in ['y', 'yes', 'д', 'да']

def prepare_build_environment(args):
    """Подготовка папки сборки"""
    print_step("Подготовка среды сборки...")
    
    if args.clean and os.path.exists(args.build_dir):
        print_info(f"Очистка папки сборки: {args.build_dir}")
        shutil.rmtree(args.build_dir)
    
    if not os.path.exists(args.build_dir):
        print_info(f"Создание папки сборки: {args.build_dir}")
        os.makedirs(args.build_dir)
    else:
        print_info(f"Использование существующей папки: {args.build_dir}")

def copy_data_directory(args):
    """Копирование каталога данных в папку сборки"""
    if args.data_dir and os.path.exists(args.data_dir):
        data_dst = os.path.join(args.build_dir, os.path.basename(args.data_dir))
        if os.path.exists(data_dst):
            print_info(f"Очистка существующего каталога данных: {data_dst}")
            shutil.rmtree(data_dst)
        
        print_step(f"Копирование данных из {args.data_dir}...")
        shutil.copytree(args.data_dir, data_dst)
        print_success(f"Каталог данных скопирован: {data_dst}")
    elif args.data_dir:
        print_warning(f"Каталог данных не найден: {args.data_dir}")

def copy_icon_to_build(args):
    """Копирование иконки в папку сборки"""
    icons_dir = os.path.join(args.build_dir, "icons")
    
    # Создаем папку icons если ее нет
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    # Копируем иконку
    if os.path.exists(ICON_PATH):
        icon_filename = os.path.basename(ICON_PATH)
        icon_dst = os.path.join(icons_dir, icon_filename)
        
        print_step(f"Копирование иконки: {icon_filename}")
        shutil.copy2(ICON_PATH, icon_dst)
        print_success(f"Иконка скопирована: {icon_dst}")
        return icon_dst
    else:
        print_warning(f"Исходная иконка не найдена: {ICON_PATH}")
        return None

def build_project(args):
    """Запуск сборки через Nuitka"""
    python_path = args.python_path
    source_file = args.source_file
    output_name = args.output_name or os.path.basename(source_file).split('.')[0]
    
    # Базовые параметры сборки
    build_params = [
        f'"{python_path}" -m nuitka',
        source_file,
        '--onefile',
        '--standalone',
        '--verbose',
        f'--remove-output',
        f'--show-progress',
        f'--windows-icon-from-ico={ICON_PATH}',
        f'--output-filename={output_name}.exe'
    ]
    
    # Добавляем параметр для скрытия консоли если указан флаг
    if args.no_console:
        build_params.append('--windows-console-mode=disable')
        print_info("Режим сборки: БЕЗ КОНСОЛИ (окно консоли не будет отображаться)")
    else:
        print_info("Режим сборки: С КОНСОЛЬЮ (окно консоли будет отображаться)")
    
    build_command = ' '.join(build_params)
    
    print_header("ЗАПУСК NUITKA СБОРКИ")
    print_info(f"Команда сборки: {build_command}")
    print_step(f"Сборка {source_file}...")
    
    start_time = time.time()
    exit_code = os.system(build_command)
    build_time = time.time() - start_time
    
    if exit_code != 0:
        raise RuntimeError(f"Ошибка сборки Nuitka (код {exit_code})")
    
    print_success(f"Nuitka сборка завершена за {build_time:.2f} секунд")

def finalize_build(args):
    """Перенос собранных файлов в финальную папку"""
    print_header("ФИНАЛИЗАЦИЯ СБОРКИ")
    
    output_name = args.output_name or os.path.basename(args.source_file).split('.')[0]
    exe_file = f"{output_name}.exe"
    
    # Копирование иконки
    copy_icon_to_build(args)
    
    # Копирование DLLs (если не отключено)
    if not args.no_dlls:
        dlls_src = "Moon/dlls"
        dlls_dst = os.path.join(args.build_dir, "dlls")
        if os.path.exists(dlls_src):
            if os.path.exists(dlls_dst):
                print_info(f"Очистка существующих DLLs: {dlls_dst}")
                shutil.rmtree(dlls_dst)
            
            print_step("Копирование DLLs...")
            shutil.copytree(dlls_src, dlls_dst)
            print_success(f"DLLs скопированы: {dlls_dst}")
        else:
            print_warning(f"Папка DLLs не найдена: {dlls_src}")
    
    # Копирование каталога данных
    copy_data_directory(args)
    
    # Перенос .exe в папку сборки
    if os.path.exists(exe_file):
        print_step(f"Перенос исполняемого файла: {exe_file}")
        shutil.move(exe_file, os.path.join(args.build_dir, exe_file))
        print_success(f"Исполняемый файл перемещен в: {os.path.join(args.build_dir, exe_file)}")
    else:
        raise FileNotFoundError(f"Собранный файл {exe_file} не найден")
    
    # Перенос в финальную папку (если указана)
    if args.output_dir:
        final_dir = os.path.join(args.output_dir, f"build.{output_name}")
        if os.path.exists(final_dir):
            print_info(f"Очистка существующей конечной папки: {final_dir}")
            shutil.rmtree(final_dir)
        
        print_step(f"Перенос в конечную папку: {final_dir}")
        shutil.move(args.build_dir, final_dir)
        print_success(f"Сборка завершена! Результат: {final_dir}")
        return final_dir
    else:
        print_success(f"Сборка завершена! Результат: {args.build_dir}")
        return args.build_dir

ICON_PATH = "Moon\data\icons\default_app_icon.png"

def main():
    start_time = time.time()
    
    try:
        if not COLORAMA_AVAILABLE:
            print_warning("Colorama не установлена. Установите: pip install colorama")
        print(Fore.BLUE,'''                                                          
                                                     
                  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                  
              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓              
            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓            
         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓         
        ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓        
       ▓▓▓▓▓▓▓▓▓▓▓██▓▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓       
      ▓▓▓▓▓▓▓▓▓▓██▓▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      
      ▓▓▓▓▓▓▓▓▓██▓▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      
      ▓▓▓▓▓▓▓▓▓██▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓█▓▒▓▓▓▓▓▓▓▓▓▓▓      
      ▓▓▓▓▓▓▓▓▓███▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓      
      ▓▓▓▓▓▓▓▓▓▓▓██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓      
       ▓▓▓▓▓▓▓▓▓▓▓▓██▓▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓       
        ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓        
         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓         
            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓            
              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓              
                  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                  
                                                     
                         MOON     
                   (by Pavlov Ivan)                                           
                                                          ''', Fore.RESET)
        print_header("MOON BUILD SYSTEM")
        print_info(f"Запуск сборки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        args = parse_arguments()
        
        # Показать конфигурацию и запросить подтверждение
        if not show_build_configuration(args):
            print_error("Сборка отменена пользователем")
            sys.exit(0)
            
        prepare_build_environment(args)
        build_project(args)
        result_dir = finalize_build(args)
        
        total_time = time.time() - start_time
        minutes, seconds = divmod(total_time, 60)
        
        print_header("СБОРКА УСПЕШНО ЗАВЕРШЕНА! 🎉")
        print_success(f"Время сборки: {int(minutes)} мин {seconds:.2f} сек")
        print_success(f"Итоговый каталог: {result_dir}")
        
        if args.no_console:
            print_info("ℹ️  Собранный exe-файл будет запускаться БЕЗ отображения консоли")
        else:
            print_info("ℹ️  Собранный exe-файл будет запускаться С отображением консоли")
        
        if COLORAMA_AVAILABLE:
            print(f"\n{Style.BRIGHT}{Fore.GREEN}🚀 Готово! Ваше приложение собрано и готово к использованию!{Style.RESET_ALL}")
        else:
            print("\n🚀 Готово! Ваше приложение собрано и готово к использованию!")
            
    except Exception as e:
        total_time = time.time() - start_time
        print_error(f"Ошибка во время сборки: {str(e)}")
        print_error(f"Общее время до ошибки: {total_time:.2f} секунд")
        if COLORAMA_AVAILABLE:
            print(f"{Style.BRIGHT}{Fore.RED}❌ Сборка прервана из-за ошибки!{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()