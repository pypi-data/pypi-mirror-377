# sbr-model 📈

[![PyPI version](https://badge.fury.io/py/sbr-model.svg)](https://badge.fury.io/py/sbr-model)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Un regresor de Machine Learning fácil de usar que implementa un ensamblaje de Stacking con modelos de Boosting (XGBoost, LightGBM, CatBoost).

## ¿Qué es sbr-model? 🤔

`sbr-model` es una librería de alto nivel diseñada para simplificar el proceso de creación de modelos de ensamblaje robustos para tareas de **regresión**. En lugar de configurar manualmente la validación cruzada y el meta-modelo, `sbr-model` lo encapsula en una sola clase, compatible con scikit-learn.

El nombre **SBR** significa **S**tacking **B**oosting **R**egressor.

---

## Características Principales ✨

* **Modelos Potentes:** Utiliza XGBoost, LightGBM y CatBoost como modelos base, tres de los algoritmos más potentes para datos tabulares.
* **Stacking Automatizado:** Gestiona automáticamente el proceso de validación cruzada para generar predicciones "out-of-fold" y entrenar un meta-modelo.
* **Fácil de Usar:** Interfaz simple inspirada en scikit-learn. Solo necesitas instanciar la clase y llamar a `.fit()` y `.predict()`.
* **Compatible:** Al heredar de `RegressorMixin`, se integra con el ecosistema de scikit-learn.

---

## Instalación 📦

Puedes instalar `sbr-model` directamente desde PyPI:

```bash
pip install sbr-model

import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression
import xgboost as xgb

# Importamos tu clase desde la librería instalada
from sbr_model import StackingRegressor

# 1. Crear datos de ejemplo para un problema de regresión
# Esto nos permite probar el modelo sin necesidad de un archivo CSV
X, y = make_regression(n_samples=1000, n_features=20, n_informative=15, noise=0.1, random_state=42)
X_test, _ = make_regression(n_samples=500, n_features=20, n_informative=15, noise=0.1, random_state=2025)

# 2. Definir los "ingredientes": modelos base y meta-modelo
base_models = [
    ('xgb', xgb.XGBRegressor(random_state=42)),
    # Aquí podrías añadir más modelos, como LGBMRegressor o CatBoostRegressor
]
meta_model = LinearRegression()

# 3. Instanciar y entrenar el modelo
sbr = StackingRegressor(base_models=base_models, meta_model=meta_model, n_folds=5)
sbr.fit(X, y)

# 4. Hacer predicciones
predictions = sbr.predict(X_test)

# 5. Ver los resultados
print("Primeras 10 predicciones generadas por sbr-model:")
print(predictions[:10])