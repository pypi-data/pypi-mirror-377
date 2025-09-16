# ===== ./README.md =====
# TabKAN: Advancing Tabular Data Analysis using Kolmogorov-Arnold Networks

[![PyPI version](https://badge.fury.io/py/tabkan.svg)](https://badge.fury.io/py/tabkan)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)

**TabKAN** is a Python framework that implements a family of Kolmogorov-Arnold Network (KAN) based architectures specifically designed for tabular data analysis. This library is the official implementation of the research paper: [**TabKAN: Advancing Tabular Data Analysis using Kolmogorov-Arnold Network**](http://bit.ly/3RFZfwh).

Traditional deep learning models often struggle to outperform tree-based methods like XGBoost on structured data. TabKAN bridges this gap by leveraging the expressive power of KANs, which use learnable activation functions on the edges of the neural network instead of fixed activations on the nodes.

This library provides a unified API for various KAN variants, making it easy to experiment, train, and evaluate state-of-the-art models for tabular tasks.

## Key Features

- **Multiple KAN Variants:** Includes implementations and wrappers for:
  - **ChebyshevKAN**: Uses Chebyshev polynomials for function approximation.
  - **FourierKAN**: Uses Fourier series for capturing periodic patterns.
  - **SplineKAN**: The original KAN architecture based on B-splines (via `kan-python`).
  - **Rational KANs**: `JacobiKAN` and `PadeKAN` for modeling complex rational functions (via `rkan`).
  - **FractionalKAN**: Utilizes fractional-order Jacobi functions for enhanced flexibility (via `fkan`).
- **Advanced Architectures**: A generic and powerful `KANMixer` architecture that replaces MLPs in a Mixer design with any KAN layer, enhancing expressivity.
- **Unified and Simple API**: All models inherit from a base `KAN` class, providing consistent `.fit()` and `.tune()` methods.
- **Built-in Hyperparameter Tuning**: Seamlessly find the best model architecture using an integrated Optuna-based tuner.
- **Model Interpretability**: Includes methods like `.get_feature_importance()` for `ChebyshevKAN` and `FourierKAN`, as described in the paper.

## Installation

You can install TabKAN directly from PyPI:
```bash
pip install tabkan