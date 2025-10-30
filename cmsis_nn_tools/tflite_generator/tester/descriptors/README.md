# Existing Test Descriptors

This directory contains YAML descriptors generated from the existing CMSIS-NN test cases in the `TestCases` directory.

## Generated Descriptors

The following descriptors have been generated based on the existing test cases:

### Core Operations
- **conv2d.yaml** - Convolution 2D operations (3 test cases)
- **depthwiseconv.yaml** - Depthwise convolution operations (3 test cases)
- **fullyconnected.yaml** - Fully connected layer operations (3 test cases)
- **softmax.yaml** - Softmax activation operations (2 test cases)

### Pooling Operations
- **maxpool.yaml** - Max pooling operations (2 test cases)
- **averagepool.yaml** - Average pooling operations (2 test cases)

### Element-wise Operations
- **add.yaml** - Addition operations (2 test cases)
- **mul.yaml** - Multiplication operations (2 test cases)
- **maximum.yaml** - Maximum operations (2 test cases)

### Activation Functions
- **relu.yaml** - ReLU activation (1 test case)
- **relu6.yaml** - ReLU6 activation (1 test case)
- **leakyrelu.yaml** - Leaky ReLU activation (1 test case)

### Utility Operations
- **pad.yaml** - Padding operations (2 test cases)
- **transpose.yaml** - Transpose operations (2 test cases)
- **mean.yaml** - Mean operations (2 test cases)
- **reducemax.yaml** - Reduce max operations (2 test cases)

### Specialized Operations
- **lstm.yaml** - LSTM operations (2 test cases)
- **svdf.yaml** - SVDF operations (1 test case)
- **matmulbatch.yaml** - Batch matrix multiplication (2 test cases)
- **stridedslice.yaml** - Strided slice operations (1 test case)

### Quantization Operations
- **quantize_f32.yaml** - Float32 quantization (2 test cases)
- **quantize_s8.yaml** - INT8 quantization (1 test case)
- **quantize_s16.yaml** - INT16 quantization (1 test case)
- **dequantize_s8.yaml** - INT8 dequantization (1 test case)
- **dequantize_s16.yaml** - INT16 dequantization (1 test case)

### Specialized Convolution Variants
- **convolve_1x1_s4.yaml** - 1x1 convolution INT4 (1 test case)
- **convolve_1x1_s8.yaml** - 1x1 convolution INT8 (1 test case)
- **convolve_1_x_n.yaml** - 1xN convolution (1 test case)
- **depthwise_conv_3x3.yaml** - 3x3 depthwise convolution (1 test case)
- **depthwise_conv_fast.yaml** - Fast depthwise convolution (1 test case)
- **depthwise_conv_s4.yaml** - INT4 depthwise convolution (1 test case)
- **depthwise_conv_s8.yaml** - INT8 depthwise convolution (1 test case)
- **grouped_convolve.yaml** - Grouped convolution (1 test case)

### Complex Models
- **ds_cnn_s.yaml** - Deep separable CNN small (1 test case)
- **ds_cnn_l.yaml** - Deep separable CNN large (1 test case)

## Usage

These descriptors can be used with the CMSIS-NN tester to generate test harnesses for the existing test cases. Each descriptor follows the same format as the manually created descriptors in the parent directory.

## Notes

- The descriptors use default quantization parameters (scales and zero points)
- Input shapes and filter shapes are estimated based on common patterns
- Some operations may need manual adjustment of parameters for optimal testing
- The descriptors maintain the same structure as the original test cases but in YAML format

## Total Statistics

- **Total descriptors generated**: 40
- **Total test cases**: 80+
- **Operations covered**: 25+ different operation types
- **Data types supported**: INT8, INT16, UINT8, INT4
