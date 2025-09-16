# Contenido del archivo sbc_model/model.py

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
import copy

class StackingModel(BaseEstimator, ClassifierMixin):
    """
    Un clasificador de Stacking compatible con scikit-learn que utiliza
    validación cruzada para entrenar un meta-modelo.

    Parameters
    ----------
    base_models : list of tuples
        Una lista de tuplas donde cada una contiene un nombre (str) y una instancia
        de un modelo base de clasificación (ej. [('xgb', XGBClassifier())]).
    
    meta_model : object
        El meta-modelo que se entrenará sobre las predicciones de los modelos base.
    
    n_folds : int, default=5
        El número de pliegues a usar en la validación cruzada para generar las
        predicciones "out-of-fold".
    """
    def __init__(self, base_models, meta_model, n_folds=5):
        self.base_models = base_models
        self.meta_model = meta_model
        self.n_folds = n_folds

    def fit(self, X, y):
        """
        Entrena el ensamblaje de Stacking.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Los datos de entrenamiento.
        
        y : array-like of shape (n_samples,)
            La variable objetivo.

        Returns
        -------
        self : object
            Retorna la instancia del modelo entrenado.
        """
        # Validar y convertir los datos de entrada
        X, y = check_X_y(X, y)
        self.X_ = X
        self.y_ = y
        
        # Guardar una copia de los modelos originales para no modificarlos
        self.base_models_ = [copy.deepcopy(model) for _, model in self.base_models]
        self.meta_model_ = copy.deepcopy(self.meta_model)
        
        kf = KFold(n_splits=self.n_folds, shuffle=True, random_state=42)
        
        # Generar predicciones "out-of-fold" (OOF)
        oof_preds = np.zeros((X.shape[0], len(self.base_models_)))

        for i, model in enumerate(self.base_models_):
            for train_idx, val_idx in kf.split(X, y):
                X_train, y_train = X[train_idx], y[train_idx]
                X_val = X[val_idx]
                
                model.fit(X_train, y_train)
                oof_preds[val_idx, i] = model.predict_proba(X_val)[:, 1]

        # Entrenar el meta-modelo con las predicciones OOF
        self.meta_model_.fit(oof_preds, y)

        # Re-entrenar los modelos base con todos los datos de entrenamiento
        # para que estén listos para `.predict_proba()`
        for model in self.base_models_:
            model.fit(self.X_, self.y_)

        return self

    def predict_proba(self, X):
        """
        Genera predicciones de probabilidad para nuevas muestras.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Los datos para los que se generarán predicciones.

        Returns
        -------
        proba : array-like of shape (n_samples, n_classes)
            Las probabilidades para cada clase.
        """
        # Verificar que el modelo ha sido entrenado
        check_is_fitted(self)
        X = check_array(X)
        
        # Generar las predicciones de los modelos base (meta-features)
        meta_features = np.column_stack([
            model.predict_proba(X)[:, 1] for model in self.base_models_
        ])
        
        # Devolver la predicción final del meta-modelo
        return self.meta_model_.predict_proba(meta_features)