from ....base.Metric import Metric
from pate.PATE_metric import PATE


class PateFScore(Metric):
    """
    Calculate PATE score for anomaly detection in time series.
    
    PATE evaluates predictions by assigning weighted scores based on temporal proximity 
    to true anomaly intervals. It uses buffer zones around each true anomaly: an early buffer of length
    `early` preceding the interval and a delay buffer of length `delay` following it. Detections within
    the true interval receive full weight, while those in the early or delay buffers receive linearly
    decaying weights based on distance from the interval edges. Predictions outside these zones are
    treated as false positives, and missed intervals as false negatives. The final score balances these
    weighted detections into a single measure of performance.

    Implementation of https://arxiv.org/abs/2405.12096
    
    For more information, see the original paper:
    https://arxiv.org/abs/2405.12096

    Parameters:
        early (int):
            The maximum number of time steps before an anomaly must be predicted to be considered early.
        delay (int):
            The maximum number of time steps after an anomaly must be predicted to be considered delayed.
    """
    name = "pate_f1"
    binary_prediction = True
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
        super().__init__(name="pate_f1", **kwargs)

    def _compute(self, y_true, y_pred):
        """
        Calculate the PATE score.

        Parameters:
            y_true (np.array):
                The ground truth binary labels for the time series data.
            y_pred (np.array):
                The predicted binary labels for the time series data.

        Returns:
            float: The PATE score.
        """

        early = self.params["early"]
        delay = self.params["delay"]

        return PATE(y_true, y_pred, early, delay, binary_scores=True)