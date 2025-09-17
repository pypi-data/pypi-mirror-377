from tsadmetrics.metrics.tem.mdtp.TotalDetectedInRange import TotalDetectedInRange
from tsadmetrics.evaluation.Runner import Runner
import numpy as np

y_true = [0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
y_pred = [0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]

# Direct usage
metric = TotalDetectedInRange()
result = metric.compute(y_true, y_pred)
print("TotalDetectedInRange:", result)

# Usage with Runner
dataset_evaluations = [
    ("dataset1", y_true, (y_pred, y_pred))
]

metrics = [
    ("tdir", {})
]

runner = Runner(dataset_evaluations, metrics)
results = runner.run()
print(results)
