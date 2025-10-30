"""
Quantize operation implementation for CMSIS-NN tester.

Following the official CMSIS-NN test generator logic from RefactoredTestGen/Lib/op_quantize.py
"""

from typing import Dict, Any
import numpy as np
import tensorflow as tf
from .base import OperationBase


class OpQuantize(OperationBase):
    """
    Quantize operation.
    """
    
    def build_keras_model(self) -> tf.keras.Model:
        """Build Keras model for Quantize operation.
        
        Following the official CMSIS-NN test generator logic:
        - Use an identity Dense layer to create a model that can be quantized
        - Input shape is (1, 8, 1) which gets flattened to 8 elements
        - Dense(8) with identity weights preserves the input
        """
        model = tf.keras.Sequential()
        model.add(tf.keras.Input(shape=(1, 8, 1)))
        
        # Flatten to 1D vector of length 8
        model.add(tf.keras.layers.Flatten())
        
        # Dense(8) with identity weights - this preserves input values
        dense = tf.keras.layers.Dense(units=8, use_bias=False, activation=None)
        model.add(dense)
        
        # Build the model to initialize weights
        model.build((None, 1, 8, 1))
        
        # Set identity weights to preserve input values
        identity_weights = np.eye(8, dtype=np.float32)
        dense.set_weights([identity_weights])
        

    def convert_to_tflite(self, model, out_path: str, rep_seed: int) -> None:
        """Convert Keras model to TFLite with quantization."""
        import tensorflow as tf
        import numpy as np
        
        # Create converter
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Apply quantization based on activation_dtype
        activation_dtype = self.desc.get('activation_dtype', 'S8')
        
        if activation_dtype == 'S8':
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.int8]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8
        elif activation_dtype == 'S16':
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.int16]
            # For int16 quantization, keep input/output as float32
            # For int16 quantization, keep input/output as float32
        
        # Generate representative dataset
        def representative_data_gen():
            for _ in range(100):
                if 'input_shape' in self.desc:
                    inputs = self.rng.uniform(-1.0, 1.0, size=self.desc['input_shape']).astype(np.float32)
                    yield [inputs]
                elif 'input_1_shape' in self.desc and 'input_2_shape' in self.desc:
                    inputs1 = self.rng.uniform(-1.0, 1.0, size=self.desc['input_1_shape']).astype(np.float32)
                    inputs2 = self.rng.uniform(-1.0, 1.0, size=self.desc['input_2_shape']).astype(np.float32)
                    yield [inputs1, inputs2]
        
        converter.representative_dataset = representative_data_gen
        
        # Convert and save
        tflite_model = converter.convert()
        with open(out_path, 'wb') as f:
            f.write(tflite_model)
