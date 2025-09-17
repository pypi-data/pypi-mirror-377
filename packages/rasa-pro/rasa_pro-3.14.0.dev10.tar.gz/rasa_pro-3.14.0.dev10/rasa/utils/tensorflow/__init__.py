"""TensorFlow utilities for Rasa components.

This module provides TensorFlow-related utilities and components.
TensorFlow is an optional dependency and should be installed separately
if you want to use components that require it. These are:
- DIETClassifier
- TEDPolicy
- UnexpecTEDIntentPolicy
- ResponseSelector
- ConveRTFeaturizer
- LanguageModelFeaturizer

To install Rasa with TensorFlow support:
`pip install "rasa[tensorflow]"`

To install it with poetry:
`poetry install --extras tensorflow`

For macOS with Apple Silicon (M1/M2) (platform-specific TensorFlow installation):
`pip install "rasa[tensorflow,metal]"`
"""

import importlib.util
import logging

logger = logging.getLogger(__name__)

# check if TensorFlow is available
TENSORFLOW_AVAILABLE = importlib.util.find_spec("tensorflow") is not None
