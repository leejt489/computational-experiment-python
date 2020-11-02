from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .Experiment import Experiment
    from .IndependentVariable import IndependentVariableInstance
    from .Output import Output
    from .TestCase import TestCase
    from .TestSet import TestSet
else:
    Experiment = 'Experiment'
    IndependentVariableInstance = 'IndependentVariableInstance'
    Output = 'Output'
    TestCase = 'TestCase'
    TestSet = 'TestSet'


class Trial:

    experiment: Experiment
    outputs: List[Output]

    def __init__(self, id: int, experiment: Experiment):
        self.id = id
        self.experiment = experiment
        self.confounding_variables = None
        self.is_completed = False
        self.outputs = []

    @property
    def independent_variable_instances(self) -> List[IndependentVariableInstance]:
        return self.experiment.independent_variable.instances

    @staticmethod
    def from_dict(id, experiment: Experiment, dict_data: Dict):
        trial = Trial(id, experiment)
        trial.confounding_variables = dict_data['confounding_variables']
        trial.outputs = [trial.experiment.OutputClass.from_dict(output_dict) for output_dict in dict_data['outputs']]
        trial.is_completed = dict_data['is_completed']
        return trial

    def to_dict(self):
        return {
            'is_completed': self.is_completed,
            'confounding_variables': self.confounding_variables,
            'outputs': [output.to_json_serializable() for output in self.outputs]
        }

    def get_test_case(self, ind: int) -> TestCase:
        return self.experiment.TestCaseClass(self, ind)

    def get_test_set(self, ind: int) -> TestSet:
        return self.experiment.TestSetClass(self, ind)
