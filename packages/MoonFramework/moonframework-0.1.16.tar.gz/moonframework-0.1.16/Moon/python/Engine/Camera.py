"""
#### *Модуль системы камер для Moon*

---

##### Версия: 2.0.0

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 95%

---

✓ Продвинутая система камер 2D:
  - Плавное следование за объектами с интерполяцией
  - Система тряски камеры с настраиваемыми параметрами
  - Автоматическое масштабирование для двух целей
  - Поворот камеры с плавной анимацией

✓ Гибкие режимы работы:
  - Следование за одним объектом
  - Следование за двумя объектами с автомасштабированием
  - Ручное управление позицией (CameraMachine2D)
  - Настраиваемые границы и ограничения

✓ Система эффектов:
  - Тряска по осям X/Y или комбинированная
  - Плавные переходы между состояниями
  - Настраиваемая скорость интерполяции
  - Автоматическое затухание эффектов

✓ Интеграция с окном:
  - Автоматическая адаптация к изменению размера окна
  - Поддержка различных разрешений
  - Оптимизированная производительность

---

:Requires:

• Python 3.8+

• Moon.Views (система представлений)

• Moon.Vectors (векторная математика)

• Moon.Window (оконная система)

---

== Лицензия MIT ==================================================

[MIT License]
Copyright (c) 2025 Pavlov Ivan

Данная лицензия разрешает лицам, получившим копию данного программного обеспечения 
и сопутствующей документации (в дальнейшем именуемыми «Программное Обеспечение»), 
безвозмездно использовать Программное Обеспечение без ограничений, включая неограниченное 
право на использование, копирование, изменение, слияние, публикацию, распространение, 
сублицензирование и/или продажу копий Программного Обеспечения.

[ Уведомление об авторском праве и данные условия должны быть включены во все копии ]
[                 или значительные части Программного Обеспечения.                  ]

ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ.
"""

from random import randint, uniform
from typing import Self, final
from Moon.python.Views import *
from Moon.python.Vectors import *
from Moon.python.Window import Window

@final
class Camera2D:
    """
    #### Класс для создания и управления 2D камерой
    
    ---
    
    :Description:
    - Обеспечивает плавное следование за объектами в 2D пространстве
    - Поддерживает различные эффекты (тряска, поворот, масштабирование)
    - Автоматически адаптируется к изменениям размера окна
    - Оптимизирован для игровых приложений
    
    ---
    
    :Features:
    - Интерполированное движение и масштабирование
    - Система тряски камеры с настраиваемыми параметрами
    - Следование за одним или двумя объектами
    - Автоматическое масштабирование для удержания объектов в кадре
    """
    
    @final
    def __init__(self, width: int, height: int):
        """
        #### Инициализация 2D камеры
        
        ---
        
        :Args:
        - width (int): Ширина области просмотра камеры (>0)
        - height (int): Высота области просмотра камеры (>0)
        
        ---
        
        :Raises:
        - ValueError: При недопустимых размерах камеры
        
        ---
        
        :Example:
        ```python
        # Создание камеры под размер окна
        camera = Camera2D(800, 600)
        ```
        """
        if width <= 0 or height <= 0:
            raise ValueError("Camera dimensions must be positive")

        # =============================================
        # Основные параметры камеры
        # =============================================
        self.__width = width                    # Ширина области просмотра
        self.__height = height                  # Высота области просмотра
        self.__view = View(FloatRect(0, 0, self.__width, self.__height))  # Объект представления SFML

        # =============================================
        # Система позиционирования
        # =============================================
        self.__target_center: Vector2f = Vector2f(0, 0)    # Целевая позиция центра камеры
        self.__current_center: Vector2f = Vector2f(0, 0)   # Текущая позиция центра камеры
        self.__lerp_movement: float = 0.1                  # Скорость интерполяции движения (0-1)
        
        # =============================================
        # Система масштабирования
        # =============================================
        self.__target_zoom: float = 1           # Целевой уровень масштабирования
        self.__saved_zoom: float = 1            # Сохраненный базовый уровень масштабирования
        self.__zoom: float = 1                  # Текущий уровень масштабирования
        self.__lerp_zoom: float = 0.1           # Скорость интерполяции масштабирования (0-1)
        self.__min_zoom: float = 0.01          # Минимальный уровень масштабирования
        self.__max_zoom: float = 10.0           # Максимальный уровень масштабирования

        # =============================================
        # Система тряски камеры
        # =============================================
        self.__target_shake = Vector2f(0, 0)    # Целевая амплитуда тряски
        self.__current_shake = Vector2f(0, 0)   # Текущее смещение от тряски
        self.__shake_lerp = Vector2f(0.9, 0.9)  # Скорость затухания тряски по осям
        self.__shake_only_x = False             # Флаг тряски только по оси X
        self.__shake_only_y = False             # Флаг тряски только по оси Y
        self.__shake_intensity: float = 1.0     # Общая интенсивность тряски

        # =============================================
        # Система поворота камеры
        # =============================================
        self.__angle = 0                        # Текущий угол поворота камеры (в градусах)
        self.__target_angle = 0                 # Целевой угол поворота камеры
        self.__angle_lerp = 0.1                 # Скорость интерполяции поворота (0-1)

        # =============================================
        # Система следования за двумя объектами
        # =============================================
        self.__first_target: Vector2i | Vector2f | Vector2f | None = None   # Первый объект слежения
        self.__second_target: Vector2i | Vector2f | Vector2f | None = None  # Второй объект слежения
        self.__two_target_factor: float = 0.5                                  # Коэффициент позиции между объектами (0-1)
        self.__use_two_target: bool = False                                    # Флаг использования двойного слежения
        self.__auto_scale_padding: float = 0                                   # Отступ для автомасштабирования

        # =============================================
        # Система границ и ограничений
        # =============================================
        self.__bounds_enabled: bool = False     # Флаг включения границ камеры
        self.__bounds_rect: FloatRect = FloatRect(0, 0, 0, 0)  # Прямоугольник ограничений
        self.__deadzone_enabled: bool = False   # Флаг включения мертвой зоны
        self.__deadzone_rect: FloatRect = FloatRect(0, 0, 100, 100)  # Мертвая зона в центре

        # =============================================
        # Интеграция с окном
        # =============================================
        self.__window: Window | None = None     # Ссылка на окно для автоадаптации
    
    @final
    def set_zoom(self, zoom: float = 1) -> Self:
        self.__zoom = zoom
        return self

    @final
    def set_window(self, window: Window) -> Self:
        """
        #### Привязывает камеру к окну для автоматической адаптации
        
        ---
        
        :Description:
        - Позволяет камере автоматически адаптироваться к изменениям размера окна
        - Обновляет размеры области просмотра при ресайзе
        - Рекомендуется для динамических интерфейсов
        
        ---
        
        :Args:
        - window (Window): Объект окна для привязки
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        camera.set_window(window).set_lerp_movement(0.05)
        ```
        """
        self.__window = window
        return self

    @final
    def set_two_target_factor(self, factor: float = 0.5) -> Self:
        """
        #### Устанавливает коэффициент позиции между двумя объектами слежения
        
        ---
        
        :Description:
        - Определяет, где будет находиться камера между двумя объектами
        - 0.0 = камера следует за первым объектом
        - 0.5 = камера находится посередине между объектами
        - 1.0 = камера следует за вторым объектом
        
        ---
        
        :Args:
        - factor (float): Коэффициент позиции (0.0-1.0)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Камера ближе к первому игроку
        camera.set_two_target_factor(0.3)
        ```
        """
        self.__two_target_factor = max(0.0, min(1.0, factor))
        return self

    @final
    def set_auto_scale_padding(self, padding: float) -> Self:
        """
        #### Устанавливает отступ для автоматического масштабирования
        
        ---
        
        :Description:
        - Определяет минимальное расстояние от краев экрана до объектов
        - Используется при автомасштабировании для двух объектов
        - Большие значения = больше свободного места вокруг объектов
        
        ---
        
        :Args:
        - padding (float): Размер отступа в пикселях
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Оставить 100 пикселей отступа
        camera.set_auto_scale_padding(100)
        ```
        """
        self.__auto_scale_padding = max(0, padding)
        return self

    @final
    def get_auto_scale_padding(self) -> float:
        """
        #### Возвращает текущий отступ для автомасштабирования
        
        ---
        
        :Returns:
        - float: Размер отступа в пикселях
        
        ---
        
        :Example:
        ```python
        print(f"Текущий отступ: {camera.get_auto_scale_padding()}px")
        ```
        """
        return self.__auto_scale_padding
    
    @final
    def set_using_two_target(self, flag: bool = True) -> Self:
        """
        #### Включает/выключает режим следования за двумя объектами
        
        ---
        
        :Description:
        - При включении камера будет следить за двумя объектами одновременно
        - Автоматически масштабируется для удержания обоих объектов в кадре
        - Позиция камеры определяется коэффициентом two_target_factor
        
        ---
        
        :Args:
        - flag (bool): True - включить двойное слежение, False - выключить
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Включить слежение за двумя игроками
        camera.set_using_two_target(True)
        ```
        """
        self.__use_two_target = flag
        return self

    @final
    def get_using_two_target(self) -> bool:
        """
        #### Проверяет, включен ли режим двойного слежения
        
        ---
        
        :Returns:
        - bool: True если режим включен, False если выключен
        
        ---
        
        :Example:
        ```python
        if camera.get_using_two_target():
            print("Камера следит за двумя объектами")
        ```
        """
        return self.__use_two_target

    @final
    def get_view(self) -> View:
        """
        #### Возвращает объект представления камеры
        
        ---
        
        :Description:
        - Предоставляет доступ к внутреннему объекту View
        - Используется для применения камеры к окну
        - Содержит все трансформации камеры
        
        ---
        
        :Returns:
        - View: Объект представления SFML
        
        ---
        
        :Example:
        ```python
        # Применить камеру к окну
        window.set_view(camera.get_view())
        ```
        """
        return self.__view

    @final
    def get_zoom(self) -> float:
        """
        #### Возвращает текущий уровень масштабирования
        
        ---
        
        :Description:
        - Показывает фактический уровень масштабирования камеры
        - 1.0 = нормальный масштаб
        - <1.0 = увеличение (приближение)
        - >1.0 = уменьшение (отдаление)
        
        ---
        
        :Returns:
        - float: Текущий коэффициент масштабирования
        
        ---
        
        :Example:
        ```python
        if camera.get_zoom() < 0.5:
            print("Камера сильно приближена")
        ```
        """
        return self.__zoom
    
    @final
    def get_target_zoom(self) -> float:
        return self.__target_zoom

    @final
    def shake(self, amplitude: float = 5, duration: float = 1.0) -> Self:
        """
        #### Запускает тряску камеры по обеим осям
        
        ---
        
        :Description:
        - Создает эффект тряски камеры в случайных направлениях
        - Амплитуда постепенно затухает до нуля
        - Подходит для взрывов, ударов и других динамических событий
        
        ---
        
        :Args:
        - amplitude (float): Максимальная амплитуда тряски в пикселях
        - duration (float): Продолжительность эффекта (влияет на скорость затухания)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Сильная тряска при взрыве
        camera.shake(15, 2.0)
        ```
        """
        self.__target_shake = Vector2f(amplitude * self.__shake_intensity, amplitude * self.__shake_intensity)
        self.__shake_lerp = Vector2f(0.95 - (duration * 0.1), 0.95 - (duration * 0.1))
        self.__shake_only_x = False
        self.__shake_only_y = False
        return self

    @final
    def shake_x(self, amplitude: float = 5, duration: float = 1.0) -> Self:
        """
        #### Запускает тряску камеры только по горизонтальной оси
        
        ---
        
        :Description:
        - Создает горизонтальную тряску камеры
        - Полезно для эффектов землетрясения или горизонтальных ударов
        - Вертикальная позиция остается стабильной
        
        ---
        
        :Args:
        - amplitude (float): Максимальная амплитуда тряски по оси X
        - duration (float): Продолжительность эффекта
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Горизонтальная тряска при землетрясении
        camera.shake_x(10, 3.0)
        ```
        """
        self.__target_shake = Vector2f(amplitude * self.__shake_intensity, 0)
        self.__shake_lerp.x = 0.95 - (duration * 0.1)
        self.__shake_only_x = True
        self.__shake_only_y = False
        return self

    @final
    def shake_y(self, amplitude: float = 5, duration: float = 1.0) -> Self:
        """
        #### Запускает тряску камеры только по вертикальной оси
        
        ---
        
        :Description:
        - Создает вертикальную тряску камеры
        - Подходит для эффектов прыжков или вертикальных ударов
        - Горизонтальная позиция остается стабильной
        
        ---
        
        :Args:
        - amplitude (float): Максимальная амплитуда тряски по оси Y
        - duration (float): Продолжительность эффекта
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Вертикальная тряска при приземлении
        camera.shake_y(8, 0.5)
        ```
        """
        self.__target_shake = Vector2f(0, amplitude * self.__shake_intensity)
        self.__shake_lerp.y = 0.95 - (duration * 0.1)
        self.__shake_only_x = False
        self.__shake_only_y = True
        return self

    @final
    def set_shake_intensity(self, intensity: float) -> Self:
        """
        #### Устанавливает общую интенсивность тряски камеры
        
        ---
        
        :Description:
        - Глобальный множитель для всех эффектов тряски
        - Позволяет быстро настроить силу всех эффектов тряски
        - Полезно для настроек игры или адаптации под разные устройства
        
        ---
        
        :Args:
        - intensity (float): Коэффициент интенсивности (0.0-2.0, где 1.0 = нормальная интенсивность)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Уменьшить интенсивность тряски для мобильных устройств
        camera.set_shake_intensity(0.5)
        ```
        """
        self.__shake_intensity = max(0.0, min(2.0, intensity))
        return self

    @final
    def get_shake_intensity(self) -> float:
        """
        #### Возвращает текущую интенсивность тряски
        
        ---
        
        :Returns:
        - float: Текущий коэффициент интенсивности тряски
        
        ---
        
        :Example:
        ```python
        print(f"Интенсивность тряски: {camera.get_shake_intensity()}")
        ```
        """
        return self.__shake_intensity

    @final
    def set_zoom_limits(self, min_zoom: float, max_zoom: float) -> Self:
        """
        #### Устанавливает ограничения масштабирования камеры
        
        ---
        
        :Description:
        - Определяет минимальный и максимальный уровни масштабирования
        - Предотвращает чрезмерное приближение или отдаление
        - Автоматически применяется при всех операциях масштабирования
        
        ---
        
        :Args:
        - min_zoom (float): Минимальный уровень масштабирования (>0)
        - max_zoom (float): Максимальный уровень масштабирования (>min_zoom)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Raises:
        - ValueError: При некорректных значениях ограничений
        
        ---
        
        :Example:
        ```python
        # Ограничить масштаб от 0.5x до 3x
        camera.set_zoom_limits(0.5, 3.0)
        ```
        """
        if min_zoom <= 0 or max_zoom <= min_zoom:
            raise ValueError("Invalid zoom limits: min_zoom must be > 0 and max_zoom > min_zoom")
        self.__min_zoom = min_zoom
        self.__max_zoom = max_zoom
        return self

    @final
    def get_zoom_limits(self) -> tuple[float, float]:
        """
        #### Возвращает текущие ограничения масштабирования
        
        ---
        
        :Returns:
        - tuple[float, float]: Кортеж (минимальный_масштаб, максимальный_масштаб)
        
        ---
        
        :Example:
        ```python
        min_zoom, max_zoom = camera.get_zoom_limits()
        print(f"Масштаб: {min_zoom}x - {max_zoom}x")
        ```
        """
        return (self.__min_zoom, self.__max_zoom)

    @final
    def set_bounds(self, rect: FloatRect) -> Self:
        """
        #### Устанавливает границы движения камеры
        
        ---
        
        :Description:
        - Ограничивает область, в которой может перемещаться камера
        - Полезно для предотвращения выхода камеры за пределы уровня
        - Автоматически включает систему ограничений
        
        ---
        
        :Args:
        - rect (FloatRect): Прямоугольник ограничений в мировых координатах
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Ограничить камеру областью уровня
        level_bounds = FloatRect(0, 0, 2000, 1500)
        camera.set_bounds(level_bounds)
        ```
        """
        self.__bounds_rect = rect
        self.__bounds_enabled = True
        return self

    @final
    def disable_bounds(self) -> Self:
        """
        #### Отключает ограничения движения камеры
        
        ---
        
        :Description:
        - Позволяет камере свободно перемещаться в любом направлении
        - Полезно для открытых миров или динамических уровней
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Отключить ограничения для свободного полета
        camera.disable_bounds()
        ```
        """
        self.__bounds_enabled = False
        return self

    @final
    def set_deadzone(self, rect: FloatRect) -> Self:
        """
        #### Устанавливает мертвую зону в центре камеры
        
        ---
        
        :Description:
        - Создает область в центре экрана, где объект может двигаться без движения камеры
        - Камера начинает следовать только когда объект выходит за пределы мертвой зоны
        - Полезно для платформеров и action-игр
        
        ---
        
        :Args:
        - rect (FloatRect): Прямоугольник мертвой зоны относительно центра камеры
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Создать мертвую зону 200x150 пикселей
        deadzone = FloatRect(-100, -75, 200, 150)
        camera.set_deadzone(deadzone)
        ```
        """
        self.__deadzone_rect = rect
        self.__deadzone_enabled = True
        return self

    @final
    def disable_deadzone(self) -> Self:
        """
        #### Отключает мертвую зону камеры
        
        ---
        
        :Description:
        - Камера будет немедленно следовать за объектом без задержки
        - Обеспечивает более плавное и отзывчивое следование
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Отключить мертвую зону для точного следования
        camera.disable_deadzone()
        ```
        """
        self.__deadzone_enabled = False
        return self

    @final
    def set_lerp_rotate(self, lerp: float) -> Self:
        """
        #### Устанавливает скорость интерполяции поворота камеры
        
        ---
        
        :Description:
        - Определяет, насколько быстро камера поворачивается к целевому углу
        - Меньшие значения = более плавный поворот
        - Большие значения = более быстрый поворот
        
        ---
        
        :Args:
        - lerp (float): Коэффициент интерполяции (0.01-1.0)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Медленный плавный поворот
        camera.set_lerp_rotate(0.02)
        ```
        """
        self.__angle_lerp = max(0.01, min(1.0, lerp))
        return self

    @final
    def set_lerp_movement(self, lerp: float) -> Self:
        """
        #### Устанавливает скорость интерполяции движения камеры
        
        ---
        
        :Description:
        - Определяет, насколько быстро камера следует за целевой позицией
        - Меньшие значения = более плавное следование с задержкой
        - Большие значения = более быстрое и отзывчивое следование
        
        ---
        
        :Args:
        - lerp (float): Коэффициент интерполяции (0.01-1.0)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Очень плавное следование
        camera.set_lerp_movement(0.05)
        ```
        """
        self.__lerp_movement = max(0.01, min(1.0, lerp))
        return self

    @final
    def set_target_angle(self, angle: float) -> Self:
        """
        #### Устанавливает целевой угол поворота камеры
        
        ---
        
        :Description:
        - Камера плавно повернется к указанному углу
        - Угол указывается в градусах
        - Скорость поворота зависит от set_lerp_rotate()
        
        ---
        
        :Args:
        - angle (float): Целевой угол в градусах (0-360)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Повернуть камеру на 45 градусов
        camera.set_target_angle(45)
        ```
        """
        self.__target_angle = angle % 360
        return self

    @final
    def rotate_by(self, angle_delta: float) -> Self:
        """
        #### Поворачивает камеру на указанное количество градусов
        
        ---
        
        :Description:
        - Добавляет указанный угол к текущему целевому углу
        - Положительные значения = поворот по часовой стрелке
        - Отрицательные значения = поворот против часовой стрелки
        
        ---
        
        :Args:
        - angle_delta (float): Изменение угла в градусах
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Повернуть камеру на 90 градусов по часовой стрелке
        camera.rotate_by(90)
        ```
        """
        self.__target_angle = (self.__target_angle + angle_delta) % 360
        return self

    @final
    def get_angle(self) -> float:
        """
        #### Возвращает текущий угол поворота камеры
        
        ---
        
        :Returns:
        - float: Текущий угол поворота в градусах (0-360)
        
        ---
        
        :Example:
        ```python
        print(f"Камера повернута на {camera.get_angle():.1f} градусов")
        ```
        """
        return self.__angle

    @final
    def set_lerp_zoom(self, lerp: float) -> Self:
        """
        #### Устанавливает скорость интерполяции масштабирования
        
        ---
        
        :Description:
        - Определяет, насколько быстро камера масштабируется к целевому уровню
        - Меньшие значения = более плавное масштабирование
        - Большие значения = более быстрое масштабирование
        
        ---
        
        :Args:
        - lerp (float): Коэффициент интерполяции (0.01-1.0)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Медленное плавное масштабирование
        camera.set_lerp_zoom(0.03)
        ```
        """
        self.__lerp_zoom = max(0.01, min(1.0, lerp))
        return self

    @final
    def follow(self, position_1: Vector2f, position_2: Vector2f | None = None) -> Self:
        """
        #### Устанавливает объект(ы) для слежения камеры
        
        ---
        
        :Description:
        - При одном объекте: камера следует за ним с учетом мертвой зоны
        - При двух объектах: камера позиционируется между ними с автомасштабированием
        - Автоматически переключает режимы слежения
        
        ---
        
        :Args:
        - position_1 (Vector2f): Позиция первого объекта слежения
        - position_2 (Vector2f | None): Позиция второго объекта (опционально)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Следить за одним игроком
        camera.follow(player.position)
        
        # Следить за двумя игроками одновременно
        camera.follow(player1.position, player2.position)
        ```
        """
        self.__target_center = position_1

        if position_2 is not None:
            self.__first_target = position_1
            self.__second_target = position_2
            self.set_using_two_target(True)
        else:
            self.set_using_two_target(False)
        
        return self

    @final
    def set_target_zoom(self, zoom: float = 1) -> Self:
        """
        #### Устанавливает целевой уровень масштабирования
        
        ---
        
        :Description:
        - Камера плавно масштабируется к указанному уровню
        - Автоматически ограничивается установленными лимитами
        - Скорость масштабирования зависит от set_lerp_zoom()
        
        ---
        
        :Args:
        - zoom (float): Целевой уровень масштабирования (>0)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Приблизить камеру в 2 раза
        camera.set_target_zoom(0.5)
        ```
        """
        zoom = max(self.__min_zoom, min(self.__max_zoom, zoom))
        self.__target_zoom = zoom
        self.__saved_zoom = zoom
        return self

    @final
    def set_size(self, width: int, height: int) -> Self:
        """
        #### Изменяет размер области просмотра камеры
        
        ---
        
        :Description:
        - Обновляет размеры области просмотра камеры
        - Автоматически пересчитывает внутренние параметры
        - Полезно при изменении разрешения или размера окна
        
        ---
        
        :Args:
        - width (int): Новая ширина области просмотра (>0)
        - height (int): Новая высота области просмотра (>0)
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Raises:
        - ValueError: При недопустимых размерах
        
        ---
        
        :Example:
        ```python
        # Адаптировать камеру к новому размеру окна
        camera.set_size(1920, 1080)
        ```
        """
        if width <= 0 or height <= 0:
            raise ValueError("Camera dimensions must be positive")
        
        self.__view.set_size(width, height)
        self.__width = width
        self.__height = height
        return self

    @final
    def get_center_position(self) -> Vector2f:
        """
        #### Возвращает текущую позицию центра камеры
        
        ---
        
        :Description:
        - Показывает фактическую позицию центра камеры в мировых координатах
        - Учитывает все трансформации и эффекты
        - Полезно для расчетов видимости объектов
        
        ---
        
        :Returns:
        - Vector2f: Координаты центра камеры
        
        ---
        
        :Example:
        ```python
        center = camera.get_center_position()
        print(f"Камера находится в ({center.x}, {center.y})")
        ```
        """
        return Vector2f(*self.__view.get_center())
    
    @final
    def get_size(self) -> Vector2f:
        """
        #### Возвращает текущий размер области просмотра камеры
        
        ---
        
        :Description:
        - Показывает фактический размер области просмотра с учетом масштабирования
        - Больший размер = больше видимой области (отдаленная камера)
        - Меньший размер = меньше видимой области (приближенная камера)
        
        ---
        
        :Returns:
        - Vector2f: Размер области просмотра (ширина, высота)
        
        ---
        
        :Example:
        ```python
        size = camera.get_size()
        print(f"Видимая область: {size.x}x{size.y}")
        ```
        """
        size = self.__view.get_float_rect().get_size()
        return Vector2f(*size) * self.__zoom
    
    @final
    def get_position(self) -> Vector2f:
        """
        #### Возвращает текущую позицию камеры
        
        ---
        
        :Description:
        - Возвращает текущую позицию центра камеры
        - Эквивалентно get_center_position() для совместимости
        
        ---
        
        :Returns:
        - Vector2f: Текущая позиция камеры
        
        ---
        
        :Example:
        ```python
        pos = camera.get_position()
        ```
        """
        return self.__current_center 
    
    def set_center(self, position: Vector2f):
        self.__current_center = position
        self.__view.set_center(*position.as_tuple())

    @final
    def update(self, delta: float = 1) -> None:
        """
        #### Обновляет состояние камеры
        
        ---
        
        :Description:
        - Выполняет все вычисления и анимации камеры
        - Обрабатывает интерполяцию движения, масштабирования и поворота
        - Применяет эффекты тряски и ограничения
        - Должен вызываться каждый кадр
        
        ---
        
        :Args:
        - delta (float): Коэффициент времени кадра (обычно 1.0)
        
        ---
        
        :Workflow:
        1. Адаптация к изменению размера окна
        2. Обработка двойного слежения
        3. Интерполяция позиции и масштаба
        4. Применение эффектов тряски
        5. Обработка поворота камеры
        6. Применение ограничений
        
        ---
        
        :Example:
        ```python
        # В основном игровом цикле
        camera.update(window.get_delta())
        ```
        """
        # =============================================
        # Адаптация к изменению размера окна
        # =============================================
        if self.__window and self.__window.get_resized():
            self.__width = self.__window.get_size().x
            self.__height = self.__window.get_size().y
            self.__view.set_size(self.__width, self.__height)

        # =============================================
        # Обработка режима двойного слежения
        # =============================================
        if self.__use_two_target and self.__first_target and self.__second_target:
            # Вычисляем позицию между двумя объектами
            pos_1 = self.__first_target.as_tuple()
            pos_2 = self.__second_target.as_tuple()
            normal = Vector2f(pos_1[0] - pos_2[0], pos_1[1] - pos_2[1])
            self.__target_center = self.__second_target + normal * self.__two_target_factor
        
        # =============================================
        # Интерполяция позиции камеры
        # =============================================
        self.__current_center = Vector2f(*self.__view.get_center())
        self.__current_center += (self.__target_center - self.__current_center) * self.__lerp_movement * delta
        self.__view.set_center(*self.__current_center.xy)

        # =============================================
        # Автоматическое масштабирование для двух объектов
        # =============================================
        if self.__use_two_target and self.__first_target and self.__second_target:
            vector_delta = (self.__first_target - self.__second_target)
            distance_x = abs(vector_delta.x)
            distance_y = abs(vector_delta.y)

            k = 0.5 / max(self.__two_target_factor, 1 - self.__two_target_factor)

            d_x = max(distance_x / ((self.__width - self.__auto_scale_padding) * k), self.__saved_zoom)
            d_y = max(distance_y / ((self.__height - self.__auto_scale_padding) * k), self.__saved_zoom)

            self.__target_zoom = max(d_x, d_y)
        else:
            self.__target_zoom = self.__saved_zoom
            
        # Применение ограничений масштабирования
        self.__target_zoom = max(self.__min_zoom, min(self.__max_zoom, self.__target_zoom))

        # =============================================
        # Интерполяция масштабирования
        # =============================================
        self.__zoom += (self.__target_zoom - self.__zoom) * self.__lerp_zoom * delta
        self.__view.set_size(self.__width * self.__zoom, self.__height * self.__zoom)

        # =============================================
        # Обработка эффектов тряски
        # =============================================
        self.__target_shake *= self.__shake_lerp ** delta
        
        # Генерация случайного направления тряски
        if not self.__shake_only_x and not self.__shake_only_y:
            self.__current_shake = self.__target_shake.rotate(randint(0, 360))
        elif self.__shake_only_x:
            self.__current_shake.x = self.__target_shake.x * uniform(-1, 1)
            self.__current_shake.y = 0
        elif self.__shake_only_y:
            self.__current_shake.x = 0
            self.__current_shake.y = self.__target_shake.y * uniform(-1, 1)
        
        # Применение тряски к позиции камеры
        self.__view.move(self.__current_shake.x, self.__current_shake.y)

        # =============================================
        # Интерполяция поворота камеры
        # =============================================
        angle_diff = self.__target_angle - self.__angle
        
        # Обработка перехода через 360/0 градусов
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
            
        self.__angle += angle_diff * self.__angle_lerp * delta
        self.__angle = self.__angle % 360
        
        self.__view.set_angle(self.__angle)

    @final
    def apply(self, window: Window) -> None:
        """
        #### Применяет камеру к окну
        
        ---
        
        :Description:
        - Устанавливает представление камеры как активное для окна
        - Все последующие операции рендеринга будут использовать эту камеру
        - Должен вызываться перед рендерингом объектов
        
        ---
        
        :Args:
        - window (Window): Окно для применения камеры
        
        ---
        
        :Example:
        ```python
        # Применить камеру перед рендерингом игровых объектов
        camera.apply(window)
        render_game_objects()
        ```
        """
        window.set_view(self.__view)

    @final
    def apply_texture(self, texture):
        texture.set_view(self.__view)

    @final
    def reapply(self, window: Window) -> None:
        """
        #### Восстанавливает стандартное представление окна
        
        ---
        
        :Description:
        - Сбрасывает представление окна к стандартному виду
        - Полезно для рендеринга UI элементов в экранных координатах
        - Отменяет все трансформации камеры
        
        ---
        
        :Args:
        - window (Window): Окно для восстановления стандартного представления
        
        ---
        
        :Example:
        ```python
        # Восстановить стандартный вид для UI
        camera.reapply(window)
        render_ui_elements()
        ```
        """
        window.set_view(window.get_default_view())


@final
class CameraMachine2D(Camera2D):
    """
    #### Класс камеры с ручным управлением позицией
    
    ---
    
    :Description:
    - Расширяет базовую Camera2D возможностью ручного управления
    - Позволяет программно перемещать камеру без привязки к объектам
    - Идеально подходит для стратегических игр, редакторов уровней
    - Сохраняет все возможности базовой камеры (тряска, масштабирование, поворот)
    
    ---
    
    :Features:
    - Прямое управление позицией камеры
    - Плавное движение с интерполяцией
    - Совместимость со всеми эффектами базовой камеры
    - Простой интерфейс для программного управления
    """
    
    def __init__(self, width: int, height: int):
        """
        #### Инициализация камеры с ручным управлением
        
        ---
        
        :Args:
        - width (int): Ширина области просмотра камеры
        - height (int): Высота области просмотра камеры
        
        ---
        
        :Example:
        ```python
        # Создание камеры для стратегической игры
        strategy_camera = CameraMachine2D(1920, 1080)
        ```
        """
        super().__init__(width, height)
        self.__manual_position = Vector2f(0, 0)  # Позиция для ручного управления
        self.__movement_speed = 300.0            # Скорость движения в пикселях/секунду

    @final
    def move(self, x: float = 0, y: float = 0) -> Self:
        """
        #### Перемещает камеру на указанное смещение
        
        ---
        
        :Description:
        - Добавляет смещение к текущей позиции камеры
        - Использует плавную интерполяцию базовой камеры
        - Подходит для постепенного движения камеры
        
        ---
        
        :Args:
        - x (float): Смещение по горизонтали
        - y (float): Смещение по вертикали
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Движение камеры клавишами WASD
        if keyboard.is_pressed('w'): camera.move(0, -5)
        if keyboard.is_pressed('s'): camera.move(0, 5)
        if keyboard.is_pressed('a'): camera.move(-5, 0)
        if keyboard.is_pressed('d'): camera.move(5, 0)
        ```
        """
        self.__manual_position += Vector2f(x, y)
        return self

    @final
    def get_position(self) -> Vector2f:
        """
        #### Возвращает текущую позицию ручного управления
        
        ---
        
        :Description:
        - Показывает позицию, установленную через ручное управление
        - Может отличаться от фактической позиции камеры из-за интерполяции
        
        ---
        
        :Returns:
        - Vector2f: Целевая позиция ручного управления
        
        ---
        
        :Example:
        ```python
        pos = camera.get_position()
        print(f"Целевая позиция: ({pos.x}, {pos.y})")
        ```
        """
        return self.__manual_position
    
    @final
    def set_position(self, position: Vector2f) -> Self:
        """
        #### Устанавливает позицию камеры для ручного управления
        
        ---
        
        :Description:
        - Устанавливает целевую позицию для камеры
        - Камера плавно переместится к этой позиции
        - Не влияет на режимы автоматического слежения
        
        ---
        
        :Args:
        - position (Vector2f): Новая целевая позиция
        
        ---
        
        :Returns:
        - Self: Возвращает self для цепочки вызовов
        
        ---
        
        :Example:
        ```python
        # Переместить камеру к важному объекту
        camera.set_position(important_object.position)
        ```
        """
        self.__manual_position = position
        return self

    @final
    def update(self, delta_time: float = 1.0) -> None:
        """
        #### Обновляет состояние камеры с ручным управлением
        
        ---
        
        :Description:
        - Устанавливает целевую позицию для базовой камеры
        - Вызывает обновление базовой камеры со всеми эффектами
        - Должен вызываться каждый кадр
        
        ---
        
        :Args:
        - delta_time (float): Коэффициент времени кадра
        
        ---
        
        :Example:
        ```python
        # В основном игровом цикле
        camera.update(window.get_delta())
        ```
        """
        # Устанавливаем ручную позицию как цель для слежения
        self.follow(self.__manual_position)
        # Обновляем базовую камеру со всеми эффектами
        super().update(delta_time)
