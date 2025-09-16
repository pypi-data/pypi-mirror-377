"""
#### *Модуль работы с текстом в PySGL*

---

##### Версия: 1.1.8

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 95%

---

✓ Полноценная работа с текстом:
  - Загрузка системных и пользовательских шрифтов
  - Настройка размера, цвета и стиля текста
  - Поддержка контуров и межбуквенных интервалов

✓ Гибкая система шрифтов:
  - Автоматическая загрузка системных шрифтов Windows
  - Поддержка TTF файлов
  - Кэширование загруженных шрифтов

✓ Расширенные возможности:
  - Трансформации (поворот, масштабирование, позиционирование)
  - Стили текста (жирный, курсив, подчеркивание, зачеркивание)
  - Настройка контуров и прозрачности

✓ Готовые интерфейсы:
  - Font - класс для работы со шрифтами
  - BaseText - основной класс для отображения текста
  - TextStyle - перечисление стилей текста

---

:Requires:

• Python 3.8+

• Библиотека ctypes (для работы с DLL)

• PySGL.dll (нативная библиотека рендеринга)

• Системные шрифты Windows (для Font.SystemFont)

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

import os
import ctypes
from colorama import Fore
from typing import Any, Self


from Moon.python.Colors import *
from Moon.python.Vectors import Vector2f
from Moon.python.Types import OriginTypes

from Moon.python.utils import find_library, LibraryLoadError

##################################################################
#                   `C / C++` Bindings                           #
#   Определение аргументов и возвращаемых типов для функций      #
#   из нативной DLL библиотеки PySGL, используемых через ctypes. #
##################################################################

# Загружаем DLL библиотеку
try:
    LIB_MOON = ctypes.CDLL(find_library())
except Exception as e:
    raise ImportError(f"Failed to load PySGL library: {e}")


LIB_MOON.loadSystemFont.argtypes = [ctypes.c_char_p]
LIB_MOON.loadSystemFont.restype = ctypes.c_void_p
LIB_MOON.createText.argtypes = [ctypes.c_void_p]
LIB_MOON.createText.restype =  ctypes.c_void_p
LIB_MOON.setText.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
LIB_MOON.setText.restype = None
LIB_MOON.setTextSize.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON.setTextSize.restype = None
LIB_MOON.setTextColor.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON.setTextColor.restype = None
LIB_MOON.setTextPosition.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON.setTextPosition.restype = None
LIB_MOON.setTextOfsset.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON.setTextOfsset.restype = None
LIB_MOON.setTextAngle.argtypes = [ctypes.c_void_p, ctypes.c_float]
LIB_MOON.setTextAngle.restype = None
LIB_MOON.setStyle.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON.setStyle.restype = None
LIB_MOON.setOutlineColor.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON.setOutlineColor.restype = None
LIB_MOON.setOutlineThickness.argtypes = [ctypes.c_void_p, ctypes.c_float]
LIB_MOON.setOutlineThickness.restype = None
LIB_MOON.setLetterSpacing.argtypes = [ctypes.c_void_p, ctypes.c_float]
LIB_MOON.setLetterSpacing.restype = None
LIB_MOON.getTextWidth.argtypes = [ctypes.c_void_p]
LIB_MOON.getTextWidth.restype = ctypes.c_double
LIB_MOON.getTextHeight.argtypes = [ctypes.c_void_p]
LIB_MOON.getTextHeight.restype = ctypes.c_double
LIB_MOON.setFont.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON.setFont.restype = None
LIB_MOON.setTextScale.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON.setTextScale.restype = None


class FontLoadError(Exception):
    """Базовый класс для всех ошибок модуля шрифтов"""
    pass

class FailedUnicodeCharacterSet(Exception):
    """Ошибка, если набор символов Unicode не поддерживается"""
    pass


class Font:
    """
    #### Класс для работы со шрифтами

    ---

    :Description:
    - Обеспечивает загрузку и управление шрифтами TTF
    - Поддерживает системные шрифты Windows
    - Кэширует загруженные шрифты для оптимизации

    ---

    :Features:
    - Автоматический поиск системных шрифтов
    - Загрузка пользовательских TTF файлов
    - Интеграция с нативной библиотекой рендеринга
    """

    @classmethod
    def SystemFont(cls, name: str):
        """
        #### Загружает системный шрифт Windows

        ---

        :Args:
        - name (str): Имя шрифта (например, "arial", "calibri")

        ---

        :Returns:
        - Font: Объект загруженного шрифта

        ---

        :Raises:
        - FileNotFoundError: Если шрифт не найден в системе

        ---

        :Example:
        ```python
        font = Font.SystemFont("arial")
        ```
        """
        font_path = "C:/Windows/Fonts/" + name.capitalize() + ".ttf"
        if os.path.isfile(font_path):
            return Font(font_path)
        else:
            raise FileNotFoundError(f"[ {Fore.MAGENTA}FontLoader{Fore.RESET} ] [ {Fore.RED}error{Fore.RESET} ] Font file not found: '{font_path}'")

    def __init__(self, font_path: str):
        """
        #### Инициализация шрифта из файла

        ---

        :Args:
        - font_path (str): Путь к TTF файлу шрифта

        ---

        :Raises:
        - FileNotFoundError: Если файл шрифта не существует
        """
        self.__font_path = font_path
        self.__font_ptr = LIB_MOON.loadSystemFont(self.__font_path.encode('utf-8'))
        if self.__font_ptr is None:
            raise FailedUnicodeCharacterSet()

    def get_font_ptr(self):
        """
        #### Возвращает указатель на нативный объект шрифта

        ---

        :Returns:
        - ctypes.c_void_p: Указатель для использования в C++ коде
        """
        return self.__font_ptr

    def get_font_path(self):
        """
        #### Возвращает путь к файлу шрифта

        ---

        :Returns:
        - str: Абсолютный путь к TTF файлу
        """
        return self.__font_path


def get_system_font_names() -> list[str]:
    """
    #### Возвращает список имен всех системных шрифтов

    ---

    :Description:
    - Сканирует папку C:/Windows/Fonts на наличие TTF файлов
    - Возвращает имена без расширения .ttf
    - Используется для автоматической инициализации шрифтов

    ---

    :Returns:
    - list[str]: Список имен доступных системных шрифтов

    ---

    :Example:
    ```python
    fonts = get_all_system_font_names()
    print(f"Найдено {len(fonts)} шрифтов")
    ```
    """
    fonts = []
    for font_name in os.listdir("C:/Windows/Fonts"):
        if font_name.endswith(".ttf"):
            fonts.append(font_name[:-4])
    return fonts

ARRAY_OF_SYSTEM_FONTS: list[Font]

def init_system_fonts():
    """
    #### Инициализирует кэш системных шрифтов

    ---

    :Description:
    - Загружает все доступные системные шрифты в память
    - Создает глобальный массив для быстрого доступа
    - Пропускает поврежденные или недоступные шрифты

    ---

    :Note:
    - Вызывается автоматически при импорте модуля
    - Может занять время при первом запуске

    ---

    :Example:
    ```python
    # Переинициализация после установки новых шрифтов
    init_system_fonts()
    ```
    """
    global ARRAY_OF_SYSTEM_FONTS
    ARRAY_OF_SYSTEM_FONTS = []
    detected_fonts = get_system_font_names()
    print(f"[ {Fore.MAGENTA}FontLoader{Fore.RESET} ] Detected {Fore.CYAN}{len(detected_fonts)}{Fore.RESET} fonts")
    for i, name in enumerate(detected_fonts):
        print(f"[ {Fore.MAGENTA}FontLoader{Fore.RESET} ] Loading font '{name}'")
        try:
            font = Font.SystemFont(name)
            ARRAY_OF_SYSTEM_FONTS.append(font)
        except:
            print(f"[ {Fore.MAGENTA}FontLoader{Fore.RESET} ] [ {Fore.RED}error{Fore.RESET} ] Font '{name}' has not been loaded.")
    print(f"[ {Fore.MAGENTA}FontLoader{Fore.RESET} ] [ {Fore.BLACK}note{Fore.RESET} ] Loaded {Fore.CYAN}{len(ARRAY_OF_SYSTEM_FONTS)}/{len(detected_fonts)}{Fore.RESET} fonts.")

def clear_system_fonts_cache():
    """
    #### Очищает кэш системных шрифтов

    ---

    :Description:
    - Удаляет все загруженные шрифты из кэша
    """

    global ARRAY_OF_SYSTEM_FONTS
    ARRAY_OF_SYSTEM_FONTS.clear()

def system_fonts_inited() -> bool:
    """
    #### Проверяет, загружены ли системные шрифты

    ---

    :Description:
    - Проверяет наличие массива системных шрифтов
    
    ---

    :Returns:
    - bool: True, если массив системных шрифтов загружен, иначе False
    """
    if ARRAY_OF_SYSTEM_FONTS: return True
    return False

def get_system_font(index: int):
    """
    #### Возвращает системный шрифт по индексу

    ---

    :Description:
    - Получает шрифт из предзагруженного кэша
    - Быстрее чем повторная загрузка шрифта
    - Индексы соответствуют порядку в get_all_system_font_names()

    ---

    :Args:
    - index (int): Индекс шрифта в массиве (0-based)

    ---

    :Returns:
    - Font: Объект системного шрифта

    ---

    :Raises:
    - IndexError: Если индекс выходит за границы массива

    ---

    :Example:
    ```python
    # Получить первый доступный шрифт
    font = get_system_font(0)
    ```
    """
    try:
        return ARRAY_OF_SYSTEM_FONTS[index]
    except IndexError:
        raise ValueError(f"[ {Fore.MAGENTA}FontLoader{Fore.RESET} ] [ {Fore.RED}error{Fore.RESET} ] System font index {index} not found in the cache. Max index is {len(ARRAY_OF_SYSTEM_FONTS) - 1}.")

def get_system_font_with_name(name: str):
    """
    #### Возвращает системный шрифт по имени

    ---

    :Desription:
    - Ищет шрифт по имени в предзагруженном кэше
    - Регистр символов не учитывается
    - Возвращает первый найденный шрифт с таким именем

    ---

    :Args:
    - name (str): Имя шрифта (например, "arial", "Times New Roman")

    ---

    :Returns:
    - Font: Объект системного шрифта

    ---

    :Raises:
    - ValueError: Если шрифт с указанным именем не найден

    ---

    :Example:
    ```python
    font = get_system_font_with_name("calibri")
    ```
"""
    for font in ARRAY_OF_SYSTEM_FONTS:
        if font.get_font_path().lower().endswith(name.lower() + ".ttf"):
            return font
    raise ValueError(f"[ {Fore.MAGENTA}FontLoader{Fore.RESET} ] [ {Fore.RED}error{Fore.RESET} ] System font '{name}' not found in the cache.")


BaseTextPtr = ctypes.c_void_p


class TextStyle:
    """
    #### Перечисление стилей текста

    ---

    :Values:
    - REGULAR: Обычный текст без стилей
    - BOLD: Жирный текст
    - ITALIC: Курсивный текст
    - UNDERLINE: Подчеркнутый текст
    - STRIKEOUT: Зачеркнутый текст

    ---

    :Note:
    - Стили можно комбинировать через побитовое OR (|)
    - Пример: TextStyle.BOLD | TextStyle.ITALIC
    """
    REGULAR = 0
    BOLD = 1 << 0
    ITALIC = 1 << 1
    UNDERLINE = 1 << 2
    STRIKEOUT = 1 << 3

class BaseText:
    """
    #### Основной класс для отображения текста

    ---

    :Description:
    - Обеспечивает полноценную работу с текстовыми объектами
    - Поддерживает все виды трансформаций и стилизации
    - Интегрируется с системой рендеринга PySGL

    ---

    :Features:
    - Настройка шрифта, размера и цвета
    - Трансформации (позиция, поворот, масштаб)
    - Стили текста и контуры
    - Межбуквенные интервалы
    - Получение размеров текста
    """

    __slots__ = ('__font', '__text_ptr', '__text', '__scale', '__angle', '__origin', '__outline_color', '__outline_thickness', '__color', '__letter_spacing')

    def __init__(self, font: Font):
        """
        #### Инициализация текстового объекта

        ---

        :Args:
        - font (Font): Шрифт для отображения текста

        ---

        :Description:
        - Создает нативный объект текста
        - Устанавливает параметры по умолчанию
        - Связывает с указанным шрифтом
        """
        self.__font = font
        self.__text_ptr: BaseTextPtr = LIB_MOON.createText(self.__font.get_font_ptr())
        self.__text: str = ""
        self.__scale: list[float] = [1, 1]
        self.__origin: Vector2f = Vector2f(0, 0)
        self.__angle: float = 0
        self.__outline_color: Color | None = None
        self.__outline_thickness: float = 0
        self.__color: Color = Color(0, 0, 0, 255)
        self.__letter_spacing: float = 0
        LIB_MOON.setTextColor(self.__text_ptr, self.__color.r, self.__color.g, self.__color.b, self.__color.a)

    def get_ptr(self) -> BaseTextPtr:
        """
        #### Возвращает указатель на нативный объект текста

        ---

        :Returns:
        - BaseTextPtr: Указатель для использования в системе рендеринга
        """
        return self.__text_ptr

    def get_scale(self) -> list[float]:
        """
        #### Возвращает текущий масштаб текста

        ---

        :Returns:
        - list[float]: Список [scale_x, scale_y]
        """
        return self.__scale

    def set_text(self, text: str) -> Self:
        """
        #### Устанавливает текст для отображения

        ---

        :Args:
        - text (str): Текст для отображения (поддерживает Unicode)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        text_obj.set_text("Привет, мир!")
        ```
        """
        self.__text = text
        LIB_MOON.setText(self.__text_ptr, text.encode("utf-8"))
        return self

    def set_text_scale_xy(self, x: float | None = None, y: float | None = None) -> Self:
        """
        #### Устанавливает масштаб текста по осям

        ---

        :Args:
        - x (float | None): Масштаб по горизонтали (None = не изменять)
        - y (float | None): Масштаб по вертикали (None = не изменять)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Растянуть текст по горизонтали
        text_obj.set_text_scale_xy(x=2.0)
        ```
        """
        if x is not None :
            self.__scale[0] = x
        if y is not None :
            self.__scale[1] = y
        LIB_MOON.setTextScale(self.__text_ptr, self.__scale[0], self.__scale[1])
        return self

    def set_text_scale(self, scale: float) -> Self:
        """
        #### Устанавливает равномерный масштаб текста

        ---

        :Args:
        - scale (float): Коэффициент масштабирования (1.0 = оригинальный размер)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Увеличить текст в 1.5 раза
        text_obj.set_text_scale(1.5)
        ```
        """
        self.__scale[0] = scale
        self.__scale[1] = scale
        LIB_MOON.setTextScale(self.__text_ptr, self.__scale[0], self.__scale[1])
        return self

    def set_fast_text(self, value: Any) -> Self:
        """
        #### Быстро устанавливает текст из любого значения

        ---

        :Description:
        - Автоматически преобразует значение в строку
        - Оптимизирован для частых обновлений (например, счетчики)
        - Не сохраняет значение во внутренней переменной

        ---

        :Args:
        - value (Any): Любое значение для отображения

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Отображение FPS
        text_obj.set_fast_text(fps_counter)
        ```
        """
        LIB_MOON.setText(self.__text_ptr, str(value).encode('utf-8'))
        return self

    def set_size(self, size: int | float) -> Self:
        """
        #### Устанавливает размер шрифта

        ---

        :Args:
        - size (int | float): Размер шрифта в пикселях

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        text_obj.set_size(24)  # Размер 24px
        ```
        """
        LIB_MOON.setTextSize(self.__text_ptr, int(size))
        return self

    def set_color(self, color: Color) -> Self:
        """
        #### Устанавливает цвет текста

        ---

        :Args:
        - color (Color): Цвет текста с альфа-каналом

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        text_obj.set_color(Color(255, 0, 0))  # Красный текст
        ```
        """
        self.__color = color
        LIB_MOON.setTextColor(self.__text_ptr, color.r, color.g, color.b, color.a)
        return self

    def set_position(self, x: float, y: float) -> Self:
        """
        #### Устанавливает позицию текста

        ---

        :Args:
        - x (float): Координата X в пикселях
        - y (float): Координата Y в пикселях

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        text_obj.set_position(100, 50)
        ```
        """
        LIB_MOON.setTextPosition(self.__text_ptr, x, y)
        return self

    def set_origin(self, x: float, y: float) -> Self:
        """
        #### Устанавливает точку привязки текста

        ---

        :Description:
        - Определяет точку, относительно которой позиционируется текст
        - (0,0) = левый верхний угол, (width/2, height/2) = центр

        ---

        :Args:
        - x (float): Смещение точки привязки по X
        - y (float): Смещение точки привязки по Y

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Центрировать текст
        text_obj.set_origin(text_width/2, text_height/2)
        ```
        """
        LIB_MOON.setTextOfsset(self.__text_ptr, x, y)
        self.__origin.x = x
        self.__origin.y = y
        return self

    def get_origin(self) -> Vector2f:
        """
        #### Возвращает текущую точку привязки

        ---

        :Returns:
        - Vector2f: Координаты точки привязки
        """
        return self.__origin

    def set_angle(self, angle: float) -> Self:
        """
        #### Устанавливает угол поворота текста

        ---

        :Args:
        - angle (float): Угол поворота в градусах

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        text_obj.set_angle(45)  # Поворот на 45 градусов
        ```
        """
        LIB_MOON.setTextAngle(self.__text_ptr, angle)
        self.__angle = angle
        return self

    def get_angle(self) -> float:
        """
        #### Возвращает текущий угол поворота

        ---

        :Returns:
        - float: Угол поворота в градусах
        """
        return self.__angle

    def set_style(self, style: TextStyle) -> Self:
        """
        #### Устанавливает стиль текста

        ---

        :Args:
        - style (TextStyle): Стиль из перечисления TextStyle

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Жирный курсивный текст
        text_obj.set_style(TextStyle.BOLD | TextStyle.ITALIC)
        ```
        """
        LIB_MOON.setStyle(self.__text_ptr, style)
        return self

    def set_font(self, font: Font) -> Self:
        """
        #### Изменяет шрифт текста

        ---

        :Args:
        - font (Font): Новый шрифт для отображения

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        new_font = Font.SystemFont("times")
        text_obj.set_font(new_font)
        ```
        """
        LIB_MOON.setFont(self.__text_ptr, font.get_font_ptr())
        return self

    def set_outline_color(self, color: Color) -> Self:
        """
        #### Устанавливает цвет контура текста

        ---

        :Args:
        - color (Color): Цвет контура с альфа-каналом

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Note:
        - Контур будет виден только при толщине > 0

        ---

        :Example:
        ```python
        text_obj.set_outline_color(Color(0, 0, 0)).set_outline_thickness(2)
        ```
        """
        LIB_MOON.setOutlineColor(self.__text_ptr, color.r, color.g, color.b, color.a)
        self.__outline_color = color
        return self

    def get_outline_color(self) -> Color | None:
        """
        #### Возвращает текущий цвет контура

        ---

        :Returns:
        - Color: Цвет контура или None если не установлен
        """
        return self.__outline_color

    def set_outline_thickness(self, thickness: float) -> Self:
        """
        #### Устанавливает толщину контура текста

        ---

        :Args:
        - thickness (float): Толщина контура в пикселях (0 = без контура)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        text_obj.set_outline_thickness(1.5)  # Тонкий контур
        ```
        """
        LIB_MOON.setOutlineThickness(self.__text_ptr, thickness)
        self.__outline_thickness = thickness
        return self

    def get_outline_thickness(self) -> float:
        """
        #### Возвращает текущую толщину контура

        ---

        :Returns:
        - float: Толщина контура в пикселях
        """
        return self.__outline_thickness

    def set_letter_spacing(self, spacing: float) -> Self:
        """
        #### Устанавливает межбуквенный интервал

        ---

        :Args:
        - spacing (float): Дополнительное расстояние между символами в пикселях

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        text_obj.set_letter_spacing(2.0)  # Увеличить интервалы
        ```
        """
        LIB_MOON.setLetterSpacing(self.__text_ptr, spacing)
        self.__letter_spacing = spacing
        return self

    def get_letter_spacing(self) -> float:
        """
        #### Возвращает текущий межбуквенный интервал

        ---

        :Returns:
        - float: Дополнительное расстояние между символами
        """
        return self.__letter_spacing

    def get_text_width(self) -> float:
        """
        #### Возвращает ширину отрендеренного текста

        ---

        :Description:
        - Учитывает текущий шрифт, размер и межбуквенные интервалы
        - Полезно для выравнивания и позиционирования

        ---

        :Returns:
        - float: Ширина текста в пикселях

        ---

        :Example:
        ```python
        # Центрировать текст
        width = text_obj.get_text_width()
        text_obj.set_position(screen_width/2 - width/2, y)
        ```
        """
        return LIB_MOON.getTextWidth(self.__text_ptr)

    def get_text_height(self) -> float:
        """
        #### Возвращает высоту отрендеренного текста

        ---

        :Description:
        - Учитывает текущий шрифт и размер
        - Включает высоту символов с выносными элементами

        ---

        :Returns:
        - float: Высота текста в пикселях

        ---

        :Example:
        ```python
        # Вертикальное центрирование
        height = text_obj.get_text_height()
        text_obj.set_position(x, screen_height/2 - height/2)
        ```
        """
        return LIB_MOON.getTextHeight(self.__text_ptr)

    def get_uninitialized_text_width(self, text: str) -> float:
        """
        #### Возвращает ширину текста без изменения текущего содержимого

        ---

        :Description:
        - Временно устанавливает указанный текст для измерения
        - Восстанавливает исходный текст после измерения
        - Полезно для предварительных расчетов размеров

        ---

        :Args:
        - text (str): Текст для измерения

        ---

        :Returns:
        - float: Ширина указанного текста в пикселях

        ---

        :Example:
        ```python
        width = text_obj.get_uninitialized_text_width("Тестовый текст")
        ```
        """
        saved_text = self.__text
        self.set_text(text)
        width = LIB_MOON.getTextWidth(self.__text_ptr)
        self.set_text(saved_text)
        return width
    
    def get_text(self) -> str:
        return self.__text

    def get_uninitialized_text_height(self, text: str) -> float:
        """
        #### Возвращает высоту текста без изменения текущего содержимого

        ---

        :Description:
        - Временно устанавливает указанный текст для измерения
        - Восстанавливает исходный текст после измерения
        - Полезно для предварительных расчетов размеров

        ---

        :Args:
        - text (str): Текст для измерения

        ---

        :Returns:
        - float: Высота указанного текста в пикселях

        ---

        :Example:
        ```python
        height = text_obj.get_uninitialized_text_height("Тестовый текст")
        ```
        """
        saved_text = self.__text
        self.set_text(text)
        height = LIB_MOON.getTextHeight(self.__text_ptr)
        self.set_text(saved_text)
        return height




class Text(BaseText):
    """
    #### Расширенный класс для работы с текстом с типизированными точками привязки

    ---

    :Description:
    - Наследует все возможности BaseText
    - Добавляет систему типизированных точек привязки (OriginTypes)
    - Поддерживает отступы для точек привязки
    - Упрощает позиционирование текста относительно различных точек

    ---

    :Features:
    - Автоматическое вычисление точек привязки
    - Поддержка всех стандартных позиций (центр, углы, стороны)
    - Настраиваемые отступы для каждой оси
    - Учет масштабирования при расчете позиций
    """

    __slots__ = ('__typed_origin', '__origin_padding')

    def __init__(self, font: Font):
        """
        #### Инициализация расширенного текстового объекта

        ---

        :Args:
        - font (Font): Шрифт для отображения текста

        ---

        :Description:
        - Вызывает конструктор базового класса
        - Устанавливает точку привязки по умолчанию (TOP_LEFT)
        - Инициализирует нулевые отступы
        """
        super().__init__(font)

        self.__typed_origin: OriginTypes = OriginTypes.TOP_LEFT
        self.__origin_padding: Vector2f = Vector2f.zero()
        self.set_origin(0, 0)

    def set_origin_padding(self, padding: float):
        """
        #### Устанавливает одинаковые отступы для обеих осей

        ---

        :Args:
        - padding (float): Отступ в пикселях для X и Y
        """
        self.__origin_padding.x = padding
        self.__origin_padding.y = padding

    def set_origin_padding_y(self, padding: float):
        """
        #### Устанавливает отступ по вертикальной оси

        ---

        :Args:
        - padding (float): Отступ по Y в пикселях
        """
        self.__origin_padding.y = padding

    def set_origin_padding_x(self, padding: float):
        """
        #### Устанавливает отступ по горизонтальной оси

        ---

        :Args:
        - padding (float): Отступ по X в пикселях
        """
        self.__origin_padding.x = padding

    def get_origin_padding(self) -> Vector2f:
        """
        #### Возвращает текущие отступы точки привязки

        ---

        :Returns:
        - Vector2f: Вектор с отступами по X и Y
        """
        return self.__origin_padding

    def get_typed_origin(self) -> OriginTypes:
        """
        #### Возвращает текущий тип точки привязки

        ---

        :Returns:
        - OriginTypes: Текущий тип привязки из перечисления
        """
        return self.__typed_origin

    def set_typed_origin(self, origin_type: OriginTypes):
        """
        #### Устанавливает типизированную точку привязки текста

        ---

        :Description:
        - Автоматически вычисляет координаты точки привязки
        - Учитывает размеры текста и установленные отступы
        - Корректирует расчеты с учетом текущего масштаба
        - Поддерживает все стандартные позиции привязки

        ---

        :Args:
        - origin_type (OriginTypes): Тип точки привязки из перечисления

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Raises:
        - TypeError: При передаче недопустимого типа привязки

        ---

        :Example:
        ```python
        # Центрировать текст
        text_obj.set_typed_origin(OriginTypes.CENTER)

        # Привязать к правому нижнему углу
        text_obj.set_typed_origin(OriginTypes.DOWN_RIGHT)
        ```
        """
        self.__typed_origin = origin_type

        width = self.get_text_width()
        height = self.get_text_height()


        match (self.__typed_origin):
            case OriginTypes.CENTER:
                self.set_origin((width / 2 + self.__origin_padding.x) / self.get_scale()[0],    (height / 2  + self.__origin_padding.y) / self.get_scale()[1])

            case OriginTypes.TOP_CENTER:
                self.set_origin((width / 2 + self.__origin_padding.x) / self.get_scale()[0],    (0  + self.__origin_padding.y) / self.get_scale()[1])
            case OriginTypes.DOWN_CENTER:
                self.set_origin((width / 2 + self.__origin_padding.x) / self.get_scale()[0],    (height  + self.__origin_padding.y) / self.get_scale()[1])
            case OriginTypes.LEFT_CENTER:
                self.set_origin((0 + self.__origin_padding.x) / self.get_scale()[0],            (height / 2  + self.__origin_padding.y) / self.get_scale()[1])
            case OriginTypes.RIGHT_CENTER:
                self.set_origin((width + self.__origin_padding.x) / self.get_scale()[0],        (height / 2  + self.__origin_padding.y) / self.get_scale()[1])

            case OriginTypes.TOP_LEFT:
                self.set_origin((0 + self.__origin_padding.x) / self.get_scale()[0],            (0 + self.__origin_padding.y) / self.get_scale()[1])
            case OriginTypes.TOP_RIGHT:
                self.set_origin((width + self.__origin_padding.x) / self.get_scale()[0],        (0 + self.__origin_padding.y) / self.get_scale()[1])
            case OriginTypes.DOWN_LEFT:
                self.set_origin((0 + self.__origin_padding.x) / self.get_scale()[0],            (height + self.__origin_padding.y) / self.get_scale()[1])
            case OriginTypes.DOWN_RIGHT:
                self.set_origin((width + self.__origin_padding.x) / self.get_scale()[0],        (height + self.__origin_padding.y) / self.get_scale()[1])
            case _:
                raise TypeError("Invalid origin type!")

        return self
