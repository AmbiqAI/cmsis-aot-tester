"""
Simplified base operation class for TFLite model generation.
All operations inherit from this and implement build_keras_model().
"""

import numpy as np
import tensorflow as tf
from typing import Dict, Any
from abc import ABC, abstractmethod


class OperationBase(ABC):
    """
    Base class for all CMSIS-NN operations.
    
    Each operation must implement:
    1. build_keras_model() - Construct the Keras model
    2. convert_to_tflite() - Convert model to TFLite with operation-specific quantization
    """
    
    def __init__(self, desc: Dict[str, Any], seed: int = 1):
        """
        Initialize operation with descriptor and random seed.
        
        Args:
            desc: YAML descriptor dictionary
            seed: Random seed for reproducible generation
        """
        self.desc = desc
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        
    @abstractmethod
    def build_keras_model(self) -> tf.keras.Model:
        """
        Build the Keras model for this operation.
        
        Returns:
            Keras model ready for TFLite conversion
        """
        pass
    
    @abstractmethod
    def convert_to_tflite(self, model: tf.keras.Model, out_path: str, rep_seed: int) -> None:
        """
        Convert Keras model to TFLite with operation-specific quantization.
        
        Each operator implements its own quantization strategy based on:
        - activation_dtype (S8, S16, etc.)
        - weight_dtype (S8, S4, etc.)
        - operation-specific requirements
        
        Args:
            model: Keras model to convert
            out_path: Output path for .tflite file
            rep_seed: Representative dataset seed for quantization
        """
        pass