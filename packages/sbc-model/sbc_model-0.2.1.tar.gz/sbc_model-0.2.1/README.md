# sbc-model 🤖

[![PyPI version](https://badge.fury.io/py/sbc-model.svg)](https://badge.fury.io/py/sbc-model)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un clasificador de Machine Learning fácil de usar que implementa un ensamblaje de Stacking con modelos de Boosting (XGBoost, LightGBM, CatBoost).

## ¿Qué es sbc-model? 🤔

`sbc-model` es una librería de alto nivel diseñada para simplificar el proceso de creación de modelos de ensamblaje robustos. En lugar de configurar manualmente la validación cruzada y el meta-modelo, `sbc-model` lo encapsula en una sola clase, siguiendo las mejores prácticas de scikit-learn.

El nombre **SBC** significa **S**tacking **B**oosting **C**lassifier.

---

## Características Principales ✨

* **Modelos Potentes:** Utiliza XGBoost, LightGBM y CatBoost como modelos base, tres de los algoritmos más potentes para datos tabulares.
* **Stacking Automatizado:** Gestiona automáticamente el proceso de validación cruzada para generar predicciones "out-of-fold" y entrenar un meta-modelo.
* **Fácil de Usar:** Interfaz simple inspirada en scikit-learn. Solo necesitas instanciar la clase y llamar a `.fit_predict_proba()`.
* **Reproducible:** Controla la aleatoriedad con una `seed` para asegurar que tus resultados sean consistentes.

---

## Instalación 📦

Puedes instalar `sbc-model` directamente desde PyPI:

```bash
pip install sbc-model

import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
import xgboost as xgb

# Importamos tu clase desde la librería instalada con el nuevo nombre
from sbc_model import StackingClassifier

# 1. Crear datos de ejemplo para un problema de clasificación
# Esto nos permite probar el modelo sin necesidad de un archivo CSV
X, y = make_classification(n_samples=1000, n_features=20, n_informative=10, n_redundant=5, random_state=42)
X_test, _ = make_classification(n_samples=500, n_features=20, n_informative=10, n_redundant=5, random_state=2025)

# 2. Definir los "ingredientes": modelos base y meta-modelo
base_models = [
    ('xgb', xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')),
    # Aquí podrías añadir más modelos, como LGBMClassifier o CatBoostClassifier
]
meta_model = LogisticRegression(random_state=42)

# 3. Instanciar y entrenar el modelo
sbc = StackingClassifier(base_models=base_models, meta_model=meta_model, n_folds=5)
sbc.fit(X, y)

# 4. Hacer predicciones de probabilidad
# El método devuelve las probabilidades para cada clase [clase_0, clase_1]
predictions_proba = sbc.predict_proba(X_test)

# Generalmente nos interesa la probabilidad de la clase positiva (clase 1)
positive_class_proba = predictions_proba[:, 1]

# 5. Ver los resultados
print("Primeras 10 predicciones de probabilidad para la clase positiva:")
print(positive_class_proba[:10])