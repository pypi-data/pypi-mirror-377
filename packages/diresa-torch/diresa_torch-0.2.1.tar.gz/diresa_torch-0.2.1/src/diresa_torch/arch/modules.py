import torch
import torch.nn as nn
from enum import Enum

import logging


# NOTE:
# With current approach, input layer to DenseLayer is computed from either input_shape when no CNN is present or from the output of CNN. Adding this layer is the responsibility of the DIRESA class.


class ModuleList(Enum):
    """
    Enum class used for tests to select for which kind
    of module we are counting different layers.
    See test_structure.py
    """

    DenseLayer = 0
    CNNLayer = 1


class DenseLayer(nn.Module):
    """
    Provides Network with Feed Forward Fully Connected Layers.

    :param dense_units: tuple which describes the width of each feed forward layer. First element describes the first hidden layer. Last layer defines the output layer which is the size of latent space. E.g. ``(16, 32, 64)`` is a FFN with two hidden layers ``(16, 32)`` and last layer which defines latent space of size ``64``.
    :param activation: activation function. Put between each layer except the last one.
    :param reverse: Builds opposite network specified by ``dense_units``. Does not take into account last value of ``dense_unit`` representing latent space, instead output layer is defined having size ``input_size``
    """

    def __init__(self, dense_units=(), activation=nn.ReLU(), reverse=False):
        super().__init__()

        if reverse:
            dense_units = dense_units[::-1]

        layers = []

        # only 2 layers (input/output), no hidden layers -> No activation function.
        if len(dense_units) == 2:
            layers.append(nn.Linear(dense_units[0], dense_units[1]))
        elif len(dense_units) > 2:
            depth = len(dense_units)
            for i in range(depth - 1):
                layers.append(nn.Linear(dense_units[i], dense_units[i + 1]))

                # Skip activation for last layer
                if i < depth - 2:
                    layers.append(activation)

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class DistanceLayer(nn.Module):
    """
    :param x1: batch of input samples to encoder
    :param x2: batch of input shuffled samples to twin encoder
    :param y1: batch of latent representations of encoder
    :param y2: batch of latent representations of twin encoder
    :return: batch of distances between inputs, batch of distances between latent representations
    """

    def __init__(self, dim_less=False):
        """
        :param dim_less: if True distance is divided by dimension of space
        """
        super().__init__()
        self.dim_less = dim_less

    def forward(self, x1, x2, y1, y2):
        """
        :param x1: batch of input samples to encoder
        :param x2: batch of input shuffled samples to twin encoder
        :param y1: batch of latent representations of encoder
        :param y2: batch of latent representations of twin encoder
        :return: batch of distances between inputs, batch of distances between latent representations
        """
        # FIX: Use L2 norm here instead of L1
        dist1 = torch.abs(x1 - x2)
        dist2 = torch.abs(y1 - y2)
        # sum over all dims, except 0
        dist1 = torch.sum(dist1.view(dist1.shape[0], -1), dim=1)
        # sum over all dims, except 0
        dist2 = torch.sum(dist2.view(dist2.shape[0], -1), dim=1)
        if self.dim_less:
            dist1 /= torch.sum(x1) / x1.shape[1]  # divide by input dimension
            # divide by latent space dimension
            dist2 /= torch.sum(x2) / x2.shape[1]
        return torch.stack((dist1, dist2), dim=-1)


class _CNNBlock(nn.Module):
    """
    Builds CNN Block
    :param num_layers: number of layers in this block
    :param input: input channels
    :param output: output channels
    :param kernel_size: size of kernel used for the convolution operation
    :param activation: non linear activation function
    """

    def __init__(self, num_layers, input, output, kernel_size, activation=nn.ReLU()):
        super().__init__()

        layers = []

        # Maintain spatial dimensions
        padding = (kernel_size[0] // 2, kernel_size[1] // 2)

        for i in range(num_layers):
            layers.append(nn.Conv2d(input, output, kernel_size, padding=padding))
            layers.append(activation)
            # change after 1st iteration so that we can stack multiple blocks
            input = output

        layers.append(nn.MaxPool2d((2, 2)))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class _CNNTransposeBlock(nn.Module):
    """
    CNN Transpose Block for decoder - mirrors the encoder block but with transpose convolutions

    :param num_layers: number of layers in this block
    :param input: input channels
    :param output: output channels
    :param kernel_size: size of kernel used for the convolution operation
    :param activation: non linear activation function
    """

    def __init__(self, num_layers, input, output, kernel_size, activation=nn.ReLU()):
        super().__init__()
        layers = []

        # Need to reverse MaxPool2d
        layers.append(nn.Upsample(scale_factor=2, mode="nearest"))

        # Now build the transpose conv layers (in reverse order)
        current_channels = input
        for i in range(num_layers):
            # Calculate padding to maintain spatial dimensions
            padding = (kernel_size[0] // 2, kernel_size[1] // 2)

            # For the last layer, change to output channels
            if i == num_layers - 1:
                out_channels = output
            else:
                out_channels = current_channels

            layers.append(
                nn.ConvTranspose2d(
                    current_channels, out_channels, kernel_size, padding=padding
                )
            )
            layers.append(activation)
            current_channels = out_channels

        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class CNNLayer(nn.Module):
    """
    Builds CNN layers for autoencoder.

    :param stack: are the number of blocks per layer
    :param stack_filters: are the number of output channels of each block (as input channels are defined by previous layer)
    :param kernel_size: size of kernel used for the convolution operation
    :param input_shape: shape of input data in following order (channels, x, y)
    :param activation: non linear activation function
    """

    def __init__(
        self,
        stack,
        stack_filters,
        kernel_size,
        input_shape,
        activation=nn.ReLU(),
        reverse=False,
    ):
        super().__init__()

        layers = []

        if reverse:
            # Decoder mode: reverse everything
            reversed_stack = stack[::-1]
            reversed_filters = stack_filters[::-1]

            # For decoder, we need to map back to original input channels
            # Input channels for decoder are the reversed filters
            input_channels = reversed_filters

            # input_shape is now output shape
            output_channels = tuple(reversed_filters[1:] + (input_shape[0],))

            for block, input_ch, output_ch in zip(
                reversed_stack, input_channels, output_channels
            ):
                layers.append(
                    _CNNTransposeBlock(
                        block, input_ch, output_ch, kernel_size, activation
                    )
                )
        else:
            # Encoder Mode
            # renaming to fit with pytorch Docs
            output_channels = stack_filters

            # first dim of input_shape is depth (= number of channels), which are inputs of first CNN Block
            input_channels = tuple((input_shape[0],) + stack_filters)[:-1]

            for block, input_ch, output_ch in zip(
                stack, input_channels, output_channels
            ):
                layers.append(
                    _CNNBlock(block, input_ch, output_ch, kernel_size, activation)
                )

        self.cnn = nn.Sequential(*layers)

    def forward(self, x):
        return self.cnn(x)


# TODO: Add setter here for self.order
class OrderingLayer(nn.Module):
    def __init__(self):
        super().__init__()

        # NOTE: The dimensions of the ordering are not known statically
        # as it is not possible to retrieve latent dimensions of an encoder
        # a user provides. Otherwise we could just a tensor.range(latent.shape)
        # to get an identity ordering (i.e. the ordering layer just passes through
        # the components)
        self.order = None

    # Assigning and Reading self.order call those
    # methods internally. Could be used to return
    # an identity ordering in case self.order = None
    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, order):
        if order is None:
            logging.info(f"Ordering has been set to {order}")
        self._order = order

    def forward(self, x, reverse=False):
        if self.order is not None:
            if reverse:
                index = torch.argsort(self.order)
            else:
                index = self.order

            return torch.index_select(x, 1, index)

        # ignore ordering and just pass through
        else:
            return x
