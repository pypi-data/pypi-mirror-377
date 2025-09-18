# The job of this logger file is to take in the model, and get the SHAP values depending upon the details of the model.
# We don't need to check for different families in xgboost like we did in sklearn because xgboost, by it's nature, only contains tree based models.
# The only thing we need to worry about right now is to find out the task that model is doing, be it regression or classification.

# SHAP is being imported for explainations. sklearn's "is_classifier", "is_regressor" are being imported to find out task of the given model.
# The log_saver is being imported for the exact reason it was imported in sklearn_logger.

import shap
from sklearn.base import is_classifier, is_regressor
from ..saver import log_saver

def xgboost_logger(model, X, y, path):
    # For whatever case, xgboost only needs TreeExplainer. None else is needed.
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)
    if is_classifier(model):
        task = "classifier"
    elif is_regressor(model):
        task = "regressor"
    else:
        task = "Unknown"

    # sending the results we got in the logger file to the saver for saving purposes.
    return log_saver("xgboost", "TreeExplainer",model, shap_values, X, y, path,"tree" ,task)

