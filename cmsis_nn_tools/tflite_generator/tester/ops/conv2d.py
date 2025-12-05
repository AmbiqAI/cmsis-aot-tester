"""
Conv2D operation implementation.
"""

from typing import Dict, Any
import numpy as np
import tensorflow as tf
from .base import OperationBase


class OpConv2D(OperationBase):
    """
    Conv2D operation.
    """
    
    def build_keras_model(self) -> tf.keras.Model:
        input_shape = self.desc['input_shape']
        filter_shape = self.desc['filter_shape']
        
        tf.keras.utils.set_random_seed(17)
        
        padding = self.desc.get('padding', 'valid')
        if padding is not None:
            padding = str(padding).lower()
        else:
            padding = 'valid'
        
        activation = self.desc.get('activation', 'NONE')
        act = None if activation in (None, 'NONE', 'none') else activation.lower()
        
        dilation = self.desc.get('dilation', [1, 1])
        if isinstance(dilation, (int, float)):
            dilation = [int(dilation), int(dilation)]
        elif isinstance(dilation, (list, tuple)):
            if len(dilation) != 2:
                raise ValueError(f"Invalid dilation: {dilation}. Must be 2 integers or a single integer")
            dilation = [int(dilation[0]), int(dilation[1])]
        
        if any(d <= 0 for d in dilation):
            raise ValueError(f"Invalid dilation values: {dilation}. Must be positive integers")
        
        x = tf.keras.Input(
            shape=input_shape[1:],
            batch_size=input_shape[0] if len(input_shape) > 0 else None,
            dtype=tf.float32,
            name='input'
        )
        
        conv = tf.keras.layers.Conv2D(
            filters=filter_shape[3],
            kernel_size=tuple(filter_shape[0:2]),
            strides=tuple(self.desc.get('strides', [1, 1])),
            dilation_rate=tuple(dilation),
            padding=padding,
            use_bias=self.desc.get('use_bias', True),
            activation=act,
            kernel_initializer=tf.keras.initializers.GlorotUniform(seed=1234),
            bias_initializer='zeros',
            name='conv_2d'
        )(x)
        
        model = tf.keras.Model(inputs=[x], outputs=conv, name='conv_2d')
        return model

    def convert_to_tflite(self, model, out_path: str, rep_seed: int) -> None:
        """Convert Keras model to TFLite with quantization."""
        import tensorflow as tf
        import numpy as np
        
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        activation_dtype = self.desc.get('activation_dtype', 'S8')
        
        if activation_dtype == 'S8':
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.int8]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8
        elif activation_dtype == 'S16':
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.EXPERIMENTAL_TFLITE_BUILTINS_ACTIVATIONS_INT16_WEIGHTS_INT8
            ]
            converter.inference_input_type = tf.int16
            converter.inference_output_type = tf.int16
        
        def representative_data_gen():
            rep_rng = np.random.default_rng(42)
            for _ in range(100):
                if 'input_shape' in self.desc:
                    inputs = rep_rng.integers(-32, 32, size=self.desc['input_shape']).astype(np.float32)
                    yield [inputs]
                elif 'input_1_shape' in self.desc and 'input_2_shape' in self.desc:
                    inputs1 = rep_rng.integers(-32, 32, size=self.desc['input_1_shape']).astype(np.float32)
                    inputs2 = rep_rng.integers(-32, 32, size=self.desc['input_2_shape']).astype(np.float32)
                    yield [inputs1, inputs2]
        
        converter.representative_dataset = representative_data_gen
        
        tflite_model = converter.convert()
        with open(out_path, 'wb') as f:
            f.write(tflite_model)
