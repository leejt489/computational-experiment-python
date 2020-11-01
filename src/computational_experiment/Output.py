from abc import ABC, abstractmethod
from typing import Dict


class Output(ABC):

    @staticmethod
    @abstractmethod
    def from_dict(d: Dict) -> 'Output':
        pass

    @property
    @abstractmethod
    def to_json_serializable(self) -> Dict:
        pass
