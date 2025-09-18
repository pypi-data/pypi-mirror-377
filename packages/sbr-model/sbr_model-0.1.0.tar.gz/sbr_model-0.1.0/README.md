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