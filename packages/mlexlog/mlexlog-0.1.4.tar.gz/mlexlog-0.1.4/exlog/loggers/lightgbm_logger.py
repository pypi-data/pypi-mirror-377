## The only major difference between the xgboost one and this is, we need to add a warning filter for lightgbm. 
import warnings
warnings.filterwarnings(
    "ignore", message = "X does not have valid feature names*" 
)
import shap
from ..saver import log_saver
from sklearn.base import is_classifier, is_regressor
def lightgbm_logger(model, X, y, path):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)
    if is_classifier(model):
        task = "classifier"
    elif is_regressor(model):
        task = "regressor"
    else:
        task = "Unknown"
    return log_saver("lightgbm","TreeExplainer",model, shap_values, X, y, path, "tree" ,task)
