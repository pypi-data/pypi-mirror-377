"""
Detection and distance estimation heads for DistinaNet

This module contains various head architectures for classification, regression, and distance estimation.
"""

from .classification_head import ClassificationModel
from .regression_head import RegressionModel
from .distance_heads import (
    BaseConvDistModel,
    DeepConvDistModel,
    BottleneckDistModel,
    CBAMDistModel,
    DynamicBranchingDistModel
)

__all__ = [
    'ClassificationModel',
    'RegressionModel',
    'BaseConvDistModel',
    'DeepConvDistModel',
    'BottleneckDistModel',
    'CBAMDistModel',
    'DynamicBranchingDistModel'
]
