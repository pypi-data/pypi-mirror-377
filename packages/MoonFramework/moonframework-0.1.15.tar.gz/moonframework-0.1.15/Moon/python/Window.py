"""
#### *Модуль работы с окнами в Moon*

---

##### Версия: 1.1.8

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 98%

---

✓ Полноценное управление окнами:
  - Создание/уничтожение окон
  - Управление размером, позицией и стилями
  - Настройка заголовка и прозрачности

✓ Комплексная система рендеринга:
  - Поддержка View и мировых координат
  - Отрисовка примитивов с состояниями рендеринга
  - Гибкая система преобразования координат

✓ Производительность и контроль:
  - Управление FPS и вертикальной синхронизацией
  - Детальная статистика рендеринга
  - Встроенный профилировщик производительности

✓ Готовые интерфейсы:
  - Window - основной класс работы с окном
  - WindowEvents - система обработки событий
  - Window.Style - перечисление стилей окна

---

:Requires:

• Python 3.8+

• Библиотека keyboard (для обработки клавиатуры)

• Библиотека ctypes (для работы с DLL)

• Moon.dll (нативная библиотека рендеринга)

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
import keyboard

from time import time
from typing import overload, Final, final, Self

from Moon.python.Colors import *
from Moon.python.Time import Clock
from Moon.python.Views import View
from Moon.python.Types import TwoIntegerList
from Moon.python.Vectors import Vector2i, Vector2f
from Moon.python.Inputs import MouseInterface, KeyBoardInterface

from Moon.python.Rendering.Text import *
from Moon.python.Rendering.Shapes import *
from Moon.python.Rendering.Shaders import Shader
from Moon.python.Rendering.RenderStates import RenderStates

from Moon.python.utils import find_library, LibraryLoadError, find_module_installation_path


# Загружаем DLL библиотеку

try:
    LIB_MOON: Final[ctypes.CDLL] = ctypes.CDLL(find_library())
except Exception as e:
    raise ImportError(f"Failed to load Moon library: {e}")


def get_screen_resolution() -> TwoIntegerList:
    """
    #### Получает разрешение основного монитора с использованием Windows API.

    ---

    :Returns:
    - tuple: Кортеж, содержащий ширину и высоту экрана в пикселях (ширина, высота).
    """
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
    screen_height = user32.GetSystemMetrics(1) # SM_CYSCREEN
    return [screen_width, screen_height]


##################################################################
#                   `C / C++` Bindings                           #
#   Определение аргументов и возвращаемых типов для функций      #
#   из нативной DLL библиотеки Moon, используемых через ctypes.  #
##################################################################

LIB_MOON._Window_Create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p]
LIB_MOON._Window_Create.restype = ctypes.c_void_p
LIB_MOON._Window_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_Delete.restype = None
LIB_MOON._Window_Clear.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]
LIB_MOON._Window_Clear.restype = None
LIB_MOON._Window_Display.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_Display.restype = None
LIB_MOON._Window_IsOpen.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_IsOpen.restype = ctypes.c_bool
LIB_MOON._Window_Draw.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._Window_Draw.restype = None
LIB_MOON._Window_GetDefaultView.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_GetDefaultView.restype = ctypes.c_void_p
LIB_MOON._Window_SetView.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._Window_SetView.restype = None
LIB_MOON._Window_SetWaitFps.argtypes = [ctypes.c_void_p, ctypes.c_uint]
LIB_MOON._Window_SetWaitFps.restype = None
LIB_MOON._Window_SetTitle.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
LIB_MOON._Window_SetTitle.restype = None
LIB_MOON._Window_SetVsync.argtypes = [ctypes.c_void_p, ctypes.c_bool]
LIB_MOON._Window_SetVsync.restype = None
LIB_MOON._Window_MapPixelToCoordsX.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_void_p]
LIB_MOON._Window_MapPixelToCoordsX.restype = ctypes.c_float
LIB_MOON._Window_MapPixelToCoordsY.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_void_p]
LIB_MOON._Window_MapPixelToCoordsY.restype = ctypes.c_float
LIB_MOON._Window_MapCoordsToPixelX.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_void_p]
LIB_MOON._Window_MapCoordsToPixelX.restype = ctypes.c_float
LIB_MOON._Window_MapCoordsToPixelY.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_void_p]
LIB_MOON._Window_MapCoordsToPixelY.restype = ctypes.c_float
LIB_MOON._Window_DrawWithRenderStates.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._Window_DrawWithRenderStates.restype = None
LIB_MOON._Window_DrawVertexArrayWithRenderStates.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._Window_DrawVertexArrayWithRenderStates.restype = None
LIB_MOON._Window_DrawWithShader.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._Window_DrawWithShader.restype = None
LIB_MOON._Window_SetCursorVisibility.argtypes = [ctypes.c_void_p, ctypes.c_bool]
LIB_MOON._Window_SetCursorVisibility.restype = None
LIB_MOON._Window_Close.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_Close.restype = None
LIB_MOON._Window_SetSystemCursor.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._Window_SetSystemCursor.restype = None
LIB_MOON._Window_GetSizeWidth.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_GetSizeWidth.restype = ctypes.c_int
LIB_MOON._Window_GetSizeHeight.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_GetSizeHeight.restype = ctypes.c_int
LIB_MOON._Window_GetPositionX.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_GetPositionX.restype = ctypes.c_int
LIB_MOON._Window_GetPositionY.argtypes = [ctypes.c_void_p]
LIB_MOON._Window_GetPositionY.restype = ctypes.c_int
LIB_MOON._Window_SetPosition.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
LIB_MOON._Window_SetPosition.restype = None
LIB_MOON._Window_SetSize.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
LIB_MOON._Window_SetSize.restype = None
LIB_MOON._Window_GetCurrentEventType.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._Window_GetCurrentEventType.restype = ctypes.c_int
LIB_MOON._Window_SetIconFromPath.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
LIB_MOON._Window_SetIconFromPath.restype = ctypes.c_bool

LIB_MOON._Events_Create.argtypes = []
LIB_MOON._Events_Create.restype = ctypes.c_void_p
LIB_MOON._Events_Destroy.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_Destroy.restype = None
LIB_MOON._Events_GetType.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_GetType.restype = ctypes.c_int
LIB_MOON._Events_GetKey.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_GetKey.restype = ctypes.c_int
LIB_MOON._Events_GetMouseButton.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_GetMouseButton.restype = ctypes.c_int
LIB_MOON._Events_GetMouseX.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_GetMouseX.restype = ctypes.c_int
LIB_MOON._Events_GetMouseY.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_GetMouseY.restype = ctypes.c_int
LIB_MOON._Events_GetSizeWidth.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_GetSizeWidth.restype = ctypes.c_int
LIB_MOON._Events_GetSizeHeight.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_GetSizeHeight.restype = ctypes.c_int
LIB_MOON._Events_GetMouseWheel.argtypes = [ctypes.c_void_p]
LIB_MOON._Events_GetMouseWheel.restype = ctypes.c_int



@final
class WindowEvents:
    """
    #### Класс для обработки событий окна

    ---

    :Description:
    - Обеспечивает интерфейс для работы с событиями окна (клавиатура, мышь, джойстик и др.)
    - Получает события из системной очереди сообщений
    - Преобразует нативные события в удобный Python-интерфейс

    ---

    :Features:
    - Поддержка событий клавиатуры, мыши, джойстика
    - Обработка сенсорного ввода и событий окна
    - Получение детальной информации о каждом событии
    """

    class Type:
        """
        #### Перечисление типов событий окна

        ---

        :Values:
        - Closed: Окно было закрыто
        - Resized: Изменен размер окна
        - Focus: События изменения фокуса окна
        - Input: События ввода (клавиатура, мышь, джойстик)
        - Touch: События сенсорного ввода
        - Sensor: События датчиков устройства
        """
    ###########################################################################
        Closed = 0                     # Окно запросило закрытие (крестик/Alt+F4)
        Resized = 1                    # Окно изменило размер (width/height доступны)
        LostFocus = 2                  # Окно потеряло фокус ввода
        GainedFocus = 3                # Окно получило фокус ввода
        TextEntered = 4                # Введен Unicode-символ (поддержка IME)

        KeyPressed = 5                 # Нажата клавиша клавиатуры
        KeyReleased = 6                # Отпущена клавиша клавиатуры

        MouseWheelMoved = 7            # Прокручено колесо мыши (устаревший формат)
        MouseWheelScrolled = 8         # Прокручено колесо мыши (новый формат)
        MouseButtonPressed = 9         # Нажата кнопка мыши
        MouseButtonReleased = 10       # Отпущена кнопка мыши
        MouseMoved = 11                # Перемещен курсор мыши
        MouseEntered = 12              # Курсор вошел в область окна
        MouseLeft = 13                 # Курсор покинул область окна

        JoystickButtonPressed = 14     # Нажата кнопка джойстика
        JoystickButtonReleased = 15    # Отпущена кнопка джойстика
        JoystickMoved = 16             # Изменено положение оси джойстика
        JoystickConnected = 17         # Джойстик подключен
        JoystickDisconnected = 18      # Джойстик отключен

        TouchBegan = 19                # Начало касания сенсорного экрана
        TouchMoved = 20                # Перемещение касания
        TouchEnded = 21                # Окончание касания
        SensorChanged = 22             # Изменение показаний датчика устройства
    ###########################################################################

    def __init__(self):
        """
        #### Инициализация обработчика событий

        ---

        :Actions:
        - Создает нативный объект для хранения событий
        - Подготавливает внутренние структуры данных

        ---

        :Raises:
        - RuntimeError: При ошибке создания нативного объекта
        """
        self.__event_ptr = LIB_MOON._Events_Create()

    def __del__(self):
        """
        #### Освобождение ресурсов обработчика событий

        ---

        :Actions:
        - Удаляет нативный объект событий
        - Гарантирует корректное завершение работы
        """
        LIB_MOON._Events_Destroy(self.__event_ptr)

    def get_ptr(self) -> ctypes.c_void_p:
        """
        #### Получение указателя на нативный объект событий

        ---

        :Returns:
        - ctypes.c_void_p: Указатель на внутренний объект событий

        ---

        :Note:
        - Для внутреннего использования в Moon
        """
        return self.__event_ptr

    def poll(self, window) -> bool:
        """
        #### Проверка наличия событий в очереди

        ---

        :Args:
        - window: Объект окна для проверки событий

        ---

        :Returns:
        - bool: True если есть непрочитанные события, иначе False

        ---

        :Example:
        ```python
        while events.poll(window):
            handle_event(events)
        ```
        """
        return LIB_MOON._Window_GetCurrentEventType(window.get_ptr(), self.__event_ptr)

    def get_type(self) -> int:
        """
        #### Получение типа текущего события

        ---

        :Returns:
        - int: Код события из WindowEvents.Type

        ---

        :Example:
        ```python
        if events.get_type() == WindowEvents.Type.KeyPressed:
            handle_key_press()
        ```
        """
        return LIB_MOON._Events_GetType(self.__event_ptr)

    def get_key(self) -> int:
        """
        #### Получение кода клавиши для событий клавиатуры

        ---

        :Returns:
        - int: Код клавиши (соответствует KeyCode)

        ---

        :Note:
        - Только для KeyPressed/KeyReleased событий
        """
        return LIB_MOON._Events_GetKey(self.__event_ptr)

    def get_mouse_button(self) -> int:
        """
        #### Получение кода кнопки мыши

        ---

        :Returns:
        - int: Код кнопки (0-левая, 1-правая, 2-средняя)

        ---

        :Note:
        - Для MouseButtonPressed/MouseButtonReleased
        """
        return LIB_MOON._Events_GetMouseButton(self.__event_ptr)

    def get_mouse_wheel(self) -> int:
        """
        #### Получение значения прокрутки колеса мыши

        ---

        :Returns:
        - int: Шаги прокрутки (>0 - вверх, <0 - вниз)

        ---

        :Note:
        - Для MouseWheelMoved/MouseWheelScrolled
        """
        return LIB_MOON._Events_GetMouseWheel(self.__event_ptr)

    def get_mouse_x(self) -> int:
        """
        #### Получение X-координаты курсора мыши

        ---

        :Returns:
        - int: Координата X в пикселях относительно окна

        ---

        :Note:
        - Для событий связанных с положением мыши
        """
        return LIB_MOON._Events_GetMouseX(self.__event_ptr)

    def get_mouse_y(self) -> int:
        """
        #### Получение Y-координаты курсора мыши

        ---

        :Returns:
        - int: Координата Y в пикселях относительно окна

        ---

        :Note:
        - Для событий связанных с положением мыши
        """
        return LIB_MOON._Events_GetMouseY(self.__event_ptr)

    def get_size_width(self) -> int:
        """
        #### Получение новой ширины окна

        ---

        :Returns:
        - int: Ширина окна после изменения (в пикселях)

        ---

        :Note:
        - Только для Resized события
        """
        return LIB_MOON._Events_GetSizeWidth(self.__event_ptr)

    def get_size_height(self) -> int:
        """
        #### Получение новой высоты окна

        ---

        :Returns:
        - int: Высота окна после изменения (в пикселях)

        ---

        :Note:
        - Только для Resized события
        """
        return LIB_MOON._Events_GetSizeHeight(self.__event_ptr)


# Тип для хранения указателя на объект окна ===== +
type WindowPtr = ctypes.c_void_p
# =============================================== +

# Константа для обозначения неограниченного FPS (представляется большим числом) = +
FPS_UNLIMIT_CONST: Final[Union[int, float]] = 1000000                             #
# =============================================================================== +

@final
class SystemCursors:
    """Класс, представляющий системные курсоры. Каждая константа соответствует определенному типу курсора."""

    Arrow = 0                     # Стандартный курсор (стрелка)
    ArrowWait = 1                 # Стрелка с индикатором ожидания (например, при занятости системы)
    Wait = 2                      # Курсор ожидания (обычно песочные часы или круговой индикатор)
    Text = 3                      # Текстовый курсор (вертикальная черта, используется в полях ввода)
    Hand = 4                      # Указатель в виде руки (обычно для кликабельных ссылок)

    # Курсоры изменения размера
    SizeHorizontal = 5             # Двунаправленная горизонтальная стрелка (изменение ширины)
    SizeVertical = 6               # Двунаправленная вертикальная стрелка (изменение высоты)
    SizeTopLeftBottomRight = 7     # Диагональная двунаправленная стрелка (↖↘, изменение размера по диагонали)
    SizeBottomLeftTopRight = 8     # Диагональная двунаправленная стрелка (↙↗, изменение размера по диагонали)

    # Курсоры изменения размера (альтернативные варианты)
    SizeLeft = 9                  # Курсор изменения размера влево (горизонтальная стрелка ←)
    SizeRight = 10                # Курсор изменения размера вправо (горизонтальная стрелка →)
    SizeTop = 11                  # Курсор изменения размера вверх (вертикальная стрелка ↑)
    SizeBottom = 12               # Курсор изменения размера вниз (вертикальная стрелка ↓)

    # Угловые курсоры изменения размера
    SizeTopLeft = 13              # Курсор изменения размера в верхний левый угол (↖)
    SizeBottomRight = 14          # Курсор изменения размера в нижний правый угол (↘)
    SizeBottomLeft = 15           # Курсор изменения размера в нижний левый угол (↙)
    SizeTopRight = 16             # Курсор изменения размера в верхний правый угол (↗)

    SizeAll = 17                  # Курсор перемещения (четырехнаправленная стрелка)
    Cross = 18                    # Перекрестие (используется для точного выбора, например в графических редакторах)
    Help = 19                     # Курсор со знаком вопроса (указывает на справку или подсказку)
    NotAllowed = 20               # Курсор "Действие запрещено" (перечеркнутый круг, например при drag-and-drop)

# Индекс оконного атрибута отвечающего за скругления углов окна (Windows 11+) = +
DWMWA_WINDOW_CORNER_PREFERENCE: Final[int] = 33                                 #
# ============================================================================= +

# Константа обьекта оконного интерфейса ============================================ +
# ! Не рекомендуется использовать вне предоставленного функционала фреймворка!       #
DWM_API: Final[ctypes.WinDLL] = ctypes.WinDLL("dwmapi")                              #
# ================================================================================== #

LIB_MOON._WindowContextSettings_Create.restype = ctypes.c_void_p
LIB_MOON._WindowContextSettings_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._WindowContextSettings_Delete.restype = None
LIB_MOON._WindowContextSettings_SetAttributeFlags.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._WindowContextSettings_SetAttributeFlags.restype = None
LIB_MOON._WindowContextSettings_SetAntialiasingLevel.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._WindowContextSettings_SetAntialiasingLevel.restype = None
LIB_MOON._WindowContextSettings_SetDepthBits.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._WindowContextSettings_SetDepthBits.restype = None
LIB_MOON._WindowContextSettings_SetMajorVersion.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._WindowContextSettings_SetMajorVersion.restype = None
LIB_MOON._WindowContextSettings_SetMinorVersion.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._WindowContextSettings_SetMinorVersion.restype = None
LIB_MOON._WindowContextSettings_SetStencilBits.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._WindowContextSettings_SetStencilBits.restype = None
LIB_MOON._WindowContextSettings_SetSrgbCapable.argtypes = [ctypes.c_void_p, ctypes.c_bool]
LIB_MOON._WindowContextSettings_SetSrgbCapable.restype = None

@final
class ContextSettings:
    """
    #### Класс для настройки параметров графического контекста OpenGL

    ---

    :Description:
    - Управляет настройками OpenGL контекста для окна
    - Позволяет настроить антиалиасинг, буферы глубины и версию OpenGL
    - Используется при создании окна для оптимизации рендеринга

    ---

    :Features:
    - Настройка уровня антиалиасинга
    - Управление буферами глубины и трафарета
    - Выбор версии OpenGL
    - Поддержка sRGB цветового пространства
    """

    def __init__(self):
        """
        #### Инициализация настроек контекста с параметрами по умолчанию

        ---

        :Description:
        - Создает объект с базовыми настройками OpenGL
        - Все параметры устанавливаются в значения по умолчанию
        """
        self.__context_ptr = LIB_MOON._WindowContextSettings_Create()

    def __del__(self):
        """
        #### Освобождение ресурсов настроек контекста

        ---

        :Description:
        - Автоматически вызывается при удалении объекта
        - Освобождает нативные ресурсы
        """
        if hasattr(self, '_ContextSettings__context_ptr'):
            LIB_MOON._WindowContextSettings_Delete(self.__context_ptr)

    def get_ptr(self) -> ctypes.c_void_p:
        """
        #### Возвращает указатель на нативный объект настроек

        ---

        :Returns:
        - ctypes.c_void_p: Указатель для использования в C++ коде
        """
        return self.__context_ptr

    def set_antialiasing_level(self, level: int) -> Self:
        """
        #### Устанавливает уровень антиалиасинга

        ---

        :Args:
        - level (int): Уровень сглаживания (0 = выключен, 2, 4, 8, 16)

        ---

        :Returns:
        - ContextSettings: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        settings = ContextSettings().set_antialiasing_level(4)
        ```
        """
        LIB_MOON._WindowContextSettings_SetAntialiasingLevel(self.__context_ptr, level)
        return self

    def set_depth_bits(self, bits: int) -> Self:
        """
        #### Устанавливает количество бит для буфера глубины

        ---

        :Args:
        - bits (int): Количество бит (обычно 24 или 32)

        ---

        :Returns:
        - ContextSettings: Возвращает self для цепочки вызовов
        """
        LIB_MOON._WindowContextSettings_SetDepthBits(self.__context_ptr, bits)
        return self

    def set_stencil_bits(self, bits: int) -> Self:
        """
        #### Устанавливает количество бит для буфера трафарета

        ---

        :Args:
        - bits (int): Количество бит (обычно 8)

        ---

        :Returns:
        - ContextSettings: Возвращает self для цепочки вызовов
        """
        LIB_MOON._WindowContextSettings_SetStencilBits(self.__context_ptr, bits)
        return self

    def set_opengl_version(self, major: int, minor: int) -> Self:
        """
        #### Устанавливает версию OpenGL

        ---

        :Args:
        - major (int): Основная версия (например, 3 для OpenGL 3.3)
        - minor (int): Дополнительная версия (например, 3 для OpenGL 3.3)

        ---

        :Returns:
        - ContextSettings: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Запросить OpenGL 3.3
        settings.set_opengl_version(3, 3)
        ```
        """
        LIB_MOON._WindowContextSettings_SetMajorVersion(self.__context_ptr, major)
        LIB_MOON._WindowContextSettings_SetMinorVersion(self.__context_ptr, minor)
        return self

    def set_srgb_capable(self, capable: bool) -> Self:
        """
        #### Включает поддержку sRGB цветового пространства

        ---

        :Args:
        - capable (bool): True для включения sRGB поддержки

        ---

        :Returns:
        - ContextSettings: Возвращает self для цепочки вызовов
        """
        LIB_MOON._WindowContextSettings_SetSrgbCapable(self.__context_ptr, capable)
        return self

    def set_attribute_flags(self, flags: int) -> Self:
        """
        #### Устанавливает флаги атрибутов контекста

        ---

        :Args:
        - flags (int): Битовая маска флагов контекста

        ---

        :Returns:
        - ContextSettings: Возвращает self для цепочки вызовов
        """
        LIB_MOON._WindowContextSettings_SetAttributeFlags(self.__context_ptr, flags)
        return self


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                     Default Window Appearance Settings                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

DEFAULT_WINDOW_HEADER_COLOR: Final[Color] = Color(98, 134, 248).lighten(0.2)  # Цвет фона заголовка окна
DEFAULT_WINDOW_BORDER_COLOR: Final[Color] = Color(98, 134, 248).lighten(0.2)  # Цвет рамки окна

# Белый цвет для текста заголовка окна, обеспечивает хороший контраст
DEFAULT_WINDOW_TITLE_COLOR:  Final[Color] = Color(255, 255, 255)

# Путь к стандартной иконке приложения, используемой если не задана пользовательская
DEFAULT_WINDOW_ICON_PATH:    Final[str]   = "Moon/data/icons/default_app_icon.png"
DEFAULT_WINDOW_ICON_LOCAL_PATH: Final[str] = "./icons/default_app_icon.png"



class Window:
    """
    #### Класс для создания и управления окном приложения

    ---

    :Description:
    - Создает графическое окно для отображения контента
    - Управляет параметрами окна (размер, заголовок, стиль)
    - Обеспечивает рендеринг графики и обработку событий

    ---

    :Features:
    - Поддержка различных стилей оформления окна
    - Настройка вертикальной синхронизации
    - Управление прозрачностью окна
    - Полноэкранные режимы работы
    """

    @final
    class Style:
        """
        #### Перечисление стилей окна

        ---

        :Values:
        - No: Окно без рамки и элементов управления
        - Titlebar: Окно с заголовком
        - Resize: Окно с возможностью изменения размера
        - Close: Окно с кнопкой закрытия
        - FullScreen: Настоящий полноэкранный режим
        - FullScreenDesktop: Псевдо-полноэкранный режим (окно под разрешение рабочего стола)
        - Default: Стандартный набор стилей (Titlebar | Resize | Close)

        ---

        :Note:
        - Стили можно комбинировать через побитовое OR (|)
        - Пример: `Style.Titlebar | Style.Close`
        """
        No = 0                        # Просто окно без каких-либо декораций
        Titlebar = 1 << 0             # Окно с заголовком и кнопкой свернуть
        Resize = 1 << 1               # Окно с изменяемым размером и рамкой
        Close = 1 << 2                # Окно с кнопкой закрытия
        FullScreen = 1 << 3           # Полноэкранный режим с собственным разрешением
        FullScreenDesktop = 1 << 4    # Полноэкранный режим с разрешением рабочего стола
        Default = Titlebar | Resize | Close  # Стандартный набор стилей окон


    def __init__(self, width: int = 800, height: int = 600,
                 title: str = "Moon Window", style: int = Style.Default,
                 vsync: bool = False, alpha: float = 255,
                 context_settings: ContextSettings | None = None):
        """
        #### Инициализация нового окна приложения

        ---

        :Args:
        - width (int): Начальная ширина окна в пикселях (по умолчанию 800)
        - height (int): Начальная высота окна в пикселях (по умолчанию 600)
        - title (str): Заголовок окна (по умолчанию "Moon Window")
        - style (int): Комбинация стилей из Window.Style (по умолчанию Style.Default)
        - vsync (bool): Включение вертикальной синхронизации (по умолчанию False)
        - alpha (float): Уровень прозрачности окна (0-255, по умолчанию 255 - непрозрачное)
        - context_settings (ContextSettings | None): Настройки OpenGL контекста (по умолчанию None - стандартные настройки)

        ---

        :Raises:
        - RuntimeError: При невозможности создать графическое окно

        ---

        :Note:
        - Вертикальная синхронизация (vsync) устраняет артефакты разрыва кадров
        - Прозрачность (alpha) поддерживается не на всех платформах

        ---

        :Example:
        ```python
        # Создание окна со стандартными параметрами
        window = Window()

        # Создание полноэкранного окна
        fullscreen = Window(style=Window.Style.FullScreen)
        ```
        """

        # Обработка кастомного стиля FullScreenDesktop:
        # Если стиль FullScreenDesktop, ширина и высота окна будут равны разрешению экрана.
        if style == Window.Style.FullScreenDesktop:
            width, height = get_screen_resolution() # Получаем максимальное разрешение экрана монитора
            style = Window.Style.No # Переключаем на режим без ничего

        # Используем переданные настройки или создаем новые по умолчанию
        if context_settings is None:
            temp_context_settings = LIB_MOON._WindowContextSettings_Create()
            context_ptr = temp_context_settings
            should_delete_context = True
        else:
            context_ptr = context_settings.get_ptr()
            should_delete_context = False

        # Создаем окно через нативную библиотеку и сохраняем указатель на него
        self.__window_ptr: WindowPtr = LIB_MOON._Window_Create(width, height, title.encode('utf-8'), style, context_ptr)

        # Освобождаем временные настройки контекста (только если мы их создали)
        if should_delete_context:
            LIB_MOON._WindowContextSettings_Delete(temp_context_settings)
        self.__title = title
        self.__window_descriptor = ctypes.windll.user32.FindWindowW(None, self.__title)
        self.__window_alpha: int = alpha

        #self.set_alpha(self.__window_alpha)
        # Получаем стандартную область отображения (View) и сохраняем указатель на нее
        self.__view = self.get_default_view()

        # __wait_fps - ожидание кадров в секунду (максимальное число кадров в секунду, установленное пользователем)становленное пользователем)
        self.__wait_fps = 60

        # __target_fps - целевое число кадров в секунду (используется для вычисления delta-time)
        self.__target_fps = 60

        # Истинные значения текущего FPS и delta-time
        self.__fps = 0.0
        self.__delta = 0.0

        # render_time - время, затраченное на рендер одного кадра
        self.__render_time = 0.0

        # Инициализация переменных для отслеживания FPS (максимальное и минимальное значения)
        self.__min_fps_in_fps_history: float = 0
        self.__max_fps_in_fps_history: float = 0
        LIB_MOON._Window_SetWaitFps(self.__window_ptr, int(self.__wait_fps))

        #////////////////////////////////////////////////////////////////////////////////
        # (             Переменные, необходимые для генерации графика фрейм-тайма            )
        #////////////////////////////////////////////////////////////////////////////////
        self.__info_alpha = 0
        self.__target_info_alpha = 100
        self.__fps_update_timer = 0.0
        self.__fps_history = [] # История значений FPS для построения графика
        self.__max_history = 40 # Максимальное количество точек в истории FPS

        # Настройка шрифта и текстовых элементов для отображения отладочной информации
        self.__info_font = Font.SystemFont("calibri")
        self.__info_text = BaseText(self.__info_font).\
            set_outline_thickness(2).set_outline_color(COLOR_GHOST_WHITE)
        self.__info_text_color_ghost_white = Color(248, 248, 255, 100)
        self.__info_text_color_black = Color(0, 0, 0, 100)
        self.__info_text_color_gray = Color(100, 100, 100, 100)

        # Настройка фонового прямоугольника и линий для графика FPS
        self.__info_bg_color = Color(200, 200, 220, 100)
        self.__info_bg = RectangleShape(100, 200)
        self.__info_line_color = Color(200, 200, 250, 100)
        self.__info_line = LineThinShape()
        self.__fps_line_color_red = Color(200, 0, 0, 100)
        self.__fps_line_color_green = Color(0, 200, 0, 100)
        self.__fps_line = LinesThinShape()
        self.__info_text_fps_color = Color(0, 0, 0, 180)
        self.__info_text_fps = BaseText(self.__info_font)



        #////////////////////////////////////////////////////////////////////////////////

        # Внутренняя переменная для вычисления FPS, render_time, delta-time и т.д.
        self.__clock = Clock()

        # Флаги и константы состояния окна
        self.__view_info = False            # Флаг отображения информации о рендере (FPS, дельта и т.д.)
        self.__exit_key = "esc"             # Клавиша для закрытия окна (по умолчанию Esc)
        self.__vsync = vsync                # Флаг вертикальной синхронизации
        self.__clear_color = COLOR_WHITE    # Цвет по умолчанию для очистки окна

        # Текущий размер окна и флаг для отслеживания изменения размера
        self.__width = width                # Ширина окна в текущем кадре
        self.__height = height              # Высота окна в текущем кадре
        self.__end_width = width            # Ширина окна в прошлом кадре (для отслеживания изменений)
        self.__end_height = height          # Высота окна в прошлом кадре (для отслеживания изменений)
        self.__resized: bool = False        # Флаг, указывающий, был ли изменен размер окна в текущем кадре

        self.__start_time = time()              # Время открытия окна (для get_global_timer)

        self.__cursor_visibility: bool = True   # Флаг видимости курсора мыши

        self.set_vertical_sync(vsync)           # Устанавливает вертикальную синхронизацию при инициализации

        self.__ghosting: bool = False
        self.__ghosting_min_value: int = 30
        self.__ghosting_at_value: int = 255
        self.__ghosting_interpolation: float = 0.1

        self.__active: bool = True
        self.__cursor: SystemCursors = SystemCursors.Arrow
        self.__using_keybinding_for_open_fps_monitor: bool = False
        self.__fps_monitor_key_binding: str = "alt+f"
        self.__fps_monitor_opened: bool = True

        # Значения вычисляющиеся с кеширование
        self.__cached_window_center: Vector2f = Vector2f(width / 2, height / 2)

        # Флаг который будет реализован в будщем
        self.__using_custom_window: bool = False


        self.__title_color: Color | None = None
        self.__header_color: Color | None = None
        self.__border_color: Color | None = None
        self.__icon_path: str | None = None


        self.set_title_color(DEFAULT_WINDOW_TITLE_COLOR)
        self.set_header_color(DEFAULT_WINDOW_HEADER_COLOR)
        self.set_border_color(DEFAULT_WINDOW_BORDER_COLOR)

        try:
            self.set_icon_from_path(DEFAULT_WINDOW_ICON_PATH)
        except:
            try:
                self.set_icon_from_path(DEFAULT_WINDOW_ICON_LOCAL_PATH)
            except:
                try:
                    path = find_module_installation_path('Moon') + "/data/icons/default_app_icon.png"
                    self.set_icon_from_path(path)
                except:
                    raise "App Icon path not found"

    def set_fullscreen_desktop(self) -> Self:
        ctypes.windll.user32.ShowWindow(self.__window_descriptor, 3)

    def set_fps_monitor_opened(self, value: bool) -> Self:
        self.__fps_monitor_opened = value
        return self

    def enable_fpsmonitor_keybinding(self, value: bool = True) -> Self:
        """
        #### Включает/выключает горячие клавиши для FPS монитора

        ---

        :Args:
        - value (bool): True - включить, False - выключить (по умолчанию True)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов
        """
        self.__using_keybinding_for_open_fps_monitor = value
        return self

    def get_using_keybindind_for_fpsmonitor(self) -> bool:
        """
        #### Проверяет, включены ли горячие клавиши для FPS монитора

        ---

        :Returns:
        - bool: True если горячие клавиши включены, False если выключены
        """
        return self.__using_keybinding_for_open_fps_monitor

    def get_fpsmonitor_keybinding(self) -> str:
        """
        #### Возвращает текущую комбинацию клавиш для FPS монитора

        ---

        :Returns:
        - str: Строка с комбинацией клавиш
        """
        return self.__fps_monitor_key_binding

    def get_fpsmonitor_opened_for_keybinding(self) -> bool:
        """
        #### Проверяет, открыт ли FPS монитор через горячие клавиши

        ---

        :Returns:
        - bool: True если монитор открыт, False если закрыт
        """
        return self.__fps_monitor_opened

    def set_fpsmonitor_keybinding(self, keys: str) -> Self:
        """
        #### Устанавливает комбинацию клавиш для FPS монитора

        Пример: `ctrl+f`

        ---

        :Args:
        - keys (str): Строка с комбинацией клавиш

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов
        """
        self.__fps_monitor_key_binding = keys
        return self

    def set_icon_from_path(self, path: str) -> bool:
        """
        #### Устанавливает иконку окна из файла

        ---

        :Args:
        - path (str): Путь к файлу иконки (.ico, .png, .bmp)

        ---

        :Returns:
        - bool: True если иконка успешно установлена, False при ошибке

        ---

        :Note:
        - Поддерживает форматы .ico, .png, .bmp
        - Рекомендуемый размер: 32x32 или 16x16 пикселей

        ---

        :Example:
        ```python
        window.set_icon_from_path("icon.ico")  # Установить иконку
        ```
        """
        if os.path.exists(path) is False:
            raise FileNotFoundError(f"Icon file not found: {path}")
        result = LIB_MOON._Window_SetIconFromPath(self.__window_ptr, path.encode('utf-8'))
        if result:
            self.__icon_path = path
        return result

    def get_icon_path(self) -> str | None:
        """
        #### Возвращает путь к текущей иконке окна

        ---

        :Returns:
        - str | None: Путь к файлу иконки или None если не установлена

        ---

        :Example:
        ```python
        icon_path = window.get_icon_path()
        ```
        """
        return self.__icon_path

    def set_title_color(self, color: Color) -> Self:
        """
        #### Устанавливает цвет заголовка окна (Windows 10+)

        ---

        :Args:
        - color (Color): Цвет заголовка в формате RGB

        ---

        :Note:
        - Работает только в Windows 10 и новее
        - Цвет автоматически преобразуется в BGR формат для Windows API
        - По умолчанию используется DEFAULT_WINDOW_TITLE_COLOR

        ---

        :Example:
        ```python
        window.set_title_color(Color(255, 0, 0))  # Красный заголовок
        ```
        """
        self.__title_color = color
        bgr_value = (color.b << 16) | (color.g << 8) | color.r
        color_value = ctypes.wintypes.DWORD(bgr_value)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            self.__window_descriptor,
            36,  # DWMWA_CAPTION_COLOR
            ctypes.byref(color_value),
            ctypes.sizeof(color_value)
        )
        return self

    def set_header_color(self, color: Color) -> Self:
        """
        #### Устанавливает цвет заголовка окна (Windows 10+)

        ---

        :Args:
        - color (Color): Цвет заголовка в формате RGB

        ---

        :Note:
        - Работает только в Windows 10 и новее
        - Цвет автоматически преобразуется в BGR формат для Windows API
        - По умолчанию используется DEFAULT_WINDOW_HEADER_COLOR

        ---

        :Example:
        ```python
        window.set_header_color(Color(0, 255, 0))  # Зеленый заголовок
        ```
        """
        self.__header_color = color
        bgr_value = (color.b << 16) | (color.g << 8) | color.r
        color_value = ctypes.wintypes.DWORD(bgr_value)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            self.__window_descriptor,
            35,  # DWMWA_CAPTION_COLOR
            ctypes.byref(color_value),
            ctypes.sizeof(color_value)
        )
        return self

    def set_border_color(self, color: Color) -> Self:
        """
        #### Устанавливает цвет рамки окна (Windows 10+)

        ---

        :Args:
        - color (Color): Цвет рамки в формате RGB

        ---

        :Note:
        - Работает только в Windows 10 и новее
        - Цвет автоматически преобразуется в BGR формат для Windows API
        - По умолчанию используется DEFAULT_WINDOW_BORDER_COLOR

        ---

        :Example:
        ```python
        window.set_border_color(Color(0, 0, 255))  # Синяя рамка
        ```
        """
        self.__border_color = color
        bgr_value = (color.b << 16) | (color.g << 8) | color.r
        color_value = ctypes.wintypes.DWORD(bgr_value)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            self.__window_descriptor,
            34,  # DWMWA_BORDER_COLOR
            ctypes.byref(color_value),
            ctypes.sizeof(color_value)
        )
        return self

    def get_title_color(self) -> Color | None:
        """
        #### Возвращает текущий цвет заголовка окна

        ---

        :Returns:
        - Color | None: Текущий цвет заголовка или None если не установлен

        ---

        :Example:
        ```python
        color = window.get_title_color()
        ```
        """
        return self.__title_color

    def get_header_color(self) -> Color | None:
        """
        #### Возвращает текущий цвет заголовка окна

        ---

        :Returns:
        - Color | None: Текущий цвет заголовка или None если не установлен

        ---

        :Example:
        ```python
        color = window.get_header_color()
        ```
        """
        return self.__header_color

    def get_border_color(self) -> Color | None:
        """
        #### Возвращает текущий цвет рамки окна

        ---

        :Returns:
        - Color | None: Текущий цвет рамки или None если не установлен

        ---

        :Example:
        ```python
        color = window.get_border_color()
        ```
        """
        return self.__border_color

    @final
    def enable_rounded_corners(self) -> Self:
        """
        #### Включает скругленные углы для окна (Windows 11+)

        ---

        :Description:
        - Применяет современный стиль с закругленными углами к окну
        - Работает только в Windows 11 и новее
        - Для других ОС или версий Windows эффекта не будет

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        window.enable_rounded_corners()
        ```
        """
        DWM_API.DwmSetWindowAttribute(
            self.__window_descriptor,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(ctypes.c_int(2)),
            ctypes.sizeof(ctypes.c_int(2)))
        return self

    @final
    def set_system_cursor(self, cursor: SystemCursors) -> Self:
        """
        #### Устанавливает системный курсор для окна

        ---

        :Args:
        - cursor (SystemCursors): Тип курсора из перечисления SystemCursors

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        window.set_system_cursor(SystemCursors.Hand)  # Курсор в виде руки
        ```
        """
        self.__cursor = cursor
        LIB_MOON._Window_SetSystemCursor(self.__window_ptr, cursor)
        return self

    @final
    def get_cursor(self) -> SystemCursors:
        """
        #### Возвращает текущий системный курсор окна

        ---

        :Returns:
        - SystemCursors: Текущий установленный курсор

        ---

        :Example:
        ```python
        if window.get_cursor() == SystemCursors.Wait:
            print("Сейчас установлен курсор ожидания")
        ```
        """
        return self.__cursor

    @final
    def get_active(self) -> bool:
        """
        #### Проверяет, является ли окно активным

        ---

        :Description:
        - Возвращает True, если окно в данный момент окное не заблокированно
        - Возвращает False, если окно заблокированно програмно

        ---

        :Returns:
        - bool: True если окно активно, False в противном случае

        ---

        :Example:
        ```python
        # Обновлять содержимое только для активного окна
        if window.get_active():
            ...
        ```
        """
        return self.__active

    @final
    def enable_vsync(self) -> Self:
        self.__vsync = True
        LIB_MOON._Window_SetVsync(self.__window_ptr, self.__vsync)

    @final
    def enable_ghosting(self, value: bool = True) -> Self:
        """
        #### Включает/выключает эффект "призрачного" окна

        ---

        :Description:
        - При включении делает окно полупрозрачным при потере фокуса
        - Эффект автоматически регулирует прозрачность между минимальным и максимальным значениями

        ---

        :Args:
        - value (bool): True - включить эффект, False - выключить (по умолчанию True)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Включить эффект призрачного окна
        window.enable_ghosting()

        # Выключить эффект
        window.enable_ghosting(False)
        ```
        """
        self.__ghosting = value
        return self

    @final
    def get_ghosting(self) -> bool:
        """
        #### Проверяет, включен ли эффект призрачного окна

        ---

        :Returns:
        - bool: True если эффект включен, False если выключен

        ---

        :Example:
        ```python
        if window.get_ghosting():
            print("Эффект призрачного окна активен")
        ```
        """
        return self.__ghosting

    @final
    def set_ghosting_min_alpha(self, alpha: int) -> Self:
        """
        #### Устанавливает минимальную прозрачность для эффекта призрачного окна

        ---

        :Args:
        - alpha (int): Значение прозрачности (0-255), где 0 - полностью прозрачное

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Note:
        - Действует только при включенном эффекте ghosting

        ---

        :Example:
        ```python
        # Установить минимальную прозрачность 50%
        window.set_ghosting_min_alpha(128)
        ```
        """
        self.__ghosting_min_value = alpha
        return self

    @final
    def get_ghosting_min_alpha(self) -> int:
        """
        #### Возвращает текущее минимальное значение прозрачности для эффекта призрачного окна

        ---

        :Returns:
        - int: Текущее значение минимальной прозрачности (0-255)

        ---

        :Example:
        ```python
        print(f"Текущая минимальная прозрачность: {window.get_ghosting_min_alpha()}")
        ```
        """
        return self.__ghosting_min_value

    @final
    def set_alpha(self, alpha: int):
        """
        #### Устанавливает глобальную прозрачность окна

        ---

        :Args:
        - alpha (int): Уровень прозрачности (0 - полностью прозрачное, 255 - непрозрачное)

        ---

        :Note:
        - Работает только на Windows через WinAPI
        - Требует стиль WS_EX_LAYERED
        - `! Кроссплатформенные решения еще не реализованы !`

        ---

        :Example:
        ```python
        window.set_alpha(100)
        ```
        """
        self.__window_descriptor = ctypes.windll.user32.FindWindowW(None, self.__title)
        self.__window_alpha = alpha  # Конвертируем в диапазон 0-255

        # Устанавливаем стиль слоистого окна
        style = ctypes.windll.user32.GetWindowLongW(self.__window_descriptor, -20)  # GWL_EXSTYLE = -20
        ctypes.windll.user32.SetWindowLongW(self.__window_descriptor, -20, style | 0x00080000)  # WS_EX_LAYERED = 0x00080000

        # Применяем прозрачность
        ctypes.windll.user32.SetLayeredWindowAttributes(
            self.__window_descriptor,
            0,  # Ключ цвета (не используется)
            int(self.__window_alpha),  # Значение альфа-канала
            2  # LWA_ALPHA = 2
        )

    @final
    def get_alpha(self) -> float:
        """
        #### Возвращает текущий уровень прозрачности окна

        ---

        :Description:
        - Возвращает значение в диапазоне от 0 (полная прозрачность) до 255 (полная непрозрачность)
        - Соответствует последнему установленному значению через set_alpha()

        ---

        :Returns:
        - float: Текущий уровень прозрачности окна

        ---

        :Example:
        ```python
        # Проверить текущую прозрачность
        transparency = window.get_alpha()
        print(f"Текущая прозрачность: {transparency}")
        ```
        """
        return self.__window_alpha

    @final
    def close(self) -> None:
        """
        #### Полностью закрывает окно и освобождает ресурсы

        ---

        :Description:
        - Завершает работу графического контекста
        - Освобождает системные ресурсы
        - Удаляет все связанные с окном объекты

        ---

        :Note:
        - После вызова этого метода окно нельзя использовать повторно
        - Рекомендуется вызывать в конце работы приложения

        ---

        :Example:
        ```python
        # Стандартный цикл закрытия
        window.close()
        ```
        """
        LIB_MOON._Window_Close(self.__window_ptr)

    @final
    def hide_cursor(self) -> Self:
        """
        #### Скрывает системный курсор в области окна

        ---

        :Description:
        - Делает курсор невидимым при наведении на окно
        - Сохраняет состояние для последующего восстановления

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Для режима полноэкранной игры
        window.hide_cursor().set_fullscreen(True)
        ```
        """
        LIB_MOON._Window_SetCursorVisibility(self.__window_ptr, False)
        self.__cursor_visibility = False
        return self

    @final
    def show_cursor(self) -> Self:
        """
        #### Восстанавливает видимость курсора в области окна

        ---

        :Description:
        - Показывает стандартный курсор при наведении на окно
        - Восстанавливает предыдущее состояние курсора

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Для обычного оконного режима
        window.show_cursor().set_fullscreen(False)
        ```
        """
        LIB_MOON._Window_SetCursorVisibility(self.__window_ptr, True)
        self.__cursor_visibility = True
        return self

    @final
    def get_cursor_visibility(self) -> bool:
        """
        #### Проверяет видимость курсора мыши в окне

        ---

        :Description:
        - Возвращает текущее состояние видимости курсора
        - Соответствует последнему установленному значению через show_cursor()/hide_cursor()

        ---

        :Returns:
        - bool: True если курсор видим, False если скрыт

        ---

        :Example:
        ```python
        if window.get_cursor_visibility():
            print("Курсор в настоящее время виден")
        else:
            print("Курсор скрыт")
        ```
        """
        return self.__cursor_visibility

    @final
    def set_max_fps_history(self, number: int) -> Self:
        """
        #### Устанавливает глубину истории значений FPS

        ---

        :Description:
        - Определяет сколько последних значений FPS сохраняется для анализа
        - Используется для построения графиков производительности
        - Большие значения требуют больше памяти, но дают более точную статистику

        ---

        :Args:
        - number (int): Максимальное количество сохраняемых значений (должно быть > 0)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Raises:
        - ValueError: Если передано неположительное число

        ---

        :Example:
        ```python
        # Сохранять последние 120 значений FPS (2 секунды при 60 FPS)
        window.set_max_fps_history(120)
        ```
        """
        if number <= 0:
            raise ValueError("History size must be positive")
        self.__max_history = number
        return self

    @final
    def get_max_fps_history(self) -> int:
        """
        #### Возвращает текущий размер истории FPS

        ---

        :Description:
        - Показывает сколько последних значений FPS сохраняется в памяти
        - Значение по умолчанию обычно составляет 60 (1 секунда при 60 FPS)

        ---

        :Returns:
        - int: Текущая глубина истории значений FPS

        ---

        :Example:
        ```python
        print(f"Текущий размер истории FPS: {window.get_max_fps_history()}")
        ```
        """
        return self.__max_history

    @final
    def convert_window_coords_to_view_coords(self, x: float, y: float, view: View) -> Vector2f:
        """
        #### Преобразует экранные координаты в мировые относительно камеры

        ---

        :Description:
        - Конвертирует координаты из пикселей экрана в мировые координаты игры
        - Учитывает текущее положение, масштаб и поворот камеры (View)
        - Полезно для обработки ввода (мышь/тач) в игровом пространстве

        ---

        :Args:
        - x (float): Горизонтальная позиция в пикселях (от левого края окна)
        - y (float): Вертикальная позиция в пикселях (от верхнего края окна)
        - view (View): Камера/вид, относительно которой выполняется преобразование

        ---

        :Returns:
        - Vector2f: Преобразованные координаты в игровом пространстве

        ---

        :Example:
        ```python
        # Получить мировые координаты клика мыши
        mouse_pos = window.convert_window_coords_to_view_coords(mouse_x, mouse_y, game_view)
        print(f"Клик в мире игры: {mouse_pos.x}, {mouse_pos.y}")
        ```
        """
        return Vector2f(
            LIB_MOON._Window_MapPixelToCoordsX(self.__window_ptr, x, y, view.get_ptr()),
            LIB_MOON._Window_MapPixelToCoordsY(self.__window_ptr, x, y, view.get_ptr()),
        )

    @final
    def convert_view_coords_to_window_coords(self, x: float, y: float, view: View) -> Vector2f:
        """
        #### Преобразует мировые координаты в экранные относительно камеры

        ---

        :Description:
        - Конвертирует координаты из игрового пространства в пиксели экрана
        - Учитывает текущее положение, масштаб и поворот камеры (View)
        - Полезно для позиционирования UI элементов в мировых координатах

        ---

        :Args:
        - x (float): Горизонтальная позиция в игровом пространстве
        - y (float): Вертикальная позиция в игровом пространстве
        - view (View): Камера/вид, относительно которой выполняется преобразование

        ---

        :Returns:
        - Vector2f: Преобразованные экранные координаты в пикселях

        ---

        :Example:
        ```python
        # Получить экранные координаты игрового объекта
        screen_pos = window.convert_view_coords_to_window_coords(object_x, object_y, game_view)
        print(f"Объект на экране: {screen_pos.x}, {screen_pos.y}")
        ```
        """
        return Vector2f(
            LIB_MOON._Window_MapCoordsToPixelX(self.__window_ptr, x, y, view.get_ptr()),
            LIB_MOON._Window_MapCoordsToPixelY(self.__window_ptr, x, y, view.get_ptr()),
        )

    @final
    def get_default_view(self) -> View:
        """
        #### Возвращает стандартное представление (View) окна

        ---

        :Description:
        - Возвращает View, соответствующее полному размеру окна
        - Начало координат (0,0) в левом верхнем углу
        - Не содержит трансформаций (масштаб=1, поворот=0)
        - Автоматически обновляется при изменении размера окна

        ---

        :Returns:
        - View: Объект стандартного представления

        ---

        :Example:
        ```python
        # Сброс камеры к стандартному виду (это просто пример)
        camera = window.get_default_view()
        ```
        """
        return View.from_view_ptr(LIB_MOON._Window_GetDefaultView(self.__window_ptr))

    @final
    def set_position(self, x: int, y: int) -> Self:
        """
        #### Устанавливает позицию окна на экране

        ---

        :Description:
        - Позиционирует окно относительно верхнего левого угла экрана
        - Координаты указываются в пикселях

        ---

        :Args:
        - x (int): Горизонтальная позиция (X координата)
        - y (int): Вертикальная позиция (Y координата)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Позиционировать окно в точке (100, 200)
        window.set_position(100, 200)
        ```
        """
        LIB_MOON._Window_SetPosition(self.__window_ptr, x, y)
        return self

    @final
    def set_size(self, width: int, height: int) -> Self:
        """
        #### Изменяет размер окна

        ---

        :Description:
        - Устанавливает новые размеры клиентской области окна
        - Минимальный/максимальный размер зависит от системы
        - Может вызвать событие `Resized`

        ---

        :Args:
        - width (int): Новая ширина в пикселях (>0)
        - height (int): Новая высота в пикселях (>0)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Raises:
        - ValueError: При недопустимых размерах

        ---

        :Example:
        ```python
        # Установить размер 800x600
        window.set_size(800, 600)
        ```
        """
        if width <= 0 or height <= 0:
            raise ValueError("Window dimensions must be positive")
        LIB_MOON._Window_SetSize(self.__window_ptr, width, height)
        return self

    @final
    def get_ptr(self) -> WindowPtr:
        """
        #### Возвращает нативный указатель на окно

        ---

        :Description:
        - Предоставляет доступ к низкоуровневому объекту окна
        - Используется для интеграции с нативным кодом

        ---

        :Returns:
        - WindowPtr: Указатель на внутренний объект окна

        ---

        :Note:
        - Только для продвинутого использования
        - Не изменяйте объект напрямую

        ---

        :Example:
        ```python
        # Передать указатель в нативную функцию
        native_function(window.get_ptr())
        ```
        """
        return self.__window_ptr

    @final
    def get_size(self) -> Vector2i:
        """
        #### Возвращает текущий размер клиентской области окна

        ---

        :Description:
        - Возвращает размеры в пикселях
        - Учитывает только рабочую область (без рамок и заголовка)
        - Размеры обновляются при изменении окна

        ---

        :Returns:
        - Vector2i: Вектор с шириной (x) и высотой (y) окна

        ---

        :Example:
        ```python
        # Получить текущий размер окна
        size = window.get_size()
        print(f"Ширина: {size.x}, Высота: {size.y}")
        ```
        """
        return Vector2i(
            LIB_MOON._Window_GetSizeWidth(self.__window_ptr),
            LIB_MOON._Window_GetSizeHeight(self.__window_ptr)
        )

    @final
    def get_center(self, use_cache: bool = True) -> Vector2f:
        """
        #### Возвращает координаты центра окна

        ---

        :Description:
        - Вычисляет центр относительно клиентской области
        - Возвращает координаты в пикселях
        - Полезно для центрирования элементов

        ---

        :Args:
        - use_cache: bool - использовать ли кэш ( не обращаться каждый раз к системе для получения данных об окне )

        ---

        :Returns:
        - Vector2f: Вектор с координатами центра (x, y)

        ---

        :Example:
        ```python
        # Поместить спрайт в центр окна
        sprite.position = window.get_center()
        ```
        """
        if use_cache:
            return self.__cached_window_center
        size = self.get_size()
        return Vector2f(
            size.x / 2,
            size.y / 2
        )

    @final
    def get_position(self) -> Vector2i:
        """
        #### Возвращает позицию окна на экране

        ---

        :Description:
        - Координаты относительно верхнего левого угла экрана
        - Учитывает системные рамки окна
        - Позиция в пикселях

        ---

        :Returns:
        - Vector2i: Вектор с координатами (x, y) верхнего левого угла

        ---

        :Example:
        ```python
        # Проверить положение окна
        pos = window.get_position()
        print(f"Окно расположено в ({pos.x}, {pos.y})")
        ```
        """
        return Vector2i(
            LIB_MOON._Window_GetPositionX(self.__window_ptr),
            LIB_MOON._Window_GetPositionY(self.__window_ptr)
        )

    @final
    def view_info(self) -> None:
        """
        #### Отображает отладочную информацию о производительности

        ---

        :Description:
        - Показывает FPS, время рендеринга и дельта-тайм
        - Включает график изменения FPS за последние кадры
        - Адаптивная прозрачность при наведении курсора
        - Требует включения флага __view_info

        ---

        :Features:
        - Динамический график FPS с цветовой индикацией
        - Подсветка при наведении в область информации
        - Подробная текстовая статистика
        - Индикатор активности окна

        ---

        :Note:
        - Для активации установите window.set_view_info()
        - Автоматически использует стандартный View
        """

        if not self.__view_info:
            return

        if not self.__fps_monitor_opened:
            return

        # Устанавливаем представление по умолчанию, чтобы информация отображалась в экранных координатах
        self.set_view(self.get_default_view().set_size(*self.get_size().xy).set_center(*self.get_center().xy))

        # Изменяем прозрачность информационного блока в зависимости от положения курсора
        mp = MouseInterface.get_position_in_window(self)

        if mp.x < 250 and mp.y < 200: # Если курсор в верхнем левом углу
            self.__target_info_alpha = 200
        else:
            self.__target_info_alpha = 50

        # Анимируем прозрачность информационного блока
        self.__info_alpha += (self.__target_info_alpha - self.__info_alpha) * 0.3 * self.get_render_time() * 10
        self.__info_bg_color.set_alpha(int(self.__info_alpha))
        self.__info_line_color.set_alpha(int(self.__info_alpha))
        self.__info_text_fps_color.set_alpha(int(self.__info_alpha))
        self.__fps_line_color_green.set_alpha(int(self.__info_alpha))
        self.__fps_line_color_red.set_alpha(int(self.__info_alpha))
        self.__info_text_color_black.set_alpha(int(self.__info_alpha))
        self.__info_text_color_gray.set_alpha(int(self.__info_alpha))
        self.__info_text_color_ghost_white.set_alpha(int(self.__info_alpha))

        # Основная информация: FPS
        self.__info_text.set_size(30)
        self.__info_text.set_outline_color(self.__info_text_color_ghost_white)
        self.__info_text.set_style(TextStyle.BOLD)
        if self.get_wait_fps() >= FPS_UNLIMIT_CONST:
            self.__info_text.set_text(f"FPS: {self.get_fps():.0f} / unlimit")
        else:
            self.__info_text.set_text(f"FPS: {self.get_fps():.0f} / {self.get_wait_fps():.0f}")
        self.__info_text.set_position(10, 5)
        self.__info_text.set_color(self.__info_text_color_black)
        self.draw(self.__info_text)


        width =  self.__info_text.get_text_width()
        self.__info_text.set_position(width + 15, 9)
        self.__info_text.set_size(14)
        self.__info_text.set_style(TextStyle.REGULAR)
        self.__info_text.set_text(f"max: {self.__max_fps_in_fps_history:.0f}")
        self.draw(self.__info_text)

        self.__info_text.set_position(width + 15, 20)
        self.__info_text.set_size(14)
        self.__info_text.set_text(f"min: {self.__min_fps_in_fps_history:.0f}")
        self.draw(self.__info_text)


        # Дополнительная информация: время рендеринга
        self.__info_text.set_style(TextStyle.REGULAR)
        self.__info_text.set_size(18)
        self.__info_text.set_text(f"Render time: {self.get_render_time()*1000:.1f}ms")
        self.__info_text.set_position(10, 35)
        self.__info_text.set_color(self.__info_text_color_gray)
        self.draw(self.__info_text)

        # Дополнительная информация: дельта-тайм
        self.__info_text.set_text(f"Delta: {self.get_delta():.3f}")
        self.__info_text.set_position(10, 55)
        self.draw(self.__info_text)

        # Дополнительная информация: вертикальная синхронизация
        self.__info_text.set_text(f"Vsync: {self.__vsync}")
        self.__info_text.set_position(10, 75)
        # Цвет текста Vsync зависит от ее состояния (красный - выключена, зеленый - включена)
        self.__info_text.set_color(self.__fps_line_color_red if not self.__vsync else self.__fps_line_color_green)
        self.draw(self.__info_text)

        self.__info_text.set_position(10, 75 + 125)
        self.__info_text.set_text(f"Active: {self.__active}")
        self.draw(self.__info_text)

        # График фреймтайма
        graph_width = 200
        graph_height = 100
        graph_x = 10
        graph_y = 100

        # Фон графика
        self.__info_bg.set_size(graph_width, graph_height)
        self.__info_bg.set_position(graph_x, graph_y)
        self.__info_bg.set_color(self.__info_bg_color)
        self.draw(self.__info_bg)

        # Сетка графика
        # Максимальное значение FPS для масштабирования графика
        max_fps = max(self.__fps_history) if self.__fps_history else self.__wait_fps
        for i in range(5): # Рисуем 5 горизонтальных линий сетки
            y_pos = graph_y + i * (graph_height / 4)
            self.__info_line.set_start_point(graph_x, y_pos)
            self.__info_line.set_end_point(graph_x + graph_width, y_pos)
            self.__info_line.set_color(self.__info_line_color)
            self.draw(self.__info_line)

            # Отображаем числовые значения FPS по оси Y
            fps_value = max_fps - (i * (max_fps / 4))
            self.__info_text_fps.set_size(10)
            self.__info_text_fps.set_text(f"{fps_value:.0f}")
            self.__info_text_fps.set_position(graph_x + graph_width + 3, y_pos - 7)
            self.__info_text_fps.set_color(self.__info_text_fps_color)
            self.draw(self.__info_text_fps)

        # Линия графика FPS
        if len(self.__fps_history) > 1: # Рисуем линию только если есть хотя бы 2 точки в истории
            self.__fps_line.clear() # Очищаем предыдущие точки линии

            for i, fps in enumerate(self.__fps_history):
                # Вычисляем координаты точки на графике
                x = graph_x + (i * graph_width / (self.__max_history - 1))
                y = graph_y + graph_height - (fps * graph_height / max_fps)
                # Выбираем цвет линии в зависимости от производительности
                color = self.__fps_line_color_green if fps >= max_fps * 0.5 else self.__fps_line_color_red
                self.__fps_line.append_point_to_end(x, y, color) # Добавляем точку к линии

            self.draw(self.__fps_line) # Отрисовываем линию

    @final
    def set_vertical_sync(self, value: bool) -> Self:
        """
        #### Управляет вертикальной синхронизацией (VSync)

        ---

        :Description:
        - Синхронизирует частоту кадров с частотой обновления монитора
        - Устраняет артефакты разрыва изображения
        - Может уменьшить нагрузку на GPU

        ---

        :Args:
        - value (bool): True - включить VSync, False - выключить

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Включить вертикальную синхронизацию
        window.set_vertical_sync(True)
        ```
        """
        self.__vsync = value
        LIB_MOON._Window_SetVsync(self.__window_ptr, value)
        return self

    @final
    def set_exit_key(self, key: str) -> Self:
        """
        #### Устанавливает клавишу для закрытия окна

        ---

        :Description:
        - Определяет клавишу, которая будет закрывать окно при нажатии
        - Использует системное отслеживание клавиатуры
        - По умолчанию `esc`

        ---

        :Args:
        - key (str): Идентификатор клавиши в формате
                    (например: "esc", "space", "ctrl+c")

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Закрывать окно по Escape
        window.set_exit_key("esc")

        # Закрывать по комбинации Ctrl+Q
        window.set_exit_key("ctrl+q")
        ```
        """
        self.__exit_key = key
        return self

    @final
    def get_exit_key(self) -> str:
        """
        #### Возвращает текущую клавишу для закрытия окна

        ---

        :Description:
        - Возвращает None если клавиша не установлена
        - Значение соответствует последнему set_exit_key()

        ---

        :Returns:
        - str: Текущая установленная клавиша или None

        ---

        :Example:
        ```python
        if window.get_exit_key() == "esc":
            print("Окно закрывается по Escape")
        ```
        """
        return self.__exit_key

    @final
    def set_view_info(self, value: bool = True) -> Self:
        """
        #### Управляет отображением отладочной информации

        ---

        :Description:
        - Включает/выключает панель с FPS и статистикой рендеринга
        - Отображается в верхнем левом углу окна
        - Полезно для отладки производительности

        ---

        :Args:
        - value (bool): Флаг отображения (True - показать, False - скрыть)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Показать информацию
        window.set_view_info(True)

        # Скрыть информацию
        window.set_view_info(False)
        ```
        """
        self.__view_info = value
        return self

    @final
    def get_delta(self) -> float:
        """
        #### Возвращает коэффициент дельта-тайм

        ---

        :Description:
        - Показывает отношение реального FPS к целевому
        - Значение 1.0 означает идеальное соответствие
        - <1.0 - рендеринг медленнее целевого
        - >1.0 - рендеринг быстрее целевого
        - Используется для нормализации игрового времени

        ---

        :Returns:
        - float: Коэффициент дельта-тайм

        ---

        :Example:
        ```python
        # Нормализовать движение относительно FPS
        distance = speed * window.get_delta()
        ```
        """
        return self.__delta

    @final
    def set_target_fps(self, fps: int) -> Self:
        """
        #### Устанавливает эталонный FPS для расчетов

        ---

        :Description:
        - Определяет целевую частоту кадров для расчета delta-time
        - Не ограничивает фактический FPS рендеринга
        - Используется для нормализации игрового времени

        ---

        :Args:
        - fps (int): Целевые кадры в секунду (>0)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Установить 60 FPS как эталон для расчетов
        window.set_target_fps(60)
        ```
        """
        self.__target_fps = fps
        return self

    @final
    def get_target_fps(self) -> int:
        """
        #### Возвращает текущий эталонный FPS

        ---

        :Description:
        - Показывает значение, установленное set_target_fps()
        - По умолчанию обычно 60 FPS

        ---

        :Returns:
        - int: Текущее целевое значение FPS

        ---

        :Example:
        ```python
        print(f"Эталонная частота: {window.get_target_fps()} FPS")
        ```
        """
        return self.__target_fps

    @final
    def set_wait_fps(self, fps: int) -> Self:
        """
        #### Устанавливает ограничение частоты кадров

        ---

        :Description:
        - Ограничивает максимальный FPS рендеринга
        - Реальное значение может отличаться из-за:
        - Ограничений системы
        - Сложности сцены
        - Нагрузки на GPU/CPU

        ---

        :Args:
        - fps (int): Максимальные кадры в секунду (FPS_UNLIMIT_CONST = без ограничений)
        - `! Снятие ограничения может привести к перегереву устройства и последующего сбрасывания частот !`

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Ограничить 60 FPS для экономии батареи
        window.set_wait_fps(60)

        # Снять ограничение FPS
        window.set_wait_fps(FPS_UNLIMIT_CONST)
        ```
        """
        LIB_MOON._Window_SetWaitFps(self.__window_ptr, int(fps))
        self.__wait_fps = fps
        return self

    @final
    def get_wait_fps(self) -> int:
        """
        #### Возвращает текущее ограничение FPS

        ---

        :Description:
        - Показывает значение, установленное set_wait_fps()
        - 0 означает отсутствие ограничений

        ---

        :Returns:
        - int: Текущее ограничение FPS (FPS_UNLIMIT_CONST = без лимита)

        ---

        :Example:
        ```python
        if window.get_wait_fps() == FPS_UNLIMIT_CONST:
            print("Ограничение FPS отключено")
        ```
        """
        return self.__wait_fps

    @final
    def get_render_time(self, factor: float = 1) -> float:
        """
        #### Возвращает время рендеринга последнего кадра

        ---

        :Description:
        - Измеряет только время отрисовки (рендеринг)
        - Не включает время логики и ожидания
        - Полезно для оптимизации производительности

        ---

        :Args:
        - factor (float): Множитель для преобразования единиц (по умолчанию 1 = секунды)

        ---

        :Returns:
        - float: Время в секундах (или других единицах при factor != 1)

        ---

        :Example:
        ```python
        # Получить время в секундах
        render_sec = window.get_render_time()

        # Получить время в миллисекундах
        render_ms = window.get_render_time(1000)
        ```
        """
        return self.__render_time * factor

    @final
    def get_fps(self) -> float:
        """
        #### Возвращает текущую частоту кадров

        ---

        :Description:
        - Рассчитывается как среднее за последние N кадров
        - Учитывает только время рендеринга
        - Может колебаться в зависимости от нагрузки

        ---

        :Returns:
        - float: Текущее значение FPS

        ---

        :Example:
        ```python
        # Адаптивное качество при падении FPS
        if window.get_fps() < 30:
            decrease_quality()
        ```
        """
        return self.__fps

    @final
    def get_global_timer(self, factor: float = 1.0) -> float:
        """
        #### Возвращает время работы приложения

        ---

        :Description:
        - Отсчет начинается при создании окна
        - Независит от пауз/остановок
        - Полезно для анимаций и таймеров

        ---

        :Args:
        - factor (float): Множитель времени (1.0 = реальное время)

        ---

        :Returns:
        - float: Время в секундах × factor

        ---

        :Example:
        ```python
        # Простое измерение времени
        run_time = window.get_global_timer()

        # Ускоренное время для эффектов
        fast_time = window.get_global_timer(2.0)
        ```
        """
        return (time() - self.__start_time) * factor

    @final
    def set_view(self, view: View) -> Self:
        """
        #### Устанавливает активную камеру/область просмотра

        ---

        :Description:
        - Определяет систему координат для всех последующих операций отрисовки
        - Влияет на позиционирование, масштабирование и поворот графики
        - По умолчанию используется стандартный View (охватывает все окно)

        ---

        :Args:
        - view (View): Объект камеры/вида для установки

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов
        """
        LIB_MOON._Window_SetView(self.__window_ptr, view.get_ptr())
        return self

    @final
    def disable(self) -> None:
        """
        #### Деактивирует окно (Windows-only)

        ---

        :Description:
        - Блокирует ввод и взаимодействие с окном
        - Затемняет заголовок окна (визуальный индикатор неактивности)
        - Автоматически устанавливает флаг __active в False

        ---

        :Note:
        - Работает только на платформе Windows

        """
        self.__window_descriptor = ctypes.windll.user32.FindWindowW(None, self.__title)
        ctypes.windll.user32.EnableWindow(self.__window_descriptor, False)
        self.__active = False

    @final
    def enable(self) -> None:
        """
        #### Активирует окно (Windows-only)

        ---

        :Description:
        - Восстанавливает возможность взаимодействия с окном
        - Возвращает нормальный вид заголовка окна
        - Автоматически устанавливает флаг __active в True

        ---

        :Note:
        - Работает только на платформе Windows

        """
        self.__window_descriptor = ctypes.windll.user32.FindWindowW(None, self.__title)
        ctypes.windll.user32.EnableWindow(self.__window_descriptor, True)
        self.__active = True

    @final
    def update(self, events: WindowEvents) -> bool:
        """
        #### Основной метод обновления состояния окна

        ---

        :Description:
        - Обрабатывает все события окна (ввод, изменение размера и т.д.)
        - Вычисляет метрики производительности (FPS, время рендеринга)
        - Управляет эффектом "призрачности" окна
        - Должен вызываться каждый кадр в основном цикле приложения

        ---

        :Args:
        - events (WindowEvents): Объект для работы с событиями окна

        ---

        :Returns:
        - bool: True если окно должно продолжать работу, False если требуется закрытие

        ---

        :Workflow:
        1. Обновление эффекта "призрачности" (если включен)
        2. Расчет метрик производительности
        3. Обработка событий окна
        4. Проверка условий закрытия
        5. Обновление состояния окна
        """

        # Реализация эффекта "призрачности" окна
        if self.__ghosting:
            # Прозрачность зависит от нахождения курсора в окне
            target_alpha = 255 if MouseInterface.in_window(self) else self.__ghosting_min_value
            # Плавное изменение прозрачности
            self.__window_alpha += (target_alpha - self.__window_alpha) * self.__ghosting_interpolation * self.__render_time * 100
            self.set_alpha(self.__window_alpha)

        if self.__using_keybinding_for_open_fps_monitor:
            if KeyBoardInterface.get_click_combination(self.__fps_monitor_key_binding):
                self.__fps_monitor_opened = not self.__fps_monitor_opened

        # =============================================
        # Расчет метрик производительности
        # =============================================

        # Замер времени рендеринга предыдущего кадра
        self.__render_time = self.__clock.get_elapsed_time()
        self.__clock.restart()

        # Расчет текущего FPS (с защитой от деления на ноль)
        self.__fps = 1 / self.__render_time if self.__render_time > 0 else 0

        # Расчет delta-time (нормализованного времени кадра)
        self.__delta = self.__target_fps / self.__fps if self.__fps > 0 else 1

        # Обновление истории FPS для графика производительности
        self.__update_fps_history()

        # =============================================
        # Обработка событий окна
        # =============================================

        # Опрос событий из системной очереди
        event_type = events.poll(self)

        # Проверка условий закрытия окна
        if self.__should_close_window(event_type, events):
            return False

        # Обработка изменения размера окна
        if event_type == WindowEvents.Type.Resized:
            self.__handle_window_resize(events)

        # Обновление флага изменения размера
        self.__update_resize_status()

        if self.get_resized():
            size = self.get_size()
            self.__cached_window_center = Vector2f(size.x / 2, size.y / 2)

        return True

    def __update_fps_history(self):
        """
        #### Обновляет историю значений FPS

        ---
        :Description:
        - Сохраняет значения FPS для построения графика
        - Обновляется каждые 0.1 секунды
        - Поддерживает ограниченный размер истории
        """
        self.__fps_update_timer += self.__render_time
        if self.__fps_update_timer >= 0.1:
            self.__fps_history.append(self.__fps)
            self.__min_fps_in_fps_history = min(self.__fps_history)
            self.__max_fps_in_fps_history = max(self.__fps_history)

            # Ограничение размера истории
            if len(self.__fps_history) > self.__max_history:
                self.__fps_history.pop(0)

            self.__fps_update_timer = 0

    def __should_close_window(self, event_type: int, events: WindowEvents) -> bool:
        """
        #### Проверяет условия закрытия окна

        ---
        :Args:
        - event_type: Тип последнего события
        - events: Объект событий окна

        :Returns:
        - bool: True если окно должно закрыться
        """
        return (event_type == WindowEvents.Type.Closed or
                keyboard.is_pressed(self.__exit_key))

    def __handle_window_resize(self, events: WindowEvents):
        """
        #### Обрабатывает изменение размера окна

        ---
        :Description:
        - Обновляет внутренние размеры окна
        - Корректирует стандартную область просмотра
        """
        self.__width = events.get_size_width()
        self.__height = events.get_size_height()

        # Обновление стандартного View под новый размер
        self.__view.set_size(self.__width, self.__height)
        self.__view.set_center(self.__width / 2, self.__height / 2)
        self.set_view(self.__view)

    def __update_resize_status(self):
        """
        #### Обновляет флаг изменения размера окна

        ---
        :Description:
        - Сравнивает текущие размеры с предыдущими
        - Устанавливает флаг __resized
        - Сохраняет текущие размеры для следующего сравнения
        """
        self.__resized = (self.__end_height != self.__height or
                        self.__end_width != self.__width)
        self.__end_height = self.__height
        self.__end_width = self.__width

    @final
    def get_resized(self) -> bool:
        """
        #### Проверяет изменение размера окна в текущем кадре

        ---

        :Description:
        - Возвращает True, если в этом кадре произошло изменение размера окна
        - Автоматически сбрасывается при следующем вызове update()
        - Полезно для адаптации интерфейса к новому размеру

        ---

        :Returns:
        - bool: Флаг изменения размера

        ---

        :Example:
        ```python
        if window.get_resized():
            # Пересчитать позиции элементов при изменении размера
            resize_ui_elements()
        ```
        """
        return self.__resized

    @final
    def clear(self, color: Color | None = None) -> None:
        """
        #### Очищает буфер рисования окна

        ---

        :Description:
        - Заполняет окно указанным цветом
        - Если цвет не указан, используется цвет по умолчанию
        - Должен вызываться перед началом рисования каждого кадра

        ---

        :Args:
        - color (Color | None): Цвет очистки или None для цвета по умолчанию

        ---

        :Raises:
        - TypeError: Если передан недопустимый тип цвета

        ---

        :Example:
        ```python
        # Очистить черным цветом
        window.clear(Color(0, 0, 0))

        # Очистить цветом по умолчанию
        window.clear()
        ```
        """
        if isinstance(color, Color):
            LIB_MOON._Window_Clear(self.__window_ptr, color.r, color.g, color.b, color.a)
        elif color is None:
            LIB_MOON._Window_Clear(
                self.__window_ptr,
                self.__clear_color.r,
                self.__clear_color.g,
                self.__clear_color.b,
                self.__clear_color.a
            )
        else:
            raise TypeError(f"Expected Color or None, got {type(color).__name__}")


    def display(self) -> None:
        """
        #### Отображает нарисованное содержимое

        ---

        :Description:
        - Выводит все нарисованные объекты на экран
        - Выполняет переключение буферов (double buffering)
        - Должен вызываться после завершения рисования кадра

        ---

        :Note:
        - Все операции рисования между clear() и display() будут показаны одновременно

        ---

        :Example:
        ```python
        # Стандартный цикл рендеринга
        window.clear()
        # ... рисование объектов ...
        window.display()
        ```
        """
        LIB_MOON._Window_Display(self.__window_ptr)

    @final
    def set_title(self, title: str) -> Self:
        """
        #### Устанавливает заголовок окна

        ---

        :Description:
        - Изменяет текст в заголовке окна
        - Поддерживает Unicode символы
        - Влияет на отображение в панели задач и заголовке окна

        ---

        :Args:
        - title (str): Новый заголовок окна

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Установить заголовок с FPS счетчиком
        window.set_title(f"My Game - {window.get_fps():.0f} FPS")
        ```
        """
        self.__title = title
        LIB_MOON._Window_SetTitle(self.__window_ptr, title.encode('utf-8'))
        return self

    @final
    def get_title(self) -> str:
        """
        #### Возвращает текущий заголовок окна

        ---

        :Description:
        - Возвращает текст, отображаемый в заголовке окна
        - Соответствует последнему значению, установленному через set_title()

        ---

        :Returns:
        - str: Текущий заголовок окна

        ---

        :Example:
        ```python
        print(f"Текущий заголовок: {window.get_title()}")
        ```
        """
        return self.__title

    @final
    def set_clear_color(self, color: Color) -> Self:
        """
        #### Устанавливает цвет очистки по умолчанию

        ---

        :Description:
        - Определяет цвет, которым будет заполняться окно при clear()
        - Используется, когда clear() вызывается без параметров
        - Начальное значение обычно черный цвет (0, 0, 0)

        ---

        :Args:
        - color (Color): Цвет для очистки (должен быть объектом Color)

        ---

        :Returns:
        - Self: Возвращает self для цепочки вызовов

        ---

        :Example:
        ```python
        # Установить синий цвет фона
        window.set_clear_color(Color(0, 0, 255))
        ```
        """
        self.__clear_color = color
        return self

    @final
    def get_clear_color(self) -> Color:
        """
        #### Возвращает текущий цвет очистки

        ---

        :Description:
        - Показывает цвет, установленный через set_clear_color()
        - Может отличаться от фактического цвета окна, если используется clear() с параметром

        ---

        :Returns:
        - Color: Текущий цвет очистки по умолчанию

        ---

        :Example:
        ```python
        # Проверить текущий цвет фона
        bg_color = window.get_clear_color()
        print(f"Фон: R={bg_color.r}, G={bg_color.g}, B={bg_color.b}")
        ```
        """
        return self.__clear_color

    @final
    def is_open(self) -> bool:
        """
        #### Проверяет состояние окна

        ---

        :Description:
        - Возвращает True, если окно создано и не закрыто
        - False означает, что окно было закрыто и больше не может использоваться

        ---

        :Returns:
        - bool: Состояние окна (открыто/закрыто)

        ---

        :Example:
        ```python
        # Основной цикл приложения
        while window.is_open():
            if not window.update(events): window.close()
            ...
        ```
        """
        return LIB_MOON._Window_IsOpen(self.__window_ptr)

    @final
    @overload
    def draw(self, shape, render_states: RenderStates) -> None:
        """
        #### Отрисовывает объект с пользовательскими параметрами рендеринга

        ---

        :Description:
        - Позволяет указать точные параметры отрисовки через RenderStates
        - Поддерживает кастомные трансформации, blending modes и текстуры

        ---

        :Args:
        - shape (Drawable): Отрисовываемый объект (Shape, Sprite, Text)
        - render_states (RenderStates): Параметры рендеринга

        ---

        :Example:
        ```python
        states = RenderStates(blend_mode=BlendMode.ADD)
        window.draw(sprite, states)
        ```
        """
        ...

    @final
    @overload
    def draw(self, shape, shader: Shader) -> None:
        """
        #### Отрисовывает объект с пользовательским шейдером

        ---

        :Description:
        - Применяет указанный шейдер к объекту
        - Позволяет создавать сложные визуальные эффекты

        ---

        :Args:
        - shape (Drawable): Отрисовываемый объект
        - shader (Shader): Шейдер для применения

        ---

        :Example:
        ```python
        shader = Shader.from_file("blur.frag")
        window.draw(sprite, shader)
        ```
        """
        ...

    @final
    @overload
    def draw(self, shape) -> None:
        """
        #### Отрисовывает объект с параметрами по умолчанию

        ---

        :Description:
        - Использует стандартные настройки рендеринга
        - Подходит для большинства случаев

        ---

        :Args:
        - shape (Drawable): Отрисовываемый объект

        ---

        :Example:
        ```python
        window.draw(sprite)  # Простая отрисовка
        ```
        """
        ...

    @final
    def draw(self, shape, render_states: RenderStates | Shader | None = None) -> None:
        """
        #### Основной метод отрисовки объектов

        ---

        :Description:
        - Поддерживает три режима отрисовки:
            - Стандартный (без параметров)
            - С пользовательскими RenderStates
            - С шейдером
        - Автоматически определяет тип объекта и способ его отрисовки

        ---

        :Args:
        - shape (Drawable): Объект для отрисовки (должен иметь get_ptr())
        - render_states (RenderStates|Shader|None): Параметры отрисовки

        ---

        :Workflow:
        1. Проверяет тип объекта (специальный или стандартный)
        2. Для специальных объектов вызывает их метод отрисовки
        3. Для стандартных объектов выбирает подходящий метод C++

        ---

        :Note:
        - Специальные объекты (LineThin и др.) обрабатываются в Python
        - Стандартные объекты передаются в нативный код

        ---

        :Example:
        ```python
        # Все три варианта использования:
        window.draw(sprite)  # По умолчанию
        window.draw(sprite, RenderStates(...))
        window.draw(sprite, shader)
        ```
        """
        if not isinstance(shape.get_ptr(), int):
            # Специальные объекты с собственной логикой отрисовки
            try:
                shape.special_draw(self, render_states)
            except:
                shape.special_draw(self)
        else:
            # Стандартные объекты
            if render_states is None:
                LIB_MOON._Window_Draw(self.__window_ptr, shape.get_ptr())
            elif isinstance(render_states, RenderStates):
                    LIB_MOON._Window_DrawWithRenderStates(
                        self.__window_ptr,
                        render_states.get_ptr(),
                        shape.get_ptr()
                    )
            elif isinstance(render_states, Shader):
                LIB_MOON._Window_DrawWithShader(
                    self.__window_ptr,
                    render_states.get_ptr(),
                    shape.get_ptr()
                )


from Moon.python.Rendering.Sprites import BaseSprite, LoadSprite

class _CustomWindowButton:
    def __init__(self, size: TwoNumberList, color: Color, sprite: BaseSprite) -> None:
        self.__size = size
        self.__color = color
        self.position = [0, 0]
        self.__sprite = sprite



    def render(self, window: Window):
        ...

CUSTOM_WINDOW_BUTTON_SIZE: Sequence[int] = [50, 31]
CUSTOM_WINDOW_EXIT_BUTTON: Final[_CustomWindowButton] = _CustomWindowButton(CUSTOM_WINDOW_BUTTON_SIZE, COLOR_RED, LoadSprite(r"Moon\data\ui\close.png", 1))

CUSTOM_WINDOW_HEAD_HEIGHT: int = 31


class CustomWindow(Window):
    def __init__(self, width: int = 800, height: int = 600, title: str = "Moon Window",
        vsync: bool = False, alpha: float = 255, context_settings: ContextSettings | None = None):
        super().__init__(width, height + CUSTOM_WINDOW_HEAD_HEIGHT, title, Window.Style.No, vsync, alpha, context_settings)
        super().enable_rounded_corners()

        self.__head_rectangle = RectangleShape(width, CUSTOM_WINDOW_HEAD_HEIGHT).set_color(DEFAULT_WINDOW_HEADER_COLOR)

    def display(self):
        super().draw(self.__head_rectangle)

        super().display()
