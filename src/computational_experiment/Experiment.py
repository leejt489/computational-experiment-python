from abc import ABC, abstractmethod
import json
import numpy as np
from numpy.random import SeedSequence, default_rng, MT19937, RandomState, Generator
from os import path, makedirs
from pandas import DataFrame
from typing import List, Tuple, Dict

from .IndependentVariable import IndependentVariable, IndependentVariableSet
from .Metric import Metric
from .Output import Output
from .Results import Results
from .TestCase import TestCase
from .TestSet import TestSet
from .Trial import Trial


class Experiment(ABC):

    independent_variable: IndependentVariable
    n_trials: int

    OutputClass = Output
    TestCaseClass = TestCase
    TestSetClass = TestSet

    _rng: Generator
    _rand_state: RandomState
    _trial_seeds: List[SeedSequence]
    _test_seeds: List[SeedSequence]

    def __init__(
            self,
            name: str,
            independent_variable_set: IndependentVariableSet,
            case_name: str = 'default', data_dir: str = 'data'
    ):
        self.name = name
        self.case_name = case_name
        self.data_dir = data_dir

        # Ensure directory for output data exists
        if not path.exists(f'{self.outputs_dir}/trials'):
            makedirs(f'{self.outputs_dir}/trials')

        # set up experiment parameters
        self.parameters = None
        self.load_experiment_parameters()  # load parameters from json file into self.parameters
        self.parameters = {**self.parameters, **self.generate_experiment_parameters()}
        self.n_trials = self.parameters['n_trials']
        self._rand_seed = self.parameters['rand_seed'] if 'rand_seed' in self.parameters else 0

        self._completed_trials = []
        self._completed_trials_dirty = True

        # Assign independent variables
        self.independent_variable = IndependentVariable(self, independent_variable_set)

        # Initialize random number generators
        seed_sequence = SeedSequence(self._rand_seed)
        seeds = seed_sequence.spawn(2*self.n_trials)
        self._trial_seeds = seeds[:self.n_trials]
        self._test_seeds = seeds[self.n_trials:]

    @property
    def completed_trials(self) -> List[Trial]:
        if self._completed_trials_dirty:
            self.load_completed_trials()
        return self._completed_trials

    @property
    def inputs_dir(self):
        return f'{self.data_dir}/{self.name}/inputs/{self.case_name}'

    @property
    def metric_names(self):
        return [m.name for m in self.metrics]

    @property
    def outputs_dir(self):
        return f'{self.data_dir}/{self.name}/outputs/{self.case_name}'

    @property
    def results(self) -> Results:
        return Results(self)

    @property
    def trial_ids(self) -> list:
        return list(range(self.n_trials))

    @property
    def n_iv_instances(self) -> int:
        return len(self.independent_variable.instances)

    @property
    @abstractmethod
    def metrics(self) -> List[Metric]:
        pass

    @abstractmethod
    def generate_experiment_parameters(self) -> Dict:
        pass

    @abstractmethod
    def generate_confounding_variables(self, trial_ind: int) -> Dict:
        pass

    @abstractmethod
    def simulate_test_set(self, test_set: TestSet) -> Output:
        pass

    def load_experiment_parameters(self):
        with open(f'{self.inputs_dir}/parameters.json') as f:
            self.parameters = json.load(f)

    def load_trial(self, trial_id) -> Trial:
        with open(f'{self.outputs_dir}/trials/{trial_id}.json', 'r') as f:
            return Trial.from_dict(trial_id, self, json.load(f))

    def load_all_trials(self) -> List[Trial]:
        return [self.load_trial(trial_id) for trial_id in self.trial_ids]

    def load_completed_trials(self) -> Tuple[List[Trial], List]:
        completed_trials = []
        completed_trial_ids = []
        for trial_id in self.trial_ids:
            try:
                trial = self.load_trial(trial_id)
                if trial.is_completed:
                    completed_trials.append(trial)
                    completed_trial_ids.append(trial_id)
            except FileNotFoundError:
                pass
        self._completed_trials = completed_trials
        self._completed_trials_dirty = False
        return completed_trials, completed_trial_ids

    def plot_all_metrics(self):
        pass

    def run_experiment(self):
        self.run_trials_serially()

    def run_trial(self, trial_ind, use_saved_cvs=False) -> Trial:
        print(f'Starting trial {trial_ind}...')

        # Initialize random number generators
        self._rng = default_rng(self._trial_seeds[trial_ind])
        self._rand_state = RandomState(MT19937(self._trial_seeds[trial_ind]))

        trial_loaded = False
        if use_saved_cvs:
            try:
                trial = self.load_trial(trial_ind)
                trial.is_completed = False
                print(f'Using saved confounding variables for trial {trial_ind}')
                trial_loaded = True
            except FileNotFoundError:
                trial_loaded = False
        if not trial_loaded:
            trial = Trial(trial_ind, self)
            # Generate confounding variables
            print(f'Generating confounding variables for trial {trial_ind}...')
            trial.confounding_variables = self.generate_confounding_variables(trial_ind)
            print(f'...confounding variables generated for trial {trial_ind}')

        self.save_trial(trial)
        trial.outputs = [] * self.n_iv_instances
        for ind in range(self.n_iv_instances):
            # Initialize random number generators
            self._rng = default_rng(self._test_seeds[trial_ind])
            self._rand_state = RandomState(MT19937(self._test_seeds[trial_ind]))
            print(f'Simulating independent variables {ind+1} of {self.n_iv_instances} for trial {trial_ind}...')
            output = self.simulate_test_set(self.TestSetClass(trial, ind))
            trial.outputs[ind] = output
            print('...done')
        trial.is_completed = True
        print(f'...completed trial {trial_ind}')
        return trial

    def run_trials_serially(self, start_trial: int = 0, end_trial: int = None, use_saved_cvs=False) -> List[Trial]:
        if end_trial is None:
            end_trial = self.n_trials-1

        print(f'Running experiment "{self.name}" serially, trials {start_trial} to {end_trial-1} (inclusive)...')

        trials = []
        for trial_ind in self.trial_ids[start_trial:end_trial+1]:
            trial = self.run_trial(trial_ind, use_saved_cvs=use_saved_cvs)
            self.save_trial(trial)
            trials.append(trial)

        return trials

    def save_trial(self, trial: Trial):
        with open(f'{self.outputs_dir}/trials/{trial.id}.json', 'w') as f:
            json.dump(trial.to_dict(), f)
        self._completed_trials_dirty = True
