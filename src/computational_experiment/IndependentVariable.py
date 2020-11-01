from abc import ABC, abstractmethod
from enum import Enum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .Experiment import Experiment
else:
    Experiment = 'Experiment'


class IndependentVariableSetType(Enum):
    CATEGORICAL = 0
    RANGE = 1


class IndependentVariableSet(ABC):

    def __init__(
        self,
        name: str,
        display_name: str = None,
        display_name_short: str = None
    ):
        self.name = name
        self.display_name = display_name if display_name is not None else name
        self.display_name_short = display_name_short if display_name_short is not None else display_name

    @property
    @abstractmethod
    def set_type(self):
        pass

    @abstractmethod
    def generator(self, experiment: Experiment):
        pass


class IndependentVariableInstance(ABC):

    @property
    @abstractmethod
    def value(self):
        pass


class IndependentVariable:

    experiment: Experiment
    set: IndependentVariableSet
    instances: List[IndependentVariableInstance]

    def __init__(self, experiment: Experiment, set: IndependentVariableSet):
        self.experiment = experiment
        self.set = set
        self.instances = set.generator(self.experiment)


class CategoricalIndependentVariableInstance(IndependentVariableInstance):

    def __init__(self, value, display_value: str = None, display_value_short: str = None):
        self._value = value
        self.display_value = display_value if display_value is not None else value
        self.display_value_short = display_value_short if display_value_short is not None else self.display_value

    @property
    def value(self):
        return self._value


class CategoricalIndependentVariableSet(IndependentVariableSet):

    set_type = IndependentVariableSetType.CATEGORICAL

    @abstractmethod
    def generator(self, experiment: Experiment):
        pass



