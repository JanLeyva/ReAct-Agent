from abc import ABC, abstractmethod

from .place import Place


class PlacesAPI(ABC):
    @abstractmethod
    def get_places_by_id(self) -> list[Place]:
        pass

    @abstractmethod
    def get_places_by_name(self) -> list[Place]:
        pass
