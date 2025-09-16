from ....base.Metric import Metric
from pate.PATE_metric import PATE
import numpy as np


class Pate(Metric):
    """
    Calculate PATE score for anomaly detection in time series using real-valued anomaly scores.

    This version of PATE evaluates real-valued anomaly scores by assigning weights to predictions 
    based on their temporal proximity to the true anomaly intervals. It defines an early buffer of 
    length `early` before each anomaly and a delay buffer of length `delay` after it. Detections with 
    high scores within the anomaly interval receive full weight, while those in the buffer zones are 
    assigned linearly decaying weights depending on their distance from the interval. Scores outside 
    these zones contribute to false positives, and intervals with insufficient detection are penalized 
    as false negatives.

    The final PATE score aggregates these weighted contributions across all time steps, yielding 
    a smooth performance measure that is sensitive to both the timing and confidence of the predictions.

    Implementation of https://arxiv.org/abs/2405.12096

    For more information, see the original paper:
    https://arxiv.org/abs/2405.12096

    Parameters:
        early (int):
            Length of the early buffer zone before each anomaly interval.
        delay (int):
            Length of the delay buffer zone after each anomaly interval.
    """
    name = "pate"
    binary_prediction = False
    param_schema = {
        "early": {
            "default": 5,
            "type": int
        },
        "delay": {
            "default": 5,
            "type": int
        }
    }

    def __init__(self, **kwargs):
        super().__init__(name="pate", **kwargs)

    def _compute(self, y_true, y_anomaly_scores):
        """
        Calculate the real-valued PATE score.

        Parameters:
            y_true (np.array):
                Ground truth binary labels (0 = normal, 1 = anomaly).
            y_anomaly_scores (np.array):
                Real-valued anomaly scores for each time point.

        Returns:
            float: The real-valued PATE score.
        """

        return PATE(y_true, y_anomaly_scores, self.params["early"], self.params["delay"], binary_scores=False)