"""
#### *Модуль работы с цветами в Moon*

---

##### Версия: 1.0.3

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 100%

---

✓ Полноценная работа с цветами:
  - Поддержка форматов RGB/RGBA
  - Преобразования между цветовыми пространствами
  - Генерация случайных цветов

✓ Расширенные возможности:
  - Гармоничные цветовые палитры
  - Плавные цветовые градиенты
  - Математические операции с цветами

✓ Оптимизированные алгоритмы:
  - Быстрые преобразования цветов
  - Эффективные методы смешивания
  - Оптимизированные градиенты

✓ Готовые интерфейсы:
  - Color - базовый класс цвета
  - BaseColorGradient - простой градиент
  - ColorGradient - многоцветный градиент
  - ColorGradientEx - расширенный градиент

✓ Встроенные цветовые палитры:
  - Базовые цвета (RGB, CMYK)
  - Веб-цвета
  - Современные UI цвета
  - Специальные градиенты (радуга)

---

:Requires:

• Python 3.8+

• Стандартная библиотека math

• Стандартная библиотека random

• Стандартная библиотека colorsys


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
import random
import colorsys
from typing import Literal, Final, Self, final



# Тип для представления цвета в виде массива RGBA ==== +
type RGBAColorAsArrayType = tuple[int, int, int, int]
# ==================================================== +

# Тип для представления массива цветов в виде RGBA ===================================== +
type RGBAColorsArrayType = list[RGBAColorAsArrayType] | tuple[RGBAColorAsArrayType, ...]
# ====================================================================================== +

# Тип для представления цвета в виде массива RGB ===== +
type RGBColorAsArrayType = tuple[int, int, int]
# ==================================================== +

# Тип для представления массива цветов в виде RGB ====================================== +
type RGBColorsArrayType = list[RGBColorAsArrayType] | tuple[RGBColorAsArrayType, ...]
# ====================================================================================== +


# Класс для хранения и манипуляции с цветами `RGBA`
@final
class Color:
    __slots__ = ('r', 'g', 'b', 'a')

    @classmethod
    def random(cls) -> 'Color':
        """
        #### Генерирует полностью непрозрачный случайный цвет

        ---

        :Return:
        - Color(r, g, b, 255) - Случайный цвет

        ---

        :Example:
        ```python
        color = Color.random()
        print(color)  # Например: Color(123, 45, 67, 255)
        ```
        """
        return cls(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    @classmethod
    def random_alpha(cls) -> 'Color':
        """
        #### Генерирует случайный цвет со случайной прозрачностью

        ---

        :Return:
        - Color(r, g, b, a) - Случайный цвет с альфа-каналом

        ---

        :Example:
        ```python
        color = Color.random_alpha()
        print(color)  # Например: Color(123, 45, 67, 128)
        ```
        """
        return cls(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def __init__(self, r: int, g: int, b: int, a: int = 255):
        """
        #### Инициализирует цвет в формате RGBA

        ---

        :Args:
        - r - Красный компонент (0-255)
        - g - Зеленый компонент (0-255)
        - b - Синий компонент (0-255)
        - a - Альфа-канал (0-255, по умолчанию 255)

        ---

        :Raises:
        - ValueError: Если компоненты выходят за допустимый диапазон

        ---

        :Example:
        ```python
        red = Color(255, 0, 0)  # Красный цвет
        semi_transparent = Color(0, 255, 0, 128)  # Полупрозрачный зеленый
        ```
        """

        self.r = int(min(max(r, 0), 255))
        self.g = int(min(max(g, 0), 255))
        self.b = int(min(max(b, 0), 255))
        self.a = int(min(max(a, 0), 255))

    def copy(self) -> "Color":
        return Color(self.r, self.g, self.b, self.a)

    def lighten(self, factor: float) -> "Color":
        """
        #### Осветляет цвет, смешивая его с белым

        ---

        :Args:
        - factor - Коэффициент осветления (0.0 - исходный цвет, 1.0 - полностью белый)

        ---

        :Return:
        - Color - Новый осветленный цвет

        ---

        :Raises:
        - ValueError: Если factor вне диапазона [0, 1]

        ---

        :Example:
        ```python
        blue = Color(0, 0, 255)
        light_blue = blue.lighten(0.3)  # Осветленный на 30% синий
        ```
        """
        if not 0 <= factor <= 1:
            raise ValueError("Factor must be between 0 and 1")

        r = int(self.r + (255 - self.r) * factor)
        g = int(self.g + (255 - self.g) * factor)
        b = int(self.b + (255 - self.b) * factor)

        return Color(r, g, b, self.a)

    def darken(self, factor: float) -> "Color":
        """
        #### Затемняет цвет, смешивая его с черным

        ---

        :Args:
        - factor - Коэффициент затемнения (0.0 - исходный цвет, 1.0 - полностью черный)

        ---

        :Return:
        - Color - Новый затемненный цвет

        ---

        :Raises:
        - ValueError: Если factor вне диапазона [0, 1]

        ---

        :Example:
        ```python
        red = Color(255, 0, 0)
        dark_red = red.darken(0.4)  # Затемненный на 40% красный
        ```
        """
        if not 0 <= factor <= 1:
            raise ValueError("Factor must be between 0 and 1")

        r = int(self.r * (1 - factor))
        g = int(self.g * (1 - factor))
        b = int(self.b * (1 - factor))
        return Color(r, g, b, self.a)

    def lighten_hsv(self, factor: float) -> "Color":
        """
        #### Осветляет цвет через увеличение Value в HSV

        ---

        :Args:
        - factor - Коэффициент осветления (0.0 - без изменений, 1.0 - максимальное осветление)

        ---

        :Return:
        - Color - Новый цвет с увеличенной яркостью

        ---

        :Raises:
        - ValueError: Если factor вне диапазона [0, 1]

        ---

        :Example:
        ```python
        green = Color(0, 128, 0)
        light_green = green.lighten_hsv(0.5)  # Осветленный в HSV пространстве
        ```
        """
        if not 0 <= factor <= 1:
            raise ValueError("Factor must be between 0 and 1")

        h, s, v = colorsys.rgb_to_hsv(self.r/255, self.g/255, self.b/255)
        new_v = min(1.0, v + (1 - v) * factor)
        r, g, b = colorsys.hsv_to_rgb(h, s, new_v)

        return Color(int(r*255), int(g*255), int(b*255), self.a)

    def darken_hsv(self, factor: float) -> "Color":
        """
        #### Затемняет цвет через уменьшение Value в HSV

        ---

        :Args:
        - factor - Коэффициент затемнения (0.0 - без изменений, 1.0 - полное затемнение)

        ---

        :Return:
        - Color - Новый цвет с уменьшенной яркостью

        ---

        :Raises:
        - ValueError: Если factor вне диапазона [0, 1]

        ---

        :Example:
        ```python
        yellow = Color(255, 255, 0)
        dark_yellow = yellow.darken_hsv(0.6)  # Затемненный в HSV пространстве
        ```
        """
        if not 0 <= factor <= 1:
            raise ValueError("Factor must be between 0 and 1")

        h, s, v = colorsys.rgb_to_hsv(self.r/255, self.g/255, self.b/255)
        new_v = max(0.0, v * (1 - factor))
        r, g, b = colorsys.hsv_to_rgb(h, s, new_v)

        return Color(int(r*255), int(g*255), int(b*255), self.a)

    def invert(self) -> "Color":
        """
        #### Инвертирует компоненты цвета и возвращает новый объект Color

        ---

        :Return:
        - Color - Инвертированный цвет

        ---

        :Example:
        ```python
        white = Color(255, 255, 255)
        black = white.invert()  # Color(0, 0, 0)
        ```
        """
        return Color(255 - self.r, 255 - self.g, 255 - self.b, self.a)

    def invert_this(self) -> "Color":
        """
        #### Инвертирует компоненты данного цвета

        ---

        :Return:
        - Color - Инвертированный цвет

        ---

        :Example:
        ```python
        white = Color(255, 255, 255)
        white.invert_this()  # Color(0, 0, 0)
        ```
        """
        self.r, self.g, self.b = 255 - self.r, 255 - self.g, 255 - self.b
        return self

    def set_alpha(self, a: int | float) -> "Color":
        """
        #### Устанавливает значение альфа-канала

        ---

        :Args:
        - a - Новое значение альфа-канала (0-255)

        ---

        :Return:
        - Color - Текущий объект цвета (для цепочки вызовов)

        ---

        :Raises:
        - ValueError: Если значение вне диапазона [0, 255]

        ---

        :Example:
        ```python
        color = Color(255, 0, 0).set_alpha(128)  # Полупрозрачный красный
        ```
        """
        a = abs(a)
        a = max(0, min(255, a))
        if not 0 <= a <= 255:
            raise ValueError("Alpha must be between 0 and 255")
        self.a = int(a)
        return self

    def set_alpha_float(self, a: float) -> "Color":
        """
        #### Устанавливает альфа-канал в диапазоне 0.0-1.0

        ---

        :Args:
        - a - Новое значение альфа-канала (0.0-1.0)

        ---

        :Return:
        - Color - Текущий объект цвета (для цепочки вызовов)

        ---

        :Raises:
        - ValueError: Если значение вне диапазона [0.0, 1.0]

        ---

        :Example:
        ```python
        color = Color(0, 0, 255).set_alpha_float(0.5)  # Полупрозрачный синий
        ```
        """
        if not (0 <= a <= 1):
            raise ValueError("Alpha must be between 0.0 and 1.0")
        self.a = int(255 * a)
        return self

    def __mul__(self, number: float | int) -> "Color":
        """
        #### Умножает цвет на коэффициент (перегрузка оператора *)

        ---

        :Args:
        - number - Коэффициент умножения (-1.0 до 1.0)

        ---

        :Return:
        - Color - Результат умножения

        ---

        :Raises:
        - TypeError: Если коэффициент вне допустимого диапазона

        ---

        :Note:
        - Положительные значения затемняют цвет
        - Отрицательные значения осветляют цвет
        """
        if not (-1 <= number <= 1):
            raise TypeError("Color must be mul with float number (-1.0 - 1.0)")
        if number >= 0:
            return Color(int(self.r * number), int(self.g * number), int(self.b * number), self.a)
        else:
            r = (255 - self.r) * number
            g = (255 - self.g) * number
            b = (255 - self.b) * number
            return Color(int(round(r)), int(round(g)), int(round(b)), self.a)

    def mul(self, number: float | int) -> "Color":
        """
        #### Умножает цвет на заданное число

        ---

        :Args:
        - number - Коэффициент умножения (-1.0 до 1.0)

        ---

        :Return:
        - Color - Результат умножения

        ---

        :Raises:
        - TypeError: Если коэффициент вне допустимого диапазона

        ---

        :Example:
        ```python
        color = Color(100, 100, 100)
        darker = color.mul(0.5)  # Color(50, 50, 50)
        lighter = color.mul(-0.5)  # Color(178, 178, 178)
        ```
        """
        return self.__mul__(number)

    @property
    def rgb(self) -> RGBColorAsArrayType:
        """
        #### Возвращает RGB компоненты цвета

        ---

        :Return:
        - tuple[int, int, int] - Кортеж (r, g, b)

        ---

        :Example:
        ```python
        color = Color(255, 128, 0)
        print(color.rgb)  # (255, 128, 0)
        ```
        """
        return (self.r, self.g, self.b)

    @property
    def rgba(self) -> RGBAColorAsArrayType:
        """
        #### Возвращает RGBA компоненты цвета

        ---

        :Return:
        - tuple[int, int, int, int] - Кортеж (r, g, b, a)

        ---

        :Example:
        ```python
        color = Color(255, 0, 0, 128)
        print(color.rgba)  # (255, 0, 0, 128)
        ```
        """
        return (self.r, self.g, self.b, self.a)

    @property
    def hex(self) -> str:
        """
        #### Возвращает HEX представление цвета

        ---

        :Return:
        - str - Строка в формате "#RRGGBB"

        ---

        :Example:
        ```python
        color = Color(255, 0, 0)
        print(color.hex)  # "#ff0000"
        ```
        """
        return "#{:02x}{:02x}{:02x}".format(self.r, self.g, self.b)

    def __str__(self) -> str:
        """
        #### Строковое представление цвета

        ---

        :Return:
        - str - Строка в формате "Color: (r, g, b, a)"
        """
        return f"Color: {self.rgba}"

    def __repr__(self) -> str:
        """
        #### Официальное строковое представление объекта

        ---

        :Return:
        - str - Строка, которую можно использовать для eval()
        """
        return self.__str__()

# Тип для хранения массива цветов ===================== +
type ColorArrayType = list[Color] | tuple[Color, ...]
# ===================================================== +

# Функция реализует инструмент Coolors, будет возвращать набор связанных цветов по различным схемам.
# Очень мощный инструмент!
def generate_palette(
    color: Color,
    scheme: Literal["analogous", "monochromatic", "complementary", "split_complementary",
                   "triadic", "tetradic", "square"] = "complementary",
    num_colors: int = 5,
    saturation_range: tuple[float, float] = (0.7, 1.0),
    brightness_range: tuple[float, float] = (0.6, 0.9)
) -> ColorArrayType:
    """
    #### Генерирует гармоничную цветовую палитру на основе базового цвета

    ---

    :Args:
    - color - Базовый цвет для генерации палитры
    - scheme - Схема генерации (по умолчанию 'complementary'):
      - 'analogous': соседние цвета в цветовом круге (±30°)
      - 'monochromatic': оттенки одного цвета
      - 'complementary': основной цвет + его дополнение
      - 'split_complementary': основной цвет + два соседних к дополнению
      - 'triadic': три равноудаленных цвета (120°)
      - 'tetradic': четыре цвета (две комплементарные пары)
      - 'square': четыре цвета через 90°
    - num_colors - Количество цветов в палитре (2-5, для некоторых схем фиксировано)
    - saturation_range - Диапазон насыщенности (0.0-1.0)
    - brightness_range - Диапазон яркости (0.0-1.0)

    ---

    :Return:
    - list[Color] - Список сгенерированных цветов

    ---

    :Raises:
    - ValueError: Если параметры выходят за допустимые диапазоны

    ---

    :Example:
    ```python
    # Генерация триадной палитры из синего цвета
    blue = Color(0, 0, 255)
    palette = generate_palette(blue, scheme='triadic', num_colors=3)

    # Генерация монохроматической палитры с 5 оттенками
    red_palette = generate_palette(Color(255, 0, 0), 'monochromatic', 5)
    ```
    """
    if num_colors < 2:
        raise ValueError("Number of colors must be at least 2")

    if not (0 <= saturation_range[0] <= 1 and 0 <= saturation_range[1] <= 1):
        raise ValueError("Saturation range must be between 0 and 1")

    if not (0 <= brightness_range[0] <= 1 and 0 <= brightness_range[1] <= 1):
        raise ValueError("Brightness range must be between 0 and 1")

    # Конвертация базового цвета в HSV
    h, s, v = colorsys.rgb_to_hsv(color.r/255, color.g/255, color.b/255)

    colors = []

    if scheme == "monochromatic":
        # Генерация вариаций насыщенности и яркости
        for i in range(num_colors):
            new_s = saturation_range[0] + (saturation_range[1]-saturation_range[0]) * (i/(num_colors-1))
            new_v = brightness_range[0] + (brightness_range[1]-brightness_range[0]) * (i/(num_colors-1))
            r, g, b = colorsys.hsv_to_rgb(h, new_s, new_v)
            colors.append(Color(int(r*255), int(g*255), int(b*255)))

    elif scheme == "analogous":
        # Соседние цвета (±30° в цветовом круге)
        angles = [-30, -15, 0, 15, 30][:num_colors]
        for angle in angles:
            new_h = (h + angle/360) % 1.0
            r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
            colors.append(Color(int(r*255), int(g*255), int(b*255)))

    elif scheme == "complementary":
        # Основной цвет + комплементарный (противоположный)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        colors.append(Color(int(r*255), int(g*255), int(b*255)))
        r, g, b = colorsys.hsv_to_rgb((h+0.5)%1.0, s, v)
        colors.append(Color(int(r*255), int(g*255), int(b*255)))

    elif scheme == "split_complementary":
        # Основной цвет + два соседних к комплементарному
        base_r, base_g, base_b = colorsys.hsv_to_rgb(h, s, v)
        colors.append(Color(int(base_r*255), int(base_g*255), int(base_b*255)))

        for angle in [150, 210]:  # ±30° от комплементарного
            new_h = (h + angle/360) % 1.0
            r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
            colors.append(Color(int(r*255), int(g*255), int(b*255)))

    elif scheme == "triadic":
        # Три равноудаленных цвета (через 120°)
        for i in range(3):
            new_h = (h + i/3) % 1.0
            r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
            colors.append(Color(int(r*255), int(g*255), int(b*255)))

    elif scheme == "tetradic":
        # Две комплементарные пары (4 цвета)
        angles = [0, 0.25, 0.5, 0.75][:num_colors]
        for angle in angles:
            new_h = (h + angle) % 1.0
            r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
            colors.append(Color(int(r*255), int(g*255), int(b*255)))

    elif scheme == "square":
        # Четыре цвета через 90°
        for i in range(4):
            new_h = (h + i*0.25) % 1.0
            r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
            colors.append(Color(int(r*255), int(g*255), int(b*255)))

    # Добавление случайных вариаций насыщенности и яркости
    if scheme != "monochromatic":
        for i in range(len(colors)):
            h2, s2, v2 = colorsys.rgb_to_hsv(colors[i].r/255, colors[i].g/255, colors[i].b/255)
            new_s = max(0, min(1, s2 * random.uniform(*saturation_range)))
            new_v = max(0, min(1, v2 * random.uniform(*brightness_range)))
            r, g, b = colorsys.hsv_to_rgb(h2, new_s, new_v)
            colors[i] = Color(int(r*255), int(g*255), int(b*255))

    return colors[:num_colors]


# Основные цвета
COLOR_RED: Final[Color] = Color(255, 0, 0)
COLOR_GREEN: Final[Color] = Color(0, 255, 0)
COLOR_BLUE: Final[Color] = Color(0, 0, 255)
COLOR_YELLOW: Final[Color] = Color(255, 255, 0)
COLOR_CYAN: Final[Color] = Color(0, 255, 255)
COLOR_MAGENTA: Final[Color] = Color(255, 0, 255)
COLOR_WHITE: Final[Color] = Color(255, 255, 255)
COLOR_BLACK: Final[Color] = Color(0, 0, 0)

# Дополнительные базовые цвета
COLOR_ORANGE: Final[Color] = Color(255, 165, 0)
COLOR_PURPLE: Final[Color] = Color(128, 0, 128)
COLOR_PINK: Final[Color] = Color(255, 192, 203)
COLOR_BROWN: Final[Color] = Color(165, 42, 42)
COLOR_GRAY: Final[Color] = Color(128, 128, 128)
COLOR_LIGHT_GRAY: Final[Color] = Color(211, 211, 211)
COLOR_DARK_GRAY: Final[Color] = Color(169, 169, 169)

# Металлические цвета
COLOR_GOLD: Final[Color] = Color(255, 215, 0)
COLOR_SILVER: Final[Color] = Color(192, 192, 192)
COLOR_BRONZE: Final[Color] = Color(205, 127, 50)
COLOR_ROSE_GOLD: Final[Color] = Color(183, 110, 121)

# Оттенки синего
COLOR_NAVY: Final[Color] = Color(0, 0, 128)
COLOR_DARK_BLUE: Final[Color] = Color(0, 0, 139)
COLOR_MIDNIGHT_BLUE: Final[Color] = Color(25, 25, 112)
COLOR_ROYAL_BLUE: Final[Color] = Color(65, 105, 225)
COLOR_STEEL_BLUE: Final[Color] = Color(70, 130, 180)
COLOR_SKY_BLUE: Final[Color] = Color(135, 206, 235)
COLOR_LIGHT_BLUE: Final[Color] = Color(173, 216, 230)

# Оттенки зеленого
COLOR_LIME: Final[Color] = Color(0, 255, 0)
COLOR_FOREST_GREEN: Final[Color] = Color(34, 139, 34)
COLOR_OLIVE: Final[Color] = Color(128, 128, 0)
COLOR_DARK_GREEN: Final[Color] = Color(0, 100, 0)
COLOR_SEA_GREEN: Final[Color] = Color(46, 139, 87)
COLOR_SPRING_GREEN: Final[Color] = Color(0, 255, 127)
COLOR_EMERALD: Final[Color] = Color(80, 200, 120)

# Оттенки красного
COLOR_DARK_RED: Final[Color] = Color(139, 0, 0)
COLOR_CRIMSON: Final[Color] = Color(220, 20, 60)
COLOR_FIREBRICK: Final[Color] = Color(178, 34, 34)
COLOR_TOMATO: Final[Color] = Color(255, 99, 71)
COLOR_SALMON: Final[Color] = Color(250, 128, 114)
COLOR_LIGHT_CORAL: Final[Color] = Color(240, 128, 128)

# Фиолетовые и пурпурные оттенки
COLOR_INDIGO: Final[Color] = Color(75, 0, 130)
COLOR_DARK_VIOLET: Final[Color] = Color(148, 0, 211)
COLOR_ORCHID: Final[Color] = Color(218, 112, 214)
COLOR_PLUM: Final[Color] = Color(221, 160, 221)
COLOR_THISTLE: Final[Color] = Color(216, 191, 216)

# Коричневые и земляные тона
COLOR_SIENNA: Final[Color] = Color(160, 82, 45)
COLOR_CHOCOLATE: Final[Color] = Color(210, 105, 30)
COLOR_SANDY_BROWN: Final[Color] = Color(244, 164, 96)
COLOR_BURLYWOOD: Final[Color] = Color(222, 184, 135)
COLOR_TAN: Final[Color] = Color(210, 180, 140)
COLOR_BEIGE: Final[Color] = Color(245, 245, 220)

# Специальные цвета
COLOR_TEAL: Final[Color] = Color(0, 128, 128)
COLOR_AQUA: Final[Color] = Color(0, 255, 255)
COLOR_TURQUOISE: Final[Color] = Color(64, 224, 208)
COLOR_LAVENDER: Final[Color] = Color(230, 230, 250)
COLOR_MINT: Final[Color] = Color(189, 252, 201)
COLOR_IVORY: Final[Color] = Color(255, 255, 240)
COLOR_SNOW: Final[Color] = Color(255, 250, 250)
COLOR_HONEYDEW: Final[Color] = Color(240, 255, 240)

# Веб-безопасные цвета
COLOR_WEB_GRAY: Final[Color] = Color(128, 128, 128)
COLOR_WEB_MAROON = Color(128, 0, 0)
COLOR_WEB_OLIVE: Final[Color] = Color(128, 128, 0)
COLOR_WEB_GREEN: Final[Color] = Color(0, 128, 0)
COLOR_WEB_PURPLE: Final[Color] = Color(128, 0, 128)
COLOR_WEB_NAVY: Final[Color] = Color(0, 0, 128)

# Современные UI цвета
COLOR_SLATE: Final[Color] = Color(112, 128, 144)
COLOR_GHOST_WHITE: Final[Color] = Color(248, 248, 255)
COLOR_ALICE_BLUE: Final[Color] = Color(240, 248, 255)
COLOR_AZURE: Final[Color] = Color(240, 255, 255)
COLOR_CORAL: Final[Color] = Color(255, 127, 80)
COLOR_VIOLET_RED: Final[Color] = Color(208, 32, 144)


# /////////////////////////////////////////////////////
# Специальный цвет для прозрачности
COLOR_TRANSPARENT: Final[Color] = Color(0, 0, 0, 0)
# /////////////////////////////////////////////////////

def mix(color_1: Color, color_2: Color, amount: float | int) -> Color:
    """
    #### Смешивает два цвета в заданной пропорции

    ---

    :Args:
    - color_1 - Первый цвет для смешивания
    - color_2 - Второй цвет для смешивания
    - amount - Доля второго цвета (0.0 - color_1, 1.0 - color_2)

    ---

    :Return:
    - Color - Новый цвет, результат смешивания

    ---

    :Raises:
    - ValueError: Если amount вне диапазона [0, 1]

    ---

    :Example:
    ```python
    red = Color(255, 0, 0)
    blue = Color(0, 0, 255)
    purple = mix(red, blue, 0.5)  # Смешанный цвет
    ```
    """
    if not 0 <= amount <= 1:
        raise ValueError("Amount must be between 0 and 1")

    r = int(color_1.r * (1 - amount) + color_2.r * amount)
    g = int(color_1.g * (1 - amount) + color_2.g * amount)
    b = int(color_1.b * (1 - amount) + color_2.b * amount)
    return Color(r, g, b)


def middle(color_1: Color, color_2: Color) -> Color:
    """
    #### Находит средний цвет между двумя цветами

    ---

    :Args:
    - color_1 - Первый цвет
    - color_2 - Второй цвет

    ---

    :Return:
    - Color - Цвет, находящийся посередине между color_1 и color_2

    ---

    :Example:
    ```python
    black = Color(0, 0, 0)
    white = Color(255, 255, 255)
    gray = middle(black, white)  # Color(127, 127, 127)
    ```
    """
    return mix(color_1, color_2, 0.5)

@final
class BaseColorGradient:
    __slots__ = ('__color_1', '__color_2')

    def __init__(self, color_1: Color, color_2: Color):
        """
        #### Создает базовый градиент между двумя цветами

        ---

        :Args:
        - color_1 - Начальный цвет градиента
        - color_2 - Конечный цвет градиента

        ---

        :Example:
        ```python
        gradient = BaseColorGradient(COLOR_RED, COLOR_BLUE)
        ```
        """
        self.__color_1 = color_1
        self.__color_2 = color_2

    def get(self, amount: float | int) -> Color:
        """
        #### Возвращает промежуточный цвет градиента

        ---

        :Args:
        - amount - Позиция в градиенте (0.0 - начальный цвет, 1.0 - конечный цвет)

        ---

        :Return:
        - Color - Промежуточный цвет

        ---

        :Raises:
        - ValueError: Если amount вне диапазона [0, 1]

        ---

        :Example:
        ```python
        color = gradient.get(0.5)  # Цвет посередине градиента
        ```
        """
        if not 0 <= amount <= 1:
            raise ValueError("Amount must be between 0 and 1")
        return mix(self.__color_1, self.__color_2, amount)

    def get_color_1(self) -> Color:
        """
        #### Возвращает начальный цвет градиента

        ---

        :Return:
        - Color - Первый цвет градиента

        ---

        :Example:
        ```python
        start_color = gradient.get_color_1()
        ```
        """
        return self.__color_1

    def get_color_2(self) -> Color:
        """
        #### Возвращает конечный цвет градиента

        ---

        :Return:
        - Color - Второй цвет градиента

        ---

        :Example:
        ```python
        end_color = gradient.get_color_2()
        ```
        """
        return self.__color_2

    def set_color_1(self, color: Color) -> "BaseColorGradient":
        """
        #### Устанавливает начальный цвет градиента

        ---

        :Args:
        - color - Новый начальный цвет

        ---

        :Return:
        - BaseColorGradient - Текущий объект (для цепочки вызовов)

        ---

        :Example:
        ```python
        gradient.set_color_1(COLOR_GREEN)
        ```
        """
        self.__color_1 = color
        return self

    def set_color_2(self, color: Color) -> "BaseColorGradient":
        """
        #### Устанавливает конечный цвет градиента

        ---

        :Args:
        - color - Новый конечный цвет

        ---

        :Return:
        - BaseColorGradient - Текущий объект (для цепочки вызовов)

        ---

        :Example:
        ```python
        gradient.set_color_2(COLOR_YELLOW)
        ```
        """
        self.__color_2 = color
        return self

# Тип для представления массива градиентов из двух цветов ========================== +
type BaseGradientsArrayType = list[BaseColorGradient] | tuple[BaseColorGradient, ...]
# ================================================================================== +

@final
class ColorGradient:
    __slots__ = ('__colors', '__gradients')

    def __init__(self, colors: ColorArrayType):
        """
        #### Создает многоцветный градиент из списка цветов

        ---

        :Args:
        - colors - Список цветов для создания градиента (минимум 2 цвета)

        ---

        :Raises:
        - ValueError: Если передано меньше 2 цветов

        ---

        :Example:
        ```python
        gradient = ColorGradient([Color.RED, Color.GREEN, Color.BLUE])
        ```
        """
        if len(colors) < 2:
            raise ValueError("At least 2 colors are required to create a gradient")

        self.__colors = list(colors)
        self.__gradients = []
        for i in range(len(colors) - 1):
            self.__gradients.append(BaseColorGradient(colors[i], colors[i + 1]))

    def get_colors(self) -> ColorArrayType:
        """
        #### Возвращает список всех цветов градиента

        ---

        :Return:
        - list[Color] - Список цветов в градиенте

        ---

        :Example:
        ```python
        colors = gradient.get_colors()
        ```
        """
        return self.__colors

    def get_gradients(self) -> BaseGradientsArrayType:
        """
        #### Возвращает список базовых градиентов между цветами

        ---

        :Return:
        - list[BaseColorGradient] - Список промежуточных градиентов

        ---

        :Example:
        ```python
        base_gradients = gradient.get_gradients()
        ```
        """
        return self.__gradients

    def get(self, amount: float | int) -> Color:
        """
        #### Возвращает цвет в указанной позиции градиента

        ---

        :Args:
        - amount - Позиция в градиенте (0.0 - начало, 1.0 - конец)

        ---

        :Return:
        - Color - Цвет в указанной позиции

        ---

        :Example:
        ```python
        # Получить цвет в середине градиента
        mid_color = gradient.get(0.5)
        ```
        """
        if amount <= 0:
            return self.__colors[0]
        elif amount >= 1:
            return self.__colors[-1]

        index = int(amount * len(self.__gradients))
        relative_pos = amount * len(self.__gradients) - index
        return self.__gradients[index].get(relative_pos)

    def to_list_rgba(self) -> RGBAColorsArrayType:
        """
        #### Возвращает цвета в формате RGBA

        ---

        :Return:
        - list[tuple] - Список кортежей (r, g, b, a)

        ---

        :Example:
        ```python
        rgba_values = gradient.to_list_rgba()
        ```
        """
        return [color.rgba for color in self.__colors]

    def to_list_rgb(self) -> RGBColorsArrayType:
        """
        #### Возвращает цвета в формате RGB

        ---

        :Return:
        - list[tuple] - Список кортежей (r, g, b)

        ---

        :Example:
        ```python
        rgb_values = gradient.to_list_rgb()
        ```
        """
        return [color.rgb for color in self.__colors]

    def reverse(self) -> Self:
        """
        #### Обращает порядок цветов в градиенте

        ---

        :Return:
        - ColorGradient - Текущий объект (для цепочки вызовов)

        ---

        :Example:
        ```python
        gradient.reverse()  # Изменяет порядок цветов на обратный
        ```
        """
        self.__colors.reverse()
        self.__gradients = []

        for i in range(len(self.__colors) - 1):
            self.__gradients.append(BaseColorGradient(self.__colors[i], self.__colors[i + 1]))

        return self

    def add_color(self, color: Color) -> Self:
        """
        #### Добавляет цвет в конец градиента

        ---

        :Args:
        - color - Цвет для добавления

        ---

        :Return:
        - ColorGradient - Текущий объект (для цепочки вызовов)

        ---

        :Example:
        ```python
        gradient.add_color(Color.PURPLE)
        ```
        """
        self.__colors.append(color)
        self.__rebuild_gradients()
        return self

    def insert_color(self, index: int, color: Color) -> Self:
        """
        #### Вставляет цвет в указанную позицию градиента

        ---

        :Args:
        - index - Позиция для вставки
        - color - Цвет для вставки

        ---

        :Return:
        - ColorGradient - Текущий объект (для цепочки вызовов)

        ---

        :Raises:
        - IndexError: Если индекс вне допустимого диапазона

        ---

        :Example:
        ```python
        gradient.insert_color(1, Color.YELLOW)  # Вставляет желтый цвет на вторую позицию
        ```
        """
        self.__colors.insert(index, color)
        self.__rebuild_gradients()
        return self

    def remove_color(self, index: int) -> Self:
        """
        #### Удаляет цвет из градиента по индексу

        ---

        :Args:
        - index - Индекс цвета для удаления

        ---

        :Return:
        - ColorGradient - Текущий объект (для цепочки вызовов)

        ---

        :Raises:
        - IndexError: Если индекс вне допустимого диапазона
        - ValueError: Если после удаления останется меньше 2 цветов

        ---

        :Example:
        ```python
        gradient.remove_color(0)  # Удаляет первый цвет
        ```
        """
        if len(self.__colors) <= 2:
            raise ValueError("Gradient must contain at least 2 colors")

        self.__colors.pop(index)
        self.__rebuild_gradients()
        return self

    def __rebuild_gradients(self):
        """Внутренний метод для перестроения градиентов"""
        self.__gradients = []
        for i in range(len(self.__colors) - 1):
            self.__gradients.append(BaseColorGradient(self.__colors[i], self.__colors[i + 1]))

@final
class ColorGradientEx:
    __slots__ = ('__colors', '__lengths', '__gradients')

    @classmethod
    def rainbow_gradient(cls) -> "ColorGradientEx":
        """
        #### Создает плавный радужный градиент с 13 цветами

        ---

        :Return:
        - ColorGradientEx - Градиент, содержащий все цвета радуги

        ---

        :Example:
        ```python
        rainbow = ColorGradientEx.rainbow_gradient()
        ```
        """
        colors = [
            Color(255, 0, 0),      # Красный
            Color(255, 100, 0),    # Красно-оранжевый
            Color(255, 165, 0),    # Оранжевый
            Color(255, 200, 0),    # Желто-оранжевый
            Color(255, 255, 0),    # Желтый
            Color(180, 255, 0),    # Желто-зеленый
            Color(0, 255, 0),      # Зеленый
            Color(0, 255, 150),    # Зелено-голубой
            Color(0, 255, 255),    # Голубой
            Color(0, 100, 255),    # Сине-голубой
            Color(0, 0, 255),      # Синий
            Color(70, 0, 255),     # Сине-фиолетовый
            Color(128, 0, 128)     # Фиолетовый
        ]
        return cls.from_colors(colors)

    @classmethod
    def from_integers(cls, colors: list[Color], lengths: list[int | float]) -> "ColorGradientEx":
        """
        #### Создает градиент из цветов с длинами участков, заданных в виде целых чисел

        ---

        :Args:
        - colors - Список целочисленных значений цветов
        - lengths - Список длин участков между цветами

        ---

        :Return:
        - ColorGradientEx - Новый экземпляр градиента

        ---

        :Raises:
        - ValueError: Если количество длин не соответствует количеству цветов

        ---

        :Example:
        ```python
        gradient = ColorGradientEx.from_integers(
            [COLOR_RED, COLOR_GREEN, COLOR_BLACK],
            [200, 100]
        )
        ```
        """
        if len(colors) != len(lengths) + 1:
            raise ValueError("Lengths count must be exactly one less than colors count")

        total_length = sum(lengths)
        normalized_lengths = [l/total_length for l in lengths]
        return cls(colors, normalized_lengths)

    @classmethod
    def from_colors(cls, colors: list[Color]) -> "ColorGradientEx":
        """
        #### Создает градиент с равномерным распределением цветов

        ---

        :Args:
        - colors - Список цветов Color

        ---

        :Return:
        - ColorGradientEx - Градиент с равными промежутками между цветами

        ---

        :Example:
        ```python
        gradient = ColorGradientEx.from_colors([Color.RED, Color.GREEN, Color.BLUE])
        ```
        """
        if len(colors) < 2:
            raise ValueError("At least 2 colors are required")

        lengths = [1.0 / (len(colors) - 1) for _ in range(len(colors) - 1)]
        return cls(colors, lengths)

    def __init__(self, colors: list[Color], lengths: list[float]):
        """
        #### Инициализирует расширенный градиент с настраиваемыми длинами участков

        ---

        :Args:
        - colors - Список цветов (минимум 2)
        - lengths - Список длин участков между цветами

        ---

        :Raises:
        - ValueError: Если нарушены условия:
          - Количество длин ≠ количество цветов - 1
          - Сумма длин ≠ 1
          - Меньше 2 цветов

        ---

        :Example:
        ```python
        gradient = ColorGradientEx(
            [Color.RED, Color.GREEN, Color.BLUE],
            [0.3, 0.7]
        )
        ```
        """
        if len(colors) != len(lengths) + 1:
            raise ValueError("Colors count must be exactly one more than lengths count")
        if not math.isclose(sum(lengths), 1.0, rel_tol=1e-9):
            raise ValueError("Sum of lengths must equal 1.0")
        if len(colors) < 2:
            raise ValueError("At least 2 colors are required")

        self.__colors = colors.copy()
        self.__lengths = lengths.copy()
        self.__rebuild_gradients()

    def __rebuild_gradients(self) -> None:
        """Внутренний метод для перестроения градиентов"""
        self.__gradients = []
        start = 0.0
        for i in range(len(self.__colors) - 1):
            end = start + self.__lengths[i]
            self.__gradients.append((
                BaseColorGradient(self.__colors[i], self.__colors[i + 1]),
                start,
                end
            ))
            start = end

    def get_colors(self) -> ColorArrayType:
        """
        #### Возвращает копию списка цветов градиента

        ---

        :Return:
        - list[Color] - Копия списка цветов

        ---

        :Example:
        ```python
        colors = gradient.get_colors()
        ```
        """
        return self.__colors.copy()

    def get_gradients(self) -> BaseGradientsArrayType:
        """
        #### Возвращает базовые градиенты между цветами

        ---

        :Return:
        - list[BaseColorGradient] - Список градиентов между соседними цветами

        ---

        :Example:
        ```python
        base_gradients = gradient.get_gradients()
        ```
        """
        return [gradient[0] for gradient in self.__gradients]

    def get(self, amount: float | int) -> Color:
        """
        #### Возвращает цвет в указанной позиции градиента

        ---

        :Args:
        - amount - Позиция в градиенте (0.0-1.0)

        ---

        :Return:
        - Color - Цвет в заданной позиции

        ---

        :Example:
        ```python
        color = gradient.get(0.75)  # Цвет на 75% длины градиента
        ```
        """
        if amount <= 0.0:
            return self.__colors[0]
        if amount >= 1.0:
            return self.__colors[-1]

        for gradient, start, end in self.__gradients:
            if start <= amount <= end:
                relative = (amount - start) / (end - start)
                return gradient.get(relative)

        return self.__colors[-1]

    def to_list_rgba(self) -> RGBAColorsArrayType:
        """
        #### Возвращает цвета в формате RGBA

        ---

        :Return:
        - list[tuple] - Список кортежей (r, g, b, a)

        ---

        :Example:
        ```python
        rgba_colors = gradient.to_list_rgba()
        ```
        """
        return [color.rgba for color in self.__colors]

    def to_list_rgb(self) -> RGBColorsArrayType:
        """
        #### Возвращает цвета в формате RGB

        ---

        :Return:
        - list[tuple] - Список кортежей (r, g, b)

        ---

        :Example:
        ```python
        rgb_colors = gradient.to_list_rgb()
        ```
        """
        return [color.rgb for color in self.__colors]

    def reverse(self) -> Self:
        """
        #### Обращает порядок цветов и длин участков

        ---

        :Return:
        - ColorGradientEx - Текущий объект (для цепочки вызовов)

        ---

        :Example:
        ```python
        gradient.reverse()  # Инвертирует градиент
        ```
        """
        self.__colors.reverse()
        self.__lengths.reverse()
        self.__rebuild_gradients()
        return self

    def add_color(self, color: Color, length: float) -> Self:
        """
        #### Добавляет цвет в конец градиента

        ---

        :Args:
        - color - Цвет для добавления
        - length - Длина нового участка

        ---

        :Return:
        - ColorGradientEx - Текущий объект (для цепочки вызовов)

        ---

        :Raises:
        - ValueError: Если длина не в диапазоне (0,1)
        - ValueError: Если сумма длин превысит 1

        ---

        :Example:
        ```python
        gradient.add_color(Color.PURPLE, 0.2)
        ```
        """
        if not 0 < length < 1:
            raise ValueError("Length must be between 0 and 1")
        if sum(self.__lengths) + length > 1:
            raise ValueError("Total length would exceed 1.0")

        self.__colors.append(color)
        self.__lengths.append(length)
        self.__rebuild_gradients()
        return self

    def insert_color(self, index: int, color: Color, length: float) -> Self:
        """
        #### Вставляет цвет в указанную позицию

        ---

        :Args:
        - index - Позиция для вставки
        - color - Цвет для вставки
        - length - Длина нового участка

        ---

        :Return:
        - ColorGradientEx - Текущий объект (для цепочки вызовов)

        ---

        :Raises:
        - IndexError: При недопустимом индексе
        - ValueError: При недопустимой длине

        ---

        :Example:
        ```python
        gradient.insert_color(1, Color.YELLOW, 0.15)
        ```
        """
        if not 0 < length < 1:
            raise ValueError("Length must be between 0 and 1")
        if sum(self.__lengths) + length > 1:
            raise ValueError("Total length would exceed 1.0")

        self.__colors.insert(index, color)
        self.__lengths.insert(index, length)
        self.__rebuild_gradients()
        return self

    def remove_color(self, index: int) -> Self:
        """
        #### Удаляет цвет по указанному индексу

        ---

        :Args:
        - index - Индекс цвета для удаления

        ---

        :Return:
        - ColorGradientEx - Текущий объект (для цепочки вызовов)

        ---

        :Raises:
        - IndexError: При недопустимом индексе
        - ValueError: Если останется меньше 2 цветов

        ---

        :Example:
        ```python
        gradient.remove_color(0)  # Удаляет первый цвет
        ```
        """
        if len(self.__colors) <= 2:
            raise ValueError("Cannot remove color - gradient must have at least 2 colors")
        if index >= len(self.__colors):
            raise IndexError("Index out of range")

        self.__colors.pop(index)
        length_index = index if index < len(self.__lengths) else len(self.__lengths) - 1
        self.__lengths.pop(length_index)
        self.__rebuild_gradients()
        return self

    def get_lengths(self) -> list[float]:
        """
        #### Возвращает длины участков градиента

        ---

        :Return:
        - list[float] - Список длин участков

        ---

        :Example:
        ```python
        lengths = gradient.get_lengths()
        ```
        """
        return self.__lengths.copy()

# ///////////////////////////////////////////////////////////////////////////////
# Константа для радужного градиента
RAINBOW_GRADIENT: Final[ColorGradientEx] = ColorGradientEx.rainbow_gradient()
# ///////////////////////////////////////////////////////////////////////////////

def get_rainbow_with_time(time: float | int) -> Color:
    """
    #### Возвращает цвет радуги, зависящий от времени

    ---

    :Args:
    - time - Временная координата

    ---

    :Return:
    - Color - Цвет из радужного градиента

    ---

    :Example:
    ```python
    # Для анимации можно использовать:
    color = get_rainbow_with_time(time.time())
    ```
    """
    return RAINBOW_GRADIENT.get(abs(math.cos(time)))

def random_color_with_alpha(alpha: int) -> Color:
    """
    #### Возвращае случайный цвет с указаным альфа каналом

    ---

    :Args:
    - alpha - значение альфа канала

    ---

    :Returns:
    - Color - случайный цвет
    """

    if alpha < 0 or alpha > 255:
        raise ValueError("Alpha must be between 0 and 255")

    return Color.random().set_alpha(alpha)
