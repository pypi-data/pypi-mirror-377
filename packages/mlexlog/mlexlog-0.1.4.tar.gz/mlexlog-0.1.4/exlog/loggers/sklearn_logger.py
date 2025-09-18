### imports: We have shap here because they are our explainers. We are also importing log_saver from the saver file.

import shap
from ..saver import log_saver

### In order to apply the correct explainer of SHAP, we first have to indentify the kind of model we have in our hands
### If we ended up in sklearn_logger, it means that no matter the model,  it belongs to the sklearn library. 
### Sklearn has several types of models. Most important of those are:
### 1. Linear, 2. Tree, 3. svm related models, 4. KNN related models, 5. Naive Bayes.
### I created support for all the mentioned models.


# What this function does is, it isolates the family (the kind of model) of the model, and the task it does (regression or classification).
def model_type(model):
        output = [None]*2
        name = model.__class__.__name__.lower()
        module = model.__class__.__module__.lower()
        if hasattr(model, "coef_"):
                output[0] = ("linear")
                type_ = model._estimator_type
        elif hasattr(model, "tree_") or hasattr(model, "estimators_"):
                output[0] = ("tree")
                type_ = model._estimator_type
        elif hasattr(model, "support_vectors_") or "svm" in module or "svc" in name or "svr" in name:
                output[0] = ("svm")
                type_ = model._estimator_type
        elif "neighbors" in module or "kneighbors" in dir(model):
                output[0] = ("neighbors")
                type_ = model._estimator_type
        elif "naive_bayes" in module:
                output[0] = ("naive_bayes")
                type_ = model._estimator_type
        else:
                output[0] = ("unknown")
                type_ = "unknown"
        output[1] = (type_)
        return output


def sklearn_logger(model, X, y, path, sample_size):
        ### We are using the function we created earlier to extract the neccesarry information.
        explainer_name = None
        output = model_type(model)
        family = output[0]
        task = output[1]

        # Depending upon the extracted information, we are attempting to use the correct SHAP explainer in play. We also added a default case error handling line that ensures we cover all the edge cases.
        if family == "linear":
                explainer = shap.Explainer(model , X)
                shap_values = explainer(X)
                explainer_name = "Explainer"
        elif family == "tree":
                explainer = shap.TreeExplainer(model , X)
                shap_values = explainer(X, check_additivity = False)
                explainer_name = "TreeExplainer"
        elif family == "svm" or family == "neighbors" or family == "naive_bayes" or family == "unknown":
                print(f"Model not supported by explainer in shap... using kernelExplainer. using a sample for speed...")
                sample = X[:sample_size]
                if hasattr(model, "predict_proba"):
                        explainer = shap.KernelExplainer(lambda x: model.predict_proba(x) , sample)
                else:
                        explainer = shap.KernelExplainer(lambda x: model.predict(x) , sample)
                explainer_name = "KernelExplainer"
                shap_values = explainer(sample)
        else:
                raise ValueError(f"Unsupported model type: {family}")
        # All the extracted information is then passed into the log_saver function that we imported from the "saver.py" file. 
        return log_saver("sklearn", explainer_name, model, shap_values, X , y, path, family, task)

