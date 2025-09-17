"""
#### *Модуль работы с камерами и областями просмотра в Moon*

---

##### Версия: 1.1.8

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 98%

---

✓ Полноценное управление камерами:
  - Создание/уничтожение View объектов
  - Управление позицией, размером и поворотом
  - Настройка центра и области просмотра

✓ Комплексная система координат:
  - Поддержка FloatRect для точного позиционирования
  - Преобразование координат между системами
  - Гибкая система масштабирования и поворота

✓ Производительность и контроль:
  - Эффективное управление памятью
  - Временные трансформации через контекстные менеджеры
  - Встроенная валидация параметров

✓ Готовые интерфейсы:
  - FloatRect - класс прямоугольных областей
  - View - основной класс камеры/области просмотра
  - Контекстные менеджеры для временных изменений

---

:Requires:

• Python 3.8+

• Библиотека ctypes (для работы с DLL)

• PySGL.dll (нативная библиотека рендеринга)

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

from contextlib import contextmanager
from typing import Self, Optional, Final, final

from Moon.python.utils import find_library, LibraryLoadError

@final
class ViewError(Exception):
    """Ошибка работы с View"""
    pass

# Загружаем DLL библиотеку
try:
    LIB_MOON: Final[ctypes.CDLL] = ctypes.CDLL(find_library())
except Exception as e:
    raise ImportError(f"Failed to load Moon library: {e}")

##################################################################
#                   `C / C++` Bindings                           #
#   Определение аргументов и возвращаемых типов для функций      #
#   из нативной DLL библиотеки Moon, используемых через ctypes. #
##################################################################

# Типы указателея на прамоугольную область просмотра = +
type FloatRectPtr = ctypes.c_void_p                    #
# ==================================================== +

# Тип указателя на вид ========= +
type ViewPtr = ctypes.c_void_p   #
# ============================== +

# FloatRect функции
LIB_MOON._FloatRect_Create.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
LIB_MOON._FloatRect_Create.restype = ctypes.c_void_p

LIB_MOON._FloatRect_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._FloatRect_Delete.restype = None

LIB_MOON._FloatRect_GetPositionX.argtypes = [ctypes.c_void_p]
LIB_MOON._FloatRect_GetPositionX.restype = ctypes.c_float

LIB_MOON._FloatRect_GetPositionY.argtypes = [ctypes.c_void_p]
LIB_MOON._FloatRect_GetPositionY.restype = ctypes.c_float

LIB_MOON._FloatRect_GetWidth.argtypes = [ctypes.c_void_p]
LIB_MOON._FloatRect_GetWidth.restype = ctypes.c_float

LIB_MOON._FloatRect_GetHeight.argtypes = [ctypes.c_void_p]
LIB_MOON._FloatRect_GetHeight.restype = ctypes.c_float

LIB_MOON._FloatRect_SetPosition.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._FloatRect_SetPosition.restype = None

LIB_MOON._FloatRect_SetSize.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._FloatRect_SetSize.restype = None

# View функции
LIB_MOON._View_Create.argtypes = [ctypes.c_void_p]
LIB_MOON._View_Create.restype = ctypes.c_void_p

LIB_MOON._View_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._View_Delete.restype = None

LIB_MOON._View_GetCenterX.argtypes = [ctypes.c_void_p]
LIB_MOON._View_GetCenterX.restype = ctypes.c_float

LIB_MOON._View_GetCenterY.argtypes = [ctypes.c_void_p]
LIB_MOON._View_GetCenterY.restype = ctypes.c_float

LIB_MOON._View_GetPositionX.argtypes = [ctypes.c_void_p]
LIB_MOON._View_GetPositionX.restype = ctypes.c_float

LIB_MOON._View_GetPositionY.argtypes = [ctypes.c_void_p]
LIB_MOON._View_GetPositionY.restype = ctypes.c_float

LIB_MOON._View_GetAngle.argtypes = [ctypes.c_void_p]
LIB_MOON._View_GetAngle.restype = ctypes.c_float

LIB_MOON._View_GetWidth.argtypes = [ctypes.c_void_p]
LIB_MOON._View_GetWidth.restype = ctypes.c_float

LIB_MOON._View_GetHeight.argtypes = [ctypes.c_void_p]
LIB_MOON._View_GetHeight.restype = ctypes.c_float

LIB_MOON._View_Rotate.argtypes = [ctypes.c_void_p, ctypes.c_float]
LIB_MOON._View_Rotate.restype = None

LIB_MOON._View_Reset.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._View_Reset.restype = None

LIB_MOON._View_Move.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._View_Move.restype = None

LIB_MOON._View_SetCenter.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._View_SetCenter.restype = None

LIB_MOON._View_SetAngle.argtypes = [ctypes.c_void_p, ctypes.c_float]
LIB_MOON._View_SetAngle.restype = None

LIB_MOON._View_SetViewport.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._View_SetViewport.restype = None

LIB_MOON._View_SetSize.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._View_SetSize.restype = None

LIB_MOON._View_Zoom.argtypes = [ctypes.c_void_p, ctypes.c_float]
LIB_MOON._View_Zoom.restype = None


@final
class FloatRect:
    """
    #### Класс прямоугольной области с плавающей точкой
    
    ---
    
    :Description:
    - Представляет прямоугольную область в 2D пространстве
    - Соответствует sf::FloatRect в SFML
    - Используется для определения областей просмотра и позиционирования
    
    ---
    
    :Features:
    - Точное позиционирование с плавающей точкой
    - Валидация размеров и координат
    - Автоматическое управление памятью
    - Цепочка вызовов для удобства использования
    
    ---
    
    :Attributes:
    - _ptr: Указатель на нативный объект FloatRect
    - _is_valid: Флаг валидности объекта
    """
    
    @final
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        """
        #### Создает новый FloatRect с указанными параметрами
        
        ---
        
        :Args:
        - x (float): Позиция по X
        - y (float): Позиция по Y  
        - w (float): Ширина (должна быть >= 0)
        - h (float): Высота (должна быть >= 0)
            
        ---
        
        :Raises:
        - ValueError: Если размеры отрицательные
        - ViewError: Если не удалось создать объект
        
        ---
        
        :Example:
        ```python
        # Создать прямоугольник 100x50 в позиции (10, 20)
        rect = FloatRect(10.0, 20.0, 100.0, 50.0)
        ```
        """
        if w < 0 or h < 0:
            raise ValueError(f"Размеры должны быть неотрицательными: w={w}, h={h}")
            
        self._ptr = LIB_MOON._FloatRect_Create(float(x), float(y), float(w), float(h))
        if not self._ptr:
            raise ViewError("Не удалось создать FloatRect")
        self._is_valid = True

    @final
    def _check_valid(self) -> None:
        """
        #### Проверяет валидность объекта
        
        ---
        
        :Raises:
        - ViewError: Если объект был удален или поврежден
        """
        if not self._is_valid:
            raise ViewError("FloatRect был удален")

    @final
    def get_ptr(self) -> FloatRectPtr:
        """
        #### Возвращает указатель на нативный объект
        
        ---
        
        :Returns:
        - FloatRectPtr: Указатель для использования в нативном коде
        
        ---
        
        :Note:
        - Для внутреннего использования в Moon
        """
        self._check_valid()
        return self._ptr

    @final
    def __del__(self) -> None:
        """
        #### Освобождает ресурсы нативного объекта
        
        ---
        
        :Description:
        - Автоматически вызывается при удалении объекта
        - Освобождает нативные ресурсы
        - Безопасно обрабатывает ошибки освобождения
        """
        if hasattr(self, '_is_valid') and self._is_valid and hasattr(self, '_ptr'):
            try:
                LIB_MOON._FloatRect_Delete(self._ptr)
            except:
                pass  # Игнорируем ошибки при удалении
            finally:
                self._is_valid = False

    @final
    def get_position(self) -> tuple[float, float]:
        """
        #### Возвращает текущую позицию прямоугольника
        
        ---
        
        :Returns:
        - tuple[float, float]: Кортеж (x, y) с координатами левого верхнего угла
        
        ---
        
        :Example:
        ```python
        x, y = rect.get_position()
        print(f"Позиция: ({x}, {y})")
        ```
        """
        self._check_valid()
        return (
            LIB_MOON._FloatRect_GetPositionX(self._ptr),
            LIB_MOON._FloatRect_GetPositionY(self._ptr),
        )
    
    @final
    def get_size(self) -> tuple[float, float]:
        """
        #### Возвращает текущие размеры прямоугольника
        
        ---
        
        :Returns:
        - tuple[float, float]: Кортеж (width, height) с размерами
        
        ---
        
        :Example:
        ```python
        width, height = rect.get_size()
        print(f"Размер: {width}x{height}")
        ```
        """
        self._check_valid()
        return (
            LIB_MOON._FloatRect_GetWidth(self._ptr),
            LIB_MOON._FloatRect_GetHeight(self._ptr),
        )
    
    @final
    def set_position(self, x: Optional[float] = None, y: Optional[float] = None) -> Self:
        """
        #### Устанавливает новую позицию прямоугольника
        
        ---
        
        :Args:
        - x (Optional[float]): Новая позиция X (None - не изменять)
        - y (Optional[float]): Новая позиция Y (None - не изменять)
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Установить только X координату
        rect.set_position(x=100.0)
        
        # Установить обе координаты
        rect.set_position(50.0, 75.0)
        ```
        """
        self._check_valid()
        if x is None and y is None:
            return self
            
        current_x, current_y = self.get_position()
        new_x = float(x) if x is not None else current_x
        new_y = float(y) if y is not None else current_y
        
        LIB_MOON._FloatRect_SetPosition(self._ptr, new_x, new_y)
        return self
    
    @final
    def set_size(self, w: Optional[float] = None, h: Optional[float] = None) -> Self:
        """
        #### Устанавливает новые размеры прямоугольника
        
        ---
        
        :Args:
        - w (Optional[float]): Новая ширина (None - не изменять, должна быть >= 0)
        - h (Optional[float]): Новая высота (None - не изменять, должна быть >= 0)
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
            
        ---
        
        :Raises:
        - ValueError: Если размеры отрицательные
        
        ---
        
        :Example:
        ```python
        # Изменить только ширину
        rect.set_size(w=200.0)
        
        # Изменить оба размера
        rect.set_size(150.0, 100.0)
        ```
        """
        self._check_valid()
        if w is None and h is None:
            return self
            
        if (w is not None and w < 0) or (h is not None and h < 0):
            raise ValueError(f"Размеры должны быть неотрицательными: w={w}, h={h}")
            
        current_w, current_h = self.get_size()
        new_w = float(w) if w is not None else current_w
        new_h = float(h) if h is not None else current_h
        
        LIB_MOON._FloatRect_SetSize(self._ptr, new_w, new_h)
        return self
        
    @final
    def __repr__(self) -> str:
        """
        #### Строковое представление для отладки
        
        ---
        
        :Returns:
        - str: Читаемое представление объекта
        
        ---
        
        :Example:
        ```python
        print(rect)  # FloatRect(x=10.0, y=20.0, w=100.0, h=50.0)
        ```
        """
        if not self._is_valid:
            return "FloatRect(deleted)"
        try:
            x, y = self.get_position()
            w, h = self.get_size()
            return f"FloatRect(x={x}, y={y}, w={w}, h={h})"
        except:
            return "FloatRect(invalid)"


@final
class View:
    """
    #### Класс камеры/области просмотра для управления отображением
    
    ---
    
    :Description:
    - Представляет камеру или область просмотра в 2D пространстве
    - Соответствует sf::View в SFML
    - Позволяет управлять позицией, размером, поворотом и масштабом
    - Используется для создания различных видов сцены
    
    ---
    
    :Features:
    - Управление центром и размером области просмотра
    - Поворот и масштабирование вида
    - Настройка вьюпорта для отображения
    - Временные трансформации через контекстные менеджеры
    - Автоматическое управление памятью
    
    ---
    
    :Attributes:
    - _ptr: Указатель на нативный объект View
    - _float_rect: Базовый прямоугольник вида
    - _is_valid: Флаг валидности объекта
    - _owns_ptr: Флаг владения указателем
    """
    
    @final
    def __init__(self, float_rect: FloatRect) -> None:
        """
        #### Создает новый View с указанным прямоугольником
        
        ---
        
        :Args:
        - float_rect (FloatRect): Прямоугольник области просмотра
            
        ---
        
        :Raises:
        - TypeError: Если float_rect не является экземпляром FloatRect
        - ViewError: Если не удалось создать View
        
        ---
        
        :Example:
        ```python
        # Создать область просмотра 800x600
        rect = FloatRect(0, 0, 800, 600)
        view = View(rect)
        ```
        """
        if not isinstance(float_rect, FloatRect):
            raise TypeError("float_rect должен быть экземпляром FloatRect")
            
        self._float_rect = float_rect
        self._ptr = LIB_MOON._View_Create(float_rect.get_ptr())
        if not self._ptr:
            raise ViewError("Не удалось создать View")
        self._is_valid = True
        self._owns_ptr = True
    
    @final
    @classmethod
    def from_view_ptr(cls, view_ptr: ViewPtr) -> "View":
        """
        #### Создает объект View из существующего указателя на нативный View
        
        ---
        
        :Args:
        - view_ptr (ViewPtr): Указатель на нативный View
            
        ---
        
        :Returns:
        - View: Новый экземпляр View
            
        ---
        
        :Raises:
        - ViewError: Если указатель невалиден или не удалось получить параметры
        
        ---
        
        :Note:
        - Создаваемый объект не владеет указателем
        - Используется для работы с View, созданными в нативном коде
        
        ---
        
        :Example:
        ```python
        # Создать View из нативного указателя
        view = View.from_view_ptr(native_view_ptr)
        ```
        """
        if not view_ptr:
            raise ViewError("Невалидный указатель на View")
            
        # Получаем параметры из нативного View
        try:
            width = LIB_MOON._View_GetWidth(view_ptr)
            height = LIB_MOON._View_GetHeight(view_ptr)
            pos_x = LIB_MOON._View_GetPositionX(view_ptr)
            pos_y = LIB_MOON._View_GetPositionY(view_ptr)
        except Exception as e:
            raise ViewError(f"Не удалось получить параметры View: {e}")

        # Создаем FloatRect и View
        float_rect = FloatRect(pos_x, pos_y, width, height)
        view = cls.__new__(cls)
        view._float_rect = float_rect
        view._ptr = view_ptr
        view._is_valid = True
        view._owns_ptr = False  # Не владеем указателем
        return view
    
    @final
    def _check_valid(self) -> None:
        """
        #### Проверяет валидность объекта
        
        ---
        
        :Raises:
        - ViewError: Если объект был удален или поврежден
        """
        if not self._is_valid:
            raise ViewError("View был удален")

    @final
    def __del__(self) -> None:
        """
        #### Освобождает ресурсы нативного объекта
        
        ---
        
        :Description:
        - Автоматически вызывается при удалении объекта
        - Освобождает нативные ресурсы только если объект владеет указателем
        - Безопасно обрабатывает ошибки освобождения
        """
        if (hasattr(self, '_is_valid') and self._is_valid and 
            hasattr(self, '_owns_ptr') and self._owns_ptr and 
            hasattr(self, '_ptr') and hasattr(LIB_MOON, '_View_Delete')):
            try:
                LIB_MOON._View_Delete(self._ptr)
            except:
                pass  # Игнорируем ошибки при удалении
            finally:
                self._is_valid = False

    @final
    def get_ptr(self) -> ViewPtr:
        """
        #### Возвращает указатель на нативный объект
        
        ---
        
        :Returns:
        - ViewPtr: Указатель для использования в нативном коде
        
        ---
        
        :Note:
        - Для внутреннего использования в Moon
        """
        self._check_valid()
        return self._ptr
        
    @final
    def get_float_rect(self) -> FloatRect:
        """
        #### Возвращает базовый прямоугольник вида
        
        ---
        
        :Returns:
        - FloatRect: Прямоугольник, определяющий область просмотра
        
        ---
        
        :Example:
        ```python
        rect = view.get_float_rect()
        print(f"Область просмотра: {rect}")
        ```
        """
        return self._float_rect

    @final
    def set_center(self, x: float, y: float) -> Self:
        """
        #### Устанавливает центр области просмотра
        
        ---
        
        :Args:
        - x (float): Координата X центра
        - y (float): Координата Y центра
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Центрировать камеру на точке (400, 300)
        view.set_center(400.0, 300.0)
        ```
        """
        self._check_valid()
        LIB_MOON._View_SetCenter(self._ptr, float(x), float(y))
        return self

    @final
    def set_size(self, width: float, height: float) -> Self:
        """
        #### Устанавливает размер области просмотра
        
        ---
        
        :Args:
        - width (float): Ширина (должна быть > 0)
        - height (float): Высота (должна быть > 0)
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
            
        ---
        
        :Raises:
        - ValueError: Если размеры неположительные
        
        ---
        
        :Example:
        ```python
        # Установить размер области просмотра 1024x768
        view.set_size(1024.0, 768.0)
        ```
        """
        if width <= 0 or height <= 0:
            raise ValueError(f"Размеры должны быть положительными: width={width}, height={height}")
            
        self._check_valid()
        LIB_MOON._View_SetSize(self._ptr, float(width), float(height))
        return self

    @final
    def set_viewport(self, viewport: FloatRect) -> Self:
        """
        #### Устанавливает вьюпорт (область экрана для отображения)
        
        ---
        
        :Args:
        - viewport (FloatRect): Прямоугольник вьюпорта в нормализованных координатах (0-1)
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Raises:
        - TypeError: Если viewport не является экземпляром FloatRect
        
        ---
        
        :Example:
        ```python
        # Установить вьюпорт на левую половину экрана
        viewport = FloatRect(0.0, 0.0, 0.5, 1.0)
        view.set_viewport(viewport)
        ```
        """
        if not isinstance(viewport, FloatRect):
            raise TypeError("viewport должен быть экземпляром FloatRect")
            
        self._check_valid()
        LIB_MOON._View_SetViewport(self._ptr, viewport.get_ptr())
        return self

    @final
    def set_angle(self, angle: float) -> Self:
        """
        #### Устанавливает угол поворота области просмотра
        
        ---
        
        :Args:
        - angle (float): Угол поворота в градусах
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Повернуть камеру на 45 градусов
        view.set_angle(45.0)
        ```
        """
        self._check_valid()
        LIB_MOON._View_SetAngle(self._ptr, float(angle))
        return self

    @final
    def move(self, offset_x: float, offset_y: float) -> Self:
        """
        #### Перемещает область просмотра на указанное смещение
        
        ---
        
        :Args:
        - offset_x (float): Смещение по оси X
        - offset_y (float): Смещение по оси Y
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Сдвинуть камеру вправо на 50 пикселей
        view.move(50.0, 0.0)
        ```
        """
        self._check_valid()
        LIB_MOON._View_Move(self._ptr, float(offset_x), float(offset_y))
        return self

    @final
    def get_center(self) -> tuple[float, float]:
        """
        #### Возвращает центр области просмотра
        
        ---
        
        :Returns:
        - tuple[float, float]: Кортеж (center_x, center_y) с координатами центра
        
        ---
        
        :Example:
        ```python
        center_x, center_y = view.get_center()
        print(f"Центр камеры: ({center_x}, {center_y})")
        ```
        """
        self._check_valid()
        return (
            LIB_MOON._View_GetCenterX(self._ptr),
            LIB_MOON._View_GetCenterY(self._ptr),
        )

    @final
    def get_position(self) -> tuple[float, float]:
        """
        #### Возвращает позицию области просмотра
        
        ---
        
        :Returns:
        - tuple[float, float]: Кортеж (position_x, position_y) с координатами левого верхнего угла
        
        ---
        
        :Example:
        ```python
        pos_x, pos_y = view.get_position()
        print(f"Позиция камеры: ({pos_x}, {pos_y})")
        ```
        """
        self._check_valid()
        return (
            LIB_MOON._View_GetPositionX(self._ptr),
            LIB_MOON._View_GetPositionY(self._ptr),
        )

    @final
    def get_angle(self) -> float:
        """
        #### Возвращает угол поворота области просмотра
        
        ---
        
        :Returns:
        - float: Угол поворота в градусах
        
        ---
        
        :Example:
        ```python
        angle = view.get_angle()
        print(f"Угол поворота: {angle}°")
        ```
        """
        self._check_valid()
        return LIB_MOON._View_GetAngle(self._ptr)

    @final
    def get_size(self) -> tuple[float, float]:
        """
        #### Возвращает размер области просмотра
        
        ---
        
        :Returns:
        - tuple[float, float]: Кортеж (width, height) с размерами
        
        ---
        
        :Example:
        ```python
        width, height = view.get_size()
        print(f"Размер области просмотра: {width}x{height}")
        ```
        """
        self._check_valid()
        return (
            LIB_MOON._View_GetWidth(self._ptr),
            LIB_MOON._View_GetHeight(self._ptr),
        )

    @final
    def rotate(self, angle: float) -> Self:
        """
        #### Поворачивает область просмотра на указанный угол
        
        ---
        
        :Args:
        - angle (float): Угол поворота в градусах (добавляется к текущему углу)
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Повернуть камеру на дополнительные 90 градусов
        view.rotate(90.0)
        ```
        """
        self._check_valid()
        LIB_MOON._View_Rotate(self._ptr, float(angle))
        return self

    @final
    def zoom(self, factor: float) -> Self:
        """
        #### Масштабирует область просмотра
        
        ---
        
        :Args:
        - factor (float): Коэффициент масштабирования (должен быть > 0)
                         1.0 - без изменений, <1.0 - приближение, >1.0 - отдаление
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
            
        ---
        
        :Raises:
        - ValueError: Если коэффициент неположительный
        
        ---
        
        :Example:
        ```python
        # Приблизить в 2 раза
        view.zoom(0.5)
        
        # Отдалить в 2 раза
        view.zoom(2.0)
        ```
        """
        if factor <= 0:
            raise ValueError(f"Коэффициент масштабирования должен быть положительным: {factor}")
            
        self._check_valid()
        LIB_MOON._View_Zoom(self._ptr, float(factor))
        return self

    @final
    def reset(self, rectangle: FloatRect) -> Self:
        """
        #### Сбрасывает параметры области просмотра к указанному прямоугольнику
        
        ---
        
        :Args:
        - rectangle (FloatRect): Новый прямоугольник области просмотра
            
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Raises:
        - TypeError: Если rectangle не является экземпляром FloatRect
        
        ---
        
        :Example:
        ```python
        # Сбросить камеру к новой области
        new_rect = FloatRect(0, 0, 1920, 1080)
        view.reset(new_rect)
        ```
        """
        if not isinstance(rectangle, FloatRect):
            raise TypeError("rectangle должен быть экземпляром FloatRect")
            
        self._check_valid()
        LIB_MOON._View_Reset(self._ptr, rectangle.get_ptr())
        self._float_rect = rectangle
        return self
        
    @final
    def __repr__(self) -> str:
        """
        #### Строковое представление для отладки
        
        ---
        
        :Returns:
        - str: Читаемое представление объекта с основными параметрами
        
        ---
        
        :Example:
        ```python
        print(view)  # View(center=(400.0, 300.0), size=(800.0, 600.0), angle=0.0°)
        ```
        """
        if not self._is_valid:
            return "View(deleted)"
        try:
            center = self.get_center()
            size = self.get_size()
            angle = self.get_angle()
            return f"View(center={center}, size={size}, angle={angle}°)"
        except:
            return "View(invalid)"
            
    @final
    @contextmanager
    def temporary_transform(self, center: Optional[tuple[float, float]] = None, 
                          size: Optional[tuple[float, float]] = None,
                          angle: Optional[float] = None):
        """
        #### Контекстный менеджер для временного изменения параметров области просмотра
        
        ---
        
        :Args:
        - center (Optional[tuple[float, float]]): Временный центр (x, y)
        - size (Optional[tuple[float, float]]): Временный размер (width, height)
        - angle (Optional[float]): Временный угол поворота в градусах
        
        ---
        
        :Yields:
        - View: Текущий объект View с примененными временными параметрами
        
        ---
        
        :Description:
        - Автоматически сохраняет текущие параметры
        - Применяет временные изменения
        - Восстанавливает исходные параметры при выходе из контекста
        
        ---
        
        :Example:
        ```python
        # Временно изменить центр и размер для специального рендеринга
        with view.temporary_transform(center=(100, 100), size=(400, 300)):
            # Рендеринг с временными параметрами
            window.draw(special_object)
        # Параметры автоматически восстановлены
        ```
        """
        # Сохраняем текущие параметры
        old_center = self.get_center()
        old_size = self.get_size()
        old_angle = self.get_angle()
        
        try:
            # Применяем временные параметры
            if center is not None:
                self.set_center(*center)
            if size is not None:
                self.set_size(*size)
            if angle is not None:
                self.set_angle(angle)
            yield self
        finally:
            # Восстанавливаем старые параметры
            self.set_center(*old_center)
            self.set_size(*old_size)
            self.set_angle(old_angle)