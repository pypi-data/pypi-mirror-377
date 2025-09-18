from inspect import signature
from typing import TypeVar, Type, Dict
from underpy import Encapsulated
from pydm.parameters_bag import ParametersBagInterface

T = TypeVar("T")
F = TypeVar("F")

class ServiceContainer(Encapsulated):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls._instance = super(ServiceContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "__services"):
            self.__services: dict[Type[T], T] = {}
            self.__binds: dict[Type[T], Type[T]] = {}
            self.__factories: dict[Type[T], tuple[Type[T], str]] = {}
            self.__mapped_params: dict[Type[T], dict[str, str]] = {}
            self.__parameters: ParametersBagInterface|None = None

    @classmethod
    def get_instance(cls) -> 'ServiceContainer':
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    def get_service(self, cls: Type[T]) -> T:
        if cls in self.__services:
            return self.__services[cls]

        if cls in self.__binds:
            return self.get_service(self.__binds[cls])

        if cls in self.__factories:
            factory = self.get_service(self.__factories[cls][0])
            # TODO: Support factory method args
            return getattr(factory, self.__factories[cls][1])()

        dependencies: dict[str, T] = {}
        arguments = signature(cls.__init__).parameters
        for arg_name, arg in arguments.items():
            if cls in self.__mapped_params and arg_name in self.__mapped_params[cls] and not self.__parameters is None:
                dependencies[arg_name] = self.__parameters.get(self.__mapped_params[cls][arg_name])
                continue

            if 'self' == arg_name or arg.VAR_POSITIONAL == arg.kind or arg.VAR_KEYWORD == arg.kind:
                continue

            arg_cls = arg.annotation
            if arg.empty == arg_cls:
                raise ValueError(f"Dependency '{arg_name}' in '{cls.__name__}' constructor is missing a type hint.")

            dependencies[arg_name] = self.get_service(arg_cls)

        instance = cls(**dependencies)
        self.__services[cls] = instance

        return instance

    def bind(self, interface: Type[T], implementation: Type[T]) -> None:
        self.__binds[interface] = implementation

    def bind_to_factory(self, cls: Type[T], factory_cls: Type[F], factory_method: str) -> None:
        self.__factories[cls] = (factory_cls, factory_method)

    def bind_parameters(self, cls: Type[T], parameters: dict[str, str]) -> None:
        self.__mapped_params[cls] = parameters

    def set_parameters(self, parameters: ParametersBagInterface) -> None:
        self.__parameters = parameters