"""
#### *Модуль обработки ввода в Moon*

---

##### Версия: 1.0.3

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 100% 

---

✓ Полноценная обработка ввода мыши:
  - Определение позиции (экран/окно)
  - Отслеживание кликов и нажатий
  - Расчет скорости движения

✓ Комплексная работа с клавиатурой:
  - Определение нажатий клавиш
  - Поддержка комбинаций клавиш
  - Отслеживание "кликов" клавиш

✓ Гибкая система событий:
  - Подписка на события ввода
  - Менеджер событий с callback-функциями
  - Фильтрация и обработка событий

✓ Готовые интерфейсы:
  - MouseInterface - предварительно настроенный объект мыши
  - KeyBoardInterface - готовый объект клавиатуры

---

:Requires:

• Python 3.8+

• Библиотека keyboard (для обработки клавиатуры)

• Библиотека ctypes (для работы с DLL)

• Moon.dll (нативная библиотека обработки ввода)

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
ВОЗНИКШИМ ИЗ, ИМЕЮЩИМ ПРИЧИНОЙ ИЛИ СВЯЗАННЫМ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ ИЛИ 
ИСПОЛЬЗОВАНИЕМ ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ ИЛИ ИНЫМИ ДЕЙСТВИЯМИ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ.
"""

import ctypes
import keyboard

from enum import Enum
from typing import Any, Callable, Literal, Final, final, Optional, Union, Set, Dict

from Moon.python.Types import Self
from Moon.python.Vectors import Vector2i  # Векторные операции для позиций
from Moon.python.utils import find_library, LibraryLoadError

from functools import lru_cache


# ==================== КЛАССЫ ОШИБОК ====================
class InputError(Exception):
    """Базовый класс для всех ошибок модуля ввода"""
    pass

class InvalidInputError(InputError):
    """Некорректные параметры ввода"""
    pass

# ==================== НАТИВНЫЕ ФУНКЦИИ ====================
# Загрузка библиотеки
try:
    _lib = ctypes.CDLL(find_library())
except Exception as e:
    raise LibraryLoadError(f"Failed to load Moon library: {e}")

# Проверка наличия обязательных функций
REQUIRED_FUNCTIONS = [
    'IsKeyPressed', 'IsMouseButtonPressed',
    'GetMousePositionX', 'GetMousePositionY',
    'GetMousePositionXWindow', 'GetMousePositionYWindow'
]


for func in REQUIRED_FUNCTIONS:
    if not hasattr(_lib, func):
        raise LibraryLoadError(f"Required function {func} not found in library")

# ==================== C/C++ БИНДИНГИ ====================
@final
def is_key_pressed(key: Union[int, str]) -> bool:
    """
    #### Проверяет нажатие клавиши через нативную библиотеку

    ---
    
    :Arguments:
        key: Код клавиши (int) или символ (str)
        
    ---

    :Returns:
        bool: Нажата ли клавиша
        
    ---

    :Raises:
        InvalidInputError: Некорректный формат клавиши
        InputError: Ошибка при проверке состояния
    """
    # Конвертация строки в код символа
    if isinstance(key, str):
        if len(key) != 1:
            raise InvalidInputError("Key symbol must be a single character")
        key = ord(key)
    elif not isinstance(key, int):
        raise InvalidInputError("Key must be either int (keycode) or str (single character)")
    
    try:
        # Настройка и вызов нативной функции
        _lib.IsKeyPressed.restype = ctypes.c_bool
        _lib.IsKeyPressed.argtypes = [ctypes.c_int]
        return _lib.IsKeyPressed(key)
    except Exception as e:
        raise InputError(f"Key press check failed: {e}")

@final
def is_mouse_button_pressed(button: int) -> bool:
    """
    #### Проверяет нажатие кнопки мыши
    
    ---
    
    :Arguments:
        button: Номер кнопки (0-левая, 1-правая, 2-средняя)
        
    ---
    
    :Returns:
        bool: Нажата ли кнопка
        
    ---
    
    :Raises:
        InvalidInputError: Некорректный номер кнопки
        InputError: Ошибка при проверке состояния
    """
    if not isinstance(button, int) or button < 0 or button > 2:
        raise InvalidInputError("Mouse button must be integer 0-2")
    
    try:
        _lib.IsMouseButtonPressed.restype = ctypes.c_bool
        _lib.IsMouseButtonPressed.argtypes = [ctypes.c_int]
        return _lib.IsMouseButtonPressed(button)
    except Exception as e:
        raise InputError(f"Mouse button check failed: {e}")

@final
def get_mouse_position() -> Vector2i:
    """
    #### Получает текущую позицию курсора на экране
    
    ---
    
    :Returns:
        Vector2i: Позиция (x, y) в пикселях
        
    ---
    
    :Raises:
        InputError: Ошибка при получении позиции
    """
    try:
        _lib.GetMousePositionX.restype = ctypes.c_int
        _lib.GetMousePositionY.restype = ctypes.c_int
        return Vector2i(_lib.GetMousePositionX(), _lib.GetMousePositionY())
    except Exception as e:
        raise InputError(f"Failed to get mouse position: {e}")

@final
def get_mouse_position_in_window(window: Any) -> Vector2i:
    """
    #### Получает позицию курсора относительно окна
    
    ---
    
    :Arguments:
        window: Объект окна с методом get_ptr()
        
    ---
    
    :Returns:
        Vector2i: Позиция (x, y) относительно окна
        
    ---
    
    :Raises:
        InvalidInputError: Некорректный объект окна
        InputError: Ошибка при получении позиции
    """
    if not hasattr(window, 'get_ptr'):
        raise InvalidInputError("Window object must have get_ptr() method")
    
    try:
        window_ptr = window.get_ptr()
        if not isinstance(window_ptr, int):
            raise InvalidInputError("Window pointer must be integer")
            
        _lib.GetMousePositionXWindow.restype = ctypes.c_int
        _lib.GetMousePositionYWindow.restype = ctypes.c_int
        _lib.GetMousePositionXWindow.argtypes = [ctypes.c_void_p]
        _lib.GetMousePositionYWindow.argtypes = [ctypes.c_void_p]
        
        x = _lib.GetMousePositionXWindow(window_ptr)
        y = _lib.GetMousePositionYWindow(window_ptr)
        return Vector2i(x, y)
    except Exception as e:
        raise InputError(f"Failed to get window mouse position: {e}")

# ==================== КЛАССЫ ВВОДА ====================
@final
class MouseButtons(Enum):
    """Перечисление кнопок мыши"""
    LEFT = 0    # Левая кнопка
    RIGHT = 1   # Правая кнопка
    MIDDLE = 2  # Средняя кнопка (колесо)

@final
def convert_mouse_button(button: Union[Literal["left", "right", "middle"], MouseButtons]) -> int:
    """
    #### Конвертирует кнопку мыши в числовой код
    
    ---
    
    :Arguments:
        button: Название кнопки или элемент MouseButtons
        
    ---
    
    :Returns:
        int: Числовой код кнопки
        
    ---
    
    :Raises:
        InvalidInputError: Некорректное название кнопки
    """
    if isinstance(button, MouseButtons):
        return button.value
    elif isinstance(button, str):
        button = button.lower()
        if button == "left": return 0
        elif button == "right": return 1
        elif button == "middle": return 2
    
    raise InvalidInputError(
        f"Invalid mouse button: {button}. Expected 'left', 'right', 'middle' or MouseButtons enum"
    )

@final
class Mouse:
    """
    Основной класс для работы с мышью
    
    Предоставляет:
    - Проверку нажатий кнопок
    - Отслеживание кликов
    - Получение позиции курсора
    - Расчет скорости движения
    """
    
    Buttons = MouseButtons  # Доступ к перечислению кнопок
    
    def __init__(self):
        """Инициализация состояния мыши"""
        self._last_click_state = {
            "left": False,   # Состояние левой кнопки в предыдущем кадре
            "right": False, # Состояние правой кнопки
            "middle": False # Состояние средней кнопки
        }
        self._last_position = get_mouse_position()  # Позиция в предыдущем кадре

    @classmethod
    def get_press(cls, button: Union[Literal["left", "right", "middle"], MouseButtons]) -> bool:
        """
        #### Проверяет, нажата ли кнопка мыши в текущий момент
        
        ---
        
        :Arguments:
            button: Кнопка для проверки
            
        ---
        
        :Returns:
            bool: Нажата ли кнопка
        """
        return is_mouse_button_pressed(convert_mouse_button(button))
    
    def in_window(self, window) -> bool:
        mouse_position = self.get_position()
        window_pos = window.get_position()
        window_size = window.get_size()

        if (window_pos.x <= mouse_position.x <= window_pos.x + window_size.x and
            window_pos.y <= mouse_position.y <= window_pos.y + window_size.y):
            return True
        return False

    
    def get_click(self, button: Union[Literal["left", "right", "middle"], MouseButtons]) -> bool:
        """
        #### Проверяет, была ли кнопка только что нажата (в этом кадре)
        
        ---
        
        :Arguments:
            button: Кнопка для проверки
            
        ---
        
        :Returns:
            bool: Был ли клик
            
        ---
        
        :Raises:
            InputError: Ошибка при проверке состояния
        """
        try:
            current_state = self.get_press(button)
            button_name = button if isinstance(button, str) else button.name.lower()
            
            # Если кнопка нажата сейчас, но не была нажата в прошлом кадре
            if current_state and not self._last_click_state[button_name]:
                self._last_click_state[button_name] = True
                return True
            elif not current_state:
                self._last_click_state[button_name] = False
            return False
        except Exception as e:
            raise InputError(f"Failed to get mouse click: {e}")
        
    def get_release(self, button: Union[Literal["left", "right", "middle"], MouseButtons]) -> bool:
        """
        #### Проверяет, была ли кнопка только что отпущена
        
        ---
        
        :Arguments:
            button: Кнопка для проверки
            
        ---
        
        :Returns:
            bool: Был ли отпуск
        
        ---
        
        :Raises:
            InputError: Ошибка при проверке состояния
        """
        try:
            current_state = self.get_press(button)
            button_name = button if isinstance(button, str) else button.name.lower()

            # Если кнопка не нажата сейчас, но была нажата в прошлом кадре
            if not current_state and self._last_click_state[button_name]:
                self._last_click_state[button_name] = False
                return True
            elif current_state:
                self._last_click_state[button_name] = True
            return False
        except Exception as e:
            raise InputError(f"Failed to get mouse release: {e}")

        

    @classmethod
    def get_position_in_window(cls, window: Any) -> Vector2i:
        """
        #### Получает позицию курсора относительно окна
        
        ---
        
        :Arguments:
            window: Объект окна
            
        ---
        
        :Returns:
            Vector2i: Позиция относительно окна
        """
        return get_mouse_position_in_window(window)
    
    def get_speed(self) -> Vector2i:
        """
        #### Рассчитывает скорость движения мыши (пикселей/кадр)
        
        ---
        
        :Returns:
            Vector2i: Вектор скорости (dx, dy)
            
        ---
        
        :Raises:
            InputError: Ошибка при расчете скорости
        """
        try:
            current_pos = get_mouse_position()
            speed = current_pos - self._last_position
            self._last_position = current_pos
            return speed
        except Exception as e:
            raise InputError(f"Failed to calculate mouse speed: {e}")
    
    @classmethod
    def get_position(cls) -> Vector2i:
        """
        #### Получает абсолютную позицию курсора на экране
        
        ---
        
        :Returns:
            Vector2i: Позиция (x, y)
        """
        return get_mouse_position()

# ////////////////////////////////////////////////////////////////////////////
# Глобальный экземпляр интерфейса мыши
# Используется для удобства, чтобы не создавать экземпляр класса каждый раз
MouseInterface: Final[Mouse] = Mouse()
# ////////////////////////////////////////////////////////////////////////////

@final
class Keyboard:
    """
    Оптимизированный класс для работы с клавиатурой
    
    Предоставляет:
    - Проверку нажатий клавиш
    - Отслеживание кликов клавиш
    - Работу с комбинациями клавиш
    """
    
    # Поддерживаемые клавиши с быстрым доступом
    KEYS_ARRAY: Final[list[str]] = [
        # Буквы
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "а", "б", "в","г","д","е","ё","ж","з","и","й","к","л","м","н","о","п","р","с","т","у","ф","х","ц","ч","щ","ъ","ь","э","ю","я",
        # Цифры
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        # Функциональные клавиши
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
        # Клавиши управления
        "up", "down", "left", "right",
        # Специальные клавиши
        "esc", "enter", "space", "backspace", "tab", "capslock", 
        "shift", "ctrl", "alt", "win", "menu", "pause",
        # Символы
        "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "=", "-"
        "`", "~", "{", "}", "[", "]", "|", ":", "\"", "<", ">", "?", "/", ".", ","
    ]
    
    # Кэш для быстрого доступа к нормализованным комбинациям
    _COMBINATION_CACHE: Dict[str, Set[str]] = {}
    _PRESSED_KEYS_CACHE: Set[str] = set()
    _LAST_UPDATE_TIME: float = 0
    _CACHE_TTL: float = 0.01  # 10ms кэширование

    def __init__(self):
        """Инициализация состояния клавиатуры"""
        self._last_click_state: Dict[str, bool] = {}
        self._last_pressed_keys: Set[str] = set()
        self._last_combination_state: Dict[str, bool] = {}

    @classmethod
    def _update_pressed_cache(cls) -> None:
        """
        #### Обновляет кэш нажатых клавиш с ограничением по времени
        
        ---
        
        :Raises:
            InputError: Ошибка при обновлении кэша
        """
        import time
        current_time = time.time()
        
        if current_time - cls._LAST_UPDATE_TIME > cls._CACHE_TTL:
            try:
                cls._PRESSED_KEYS_CACHE.clear()
                for key in cls.KEYS_ARRAY:
                    try:
                        if keyboard.is_pressed(key):
                            cls._PRESSED_KEYS_CACHE.add(key)
                    except: ...
                cls._LAST_UPDATE_TIME = current_time
            except Exception as e:
                raise InputError(f"Failed to update pressed keys cache: {e}")

    @classmethod
    def get_press(cls, keys: str) -> bool:
        """
        #### Проверяет, нажата ли клавиша/комбинация (оптимизированная версия)
        
        ---
        
        :Arguments:
            keys: Клавиша или комбинация (например "ctrl+c")
            
        ---
        
        :Returns:
            bool: Нажата ли клавиша
            
        ---
        
        :Raises:
            InvalidInputError: Некорректный формат клавиши
            InputError: Ошибка при проверке состояния
        """
        if not isinstance(keys, str):
            raise InvalidInputError("Keys must be a string")
        
        # Для одиночных клавиш используем быструю проверку
        if '+' not in keys:
            cls._update_pressed_cache()
            return keys.lower() in cls._PRESSED_KEYS_CACHE
        
        # Для комбинаций используем оптимизированный метод
        return cls.get_press_combination(keys)

    def get_click(self, keys: str) -> bool:
        """
        #### Проверяет, была ли клавиша только что нажата (оптимизированная версия)
        
        ---
        
        :Arguments:
            keys: Клавиша для проверки
            
        ---
        
        :Returns:
            bool: Был ли клик
            
        ---
        
        :Raises:
            InputError: Ошибка при проверке состояния
        """
        try:
            current_state = self.get_press(keys)
            
            # Быстрая проверка состояния через локальный кэш
            was_pressed = self._last_click_state.get(keys, False)
            
            if current_state and not was_pressed:
                self._last_click_state[keys] = True
                return True
            elif not current_state:
                self._last_click_state[keys] = False
            
            return False
        except Exception as e:
            raise InputError(f"Failed to get key click: {e}")

    @classmethod
    @lru_cache(maxsize=128)
    def _normalize_combination(cls, keys: str) -> Set[str]:
        """
        #### Нормализует и кэширует комбинацию клавиш
        
        ---
        
        :Arguments:
            keys: Комбинация клавиш для нормализации
            
        ---
        
        :Returns:
            Set[str]: Нормализованное множество клавиш
        """
        return set(key.strip().lower() for key in keys.split('+'))

    @classmethod
    def get_press_combination(cls, keys: str) -> bool:
        """
        #### Оптимизированная проверка комбинации клавиш
        
        ---
        
        :Arguments:
            keys: Комбинация клавиш через "+" (например "ctrl+shift+c")
            
        ---
        
        :Returns:
            bool: Нажата ли комбинация
            
        ---
        
        :Raises:
            InvalidInputError: Некорректный формат комбинации
            InputError: Ошибка при проверке состояния
        """
        if not isinstance(keys, str) or '+' not in keys:
            raise InvalidInputError("Key combination must be string with '+' separator")
        
        try:
            # Используем кэшированную нормализацию
            keys_set = cls._normalize_combination(keys)
            
            # Обновляем кэш нажатых клавиш
            cls._update_pressed_cache()
            
            # Быстрая проверка подмножества
            return keys_set.issubset(cls._PRESSED_KEYS_CACHE)
        except Exception as e:
            raise InputError(f"Failed to check key combination: {e}")

    def get_click_combination(self, keys: str) -> bool:
        """
        #### Проверяет, была ли комбинация только что нажата (оптимизированная версия)
        
        ---
        
        :Arguments:
            keys: Комбинация клавиш
            
        ---
        
        :Returns:
            bool: Была ли нажата комбинация
            
        ---
        
        :Raises:
            InputError: Ошибка при проверке состояния
        """
        try:
            current_state = self.get_press_combination(keys)
            was_pressed = self._last_combination_state.get(keys, False)
            
            if current_state and not was_pressed:
                self._last_combination_state[keys] = True
                return True
            elif not current_state:
                self._last_combination_state[keys] = False
            
            return False
        except Exception as e:
            raise InputError(f"Failed to get combination click: {e}")

    @classmethod
    def get_pressed_keys(cls) -> list[str]:
        """
        #### Оптимизированное получение списка нажатых клавиш
        
        ---
        
        :Returns:
            list[str]: Список нажатых клавиш
            
        ---
        
        :Raises:
            InputError: Ошибка при получении состояния
        """
        cls._update_pressed_cache()
        return list(cls._PRESSED_KEYS_CACHE)

    def update_frame(self) -> None:
        """
        #### Метод для обновления состояния в конце кадра
        (опционально, для ручного управления кэшем)
        """
        self._update_pressed_cache()

    def clear_cache(self) -> None:
        """
        #### Очищает внутренние кэши
        """
        self._last_click_state.clear()
        self._last_combination_state.clear()
        self._normalize_combination.cache_clear()
        self._PRESSED_KEYS_CACHE.clear()

# ////////////////////////////////////////////////////////////////////////////
# Глобальный экземпляр интерфейса клавиатуры
# Используется для удобства, чтобы не создавать экземпляр класса каждый раз
KeyBoardInterface: Final[Keyboard] = Keyboard()
# ////////////////////////////////////////////////////////////////////////////

# ==================== МЕНЕДЖЕР СОБЫТИЙ ====================
@final
class InputEventsManager:
    """
    Менеджер событий ввода
    
    Позволяет:
    - Создавать слушатели событий ввода
    - Управлять подписками на события
    - Обрабатывать события через callback-функции
    """
    
    class EventType(Enum):
        """Типы событий ввода"""
        MOUSE_CLICK = 0    # Клик кнопки мыши
        MOUSE_PRESS = 1    # Удержание кнопки мыши
        KEYBOARD_CLICK = 2 # Нажатие клавиши
        KEYBOARD_PRESS = 3 # Удержание клавиши

    def __init__(self):
        """Инициализация менеджера событий"""
        self.__listened_objects: list[dict] = []  # Список слушателей
        self.__events: list[dict] = []            # Текущие события

    def add_mouse_listener(
        self, 
        event_type: EventType, 
        button: Union[Literal["left", "right", "middle"], MouseButtons], 
        listener_id: Optional[Union[int, str]] = None
    ) -> Self:
        """
        #### Добавляет слушатель событий мыши
        
        ---
        
        :Arguments:
        - event_type: Тип события (клик/удержание)
        - button: Кнопка мыши
        - listener_id: Уникальный идентификатор слушателя
            
        ---
        
        :Returns:
            InputEventsManager: self для цепочки вызовов
            
        ---
        
        :Raises:
            InvalidInputError: Некорректный тип события
        """
        if not isinstance(event_type, self.EventType):
            raise InvalidInputError("Invalid event type")
            
        self.__listened_objects.append({
            "type": event_type,
            "listener": Mouse(),
            "button": button,
            "id": listener_id or len(self.__listened_objects)
        })
        return self

    def add_keyboard_listener(
        self, 
        event_type: EventType, 
        keys: str, 
        listener_id: Optional[Union[int, str]] = None
    ) -> Self:
        """
        #### Добавляет слушатель событий клавиатуры
        
        ---
        
        :Arguments:
        - event_type: Тип события (клик/удержание)
        - keys: Клавиша или комбинация
        - listener_id: Уникальный идентификатор слушателя
            
        ---
        
        :Returns:
            InputEventsManager: self для цепочки вызовов
            
        ---
        
        :Raises:
            InvalidInputError: Некорректный тип события или клавиши
        """
        if not isinstance(event_type, self.EventType):
            raise InvalidInputError("Invalid event type")
        if not isinstance(keys, str):
            raise InvalidInputError("Keys must be string")
            
        self.__listened_objects.append({
            "type": event_type,
            "listener": Keyboard(),
            "keys": keys,
            "id": listener_id or len(self.__listened_objects)
        })
        return self
    
    def remove_listener(self, listener_id: Union[int, str]) -> None:
        """
        #### Удаляет слушатель по идентификатору
        
        ---
        
        :Arguments:
            listener_id: Идентификатор слушателя
            
        ---
        
        :Raises:
            ValueError: Слушатель не найден
        """
        for i, listener in enumerate(self.__listened_objects):
            if listener["id"] == listener_id:
                self.__listened_objects.pop(i)
                return
        raise ValueError(f"Listener with id '{listener_id}' not found")

    def remove_all_listeners(self) -> None:
        """Удаляет все слушатели"""
        self.__listened_objects.clear()

    def present_call(
        self, 
        listener_id: Union[int, str], 
        callback: Callable, 
        *args, 
        **kwargs
    ) -> None:
        """
        #### Вызывает callback-функцию при наступлении события

        Необходимо вызывать непосредственно в цикле
        
        ---
        
        :Arguments:
        - listener_id: Идентификатор слушателя
        - callback: Функция для вызова
        - args: Позиционные аргументы
        - kwargs: Именованные аргументы
            
        ---
        
        :Raises:
            InvalidInputError: Callback не является функцией
            ValueError: Слушатель не найден
        """
        if not callable(callback):
            raise InvalidInputError("Callback must be callable")
            
        if self.get(listener_id):
            callback(*args, **kwargs)

    def get(self, listener_id: Union[int, str]) -> bool:
        """
        #### Проверяет, произошло ли событие
        
        ---
        
        :Arguments:
            listener_id: Идентификатор слушателя
            
        ---
        
        :Returns:
            bool: Произошло ли событие
            
        ---
        
        :Raises:
            ValueError: Слушатель не найден
        """
        for event in self.__events:
            if event["id"] == listener_id:
                return event["value"]
        raise ValueError(f"Event with id '{listener_id}' not found")
            
    def get_all(self) -> list[tuple[Union[int, str], bool]]:
        """
        #### Возвращает все текущие события
        
        ---
        
        :Returns:
            list: Список кортежей (идентификатор, состояние)
        """
        return [(event["id"], event["value"]) for event in self.__events]

    def update(self) -> None:
        """
        #### Обновляет состояние всех событий
        
        Должен вызываться каждый кадр для корректной работы
        """
        self.__events.clear()
        
        for listener in self.__listened_objects:
            try:
                listener_obj = listener["listener"]
                event_type = listener["type"]
                listener_id = listener["id"]
                
                # Обработка событий мыши
                if isinstance(listener_obj, Mouse):
                    button = listener["button"]
                    if event_type == self.EventType.MOUSE_CLICK:
                        value = listener_obj.get_click(button)
                    elif event_type == self.EventType.MOUSE_PRESS:
                        value = listener_obj.get_press(button)
                    else:
                        continue
                        
                # Обработка событий клавиатуры
                elif isinstance(listener_obj, Keyboard):
                    keys = listener["keys"]
                    if event_type == self.EventType.KEYBOARD_CLICK:
                        value = listener_obj.get_click(keys)
                    elif event_type == self.EventType.KEYBOARD_PRESS:
                        value = listener_obj.get_press(keys)
                    else:
                        continue
                
                # Сохранение результата проверки
                self.__events.append({"id": listener_id, "value": value})
                
            except Exception as e:
                raise InputError(f"Failed to update input events: {e}")