from typing import Callable, Dict, List

from .TestCase import TestCase
from .Trial import Trial


class Metric:

    def __init__(
        self,
        name: str,
        fun: Callable[[TestCase], float],
        display_name: str = None,
        display_name_short: str = None
    ):
        self.name = name
        self._fun = fun
        self.display_name = display_name if display_name is not None else self.name
        self.display_name_short = display_name_short if display_name_short is not None else self.display_name

    def evaluate(self, test_case: TestCase):
        return self._fun(test_case)

    def compute_test_set(self, trial: Trial, ind: int) -> float:
        return self._fun(trial.outputs[ind], trial.get_test_set(ind))

    def compute_trial(self, trial: Trial) -> List[float]:
        return [self._fun(trial.outputs[ind], trial.get_test_set(ind)) for ind in range(len(trial.outputs))]

