"""
#### *Модуль работы с массивами вершин в Moon*

---

##### Версия: 1.0.0

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 95% 

---

✓ Эффективное управление вершинами:
  - Создание и управление массивами вершин
  - Поддержка всех типов примитивов OpenGL
  - Оптимизированные операции через нативный код

✓ Гибкая система вершин:
  - Легковесный класс Vertex с поддержкой позиции, цвета и текстур
  - Быстрые операции изменения отдельных атрибутов
  - Массовые операции для эффективной работы

✓ Производительность и удобство:
  - Нативное управление памятью для максимальной скорости
  - Python-интерфейс для удобства разработки
  - Автоматическое управление ресурсами

✓ Готовые интерфейсы:
  - Vertex - контейнер данных вершины
  - VertexArray - массив вершин с типами примитивов
  - PrimitiveType - перечисление типов отрисовки

---

:Requires:

• Python 3.8+

• Библиотека ctypes (для работы с DLL)

• Moon.dll (нативная библиотека рендеринга)

• Moon.Colors (модуль цветов)

• Moon.Vectors (модуль векторов)

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

from enum import Enum
from typing import Self, final

from Moon.python.Colors import Color
from Moon.python.Vectors import Vector2f

from Moon.python.utils import find_library, LibraryLoadError

# Загружаем DLL библиотеку
try:
    LIB_MOON = ctypes.CDLL(find_library())
except Exception as e:
    raise ImportError(f"Failed to load PySGL library: {e}")

# --- Настройка функций для работы с VertexArray ---
# Передаем только те функции, которые взаимодействуют с VertexArray
LIB_MOON._VertexArray_Create.restype = ctypes.c_void_p
LIB_MOON._VertexArray_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._VertexArray_Delete.restype = None
LIB_MOON._VertexArray_AddVertexForPositionAndColor.argtypes = [
    ctypes.c_void_p, ctypes.c_double, ctypes.c_double, 
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
]
LIB_MOON._VertexArray_AddVertexForPositionAndColor.restype = None
LIB_MOON._VertexArray_Clear.argtypes = [ctypes.c_void_p]
LIB_MOON._VertexArray_Clear.restype = None
LIB_MOON._VertexArray_GetVertexCount.argtypes = [ctypes.c_void_p]
LIB_MOON._VertexArray_GetVertexCount.restype = ctypes.c_int
LIB_MOON._VertexArray_GetPrimitiveType.argtypes = [ctypes.c_void_p]
LIB_MOON._VertexArray_GetPrimitiveType.restype = ctypes.c_int
LIB_MOON._VertexArray_Resize.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._VertexArray_Resize.restype = None
LIB_MOON._VertexArray_SetPrimitiveType.argtypes = [ctypes.c_void_p, ctypes.c_int]
LIB_MOON._VertexArray_SetPrimitiveType.restype = None
LIB_MOON._VertexArray_SetVertexForPositionAndColor.argtypes = [
    ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double, 
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
]
LIB_MOON._VertexArray_SetVertexForPositionAndColor.restype = None

# Оптимизированные функции для прямого доступа к данным вершин
LIB_MOON._VertexArray_SetVertexPosition.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_float, ctypes.c_float]
LIB_MOON._VertexArray_SetVertexPosition.restype = None
LIB_MOON._VertexArray_SetVertexColor.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON._VertexArray_SetVertexColor.restype = None
LIB_MOON._VertexArray_SetAllVerticesColor.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON._VertexArray_SetAllVerticesColor.restype = None

# Функции для работы с текстурными координатами
LIB_MOON._VertexArray_AddVertexWithTexCoords.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_float]
LIB_MOON._VertexArray_AddVertexWithTexCoords.restype = None
LIB_MOON._VertexArray_SetVertexTexCoords.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_float, ctypes.c_float]
LIB_MOON._VertexArray_SetVertexTexCoords.restype = None
LIB_MOON._VertexArray_SetQuadTexCoords.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
LIB_MOON._VertexArray_SetQuadTexCoords.restype = None

@final
class Vertex:
    """
    #### Легковесный контейнер для данных вершины
    
    ---
    
    :Description:
    - Хранит основные атрибуты вершины: позицию, цвет и текстурные координаты
    - Использует __slots__ для оптимизации памяти
    - Предоставляет удобный интерфейс для работы с вершинными данными
    
    ---
    
    :Features:
    - Автоматическая инициализация значениями по умолчанию
    - Поддержка всех основных атрибутов вершины
    - Оптимизированное использование памяти через __slots__
    """
    __slots__ = ('position', 'color', 'tex_coords')
    
    def __init__(self, pos: Vector2f = None, color: Color = None, tex_coords: Vector2f = None):
        """
        #### Инициализация вершины с заданными атрибутами
        
        ---
        
        :Args:
        - pos (Vector2f | None): Позиция вершины в пространстве (по умолчанию (0,0))
        - color (Color | None): Цвет вершины (по умолчанию черный)
        - tex_coords (Vector2f | None): Текстурные координаты (по умолчанию (0,0))
        
        ---
        
        :Example:
        ```python
        # Создание вершины с позицией и цветом
        vertex = Vertex(Vector2f(100, 200), Color(255, 0, 0))
        ```
        """
        self.position = pos if pos is not None else Vector2f(0, 0)
        self.color = color if color is not None else COLOR_BLACK
        self.tex_coords = tex_coords if tex_coords is not None else Vector2f(0, 0)
        
    def __repr__(self):
        """
        #### Строковое представление вершины для отладки
        
        ---
        
        :Returns:
        - str: Форматированная строка с данными вершины
        
        ---
        
        :Example:
        ```python
        print(vertex)  # Vertex(100.0, 200.0, Color(...), Vector2f(...))
        ```
        """
        return f"Vertex({self.position.x}, {self.position.y}, {self.color}, {self.tex_coords})"


@final
class VertexArray:
    """
    #### Класс массива вершин для графического рендеринга
    
    ---
    
    :Description:
    - Управляет набором вершин и определяет способ их отрисовки
    - Поддерживает различные типы примитивов (точки, линии, треугольники)
    - Вершины управляются в нативной библиотеке для максимальной производительности
    
    ---
    
    :Features:
    - Поддержка всех основных типов примитивов OpenGL
    - Эффективное управление памятью через нативный код
    - Удобный Python-интерфейс для работы с вершинами
    - Автоматическое управление ресурсами
    """

    class PrimitiveType(Enum):
        """
        #### Перечисление типов примитивов для отрисовки
        
        ---
        
        :Values:
        - POINTS: Отдельные точки
        - LINES: Пары вершин как отдельные линии
        - LINE_STRIP: Связанные линии (полилиния)
        - TRIANGLES: Тройки вершин как треугольники
        - TRIANGLE_STRIP: Полоса соединенных треугольников
        - TRIANGLE_FAN: Веер треугольников
        - QUADS: Четверки вершин как четырехугольники
        """
        POINTS = 0        # Отдельные точки
        LINES = 1         # Пары вершин как отдельные линии
        LINE_STRIP = 2    # Связанные линии (полилиния)
        TRIANGLES = 3     # Тройки вершин как треугольники
        TRIANGLE_STRIP = 4 # Полоса соединенных треугольников
        TRIANGLE_FAN = 5  # Веер треугольников
        QUADS = 6         # Четверки вершин как четырехугольники
    
    def __init__(self):
        """
        #### Инициализация пустого массива вершин
        
        ---
        
        :Description:
        - Создает нативный объект массива вершин
        - Устанавливает тип примитива по умолчанию
        - Подготавливает структуры для хранения вершин
        
        ---
        
        :Raises:
        - RuntimeError: При ошибке создания нативного объекта
        """
        self._ptr = LIB_MOON._VertexArray_Create()

    def get_ptr(self):
        """
        #### Возвращает указатель на нативный объект массива
        
        ---
        
        :Returns:
        - ctypes.c_void_p: Указатель для использования в C++ коде
        
        ---
        
        :Note:
        - Для внутреннего использования в Moon
        """
        return self._ptr
    
    def __del__(self):
        """
        #### Освобождение ресурсов нативного массива
        
        ---
        
        :Description:
        - Автоматически вызывается при удалении объекта Python
        - Освобождает память, выделенную в нативной библиотеке
        - Предотвращает утечки памяти
        
        ---
        
        :Note:
        - Проверяет существование указателя перед удалением
        """
        if self._ptr: # Проверяем, что указатель существует перед удалением
            LIB_MOON._VertexArray_Delete(self._ptr)
            self._ptr = None # Обнуляем указатель после удаления

    def __len__(self) -> int:
        """
        #### Возвращает количество вершин в массиве
        
        ---
        
        :Returns:
        - int: Текущее количество вершин
        
        ---
        
        :Example:
        ```python
        print(f"В массиве {len(vertex_array)} вершин")
        ```
        """
        return LIB_MOON._VertexArray_GetVertexCount(self._ptr)

    def __getitem__(self, index: int) -> Vertex:
        """
        #### Получение вершины по индексу
        
        ---
        
        :Description:
        - Возвращает копию вершины из нативного массива
        - Изменения в возвращенной вершине НЕ влияют на массив
        - Для обновления используйте set_vertex()
        
        ---
        
        :Args:
        - index (int): Индекс вершины (0 <= index < len(array))
        
        ---
        
        :Returns:
        - Vertex: Копия вершины с данными из массива
        
        ---
        
        :Raises:
        - IndexError: При выходе индекса за границы массива
        
        ---
        
        :Example:
        ```python
        vertex = vertex_array[0]  # Получить первую вершину
        ```
        """
        if not (0 <= index < len(self)):
            raise IndexError(f"Vertex index {index} out of bounds for VertexArray of size {len(self)}.")
        
        pos_x = LIB_MOON._VertexArray_GetVertexPositionX(self._ptr, index)
        pos_y = LIB_MOON._VertexArray_GetVertexPositionY(self._ptr, index)
        color_r = LIB_MOON._VertexArray_GetVertexColorR(self._ptr, index)
        color_g = LIB_MOON._VertexArray_GetVertexColorG(self._ptr, index)
        color_b = LIB_MOON._VertexArray_GetVertexColorB(self._ptr, index)
        color_a = LIB_MOON._VertexArray_GetVertexColorA(self._ptr, index)
        
        return Vertex(Vector2f(pos_x, pos_y), Color(color_r, color_g, color_b, color_a))

    def set_primitive_type(self, primitive_type: PrimitiveType) -> Self:
        """
        #### Устанавливает тип примитива для отрисовки
        
        ---
        
        :Description:
        - Определяет способ интерпретации вершин при рендеринге
        - Влияет на то, как OpenGL соединяет вершины
        
        ---
        
        :Args:
        - primitive_type (PrimitiveType): Тип примитива из перечисления
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Raises:
        - TypeError: При передаче неверного типа
        
        ---
        
        :Example:
        ```python
        array.set_primitive_type(VertexArray.PrimitiveType.TRIANGLES)
        ```
        """
        if not isinstance(primitive_type, self.PrimitiveType):
            raise TypeError("primitive_type must be an instance of VertexArray.PrimitiveType")
        LIB_MOON._VertexArray_SetPrimitiveType(self._ptr, primitive_type.value)
        return self

    def get_primitive_type(self) -> PrimitiveType:
        """
        #### Возвращает текущий тип примитива
        
        ---
        
        :Returns:
        - PrimitiveType: Текущий установленный тип примитива
        
        ---
        
        :Example:
        ```python
        if array.get_primitive_type() == VertexArray.PrimitiveType.TRIANGLES:
            print("Массив настроен для треугольников")
        ```
        """
        return VertexArray.PrimitiveType(LIB_MOON._VertexArray_GetPrimitiveType(self._ptr))

    def append(self, vertex: Vertex) -> None:
        """
        #### Добавляет вершину в конец массива
        
        ---
        
        :Description:
        - Увеличивает размер массива на одну вершину
        - Автоматически определяет наличие текстурных координат
        - Вызывает соответствующую нативную функцию
        
        ---
        
        :Args:
        - vertex (Vertex): Вершина для добавления
        
        ---
        
        :Raises:
        - TypeError: При передаче объекта неверного типа
        
        ---
        
        :Example:
        ```python
        vertex = Vertex(Vector2f(100, 200), Color(255, 0, 0))
        array.append(vertex)
        ```
        """
        if not isinstance(vertex, Vertex):
            raise TypeError("Argument 'vertex' must be an instance of Vertex.")
        
        if hasattr(vertex, 'tex_coords') and vertex.tex_coords is not None:
            LIB_MOON._VertexArray_AddVertexWithTexCoords(
                self._ptr,
                vertex.position.x, vertex.position.y,
                vertex.color.r, vertex.color.g, vertex.color.b, vertex.color.a,
                float(vertex.tex_coords.x), float(vertex.tex_coords.y)
            )
        else:

            LIB_MOON._VertexArray_AddVertexForPositionAndColor(
                self._ptr, 
                vertex.position.x, vertex.position.y, 
                vertex.color.r, vertex.color.g, vertex.color.b, vertex.color.a
            )
    
    def extend(self, vertices: list[Vertex]) -> None:
        """
        #### Добавляет множество вершин в массив
        
        ---
        
        :Description:
        - Последовательно добавляет все вершины из списка
        - Эквивалентно множественным вызовам append()
        
        ---
        
        :Args:
        - vertices (list[Vertex]): Список вершин для добавления
        
        ---
        
        :Example:
        ```python
        vertices = [vertex1, vertex2, vertex3]
        array.extend(vertices)
        ```
        """
        for vertex in vertices:
            self.append(vertex)

    def clear(self) -> None:
        """
        #### Удаляет все вершины из массива
        
        ---
        
        :Description:
        - Освобождает память, занятую вершинами
        - Сбрасывает размер массива до нуля
        - Сохраняет тип примитива
        
        ---
        
        :Example:
        ```python
        array.clear()  # Теперь len(array) == 0
        ```
        """
        LIB_MOON._VertexArray_Clear(self._ptr)

    def set_quad_texture_coords(self, start_index: int, tex_left: float = 0.0, tex_top: float = 0.0, tex_right: float = 1.0, tex_bottom: float = 1.0) -> None:
        """
        #### Устанавливает текстурные координаты для четырехугольника
        
        ---
        
        :Description:
        - Настраивает текстурные координаты для четырех последовательных вершин
        - Автоматически распределяет координаты по углам квада
        - Полезно для текстурирования прямоугольных объектов
        
        ---
        
        :Args:
        - start_index (int): Индекс первой вершины квада
        - tex_left (float): Левая граница текстуры (по умолчанию 0.0)
        - tex_top (float): Верхняя граница текстуры (по умолчанию 0.0)
        - tex_right (float): Правая граница текстуры (по умолчанию 1.0)
        - tex_bottom (float): Нижняя граница текстуры (по умолчанию 1.0)
        
        ---
        
        :Example:
        ```python
        # Установить координаты для спрайта
        array.set_quad_texture_coords(0, 0.0, 0.0, 1.0, 1.0)
        ```
        """
        LIB_MOON._VertexArray_SetQuadTexCoords(self._ptr, start_index, tex_left, tex_top, tex_right, tex_bottom)

    def resize(self, size: int) -> None:
        """
        #### Изменяет размер массива вершин
        
        ---
        
        :Description:
        - При уменьшении размера лишние вершины удаляются
        - При увеличении новые вершины инициализируются значениями по умолчанию
        - Операция выполняется в нативном коде для эффективности
        
        ---
        
        :Args:
        - size (int): Новый размер массива (должен быть >= 0)
        
        ---
        
        :Raises:
        - ValueError: При передаче отрицательного размера
        
        ---
        
        :Example:
        ```python
        array.resize(100)  # Установить размер 100 вершин
        ```
        """
        if not isinstance(size, int) or size < 0:
            raise ValueError("Size must be a non-negative integer.")
        LIB_MOON._VertexArray_Resize(self._ptr, size) 
        LIB_MOON._VertexArray_Resize(self._ptr, size)

    def set_vertex(self, index: int, vertex: Vertex) -> None:
        """
        #### Заменяет вершину по указанному индексу
        
        ---
        
        :Description:
        - Обновляет данные существующей вершины в массиве
        - Копирует все атрибуты (позицию, цвет, текстурные координаты)
        - Изменения сразу отражаются в нативном массиве
        
        ---
        
        :Args:
        - index (int): Индекс заменяемой вершины
        - vertex (Vertex): Новые данные вершины
        
        ---
        
        :Raises:
        - TypeError: При передаче неверного типа вершины
        - IndexError: При выходе индекса за границы массива
        
        ---
        
        :Example:
        ```python
        new_vertex = Vertex(Vector2f(50, 75), Color(0, 255, 0))
        array.set_vertex(0, new_vertex)
        ```
        """
        if not isinstance(vertex, Vertex):
            raise TypeError("Argument 'vertex' must be an instance of Vertex.")
        if not (0 <= index < len(self)):
            raise IndexError(f"Vertex index {index} out of bounds for VertexArray of size {len(self)}.")
        
        LIB_MOON._VertexArray_SetVertexForPositionAndColor(
            self._ptr, index, 
            vertex.position.x, vertex.position.y, 
            vertex.color.r, vertex.color.g, vertex.color.b, vertex.color.a
        )

    def set_vertex_position(self, index: int, x: float, y: float) -> None:
        """
        #### Быстро устанавливает позицию вершины
        
        ---
        
        :Description:
        - Обновляет только координаты вершины, не затрагивая цвет и текстуру
        - Оптимизированная операция для частых изменений позиции
        
        ---
        
        :Args:
        - index (int): Индекс вершины
        - x (float): Новая X координата
        - y (float): Новая Y координата
        
        ---
        
        :Raises:
        - IndexError: При выходе индекса за границы
        
        ---
        
        :Example:
        ```python
        array.set_vertex_position(0, 100.0, 200.0)
        ```
        """
        if not (0 <= index < len(self)):
            raise IndexError(f"Vertex index {index} out of bounds")
        LIB_MOON._VertexArray_SetVertexPosition(self._ptr, index, x, y)

    def set_vertex_color(self, index: int, color: Color) -> None:
        """
        #### Быстро устанавливает цвет вершины
        
        ---
        
        :Description:
        - Обновляет только цвет вершины, сохраняя позицию и текстурные координаты
        - Эффективная операция для изменения цветов
        
        ---
        
        :Args:
        - index (int): Индекс вершины
        - color (Color): Новый цвет вершины
        
        ---
        
        :Raises:
        - IndexError: При выходе индекса за границы
        
        ---
        
        :Example:
        ```python
        array.set_vertex_color(0, Color(255, 0, 0))  # Красный цвет
        ```
        """
        if not (0 <= index < len(self)):
            raise IndexError(f"Vertex index {index} out of bounds")
        LIB_MOON._VertexArray_SetVertexColor(self._ptr, index, color.r, color.g, color.b, color.a)

    def set_color(self, color: Color) -> None:
        """
        #### Устанавливает цвет для всех вершин массива
        
        ---
        
        :Description:
        - Применяет один цвет ко всем вершинам в массиве
        - Эффективная операция для массового изменения цвета
        - Сохраняет позиции и текстурные координаты
        
        ---
        
        :Args:
        - color (Color): Цвет для применения ко всем вершинам
        
        ---
        
        :Example:
        ```python
        array.set_color(Color(128, 128, 128))  # Серый цвет для всех
        ```
        """
        LIB_MOON._VertexArray_SetAllVerticesColor(self._ptr, color.r, color.g, color.b, color.a)

    def add_vertices(self, vertices: list[Vertex]) -> Self:
        """
        #### Добавляет множество вершин с возвратом self
        
        ---
        
        :Description:
        - Аналог extend(), но возвращает self для цепочки вызовов
        - Последовательно добавляет все вершины из списка
        
        ---
        
        :Args:
        - vertices (list[Vertex]): Список вершин для добавления
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        array.add_vertices([v1, v2, v3]).set_primitive_type(PrimitiveType.TRIANGLES)
        ```
        """
        for vertex in vertices:
            self.append(vertex)
        return self

    def add_vertex_with_texture(self, x: float, y: float, color: Color, tex_x: float, tex_y: float) -> None:
        """
        #### Добавляет вершину с текстурными координатами
        
        ---
        
        :Description:
        - Прямое добавление вершины с указанием всех параметров
        - Оптимизированная версия без создания промежуточного объекта Vertex
        
        ---
        
        :Args:
        - x (float): X координата позиции
        - y (float): Y координата позиции
        - color (Color): Цвет вершины
        - tex_x (float): X координата текстуры
        - tex_y (float): Y координата текстуры
        
        ---
        
        :Example:
        ```python
        array.add_vertex_with_texture(100, 200, Color(255, 0, 0), 0.5, 0.5)
        ```
        """
        LIB_MOON._VertexArray_AddVertexWithTexCoords(
            self._ptr, x, y, color.r, color.g, color.b, color.a, tex_x, tex_y
        )

    def set_vertex_texture_coords(self, index: int, tex_x: float, tex_y: float) -> None:
        """
        #### Устанавливает текстурные координаты вершины
        
        ---
        
        :Description:
        - Обновляет только текстурные координаты указанной вершины
        - Сохраняет позицию и цвет вершины без изменений
        
        ---
        
        :Args:
        - index (int): Индекс вершины
        - tex_x (float): X координата текстуры (обычно 0.0-1.0)
        - tex_y (float): Y координата текстуры (обычно 0.0-1.0)
        
        ---
        
        :Raises:
        - IndexError: При выходе индекса за границы массива
        
        ---
        
        :Example:
        ```python
        array.set_vertex_texture_coords(0, 0.25, 0.75)
        ```
        """
        if not (0 <= index < len(self)):
            raise IndexError(f"Vertex index {index} out of bounds")
        LIB_MOON._VertexArray_SetVertexTexCoords(self._ptr, index, tex_x, tex_y)

    def set_quad_texture_coords(self, start_index: int, left: float, top: float, width: float, height: float) -> None:
        """Устанавливает текстурные координаты для квада (4 вершины)."""
        if not (0 <= start_index < len(self) - 3):
            raise IndexError(f"Quad start index {start_index} out of bounds")
        LIB_MOON._VertexArray_SetQuadTexCoords(self._ptr, start_index, left, top, width, height)

    def add_textured_quad(self, x: float, y: float, width: float, height: float, color: Color, 
                         tex_left: float, tex_top: float, tex_width: float, tex_height: float) -> None:
        """Добавляет текстурированный квад."""
        start_index = len(self)
        
        # Добавляем 4 вершины квада
        self.add_vertex_with_texture(x, y, color, tex_left, tex_top)
        self.add_vertex_with_texture(x + width, y, color, tex_left + tex_width, tex_top)
        self.add_vertex_with_texture(x + width, y + height, color, tex_left + tex_width, tex_top + tex_height)
        self.add_vertex_with_texture(x, y + height, color, tex_left, tex_top + tex_height)