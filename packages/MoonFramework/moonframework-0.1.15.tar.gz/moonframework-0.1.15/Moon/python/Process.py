import time
from Moon.python.Types import *
from threading import Thread


type OptionalThread = Thread | None

class Process:
    def __init__(self, id: OptionalIdentifier | None = None):
        self.__id = id if id is not None else AutoIdentifier()

        self.__thread: OptionalThread = None

        self.__func: FunctionOrMethod | None = None
        self.__func_args = None
        self.__func_kwargs = None
        self.__started = False
        self.__finished = False
        self.__error = None
        self.__daemon: bool = False

    def set_daemon(self, value: bool = True) -> Self:
        self.__daemon = value
        return self
    
    def get_daemon(self) -> bool:
        return self.__daemon

    def get_identifier(self) -> Identifier:
        return self.__id
    
    def set_function(self, func: FunctionOrMethod, *args, **kwargs) -> Self:
        self.__func = func
        self.__func_args = args
        self.__func_kwargs = kwargs
        return self

    def get_started(self) -> bool:
        return self.__started

    def get_finished(self) -> bool:
        return self.__finished
    
    def get_error(self) -> None | Exception:
        return self.__error

    def __process(self):
        try:
            self.__started = True
            self.__func(self, *self.__func_args, **self.__func_kwargs)
            self.__finished = True
        except Exception as e:
            self.__error = e
            print(self.get_error())
    
    def create_thread(self) -> Self:
        self.__thread = Thread(target=self.__process, daemon=self.__daemon)
        return self
        
    def create_thread_function(self, func: FunctionOrMethod, *args, **kwargs) -> Self:
        self.set_function(func, *args, **kwargs)
        self.create_thread()
        return self

    def start(self):
        if self.__func is None:
            raise ValueError("Function is not set")
        if self.__thread is None:
            raise ValueError("Thread object is not created")
        self.__thread.start()

class CyclicalProcess(Process):
    def __init__(self, id=None):
        super().__init__(id)
        self.__started: bool = False
        self.__stoped: bool = False
        self.__sleep: float = 0

        self.__iteration: int = 0

    def stop(self) -> None:
        self.__started = False

    def get_started(self) -> bool:
        return self.__started

    def set_sleep(self, seconds: float) -> Self:
        self.__sleep = seconds
        return self
    
    def set_frequency(self, count: int) -> Self:
        self.__sleep = 1 / count
        return self
    
    def get_frequency(self) -> float:
        return 1 / self.__sleep
    
    def get_stoped(self) -> bool:
        return self.__stoped
    
    def get_iteration(self) -> int:
        return self.__iteration

    def __process(self):
        self.__started = True
        self.__stoped = False
        try:
            while self.__started:
                # Доступ к атрибутам родительского класса через экземпляр
                self._Process__func(self, *self._Process__func_args, **self._Process__func_kwargs)
                if not self.__started: 
                    break
                if self.__sleep != 0:
                    time.sleep(self.__sleep)
                self.__iteration += 1
        except Exception as e:
            # Сохраняем ошибку в родительском классе
            self._Process__error = e
            print(self.get_error())
        finally:
            self.__stoped = True
            self._Process__finished = True

    def create_thread(self) -> Self:
        self._Process__thread = Thread(target=self.__process, daemon=self.get_daemon())
        return self
        
    def start(self):
        if self._Process__func is None:
            raise ValueError("Function is not set")
        if self._Process__thread is None:
            self.create_thread()
        self._Process__thread.start()
        return self
    
