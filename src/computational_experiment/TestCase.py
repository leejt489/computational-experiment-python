from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Experiment import Experiment
    from .Output import Output
    from .TestSet import TestSet
    from .Trial import Trial
else:
    Experiment = 'Experiment'
    Output = 'Output'
    TestSet = 'TestSet'
    Trial = 'Trial'


class TestCase:

    trial: Trial
    test_set: TestSet
    independent_variable_ind: int
    output: Output

    def __init__(self, trial: Trial, independent_variable_ind: int):
        self.trial = trial
        self.independent_variable_ind = independent_variable_ind
        self.test_set = self.trial.get_test_set(self.independent_variable_ind)
        self.output = self.trial.outputs[independent_variable_ind]

    @property
    def experiment(self) -> Experiment:
        return self.trial.experiment

    @property
    def metric_dict(self):
        return {metric.name: metric.evaluate(self) for metric in self.trial.experiment.metrics}

