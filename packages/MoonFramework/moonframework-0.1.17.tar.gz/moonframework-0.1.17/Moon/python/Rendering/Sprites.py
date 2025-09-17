
from copy import copy
import time

from .Shapes import BaseLineShape, LineShape
from .RenderStates import RenderStates
from .Shaders import *

from ..Time import TIMER_BUFFER, Timer, wait_call
from ..Views import View
from ..Types import *
from ..Colors import *

from ..utils import find_library, LibraryLoadError
import ctypes

# Загружаем DLL библиотеку
try:
    LIB_MOON = ctypes.CDLL(find_library())
except Exception as e:
    raise ImportError(f"Failed to load PySGL library: {e}")

# Определение типов аргументов и возвращаемых значений для функций библиотеки
LIB_MOON._RenderTexture_Init.argtypes = None
LIB_MOON._RenderTexture_Init.restype = ctypes.c_void_p
LIB_MOON._RenderTexture_Create.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
LIB_MOON._RenderTexture_Create.restype = ctypes.c_bool
LIB_MOON._RenderTexture_Draw.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._RenderTexture_Draw.restype = None
LIB_MOON._RenderTexture_Clear.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON._RenderTexture_Clear.restype = None
LIB_MOON._RenderTexture_Display.argtypes = [ctypes.c_void_p]
LIB_MOON._RenderTexture_Display.restype = None
LIB_MOON._RenderTexture_SetSmooth.argtypes = [ctypes.c_void_p, ctypes.c_bool]
LIB_MOON._RenderTexture_SetSmooth.restype = None
LIB_MOON._RenderTexture_DrawWithStates.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._RenderTexture_DrawWithStates.restype = None
LIB_MOON._RenderTexture_DrawWithShader.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._RenderTexture_DrawWithShader.restype = None
LIB_MOON._RenderTexture_SetView.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._RenderTexture_SetView.restype = None
LIB_MOON._RenderTexture_GetView.argtypes = [ctypes.c_void_p]
LIB_MOON._RenderTexture_GetView.restype = ctypes.c_void_p
LIB_MOON._RenderTexture_GetDefaultView.argtypes = [ctypes.c_void_p]
LIB_MOON._RenderTexture_GetDefaultView.restype = ctypes.c_void_p
LIB_MOON._RenderTexture_GetTexture.argtypes = [ctypes.c_void_p]
LIB_MOON._RenderTexture_GetTexture.restype = ctypes.c_void_p
LIB_MOON._RenderTexture_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._RenderTexture_Delete.restype = None

# Тип указателя на RenderTexture ========= +
type RenderTexturePtr = ctypes.c_void_p    #
# ======================================== +

class RenderTexture:
    """
    Класс для работы с текстурой рендеринга (off-screen rendering)
    Позволяет рисовать на текстуре, которая затем может быть использована как спрайт
    """
    def __init__(self):
        """Инициализирует новую текстуру рендеринга"""
        self._ptr = LIB_MOON._RenderTexture_Init()
        self.__width: None | int = None
        self.__height: None | int = None
        self.__smooth: bool = False

    def delete(self):
        """Удаляет текстуру рендеринга"""
        LIB_MOON._RenderTexture_Delete(self._ptr)

    def __del__(self):
        self.delete()

    def create(self, width: int, height: int) -> "RenderTexture":
        """
        Создает текстуру рендеринга заданного размера
        
        Args:
            width: Ширина текстуры в пикселях
            height: Высота текстуры в пикселях
            
        Returns:
            Возвращает self для цепочки вызовов
            
        Raises:
            Exception: Если не удалось создать текстуру
        """
        if LIB_MOON._RenderTexture_Create(self._ptr, width, height):
            self.__width = width
            self.__height = height
        else:
            raise ValueError("Render texture is not created.")
        return self
    
    def get_texture(self) -> "Texture":
        """Возвращает объект текстуры, связанный с текстурой рендеринга"""
        texture = Texture()
        texture.set_ptr(LIB_MOON._RenderTexture_GetTexture(self._ptr))
        return texture

    def get_ptr(self) -> RenderTexturePtr:
        """Возвращает указатель на нативную текстуру рендеринга"""
        return self._ptr
    
    @overload
    def draw(self, shape, render_states: RenderStates):
        """Перегруженный метод для рисования с состояниями рендеринга"""
        ...

    @overload
    def draw(self, shape):
        """Перегруженный метод для рисования без дополнительных состояний"""
        ...
    
    def draw(self, shape, render_states: None | RenderStates | Shader = None):
        """
        Рисует объект на текстуре рендеринга
        
        Args:
            shape: Объект для рисования (спрайт, фигура и т.д.)
            render_states: Опциональные состояния рендеринга или шейдер
                          Если None - используется стандартный рендеринг
                          Если RenderStates - применяются указанные состояния
                          Если Shader - применяется указанный шейдер
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
                LIB_MOON._RenderTexture_Draw(self._ptr, shape.get_ptr())
            elif isinstance(render_states, RenderStates):
                LIB_MOON._RenderTexture_DrawWithStates(self._ptr, shape.get_ptr(), render_states.get_ptr())
            elif isinstance(render_states, Shader):
                LIB_MOON._RenderTexture_DrawWithShader(self._ptr, shape.get_ptr(), render_states.get_ptr())

    def clear(self, color: Color = COLOR_WHITE):
        """
        Очищает текстуру рендеринга указанным цветом
        
        Args:
            color: Цвет очистки (по умолчанию белый)
        """
        LIB_MOON._RenderTexture_Clear(self._ptr, color.r, color.g, color.b, color.r)

    def display(self):
        """Обновляет текстуру рендеринга (финализирует отрисовку)"""
        LIB_MOON._RenderTexture_Display(self._ptr)

    def set_smooth(self, smooth: bool = False):
        """
        Включает или выключает сглаживание текстуры
        
        Args:
            smooth: Если True - включает сглаживание, False - выключает
        """
        LIB_MOON._RenderTexture_SetSmooth(self._ptr, smooth)
        self.__smooth = smooth

    def get_smooth(self) -> bool:
        """Возвращает True если сглаживание включено, иначе False"""
        return self.__smooth
    
    def get_size(self) -> tuple[int | None, int | None]:
        """Возвращает размеры текстуры рендеринга в виде кортежа (ширина, высота)"""
        return (self.__width, self.__height)
    
    def set_view(self, view: View):
        """Устанавливает вид (камеру) для рендеринга"""
        LIB_MOON._RenderTexture_SetView(self._ptr, view.get_ptr())

    def get_default_view(self) -> View:
        """Возвращает вид по умолчанию для этой текстуры рендеринга"""
        return LIB_MOON._RenderTexture_GetDefaultView(self._ptr)
    
    def get_view(self) -> View:
        """Возвращает текущий активный вид текстуры рендеринга"""
        return LIB_MOON._RenderTexture_GetView(self._ptr)

# Определение функций для работы со спрайтами
LIB_MOON._Sprite_GetFromRenderTexture.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetFromRenderTexture.restype = ctypes.c_void_p

LIB_MOON._Sprite_GetFromTexture.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetFromTexture.restype = ctypes.c_void_p

LIB_MOON._Sprite_Scale.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._Sprite_Scale.restype = None
LIB_MOON._Sprite_Rotate.argtypes = [ctypes.c_void_p, ctypes.c_float]
LIB_MOON._Sprite_Rotate.restype = None
LIB_MOON._Sprite_SetColor.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON._Sprite_SetColor.restype = None
LIB_MOON._Sprite_SetOrigin.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._Sprite_SetOrigin.restype = None
LIB_MOON._Sprite_SetPosition.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._Sprite_SetPosition.restype = None
LIB_MOON._Sprite_SetRotation.argtypes = [ctypes.c_void_p, ctypes.c_float]
LIB_MOON._Sprite_SetRotation.restype = None
LIB_MOON._Sprite_SetScale.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
LIB_MOON._Sprite_SetScale.restype = None
LIB_MOON._Sprite_GetColorR.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetColorR.restype = ctypes.c_int
LIB_MOON._Sprite_GetColorG.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetColorG.restype = ctypes.c_int
LIB_MOON._Sprite_GetColorB.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetColorB.restype = ctypes.c_int
LIB_MOON._Sprite_GetColorA.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetColorA.restype = ctypes.c_int
LIB_MOON._Sprite_GetOriginX.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetOriginX.restype = ctypes.c_float
LIB_MOON._Sprite_GetOriginY.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetOriginY.restype = ctypes.c_float
LIB_MOON._Sprite_GetPositionX.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetPositionX.restype = ctypes.c_float
LIB_MOON._Sprite_GetPositionY.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetPositionY.restype = ctypes.c_float
LIB_MOON._Sprite_GetRotation.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetRotation.restype = ctypes.c_float
LIB_MOON._Sprite_GetScaleX.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetScaleX.restype = ctypes.c_float
LIB_MOON._Sprite_GetScaleY.argtypes = [ctypes.c_void_p]
LIB_MOON._Sprite_GetScaleY.restype = ctypes.c_float


# Определение функций для работы с текстурами
LIB_MOON._Texture_LoadFromFile.argtypes = [ctypes.c_char_p]
LIB_MOON._Texture_LoadFromFile.restype = ctypes.c_void_p
LIB_MOON._Texture_LoadFromFileWithBoundRect.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON._Texture_LoadFromFileWithBoundRect.restype = ctypes.c_void_p
LIB_MOON._Texture_GetMaxixmumSize.argtypes = [ctypes.c_void_p]
LIB_MOON._Texture_GetMaxixmumSize.restype = ctypes.c_int
LIB_MOON._Texture_GetSizeX.argtypes = [ctypes.c_void_p]
LIB_MOON._Texture_GetSizeX.restype = ctypes.c_int
LIB_MOON._Texture_GetSizeY.argtypes = [ctypes.c_void_p]
LIB_MOON._Texture_GetSizeY.restype = ctypes.c_int
LIB_MOON._Texture_SetRepeated.argtypes = [ctypes.c_void_p, ctypes.c_bool]
LIB_MOON._Texture_SetRepeated.restype = None
LIB_MOON._Texture_SetSmooth.argtypes = [ctypes.c_void_p, ctypes.c_bool]
LIB_MOON._Texture_SetSmooth.restype = None
LIB_MOON._Texture_Swap.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
LIB_MOON._Texture_Swap.restype = None
LIB_MOON._Texture_SubTexture.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB_MOON._Texture_SubTexture.restype = ctypes.c_void_p
LIB_MOON._Texture_Delete.argtypes = [ctypes.c_void_p]
LIB_MOON._Texture_Delete.restype = None

# Тип указателя на текстуру ========= +
TexturePtr = ctypes.c_void_p          #
# =================================== +


class Texture:
    """Класс для работы с текстурами (изображениями)"""
    def __init__(self):
        """Инициализирует новую текстуру"""
        self._ptr: TexturePtr | None = None
        self.__repeated: bool = False
        self.__smooth: bool = False

    def delete(self) -> None:
        """Удаляет текстуру"""
        if self._ptr is not None:
            LIB_MOON._Texture_Delete(self._ptr)
            self._ptr = None

    def  __del__(self):
        """Удаляет текстуру при удалении объекта"""
        self.delete()

    def set_ptr(self, ptr: TexturePtr) -> Self:
        """
        Устанавливает указатель на нативную текстуру
        
        Args:
            ptr: Указатель на текстуру
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self._ptr = ptr
        return self

    def get_ptr(self) -> TexturePtr | None:
        """Возвращает указатель на нативную текстуру"""
        return self._ptr
    
    @overload
    @classmethod
    def LoadFromFile(cls, file_path: str) -> Self:
        """Перегруженный метод для загрузки всей текстуры из файла"""
        ...

    @overload
    @classmethod
    def LoadFromFile(cls, file_path: str, position: TwoIntegerList, size: TwoIntegerList) -> Self:
        """Перегруженный метод для загрузки части текстуры из файла"""
        ...
    

    @classmethod
    def LoadFromFile(cls, arg1, arg2 = None, arg3 = None) -> "Texture":
        """
        Загружает текстуру из файла
        
        Варианты вызова:
        1. LoadFromFile(file_path) - загружает всю текстуру
        2. LoadFromFile(file_path, position, size) - загружает часть текстуры
        
        Args:
            file_path: Путь к файлу изображения
            position: Опционально - позиция (x,y) для загрузки части текстуры
            size: Опционально - размер (width,height) загружаемой части
            
        Returns:
            Новый объект Texture
            
        Raises:
            NotImplementedError: Если переданы неверные аргументы
        """
        if arg2 is None and arg3 is None:
            ptr = LIB_MOON._Texture_LoadFromFile(arg1.encode('utf-8'))
            t = Texture()
            return t.set_ptr(ptr)
        elif arg2 is not None and arg3 is not None:
            ptr = LIB_MOON._Texture_LoadFromFileWithBoundRect(arg1.encode('utf-8'),
                                                               arg2[0], arg2[1], arg3[0], arg3[1])
            t = Texture()
            return t.set_ptr(ptr)
        else:
            raise NotImplementedError("Invalid arguments!")
        
    def get_sub_texture(self, x: int, y: int, width: int, height: int) -> "Texture":
        """Возвращает новую текстуру, содержащую только часть исходной текстуры"""
        t = Texture()
        ptr = LIB_MOON._Texture_SubTexture(self._ptr, x, y, width, height)
        t.set_ptr(ptr)
        return t
    
    def get_max_size(self) -> int:
        """Возвращает максимально поддерживаемый размер текстуры"""
        return LIB_MOON._Texture_GetMaximumSize(self._ptr)
    
    def get_size(self) -> Vector2i:
        """Возвращает размер текстуры в виде Vector2i"""
        return Vector2i(
            LIB_MOON._Texture_GetSizeX(self._ptr),
            LIB_MOON._Texture_GetSizeY(self._ptr)
        )
    
    def set_repeated(self, value: bool) -> Self:
        """
        Устанавливает режим повторения текстуры
        
        Args:
            value: Если True - текстура будет повторяться при выходе за границы
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        LIB_MOON._Texture_SetRepeated(self._ptr, value)
        self.__repeated = value
        return self

    def get_repeated(self) -> bool:
        """Возвращает True если режим повторения включен, иначе False"""
        return self.__repeated
    
    def set_smooth(self, value: bool) -> Self:
        """
        Включает или выключает сглаживание текстуры
        
        Args:
            value: Если True - включает сглаживание
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        LIB_MOON._Texture_SetSmooth(self._ptr, value)
        self.__smooth = value
        return self

    def get_smooth(self) -> bool:
        """Возвращает True если сглаживание включено, иначе False"""
        return self.__smooth
    
    def swap(self, texture: "Texture") -> Self:
        """
        Меняет местами данные текущей текстуры с другой
        
        Args:
            texture: Текстура для обмена
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        LIB_MOON._Texture_Swap(self._ptr, texture.get_ptr())
        return self


# Тип указателя на базовый спрайт === +       
BaseSpritePtr = ctypes.c_void_p       #
# =================================== +


class BaseSprite:
    """Базовый класс для работы со спрайтами (2D изображениями)"""
    def __init__(self):
        """Инициализирует новый спрайт"""

        # =================================================================================================================
        self._ptr:                      BaseSpritePtr | None = None                                    # Указатель в памяти
        self.__texture:                 Texture | None = None                # Текстура `не поддерживающая рендеринг на нее`
        self.__render_texture:          RenderTexture | None = None                                  # Текстура для рендера
        self.__scale:                   Vector2f = Vector2f(1, 1)       # Масштаб изображения { не нативная трансформация }

        self.__flip_x:                  bool = False                                        # Флаг отражения по горизонтали
        self.__flip_y:                  bool = False                                          # Флаг отражения по вертикали

        self.__typed_origin:            OriginTypes = OriginTypes.TOP_LEFT                              # Тип точки отсчета
        self.__origin_padding:          Vector2f = Vector2f.zero()                  # Дополнительное смещение точки отсчета
        # =================================================================================================================

    def get_flip_x(self) -> bool:
        return self.__flip_x
    
    def get_flip_y(self) ->  bool:
        return self.__flip_y

    def copy(self) -> "BaseSprite":
        new = BaseSprite.FromTexture(self.__texture)
        new.set_angle(self.get_angle())
        new.set_scale_xy(*self.get_scale().xy)
        new.set_origin(self.get_origin())
        new.set_color(self.get_color())
        new.set_flip_x(self.get_flip_x())
        new.set_flip_y(self.get_flip_y())
        new.set_origin_padding_x(self.get_origin_padding().x)
        new.set_origin_padding_y(self.get_origin_padding().y)
        new.set_typed_origin(self.get_origin_type())
        return new

    def set_origin_padding(self, padding: Number):
        """
        Устанавливает одинаковое смещение для точки отсчета по обеим осям
        
        Args:
            padding: Величина смещения
        """
        self.__origin_padding.x = padding
        self.__origin_padding.y = padding



    def set_origin_padding_y(self, padding: Number):
        """
        Устанавливает смещение точки отсчета по оси Y
        
        Args:
            padding: Величина смещения
        """
        self.__origin_padding.y = padding



    def set_origin_padding_x(self, padding: Number):
        """
        Устанавливает смещение точки отсчета по оси X
        
        Args:
            padding: Величина смещения
        """
        self.__origin_padding.x = padding



    def get_origin_padding(self) -> Vector2f:
        """Возвращает текущее смещение точки отсчета в виде Vector2f"""
        return self.__origin_padding
    


    def get_origin_type(self) -> OriginTypes:
        """Возвращает текущий тип точки отсчета"""
        return self.__typed_origin
    


    def set_typed_origin(self, origin_type: OriginTypes):
        """
        Устанавливает точку отсчета (origin) спрайта на основе предопределенного типа выравнивания.
        Точка отсчета определяет, какая часть спрайта будет использоваться как "якорь" для всех трансформаций
        (позиционирования, вращения, масштабирования).
        
        Позволяет быстро установить стандартные точки выравнивания без ручного расчета координат.
        Учитывает дополнительное смещение (padding), которое добавляется к выбранной позиции.
        
        Args:
            origin_type (OriginTypes): Тип точки отсчета из перечисления OriginTypes:
                - CENTER: Центр спрайта
                - TOP_CENTER: Верхний центр
                - DOWN_CENTER: Нижний центр
                - LEFT_CENTER: Центр левой стороны
                - RIGHT_CENTER: Центр правой стороны
                - TOP_LEFT: Левый верхний угол (по умолчанию)
                - TOP_RIGHT: Правый верхний угол
                - DOWN_LEFT: Левый нижний угол
                - DOWN_RIGHT: Правый нижний угол
        
        Raises:
            TypeError: Если передан недопустимый тип точки отсчета
        
        """
        self.__typed_origin = origin_type

        size = self.get_size()
        if size is not None: 
            width, height = size
            match (self.__typed_origin):
                case OriginTypes.CENTER:
                    self.set_origin((width / 2 + self.__origin_padding.x), (height / 2 + self.__origin_padding.y))
                # =================================================================================================
                case OriginTypes.TOP_CENTER:
                    self.set_origin((width / 2 + self.__origin_padding.x), (0 + self.__origin_padding.y))
                case OriginTypes.DOWN_CENTER:
                    self.set_origin((width / 2 + self.__origin_padding.x), (height + self.__origin_padding.y))
                case OriginTypes.LEFT_CENTER:
                    self.set_origin((0 + self.__origin_padding.x), (height / 2 + self.__origin_padding.y))
                case OriginTypes.RIGHT_CENTER:
                    self.set_origin((width + self.__origin_padding.x), (height / 2 + self.__origin_padding.y))
                # =================================================================================================
                case OriginTypes.TOP_LEFT:
                    self.set_origin((0 + self.__origin_padding.x), (0 + self.__origin_padding.y))
                case OriginTypes.TOP_RIGHT:
                    self.set_origin((width + self.__origin_padding.x), (0 + self.__origin_padding.y))
                case OriginTypes.DOWN_LEFT:
                    self.set_origin((0 + self.__origin_padding.x), (height + self.__origin_padding.y))
                case OriginTypes.DOWN_RIGHT:
                    self.set_origin((width + self.__origin_padding.x), (height + self.__origin_padding.y))
                case _:
                    raise TypeError("Invalid origin type!")
            # =================================================================================================
        else:
            raise TypeError("Size is not matched!")



    def set_texture(self, texture: Texture) -> Self:
        """
        Устанавливает текстуру для спрайта
        
        Args:
            texture: Объект Texture
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__texture = texture
        return self



    def get_texture(self) -> Texture | None:
        """Возвращает текущую текстуру спрайта"""
        return self.__texture
    


    def set_render_texture(self, render_texture: RenderTexture) -> Self:
        """
        Устанавливает текстуру рендеринга для спрайта
        
        Args:
            render_texture: Объект RenderTexture
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__render_texture = render_texture
        return self



    def get_render_texture(self) -> RenderTexture | None:
        """Возвращает текущую текстуру рендеринга спрайта"""
        return self.__render_texture


    # ===================================================================================== +
    # [            Специальные методы для быстрой генерации спрайта из текстур              ]
    # {     !!! Категорически не советуется тут ничего трогать если вы не сеньёр !!!        }
    # ===================================================================================== +
    @classmethod                                                                            #
    def FromRenderTexture(cls, render_texture: RenderTexture) -> 'BaseSprite':              #
        """                                                                                 #
        Создает спрайт из текстуры рендеринга                                               #
                                                                                            #
        Args:                                                                               #
            render_texture: Текстура рендеринга                                             #
                                                                                            #
        Returns:                                                                            #
            Новый объект BaseSprite                                                         #
        """                                                                                 #
        ptr = LIB_MOON._Sprite_GetFromRenderTexture(render_texture.get_ptr())              #
        bs = BaseSprite()                                                                   #
        bs.set_render_texture(render_texture)                                               #
        return bs.set_ptr(ptr)                                                              #
                                                                                            #
                                                                                            #
    @classmethod                                                                            #
    def FromTexture(cls, texture: Texture) -> 'BaseSprite':                                 #
        """                                                                                 #
        Создает спрайт из обычной текстуры                                                  #
                                                                                            #
        Args:                                                                               #
            texture: Текстура изображения                                                   #
                                                                                            #
        Returns:                                                                            #
            Новый объект BaseSprite                                                         #
        """                                                                                 #
        ptr = LIB_MOON._Sprite_GetFromTexture(texture.get_ptr())                           #
        bs = BaseSprite()                                                                   #
        bs.set_texture(texture)                                                             #
        return bs.set_ptr(ptr)                                                              #
    # ===================================================================================== +


    def set_ptr(self, ptr: BaseSpritePtr) -> Self:
        """
        Устанавливает указатель на нативный спрайт
        
        Args:
            ptr: Указатель на спрайт
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self._ptr = ptr
        return self



    def get_ptr(self) -> BaseSpritePtr | None:
        """Возвращает указатель на нативный спрайт"""
        return self._ptr
    


    def set_scale(self, scale: Number) -> Self:
        """
        Устанавливает масштаб спрайта (одинаковый по обеим осям)
        
        Args:
            scale: Коэффициент масштабирования
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        LIB_MOON._Sprite_SetScale(self._ptr, float(scale), float(scale))
        self.__scale.x = scale
        self.__scale.y = scale
        return self
    


    def update_scale(self) -> Self:
        """
        Обновляет масштаб спрайта (применяет текущие значения __scale)
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        LIB_MOON._Sprite_SetScale(self._ptr, self.__scale.y, self.__scale.x)
        return self



    def set_scale_xy(self, scale_x: OptionalNumber = None, scale_y: OptionalNumber = None) -> Self:
        """
        Устанавливает масштаб спрайта по осям независимо
        
        Args:
            scale_x: Опционально - масштаб по X
            scale_y: Опционально - масштаб по Y
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        if scale_x is not None:
            self.__scale.x = scale_x
        if scale_y is not None:
            self.__scale.y = scale_y

        LIB_MOON._Sprite_SetScale(self._ptr, self.__scale.y, self.__scale.x)
        
        return self



    def rotate(self, angle: Number) -> Self:
        """
        Поворачивает спрайт на указанный угол (в градусах)
        
        Args:
            angle: Угол поворота
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        LIB_MOON._Sprite_Rotate(self._ptr, angle)
        return self
    


    def set_color(self, color: Color) -> Self:
        """
        Устанавливает цвет спрайта (умножается на текстуру)
        
        Args:
            color: Цвет (объект Color)
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        LIB_MOON._Sprite_SetColor(self._ptr, color.r, color.g, color.b, color.a)
        return self
    


    @overload
    def set_origin(self, origin: Vector2f) -> Self:
        """
        Устанавливает точку отсчета спрайта
        
        Args:
            origin: Вектор координаты точки отсчета
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        ...

    @overload
    def set_origin(self, x: Number, y: Number) -> Self:
        """
        Устанавливает точку отсчета спрайта
        
        Args:
            x: Координата X точки отсчета
            y: Координата Y точки отсчета
            
        Returns:
            Возвращает self для цепочки вызовов
        """

    def set_origin(self, arg1, arg2 = None) -> Self:
        """
        Устанавливает точку отсчета спрайта
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        if arg2 is None and isinstance(arg1, Vector2f):
            LIB_MOON._Sprite_SetOrigin(self._ptr, arg1.x, arg1.y)
        elif arg2 is not None and (type(arg1) in [int, float] and type(arg2) in [int, float]):
            LIB_MOON._Sprite_SetOrigin(self._ptr, arg1, arg2)
        return self
    


    @overload
    def set_position(self, position: Vector2f) -> Self:
        """
        Устанавливает позицию спрайта
        
        Args:
            position: Вектор позиции
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        ...
    
    @overload
    def set_position(self, x: Number, y: Number) -> Self:
        """
        Устанавливает позицию спрайта
        
        Args:
            x: Координата X
            y: Координата Y
            
        Returns:
            Возвращает self для цепочки вызовов
        """

    def set_position(self, arg1, arg2 = None) -> Self:
        """
        Устанавливает позицию спрайта
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        if arg2 is None and isinstance(arg1, Vector2f):
            LIB_MOON._Sprite_SetPosition(self._ptr, arg1.x, arg1.y)
        elif arg2 is not None and (type(arg1) in [int, float] and type(arg2) in [int, float]):
            LIB_MOON._Sprite_SetPosition(self._ptr, arg1, arg2)
        else:
            raise TypeError("Invalid arguments!")
        return self
    


    def set_angle(self, angle: Number) -> Self:
        """
        Устанавливает угол поворота спрайта (в градусах)
        
        Args:
            angle: Угол поворота
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        LIB_MOON._Sprite_SetRotation(self._ptr, angle)
        return self
    


    def get_color(self) -> Color:
        """Возвращает текущий цвет спрайта"""
        return Color(
            LIB_MOON._Sprite_GetColorR(self._ptr),
            LIB_MOON._Sprite_GetColorG(self._ptr),
            LIB_MOON._Sprite_GetColorB(self._ptr),
            LIB_MOON._Sprite_GetColorA(self._ptr)
        )



    def get_origin(self) -> Vector2f:
        """Возвращает текущую точку отсчета спрайта"""
        return Vector2f(
            LIB_MOON._Sprite_GetOriginX(self._ptr),
            LIB_MOON._Sprite_GetOriginY(self._ptr)
        )



    def get_position(self) -> Vector2f:
        """Возвращает текущую позицию спрайта"""
        return Vector2f(
            LIB_MOON._Sprite_GetPositionX(self._ptr),
            LIB_MOON._Sprite_GetPositionY(self._ptr)
        )



    def get_angle(self) -> Number:
        """Возвращает текущий угол поворота спрайта (в градусах)"""
        return LIB_MOON._Sprite_GetRotation(self._ptr)



    def get_scale(self) -> Vector2f:
        """Возвращает текущий масштаб спрайта"""
        return Vector2f(
            LIB_MOON._Sprite_GetScaleX(self._ptr),
            LIB_MOON._Sprite_GetScaleY(self._ptr)
        )
    


    def get_at_size(self) -> Optional[Vector2f]:
        """Возвращает размер спрайта с учетом текущего масштаба"""
        if self.__texture is not None:
            size = self.__texture.get_size()
            return Vector2f(abs(size.x * self.__scale.x), abs(size.y * self.__scale.y))
        else:
            return None
        
    


    def get_size(self) -> Optional[Vector2f]:
        """Возвращает исходный размер спрайта (без учета масштаба)"""
        if self.__texture is not None:
            return self.__texture.get_size().to_float()
        else:
            return None
    


    def set_flip_x(self, value: bool = False) -> Self:
        """
        Устанавливает отражение спрайта по горизонтали
        
        Args:
            value: Если True - отражает спрайт
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__flip_x = value
        if self.__flip_x == True and self.__scale.x > 0:
            self.__scale.x = -self.__scale.x
        if self.__flip_x == False and self.__scale.x < 0:
            self.__scale.x = -self.__scale.x

        self.update_scale()
        return self



    def set_flip_y(self, value: bool = False) -> Self:
        """
        Устанавливает отражение спрайта по вертикали
        
        Args:
            value: Если True - отражает спрайт
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__flip_y = value
        if self.__flip_y == True and self.__scale.y > 0:
            self.__scale.y = -self.__scale.y
        if self.__flip_y == False and self.__scale.y < 0:
            self.__scale.y = -self.__scale.y

        self.update_scale()
        return self
    


    def flip_x(self) -> Self:
        """
        Переключает отражение спрайта по горизонтали (инвертирует текущее состояние)
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__scale.x = -self.__scale.x
        self.update_scale()
        return self



    def flip_y(self) -> Self:
        """
        Переключает отражение спрайта по вертикали (инвертирует текущее состояние)
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__scale.y = -self.__scale.y
        self.update_scale()
        return self
         

def LoadSprite(file_path: str, scale: Number = 1) -> BaseSprite:
    """
    Вспомогательная функция для быстрой загрузки спрайта из файла
    
    Args:
        file_path: Путь к файлу изображения
        scale: Масштаб спрайта (по умолчанию 1)
        
    Returns:
        Новый объект BaseSprite
    """
    texture = Texture.LoadFromFile(file_path)
    sprite = BaseSprite.FromTexture(texture)
    sprite.set_scale(scale)
    return sprite




# Тип для хранения массива спрайтов ============================= +
type SpriteArray = list[BaseSprite] | tuple[BaseSprite, ...]      #
# =============================================================== +

# Тип для хранения массива текстур ============================== +
type TextureArray = list[Texture] | tuple[Texture, ...]           #
# =============================================================== +

# Методы для загрузки массива спрайтов =========================================================================== +
def LoadSpriteArrayFromSpritePath(path_template: str, count: int, scale: Number = 1) -> SpriteArray:
    sprites = []
    for i in range(count):
        file_path = path_template.format(i + 1)
        sprites.append(LoadSprite(file_path, scale))
    return sprites
        
def LoadSpriteArrayFromSprite(path: str, one_sprite_size: TwoIntegerList, scale: Number = 1) ->  SpriteArray:
    full_texture = Texture.LoadFromFile(path)
    full_texture_size = full_texture.get_size()

    if full_texture_size.x % one_sprite_size[0] != 0:
        raise TypeError("Ivalid sprite sheet size!")
    
    sprite_array =  []
    for i in range(full_texture_size.x // one_sprite_size[0]):
        texture = Texture.LoadFromFile(path, [i * one_sprite_size[0], 0], one_sprite_size)
        sprite = BaseSprite.FromTexture(texture)
        sprite.set_scale(scale)
        sprite_array.append(sprite)

    return sprite_array
# Методы для загрузки массива спрайтов =========================================================================== +




SPRITE_ANIMATION_COUNTER: int = 0  # Глобальный счетчик для идентификации таймеров анимаций

class SpriteAnimation:
    """
    Класс для управления анимациями на основе спрайтов.
    Позволяет проигрывать последовательности спрайтов с разными типами анимации.
    """

    def __init__(self):
        """Инициализирует новую анимацию с параметрами по умолчанию"""
        self.__frames: SpriteArray = []          # Массив кадров анимации (спрайтов)
        self.__frames_count: int = 0             # Общее количество кадров
        self.__frame_index: int = 0              # Текущий индекс кадра

        self.__timer_index: None | int = None    # Идентификатор таймера
        self.__time_between_frames: float = 0.1  # Время между сменой кадров (в секундах)

        # Тип анимации: 
        # 'none' - однократное проигрывание
        # 'loop' - зацикленная
        # 'elastic' - "туда-обратно"
        self.__animation_type: Literal['none', 'loop', 'elastic'] = 'none'  
        self.__elastic_direction: int = 1        # Направление для elastic-анимации (1 или -1)
        self.__started: bool = False             # Флаг активности анимации

        # Параметры трансформации для всех кадров
        self.__position: Vector2f = Vector2f.zero()  # Позиция анимации
        self.__scale: Vector2f = Vector2f.one()      # Масштаб
        self.__origin: Vector2f = Vector2f.zero()    # Точка отсчета
        self.__use_typed_origin: bool = False        # Использовать предопределенные точки отсчета
        self.__angle: Number = 0                     # Угол поворота
        self.__typed_origin: OriginTypes | None = None  # Тип точки отсчета
        self.__color: Color | None = None            # Цвет анимации
        self.__flip_x: bool = False
        self.__flip_y: bool = False

        self.__play_time: float = 0
        self.__start_time: float = 0
        self.__finish: bool = False

    def get_frames(self) -> SpriteArray:
        """
        Возвращает массив кадров анимации

        Returns:
            Массив кадров анимации
        """
        return self.__frames

    def set_start_frame_index(self, index: int) -> Self:
        self.__frame_index = index
        return self

    def set_color(self, color: Color) -> Self:
        """
        Устанавливает цвет для всех кадров анимации
        
        Args:
            color: Цвет (объект Color)
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__color = color
        return self

    def get_color(self) -> Color:
        """
        Возвращает текущий цвет анимации
        
        Returns:
            Объект Color или None, если цвет не установлен
        """
        return self.__color

    def copy(self) -> "SpriteAnimation":
        """
        Создает глубокую копию анимации
        
        Returns:
            Новый объект SpriteAnimation с теми же параметрами
        """
        new_frames = []
        for frame in self.__frames:
            new_frames.append(frame.copy())
        anim = SpriteAnimation().set_frames(new_frames)
        anim.set_scale_xy(self.__scale.x, self.__scale.y)
        if self.__typed_origin is not None:
            anim.set_origin_type(self.__typed_origin)
        else:
            anim.set_origin(self.__origin)
        anim.set_angle(self.__angle)
        anim.set_time_between_frames(self.__time_between_frames)
        anim.set_animation_type(self.__animation_type)
        return anim

    def start(self) -> Self:
        """
        Запускает анимацию
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__start_time = time.time()
        self.__started = True
        self.__finish = False
        return self
    
    def stop(self) -> Self:
        """
        Останавливает анимацию
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__play_time = 0
        self.__started = False
        return self
    
    def restart(self) -> Self:
        """
        Перезапускает анимацию с первого кадра
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__started = True
        self.__frame_index = 0
        return self

    def get_ptr(self) -> Self:
        """
        Возвращает указатель на себя (для совместимости)
        
        Returns:
            Сам объект анимации
        """
        return self

    def update_frames(self):
        """
        Обновляет все кадры анимации (позицию, масштаб, угол и другие параметры)
        """
        for i in range(self.__frames_count):
            self.update_frame(i)
            
    def update_frame(self, index: int) -> None:
        """
        Обновляет параметры конкретного кадра
        
        Args:
            index: Индекс кадра для обновления
        """
        self.__frames[index].set_position(self.__position)
        self.__frames[index].set_scale_xy(*self.__scale.xy)
        self.__frames[index].set_angle(self.__angle)
        self.__frames[index].set_flip_x(self.__flip_y)
        self.__frames[index].set_flip_y(self.__flip_x)
        if self.__color is not None:
            self.__frames[index].set_color(self.__color)
        if not self.__use_typed_origin:
            self.__frames[index].set_origin(self.__origin)
        else:
            self.__frames[index].set_typed_origin(self.__typed_origin)

    def set_angle(self, angle: Number) -> Self:
        """
        Устанавливает угол поворота для всех кадров
        
        Args:
            angle: Угол в градусах
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__angle = angle
        return self
    
    def set_scale(self, scale: Number) -> Self:
        """
        Устанавливает одинаковый масштаб по осям X и Y
        
        Args:
            scale: Коэффициент масштабирования
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__scale.x = scale
        self.__scale.y = scale
        return self

    def set_scale_xy(self, scale_x: OptionalNumber = None, scale_y: OptionalNumber = None) -> Self:
        """
        Устанавливает масштаб отдельно для каждой оси
        
        Args:
            scale_x: Масштаб по X (опционально)
            scale_y: Масштаб по Y (опционально)
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        if scale_x is not None:
            self.__scale.x = scale_x
        if scale_y is not None:
            self.__scale.y = scale_y
        return self
        
    @overload
    def set_position(self, position: Vector2f) -> Self:
        """
        Устанавливает позицию анимации (перегрузка для Vector2f)
        
        Args:
            position: Вектор позиции
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        ...
    
    @overload
    def set_position(self, x: Number, y: Number) -> Self:
        """
        Устанавливает позицию анимации (перегрузка для отдельных координат)
        
        Args:
            x: Координата X
            y: Координата Y
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        ...
    
    def set_position(self, arg1: Union[Number, Vector2f], arg2: Union[Number, None] = None) -> Self:
        """
        Устанавливает позицию анимации (основная реализация)
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        if arg2 is None and isinstance(arg1, Vector2f):
            self.__position = arg1
        elif arg2 is not None and (type(arg1) in [int, float] and type(arg2) in [int, float]):
            self.__position = Vector2f(arg1, arg2)
        else:
            raise TypeError("Invalid arguments!")
        return self

    def set_origin_type(self, type: OriginTypes) -> Self:
        """
        Устанавливает тип точки отсчета для всех кадров
        
        Args:
            type: Тип из перечисления OriginTypes
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__use_typed_origin = True
        self.__typed_origin = type
        return self

    @overload
    def set_origin(self, origin: Vector2f) -> Self:
        """
        Устанавливает точку отсчета (перегрузка для Vector2f)
        
        Args:
            origin: Вектор точки отсчета
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        ...
    
    @overload
    def set_origin(self, x: Number, y: Number) -> Self:
        """
        Устанавливает точку отсчета (перегрузка для координат)
        
        Args:
            x: Координата X точки отсчета
            y: Координата Y точки отсчета
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        ...
    
    def set_origin(self, arg1: Union[Number, Vector2f], arg2: Union[Number, None] = None) -> Self:
        """
        Устанавливает точку отсчета (основная реализация)
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        if arg2 is None and isinstance(arg1, Vector2f):
            self.__origin = arg1
        elif arg2 is not None and (type(arg1) in [int, float] and type(arg2) in [int, float]):
            self.__origin.x = arg1
            self.__origin.y = arg2
        else:
            raise TypeError("Invalid arguments!")
        return self

    def get_position(self) -> Vector2f:
        """Возвращает текущую позицию анимации"""
        return self.__position
    
    def get_scale(self) -> Vector2f:
        """Возвращает текущий масштаб анимации"""
        return self.__scale
    
    def get_origin(self) -> Vector2f:
        """Возвращает текущую точку отсчета анимации"""
        return self.__origin
    
    def get_angle(self) -> Number:
        """Возвращает текущий угол поворота анимации"""
        return self.__angle

    def set_animation_type(self, value: Literal['none', 'elastic', 'loop']) -> Self:
        """
        Устанавливает тип анимации
        
        Args:
            value: Тип анимации ('none', 'elastic' или 'loop')
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__animation_type = value
        return self
        
    def get_animation_type(self) -> Literal['none', 'elastic', 'loop']:
        """Возвращает текущий тип анимации"""
        return self.__animation_type

    def get_frames_count(self) -> int:
        """Возвращает количество кадров в анимации"""
        return self.__frames_count

    def set_frames(self, frames: SpriteArray) -> Self:
        """
        Устанавливает кадры для анимации
        
        Args:
            frames: Массив спрайтов
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__frames = frames
        self.__frames_count = len(self.__frames)
        return self

    def get_frames(self) -> SpriteArray:
        """Возвращает массив кадров анимации"""
        return self.__frames

    def set_time_between_frames(self, time: float) -> Self:
        """
        Устанавливает время между сменой кадров
        
        Args:
            time: Время в секундах
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__time_between_frames = time
        return self
    
    def get_time_between_frames(self) -> float:
        """Возвращает текущее время между кадрами"""
        return self.__time_between_frames

    def _update_animation(self):
        """
        Внутренний метод для обновления текущего кадра анимации
        в зависимости от типа анимации
        """
        self.__frame_index += self.__elastic_direction
        
        if self.__frame_index == self.__frames_count:
            if self.__animation_type == 'loop':
                self.__frame_index = 0
                return
            elif self.__animation_type == 'none':
                self.__frame_index -= 1
                self.stop()
                return
            elif self.__animation_type == 'elastic':
                
                self.__elastic_direction = -1
                self.__frame_index -= 2
                return
                
        if self.__animation_type == 'elastic':
            if self.__frame_index == 0:
                self.__elastic_direction = 1
        
    def update(self):
        """
        Обновляет анимацию (должен вызываться каждый кадр)
        Обрабатывает смену кадров по таймеру
        """
        global SPRITE_ANIMATION_COUNTER
        if self.__started:
            if self.__timer_index is None:
                self.__timer_index = copy(SPRITE_ANIMATION_COUNTER)
                
                SPRITE_ANIMATION_COUNTER += 1
            
            wait_call(self.__timer_index, self.__time_between_frames, self._update_animation)
            self.__play_time = time.time() - self.__start_time
            if self.__animation_type == 'none' and self.__frame_index == self.__frames_count - 1:
                self.stop()
                self.__finish = True

    def get_finish(self) -> bool:
        """Возвращает True, если анимация завершена"""
        return self.__finish

    def get_play_time(self) -> float:
        """Возвращает время проигрывания анимации"""
        return self.__play_time

    def special_draw(self, window):
        """
        Специальный метод для отрисовки текущего кадра
        
        Args:
            window: Окно или текстура для отрисовки
        """
        self.update_frame(self.__frame_index)
        window.draw(self.__frames[self.__frame_index])

    def set_flip_x(self, value: bool) -> Self:
        """
        Устанавливает отражение спрайта по горизонтали
        
        Args:
            value: Если True - спрайт будет отражен по горизонтали
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__flip_x = value
        return self

    def set_flip_y(self, value: bool) -> Self:
        """
        Устанавливает отражение спрайта по вертикали
        
        Args:
            value: Если True - спрайт будет отражен по вертикали
            
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__flip_y = value
        return self
    
    def flip_x(self) -> Self:
        """
        Переключает отражение спрайта по горизонтали (инвертирует текущее состояние)
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__flip_x = not self.__flip_x
        return self

    def flip_y(self) -> Self:
        """
        Переключает отражение спрайта по вертикали (инвертирует текущее состояние)
        
        Returns:
            Возвращает self для цепочки вызовов
        """
        self.__flip_y = not self.__flip_y
        return self

    def get_flip_x(self) -> bool:
        """
        Возвращает состояние отражения по горизонтали
        
        Returns:
            True если спрайт отражен по горизонтали, иначе False
        """
        return self.__flip_x
    
    def get_flip_y(self) -> bool:
        """
        Возвращает состояние отражения по вертикали
        
        Returns:
            True если спрайт отражен по вертикали, иначе False
        """
        return self.__flip_y
    
    def get_at_index(self) -> int:
        """
        Возвращает индекс текущего кадра анимации
        
        Returns:
            Индекс текущего отображаемого кадра
        """
        return self.__frame_index
    
    def get_timer(self) -> Timer:
        """
        Возвращает таймер, управляющий сменой кадров анимации
        
        Returns:
            Объект Timer, управляющий анимацией, или None если анимация не запущена
        """
        if self.__timer_index is None: return None
        return TIMER_BUFFER[self.__timer_index]
    
def LoadSpriteAnimation(path: str, frame_size: TwoIntegerList, time_between_frames: float = 0.1, animation_type: str = 'loop', frame_scale: Number = 1) -> SpriteAnimation:
    """
    Загружает анимацию из файла

    Args:
        path: Путь к файлу анимации
        time_between_frames: Время между кадрами анимации
        animation_type: Тип анимации (loop, none, elastic)

    Returns:
            Объект класса SpriteAnimation
    """
    frames = LoadSpriteArrayFromSprite(path, frame_size, frame_scale)
    animation = SpriteAnimation().set_frames(frames)
    animation.set_scale(frame_scale)
    animation.set_time_between_frames(time_between_frames)
    animation.set_animation_type(animation_type)
    return animation


class TextureAtlas:
    """
    Класс для работы с атласами текстур
    """
    def __init__(self, texture: Texture) -> Self:
        """
        Инициализирует атлас текстур
        Args:
            texture: Текстура атласа
        """
        self.__texture = texture
        self.__size = self.__texture.get_size()

    @classmethod
    def LoadFromFile(cls, path: str) -> "TextureAtlas":
        """
        Загружает атлас из файла
        Args:
            path: Путь к файлу атласа

        Returns:
            Объект класса TextureAtlas
        """
        texture = Texture.LoadFromFile(path)
        texture_atlas = TextureAtlas(texture)
        return texture_atlas

    def get_texture(self) -> Texture:
        """
        Возвращает текстуру атласа

        Returns:
            Текстура атласа
        """
        return self.__texture
    
    def get_size(self) -> TwoIntegerList:
        """
        Возвращает размер атласа

        Returns:
            Размер атласа
        """
        return self.__size
    
    def get_texture_at(self, x: int, y: int, width: int, height: int) -> Texture:
        """
        Возвращает текстуру из атласа по координатам и размеру 

        Args:
            x: Координата X
            y: Координата Y
            width: Ширина текстуры
            height: Высота текстуры

        Returns:
            Текстура из атласа
        """
        if x >= 0 and y >= 0 and x + width <= self.__size[0] and y + height <= self.__size[1]:
            return self.__texture.get_sub_texture(x, y, width, height)
        raise ValueError("Invalid subtexture coordinates")




# Шейдеры для обводки. Используют "./PySGL/python/rendering/Shaders". ============================================ +
OUTLINE_SHADER = Shader.FromType(Shader.Type.FRAGMENT, """
uniform sampler2D texture;
                                 
uniform vec4 outlineColor;

uniform float outlineThickness;

uniform vec2 textureSize;
                                 
void main()
{

    vec2 texCoord = gl_TexCoord[0].xy;


    vec4 pixelColor = texture2D(texture, texCoord);

    if (pixelColor.a == 0.0)
    {
        bool isOutline = false;

        for (float x = -outlineThickness; x <= outlineThickness; x += 1.0)
        {
            for (float y = -outlineThickness; y <= outlineThickness; y += 1.0)
            {
                if (x == 0.0 && y == 0.0)
                    continue;

                vec2 offsetTexCoord = texCoord + vec2(x / textureSize.x, y / textureSize.y);

                vec4 neighborColor = texture2D(texture, offsetTexCoord);

                if (neighborColor.a > 0.0)
                {
                    isOutline = true;
                    break; // Нашли непрозрачного соседа, дальше проверять не нужно.
                }
            }
            if (isOutline)
                break; // Нашли непрозрачного соседа, дальше проверять не нужно.
        }
        if (isOutline)
        {
            gl_FragColor = outlineColor;
        }
        else
        {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        }
    }
    else
    {
        gl_FragColor = pixelColor;
    }
}     
""")

PIXEL_PERFECT_OUTLINE_SHADER = Shader.FromType(Shader.Type.FRAGMENT, """
uniform sampler2D texture;
uniform vec4 outlineColor;
uniform float outlineThickness;
uniform vec2 textureSize;

void main()
{
    vec2 texCoord = gl_TexCoord[0].xy;
    vec4 pixelColor = texture2D(texture, texCoord);
    
    if (pixelColor.a == 0.0)
    {
        bool isOutline = false;
        
        vec2 offsets[4];
        offsets[0] = vec2( 0.0,  1.0/textureSize.y); // up
        offsets[1] = vec2( 0.0, -1.0/textureSize.y); // down
        offsets[2] = vec2( 1.0/textureSize.x,  0.0); // right
        offsets[3] = vec2(-1.0/textureSize.x,  0.0); // left
        
        for (int i = 0; i < 4; i++)
        {
            vec4 neighborColor = texture2D(texture, texCoord + offsets[i]);
            if (neighborColor.a > 0.0)
            {
                isOutline = true;
                break;
            }
        }
        
        if (outlineThickness > 1.0 && !isOutline)
        {
            for (int i = 0; i < 4; i++)
            {
                for (float t = 2.0; t <= outlineThickness; t += 1.0)
                {
                    vec4 neighborColor = texture2D(texture, texCoord + offsets[i] * t);
                    if (neighborColor.a > 0.0)
                    {
                        isOutline = true;
                        break;
                    }
                }
                if (isOutline) break;
            }
        }
        
        if (isOutline)
        {
            gl_FragColor = outlineColor;
        }
        else
        {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        }
    }
    else
    {
        gl_FragColor = pixelColor;
    }
}
""")

RAINBOW_OUTLINE_SHADER = Shader.FromType(Shader.Type.FRAGMENT, """
uniform sampler2D texture;
uniform float outlineThickness;
uniform vec2 textureSize;
uniform float time;  // For animation

void main()
{
    vec2 texCoord = gl_TexCoord[0].xy;
    vec4 pixelColor = texture2D(texture, texCoord);
    
    // Only process transparent pixels for outline
    if (pixelColor.a == 0.0)
    {
        bool isOutline = false;
        
        // Check 4 main directions (up, down, left, right)
        vec2 offsets[4];
        offsets[0] = vec2( 0.0,  1.0/textureSize.y); // up
        offsets[1] = vec2( 0.0, -1.0/textureSize.y); // down
        offsets[2] = vec2( 1.0/textureSize.x,  0.0); // right
        offsets[3] = vec2(-1.0/textureSize.x,  0.0); // left
        
        for (int i = 0; i < 4; i++)
        {
            vec4 neighborColor = texture2D(texture, texCoord + offsets[i]);
            if (neighborColor.a > 0.0)
            {
                isOutline = true;
                break;
            }
        }
        
        // For thicker outlines
        if (outlineThickness > 1.0 && !isOutline)
        {
            for (int i = 0; i < 4; i++)
            {
                for (float t = 2.0; t <= outlineThickness; t += 1.0)
                {
                    vec4 neighborColor = texture2D(texture, texCoord + offsets[i] * t);
                    if (neighborColor.a > 0.0)
                    {
                        isOutline = true;
                        break;
                    }
                }
                if (isOutline) break;
            }
        }
        
        if (isOutline)
        {
            // Rainbow color effect based on position and time
            float hue = texCoord.x + texCoord.y + time * 0.5;
            vec3 rainbowColor = vec3(
                0.5 + 0.5 * sin(hue * 3.14159265),
                0.5 + 0.5 * sin((hue + 0.333) * 3.14159265),
                0.5 + 0.5 * sin((hue + 0.666) * 3.14159265)
            );
            
            // Add pulsing effect to outline
            float pulse = 0.8 + 0.2 * sin(time * 3.0);
            gl_FragColor = vec4(rainbowColor * pulse, 1.0);
        }
        else
        {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        }
    }
    else
    {
        gl_FragColor = pixelColor;
    }
}
""")
# Шейдеры для обводки. Используют "./PySGL/python/rendering/Shaders". ============================================ +



# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Метод использует специальные шейдеры предназаченные для создания обводки вокруг текстуры.
# Можно создать свой шейдер и передать его, или использовать один из предопределенных.
# `OUTLINE_SHADER` - шейдер для создания обводки вокруг текстуры. (Проверяет каждый пиксель вокруг данного)
# `PIXEL_PERFECT_OUTLINE_SHADER` - шейдер для создания обводки вокруг текстуры. (Проверяет только: верх, вниз, лево, право)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def apply_outline_to_texture(texture: Texture, outline_color: Color, outline_thickness: int, shader: Shader = OUTLINE_SHADER) -> Texture:
    """
    Создает обводку вокруг текстуры.
    Args:
        texture: Текстура, вокруг которой нужно создать обводку.
        outline_color: Цвет обводки.
        outline_thickness: Толщина обводки в пикселях.
        shshader: Шейдер для создания обводки.

    Returns:
        Новая текстура с обводкой.
    """
    # Создаем новую текстуру рендеринга того же размера
    render_texture = RenderTexture()
    render_texture.create(texture.get_size().x, texture.get_size().y)
    render_texture.set_smooth(False)
    
    # Создаем спрайт из исходной текстуры
    sprite = BaseSprite.FromTexture(texture)
    
    # Устанавливаем параметры шейдера
    shader.set_uniform("outlineColor", outline_color)
    shader.set_uniform("outlineThickness", float(outline_thickness))
    shader.set_uniform("textureSize", Vector2f(texture.get_size().x, texture.get_size().y))
    
    # Очищаем текстуру прозрачным цветом
    render_texture.clear(Color(0, 0, 0, 0))
    
    # Рисуем спрайт с шейдером обводки
    render_texture.draw(sprite, shader)
    
    # Финализируем отрисовку
    render_texture.display()
    
    #sprite = BaseSprite.FromRenderTexture(render_texture)
    texture = render_texture.get_texture()

    return texture



# Методы для загрузки массива текстур ========================================================================= +
def LoadTextureArrayFromPath(path_template: str, count: int) -> TextureArray:
    textures = []
    for i in range(count):
        file_path = path_template.format(i + 1)
        textures.append(Texture.LoadFromFile(file_path))
    return textures
        
def LoadTextureArrayFromTexture(path: str, one_sprite_size: TwoIntegerList) ->  TextureArray:
    full_texture = Texture.LoadFromFile(path)
    full_texture_size = full_texture.get_size()

    if full_texture_size.x % one_sprite_size[0] != 0:
        raise TypeError("Ivalid sprite sheet size!")
    
    textures = []
    for i in range(full_texture_size.x // one_sprite_size[0]):
        sub_texture = full_texture.get_sub_texture(i * one_sprite_size[0], 0, one_sprite_size[0], one_sprite_size[1])
        textures.append(sub_texture)
        
    return textures
# Методы для загрузки массива текстур ========================================================================= +



def apply_outline_to_texture_array(texture_array: TextureArray, outline_color: Color, outline_thickness: int, shader: Shader = OUTLINE_SHADER) -> TextureArray:
    """
    Применяет обводку вокруг каждой текстуры в массиве. 

    Возвращает новый массив текстур с обводкой.

    Args:
        texture_array: Массив текстур, вокруг которых нужно создать обводку.
        outline_color: Цвет обводки.
        outline_thickness: Толщина обводки в пикселях.
        shader: Шейдер для применения обводки.

    Returns:
        Новый массив текстур с обводкой.
    """
    textures_with_outline = []
    for texture in texture_array:
        texture_with_outline = apply_outline_to_texture(texture, outline_color, outline_thickness, shader)
        textures_with_outline.append(texture_with_outline)

    return textures_with_outline


# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Методы для конвертации массива текстур в массив спрайтов. Автоматически создает спрайты из текстур.
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def convery_texture_array_to_sprite_array(texture_array: TextureArray) -> SpriteArray:
    """
    Конвертирует массив текстур в массив спрайтов.
    Args:
        texture_array: Массив текстур.

    Returns:
        Массив спрайтов.
    """
    sprite_array = []
    for texture in texture_array:
        sprite = BaseSprite.FromTexture(texture)
        sprite_array.append(sprite)
    return sprite_array



