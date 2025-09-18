"""
ResNet backbone implementation for DistinaNet.
"""

import torch
import torch.nn as nn
import math
import torch.utils.model_zoo as model_zoo
from distinanet.core.blocks import BasicBlock, Bottleneck

model_urls = {
    'resnet18': 'https://download.pytorch.org/models/resnet18-5c106cde.pth',
    'resnet34': 'https://download.pytorch.org/models/resnet34-333f7ec4.pth',
    'resnet50': 'https://download.pytorch.org/models/resnet50-19c8e357.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-b121ed2d.pth',
}

class ResNetBackbone(nn.Module):
    """
    ResNet backbone for feature extraction.
    
    This class implements the ResNet architecture up to the feature extraction layers,
    returning features from layers 2, 3, and 4 for use with FPN.
    
    Args:
        block: ResNet block type (BasicBlock or Bottleneck)
        layers: List of layer repetitions for ResNet architecture
    """

    def __init__(self, block, layers):
        self.inplanes = 64
        super(ResNetBackbone, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)

        # Initialize weights
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

        self.freeze_bn()

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = [block(self.inplanes, planes, stride, downsample)]
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def freeze_bn(self):
        """Freeze BatchNorm layers."""
        for layer in self.modules():
            if isinstance(layer, nn.BatchNorm2d):
                layer.eval()

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x1 = self.layer1(x)
        x2 = self.layer2(x1)
        x3 = self.layer3(x2)
        x4 = self.layer4(x3)

        return [x2, x3, x4]

    def get_fpn_sizes(self, block, layers):
        """Get the number of channels for FPN input layers."""
        if block == BasicBlock:
            return [
                self.layer2[layers[1] - 1].conv2.out_channels,
                self.layer3[layers[2] - 1].conv2.out_channels,
                self.layer4[layers[3] - 1].conv2.out_channels
            ]
        elif block == Bottleneck:
            return [
                self.layer2[layers[1] - 1].conv3.out_channels,
                self.layer3[layers[2] - 1].conv3.out_channels,
                self.layer4[layers[3] - 1].conv3.out_channels
            ]
        else:
            raise ValueError(f"Block type {block} not understood")


def resnet18_backbone(pretrained=False):
    """ResNet-18 backbone."""
    backbone = ResNetBackbone(BasicBlock, [2, 2, 2, 2])
    if pretrained:
        backbone.load_state_dict(model_zoo.load_url(model_urls['resnet18'], model_dir='.'), strict=False)
    return backbone


def resnet34_backbone(pretrained=False):
    """ResNet-34 backbone."""
    backbone = ResNetBackbone(BasicBlock, [3, 4, 6, 3])
    if pretrained:
        backbone.load_state_dict(model_zoo.load_url(model_urls['resnet34'], model_dir='.'), strict=False)
    return backbone


def resnet50_backbone(pretrained=False):
    """ResNet-50 backbone."""
    backbone = ResNetBackbone(Bottleneck, [3, 4, 6, 3])
    if pretrained:
        backbone.load_state_dict(model_zoo.load_url(model_urls['resnet50'], model_dir='.'), strict=False)
    return backbone


def resnet101_backbone(pretrained=False):
    """ResNet-101 backbone."""
    backbone = ResNetBackbone(Bottleneck, [3, 4, 23, 3])
    if pretrained:
        backbone.load_state_dict(model_zoo.load_url(model_urls['resnet101'], model_dir='.'), strict=False)
    return backbone


def resnet152_backbone(pretrained=False):
    """ResNet-152 backbone."""
    backbone = ResNetBackbone(Bottleneck, [3, 8, 36, 3])
    if pretrained:
        backbone.load_state_dict(model_zoo.load_url(model_urls['resnet152'], model_dir='.'), strict=False)
    return backbone


# Maintain backward compatibility with the old interface
ResNet = ResNetBackbone
