from dataclasses import dataclass
from enum import Enum, auto
from uuid import uuid4

from Moon.python.Vectors import Vector2f
from Moon.python.Types import *
from Moon.python.Rendering.Shapes import RectangleShape
from Moon.python.Colors import *
from Moon.python.Window import Window
from Moon.python.Colors import COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_GRAY, COLOR_TRANSPARENT
from Moon.python.Math import rects_collision
from Moon.python.Engine.Tilesets import TileMap

from itertools import chain

from typing import Self, Literal


# --- Перечисление типов коллайдеров ---
class ColliderType(Enum):
    STATIC = auto()     # Неподвижные объекты (стены, пол) - не движутся и не реагируют на столкновения силой
    KINEMATIC = auto()  # Движущиеся платформы - их движение управляется напрямую (например, по заданному пути),
                        # но они не реагируют на столкновения силой. Они могут влиять на динамические объекты.
    DYNAMIC = auto()    # Полноценные физические объекты - подвержены силам (гравитации), скорости,
                        # и активно разрешают столкновения, отскакивая или останавливаясь.

# --- Класс ColliderMaterial: Определяет физические свойства объекта ---
class ColliderMaterial:
    def __init__(self, friction: Vector2f = Vector2f(0.0, 0.0),
                 air_resistance: Vector2f = Vector2f(0.0, 0.0),
                 self_friction: Vector2f = Vector2f(0.0, 0.0),
                 bounce: Vector2f = Vector2f(0.0, 0.0)):
        """
        Инициализация материала коллайдера.
        Параметры:
            friction (Vector2f): Коэффициент трения, применяемый при контакте с другой поверхностью.
                                 x-компонента влияет на горизонтальное движение при вертикальном столкновении.
                                 y-компонента влияет на вертикальное движение при горизонтальном столкновении.
            air_resistance (Vector2f): Коэффициент сопротивления воздуха. Чем выше значение, тем быстрее объект
                                       теряет скорость в воздухе.
            self_friction (Vector2f): Коэффициент трения самого объекта. На данный момент не используется в update-логике.
            bounce (Vector2f): Коэффициент отскока (эластичности столкновения). Значение 1.0 означает полный отскок,
                               0.0 - отсутствие отскока (абсолютно неупругое столкновение).
        """
        self.__friction = friction
        self.__air_resistance = air_resistance
        self.__self_friction = self_friction
        self.__bounce = bounce

    @property
    def self_friction(self) -> Vector2f:
        return self.__self_friction

    @property
    def friction(self) -> Vector2f:
        return self.__friction

    @property
    def air_resistance(self) -> Vector2f:
        return self.__air_resistance

    @property
    def bounce(self) -> Vector2f:
        return self.__bounce

    @bounce.setter
    def bounce(self, value: Vector2f):
        self.__bounce = value

    @self_friction.setter
    def self_friction(self, value: Vector2f):
        self.__self_friction = value

    @friction.setter
    def friction(self, value: Vector2f):
        self.__friction = value

    @air_resistance.setter
    def air_resistance(self, value: Vector2f):
        self.__air_resistance = value


# --- Базовый класс для 2D-прямоугольных форм ---
class Box2D:
    def __init__(self, width: Number, height: Number):
        """
        Инициализация базового 2D-прямоугольника.
        Параметры:
            width (Number): Ширина прямоугольника.
            height (Number): Высота прямоугольника.
        """
        self.__width = width
        self.__height = height

    @property
    def width(self) -> Number:
        return self.__width

    @property
    def height(self) -> Number:
        return self.__height

    @width.setter
    def width(self, value: Number):
        self.__width = value

    @height.setter
    def height(self, value: Number):
        self.__height = value


# --- Класс BoxCollider2D: Представляет физический коллайдер в форме прямоугольника ---
class BoxCollider2D(Box2D):
    def __init__(self, width: Number, height: Number, material: ColliderMaterial, type: ColliderType, identifier: Identifier = None):
        """
        Инициализация BoxCollider2D.
        Параметры:
            width (Number): Ширина коллайдера.
            height (Number): Высота коллайдера.
            material (ColliderMaterial): Материал, определяющий физические свойства коллайдера.
            type (ColliderType): Тип коллайдера (STATIC, KINEMATIC, DYNAMIC).
            identifier (Identifier): Уникальный идентификатор коллайдера. Если не указан, генерируется UUID.
        """
        super().__init__(width, height)

        self.__material = material
        self.__identifier = identifier if identifier is not None else str(uuid4())
        self.__type = type

        self.speed = Vector2f(0.0, 0.0)    # Текущая скорость коллайдера (для DYNAMIC и KINEMATIC)
        self.position = Vector2f(0.0, 0.0) # Позиция верхнего левого угла коллайдера

        self.__used: bool = False # Флаг для буферизации коллайдеров (пул объектов)

        # Словарь для отслеживания касаний граней в текущем кадре
        self.__touches = {
            "left": False,
            "right": False,
            "top": False,
            "bottom": False
        }

        # Словарь для определения, какие грани являются физическими (проходимыми/непроходимыми)
        self.__physical_facets = {
            "left": True,
            "right": True,
            "top": True,
            "bottom": True
        }

        # Ссылка на платформу, на которой находится динамический коллайдер (если есть)
        self.on_platform: BoxCollider2D | None = None

    def get_physical_facets(self) -> dict[Literal['left', 'right', 'top', 'bottom'], bool]:
        """Возвращает текущее состояние физических граней."""
        return self.__physical_facets

    def set_physical_facets(self, left: bool = True, right: bool = True, top: bool = True, bottom: bool = True) -> Self:
        """
        Устанавливает, какие грани коллайдера являются физическими (через них нельзя пройти).
        Например, для платформы, через которую можно провалиться, `bottom` может быть `False`.
        """
        self.__physical_facets['left'] = left
        self.__physical_facets['right'] = right
        self.__physical_facets['top'] = top
        self.__physical_facets['bottom'] = bottom
        return self

    def reset_touches(self):
        """Сбрасывает флаги касаний для всех граней в начале каждого кадра."""
        self.__touches['left'] = False
        self.__touches['right'] = False
        self.__touches['top'] = False
        self.__touches['bottom'] = False

    # --- Свойства для удобного доступа к положению и размерам коллайдера ---
    @property
    def center(self) -> Vector2f:
        return Vector2f(self.position.x + self.width / 2, self.position.y + self.height / 2)

    @center.setter
    def center(self, value: Vector2f):
        self.position = Vector2f(value.x - self.width / 2, value.y - self.height / 2)

    @property
    def top(self) -> Number:
        return self.position.y

    @property
    def bottom(self) -> Number:
        return self.position.y + self.height

    @property
    def left(self) -> Number:
        return self.position.x

    @property
    def right(self) -> Number:
        return self.position.x + self.width

    @top.setter
    def top(self, value: Number):
        self.position.y = value

    @bottom.setter
    def bottom(self, value: Number):
        self.position.y = value - self.height

    @left.setter
    def left(self, value: Number):
        self.position.x = value

    @right.setter
    def right(self, value: Number):
        self.position.x = value - self.width

    def is_static(self) -> bool:
        """Проверяет, является ли коллайдер статическим."""
        return self.__type == ColliderType.STATIC

    def set_position(self, x: Number, y: Number) -> Self:
        """Устанавливает позицию коллайдера."""
        self.position.x = x
        self.position.y = y
        return self

    # --- Методы для управления состоянием коллайдера при использовании пула объектов ---
    def _set_identifier(self, value: Identifier):
        self.__identifier = value

    def _set_used(self, value: bool):
        self.__used = value

    def get_used(self) -> bool:
        """Возвращает, используется ли коллайдер из буфера."""
        return self.__used

    def get_type(self) -> ColliderType:
        """Возвращает тип коллайдера."""
        return self.__type

    def set_type(self, value: ColliderType):
        """Устанавливает тип коллайдера."""
        self.__type = value

    def get_identifier(self) -> Identifier:
        """Возвращает уникальный идентификатор коллайдера."""
        return self.__identifier

    @property
    def material(self) -> ColliderMaterial:
        return self.__material

    @material.setter
    def material(self, value: ColliderMaterial):
        self.__material = value

    def __str__(self) -> str:
        return f"BoxCollider2D: {self.position} {self.speed} {self.width} {self.height}"

    def get_touches(self) -> dict[Literal['top', 'bottom', 'left', 'right'], bool]:
        """Возвращает словарь с флагами касаний для каждой грани."""
        return self.__touches

    def set_touche(self, touche: Literal['top', 'bottom', 'left', 'right'], value: bool):
        """Устанавливает флаг касания для конкретной грани."""
        self.__touches[touche] = value


# --- Глобальная переменная для отображения коллайдеров ---
BOX_SHAPE = RectangleShape(1, 1)
BOX_SHAPE.set_color(COLOR_TRANSPARENT) # Прозрачная заливка
BOX_SHAPE.set_outline_thickness(1) # Тонкая обводка

# --- Класс ColliderLayer: Управляет всеми коллайдерами в сцене ---
class ColliderLayer:
    def __init__(self):
        # Буфер для переиспользования коллайдеров (оптимизация)
        self.__colliders_buffer: list[BoxCollider2D] = []
        self.__use_pre_init: bool = False # Флаг использования буфера

        # Списки для хранения коллайдеров по их типам
        self.__static_colliders: list[BoxCollider2D] = []
        self.__dynamic_colliders: list[BoxCollider2D] = []
        self.__kinematic_colliders: list[BoxCollider2D] = []

        self.__gravity: Vector2f = Vector2f(0.0, 1) # Вектор гравитации (по умолчанию вниз)

    def set_gravity(self, gravity: Vector2f):
        """Устанавливает вектор гравитации."""
        self.__gravity = gravity

    def get_gravity(self) -> Vector2f:
        """Возвращает текущий вектор гравитации."""
        return self.__gravity

    def pre_init_colliders(self, count: int):
        """
        Предварительная инициализация коллайдеров в буфере.
        Используется для оптимизации, чтобы избежать частого создания/удаления объектов.
        """
        if self.__use_pre_init:
            for _ in range(count):
                # Создаем "пустые" коллайдеры и помечаем их как неиспользуемые
                collider = BoxCollider2D(10, 10, ColliderMaterial(), ColliderType.STATIC)
                collider._set_used(False)
                self.__colliders_buffer.append(collider)
        else:
            raise Exception("You must call use_pre_init() before using pre_init_colliders()")

    def use_pre_init(self) -> Self:
        """Включает режим предварительной инициализации коллайдеров."""
        self.__use_pre_init = True
        return self

    def get_use_pre_init(self) -> bool:
        """Проверяет, включен ли режим предварительной инициализации."""
        return self.__use_pre_init

    def found_unused_collider(self) -> BoxCollider2D | None:
        """Ищет неиспользуемый коллайдер в буфере."""
        for collider in self.__colliders_buffer:
            if not collider.get_used():
                return collider
        return None

    def get_used_colliders(self) -> list[BoxCollider2D]:
        """Возвращает список всех используемых (активных) коллайдеров."""
        return chain(self.__dynamic_colliders, self.__kinematic_colliders, self.__static_colliders)
    
    def delete_collider_by_id(self, identifier: Identifier):
        """Удаляет коллайдер по его идентификатору."""
        for collider in self.get_used_colliders():
            if collider.get_identifier() == identifier:
                collider._set_used(False)
                collider._set_identifier(None)
                return

    def get_dynamic_collider_by_id(self, identifier: Identifier) -> BoxCollider2D | None:
        """Ищет динамический коллайдер по его идентификатору."""
        for collider in self.get_used_colliders():
            if collider.get_identifier() == identifier:
                return collider
        return None

    def add_collider(self, collider: BoxCollider2D, identifier_suffix: int | None = None) -> BoxCollider2D:
        """
        Добавляет коллайдер в слой. Если включен режим pre_init,
        использует коллайдер из буфера.
        """
        if self.__use_pre_init:
            unused_collider = self.found_unused_collider()
            if unused_collider is None:
                raise Exception("No unused colliders available in buffer. Increase pre_init_colliders count.")

            # Копируем свойства из нового коллайдера в буферизованный
            new_identifier = collider.get_identifier()
            if identifier_suffix is not None:
                new_identifier += f"_{identifier_suffix}"

            unused_collider._set_identifier(new_identifier)
            unused_collider._set_used(True)
            unused_collider.position = collider.position.copy()
            unused_collider.width = collider.width
            unused_collider.height = collider.height
            unused_collider.speed = collider.speed.copy()
            unused_collider.material = collider.material # Возможно, тут тоже нужно .copy() если материал может меняться индивидуально
            unused_collider.set_type(collider.get_type())
            unused_collider.set_physical_facets(**collider.get_physical_facets())
            unused_collider.on_platform = None # Сбрасываем состояние платформы при переиспользовании

            # Добавляем в соответствующий список по типу
            if unused_collider.get_type() == ColliderType.STATIC:
                self.__static_colliders.append(unused_collider)
            elif unused_collider.get_type() == ColliderType.KINEMATIC:
                self.__kinematic_colliders.append(unused_collider)
            elif unused_collider.get_type() == ColliderType.DYNAMIC:
                self.__dynamic_colliders.append(unused_collider)

            return unused_collider
        else:
            # Если буфер не используется, просто добавляем коллайдер напрямую
            if collider.get_type() == ColliderType.STATIC:
                self.__static_colliders.append(collider)
            elif collider.get_type() == ColliderType.KINEMATIC:
                self.__kinematic_colliders.append(collider)
            elif collider.get_type() == ColliderType.DYNAMIC:
                self.__dynamic_colliders.append(collider)
            collider._set_used(True)
            return collider

    def remove_collider(self, collider: BoxCollider2D):
        """
        Удаляет коллайдер из слоя. Если используется буфер, помечает его как неиспользуемый.
        """
        if collider.get_type() == ColliderType.STATIC:
            if collider in self.__static_colliders:
                self.__static_colliders.remove(collider)
        elif collider.get_type() == ColliderType.KINEMATIC:
            if collider in self.__kinematic_colliders:
                self.__kinematic_colliders.remove(collider)
        elif collider.get_type() == ColliderType.DYNAMIC:
            if collider in self.__dynamic_colliders:
                self.__dynamic_colliders.remove(collider)

        if self.__use_pre_init:
            collider._set_used(False)
            # Сбрасываем состояние для переиспользования
            collider.speed = Vector2f(0, 0)
            collider.position = Vector2f(0, 0)
            collider.on_platform = None # Сброс состояния платформы

    def _get_collisions(self, collider: BoxCollider2D, colliders: list[BoxCollider2D]) -> list[BoxCollider2D]:
        """
        Вспомогательный метод для получения всех коллайдеров, с которыми данный коллайдер
        в данный момент пересекается.
        """
        collisions = []
        for other_collider in colliders:
            if collider.get_identifier() == other_collider.get_identifier():
                continue # Не проверять столкновение с самим собой
            if rects_collision(*collider.position.xy, collider.width, collider.height,
                               *other_collider.position.xy, other_collider.width, other_collider.height):
                collisions.append(other_collider)
        return collisions

    def update(self, delta_time: Number) -> None:
        """
        Основной метод обновления физики для всех коллайдеров в слое.
        Выполняет расчеты движения и разрешение столкновений.
        :param delta_time: Время, прошедшее с последнего обновления (в секундах).
        """
        # Фаза 1: Обновление кинематических коллайдеров
        # Они движутся независимо и не подвержены силам или столкновениям (в этом слое).
        # Сохраняем их смещение за кадр для последующего применения к динамическим объектам.
        kinematic_deltas = {}
        for kinematic_collider in self.__kinematic_colliders:
            old_position = kinematic_collider.position.copy()
            kinematic_collider.position += kinematic_collider.speed * delta_time
            # Рассчитываем и сохраняем вектор смещения платформы
            kinematic_deltas[kinematic_collider.get_identifier()] = kinematic_collider.position - old_position

        # Фаза 2: Обновление динамических коллайдеров
        for dynamic_collider in self.__dynamic_colliders:
            dynamic_collider.reset_touches() # Сбрасываем флаги касаний для нового кадра

            # --- Обработка движения на платформе (если dynamic_collider находится на kinematic-платформе) ---
            if dynamic_collider.on_platform:
                platform_id = dynamic_collider.on_platform.get_identifier()
                # Проверяем, существует ли еще эта платформа и двигалась ли она
                if platform_id in kinematic_deltas:
                    # Предварительно рассчитываем позицию, если бы персонаж двигался с платформой
                    predicted_position = dynamic_collider.position + kinematic_deltas[platform_id]

                    # Создаем временный коллайдер для проверки столкновений при движении с платформой
                    temp_collider = BoxCollider2D(dynamic_collider.width, dynamic_collider.height, dynamic_collider.material, dynamic_collider.get_type())
                    temp_collider.position = predicted_position

                    # Проверяем, не вызовет ли движение с платформой столкновение с другими объектами
                    # (статическими или другими кинематическими)
                    collisions = self._get_collisions(temp_collider, chain(self.__static_colliders, self.__kinematic_colliders))

                    if collisions:
                        # Если движение с платформой вызывает столкновение,
                        # мы *не* применяем это движение. Персонаж остается на месте относительно мира,
                        # и будет обрабатываться как обычное столкновение далее.
                        # Это предотвращает "застревание" в стенах при движении платформы.
                        dynamic_collider.position += kinematic_deltas[platform_id] * 0 # Эффективно 0, но явно видно намерение
                    else:
                        # Если столкновений нет, применяем движение платформы к персонажу
                        dynamic_collider.position += kinematic_deltas[platform_id]
                else:
                    # Если платформа, на которой находился персонаж, больше не существует (удалена),
                    # сбрасываем состояние "на платформе".
                    dynamic_collider.on_platform = None

            # --- Применение гравитации и сопротивления воздуха ---
            # Гравитация увеличивает вертикальную скорость
            dynamic_collider.speed.y += self.__gravity.y * delta_time
            # Сопротивление воздуха уменьшает скорость по обеим осям
            dynamic_collider.speed.x *= (1 - dynamic_collider.material.air_resistance.x * delta_time)
            dynamic_collider.speed.y *= (1 - dynamic_collider.material.air_resistance.y * delta_time)

            # --- Разрешение столкновений по оси Y ---
            # Предсказываем будущую позицию по Y, основываясь на текущей скорости
            projected_y_position = dynamic_collider.position.y + dynamic_collider.speed.y * delta_time
            # Создаем временный коллайдер для проверки столкновений только по Y-координате
            temp_y_collider = BoxCollider2D(dynamic_collider.width, dynamic_collider.height, dynamic_collider.material, dynamic_collider.get_type())
            temp_y_collider.position = Vector2f(dynamic_collider.position.x, projected_y_position)

            # Находим все потенциальные столкновения по Y
            collisions_y = self._get_collisions(temp_y_collider, chain(self.__static_colliders, self.__kinematic_colliders))

            # Сбрасываем флаг on_platform перед проверкой, он будет установлен заново,
            # если произойдет столкновение снизу с платформой.
            dynamic_collider.on_platform = None



            for collided_collider in collisions_y:
                # --- Столкновение снизу (движение вниз) ---
                if dynamic_collider.speed.y >= 0:
                    # Проверяем, является ли верхняя грань 'collided_collider' физической
                    if collided_collider.get_physical_facets()['top']:
                        # Проверяем, что temp_y_collider пересек верхнюю грань collided_collider,
                        # а исходный dynamic_collider не был ниже этой грани (для предотвращения застревания).
                        if temp_y_collider.bottom > collided_collider.top and dynamic_collider.bottom <= collided_collider.top:
                            # Перемещаем dynamic_collider точно на верхнюю грань collided_collider
                            dynamic_collider.bottom = collided_collider.top
                            # Применяем отскок: меняем направление Y-скорости и уменьшаем её на основе коэффициентов отскока
                            dynamic_collider.speed.y *= -1 * (dynamic_collider.material.bounce.y + collided_collider.material.bounce.y) / 2
                            # Применяем горизонтальное трение при вертикальном столкновении
                            dynamic_collider.speed.x *= (1 - (dynamic_collider.material.friction.x + collided_collider.material.friction.x) / 2)
                            dynamic_collider.set_touche('bottom', True) # Устанавливаем флаг касания снизу
                            # Если скорость отскока очень мала, останавливаем движение по Y
                            if abs(dynamic_collider.speed.y) < 0.5:
                                dynamic_collider.speed.y = 0

                            # Если столкнулись с кинематическим объектом, помечаем его как платформу
                            if collided_collider.get_type() == ColliderType.KINEMATIC:
                                dynamic_collider.on_platform = collided_collider
                            break  # Обработали ближайшее столкновение по Y, выходим из цикла по Y

                # --- Столкновение сверху (движение вверх) ---
                elif dynamic_collider.speed.y < 0:
                    # Проверяем, является ли нижняя грань 'collided_collider' физической
                    if collided_collider.get_physical_facets()['bottom']:
                        # Проверяем, что temp_y_collider пересек нижнюю грань collided_collider,
                        # а исходный dynamic_collider не был выше этой грани.
                        if temp_y_collider.top < collided_collider.bottom and dynamic_collider.top >= collided_collider.bottom:
                            # Перемещаем dynamic_collider точно на нижнюю грань collided_collider
                            dynamic_collider.top = collided_collider.bottom
                            # Применяем отскок (меняем направление Y-скорости)
                            dynamic_collider.speed.y *= -1 * (dynamic_collider.material.bounce.y + collided_collider.material.bounce.y) / 2
                            # Применяем горизонтальное трение
                            dynamic_collider.speed.x *= (1 - (dynamic_collider.material.friction.x + collided_collider.material.friction.x) / 2)
                            dynamic_collider.set_touche('top', True) # Устанавливаем флаг касания сверху
                            # Если скорость отскока очень мала, останавливаем движение по Y
                            if abs(dynamic_collider.speed.y) < 0.5:
                                dynamic_collider.speed.y = 0
                            break  # Обработали ближайшее столкновение по Y, выходим

            # --- Применение окончательного смещения по Y ---
            # Если после всех проверок и разрешений не было касаний по Y, применяем оставшуюся Y-скорость.
            # Это позволяет объекту свободно падать или двигаться, если он не столкнулся.
            if not dynamic_collider.get_touches()['bottom'] and not dynamic_collider.get_touches()['top']:
                dynamic_collider.position.y += dynamic_collider.speed.y * delta_time

            # --- Разрешение столкновений по оси X ---
            # Предсказываем будущую позицию по X, основываясь на текущей скорости
            projected_x_position = dynamic_collider.position.x + dynamic_collider.speed.x * delta_time
            # Создаем временный коллайдер для проверки столкновений только по X-координате
            # Важно: Используем уже скорректированную позицию по Y (dynamic_collider.position.y)
            temp_x_collider = BoxCollider2D(dynamic_collider.width, dynamic_collider.height, dynamic_collider.material, dynamic_collider.get_type())
            temp_x_collider.position = Vector2f(projected_x_position, dynamic_collider.position.y)

            # Находим все потенциальные столкновения по X
            collisions_x = self._get_collisions(temp_x_collider, chain(self.__static_colliders, self.__kinematic_colliders))


            for collided_collider in collisions_x:
                # --- Столкновение справа (движение вправо) ---
                if dynamic_collider.speed.x >= 0:
                    # Проверяем, является ли левая грань 'collided_collider' физической
                    if collided_collider.get_physical_facets()['left']:
                        # Проверяем пересечение temp_x_collider с левой гранью collided_collider,
                        # и что dynamic_collider не был правее этой грани.
                        if temp_x_collider.right > collided_collider.left and dynamic_collider.right <= collided_collider.left:
                            # Перемещаем dynamic_collider точно на левую грань collided_collider
                            dynamic_collider.right = collided_collider.left
                            # Применяем отскок по X
                            dynamic_collider.speed.x *= -1 * (dynamic_collider.material.bounce.x + collided_collider.material.bounce.x) / 2
                            # Применяем вертикальное трение при горизонтальном столкновении
                            dynamic_collider.speed.y *= (1 - (dynamic_collider.material.friction.y + collided_collider.material.friction.y) / 2)
                            dynamic_collider.set_touche('right', True) # Устанавливаем флаг касания справа
                            # Если скорость отскока очень мала, останавливаем движение по X
                            if abs(dynamic_collider.speed.x) < 0.5:
                                dynamic_collider.speed.x = 0
                            break  # Обработали ближайшее столкновение по X, выходим

                # --- Столкновение слева (движение влево) ---
                elif dynamic_collider.speed.x < 0:
                    # Проверяем, является ли правая грань 'collided_collider' физической
                    if collided_collider.get_physical_facets()['right']:
                        # Проверяем пересечение temp_x_collider с правой гранью collided_collider,
                        # и что dynamic_collider не был левее этой грани.
                        if temp_x_collider.left < collided_collider.right and dynamic_collider.left >= collided_collider.right:
                            # Перемещаем dynamic_collider точно на правую грань collided_collider
                            dynamic_collider.left = collided_collider.right
                            # Применяем отскок по X
                            dynamic_collider.speed.x *= -1 * (dynamic_collider.material.bounce.x + collided_collider.material.bounce.x) / 2
                            # Применяем вертикальное трение
                            dynamic_collider.speed.y *= (1 - (dynamic_collider.material.friction.y + collided_collider.material.friction.y) / 2)
                            dynamic_collider.set_touche('left', True) # Устанавливаем флаг касания слева
                            # Если скорость отскока очень мала, останавливаем движение по X
                            if abs(dynamic_collider.speed.x) < 0.5:
                                dynamic_collider.speed.x = 0
                            break  # Обработали ближайшее столкновение по X, выходим

            # --- Применение окончательного смещения по X ---
            # Если после всех проверок и разрешений не было касаний по X, применяем оставшуюся X-скорость.
            if not dynamic_collider.get_touches()['left'] and not dynamic_collider.get_touches()['right']:
                dynamic_collider.position.x += dynamic_collider.speed.x * delta_time


    def view_info(self, window: Window, fill: bool = False) -> None:
        """
        Отображает все используемые коллайдеры на экране,
        маркируя их разными цветами в зависимости от типа.
        """
        used_colliders = self.get_used_colliders()

        for collider in used_colliders:
            color = COLOR_GRAY # Цвет по умолчанию
            if collider.get_type() == ColliderType.DYNAMIC:
                color = COLOR_RED # Динамические - красные
            elif collider.get_type() == ColliderType.STATIC:
                color = COLOR_GREEN # Статические - зеленые
            elif collider.get_type() == ColliderType.KINEMATIC:
                color = COLOR_BLUE # Кинематические - синие

            BOX_SHAPE.set_outline_color(color)
            if fill: BOX_SHAPE.set_color(color)
            BOX_SHAPE.set_position(*collider.position.xy)
            BOX_SHAPE.set_size(collider.width, collider.height)
            window.draw(BOX_SHAPE)

    def check_colliders(self):
        """Выводит информацию о количестве коллайдеров различных типов."""
        print("\n=== Colliders Check ================")
        print(f"{'Static colliders:':<25} {len(self.__static_colliders):>10}")
        print(f"{'Kinematic colliders:':<25} {len(self.__kinematic_colliders):>10}")
        print(f"{'Dynamic colliders:':<25} {len(self.__dynamic_colliders):>10}")
        print(f"{'Colliders buffer (unused):':<25} {len([c for c in self.__colliders_buffer if not c.get_used()]):>10}")
        print(f"{'Total colliders in buffer:':<25} {len(self.__colliders_buffer):>10}")
        print("====================================")



@dataclass
class ColliderMaterialAccordance:
    """
    Класс для хранения соответствия между материалами коллайдеров и материалами объектов.
    """
    material: ColliderMaterial
    identifier: int

class CollidersMateraialAccordances:
    """
    Класс для хранения соответствий между материалами коллайдеров и материалами объектов.
    """
    def __init__(self, materaial_accordances: list[ColliderMaterialAccordance]) -> None:
        self.__materaial_accordances = materaial_accordances
        self.__material_accordances_by_identifier = {}
        for accord in self.__materaial_accordances:
            self.__material_accordances_by_identifier[accord.identifier] = accord.material

    def get_accordance(self, identifier: int) -> ColliderMaterial:
        """
        Возвращает соответствующий материал коллайдера по его идентификатору.
        """
        return self.__material_accordances_by_identifier[identifier]
    
    def get_accordances(self) -> dict[int, ColliderMaterial]:
        """
        Возвращает словарь соответствий между идентификаторами и материалами коллайдеров.
        """
        return self.__material_accordances_by_identifier
    
    def get_collider_accordances(self) -> list[ColliderMaterialAccordance]:
        """
        Возвращает список соответствий между материалами коллайдеров и идентификаторами.
        """
        return self.__materaial_accordances

def generate_static_colliders(
    map: TileMap, 
    accordance: CollidersMateraialAccordances, 
    tile_size: TwoIntegerList, 
    tile_scale: Number,
    offset_x: Number = 0,
    offset_y: Number = 0,
) -> list[BoxCollider2D]:
    """
    #### Генерирует статические коллайдеры, объединяя соседние тайлы с одинаковыми материалами.
    Оптимизировано для создания минимального количества коллайдеров.

    ---
    
    :Algorithm:
    1. Инициализируем пустой список коллайдеров и глубокую копию данных карты, чтобы можно было их "обнулять".
    2. Проходим по каждому тайлу карты слева направо, сверху вниз.
    3. Если тайл пустой (0) или уже был "покрыт" предыдущим коллайдером (то есть его значение в `map_data` стало 0), пропускаем его.
    4. Для необработанного ненулевого тайла:
        a. Получаем `tile_id` и соответствующий ему `base_material` через `accordance`.
        b. Определяем `current_max_width`: максимально возможную ширину прямоугольника, начиная от текущей позиции `(x, y)` вправо, при условии, что все тайлы в этой горизонтальной полосе имеют тот же `base_material` и не равны 0.
        c. Определяем `max_rect_height`: максимально возможную высоту для найденной `current_max_width` вниз, при условии, что весь обнаруженный прямоугольник полностью состоит из тайлов с тем же `base_material` и не равных 0.
        d. Создаем `BoxCollider2D` на основе найденного прямоугольника (`current_max_width` на `max_rect_height`).
        e. Устанавливаем позицию коллайдера, масштабируя координаты тайлов.
        f. Добавляем созданный коллайдер в список `colliders`.
        g. "Обнуляем" (устанавливаем в 0) все тайлы в `map_data` в пределах созданного коллайдера. Это гарантирует, что эти тайлы не будут обработаны повторно.
    5. Возвращаем список всех созданных коллайдеров.

    ---
    
    :Args:
    - map: Объект TileMap с данными карты
    - accordance: Соответствие между материалами коллайдеров и материалами объектов
    - tile_size: Размер тайла в пикселях [width, height]
    - tile_scale: Масштаб тайлов

    ---
        
    :Returns:
        Список коллайдеров BoxCollider2D
    """
    colliders = []
    # Создаем глубокую копию данных карты для модификации в процессе
    map_data = [row[:] for row in map.data] 
    map_width, map_height = map.get_size()
    scaled_tile_width = tile_size[0] * tile_scale
    scaled_tile_height = tile_size[1] * tile_scale
    
    # Кэш для материалов тайлов, чтобы избежать повторных запросов к accordance
    material_cache = {}
    
    def get_tile_material_from_id(tile_id: int):
        """Вспомогательная функция для получения материала по ID с кэшированием."""
        if tile_id not in material_cache:
            try:
                material_cache[tile_id] = accordance.get_accordance(tile_id)
            except KeyError:
                # Если ID не найден в соответствии, можно вернуть дефолтный материал или выбросить ошибку
                # Здесь предполагается, что для всех ID, которые могут быть в карте, есть соответствие.
                # Если нет, то можно, например, вернуть ColliderMaterial("default") или ColliderMaterial(name=f"unknown_{tile_id}")
                # Для данного контекста, просто возвращаем заглушку, чтобы код выполнялся.
                material_cache[tile_id] = ColliderMaterial() # Заглушка, так как класс ColliderMaterial не предоставлен
        return material_cache[tile_id]
    
    for y in range(map_height):
        for x in range(map_width):
            tile_id = map_data[y][x]
            
            # Если тайл пустой (0) или уже был "покрыт" другим коллайдером
            if tile_id == 0:
                continue
            
            # Получаем базовый материал для текущего тайла
            base_material = get_tile_material_from_id(tile_id)
            
            # 1. Определяем максимально возможную ширину прямоугольника (current_max_width)
            current_max_width = 0
            for w in range(x, map_width):
                # Проверяем, что тайл не 0 и его материал совпадает с базовым
                if map_data[y][w] == 0 or get_tile_material_from_id(map_data[y][w]) != base_material:
                    break
                current_max_width += 1
            
            # Если ширина 0, это означает ошибку или уже обработанный тайл, который не был обнулен
            if current_max_width == 0: 
                continue

            # 2. Определяем максимально возможную высоту для найденной ширины (max_rect_height)
            max_rect_height = 0
            for h in range(y, map_height):
                is_row_valid = True
                for w_check in range(x, x + current_max_width):
                    # Проверяем, что все тайлы в текущей строке (в пределах current_max_width)
                    # не 0 и имеют тот же базовый материал
                    if map_data[h][w_check] == 0 or get_tile_material_from_id(map_data[h][w_check]) != base_material:
                        is_row_valid = False
                        break
                if not is_row_valid:
                    break
                max_rect_height += 1
            
            # Создаем коллайдер на основе найденного прямоугольника
            collider_width = current_max_width * scaled_tile_width
            collider_height = max_rect_height * scaled_tile_height
            
            collider = BoxCollider2D(
                width=collider_width,
                height=collider_height,
                material=base_material,  # Используем полученный материал
                type=ColliderType.STATIC
            )
            collider.set_position(
                x * scaled_tile_width + offset_x,
                y * scaled_tile_height + offset_y
            )
            colliders.append(collider)
            
            # Обнуляем (помечаем как использованные) все тайлы, покрытые этим новым коллайдером
            for ry in range(y, y + max_rect_height):
                for rx in range(x, x + current_max_width):
                    map_data[ry][rx] = 0
                    
    return colliders

