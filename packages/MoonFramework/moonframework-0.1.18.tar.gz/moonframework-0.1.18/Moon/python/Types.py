from typing_extensions import Sequence
from Moon.python.Colors import Color
from enum import Enum, auto
from typing import NoReturn, Optional, Callable, TypeAlias, Union, overload, Self, Literal, Final, Generic
from uuid import uuid4

# Тип обозначающий функцию или метод == +
type FunctionOrMethod = Callable        #
# ===================================== +

# Тип числового значения (int или float) == +
type Number = int | float                   #
# ========================================= +

# Тип опционального числового значения == +
type OptionalNumber = Optional[Number]    #
# ======================================= +

# Тип обозначающий список из двух чисел (int или float) ==== +
type TwoNumberList = Sequence[Number] | tuple[Number, Number]    #
# ========================================================== +

# Тип обозначающий список из двух целых чисел ====== +
type TwoIntegerList = list[int] | tuple[int, int]    #
# ================================================== +

# Тип обозначающий список из двух дробных чисел ======== +
type TwoFloatList = list[float] | tuple[float, float]    #
# ====================================================== +

# Тип обозначающий список из трех чисел (int или float) =============== +
type ThreeNumbersList = list[Number] | tuple[Number, Number, Number]    #
# ===================================================================== +

# Тип обозначающий список из четырех чисел (int или float) =================== +
type FourNumbersList = list[Number] | tuple[Number, Number, Number, Number]    #
# ============================================================================ +

# Тип обозначающий любое значение которое можно имплементировать как цвет == +
type ColorType = Color | ThreeNumbersList                                    #
# ========================================================================== +

# Тип идентификаторного значения ======= +
type Identifier =           int | str    #
# ====================================== +

# Тип опционального идентификатора ================ +
type OptionalIdentifier =   Optional[Identifier]    #
# ================================================= +


def AutoIdentifier() -> Identifier:
    """
    #### Генерирует уникальный идентификатор.

    ---

    :Returns:
    - идентификатор
    """
    return str(uuid4())

class OriginTypes(Enum):
    TOP_CENTER =        auto()
    DOWN_CENTER =       auto()
    LEFT_CENTER =       auto()
    RIGHT_CENTER =      auto()
    CENTER =            auto()
    TOP_LEFT =          auto()
    TOP_RIGHT =         auto()
    DOWN_LEFT =         auto()
    DOWN_RIGHT =        auto()
