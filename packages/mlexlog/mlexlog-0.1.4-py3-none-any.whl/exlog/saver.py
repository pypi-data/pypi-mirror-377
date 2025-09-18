import json
from pathlib import Path
import numpy as np
import warnings

# Try optional imports
try:
    import torch
except ImportError:
    torch = None

try:
    import tensorflow as tf
except ImportError:
    tf = None


def log_saver(framework, explainer, model, shap_values, X, y, path,
              family=None, task=None, import_error=False):
    logs = []

    if import_error:
        warning = {
            "type": "dependency_warning",
            "message": "A framework that you are trying to use isn't installed",
            "dependencies": framework
        }
        logs.append(warning)
    else:
        flag = False

        if framework == "torch":
            if torch is None:
                warnings.warn(f"{framework} not found... install {framework} and try again")
                flag = True

        for i in range(len(shap_values.values)):
            if isinstance(X, np.ndarray):
                row = X[i]
                if framework == "torch":
                    if flag:
                        break
                    prediction = model(torch.tensor(row.reshape(1, -1), dtype=torch.float32))[0]
                else:
                    prediction = model.predict(row.reshape(1, -1))[0]
            else:
                row = X.iloc[i]
                if framework == "torch":
                    if flag:
                        break
                    prediction = model(torch.tensor([row.values], dtype=torch.float32))[0]
                else:
                    prediction = model.predict([row.values])[0]

            # Normalize predictions for JSON
            if isinstance(prediction, np.generic):
                prediction = prediction.item()  
            if isinstance(prediction, np.ndarray):
                prediction = prediction.tolist()
            if torch is not None and isinstance(prediction, torch.Tensor):
                if prediction.dim() == 0:
                    prediction = prediction.item()
                else:
                    prediction = prediction.tolist()

            record = {
                "framework": framework,
                "family": family,
                "task": task,
                "Explainer": explainer,
                "Input": row.to_dict() if hasattr(row, "to_dict") else row.tolist(),
                "Prediction": prediction,
                "Explanation": shap_values.values[i].tolist()
            }

            if framework == "unknown":
                record["Message"] = "Framework not recognized"
            if y is not None:
                if task in ("classification", "classifier"):
                    record["Prediction State"] = bool(prediction == y[i])
                else:
                    record["Prediction State"] = None

            logs.append(record)

    if framework == "torch" and flag:
        logs = [{"Error": "Couldn't import torch"}]

    return json_file_saver(logs, path)


def json_file_saver(logs, path):
    Path(path).write_text(json.dumps(logs, indent=2))
    print(f"Logs have been saved to {path}.")
    print("Contributions for the development of exlog are welcome... Let's make explainability easier.")
    return logs
