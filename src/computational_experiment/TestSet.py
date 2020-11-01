from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .Experiment import Experiment
else:
    Experiment = 'Experiment'

from .IndependentVariable import IndependentVariableInstance
from .Trial import Trial


class TestSet:

    experiment: Experiment
    trial: Trial
    confounding_variables: Dict
    independent_variable_instance: IndependentVariableInstance

    def __init__(self, trial: Trial, case_ind: int):
        self.experiment = trial.experiment
        self.trial = trial
        self.confounding_variables = trial.confounding_variables
        self.independent_variable_instance = self.experiment.independent_variable.instances[case_ind]
