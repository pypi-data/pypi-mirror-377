import ctypes
from typing import Self
from .Shaders import *
import os

from Moon.python.utils import find_library, LibraryLoadError

# Загружаем DLL библиотеку
try:
    LIB_MOON = ctypes.CDLL(find_library())
except Exception as e:
    raise ImportError(f"Failed to load PySGL library: {e}")

LIB_MOON._BlendMode_CreateFull.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON._BlendMode_CreateFull.restype = ctypes.c_void_p
LIB_MOON._BlendMode_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._BlendMode_Delete.restype = None

class BlendMode:
    """
    #### Класс для управления режимами смешивания пикселей
    
    ---
    
    :Description:
    - Определяет как новые пиксели смешиваются с существующими на экране
    - Позволяет создавать различные визуальные эффекты
    - Поддерживает раздельное управление цветом и альфа-каналом
    
    ---
    
    :Features:
    - Готовые пресеты для популярных эффектов
    - Полная настройка факторов и уравнений смешивания
    - Оптимизированная работа с GPU
    """

    class Factor():
        """
        #### Факторы смешивания для BlendMode
        
        ---
        
        :Description:
        - Определяют как исходный (src) и целевой (dst) цвета влияют на результат
        - Используются в уравнениях смешивания для вычисления финального цвета
        """
        Zero = 0             # (0, 0, 0, 0) - Полностью игнорировать компонент
        One = 1              # (1, 1, 1, 1) - Использовать компонент полностью
        SrcColor = 2         # (src.r, src.g, src.b, src.a) - Цвет источника
        OneMinusSrcColor = 3 # (1, 1, 1, 1) - (src.r, src.g, src.b, src.a) - Инверсия цвета источника
        DstColor = 4         # (dst.r, dst.g, dst.b, dst.a) - Цвет назначения
        OneMinusDstColor = 5 # (1, 1, 1, 1) - (dst.r, dst.g, dst.b, dst.a) - Инверсия цвета назначения
        SrcAlpha = 6         # (src.a, src.a, src.a, src.a) - Альфа источника
        OneMinusSrcAlpha = 7 # (1, 1, 1, 1) - (src.a, src.a, src.a, src.a) - Инверсия альфы источника
        DstAlpha = 8         # (dst.a, dst.a, dst.a, dst.a) - Альфа назначения
        OneMinusDstAlpha = 9  # (1, 1, 1, 1) - (dst.a, dst.a, dst.a, dst.a) - Инверсия альфы назначения
        
    class Equation():
        """
        #### Уравнения смешивания для BlendMode
        
        ---
        
        :Description:
        - Определяют математическую операцию между исходным и целевым цветами
        - Применяются после умножения на соответствующие факторы
        """
        Add = 0             # Pixel = Src * SrcFactor + Dst * DstFactor - Сложение (стандартное смешивание)
        Subtract = 1        # Pixel = Src * SrcFactor - Dst * DstFactor - Вычитание источника из назначения
        ReverseSubtract = 2 # Pixel = Dst * DstFactor - Src * SrcFactor - Вычитание назначения из источника
        Min = 3             # Pixel = min(Dst, Src) - Минимальное значение
        Max = 4             # Pixel = max(Dst, Src) - Максимальное значение

    def __init__(self, color_src_factor: Factor, color_dst_factor: Factor, color_eq: Equation,
                       alpha_src_factor: Factor, alpha_dst_factor: Factor, alpha_eq: Equation):
        """
        #### Создание пользовательского режима смешивания
        
        ---
        
        :Args:
        - color_src_factor: Фактор для исходного цвета
        - color_dst_factor: Фактор для целевого цвета
        - color_eq: Уравнение смешивания цветов
        - alpha_src_factor: Фактор для исходной альфы
        - alpha_dst_factor: Фактор для целевой альфы
        - alpha_eq: Уравнение смешивания альфы
        """
        self.__color_src_factor = color_src_factor
        self.__color_dst_factor = color_dst_factor
        self.__color_eq = color_eq

        self.__alpha_src_factor = alpha_src_factor
        self.__alpha_dst_factor = alpha_dst_factor
        self.__alpha_eq = alpha_eq

        self.__blend_mode_ptr = LIB_MOON._BlendMode_CreateFull(self.__color_src_factor, self.__color_dst_factor, self.__color_eq,
                                                                self.__alpha_src_factor, self.__alpha_dst_factor, self.__alpha_eq)

    def  __del__(self) -> None:
        LIB_MOON._BlendMode_Delete(self.__blend_mode_ptr)

    def get_ptr(self) -> ctypes.c_void_p:
        return self.__blend_mode_ptr
    
    # ================================================================================
    #                           ГОТОВЫЕ ПРЕСЕТЫ BLEND РЕЖИМОВ
    # ================================================================================
    
    @staticmethod
    def Alpha() -> "BlendMode":
        """
        #### Стандартное альфа-смешивание (прозрачность)
        
        ---
        
        :Description:
        - Самый распространенный режим смешивания
        - Новые пиксели смешиваются с существующими на основе альфа-канала
        - Полупрозрачные объекты корректно накладываются друг на друга
        
        ---
        
        :Formula:
        - Color: Src * SrcAlpha + Dst * (1 - SrcAlpha)
        - Alpha: SrcAlpha + DstAlpha * (1 - SrcAlpha)
        
        ---
        
        :Use Cases:
        - Обычная отрисовка спрайтов с прозрачностью
        - UI элементы с полупрозрачным фоном
        - Частицы и эффекты с плавным затуханием
        
        ---
        
        :Example:
        ```python
        states = RenderStates().set_blend_mode(BlendMode.Alpha())
        window.draw(sprite, states)
        ```
        """
        return BlendMode(
            BlendMode.Factor.SrcAlpha, BlendMode.Factor.OneMinusSrcAlpha, BlendMode.Equation.Add,
            BlendMode.Factor.One, BlendMode.Factor.OneMinusSrcAlpha, BlendMode.Equation.Add
        )
    
    @staticmethod
    def Add() -> "BlendMode":
        """
        #### Аддитивное смешивание (сложение цветов)
        
        ---
        
        :Description:
        - Цвета складываются, создавая эффект свечения
        - Темные области остаются темными, светлые становятся ярче
        - Результат никогда не темнее исходного изображения
        
        ---
        
        :Formula:
        - Color: Src + Dst
        - Alpha: SrcAlpha + DstAlpha
        
        ---
        
        :Use Cases:
        - Эффекты огня, взрывов, магии
        - Световые лучи и блики
        - Неоновые эффекты и голограммы
        - Частицы искр и звезд
        
        ---
        
        :Example:
        ```python
        # Эффект огня
        fire_states = RenderStates().set_blend_mode(BlendMode.Add())
        window.draw(fire_particle, fire_states)
        ```
        """
        return BlendMode(
            BlendMode.Factor.SrcAlpha, BlendMode.Factor.One, BlendMode.Equation.Add,
            BlendMode.Factor.One, BlendMode.Factor.One, BlendMode.Equation.Add
        )
    
    @staticmethod
    def Multiply() -> "BlendMode":
        """
        #### Мультипликативное смешивание (умножение цветов)
        
        ---
        
        :Description:
        - Цвета перемножаются, создавая эффект затемнения
        - Светлые области становятся темнее, белый остается белым
        - Результат никогда не светлее исходного изображения
        
        ---
        
        :Formula:
        - Color: Src * Dst
        - Alpha: SrcAlpha * DstAlpha
        
        ---
        
        :Use Cases:
        - Эффекты теней и затемнения
        - Наложение текстур освещения
        - Создание силуэтов
        - Эффекты дыма и тумана
        
        ---
        
        :Example:
        ```python
        # Эффект тени
        shadow_states = RenderStates().set_blend_mode(BlendMode.Multiply())
        window.draw(shadow_sprite, shadow_states)
        ```
        """
        return BlendMode(
            BlendMode.Factor.DstColor, BlendMode.Factor.Zero, BlendMode.Equation.Add,
            BlendMode.Factor.DstAlpha, BlendMode.Factor.Zero, BlendMode.Equation.Add
        )
    
    @staticmethod
    def Default() -> "BlendMode":
        """
        #### Отсутствие смешивания (замещение)
        
        ---
        
        :Description:
        - Новые пиксели полностью заменяют существующие
        - Альфа-канал игнорируется
        - Самый быстрый режим рендеринга
        
        ---
        
        :Formula:
        - Color: Src
        - Alpha: SrcAlpha
        
        ---
        
        :Use Cases:
        - Отрисовка непрозрачных объектов
        - Фоновые изображения
        - Оптимизация производительности
        - Отладка рендеринга
        
        ---
        
        :Example:
        ```python
        # Быстрая отрисовка фона
        bg_states = RenderStates().set_blend_mode(BlendMode.None_())
        window.draw(background, bg_states)
        ```
        """
        return BlendMode(
            BlendMode.Factor.One, BlendMode.Factor.Zero, BlendMode.Equation.Add,
            BlendMode.Factor.One, BlendMode.Factor.Zero, BlendMode.Equation.Add
        )
    
    @staticmethod
    def Subtract() -> "BlendMode":
        """
        #### Субтрактивное смешивание (вычитание цветов)
        
        ---
        
        :Description:
        - Цвета вычитаются из существующих пикселей
        - Создает эффект "выжигания" или инверсии
        - Может создавать интересные художественные эффекты
        
        ---
        
        :Formula:
        - Color: Dst - Src
        - Alpha: DstAlpha - SrcAlpha
        
        ---
        
        :Use Cases:
        - Эффекты разрушения и коррозии
        - Художественные фильтры
        - Эффекты "выжигания" лазером
        - Создание масок и вырезов
        
        ---
        
        :Example:
        ```python
        # Эффект лазерного выжигания
        laser_states = RenderStates().set_blend_mode(BlendMode.Subtract())
        window.draw(laser_beam, laser_states)
        ```
        """
        return BlendMode(
            BlendMode.Factor.SrcAlpha, BlendMode.Factor.One, BlendMode.Equation.ReverseSubtract,
            BlendMode.Factor.One, BlendMode.Factor.One, BlendMode.Equation.ReverseSubtract
        )
    
    @staticmethod
    def Screen() -> "BlendMode":
        """
        #### Экранное смешивание (осветление)
        
        ---
        
        :Description:
        - Инверсия мультипликативного смешивания
        - Осветляет изображение, сохраняя детали
        - Противоположность режиму Multiply
        
        ---
        
        :Formula:
        - Color: 1 - (1 - Src) * (1 - Dst)
        - Эквивалентно: Src + Dst - Src * Dst
        
        ---
        
        :Use Cases:
        - Эффекты освещения и бликов
        - Осветление темных областей
        - Имитация передержки фотографии
        - Мягкие световые эффекты
        
        ---
        
        :Example:
        ```python
        # Мягкое освещение
        light_states = RenderStates().set_blend_mode(BlendMode.Screen())
        window.draw(light_source, light_states)
        ```
        """
        return BlendMode(
            BlendMode.Factor.OneMinusDstColor, BlendMode.Factor.One, BlendMode.Equation.Add,
            BlendMode.Factor.OneMinusDstAlpha, BlendMode.Factor.One, BlendMode.Equation.Add
        )
    
    @staticmethod
    def Lighten() -> "BlendMode":
        """
        #### Осветление (максимум цветов)
        
        ---
        
        :Description:
        - Выбирает более светлый цвет из источника и назначения
        - Сохраняет яркие детали обоих изображений
        - Никогда не затемняет изображение
        
        ---
        
        :Formula:
        - Color: max(Src, Dst)
        - Alpha: max(SrcAlpha, DstAlpha)
        
        ---
        
        :Use Cases:
        - Наложение световых эффектов
        - Сохранение ярких деталей
        - Эффекты молний и электричества
        - Комбинирование изображений
        
        ---
        
        :Example:
        ```python
        # Эффект молнии
        lightning_states = RenderStates().set_blend_mode(BlendMode.Lighten())
        window.draw(lightning, lightning_states)
        ```
        """
        return BlendMode(
            BlendMode.Factor.One, BlendMode.Factor.One, BlendMode.Equation.Max,
            BlendMode.Factor.One, BlendMode.Factor.One, BlendMode.Equation.Max
        )
    
    @staticmethod
    def Darken() -> "BlendMode":
        """
        #### Затемнение (минимум цветов)
        
        ---
        
        :Description:
        - Выбирает более темный цвет из источника и назначения
        - Сохраняет темные детали обоих изображений
        - Никогда не осветляет изображение
        
        ---
        
        :Formula:
        - Color: min(Src, Dst)
        - Alpha: min(SrcAlpha, DstAlpha)
        
        ---
        
        :Use Cases:
        - Эффекты теней и затемнения
        - Сохранение темных деталей
        - Создание силуэтов
        - Эффекты поглощения света
        
        ---
        
        :Example:
        ```python
        # Эффект поглощающей тени
        shadow_states = RenderStates().set_blend_mode(BlendMode.Darken())
        window.draw(dark_effect, shadow_states)
        ```
        """
        return BlendMode(
            BlendMode.Factor.One, BlendMode.Factor.One, BlendMode.Equation.Min,
            BlendMode.Factor.One, BlendMode.Factor.One, BlendMode.Equation.Min
        )



LIB_MOON._RenderStates_Create.argtypes = None
LIB_MOON._RenderStates_Create.restype = ctypes.c_void_p
LIB_MOON._RenderStates_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._RenderStates_Delete.restype = None
LIB_MOON._RenderStates_SetShader.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._RenderStates_SetShader.restype = None
LIB_MOON._RenderStates_SetBlendMode.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._RenderStates_SetBlendMode.restype = None
LIB_MOON._RenderStates_SetTexture.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._RenderStates_SetTexture.restype = None

RenderStatesPtr = ctypes.c_void_p


class RenderStates:

    """
    #### Состояния рендеринга для управления отрисовкой объектов
    
    ---
    
    :Description:
    - Управляет параметрами рендеринга: шейдеры, текстуры, режимы смешивания
    - Позволяет настраивать визуальные эффекты для отрисовки
    - Поддерживает цепочку вызовов методов
    
    ---
    
    :Example:
    ```python
    # Создание состояний с аддитивным смешиванием
    states = RenderStates().set_blend_mode(BlendMode.Add()).set_texture(my_texture)
    window.draw(sprite, states)
    ```
    """
    
    def __init__(self):
        """
        #### Создает новые состояния рендеринга с настройками по умолчанию
        """
        self._ptr = LIB_MOON._RenderStates_Create()
        self.__shader: Shader | None = None
        self.__blend_mode = None
        self.__texture = None

    def get_ptr(self) -> RenderStatesPtr:
        """
        #### Возвращает указатель на внутренний объект C++
        
        :Returns:
        - RenderStatesPtr: Указатель для внутреннего использования
        """
        return self._ptr
    
    def set_shader(self, shader: Shader) -> Self:
        """
        #### Устанавливает шейдер для рендеринга
        
        :Args:
        - shader (Shader): Шейдерная программа для применения эффектов
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        """
        self.__shader = shader
        LIB_MOON._RenderStates_SetShader(self._ptr, self.__shader.get_ptr())
        return self
    
    def set_texture(self, texture) -> Self:
        """
        #### Устанавливает текстуру для рендеринга
        
        :Args:
        - texture (Texture): Текстура для наложения на объекты
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        """
        LIB_MOON._RenderStates_SetTexture(self._ptr, texture.get_ptr())
        return self
    
    def get_texture(self):
        """
        #### Возвращает текущую установленную текстуру
        
        :Returns:
        - Texture | None: Текущая текстура или None если не установлена
        """
        return self.__texture

    def set_blend_mode(self, blend_mode: BlendMode) -> Self:
        """
        #### Устанавливает режим смешивания для рендеринга
        
        ---
        
        :Args:
        - blend_mode (BlendMode): Режим смешивания пикселей
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Использование готового пресета
        states = RenderStates().set_blend_mode(BlendMode.Add())
        
        # Создание пользовательского режима
        custom_blend = BlendMode(
            BlendMode.Factor.SrcAlpha, BlendMode.Factor.One, BlendMode.Equation.Add,
            BlendMode.Factor.One, BlendMode.Factor.Zero, BlendMode.Equation.Add
        )
        states = RenderStates().set_blend_mode(custom_blend)
        ```
        """
        self.__blend_mode = blend_mode
        LIB_MOON._RenderStates_SetBlendMode(self._ptr, self.__blend_mode.get_ptr())
        return self

    def get_blend_mode(self) -> BlendMode:
        """
        #### Возвращает текущий режим смешивания
        
        :Returns:
        - BlendMode: Текущий режим смешивания пикселей
        """
        return self.__blend_mode

    def get_shader(self) -> Shader:
        """
        #### Возвращает текущий шейдер
        
        :Returns:
        - Shader: Текущая шейдерная программа
        """
        return self.__shader

    
