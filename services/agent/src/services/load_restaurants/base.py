from abc import ABC, abstractmethod

from .place import Place


class PlacesAPI(ABC):
    @abstractmethod
    def get_place_id(self) -> list[Place]:
        pass

    @abstractmethod
    def get_place_info(self) -> list[Place]:
        pass
