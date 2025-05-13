from abc import ABC, abstractmethod

from place import Place

class PlacesAPI(ABC):
    @abstractmethod
    def get_places(self) -> list[Place]:
        pass
