import numpy as np
from pandas import DataFrame
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .Experiment import Experiment
else:
    Experiment = 'Experiment'


class Results:

    def __init__(self, experiment: Experiment):
        self.experiment = experiment

    @property
    def completed_trials(self):
        return self.experiment.completed_trials

    @property
    def metrics(self):
        return self.experiment.metrics

    @property
    def metric_names(self):
        return self.experiment.metric_names

    @property
    def metric_values_3d(self) -> np.array:
        # 3D array of metric values
        #   dim 1: completed trial index
        #   dim 2: independent variable index
        #   dim 3: metric index
        completed_trials = self.completed_trials
        if not len(completed_trials):
            return np.zeros((0, 0, 0))
        num_trials = len(completed_trials)
        num_metrics = len(self.metrics)
        metric_values = np.zeros((num_trials, self.experiment.n_iv_instances, num_metrics))
        for metric_ind in range(num_metrics):
            metric = self.metrics[metric_ind]
            for trial_ind in range(num_trials):
                metric_values[trial_ind, :, metric_ind] = np.array(
                    [metric.evaluate(self.experiment.TestCaseClass(completed_trials[trial_ind], iv_ind))
                     for iv_ind in range(self.experiment.n_iv_instances)]
                )
        return metric_values

    @property
    def completed_trials_metric_values_dict_2d(self) -> Dict[str, np.array]:
        ctmv3d = self.metric_values_3d
        return {
            metric_name: ctmv3d[:, :, i] for i, metric_name in enumerate(self.metric_names)
        }

    @property
    def completed_trials_metric_values_dict_df(self) -> Dict[str, DataFrame]:
        ctmv3d = self.metric_values_3d
        return {
            metric_name: DataFrame(ctmv3d[:, :, i]) for i, metric_name in enumerate(self.metric_names)
        }

    @property
    def completed_trials_metric_stats(self) -> Dict[str, DataFrame]:
        # Return a dict of metric_name: val, where val is a data frame of statistic x independent variable from
        # DataFrame.describe
        ctmvdf = self.completed_trials_metric_values_dict_df
        return {
            metric_name: df.describe(percentiles=[0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95])
            for metric_name, df in ctmvdf.items()
        }

    @property
    def completed_trials_iv_stats(self) -> List[DataFrame]:
        # Return a list, giving for each independent variable a DataFrame of summary statistic x metric over trials
        return [
            df.describe(percentiles=[0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95])
            for df in self.completed_trials_iv_values_df
        ]

    @property
    def completed_trials_iv_values_df(self) -> List[DataFrame]:
        # Return a list, giving for each independent variable a DataFrame of trial x metric value
        ctmv3d = self.metric_values_3d
        completed_trials = self.completed_trials
        num_trials = len(completed_trials)
        num_metrics = len(self.metrics)
        return [
            DataFrame(ctmv3d[:, i, :].reshape(num_trials, num_metrics), columns=self.metric_names)
            for i in range(self.experiment.n_iv_instances)
        ]
