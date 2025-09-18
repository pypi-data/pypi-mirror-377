"""
Distance estimation heads for DistinaNet.

This module contains various architectures for distance estimation heads.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class BaseConvDistModel(nn.Module):
    """Base convolutional distance estimation head."""
    
    def __init__(self, num_features_in, num_anchors=9, feature_size=256):
        super(BaseConvDistModel, self).__init__()

        # Initialize weights
        self._initialize_weights()

        # Assume we have the same architecture as RegressionModel but with a single output per anchor for distance
        self.conv1 = nn.Conv2d(num_features_in, feature_size, kernel_size=3, padding=1)
        self.act1 = nn.ReLU()

        self.conv2 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act2 = nn.ReLU()

        self.conv3 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act3 = nn.ReLU()

        self.conv4 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act4 = nn.ReLU()

        # Output layer for distance regression, with 1 output channel per anchor
        self.output = nn.Conv2d(feature_size, num_anchors * 1, kernel_size=3, padding=1)

    def forward(self, x):
        out = self.conv1(x)
        out = self.act1(out)
        
        out = self.conv2(out)
        out = self.act2(out)

        out = self.conv3(out)
        out = self.act3(out)
        
        out = self.conv4(out)
        out = self.act4(out)

        out = self.output(out)

        # out is B x C x W x H, with C = num_anchors
        out = out.permute(0, 2, 3, 1)

        return out.contiguous().view(out.shape[0], -1, 1)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # Initialize convolutional layers with a normal distribution
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                if m.bias is not None:
                    # Initialize biases to zero
                    m.bias.data.zero_()


class DeepConvDistModel(nn.Module):
    """Deep convolutional distance estimation head with additional layers."""
    
    def __init__(self, num_features_in, num_anchors=9, feature_size=256):
        super(DeepConvDistModel, self).__init__()

        # Initialize weights
        self._initialize_weights()

        # Original architecture with additional convolutional layers for increased depth
        self.conv1 = nn.Conv2d(num_features_in, feature_size, kernel_size=3, padding=1)
        self.act1 = nn.ReLU()
        self.conv2 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act2 = nn.ReLU()
        self.conv3 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act3 = nn.ReLU()
        self.conv4 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act4 = nn.ReLU()
        # Added convolutional layers
        self.conv5 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act5 = nn.ReLU()
        self.conv6 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act6 = nn.ReLU()
        self.conv7 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.act7 = nn.ReLU()

        # Output layer for distance regression, with 1 output channel per anchor
        self.output = nn.Conv2d(feature_size, num_anchors * 1, kernel_size=3, padding=1)

    def forward(self, x):
        out = self.conv1(x)
        out = self.act1(out)
        out = self.conv2(out)
        out = self.act2(out)
        out = self.conv3(out)
        out = self.act3(out)
        out = self.conv4(out)
        out = self.act4(out)
        # Pass through the additional layers
        out = self.conv5(out)
        out = self.act5(out)
        out = self.conv6(out)
        out = self.act6(out)
        out = self.conv7(out)
        out = self.act7(out)
        out = self.output(out)

        # out is B x C x W x H, with C = num_anchors
        out = out.permute(0, 2, 3, 1)
        return out.contiguous().view(out.shape[0], -1, 1)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # Initialize convolutional layers with a normal distribution
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                if m.bias is not None:
                    # Initialize biases to zero
                    m.bias.data.zero_()


class BottleneckDistModel(nn.Module):
    """Bottleneck distance estimation head with dimensionality reduction."""
    
    def __init__(self, num_features_in, num_anchors=9, feature_size=256):
        super(BottleneckDistModel, self).__init__()

        # Bottleneck layer to reduce dimensionality
        self.bottleneck = nn.Conv2d(num_features_in, feature_size // 2, kernel_size=1)

        # Convolutional layers
        self.conv1 = nn.Conv2d(feature_size // 2, feature_size, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(feature_size)
        self.conv2 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(feature_size)
        self.conv3 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(feature_size)

        # Reintroducing the final convolutional layer similar to the original model
        self.output_conv = nn.Conv2d(feature_size, num_anchors, kernel_size=3, padding=1)

        # Initialize weights
        self._initialize_weights()

    def forward(self, x):
        x = F.relu(self.bottleneck(x))
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        
        # Use the convolutional output layer for distance estimation
        x = self.output_conv(x)
        
        # out is B x C x W x H, with C = num_anchors, matching original output before reshape
        x = x.permute(0, 2, 3, 1)  # Adjust the dimensions to match the reshaping operation in the original model

        return x.contiguous().view(x.size(0), -1, 1)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)


class ChannelAttention(nn.Module):
    """Channel attention module for CBAM."""
    
    def __init__(self, in_channels, ratio=16):
        super(ChannelAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // ratio, 1, bias=False),
            nn.ReLU(),
            nn.Conv2d(in_channels // ratio, in_channels, 1, bias=False)
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = self.fc(self.avg_pool(x))
        max_out = self.fc(self.max_pool(x))
        out = avg_out + max_out
        return self.sigmoid(out)


class SpatialAttention(nn.Module):
    """Spatial attention module for CBAM."""
    
    def __init__(self, kernel_size=7):
        super(SpatialAttention, self).__init__()
        self.conv1 = nn.Conv2d(2, 1, kernel_size, padding=kernel_size//2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        x = torch.cat([avg_out, max_out], dim=1)
        x = self.conv1(x)
        return self.sigmoid(x)


class CBAMBlock(nn.Module):
    """Convolutional Block Attention Module (CBAM)."""
    
    def __init__(self, in_channels, ratio=16, kernel_size=7):
        super(CBAMBlock, self).__init__()
        self.channel_attention = ChannelAttention(in_channels, ratio)
        self.spatial_attention = SpatialAttention(kernel_size)

    def forward(self, x):
        x = x * self.channel_attention(x)
        x = x * self.spatial_attention(x)
        return x


class CBAMDistModel(nn.Module):
    """CBAM-enhanced distance estimation head."""
    
    def __init__(self, num_features_in, num_anchors=9, feature_size=256):
        super(CBAMDistModel, self).__init__()

        self.conv1 = nn.Conv2d(num_features_in, feature_size, kernel_size=3, padding=1)
        self.cbam1 = CBAMBlock(feature_size)
        
        self.conv2 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.cbam2 = CBAMBlock(feature_size)

        self.conv3 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.cbam3 = CBAMBlock(feature_size)

        self.conv4 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)
        self.cbam4 = CBAMBlock(feature_size)

        self.output = nn.Conv2d(feature_size, num_anchors * 1, kernel_size=3, padding=1)

        self._initialize_weights()

    def forward(self, x):
        out = self.cbam1(self.conv1(x))
        out = self.cbam2(self.conv2(out))
        out = self.cbam3(self.conv3(out))
        out = self.cbam4(self.conv4(out))
        out = self.output(out)
        out = out.permute(0, 2, 3, 1)
        return out.contiguous().view(out.shape[0], -1, 1)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # Initialize convolutional layers with a normal distribution
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                if m.bias is not None:
                    # Initialize biases to zero
                    m.bias.data.zero_()


class DynamicBranchingDistModel(nn.Module):
    """Dynamic branching distance estimation head with local and global context."""
    
    def __init__(self, num_features_in, num_anchors=9, feature_size=256, global_context_dim=128):
        super(DynamicBranchingDistModel, self).__init__()

        # Local branch - Convolutional layers
        self.local_conv1 = nn.Conv2d(num_features_in, feature_size, kernel_size=3, padding=1)
        self.local_conv2 = nn.Conv2d(feature_size, feature_size, kernel_size=3, padding=1)

        # Global branch - Fully connected layers
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.global_fc1 = nn.Linear(feature_size, global_context_dim)
        # Ensure the global branch's output has the same number of channels as the local branch
        self.global_fc2 = nn.Linear(global_context_dim, feature_size)  # Output size matches local branch channel depth

        # Dynamic gating mechanism
        self.gate = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(feature_size, 2),  # 2 gates: one for each branch
            nn.Softmax(dim=1)
        )

        # Final convolution for distance prediction
        self.output_conv = nn.Conv2d(feature_size, num_anchors, kernel_size=3, padding=1)

        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        batch_size, _, height, width = x.shape

        # Local branch
        local_x = F.relu(self.local_conv1(x))
        local_x = F.relu(self.local_conv2(local_x))

        # Global branch
        global_x = self.global_pool(x).view(batch_size, -1)
        global_x = F.relu(self.global_fc1(global_x))
        global_x = self.global_fc2(global_x).view(batch_size, -1, 1, 1)  # Reshape to have correct channel depth

        # Dynamic gating
        gates = self.gate(x)
        local_gate, global_gate = gates[:, 0].view(-1, 1, 1, 1), gates[:, 1].view(-1, 1, 1, 1)

        # Combine branches based on gating
        combined_x = local_gate * local_x + global_gate * global_x.expand_as(local_x)

        # Output
        out = self.output_conv(combined_x)
        out = out.permute(0, 2, 3, 1).contiguous().view(out.size(0), -1, 1)
        return out
