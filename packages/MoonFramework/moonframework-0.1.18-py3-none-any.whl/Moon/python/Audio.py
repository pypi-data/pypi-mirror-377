"""
#### *Модуль работы со звуком в Moon*

---

##### Версия: 1.0.6

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 99% 

---

✓ Полноценная система аудио:
  - Загрузка и управление звуковыми буферами
  - Поддержка форматов WAV, OGG, MP3
  - Контроль параметров воспроизведения

✓ Расширенные возможности:
  - 3D позиционирование звука
  - Многоканальное воспроизведение
  - Гибкая система событий

✓ Оптимизированная работа:
  - Минимальные задержки воспроизведения
  - Эффективное использование ресурсов
  - Поддержка аппаратного ускорения

✓ Готовые интерфейсы:
  - SoundBuffer - работа с аудиоданными
  - Sound - управление воспроизведением
  - MultiSound - многоканальное звучание
  - SoundEventListener - обработка событий

---

:Requires:

• Python 3.8+

• Библиотека ctypes (для работы с DLL)

• Moon.dll (нативная аудио библиотека)

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
from typing import final

from Moon.python.Types import *

from Moon.python.utils import find_library, LibraryLoadError

# Загружаем DLL библиотеку
try:
    LIB_MOON = ctypes.CDLL(find_library())
except Exception as e:
    raise ImportError(f"Failed to load Moon library: {e}")

# Тип указателя на звуковой буфер ====== +
SoundBufferPtr = ctypes.c_void_p         #
# ====================================== +

# Определение типов аргументов и возвращаемых значений для функций DLL
LIB_MOON._SoundBuffer_loadFromFile.argtypes = [ctypes.c_char_p]
LIB_MOON._SoundBuffer_loadFromFile.restype = SoundBufferPtr
LIB_MOON._SoundBuffer_Destroy.argtypes = [SoundBufferPtr]
LIB_MOON._SoundBuffer_Destroy.restype = None
LIB_MOON._SoundBuffer_GetChannelsCount.argtypes = [SoundBufferPtr]
LIB_MOON._SoundBuffer_GetChannelsCount.restype = ctypes.c_int
LIB_MOON._SoundBuffer_GetSampleRate.argtypes = [SoundBufferPtr]
LIB_MOON._SoundBuffer_GetSampleRate.restype = ctypes.c_int

@final
class SoundBuffer:
    """
    #### Класс для работы со звуковыми буферами
    
    ---
    
    :Description:
    - Загружает и хранит аудиоданные из файлов
    - Предоставляет доступ к параметрам звука
    - Управляет жизненным циклом звукового буфера
    
    ---
    
    :Formats:
    - WAV
    - OGG
    - MP3

    """
    __slots__ = ("__path", "__ptr")

    def __init__(self, path: str) -> Self:
        """
        #### Инициализирует звуковой буфер из файла
        
        ---
        
        :Args:
        - path (str): Путь к файлу с расширением .wav
        
        ---
        
        :Raises:
        - RuntimeError: При ошибке загрузки файла
        
        ---
        
        :Example:
        ```python
        buffer = SoundBuffer("sound.wav")
        ```
        """
        self.__path = path
        self.__ptr: SoundBufferPtr = LIB_MOON._SoundBuffer_loadFromFile(path.encode('utf-8'))
        
    @final
    def destroy(self) -> None:
        """
        #### Освобождает ресурсы звукового буфера
        
        ---
        
        :Note:
        - Вызывается автоматически при удалении объекта
        """
        LIB_MOON._SoundBuffer_Destroy(self.__ptr)
        self.__ptr = None

    def __del__(self) -> None:
        """
        #### Деструктор, освобождающий ресурсы
        
        ---
        
        :Note:
        - Гарантирует корректное удаление нативного объекта
        """
        self.destroy()

    @final
    def get_sample_rate(self) -> int:
        """
        #### Возвращает частоту дискретизации звука
        
        ---
        
        :Returns:
        - int: Частота дискретизации в Гц
        
        ---
        
        :Example:
        ```python
        rate = buffer.get_sample_rate()  # 44100
        ```
        """
        return LIB_MOON._SoundBuffer_GetSampleRate(self.__ptr)

    @final
    def get_ptr(self) -> SoundBufferPtr:
        """
        #### Возвращает указатель на нативный буфер
        
        ---
        
        :Returns:
        - SoundBufferPtr: Указатель на внутренний объект
        
        ---
        
        :Note:
        - Для внутреннего использования в Moon
        """
        return self.__ptr
    
    @final
    def get_channels_count(self) -> int:
        """
        #### Возвращает количество аудиоканалов
        
        ---
        
        :Returns:
        - int: Количество каналов (1 - моно, 2 - стерео)
        
        ---
        
        :Example:
        ```python
        channels = buffer.get_channels_count()  # 2
        ```
        """
        return LIB_MOON._SoundBuffer_GetChannelsCount(self.__ptr)
    
    @final
    def get_path(self) -> str:
        """
        #### Возвращает путь к исходному файлу
        
        ---
        
        :Returns:
        - str: Путь к файлу, из которого загружен буфер
        """
        return self.__path

# Тип указателя на звук ========= +
SoundPtr = ctypes.c_void_p        #
# =============================== +

# Определение типов аргументов и возвращаемых значений для функций DLL
LIB_MOON._Sound_Create.argtypes = [SoundBufferPtr]
LIB_MOON._Sound_Create.restype = SoundPtr
LIB_MOON._Sound_Play.argtypes = [SoundPtr]
LIB_MOON._Sound_Play.restype = None
LIB_MOON._Sound_Pause.argtypes = [SoundPtr]
LIB_MOON._Sound_Pause.restype = None
LIB_MOON._Sound_Stop.argtypes = [SoundPtr]
LIB_MOON._Sound_Stop.restype = None
LIB_MOON._Sound_Destroy.argtypes = [SoundPtr]
LIB_MOON._Sound_Destroy.restype = None
LIB_MOON._Sound_SetLoop.argtypes = [SoundPtr, ctypes.c_bool]
LIB_MOON._Sound_SetLoop.restype = None
LIB_MOON._Sound_SetVolume.argtypes = [SoundPtr, ctypes.c_float]
LIB_MOON._Sound_SetVolume.restype = None
LIB_MOON._Sound_SetPitch.argtypes = [SoundPtr, ctypes.c_float]
LIB_MOON._Sound_SetPitch.restype = None
LIB_MOON._Sound_SetAttenuation.argtypes = [SoundPtr, ctypes.c_float]
LIB_MOON._Sound_SetAttenuation.restype = None
LIB_MOON._Sound_ResetBuffer.argtypes = [SoundPtr]
LIB_MOON._Sound_ResetBuffer.restype = None
LIB_MOON._Sound_SetPosition.argtypes = [SoundPtr, ctypes.c_float, ctypes.c_float, ctypes.c_float]
LIB_MOON._Sound_SetPosition.restype = None
LIB_MOON._Sound_SetRelativeToListener.argtypes = [SoundPtr, ctypes.c_bool]
LIB_MOON._Sound_SetRelativeToListener.restype = None
LIB_MOON._Sound_GetStatus.argtypes = [SoundPtr]
LIB_MOON._Sound_GetStatus.restype = ctypes.c_int

@final
class AudioStatus(Enum):
    """
    #### Перечисление статусов воспроизведения звука
    
    ---
    
    :Values:
    - STOPPED: Звук остановлен
    - PAUSED: Звук приостановлен
    - PLAYING: Звук воспроизводится
    """
    STOPED = auto(0)
    PAUSED = auto()
    PLAYING = auto()

@final
class Sound:
    """
    #### Класс для управления воспроизведением звука
    
    ---
    
    :Description:
    - Контролирует воспроизведение, паузу, остановку звука
    - Позволяет настраивать параметры воспроизведения
    - Поддерживает 3D-позиционирование
    """
    __slots__ = ("__sound_buffer", "__ptr", "__played", "__paused", "__volume", "__pitch", "__attenuation", "__looped", "__id")

    def __init__(self, sound_buffer: SoundBuffer) -> Self:
        """
        #### Инициализирует звук из буфера

        ---

        Есть возможность хеширования.
        
        ---
        
        :Args:
        - sound_buffer (SoundBuffer): Буфер с аудиоданными
        
        ---
        
        :Raises:
        - RuntimeError: При ошибке создания звука
        """
        self.__sound_buffer = sound_buffer

        try:
            self.__ptr: SoundPtr = LIB_MOON._Sound_Create(self.__sound_buffer.get_ptr())
        except:
            raise RuntimeError("Failed to create sound")
        
        self.__played:          bool = False
        self.__paused:          bool = False
        self.__volume:          float = 1.0
        self.__pitch:           float = 1.0
        self.__attenuation:     float = 1.0
        self.__looped:          bool = False
        self.__id:              Identifier = AutoIdentifier()

    @final
    def get_identifier(self) -> Identifier:
        """
        #### Возвращает идентификатор звука

        ---

        :Returns:
        - Identifier: Идентификатор звука

        ---

        :Example:
        ```python
        sound_id = sound.get_identifier()
        ```
        """
        return self.__id

    def __eq__(self, other: "Sound") -> bool:
        """
        #### Сравнивает два звука по идентификатору
        """
        return  self.__id == other.get_identifier()
    
    def __ne__(self, other: "Sound") -> bool:
        """
        #### Сравнивает два звука по идентификатору
        """
        return  self.__id != other.get_identifier()
        
    def __hash__(self) -> int:
        """
        #### Возвращает хэш-код звука
        """
        return hash(self.__id)
    
    @final
    def get_path(self) -> str:
        """
        #### Возвращает путь к исходному файлу

        ---

        :Returns:
        - str: Путь к файлу, из которого загружен звук
        """
        return self.__sound_buffer.get_path()

    @final
    def get_status(self) -> AudioStatus:
        """
        #### Возвращает текущий статус воспроизведения
        
        ---
        
        :Returns:
        - AudioStatus: Текущее состояние звука
        
        ---
        
        :Example:
        ```python
        if sound.get_status() == AudioStatus.PLAYING:
            print("Sound is playing")
        ```
        """
        return AudioStatus(LIB_MOON._Sound_GetStatus(self.__ptr))

    @final
    def set_relative_to_listener(self, relative: bool) -> Self:
        """
        #### Устанавливает, будет ли звук воспроизводиться относительно слушателя.

        ---

        :Args:
        - relative (bool): True, если звук должен воспроизводиться относительно слушателя

        ---

        :Returns:
        - self: Для цепных вызовов

        ---

        :Example:
        ```python
        sound.set_relative_to_listener(True)
        ```
        """
        LIB_MOON._Sound_SetRelativeToListener(self.__ptr, relative)
        return self

    @final
    def set_position(self, x: float, y: float, z: float) -> Self:
        """
        Устанавливает позицию звука в 3D пространстве.

        ---

        :Args:
        - x (float): Координата X
        - y (float): Координата Y 
        - z (float): Координата Z

        ---

        :Returns:
        - self: Для цепных вызовов

        ---

        :Example:
        ```python
        sound.set_position(0, 0, 0) # Устанавливает звук в центр экрана
        ```
        """
        LIB_MOON._Sound_SetPosition(self.__ptr, float(x), float(y), float(z))
        return self
    
    @final
    def play_left(self) -> Self:
        """
        #### Воспроизводит звук слева от слушателя.

        ---

        :Returns:
        - self: Для цепных вызовов
        """
        self.set_position(-1, 0, 0)
        self.play()
        return self
    
    @final
    def play_right(self) -> Self:
        """
        #### Воспроизводит звук справа от слушателя.

        ---

        :Returns:
        - self: Для цепных вызовов
        """
        self.set_position(1, 0, 0)
        self.play()
        return self

    @final
    def copy(self) -> "Sound":
        """
        #### Создает копию текущего звука с теми же параметрами.

        ---

        :Returns:
            Sound: Новая копия звука

        ---

        :Example:
        ```python
        sound_buffer = SoundBuffer("path/to/sound.wav")
        sound = Sound(sound_buffer)
        sound_copy = sound.copy()
        ```
        """
        sound = Sound(self.__sound_buffer)
        sound.set_attenuation(self.__attenuation)
        sound.set_pitch(self.__pitch)
        sound.set_volume(self.__volume)
        sound.set_loop(self.__looped)
        return sound

    @final
    def get_ptr(self) -> SoundPtr:
        """
        #### Возвращает указатель на звук.

        ---

        :Returns:
        - SoundPtr: Указатель на звук

        ---

        :Example:
        ```python
        sound_ptr = sound.get_ptr()
        print(sound_ptr) # Выведет адрес звука в памяти
        ```
        """
        return self.__ptr
    
    @final
    def get_sound_buffer(self) -> SoundBuffer:
        """
        #### Возвращает звуковой буфер.

        ---

        :Returns:
        - SoundBuffer: Звуковый буфер

        ---

        :Example:
        ```python
        sound_buffer = sound.get_sound_buffer()
        print(sound_buffer) # Выведет звуковый буфер
        ```
        """
        return self.__sound_buffer
    
    @final
    def play(self) -> Self:
        """
        #### Начинает воспроизведение звука.

        ---

        :Returns:
        - self: Для цепных вызовов

        ---

        :Example:
        ```python
        sound = Sound(SoundBuffer("path/to/sound.wav"))
        sound.play()
        ```
        """
        self.__played = True
        self.__paused = False
        LIB_MOON._Sound_Play(self.__ptr)
        return self
    
    @final
    def pause(self) -> Self:
        """
        #### Приостанавливает воспроизведение звука.

        :Returns:
        - self: Для цепных вызовов
        """
        self.__paused = True
        LIB_MOON._Sound_Pause(self.__ptr)
        return self
    
    @final
    def stop(self) -> Self:
        """
        #### Останавливает воспроизведение звука.

        :Returns:
        - self: Для цепных вызовов
        """
        self.__played = False
        LIB_MOON._Sound_Stop(self.__ptr)
        return self
    
    @final
    def is_playing(self) -> bool:
        """
        #### Проверяет, воспроизводится ли звук.

        ---

        :Returns:
            bool: True если звук воспроизводится

        ---

        :Example:
        ```python
        if sound.is_playing():
            print("Sound is playing")
        ```
        """
        return self.__played
    
    @final
    def is_paused(self) -> bool:
        """
        #### Проверяет, приостановлен ли звук.

        ---

        :Returns:
        - bool: True если звук приостановлен
        """
        return self.__paused
    
    @final
    def set_loop(self, loop: bool) -> Self:
        """
        #### Устанавливает зацикливание звука.

        ---

        :Args:
        - loop (bool): True для зацикливания

        :Returns:
        - self: Для цепных вызовов

        ---

        :Example:
        ```python
        sound.set_loop(True)
        ```
        """
        self.__looped = loop
        LIB_MOON._Sound_SetLoop(self.__ptr, loop)
        return self

    @final
    def get_loop(self) -> bool:
        """
        #### Проверяет, зациклен ли звук.

        ---

        :Returns:
            bool: True если звук зациклен

        ---

        :Example:
        ```python
        if sound.get_loop():
            print("Sound is looped")
        ```
        """
        return self.__looped

    @final
    def set_volume(self, volume: float) -> Self:
        """
        #### Устанавливает громкость звука.

        ---

        :Args:
        - volume (float): Громкость (0.0 - infinity)

        Чем больше число тем громче звук, зависит на сколько мощные динамики у вас

        :Returns:
        - self: Для цепных вызовов
        """
        self.__volume = volume
        LIB_MOON._Sound_SetVolume(self.__ptr, volume)
        return self
    
    @final
    def get_volume(self) -> float:
        """
        #### Возвращает текущую громкость звука.

        ---

        :Returns:
        - float: Текущая громкость
        """
        return self.__volume
    
    @final
    def set_pitch(self, pitch: float) -> Self:
        """
        #### Устанавливает высоту тона звука.

        ---

        :Args:
        - pitch (float): Высота тона (0.0 - 1.0)
        
        :Returns:
        - self: Для цепных вызовов
        """
        self.__pitch = pitch
        LIB_MOON._Sound_SetPitch(self.__ptr, pitch)
        return self
    
    @final
    def get_pitch(self) -> float:
        """
        #### Возвращает текущую высоту тона звука.

        :Returns:
        - float: Текущая высота тона
        """
        return self.__pitch
    
    @final
    def set_attenuation(self, attenuation: float) -> Self:
        """
        #### Устанавливает затухание звука.

        ---

        :Args:
        - attenuation (float): Коэффициент затухания (0.0 - 1.0)

        :Returns:
        - self: Для цепных вызовов
        """
        self.__attenuation = attenuation
        LIB_MOON._Sound_SetAttenuation(self.__ptr, attenuation)
        return self
    
    @final
    def get_attenuation(self) -> float:
        """
        #### Возвращает текущее затухание звука.

        ---

        :Returns:
        - float: Текущее затухание
        """
        return self.__attenuation
    
    @final
    def destroy(self) -> None:
        """
        #### Освобождает ресурсы звука.
        """
        LIB_MOON._Sound_Destroy(self.__ptr)
        self.__ptr = None

    def __del__(self) -> None:
        """
        #### Деструктор, освобождающий ресурсы.
        """
        self.destroy()

    @final
    def reset(self) -> Self:
        """
        #### Сбрасывает звук в начальное состояние.

        --- 

        :Returns:
            self: Для цепных вызовов
        """
        LIB_MOON._Sound_ResetBuffer(self.__ptr)
        return self

class SoundEventListener:
    """
    #### Обработчик событий состояния звука
    
    ---
    
    :Description:
    - Отслеживает изменения состояния воспроизведения звука
    - Позволяет назначить callback-функции на события
    - Требует регулярного вызова update() в основном цикле
    
    ---
    
    :Events:
    - play: Начало воспроизведения
    - pause: Приостановка воспроизведения
    - stop: Остановка воспроизведения
    """
    __slots__ = ("__sound", "__last_status", "__on_play", "__on_pause", "__on_stop", 
                "__played", "__paused", "__stopped")

    def __init__(self, sound: Sound) -> None:
        """
        #### Инициализирует обработчик событий для звука
        
        ---
        
        :Args:
        - sound (Sound): Звуковой объект для отслеживания
        
        ---
        
        :Example:
        ```python
        listener = SoundEventListener(sound)
        ```
        """
        self.__sound: Sound = sound
        self.__last_status: AudioStatus = AudioStatus.STOPPED
        
        # Callback-функции
        self.__on_play: Optional[Callable[[], None]] = None
        self.__on_pause: Optional[Callable[[], None]] = None
        self.__on_stop: Optional[Callable[[], None]] = None

        # Флаги событий
        self.__played: bool = False
        self.__paused: bool = False
        self.__stopped: bool = False

    def get_event(self, type: Literal['play', 'stop', 'pause'] = 'play') -> bool:
        """
        #### Проверяет наличие события указанного типа
        
        ---
        
        :Args:
        - type (str): Тип события ('play', 'stop', 'pause')
        
        ---
        
        :Returns:
        - bool: True если событие произошло
        
        ---
        
        :Raises:
        - ValueError: При передаче недопустимого типа события
        
        ---
        
        :Example:
        ```python
        if listener.get_event('play'):
            print("Sound started playing")
        ```
        """
        match type:
            case 'play':
                return self.__played
            case 'pause':
                return self.__paused
            case 'stop':
                return self.__stopped
            case _:
                raise ValueError(f"Invalid event type: {type}")

    def _update_statuses(self) -> None:
        """
        #### Сбрасывает флаги событий
        
        ---
        
        :Note:
        - Внутренний метод, вызывается перед проверкой состояния
        """
        self.__played = False
        self.__paused = False
        self.__stopped = False

    def set_on_play(self, callback: Callable[[], None]) -> Self:
        """
        #### Устанавливает обработчик начала воспроизведения
        
        ---
        
        :Args:
        - callback (Callable[[], None]): Функция без параметров
        
        ---
        
        :Returns:
        - self: Для цепных вызовов
        
        ---
        
        :Example:
        ```python
        listener.set_on_play(lambda: print("Playback started"))
        ```
        """
        self.__on_play = callback
        return self

    def set_on_pause(self, callback: Callable[[], None]) -> Self:
        """
        #### Устанавливает обработчик паузы
        
        ---
        
        :Args:
        - callback (Callable[[], None]): Функция без параметров
        
        ---
        
        :Returns:
        - self: Для цепных вызовов
        """
        self.__on_pause = callback
        return self

    def set_on_stop(self, callback: Callable[[], None]) -> Self:
        """
        #### Устанавливает обработчик остановки
        
        ---
        
        :Args:
        - callback (Callable[[], None]): Функция без параметров
        
        ---
        
        :Returns:
        - self: Для цепных вызовов
        """
        self.__on_stop = callback
        return self

    def update(self) -> None:
        """
        #### Проверяет состояние звука и вызывает обработчики
        
        ---
        
        :Note:
        - Должен вызываться регулярно (например, в основном цикле приложения)
        - Автоматически определяет изменение состояния звука
        
        ---
        
        :Example:
        ```python
        while True:
            listener.update()
            # Другая логика...
        ```
        """
        current_status = self.__sound.get_status()
        self._update_statuses()
        
        if current_status == self.__last_status:
            return
            
        if current_status == AudioStatus.PLAYING:
            if self.__on_play is not None:
                self.__on_play()
            self.__played = True
                
        elif current_status == AudioStatus.PAUSED:
            if self.__on_pause is not None:
                self.__on_pause()
            self.__paused = True
                
        elif current_status == AudioStatus.STOPPED:
            if self.__on_stop is not None:
                self.__on_stop()
            self.__stopped = True
                
        self.__last_status = current_status

    def get_last_status(self) -> AudioStatus:
        """
        #### Возвращает последнее зафиксированное состояние
        
        ---
        
        :Returns:
        - AudioStatus: Текущий статус воспроизведения
        
        ---
        
        :Example:
        ```python
        status = listener.get_last_status()
        ```
        """
        return self.__last_status

class MultiSound:
    """
    #### Класс для одновременного воспроизведения нескольких экземпляров одного звука
    
    ---
    
    :Description:
    - Позволяет воспроизводить один звук многократно без перекрытия предыдущих воспроизведений
    - Управляет несколькими копиями звука для плавного многократного воспроизведения
    """
    
    def __init__(self, sound: Sound, number_of_channels: int = 3) -> Self:
        """
        #### Инициализирует мультизвук
        
        ---
        
        :Args:
        - sound (Sound): Исходный звук для копирования
        - number_of_channels (int): Количество звуковых каналов (по умолчанию 3)
        
        ---
        
        :Raises:
        - ValueError: Если количество каналов меньше 1
        
        ---
        
        :Example:
        ```python
        multi_sound = MultiSound(sound, 5)  # Создаст 5 каналов для воспроизведения
        ```
        """
        if number_of_channels < 1:
            raise ValueError("Number of channels must be at least 1")

        self.__original_sound: Sound = sound
        self.__number_of_channels: int = number_of_channels
        self.__sounds: list[Sound] = [sound.copy() for _ in range(self.__number_of_channels)]
        self.__current_sound: int = 0
        self.__position: tuple[float, float, float] = (0, 0, 0)

    def auto_play(self) -> Self:
        """
        #### Автоматически воспроизводит звук, переключая каналы
        
        ---
        
        :Note:
        - Воспроизводит текущий звук и автоматически переключается на следующий канал
        - Циклически перебирает все доступные каналы
        """
        self.__sounds[self.__current_sound].play()
        self.__current_sound = (self.__current_sound + 1) % self.__number_of_channels

        return self

    # //////////////////////////////////////////////////////////////////////////////////////////
    # Методы по отдельности для удобства контроля воспроизведения
    # //////////////////////////////////////////////////////////////////////////////////////////
    
    def play(self) -> Self:
        """
        #### Воспроизводит текущий звук
        
        ---
        
        :Note:
        - Не переключает автоматически на следующий канал
        - Для автоматического переключения используйте auto_play()
        """
        self.__sounds[self.__current_sound].play()
        return self

    def next(self) -> Self:
        """
        #### Переключает на следующий звуковой канал
        
        ---
        
        :Note:
        - Циклически перебирает все доступные каналы
        - Не воспроизводит звук автоматически
        """
        self.__current_sound = (self.__current_sound + 1) % self.__number_of_channels
        return Self

    # //////////////////////////////////////////////////////////////////////////////////////////

    def stop(self) -> Self:
        """
        #### Останавливает текущий звук
        
        ---
        
        :Note:
        - Воздействует только на активный в данный момент канал
        """
        self.__sounds[self.__current_sound].stop()
        return self

    def pause(self) -> Self:
        """
        #### Приостанавливает текущий звук
        
        ---
        
        :Note:
        - Воздействует только на активный в данный момент канал
        """
        self.__sounds[self.__current_sound].pause()
        return self

    def stop_all(self) -> Self:
        """
        #### Останавливает все звуки во всех каналах
        
        ---
        
        :Note:
        - Полностью останавливает воспроизведение на всех каналах
        """
        for sound in self.__sounds:
            sound.stop()
        return self

    def pause_all(self) -> Self:
        """
        #### Приостанавливает все звуки во всех каналах
        
        ---
        
        :Note:
        - Приостанавливает воспроизведение на всех каналах
        - Можно возобновить с помощью play()
        """
        for sound in self.__sounds:
            sound.pause()
        return self

    def add_chanel(self, count: int = 1) -> Self:
        """
        #### Добавляет новый канал для воспроизведения
        
        ---
        
        :Note:
        - Создает новую копию оригинального звука
        - Увеличивает общее количество доступных каналов
        """
        for _ in range(count):
            self.__sounds.append(self.__original_sound.copy())
            self.__number_of_channels += 1
        return self

    def remove_chanel(self, index: int) -> Self:
        """
        #### Удаляет канал по указанному индексу
        
        ---
        
        :Args:
        - index (int): Индекс канала для удаления (начиная с 0)
        
        ---
        
        :Raises:
        - ValueError: Если указан недопустимый индекс
        
        ---
        
        :Note:
        - Уменьшает общее количество доступных каналов
        - Может изменить текущий активный канал, если удаляется канал с меньшим индексом
        """
        if index >= self.__number_of_channels:
            raise ValueError("Invalid channel index")
        del self.__sounds[index]
        self.__number_of_channels -= 1
        return self

    def set_position_all(self, x: float, y: float, z: float) -> None:
        """
        #### Устанавливает позицию для всех звуков
        
        ---
        
        :Args:
        - x (float): Координата X в 3D пространстве
        - y (float): Координата Y в 3D пространстве
        - z (float): Координата Z в 3D пространстве
        
        ---
        
        :Note:
        - Обновляет позицию для всех существующих каналов
        - Запоминает позицию для будущих каналов
        """
        self.__position = (x, y, z)
        for sound in self.__sounds:
            sound.set_position(x, y, z)

    def get_position_all(self) -> tuple[float, float, float]:
        """
        #### Возвращает текущую позицию всех звуков
        
        ---
        
        :Returns:
        - tuple[float, float, float]: Текущие координаты (x, y, z)
        """
        return self.__position

    def set_position_current(self, x: float, y: float, z: float) -> None:
        """
        #### Устанавливает позицию только для текущего звука
        
        ---
        
        :Args:
        - x (float): Координата X
        - y (float): Координата Y
        - z (float): Координата Z
        
        ---
        
        :Note:
        - Не изменяет позицию для других каналов
        - Не обновляет общую позицию
        """
        self.__sounds[self.__current_sound].set_position(x, y, z)

    def set_position_at(self, index: int, x: float, y: float, z: float) -> None:
        """
        #### Устанавливает позицию для конкретного канала
        
        ---
        
        :Args:
        - index (int): Индекс канала (начиная с 0)
        - x (float): Координата X
        - y (float): Координата Y
        - z (float): Координата Z
        
        ---
        
        :Raises:
        - ValueError: Если указан недопустимый индекс
        
        ---
        
        :Note:
        - Не изменяет позицию для других каналов
        - Не обновляет общую позицию
        """
        if index >= self.__number_of_channels:
            raise ValueError("Invalid channel index")
        self.__sounds[index].set_position(x, y, z)

    def set_volume_all(self, volume: float) -> Self:
        """
        #### Устанавливает громкость для всех каналов
        
        ---
        
        :Args:
        - volume (float): Уровень громкости (0.0 - 1.0)
        """
        for sound in self.__sounds:
            sound.set_volume(volume)
        return self

    def set_volume_current(self, volume: float) -> None:
        """
        #### Устанавливает громкость только для текущего канала
        
        ---
        
        :Args:
        - volume (float): Уровень громкости (0.0 - 1.0)
        """
        self.__sounds[self.__current_sound].set_volume(volume)

    def set_volume_at(self, index: int, volume: float) -> None:
        """
        #### Устанавливает громкость для конкретного канала
        
        ---
        
        :Args:
        - index (int): Индекс канала
        - volume (float): Уровень громкости (0.0 - 1.0)
        
        ---
        
        :Raises:
        - ValueError: Если указан недопустимый индекс
        """
        if index >= self.__number_of_channels:
            raise ValueError("Invalid channel index")
        self.__sounds[index].set_volume(volume)

    def set_loop_all(self, loop: bool) -> None:
        """
        #### Устанавливает цикличность воспроизведения для всех каналов
        
        ---
        
        :Args:
        - loop (bool): Флаг цикличности (True - зациклить)
        """
        for sound in self.__sounds:
            sound.set_loop(loop)

    def set_loop_current(self, loop: bool) -> None:
        """
        #### Устанавливает цикличность только для текущего канала
        
        ---
        
        :Args:
        - loop (bool): Флаг цикличности (True - зациклить)
        """
        self.__sounds[self.__current_sound].set_loop(loop)

    def set_loop_at(self, index: int, loop: bool) -> None:
        """
        #### Устанавливает цикличность для конкретного канала
        
        ---
        
        :Args:
        - index (int): Индекс канала
        - loop (bool): Флаг цикличности (True - зациклить)
        
        ---
        
        :Raises:
        - ValueError: Если указан недопустимый индекс
        """
        if index >= self.__number_of_channels:
            raise ValueError("Invalid channel index")
        self.__sounds[index].set_loop(loop)

    def set_pitch_all(self, pitch: float) -> None:
        """
        #### Устанавливает высоту тона для всех каналов
        
        ---
        
        :Args:
        - pitch (float): Высота тона (1.0 - нормальная)
        """
        for sound in self.__sounds:
            sound.set_pitch(pitch)

    def set_pitch_current(self, pitch: float) -> None:
        """
        #### Устанавливает высоту тона только для текущего канала
        
        ---
        
        :Args:
        - pitch (float): Высота тона (1.0 - нормальная)
        """
        self.__sounds[self.__current_sound].set_pitch(pitch)

    def set_pitch_at(self, index: int, pitch: float) -> None:
        """
        #### Устанавливает высоту тона для конкретного канала
        
        ---
        
        :Args:
        - index (int): Индекс канала
        - pitch (float): Высота тона (1.0 - нормальная)
        
        ---
        
        :Raises:
        - ValueError: Если указан недопустимый индекс
        """
        if index >= self.__number_of_channels:
            raise ValueError("Invalid channel index")
        self.__sounds[index].set_pitch(pitch)

    def get_current_sound(self) -> Sound:
        """
        #### Возвращает текущий активный звук
        
        ---
        
        :Returns:
        - Sound: Текущий активный звуковой объект
        """
        return self.__sounds[self.__current_sound]
    
    def get_current_sound_index(self) -> int:
        """
        #### Возвращает индекс текущего активного звука
        
        ---
        
        :Returns:
        - int: Индекс текущего канала (начиная с 0)
        """
        return self.__current_sound
    
    def get_number_of_channels(self) -> int:
        """
        #### Возвращает общее количество каналов
        
        ---
        
        :Returns:
        - int: Количество доступных каналов воспроизведения
        """
        return self.__number_of_channels
    
    def get_original_sound(self) -> Sound:
        """
        #### Возвращает исходный звуковой объект
        
        ---
        
        :Returns:
        - Sound: Оригинальный звук, используемый для создания каналов
        """
        return self.__original_sound
    
    def get_sound(self, index: int) -> Sound:
        """
        #### Возвращает звук по указанному индексу
        
        ---
        
        :Args:
        - index (int): Индекс канала
        
        ---
        
        :Returns:
        - Sound: Звуковой объект по указанному индексу
        
        ---
        
        :Raises:
        - ValueError: Если указан недопустимый индекс
        """
        if index >= self.__number_of_channels:
            raise ValueError("Invalid channel index")
        return self.__sounds[index]
    
    def get_sounds(self) -> list[Sound]:
        """
        #### Возвращает список всех звуковых объектов
        
        ---
        
        :Returns:
        - list[Sound]: Список всех звуков (каналов)
        """
        return self.__sounds