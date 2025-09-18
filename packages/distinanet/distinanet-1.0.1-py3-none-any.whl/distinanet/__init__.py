"""
DistinaNet: RetinaNet with Distance Estimation

This package implements the DistinaNet architecture, which extends RetinaNet
with an additional distance estimation head for predicting distances to detected objects.
"""

from .model import DistinaNet

__version__ = "1.0.0"
__all__ = ['DistinaNet']
