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