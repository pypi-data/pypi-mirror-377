import warnings  
def default_logger(model, X, y, path, sample_size):
    warnings.warn(f"couldn't recognize the framework of the given model... couldn't output explainations. Contributions are welcome!")
    
    
