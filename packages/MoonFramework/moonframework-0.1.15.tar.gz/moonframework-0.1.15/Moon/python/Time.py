"""
#### *Модуль работы со временем в Moon*

---

##### Версия: 1.0.3

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 100% 

---

✓ Высокоточные таймеры:
  - Наносекундная точность (Clock)
  - Кроссплатформенная реализация
  - Минимальные накладные расходы

✓ Гибкие интервальные таймеры:
  - Именованные таймеры
  - Глобальный менеджер таймеров
  - Автоматическое создание/управление

✓ Удобные утилиты:
  - Декораторы для ограничения частоты
  - Генераторы временных интервалов
  - Функции отложенного вызова

✓ Оптимизированные алгоритмы:
  - Минимальное потребление CPU
  - Эффективное управление ресурсами
  - Быстрый доступ к таймерам

---

:Features:

• Clock - высокоточный таймер на C++ (через DLL)

• Timer - простой интервальный таймер

• Глобальный менеджер таймеров (TIMER_BUFFER)

• Декоратор @throttle для ограничения частоты вызовов

• Генератор every() для периодических операций

• Функция wait_call() для отложенного выполнения

---

:Requires:

• Python 3.8+

• Стандартная библиотека time

• Стандартная библиотека typing

• Нативная библиотека Moon.dll

---

== Лицензия MIT ==================================================

[MIT License]
Copyright (c) 2025 Pavlov Ivan

Данная лицензия разрешает лицам, получившим копию данного программного обеспечения 
и сопутствующей документации (в дальнейшем именуемыми «Программное Обеспечение»), 
безвозмездно использовать Программное Обеспечение без ограничений, включая неограниченное 
право на использование, копирование, изменение, слияние, публикацию, распространение, 
сублицензирование и/или продажу копий Программного Обеспечения, а также лицам, которым 
предоставляется данное Программное Обеспечение, при соблюдении следующих условий:

[ Уведомление об авторском праве и данные условия должны быть включены во все копии ]
[                 или значительные части Программного Обеспечения.                  ]

ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ, ЯВНО 
ВЫРАЖЕННЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ГАРАНТИЯМИ ТОВАРНОЙ 
ПРИГОДНОСТИ, СООТВЕТСТВИЯ ПО ЕГО КОНКРЕТНОМУ НАЗНАЧЕНИЮ И ОТСУТСТВИЯ НАРУШЕНИЙ ПРАВ. 
НИ В КАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ НЕ НЕСУТ ОТВЕТСТВЕННОСТИ ПО ИСКАМ О 
ВОЗМЕЩЕНИИ УЩЕРБА, УБЫТКОВ ИЛИ ДРУГИХ ТРЕБОВАНИЙ ПО ДЕЙСТВУЮЩЕМУ ПРАВУ ИЛИ ИНОМУ, 
ВОЗНИКШИМ ИЗ, ИМЕЮЩИМ ПРИЧИНОЙ ИЛИ СВЯЗАННЫМ С ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ИЛИ 
ИСПОЛЬЗОВАНИЕМ ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ ИЛИ ИНЫМИ ДЕЙСТВИЯМИ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ.
"""

import os
import ctypes

from time import time
from typing import Generator, Final

from Moon.python.utils import find_library, LibraryLoadError
from Moon.python.Types import OptionalIdentifier, Identifier, FunctionOrMethod

# Загружаем DLL библиотеку
try:
    LIB_MOON = ctypes.CDLL(find_library())
except Exception as e:
    raise ImportError(f"Failed to load Moon library: {e}")


LIB_MOON.createClock.argtypes = [] 
LIB_MOON.createClock.restype = ctypes.c_void_p  
LIB_MOON.clockRestart.argtypes = [ctypes.c_void_p] 
LIB_MOON.clockRestart.restype = None  
LIB_MOON.getClockElapsedTime.argtypes = [ctypes.c_void_p] 
LIB_MOON.getClockElapsedTime.restype = ctypes.c_double  


class Clock:
    """
    Высокоточный таймер на основе C++ реализации из DLL.
    
    Используется для измерения временных интервалов с максимальной точностью.
    Особенно полезен для:
    - Измерения времени рендеринга кадров
    - Профилирования производительности
    - Синхронизации игрового цикла
    """
    
    def __init__(self):
        """
        Инициализирует новый экземпляр таймера.
        Создает внутренний таймер в DLL.
        """
        self.__clock_ptr = LIB_MOON.createClock()  # Указатель на C++ объект таймера

    def restart(self) -> None:
        """
        Сбрасывает и немедленно перезапускает таймер.
        Обнуляет счетчик прошедшего времени.
        """
        LIB_MOON.clockRestart(self.__clock_ptr)

    def get_elapsed_time(self) -> float:
        """
        Возвращает время в секундах, прошедшее с последнего вызова restart().
        
        Возвращает:
            float: Количество секунд с высокой точностью (дробное число)
        """
        return LIB_MOON.getClockElapsedTime(self.__clock_ptr)


class Timer:
    """
    Простой таймер на основе системного времени.
    
    Позволяет проверять, истек ли заданный временной интервал.
    Полезен для:
    - Периодического выполнения действий
    - Ограничения частоты обновлений
    - Реализации задержек
    """
    
    def __init__(self, name: OptionalIdentifier = 'dummy', wait_time: float = 1):
        """
        Создает новый таймер с указанным именем и интервалом.
        
        Аргументы:
            name (str): Уникальное имя для идентификации таймера
            wait_time (float): Интервал срабатывания в секундах
        """
        self.__name = name
        self.__wait_time = wait_time
        self.__saved_time = time()  # Запоминаем текущее время
        self.__delta: float = 0

    def get_name(self) -> OptionalIdentifier:
        """
        Возвращает имя таймера.
        
        Возвращает:
            str: Текущее имя таймера
        """
        return self.__name
    
    def set_name(self, name: Identifier) -> None:
        """
        Устанавливает новое имя таймера.
        
        Аргументы:
            name (str): Новое имя таймера
        """
        self.__name = name
        

    def get_wait_time(self) -> float:
        """
        Возвращает текущий установленный интервал срабатывания.
        
        Возвращает:
            float: Интервал в секундах
        """
        return self.__wait_time
    
    def set_wait_time(self, time: float) -> None:
        """
        Устанавливает новый интервал срабатывания.
        
        Аргументы:
            time (float): Новый интервал в секундах
        """
        self.__wait_time = time

    def timing(self) -> bool:
        """
        Проверяет, истек ли установленный интервал.
        Если интервал истек, сбрасывает таймер.
        
        Возвращает:
            bool: True если интервал истек, False если нет
        """
        self.__delta = time() - self.__saved_time  # Вычисляем прошедшее время
        if self.__delta >= self.__wait_time:
            self.__saved_time = time()  # Сбрасываем таймер
            return True
        return False
    
    def get_delta(self) -> float:
        return self.__delta


# Глобальный буфер для хранения именованных таймеров ========= +
TIMER_BUFFER: Final[dict[OptionalIdentifier, Timer]] = {}      #
# ============================================================ +

def wait(timer_name: OptionalIdentifier = 'dummy', wait_time: float = 0) -> bool:
    """
    Удобная обертка для работы с глобальными таймерами.
    Создает таймер при первом вызове, затем проверяет его состояние.
    
    Аргументы:
        timer_name (str): Имя таймера (по умолчанию "dummy")
        wait_time (float): Интервал срабатывания в секундах (по умолчанию 0)
        
    Возвращает:
        bool: True если интервал истек, False если нет
    """
    if timer_name not in TIMER_BUFFER:
        # Создаем новый таймер если он не существует
        TIMER_BUFFER[timer_name] = Timer(timer_name, wait_time)
    return TIMER_BUFFER[timer_name].timing()
    
def wait_call(timer_name: OptionalIdentifier, wait_time: float, func: FunctionOrMethod, *args, **kvargs) -> None:
    """
    Вызывает функцию только если истек указанный интервал для заданного таймера.
    
    Аргументы:
        timer_name (str): Имя таймера
        wait_time (float): Интервал между вызовами в секундах
        func (callable): Функция для вызова
        *args: Позиционные аргументы для функции
        **kvargs: Именованные аргументы для функции
    """
    if wait(timer_name, wait_time):
        func(*args, **kvargs)


# Мощный, но не очень то уж и полезный декоратор (используйте с умом)
def throttle(wait_time: float):
    """
    Декоратор для ограничения частоты вызовов функции
    
    Аргументы:
        wait_time (float): Минимальный интервал между вызовами в секундах
    """
    def decorator(func: FunctionOrMethod):
        last_called = 0
        
        def wrapper(*args, **kwargs):
            nonlocal last_called
            current_time = time()
            if current_time - last_called >= wait_time:
                last_called = current_time
                return func(*args, **kwargs)
        return wrapper
    return decorator

def every(interval: float) -> Generator[bool]:
    """
    Возвращает генератор, который возвращает True каждые interval секунд
    
    Аргументы:
        interval (float): Интервал в секундах
        
    Пример:
    for ready in every(1.0):
        if ready:
            print("Прошла секунда")
    """
    last_time = time()
    while True:
        current_time = time()
        if current_time - last_time >= interval:
            last_time = current_time
            yield True
        else:
            yield False