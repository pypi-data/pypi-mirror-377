import shap
import warnings
import numpy as np
from ..saver import log_saver

# Safe imports
try:
    import torch
except ImportError:
    torch = None

try:
    import tensorflow as tf
except ImportError:
    tf = None


def torch_tensorflow_logger(model, X, y, path, sample_size):
    framework = detect_framework(model)

    # Handle missing dependencies early
    if framework == "torch" and torch is None:
        warnings.warn("'torch' is not installed.")
        return log_saver("torch", None, None, None, None, path,
                         family=None, task=None, import_error=True)

    if framework == "tensorflow" and tf is None:
        warnings.warn("'tensorflow' is not installed.")
        return log_saver("tensorflow", None, None, None, None, path,
                         family=None, task=None, import_error=True)

    # Convert to numpy
    X_np = X.values if hasattr(X, "values") else X
    X_sample = X_np[:sample_size]

    # Define torch prediction fn only if torch is present
    def predict_fn(x_numpy):
        x_tensor = torch.tensor(x_numpy, dtype=torch.float32)
        with torch.no_grad():
            output = model(x_tensor)
        return output.detach().numpy()

    # Torch DeepExplainer
    if framework == "torch":
        try:
            X_tensor_sample = torch.tensor(X_sample, dtype=torch.float32)
            explainer = shap.DeepExplainer(model, X_tensor_sample)
            shap_values = explainer(torch.tensor(X_np, dtype=torch.float32))
            return log_saver("torch", "DeepExplainer", model, shap_values, X, y,
                             path, family="neural network", task="unknown")
        except Exception as e:
            warnings.warn(f"DeepExplainer failed for torch: {e}, using KernelExplainer...")

    # TensorFlow DeepExplainer
    elif framework == "tensorflow":
        try:
            explainer = shap.DeepExplainer(model, X_sample)
            shap_values = explainer(X_np)
            return log_saver("tensorflow", "DeepExplainer", model, shap_values, X, y,
                             path, family="neural network", task="unknown")
        except Exception as e:
            warnings.warn(f"DeepExplainer failed for tensorflow: {e}, using KernelExplainer...")

    # KernelExplainer fallback
    if hasattr(model, "predict_proba"):
        f = model.predict_proba
    elif framework == "tensorflow":
        f = model.predict
    elif framework == "torch":
        f = predict_fn
    else:
        f = lambda x: model.predict(x)

    explainer = shap.KernelExplainer(f, X_sample)
    shap_values = explainer(X_sample)
    return log_saver(framework, "KernelExplainer", model, shap_values, X, y,
                     path, family="neural network", task="unknown")


def detect_framework(model):
    cls = model.__class__.__module__.lower()
    if "torch" in cls:
        return "torch"
    if "tensorflow" in cls or "keras" in cls:
        return "tensorflow"
    return "unknown"