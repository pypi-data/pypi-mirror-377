from dataclasses import dataclass
from Moon.python.Rendering.Sprites import *
from Moon.python.Types import *

from enum import Enum, auto



class TileTypes(Enum):

    TOP = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM = auto()
    BOTTOM_RIGHT = auto()

    ONE = auto()

    HORIZONTAL = auto()
    HORIZONTAL_LEFT = auto()
    HORIZONTAL_RIGHT = auto()

    VERTICAL = auto()
    VERTICAL_TOP = auto()
    VERTICAL_BOTTOM = auto()



# Вспомогательные тип для тайла ============= +
type TileTypeLiteral = Literal[
    'TOP',
    'TOP_LEFT',
    'TOP_RIGHT',
    'LEFT',
    'MIDDLE',
    'RIGHT',
    'BOTTOM_LEFT',
    'BOTTOM',
    'BOTTOM_RIGHT',
    'ONE',
    'HORIZONTAL',
    'HORIZONTAL_LEFT',
    'HORIZONTAL_RIGHT',
    'VERTICAL',
    'VERTICAL_TOP',
    'VERTICAL_BOTTOM'
]

def convert_tile_type_to_type_literal(type: TileTypes) ->  TileTypeLiteral:
    return str(type).split('.')[-1]
# =========================================== +



class TileSet:
    def __init__(self, path: str, tile_size: TwoIntegerList, tile_scale: Number = 1) -> None:
        self.__path = path
        self.__texture = Texture.LoadFromFile(path)
        self.__texture_atlas = TextureAtlas(self.__texture)
        self.__tile_size = tile_size
        self.__tile_scale = tile_scale

    def get_path(self) -> str:
        return self.__path
    
    def get_texture(self) -> Texture:
        return self.__texture
    
    def get_texture_atlas(self) -> TextureAtlas:
        return self.__texture_atlas
    
    def get_tile_size(self) -> TwoIntegerList:
        return self.__tile_size
    
    def get_tile_scale(self) -> Number:
        return self.__tile_scale

    def get_texture(self, type: TileTypeLiteral) -> None:
        """
        Возвращает текстуру тайла по типу

        ---

        Не имеет реализации в базовом классе, используется в наследниках
        """
        raise NotImplementedError()
    
class TileSheet4x4(TileSet):
    def __init__(self, path: str, tile_size: TwoIntegerList, tile_scale: Number = 1) -> None:
        super().__init__(path, tile_size, tile_scale)
        self.__tile_sprites: dict[TileTypes, BaseSprite] = {}

    def get_scaled_tile_size(self) -> TwoIntegerList:
        return [
            self.get_tile_size()[0] * self.get_tile_scale(),
            self.get_tile_size()[1] * self.get_tile_scale()
        ]

    def pre_cut_tiles(self, scale: OptionalNumber = None) -> None:
        self.__tile_sprites.clear()
        for tile_type in TileTypes:
            sprite = BaseSprite.FromTexture(self.get_texture(
                convert_tile_type_to_type_literal(tile_type)
            ))
            if scale is None:
                sprite.set_scale(self.get_tile_scale())
            else:
                sprite.set_scale(scale)
            self.__tile_sprites[convert_tile_type_to_type_literal(tile_type)] = sprite

    def get_texture(self, type: TileTypeLiteral) -> Texture:
        """
        ##### Возвращает определенную текстуру тайла из атласа текстур по типу поддерживаемого тайла

        ---

        :param type: Тип тайла

        ---

        :return: Текстура тайла
        """

        match type:
            # Одиночный тайл
            case 'ONE':
                return self.get_texture_atlas().get_texture_at(0, 0, *self.get_tile_size())
            
            # Тайлы для горизонтального склеивания
            case 'HORIZONTAL_LEFT':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0], 0, *self.get_tile_size())
            case 'HORIZONTAL':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0] * 2, 0, *self.get_tile_size())
            case 'HORIZONTAL_RIGHT':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0] * 3, 0, *self.get_tile_size())
            
            # Тайлы для вертикального склеивания
            case 'VERTICAL_TOP':
                return self.get_texture_atlas().get_texture_at(0, self.get_tile_size()[1], *self.get_tile_size())
            case 'VERTICAL':
                return self.get_texture_atlas().get_texture_at(0, self.get_tile_size()[1] * 2, *self.get_tile_size())
            case 'VERTICAL_BOTTOM':
                return self.get_texture_atlas().get_texture_at(0, self.get_tile_size()[1] * 3, *self.get_tile_size())
            
            # Тайлы для склеивания `квадратом`
            case 'TOP_LEFT':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0], self.get_tile_size()[1], *self.get_tile_size())
            case 'TOP':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0] * 2, self.get_tile_size()[1], *self.get_tile_size())
            case 'TOP_RIGHT':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0] * 3, self.get_tile_size()[1], *self.get_tile_size())
            case 'LEFT':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0], self.get_tile_size()[1] * 2, *self.get_tile_size())
            case 'MIDDLE':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0] * 2, self.get_tile_size()[1] * 2, *self.get_tile_size())
            case 'RIGHT':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0] * 3, self.get_tile_size()[1] * 2, *self.get_tile_size())
            case 'BOTTOM_LEFT':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0], self.get_tile_size()[1] * 3, *self.get_tile_size())
            case 'BOTTOM':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0] * 2, self.get_tile_size()[1] * 3, *self.get_tile_size())
            case 'BOTTOM_RIGHT':
                return self.get_texture_atlas().get_texture_at(self.get_tile_size()[0] * 3, self.get_tile_size()[1] * 3, *self.get_tile_size())
            case _:
                raise ValueError(f'Unknown tile type: {type}')
            
    def get_sprite(self, type: TileTypeLiteral) -> BaseSprite:
        if len(self.__tile_sprites) == 0: 
            raise ValueError('Tile sprites not pre-cut, use pre_cut_tiles() first.')
        return self.__tile_sprites[type]
    
TileMapDataType = list[list[int]] | tuple[tuple[int, ...]]

@dataclass
class TileSheetAccordance:
    tile_sheet: TileSheet4x4
    identifier: int
    
class TileSheetAccordances:
    def __init__(self, tile_sheets_accordances: list[TileSheetAccordance]) -> None:
        self.__accordances: dict[int, TileSheet4x4] = {}
        self.__tile_sheets_accordances = tile_sheets_accordances
        for accordance in tile_sheets_accordances:
            self.__accordances[accordance.identifier] = accordance.tile_sheet

    def get_accordance(self, identifier: int) -> TileSheet4x4:
        return self.__accordances[identifier]
    
    def get_accordances(self) -> dict[int, TileSheet4x4]:
        return self.__accordances
    
    def get_tile_sheet_accordances(self) -> list[TileSheetAccordance]:
        return self.__tile_sheets_accordances
        

class TileMap:
    def __init__(self, data: TileMapDataType):
        self.__data = data
        self.__size = (len(data[0]), len(data))
    
    def get_size(self) -> TwoIntegerList:
        return self.__size
    
    @property
    def data(self) -> TileMapDataType:
        return self.__data

def generate_tile_map_sprite(map: TileMap, accordance: TileSheetAccordances, tile_size: TwoIntegerList) -> BaseSprite:
    """
    #### Генерирует спрайт тайловой карты на основе данных карты и соответствий тайлов

    ---

    :Args:
    - map - Объект TileMap с данными карты
    - accordance - Объект TileSheetAccordances с соответствиями тайлов

    ---

    :Return:
    - BaseSprite - Спрайт, содержащий всю тайловую карту

    ---

    :Raises:
    - ValueError: Если в данных карты встречен неизвестный идентификатор тайла
    - RuntimeError: Если не удалось создать текстуру рендеринга

    ---

    :Example:
    ```python
    # Создание тайловой карты
    tile_map = TileMap([
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1]
    ])
    
    # Создание соответствий тайлов
    tile_sheet = TileSheet4x4("tiles.png", [32, 32])
    accordances = TileSheetAccordances([
        TileSheetAccordance(tile_sheet, 1),  # Стены
    ])
    
    # Генерация спрайта карты
    map_sprite = generate_tile_map_sprite(tile_map, accordances)
    ```
    """
    # Получаем размеры карты и размер одного тайла
    map_width, map_height = map.get_size()
    
    

    
    # Создаем текстуру рендеринга для всей карты
    render_texture = RenderTexture()
    if not render_texture.create(map_width * tile_size[0], map_height * tile_size[1]):
        raise RuntimeError("Failed to create render texture for tile map")
    
    # Очищаем текстуру прозрачным цветом
    render_texture.clear(Color(0, 0, 0, 0))
    
    # Рендерим каждый тайл
    for y in range(map_height):
        for x in range(map_width):
            tile_id = map.data[y][x]
            if tile_id != 0:
                try:
                    tile_sheet = accordance.get_accordance(tile_id)
                except KeyError:
                    raise ValueError(f"Unknown tile ID: {tile_id}")
                
                # Определяем тип тайла на основе соседей
                tile_type = determine_tile_type_for_tilesheet4x4(map, x, y, tile_id)
                
                # Получаем спрайт тайла
                try:
                    tile_sprite = tile_sheet.get_sprite(tile_type)
                except ValueError:
                    # Если спрайты не были предварительно вырезаны, создаем на лету
                    texture = tile_sheet.get_texture(tile_type)
                    tile_sprite = BaseSprite.FromTexture(texture)
                    tile_sprite.set_scale(tile_sheet.get_tile_scale())
                    del texture
                
                # Устанавливаем позицию тайла
                tile_sprite.set_position(x * tile_size[0], y * tile_size[1])
                
                # Рисуем тайл на текстуре рендеринга
                render_texture.draw(tile_sprite)
    
    # Финализируем отрисовку
    render_texture.display()
    
    # Создаем спрайт из текстуры рендеринга
    map_sprite = BaseSprite.FromRenderTexture(render_texture)
    return map_sprite

def determine_tile_type_for_tilesheet4x4(map: TileMap, x: int, y: int, tile_id: int) -> TileTypeLiteral:
    """
    #### Определяет тип тайла на основе его соседей

    :Warning: Данная функция реализованная только для `TileSheet4x4`, поэтому не рекомендуется использовать этот метод в своих проектах.

    ---

    :Args:
    - map - Объект TileMap
    - x - X-координата тайла
    - y - Y-координата тайла
    - tile_id - ID текущего тайла

    ---

    :Return:
    - TileTypeLiteral - Тип тайла
    """
    map_width, map_height = map.get_size()
    
    # Проверяем соседей
    has_top = y > 0 and map.data[y-1][x] == tile_id
    has_bottom = y < map_height-1 and map.data[y+1][x] == tile_id
    has_left = x > 0 and map.data[y][x-1] == tile_id
    has_right = x < map_width-1 and map.data[y][x+1] == tile_id
    
    # Определяем тип тайла
    if not has_top and not has_bottom and not has_left and not has_right:
        return 'ONE'
    
    # Горизонтальные тайлы
    if has_left and has_right and not has_top and not has_bottom:
        return 'HORIZONTAL'
    if has_right and not has_left and not has_top and not has_bottom:
        return 'HORIZONTAL_LEFT'
    if has_left and not has_right and not has_top and not has_bottom:
        return 'HORIZONTAL_RIGHT'
    
    # Вертикальные тайлы
    if has_top and has_bottom and not has_left and not has_right:
        return 'VERTICAL'
    if has_bottom and not has_top and not has_left and not has_right:
        return 'VERTICAL_TOP'
    if has_top and not has_bottom and not has_left and not has_right:
        return 'VERTICAL_BOTTOM'
    
    # Угловые и центральные тайлы
    if not has_top and not has_left:
        return 'TOP_LEFT'
    if not has_top and not has_right:
        return 'TOP_RIGHT'
    if not has_bottom and not has_left:
        return 'BOTTOM_LEFT'
    if not has_bottom and not has_right:
        return 'BOTTOM_RIGHT'
    if not has_top:
        return 'TOP'
    if not has_bottom:
        return 'BOTTOM'
    if not has_left:
        return 'LEFT'
    if not has_right:
        return 'RIGHT'
    
    # Если со всех сторон есть такие же тайлы
    return 'MIDDLE'