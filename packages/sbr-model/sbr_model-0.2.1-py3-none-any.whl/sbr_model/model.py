# Contenido del archivo sbr_model/model.py

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
import copy

class StackingRegressor(BaseEstimator, RegressorMixin):
    """
    Un regresor de Stacking compatible con scikit-learn que utiliza
    validación cruzada para entrenar un meta-modelo.

    Parameters
    ----------
    base_models : list of tuples
        Una lista de tuplas con un nombre (str) y una instancia de un modelo base
        de regresión (ej. [('xgb', XGBRegressor())]).
    
    meta_model : object
        El meta-modelo de regresión que se entrenará sobre las predicciones de los modelos base.
    
    n_folds : int, default=5
        El número de pliegues para la validación cruzada.
    """
    def __init__(self, base_models, meta_model, n_folds=5):
        self.base_models = base_models
        self.meta_model = meta_model
        self.n_folds = n_folds

    def fit(self, X, y):
        """Entrena el ensamblaje de Stacking."""
        X, y = check_X_y(X, y)
        self.X_ = X
        self.y_ = y
        
        self.base_models_ = [copy.deepcopy(model) for _, model in self.base_models]
        self.meta_model_ = copy.deepcopy(self.meta_model)
        
        kf = KFold(n_splits=self.n_folds, shuffle=True, random_state=42)
        
        oof_preds = np.zeros((X.shape[0], len(self.base_models_)))

        for i, model in enumerate(self.base_models_):
            for train_idx, val_idx in kf.split(X, y):
                X_train, y_train = X[train_idx], y[train_idx]
                X_val = X[val_idx]
                
                model.fit(X_train, y_train)
                # La única diferencia clave: usamos .predict()
                oof_preds[val_idx, i] = model.predict(X_val)

        self.meta_model_.fit(oof_preds, y)

        for model in self.base_models_:
            model.fit(self.X_, self.y_)

        return self

    def predict(self, X):
        """Genera predicciones para nuevas muestras."""
        check_is_fitted(self)
        X = check_array(X)
        
        meta_features = np.column_stack([
            model.predict(X) for model in self.base_models_
        ])
        
        return self.meta_model_.predict(meta_features)