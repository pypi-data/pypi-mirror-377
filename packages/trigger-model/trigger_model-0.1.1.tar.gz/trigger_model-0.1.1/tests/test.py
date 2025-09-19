import pytest
from trigger_model.core import TriggerModel
import numpy as np

def make_dummy_model():

    from qkeras.qlayers import QDense, QActivation
    from qkeras.quantizers import quantized_bits
    from keras.models import Sequential

    from qkeras.qlayers import QDense, QActivation
    from qkeras.quantizers import quantized_bits
    from keras.models import Model
    from keras.layers import Input
    from keras.layers import *

    inputs = Input(shape=(57,))

    x = QDense(
        units=64,
        name='fc1',
        kernel_quantizer=quantized_bits(bits=6, alpha=1),
        bias_quantizer=quantized_bits(bits=6, alpha=1)
    )(inputs)

    x = QActivation("quantized_relu(3)")(x)

    outputs = QDense(
        units=1,
        name='last',
        kernel_quantizer=quantized_bits(bits=6, alpha=1),
        bias_quantizer=quantized_bits(bits=6, alpha=1)
    )(x)

    model = Model(inputs=inputs, outputs=outputs)
    return model



def test_predict():
    dummy_model = make_dummy_model()
    trigger_model = TriggerModel("Dummy", "Keras", "hls4ml", dummy_model, None)
    trigger_model()
    input_data = np.ones((10,57))
    output = trigger_model.software_predict(input_data)
    output = trigger_model.firmware_predict(input_data)
    output = trigger_model.qonnx_predict(input_data)
    assert isinstance(output[0], float)

