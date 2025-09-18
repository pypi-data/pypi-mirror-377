### Our core intention in this entire process is to figure out the type of model that we are dealing with, and then give the most optimal explaination for the given model.
from pathlib import Path

### We will first try to figure out the framework type with the help of python's __class__ and __module__ dunder attributes.
def detect_framework(model):
    cls = model.__class__.__module__.lower()
    if "xgboost" in cls:
        return "xgboost"
    if "lightgbm" in cls:
        return "lightgbm"
    if "sklearn" in cls:
        return "sklearn"
    if "torch" in cls:
        return "torch"
    if "tensorflow" in cls or "keras" in cls:
        return "tensorflow"
    return "unknown"

### We are going to assign a seperate function for the user's request depending upon the framework we are dealing with. Each function here solves the explanation problem in their unqiue way.
def log(model, X, y = None, path = "exlog.json", sample_size = 100):
    framework = detect_framework(model)
    if framework == "sklearn":
        from .loggers import sklearn_logger
        return sklearn_logger(model, X, y, path, sample_size)
    elif framework == "xgboost":
        from .loggers import xgboost_logger
        return xgboost_logger(model, X, y, path)
    elif framework == "lightgbm":
        from .loggers import lightgbm_logger
        return lightgbm_logger(model, X, y, path)
    elif framework == "torch" or framework == "tensorflow":
        from .loggers import torch_tensorflow_logger
        return torch_tensorflow_logger(model, X, y, path, sample_size)
    else:
        from .loggers import default_logger
        print(f"The framework '{framework}' is not supported. Falling back to kernel explainer...")
        return default_logger(model, X , y, path, sample_size)      