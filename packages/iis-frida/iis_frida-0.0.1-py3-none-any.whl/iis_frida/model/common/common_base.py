"""
Super Class for KIX objects
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Any, Type
from typing import Union

from iis_frida.utils.type_aliases import ApiDict


# mypy doesn't like that an abstract class is returned in parser()


@dataclass
class FridaObject(ABC):
    """
    Super class for all Frida objects. Includes common methods
    """

    # name: str

    @staticmethod
    @abstractmethod
    def parser() -> Type["FridaObjectParser"]:
        """
        :return: Parse class for parsing this concrete FridaObjectParser
        """

    # def __lt__(self, other: "FridaObject") -> bool:
    #     return self.name < other.name


class FridaObjectParser(ABC):
    """
    Super class for all Kix object parser.
    """

    @staticmethod
    @abstractmethod
    def load(frida_response: ApiDict) -> FridaObject:
        """
        :param frida_response: Response of Frida API
        :return: Parsed object representing frida_response
        """

    @staticmethod
    @abstractmethod
    def dump(frida_object: FridaObject) -> ApiDict:
        """
        :param frida_object: Parsed Frida object
        :return: Format for Frida API
        """
