"""
#### *Модуль работы с векторами в Moon*

---

##### Версия: 1.0.0

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 99%

---

✓ Двумерные векторы с плавающей точкой (Vector2f):
  - Математические операции (сложение, вычитание, умножение, деление)
  - Нормализация и вычисление длины
  - Поворот и работа с углами
  - Преобразование типов

✓ Двумерные целочисленные векторы (Vector2i):
  - Все основные математические операции
  - Преобразование в Vector2f
  - Оптимизированная работа с целыми числами

✓ Утилиты для работы с векторами:
  - Проверка параллельности и перпендикулярности
  - Вычисление углов между векторами
  - Скалярное и векторное произведение

---

:Requires:

• Python 3.8+

• Модуль math (стандартная библиотека)

• typing.Self для type hints

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

import math

from typing import Self
from random import uniform





class Vector2f:
    """
    #### Класс двумерного вектора с плавающей точкой
    
    ---
    
    :Description:
    - Представляет точку или направление в 2D пространстве
    - Поддерживает все основные математические операции
    - Оптимизирован для работы с графикой и физикой
    
    ---
    
    :Features:
    - Математические операции (+, -, *, /, +=, -=, *=, /=)
    - Нормализация и работа с длиной вектора
    - Поворот на произвольный угол
    - Преобразование в целочисленный вектор
    """

    __slots__ = ("x", "y")

    @classmethod
    def one(self) -> "Vector2f":
        """
        #### Создает единичный вектор (1, 1)
        
        ---
        
        :Returns:
        - Vector2f: Вектор с координатами (1, 1)
        
        ---
        
        :Example:
        ```python
        unit = Vector2f.one()
        print(unit)  # Vector2f(1.0, 1.0)
        ```
        """
        return Vector2f(1, 1)
    
    @classmethod
    def zero(self) -> "Vector2f":
        """
        #### Создает нулевой вектор (0, 0)
        
        ---
        
        :Returns:
        - Vector2f: Вектор с координатами (0, 0)
        
        ---
        
        :Example:
        ```python
        origin = Vector2f.zero()
        print(origin)  # Vector2f(0.0, 0.0)
        ```
        """
        return Vector2f(0, 0)
    
    @classmethod
    def between(self, point1: list[int | float] | tuple[int | float, int | float], 
                     point2: list[int | float] | tuple[int | float, int | float]):
        """
        #### Создает вектор направления между двумя точками
        
        ---
        
        :Args:
        - point1: Начальная точка [x, y] или (x, y)
        - point2: Конечная точка [x, y] или (x, y)
        
        ---
        
        :Returns:
        - Vector2f: Вектор от point1 к point2
        
        ---
        
        :Example:
        ```python
        direction = Vector2f.normal([0, 0], [3, 4])
        print(direction)  # Vector2f(3.0, 4.0)
        ```
        """
        return Vector2f(point2[0] - point1[0], point2[1] - point1[1])
    
    @classmethod
    def normal(self, vector: "Vector2f") -> "NormalizedVector":
        """
        #### Создает нормальный (перпендикулярный) вектор
        
        ---
        
        :Args:
        - vector (Vector2f): Исходный вектор
        
        ---
        
        :Returns:
        - NormalisedVector: Нормализованный перпендикулярный вектор
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(3, 4)
        normal = Vector2f.normal(vec)  # Перпендикулярный вектор
        """
        if vector.get_lenght() == 0:
            return Vector2f.zero()
        
        return vector.normalize().rotate(90)

    @classmethod
    def random(self) -> "NormalizedVector":
        vector = Vector2f(1, 0).rotate_at(uniform(0, 360))
        return vector

    def __init__(self, x: float | int, y: float | int) -> Self:
        """
        #### Инициализация вектора с координатами
        
        ---
        
        :Args:
        - x (float | int): X координата
        - y (float | int): Y координата
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(3.5, -2.1)
        ```
        """
        self.x = float(x)
        self.y = float(y)

    def to_int(self) -> "Vector2i":
        """
        #### Преобразует в целочисленный вектор
        
        ---
        
        :Returns:
        - Vector2i: Вектор с целочисленными координатами
        
        ---
        
        :Note:
        - Дробная часть отбрасывается (truncation)
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(3.7, -2.3)
        int_vec = vec.to_int()  # Vector2i(3, -2)
        ```
        """
        return Vector2i(int(self.x), int(self.y))
    
    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)
    
    def as_list(self) -> list[float]:
        return [self.x, self.y]

    @property
    def xy(self) -> tuple[float, float]:
        """
        #### Возвращает координаты как кортеж
        
        ---
        
        :Returns:
        - tuple[float, float]: Кортеж (x, y)
        """
        return (self.x, self.y)
    
    @xy.setter
    def xy(self, value: tuple[float, float]) -> None:
        """
        #### Устанавливает координаты из кортежа
        
        ---
        
        :Args:
        - value: Кортеж (x, y) с новыми координатами
        """
        self.x = float(value[0])
        self.y = float(value[1])

    def copy(self) -> "Vector2f":
        """
        #### Создает копию вектора
        
        ---
        
        :Returns:
        - Vector2f: Новый вектор с теми же координатами
        
        ---
        
        :Example:
        ```python
        original = Vector2f(1, 2)
        copy = original.copy()
        ```
        """
        return Vector2f(self.x, self.y)
    
    def get_lenght(self) -> float:
        """
        #### Вычисляет длину (модуль) вектора
        
        ---
        
        :Returns:
        - float: Длина вектора (√(x² + y²))
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(3, 4)
        length = vec.get_lenght()  # 5.0
        ```
        """
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize_at(self) -> Self:
        """
        #### Нормализует вектор на месте (изменяет текущий)
        
        ---
        
        :Description:
        - Приводит длину вектора к 1, сохраняя направление
        - Изменяет текущий объект
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(3, 4)
        vec.normalize_at()  # vec теперь (0.6, 0.8)
        ```
        """
        length = self.get_lenght()
        if length != 0:
            self.x /= length
            self.y /= length
        return self
    
    def normalize(self) -> "Vector2f":
        """
        #### Возвращает нормализованную копию вектора
        
        ---
        
        :Description:
        - Создает новый вектор единичной длины
        - Исходный вектор не изменяется
        
        ---
        
        :Returns:
        - Vector2f: Новый нормализованный вектор
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(3, 4)
        normalized = vec.normalize()  # (0.6, 0.8)
        # vec остается (3, 4)
        ```
        """
        length = self.get_lenght()
        if length != 0:
            return Vector2f(self.x / length, self.y / length)
        return Vector2f(self.x, self.y)
    
    def rotate_at(self, angle: float | int) -> Self:
        """
        #### Поворачивает вектор на месте
        
        ---
        
        :Args:
        - angle (float | int): Угол поворота в градусах
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(1, 0)
        vec.rotate_at(90)  # vec теперь (0, 1)
        ```
        """
        angle = -math.radians(angle)
        cos = math.cos(angle)
        sin = math.sin(angle)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        self.x = x
        self.y = y
        return self
    
    def rotate(self, angle: float | int) -> "Vector2f":
        """
        #### Возвращает повернутую копию вектора
        
        ---
        
        :Args:
        - angle (float | int): Угол поворота в градусах
        
        ---
        
        :Returns:
        - Vector2f: Новый повернутый вектор
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(1, 0)
        rotated = vec.rotate(90)  # (0, 1)
        # vec остается (1, 0)
        ```
        """
        angle = -math.radians(angle)
        cos = math.cos(angle)
        sin = math.sin(angle)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        return Vector2f(x, y)

    def get_angle(self) -> float:
        """
        #### Возвращает угол вектора в градусах
        
        ---
        
        :Returns:
        - float: Угол от 0 до 360 градусов
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(1, 1)
        angle = vec.get_angle()  # 45.0
        ```
        """
        angle = -math.atan2(self.y, self.x) * 180 / math.pi
        return angle if angle >= 0 else angle + 360   
     
    def set_angle(self, angle: float | int) -> Self:
        """
        #### Устанавливает угол вектора, сохраняя длину
        
        ---
        
        :Args:
        - angle (float | int): Новый угол в градусах
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(5, 0)
        vec.set_angle(90)  # vec теперь (0, 5)
        ```
        """
        length = self.get_lenght()
        angle = -angle
        self.x = math.cos(angle * math.pi / 180) * length
        self.y = math.sin(angle * math.pi / 180) * length
        return self
    
    def set_lenght(self, lenght: float | int) -> Self:
        """
        #### Устанавливает длину вектора, сохраняя направление
        
        ---
        
        :Args:
        - lenght (float | int): Новая длина вектора
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(3, 4)  # длина 5
        vec.set_lenght(10)    # теперь (6, 8)
        ```
        """
        length = self.get_lenght()
        if length != 0:
            self.x *= lenght / length
            self.y *= lenght / length
        return self
    
    def is_normalized(self) -> bool:
        """
        #### Проверяет, является ли вектор нормализованным
        
        ---
        
        :Returns:
        - bool: True если длина равна 1
        
        ---
        
        :Example:
        ```python
        vec = Vector2f(0.6, 0.8)
        print(vec.is_normalized())  # True
        ```
        """
        return self.get_lenght() == 1
    
    def is_zero(self) -> bool:
        """
        #### Проверяет, является ли вектор нулевым
        
        ---
        
        :Returns:
        - bool: True если обе координаты равны 0
        
        ---
        
        :Example:
        ```python
        vec = Vector2f.zero()
        print(vec.is_zero())  # True
        ```
        """
        return self.x == 0 and self.y == 0
    
    def __iter__(self):
        return iter((self.x, self.y))
    
    def __copy__(self) -> "Vector2f":
        return self.copy()

    def __repr__(self) -> str:
        return f"Vector2f({self.x}, {self.y})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __eq__(self, other: "Vector2f") -> bool:
        return self.x == other.x and self.y == other.y
        
    def __ne__(self, other: "Vector2f") -> bool:
        return not self.__eq__(other)
    
    def __neg__(self) -> Self:
        return Vector2f(-self.x, -self.y)
    
    def __abs__(self) -> Self:
        return Vector2f(abs(self.x), abs(self.y))
    
    def __add__(self, other: "Vector2f") -> Self:
        return Vector2f(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: "Vector2f") -> Self:
        return Vector2f(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float | int) -> Self:
        if isinstance(scalar, Vector2f):
            return Vector2f(self.x * scalar.x, self.y * scalar.y)
        return Vector2f(self.x * scalar, self.y * scalar)
    
    def __pow__(self, scalar: float | int) -> Self:
        if isinstance(scalar, Vector2f):
            return Vector2f(self.x ** scalar.x, self.y ** scalar.y)
        return Vector2f(self.x ** scalar, self.y ** scalar)
    
    def __truediv__(self, scalar: float | int) -> Self:
        if isinstance(scalar, Vector2f):
            return Vector2f(self.x / scalar.x, self.y / scalar.y)
        return Vector2f(self.x / scalar, self.y / scalar)
    
    def __iadd__(self, other: Self) -> Self:
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: Self) -> Self:
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, scalar: float | int) -> Self:
        if isinstance(scalar, Vector2f):
            self.x *= scalar.x
            self.y *= scalar.y
        else:
            self.x *= scalar
            self.y *= scalar
        return self
    
    def __itruediv__(self, scalar: float | int) -> Self:
        if isinstance(scalar, Vector2f):
            self.x /= scalar.x
            self.y /= scalar.y
        else:
            self.x /= scalar
            self.y /= scalar
        return self
    
# Тип нормализованного вектора == +
NormalizedVector = Vector2f       #
# =============================== +
    

class Vector2i:
    """
    #### Класс двумерного вектора с целочисленными координатами
    
    ---
    
    :Description:
    - Представляет точку или направление в 2D пространстве с целыми координатами
    - Оптимизирован для работы с пиксельными координатами
    - Поддерживает все основные математические операции
    
    ---
    
    :Features:
    - Математические операции с целыми числами
    - Преобразование в Vector2f
    - Защищенные координаты через свойства
    """

    __slots__ = ("__x", "__y")

    def __init__(self, x: int | float, y: int | float):
        """
        #### Инициализация целочисленного вектора
        
        ---
        
        :Args:
        - x (int | float): X координата (будет приведена к int)
        - y (int | float): Y координата (будет приведена к int)
        
        ---
        
        :Example:
        ```python
        vec = Vector2i(3.7, -2.3)  # Vector2i(3, -2)
        ```
        """
        self.__x = int(x)
        self.__y = int(y)
    
    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    def as_list(self) -> list[int]:
        return [self.x, self.y]

    def to_float(self) -> Vector2f:
        """
        #### Преобразует в вектор с плавающей точкой
        
        ---
        
        :Returns:
        - Vector2f: Вектор с координатами float
        
        ---
        
        :Example:
        ```python
        int_vec = Vector2i(3, -2)
        float_vec = int_vec.to_float()  # Vector2f(3.0, -2.0)
        ```
        """
        return Vector2f(float(self.__x), float(self.__y))
    
    def get_lenght(self) -> float:
        """
        #### Вычисляет длину вектора
        
        ---
        
        :Returns:
        - float: Длина вектора (√(x² + y²))
        
        ---
        
        :Example:
        ```python
        vec = Vector2i(3, 4)
        length = vec.get_lenght()  # 5.0
        ```
        """
        return math.sqrt(self.__x * self.__x + self.__y * self.__y)

    @property
    def x(self) -> int:
        return self.__x
        
    @property
    def y(self) -> int:
        return self.__y

    @x.setter
    def x(self, value: int | float) -> None:
        self.__x = int(value)

    @y.setter
    def y(self, value: int | float) -> None:
        self.__y = int(value)

    @property
    def xy(self) -> tuple[int, int]:
        return (self.__x, self.__y)

    @xy.setter
    def xy(self, xy: tuple[int | float, int | float]) -> None:
        self.__x = int(xy[0])
        self.__y = int(xy[1])

    def __iter__(self) -> tuple[int, int]:
        return iter((self.__x, self.__y))

    def __repr__(self) -> str:
        return f"Vector2i({self.__x}, {self.__y})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __eq__(self, other: "Vector2i") -> bool:
        return self.__x == other.x and self.__y == other.y
        
    def __ne__(self, other: "Vector2i") -> bool:
        return not self.__eq__(other)
    
    def __neg__(self) -> "Vector2i":
        return Vector2i(-self.__x, -self.__y)
    
    def __abs__(self) -> "Vector2i":
        return Vector2i(abs(self.__x), abs(self.__y))
    
    def __add__(self, other: "Vector2i") -> "Vector2i":
        return Vector2i(self.__x + other.x, self.__y + other.y)
    
    def __sub__(self, other: "Vector2i") -> "Vector2i":
        return Vector2i(self.__x - other.x, self.__y - other.y)

    def __mul__(self, scalar: int | float) -> "Vector2i":
        if isinstance(scalar, Vector2i):
            return Vector2i(self.__x * scalar.x, self.__y * scalar.y)
        return Vector2i(self.__x * scalar, self.__y * scalar)
    
    def __truediv__(self, scalar: int | float) -> "Vector2i":
        if isinstance(scalar, Vector2i):
            return Vector2i(self.__x / scalar.x, self.__y / scalar.y)
        return Vector2i(self.__x / scalar, self.__y / scalar)
    
    def __iadd__(self, other: "Vector2i") -> "Vector2i":
        self.__x += other.x
        self.__y += other.y
        return self

    def __isub__(self, other: "Vector2i") -> "Vector2i":
        self.__x -= other.x
        self.__y -= other.y
        return self

    def __imul__(self, scalar: int | float) -> "Vector2i":
        if isinstance(scalar, Vector2i):
            self.__x *= scalar.x
            self.__y *= scalar.y
        else:
            self.__x *= scalar
            self.__y *= scalar
        return self
    
    def __itruediv__(self, scalar: int | float) -> "Vector2i":
        if isinstance(scalar, Vector2i):
            self.__x //= scalar.x
            self.__y //= scalar.y
        else:
            self.__x //= scalar
            self.__y //= scalar
        return self

def is_parallel(v1: "VectorType", v2: "VectorType") -> bool:
    """
    #### Проверяет параллельность двух векторов
    
    ---
    
    :Args:
    - v1 (VectorType): Первый вектор
    - v2 (VectorType): Второй вектор
    
    ---
    
    :Returns:
    - bool: True если векторы параллельны
    
    ---
    
    :Example:
    ```python
    v1 = Vector2f(2, 4)
    v2 = Vector2f(1, 2)
    print(is_parallel(v1, v2))  # True
    ```
    """
    return v1.x * v2.y == v1.y * v2.x

def is_perpendicular(v1: "VectorType", v2: "VectorType") -> bool:
    """
    #### Проверяет перпендикулярность двух векторов
    
    ---
    
    :Args:
    - v1 (VectorType): Первый вектор
    - v2 (VectorType): Второй вектор
    
    ---
    
    :Returns:
    - bool: True если векторы перпендикулярны
    
    ---
    
    :Example:
    ```python
    v1 = Vector2f(1, 0)
    v2 = Vector2f(0, 1)
    print(is_perpendicular(v1, v2))  # True
    ```
    """
    return v1.x * v2.x + v1.y * v2.y == 0

def angle_between(v1: "VectorType", v2: "VectorType") -> float:
    """
    #### Вычисляет угол между двумя векторами
    
    ---
    
    :Args:
    - v1 (VectorType): Первый вектор
    - v2 (VectorType): Второй вектор
    
    ---
    
    :Returns:
    - float: Угол в градусах (0-180)
    
    ---
    
    :Example:
    ```python
    v1 = Vector2f(1, 0)
    v2 = Vector2f(0, 1)
    angle = angle_between(v1, v2)  # 90.0
    ```
    """
    return math.degrees(math.acos((v1.x * v2.x + v1.y * v2.y) / (v1.get_lenght() * v2.get_lenght())))

def cross(v1: "VectorType", v2: "VectorType") -> float:
    """
    #### Вычисляет векторное произведение (в 2D - скаляр)
    
    ---
    
    :Args:
    - v1 (VectorType): Первый вектор
    - v2 (VectorType): Второй вектор
    
    ---
    
    :Returns:
    - float: Результат векторного произведения
    
    ---
    
    :Note:
    - Положительное значение означает поворот против часовой стрелки
    - Отрицательное - по часовой стрелке
    
    ---
    
    :Game Applications:
    - Определение стороны поворота (влево/вправо) для AI навигации
    - Проверка пересечения линий и коллизий
    - Вычисление площади треугольников и многоугольников
    - Определение направления вращения объектов
    - Алгоритмы поиска пути и обхода препятствий
    
    ---
    
    :Example:
    ```python
    # Определить, поворачивает ли игрок влево или вправо
    player_forward = Vector2f(1, 0)
    to_target = Vector2f(0, 1)
    turn_direction = cross(player_forward, to_target)  # 1.0 (влево)
    
    # Проверка пересечения отрезков для коллизий
    if cross(line1_dir, line2_dir) != 0:
        print("Линии пересекаются")
    ```
    """
    return v1.x * v2.y - v1.y * v2.x

def dot(v1: "VectorType", v2: "VectorType") -> float:
    """
    #### Вычисляет скалярное произведение векторов
    
    ---
    
    :Args:
    - v1 (VectorType): Первый вектор
    - v2 (VectorType): Второй вектор
    
    ---
    
    :Returns:
    - float: Результат скалярного произведения
    
    ---
    
    :Note:
    - Используется для определения угла между векторами
    - Равно 0 для перпендикулярных векторов
    - Положительное значение - острый угол, отрицательное - тупой
    
    ---
    
    :Game Applications:
    - Определение поля зрения (FOV) для AI и камер
    - Проверка направления взгляда персонажа на цель
    - Вычисление освещения (угол между светом и поверхностью)
    - Определение "за спиной" или "впереди" для стелс-механик
    - Расчет отражения снарядов и физических объектов
    - Оптимизация рендеринга (culling невидимых объектов)
    
    ---
    
    :Example:
    ```python
    # Проверить, видит ли игрок цель (в пределах 90° конуса)
    player_forward = Vector2f(1, 0).normalize()
    to_target = (target_pos - player_pos).normalize()
    visibility = dot(player_forward, to_target)
    if visibility > 0.7:  # cos(45°) ≈ 0.7
        print("Цель в поле зрения")
    
    # Определить, движется ли объект к игроку или от него
    to_player = (player_pos - enemy_pos).normalize()
    enemy_velocity_normalized = enemy_velocity.normalize()
    approaching = dot(to_player, enemy_velocity_normalized) > 0
    ```
    """
    return v1.x * v2.x + v1.y * v2.y


# Union подобный веткорый тип ========= +
type VectorType = Vector2f | Vector2i   #
# ===================================== +

