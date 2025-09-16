"""
#### *Модуль работы с шейдерами в PySGL*

---

##### Версия: 1.1.8

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 90% 

---

✓ Полноценная работа с шейдерами:
  - Загрузка вершинных и фрагментных шейдеров
  - Поддержка геометрических шейдеров
  - Установка uniform переменных различных типов

✓ Гибкая система загрузки:
  - Загрузка из файлов (vertex/fragment)
  - Загрузка из строк в коде
  - Загрузка по типу шейдера

✓ Расширенные возможности:
  - Поддержка текстур в шейдерах
  - Векторные и цветовые uniform'ы
  - Интеграция с системой рендеринга

✓ Готовые интерфейсы:
  - Shader - основной класс для работы с шейдерами
  - Type - перечисление типов шейдеров
  - Методы класса для быстрого создания

---

:Requires:

• Python 3.8+

• Библиотека ctypes (для работы с DLL)

• PySGL.dll (нативная библиотека рендеринга)

• OpenGL 3.3+ (для поддержки шейдеров)

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
from enum import Enum

import os
from Moon.python.Vectors import Vector2f, Vector2i
from Moon.python.Colors import Color

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



LIB_MOON._Shader_Create.argtypes = None
LIB_MOON._Shader_Create.restype = ctypes.c_void_p
LIB_MOON._Shader_LoadFromFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
LIB_MOON._Shader_LoadFromFile.restype = ctypes.c_bool
LIB_MOON._Shader_LoadFromStrings.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
LIB_MOON._Shader_LoadFromStrings.restype = ctypes.c_bool
LIB_MOON._Shader_LoadFromStringWithType.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
LIB_MOON._Shader_LoadFromStringWithType.restype = ctypes.c_bool
LIB_MOON._Shader_GetCurrentTexture.argtypes = None
LIB_MOON._Shader_GetCurrentTexture.restype = ctypes.c_void_p

LIB_MOON._Shader_SetUniformInt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
LIB_MOON._Shader_SetUniformFloat.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_float]
LIB_MOON._Shader_SetUniformBool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_bool]
LIB_MOON._Shader_SetUniformTexture.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
LIB_MOON._Shader_SetUniformIntVector.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
LIB_MOON._Shader_SetUniformFloatVector.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._Shader_SetUniformColor.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]


ShaderPtr = ctypes.c_void_p

def get_current_texture() -> ctypes.c_void_p:
    """
    #### Получает указатель на текущую активную текстуру
    
    ---
    
    :Description:
    - Возвращает указатель на текстуру, которая в данный момент привязана к OpenGL контексту
    - Используется для передачи текущей текстуры в uniform переменные шейдера
    - Полезно для создания эффектов постобработки
    
    ---
    
    :Returns:
    - ctypes.c_void_p: Указатель на активную текстуру
    
    ---
    
    :Example:
    ```python
    current_tex = get_current_texture()
    shader.set_uniform("u_texture", current_tex)
    ```
    """
    return LIB_MOON._Shader_GetCurrentTexture()


class Shader:
    """
    #### Класс для работы с OpenGL шейдерами
    
    ---
    
    :Description:
    - Обеспечивает загрузку, компиляцию и использование шейдеров
    - Поддерживает вершинные, геометрические и фрагментные шейдеры
    - Предоставляет удобный интерфейс для установки uniform переменных
    
    ---
    
    :Features:
    - Загрузка шейдеров из файлов или строк
    - Автоматическая компиляция и линковка
    - Типобезопасная установка uniform переменных
    - Поддержка текстур, векторов и цветов
    """

    class Type(Enum):
        """
        #### Перечисление типов шейдеров
        
        ---
        
        :Values:
        - VERTEX: Вершинный шейдер (обработка вершин)
        - GEOMETRY: Геометрический шейдер (генерация геометрии)
        - FRAGMENT: Фрагментный шейдер (обработка пикселей)
        
        ---
        
        :Note:
        - Вершинный и фрагментный шейдеры обязательны
        - Геометрический шейдер опционален
        """
        VERTEX = 0
        GEOMETRY = 1
        FRAGMENT = 2

    @classmethod
    def FromString(cls, fragment: str, vertex: str) -> "Shader":
        """
        #### Создает шейдер из строк с исходным кодом
        
        ---
        
        :Description:
        - Создает новый объект шейдера и загружает в него код из строк
        - Автоматически компилирует и линкует шейдерную программу
        - Удобно для встроенных в код шейдеров
        
        ---
        
        :Args:
        - fragment (str): Исходный код фрагментного шейдера
        - vertex (str): Исходный код вершинного шейдера
        
        ---
        
        :Returns:
        - Shader: Готовый к использованию объект шейдера
        
        ---
        
        :Example:
        ```python
        vertex_code = 

        #version 330 core
        layout (location = 0) in vec3 aPos;
        void main() {
            gl_Position = vec4(aPos, 1.0);
        }
        
        
        fragment_code = 

        #version 330 core
        out vec4 FragColor;
        void main() {
            FragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
        
        
        shader = Shader.FromString(fragment_code, vertex_code)
        ```
        """
        shader = Shader()
        shader.load_from_strings(fragment, vertex)
        return shader
    
    @classmethod
    def FromFile(cls, fragment_path: str, vertex_path: str) -> "Shader":
        """
        #### Создает шейдер из файлов
        
        ---
        
        :Description:
        - Загружает исходный код шейдеров из указанных файлов
        - Автоматически читает содержимое файлов и компилирует шейдеры
        - Рекомендуемый способ для больших шейдерных программ
        
        ---
        
        :Args:
        - fragment_path (str): Путь к файлу фрагментного шейдера (.frag)
        - vertex_path (str): Путь к файлу вершинного шейдера (.vert)
        
        ---
        
        :Returns:
        - Shader: Готовый к использованию объект шейдера
        
        ---
        
        :Raises:
        - FileNotFoundError: Если один из файлов не найден
        - IOError: При ошибке чтения файлов
        
        ---
        
        :Example:
        ```python
        shader = Shader.FromFile("shaders/basic.frag", "shaders/basic.vert")
        ```
        """
        shader = Shader()
        shader.load_from_files(fragment_path, vertex_path)
        return shader
    
    @classmethod
    def FromType(cls, type: Type, source: str) -> "Shader":
        """
        #### Создает шейдер определенного типа из строки
        
        ---
        
        :Description:
        - Загружает шейдер конкретного типа (вершинный, геометрический или фрагментный)
        - Полезно для загрузки отдельных шейдеров или compute шейдеров
        - Выводит сообщение о результате загрузки
        
        ---
        
        :Args:
        - type (Type): Тип шейдера из перечисления Shader.Type
        - source (str): Исходный код шейдера
        
        ---
        
        :Returns:
        - Shader: Объект шейдера (может быть неполным)
        
        ---
        
        :Example:
        ```python
        compute_code = 

        #version 430
        layout(local_size_x = 1, local_size_y = 1) in;
        void main() {
            // compute shader logic
        }
        
        
        shader = Shader.FromType(Shader.Type.FRAGMENT, compute_code)
        ```
        """
        shader = Shader()
        if shader.load_from_type(type, source):
            print("Shader loaded!")
        else:
            print("Shader not loaded!")
        return shader

    def __init__(self):
        """
        #### Инициализация объекта шейдера
        
        ---
        
        :Description:
        - Создает пустой объект шейдера с нативным указателем
        - Инициализирует внутренние переменные для хранения данных
        - Шейдер готов к загрузке исходного кода
        
        ---
        
        :Note:
        - После создания необходимо загрузить шейдерный код
        - Используйте методы load_from_* или FromString/FromFile
        """
        self._ptr: ShaderPtr | None = LIB_MOON._Shader_Create()
        self.__fragment_data: str = ""
        self.__vertex_data: str = ""

        self.__fragment_path: str | None = None
        self.__vertex_path: str | None =  None

    def set_uniform(self, name: str, value: int | float | bool | Vector2i | Vector2f | Color | ctypes.c_void_p) -> "Shader":
        """
        #### Устанавливает значение uniform переменной в шейдере
        
        ---
        
        :Description:
        - Передает данные из Python кода в шейдерную программу
        - Автоматически определяет тип данных и вызывает соответствующую функцию
        - Поддерживает все основные типы данных OpenGL
        
        ---
        
        :Args:
        - name (str): Имя uniform переменной в шейдере
        - value: Значение для установки (поддерживаемые типы ниже)
        
        ---
        
        :Supported Types:
        - int: Целое число (uniform int)
        - float: Дробное число (uniform float)
        - bool: Логическое значение (uniform bool)
        - Vector2i: Вектор из двух целых чисел (uniform ivec2)
        - Vector2f: Вектор из двух дробных чисел (uniform vec2)
        - Color: Цвет RGBA (uniform vec4)
        - ctypes.c_void_p: Указатель на текстуру (uniform sampler2D)
        
        ---
        
        :Returns:
        - Shader: Возвращает self для цепочки вызовов
        
        ---
        
        :Raises:
        - TypeError: При передаче неподдерживаемого типа данных
        
        ---
        
        :Example:
        ```python
        # Установка различных типов uniform переменных
        shader.set_uniform("u_time", 1.5)  # float
        shader.set_uniform("u_resolution", Vector2f(800, 600))  # vec2
        shader.set_uniform("u_color", Color(255, 0, 0))  # vec4
        shader.set_uniform("u_texture", texture_ptr)  # sampler2D
        shader.set_uniform("u_enabled", True)  # bool
        ```
        """
        if isinstance(value, bool):
            LIB_MOON._Shader_SetUniformBool(self._ptr, name.encode('utf-8'), value)
        elif isinstance(value, int):
            LIB_MOON._Shader_SetUniformInt(self._ptr, name.encode('utf-8'), value)
        elif isinstance(value, float):
            LIB_MOON._Shader_SetUniformFloat(self._ptr, name.encode('utf-8'), value)
        elif isinstance(value, ctypes.c_void_p):
            LIB_MOON._Shader_SetUniformTexture(self._ptr, name.encode('utf-8'), value)
        elif isinstance(value, Vector2f):
            LIB_MOON._Shader_SetUniformFloatVector(self._ptr, name.encode('utf-8'), float(value.x), float(value.y))
        elif isinstance(value, Vector2i):
            LIB_MOON._Shader_SetUniformIntVector(self._ptr, name.encode('utf-8'), int(value.x), int(value.y))
        elif isinstance(value, Color):
            LIB_MOON._Shader_SetUniformColor(self._ptr, name.encode('utf-8'), int(value.r), int(value.g), int(value.b), int(value.a))
        else:
            raise TypeError("Invalid uniform type.")
        
        return self

    def get_ptr(self) -> ShaderPtr:
        """
        #### Возвращает указатель на нативный объект шейдера
        
        ---
        
        :Description:
        - Предоставляет доступ к внутреннему указателю для системы рендеринга
        - Используется методом Window.draw() для применения шейдера
        - Не предназначен для прямого использования пользователем
        
        ---
        
        :Returns:
        - ShaderPtr: Указатель на нативный объект шейдера
        """
        return self._ptr

    def set_ptr(self, ptr: ShaderPtr) -> "Shader":
        """
        #### Устанавливает указатель на нативный объект шейдера
        
        ---
        
        :Description:
        - Позволяет заменить внутренний указатель на другой
        - Используется для продвинутых сценариев работы с шейдерами
        - Будьте осторожны при использовании этого метода
        
        ---
        
        :Args:
        - ptr (ShaderPtr): Новый указатель на нативный объект
        
        ---
        
        :Returns:
        - Shader: Возвращает self для цепочки вызовов
        
        ---
        
        :Warning:
        - Неправильное использование может привести к ошибкам
        - Убедитесь, что указатель валиден
        """
        self._ptr = ptr
        return self
    
    def load_from_type(self, type: Type, source: str) -> bool:
        """
        #### Загружает шейдер определенного типа из строки
        
        ---
        
        :Description:
        - Компилирует шейдер указанного типа из исходного кода
        - Полезно для загрузки отдельных компонентов шейдерной программы
        - Возвращает результат компиляции
        
        ---
        
        :Args:
        - type (Type): Тип шейдера (VERTEX, GEOMETRY, FRAGMENT)
        - source (str): Исходный код шейдера на GLSL
        
        ---
        
        :Returns:
        - bool: True если компиляция успешна, False при ошибке
        
        ---
        
        :Example:
        ```python
        vertex_code = 

        #version 330 core
        layout (location = 0) in vec3 aPos;
        void main() {
            gl_Position = vec4(aPos, 1.0);
        }
        
        
        success = shader.load_from_type(Shader.Type.VERTEX, vertex_code)
        if not success:
            print("Ошибка компиляции вершинного шейдера")
        ```
        """
        return LIB_MOON._Shader_LoadFromStringWithType(self._ptr, source.encode('utf-8'), type.value)
    
    def load_from_strings(self, fragment: str, vertex: str) -> "Shader":
        """
        #### Загружает шейдерную программу из строк с исходным кодом
        
        ---
        
        :Description:
        - Компилирует и линкует полную шейдерную программу из двух строк
        - Сохраняет исходный код во внутренних переменных для отладки
        - Автоматически создает готовую к использованию шейдерную программу
        
        ---
        
        :Args:
        - fragment (str): Исходный код фрагментного шейдера
        - vertex (str): Исходный код вершинного шейдера
        
        ---
        
        :Returns:
        - Shader: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        shader = Shader()
        shader.load_from_strings(fragment_code, vertex_code)
        
        # Или через цепочку вызовов
        shader = Shader().load_from_strings(fragment_code, vertex_code)
        ```
        """
        self.__fragment_data = fragment
        self.__vertex_data = vertex
        LIB_MOON._Shader_LoadFromStrings(self._ptr, self.__vertex_data.encode('utf-8'), self.__fragment_data.encode('utf-8'))
        return self

    def load_from_files(self, fragment_path: str, vertex_path: str) -> "Shader":
        """
        #### Загружает шейдерную программу из файлов
        
        ---
        
        :Description:
        - Читает исходный код шейдеров из указанных файлов
        - Сохраняет пути к файлам и содержимое для отладки
        - Компилирует и линкует полную шейдерную программу
        
        ---
        
        :Args:
        - fragment_path (str): Путь к файлу фрагментного шейдера
        - vertex_path (str): Путь к файлу вершинного шейдера
        
        ---
        
        :Returns:
        - Shader: Возвращает self для цепочки вызовов
        
        ---
        
        :Raises:
        - FileNotFoundError: Если один из файлов не найден
        - IOError: При ошибке чтения файлов
        - UnicodeDecodeError: При проблемах с кодировкой файлов
        
        ---
        
        :Example:
        ```python
        shader = Shader()
        shader.load_from_files("shaders/basic.frag", "shaders/basic.vert")
        
        # Проверка загруженных путей
        print(f"Fragment: {shader._Shader__fragment_path}")
        print(f"Vertex: {shader._Shader__vertex_path}")
        ```
        """
        self.__fragment_path = fragment_path
        self.__vertex_path = vertex_path
        self.__fragment_data = open(self.__fragment_path, 'r').read()
        self.__vertex_data = open(self.__vertex_path, 'r').read()
        LIB_MOON._Shader_LoadFromFile(self._ptr, self.__vertex_path.encode('utf-8'), self.__fragment_path.encode('utf-8'))
        return self
    