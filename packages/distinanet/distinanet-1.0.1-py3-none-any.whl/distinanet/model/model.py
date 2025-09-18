"""
DistinaNet: RetinaNet with Distance Estimation

This module implements the main DistinaNet architecture, which extends RetinaNet
with an additional distance estimation head for predicting distances to detected objects.
"""

import torch
import torch.nn as nn
import math
import torch.utils.model_zoo as model_zoo
from torchvision.ops import nms

from distinanet.core.blocks import BasicBlock, Bottleneck
from distinanet.core.box_ops import BBoxTransform, ClipBoxes
from distinanet.core.anchors import Anchors
from distinanet.core import losses
from distinanet.utils import setup_logger

from distinanet.backbones import ResNetBackbone, PyramidFeatures
from distinanet.heads import (
    ClassificationModel, 
    RegressionModel,
    BaseConvDistModel,
    DeepConvDistModel,
    BottleneckDistModel,
    CBAMDistModel,
    DynamicBranchingDistModel
)

logger = setup_logger("model", "INFO")


class DistinaNet(nn.Module):
    """
    DistinaNet: RetinaNet detection & classification heads and distance estimation.

    This is the main DistinaNet model that combines:
    - ResNet backbone for feature extraction
    - Feature Pyramid Network (FPN) for multi-scale features
    - Classification head for object detection
    - Regression head for bounding box prediction  
    - Distance estimation head for predicting distances to objects
    
    Args:
        num_classes: Number of object classes to detect
        backbone_depth: ResNet depth (18, 34, 50, 101, 152)
        pretrained: Whether to use pretrained backbone weights
        distance_loss_type: Loss function for distance estimation ('huber', 'l1', 'l2', etc.)
        distance_head_type: Architecture for distance head ('base', 'deep', 'bottleneck', 'cbam', 'dynamicbranching')
    """
    
    # Architecture configurations
    _CONFIGS = {
        18: (BasicBlock, [2, 2, 2, 2], 'https://download.pytorch.org/models/resnet18-5c106cde.pth'),
        34: (BasicBlock, [3, 4, 6, 3], 'https://download.pytorch.org/models/resnet34-333f7ec4.pth'),
        50: (Bottleneck, [3, 4, 6, 3], 'https://download.pytorch.org/models/resnet50-19c8e357.pth'),
        101: (Bottleneck, [3, 4, 23, 3], 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth'),
        152: (Bottleneck, [3, 8, 36, 3], 'https://download.pytorch.org/models/resnet152-b121ed2d.pth'),
    }

    def __init__(self, num_classes, backbone_depth=18, pretrained=False, distance_loss_type='huber', distance_head_type='base'):
        super(DistinaNet, self).__init__()
        
        if backbone_depth not in self._CONFIGS:
            raise ValueError(f"Unsupported backbone depth: {backbone_depth}. Supported: {list(self._CONFIGS.keys())}")
        
        block, layers, pretrained_url = self._CONFIGS[backbone_depth]
        
        self.distance_loss_type = distance_loss_type
        self.distance_head_type = distance_head_type

        # Initialize backbone
        self.backbone = ResNetBackbone(block, layers)
        
        # Load pretrained weights if requested
        if pretrained:
            self.backbone.load_state_dict(model_zoo.load_url(pretrained_url, model_dir='.'), strict=False)
        
        # Get FPN input sizes
        fpn_sizes = self.backbone.get_fpn_sizes(block, layers)
        
        # Initialize FPN
        self.fpn = PyramidFeatures(fpn_sizes[0], fpn_sizes[1], fpn_sizes[2])

        # Initialize heads
        self.regressionModel = RegressionModel(256)
        self.classificationModel = ClassificationModel(256, num_classes=num_classes)

        # Initialize distance head based on type
        logger.info(f"Dist Head: {self.distance_head_type}")
        if self.distance_head_type == 'base':
            self.distanceRegressionModel = BaseConvDistModel(256)
        elif self.distance_head_type == 'deep':
            self.distanceRegressionModel = DeepConvDistModel(256)
        elif self.distance_head_type == 'bottleneck':
            self.distanceRegressionModel = BottleneckDistModel(256)
        elif self.distance_head_type == 'cbam':
            self.distanceRegressionModel = CBAMDistModel(256)
        elif self.distance_head_type == 'dynamicbranching':
            self.distanceRegressionModel = DynamicBranchingDistModel(256)
        else:
            logger.error(f"{distance_head_type} invalid distance head type")
            raise ValueError(f"{distance_head_type} is not a valid distance head type.")

        # Initialize utility modules
        self.anchors = Anchors()
        self.regressBoxes = BBoxTransform()
        self.clipBoxes = ClipBoxes()
        self.focalLoss = losses.FocalLoss(distance_loss_type=self.distance_loss_type, delta=0.5)

        # Initialize head weights
        self._initialize_head_weights()

    def _initialize_head_weights(self):
        """Initialize classification and regression head weights."""
        prior = 0.01

        self.classificationModel.output.weight.data.fill_(0)
        self.classificationModel.output.bias.data.fill_(-math.log((1.0 - prior) / prior))

        self.regressionModel.output.weight.data.fill_(0)
        self.regressionModel.output.bias.data.fill_(0)

    def freeze_bn(self):
        """Freeze BatchNorm layers."""
        for layer in self.modules():
            if isinstance(layer, nn.BatchNorm2d):
                layer.eval()

    def forward(self, inputs):
        if self.training:
            img_batch, annotations = inputs
        else:
            img_batch = inputs

        # Extract features using backbone
        features = self.backbone(img_batch)
        
        # Apply FPN
        features = self.fpn(features)

        # Apply heads
        regression = torch.cat([self.regressionModel(feature) for feature in features], dim=1)
        classification = torch.cat([self.classificationModel(feature) for feature in features], dim=1)
        distance = torch.cat([self.distanceRegressionModel(feature) for feature in features], dim=1)

        anchors = self.anchors(img_batch)

        if self.training:
            return self.focalLoss(classification, regression, distance, anchors, annotations)
        else:
            return self._inference_forward(classification, regression, distance, anchors, img_batch)

    def _inference_forward(self, classification, regression, distance, anchors, img_batch):
        """Handle inference forward pass with NMS and post-processing."""
        transformed_anchors = self.regressBoxes(anchors, regression)
        transformed_anchors = self.clipBoxes(transformed_anchors, img_batch)
        
        finalResult = [[], [], [], []]

        finalScores = torch.Tensor([])
        finalAnchorBoxesIndexes = torch.Tensor([]).long()
        finalAnchorBoxesCoordinates = torch.Tensor([])
        finalDistances = torch.tensor([])

        if torch.cuda.is_available():
            finalScores = finalScores.cuda()
            finalAnchorBoxesIndexes = finalAnchorBoxesIndexes.cuda()
            finalAnchorBoxesCoordinates = finalAnchorBoxesCoordinates.cuda()
            finalDistances = finalDistances.cuda()

        for i in range(classification.shape[2]):
            scores = torch.squeeze(classification[:, :, i])
            scores_over_thresh = (scores > 0.05)
            if scores_over_thresh.sum() == 0:
                # no boxes to NMS, just continue
                continue
            
            scores = scores[scores_over_thresh]
            anchorBoxes = torch.squeeze(transformed_anchors)
            logger.debug(f"{i} anchors {anchorBoxes.shape}")
            anchorBoxes = anchorBoxes[scores_over_thresh]
            logger.debug(f"{i} filt_anchors {anchorBoxes.shape}")

            distances = distance.squeeze().unsqueeze(1)
            logger.debug(f"{i} dist {distances.shape}")
            distances = distances[scores_over_thresh]
            logger.debug(f"{i} filt_dist {distances.shape}")

            anchors_nms_idx = nms(anchorBoxes, scores, 0.5)
            logger.debug(f"{i} nms_idx {anchors_nms_idx.shape}")

            finalResult[0].extend(scores[anchors_nms_idx])
            finalResult[1].extend(torch.tensor([i] * anchors_nms_idx.shape[0]))
            
            logger.debug(f"{i} final_boxes {anchorBoxes.shape}")
            
            finalResult[2].extend(anchorBoxes[anchors_nms_idx])
            
            logger.debug(f"{i} dist_nms {distances[anchors_nms_idx].shape}")
            
            finalScores = torch.cat((finalScores, scores[anchors_nms_idx]))
            finalAnchorBoxesIndexesValue = torch.tensor([i] * anchors_nms_idx.shape[0])
            if torch.cuda.is_available():
                finalAnchorBoxesIndexesValue = finalAnchorBoxesIndexesValue.cuda()

            finalAnchorBoxesIndexes = torch.cat((finalAnchorBoxesIndexes, finalAnchorBoxesIndexesValue))
            finalAnchorBoxesCoordinates = torch.cat((finalAnchorBoxesCoordinates, anchorBoxes[anchors_nms_idx]))
            finalDistances = torch.cat((finalDistances, distances[anchors_nms_idx]))
            logger.debug("finalDistances", finalDistances, "\n")

        return [finalScores, finalAnchorBoxesIndexes, finalAnchorBoxesCoordinates, finalDistances]
