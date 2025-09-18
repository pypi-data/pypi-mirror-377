import numpy as np
import torch
import torch.nn as nn
from distinanet.utils import setup_logger

logger = setup_logger("losses", "INFO")


def calc_iou(a, b):
    area = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])

    iw = torch.min(torch.unsqueeze(a[:, 2], dim=1), b[:, 2]) - torch.max(torch.unsqueeze(a[:, 0], 1), b[:, 0])
    ih = torch.min(torch.unsqueeze(a[:, 3], dim=1), b[:, 3]) - torch.max(torch.unsqueeze(a[:, 1], 1), b[:, 1])

    iw = torch.clamp(iw, min=0)
    ih = torch.clamp(ih, min=0)

    ua = torch.unsqueeze((a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1]), dim=1) + area - iw * ih

    ua = torch.clamp(ua, min=1e-8)

    intersection = iw * ih

    IoU = intersection / ua

    return IoU


def logcosh_loss(y_pred, y_true):
    """
    Log-Cosh loss function, with improved numerical stability for large differences.
    
    Parameters:
    - y_pred: Predicted values
    - y_true: True values
    
    Returns:
    - torch.Tensor: Computed log-cosh loss
    """
    # Calculate the difference between the predicted and actual values
    diff = y_pred - y_true

    # Limit the difference to a max/min to prevent overflow in cosh()
    diff = torch.clamp(diff, min=-15, max=15)  # Clamp values to prevent exponential growth

    # Calculate the log-cosh of the difference
    loss = torch.log(torch.cosh(diff))

    # Return the mean of the log-cosh loss
    return torch.mean(loss)

class FocalLoss(nn.Module):
    def __init__(self, distance_loss_type='huber', delta=0.5):
        super(FocalLoss, self).__init__()
        self.delta = delta
        self.distance_loss_type = distance_loss_type
        logger.info("Loss Function: %s", distance_loss_type)
        if distance_loss_type == 'huber':
            logger.info("Huber Loss delta: %f", delta)

    def forward(self, classifications, regressions, distances, anchors, annotations):
        alpha = 0.25
        gamma = 2.0
        batch_size = classifications.shape[0]
        classification_losses = []
        regression_losses = []
        distance_losses = []  # List to collect distance losses

        anchor = anchors[0, :, :]

        anchor_widths  = anchor[:, 2] - anchor[:, 0]
        anchor_heights = anchor[:, 3] - anchor[:, 1]
        anchor_ctr_x   = anchor[:, 0] + 0.5 * anchor_widths
        anchor_ctr_y   = anchor[:, 1] + 0.5 * anchor_heights

        for j in range(batch_size):

            classification = classifications[j, :, :]
            regression = regressions[j, :, :]
            distance = distances[j, :, :]

            logger.debug("\ninside loss - batch classif", classification.shape)
            logger.debug("\ninside loss - batch regression", regression.shape)
            logger.debug("\ninside loss - batch distance", distance.shape)

            bbox_annotation = annotations[j, :, :]
            bbox_annotation = bbox_annotation[bbox_annotation[:, 4] != -1]

            classification = torch.clamp(classification, 1e-4, 1.0 - 1e-4)

            if bbox_annotation.shape[0] == 0:
                if torch.cuda.is_available():
                    alpha_factor = torch.ones(classification.shape).cuda() * alpha

                    alpha_factor = 1. - alpha_factor
                    focal_weight = classification
                    focal_weight = alpha_factor * torch.pow(focal_weight, gamma)

                    bce = -(torch.log(1.0 - classification))

                    # cls_loss = focal_weight * torch.pow(bce, gamma)
                    cls_loss = focal_weight * bce
                    classification_losses.append(cls_loss.sum())
                    regression_losses.append(torch.tensor(0).float().cuda())

                else:
                    alpha_factor = torch.ones(classification.shape) * alpha

                    alpha_factor = 1. - alpha_factor
                    focal_weight = classification
                    focal_weight = alpha_factor * torch.pow(focal_weight, gamma)

                    bce = -(torch.log(1.0 - classification))

                    # cls_loss = focal_weight * torch.pow(bce, gamma)
                    cls_loss = focal_weight * bce
                    classification_losses.append(cls_loss.sum())
                    regression_losses.append(torch.tensor(0).float())

                continue

            IoU = calc_iou(anchors[0, :, :], bbox_annotation[:, :4]) # num_anchors x num_annotations

            IoU_max, IoU_argmax = torch.max(IoU, dim=1) # num_anchors x 1

            #import pdb
            #pdb.set_trace()

            # compute the loss for classification
            targets = torch.ones(classification.shape) * -1

            if torch.cuda.is_available():
                targets = targets.cuda()

            targets[torch.lt(IoU_max, 0.4), :] = 0

            positive_indices = torch.ge(IoU_max, 0.5)

            num_positive_anchors = positive_indices.sum()

            assigned_annotations = bbox_annotation[IoU_argmax, :]

            targets[positive_indices, :] = 0
            targets[positive_indices, assigned_annotations[positive_indices, 4].long()] = 1

            if torch.cuda.is_available():
                alpha_factor = torch.ones(targets.shape).cuda() * alpha
            else:
                alpha_factor = torch.ones(targets.shape) * alpha

            alpha_factor = torch.where(torch.eq(targets, 1.), alpha_factor, 1. - alpha_factor)
            focal_weight = torch.where(torch.eq(targets, 1.), 1. - classification, classification)
            focal_weight = alpha_factor * torch.pow(focal_weight, gamma)

            bce = -(targets * torch.log(classification) + (1.0 - targets) * torch.log(1.0 - classification))

            # cls_loss = focal_weight * torch.pow(bce, gamma)
            cls_loss = focal_weight * bce

            if torch.cuda.is_available():
                cls_loss = torch.where(torch.ne(targets, -1.0), cls_loss, torch.zeros(cls_loss.shape).cuda())
            else:
                cls_loss = torch.where(torch.ne(targets, -1.0), cls_loss, torch.zeros(cls_loss.shape))

            classification_losses.append(cls_loss.sum()/torch.clamp(num_positive_anchors.float(), min=1.0))

            # compute the loss for regression

            if positive_indices.sum() > 0:
                assigned_annotations = assigned_annotations[positive_indices, :]

                anchor_widths_pi = anchor_widths[positive_indices]
                anchor_heights_pi = anchor_heights[positive_indices]
                anchor_ctr_x_pi = anchor_ctr_x[positive_indices]
                anchor_ctr_y_pi = anchor_ctr_y[positive_indices]

                gt_widths  = assigned_annotations[:, 2] - assigned_annotations[:, 0]
                gt_heights = assigned_annotations[:, 3] - assigned_annotations[:, 1]
                gt_ctr_x   = assigned_annotations[:, 0] + 0.5 * gt_widths
                gt_ctr_y   = assigned_annotations[:, 1] + 0.5 * gt_heights
                gt_distances = assigned_annotations[:, 5]  # Make sure gt_distances is 2D 

                logger.debug(f"\ninside focal loss after pos mask - gt_w {gt_widths.shape}")
                logger.debug(f"inside focal loss after pos mask - gt_h {gt_heights.shape}")
                logger.debug(f"inside focal loss after pos mask - distance_pred {gt_distances.shape}")
          
                # clip widths to 1
                gt_widths  = torch.clamp(gt_widths, min=1)
                gt_heights = torch.clamp(gt_heights, min=1)

                targets_dx = (gt_ctr_x - anchor_ctr_x_pi) / anchor_widths_pi
                targets_dy = (gt_ctr_y - anchor_ctr_y_pi) / anchor_heights_pi
                targets_dw = torch.log(gt_widths / anchor_widths_pi)
                targets_dh = torch.log(gt_heights / anchor_heights_pi)

                targets = torch.stack((targets_dx, targets_dy, targets_dw, targets_dh))
                targets = targets.t()

                if torch.cuda.is_available():
                    targets = targets/torch.Tensor([[0.1, 0.1, 0.2, 0.2]]).cuda()
                else:
                    targets = targets/torch.Tensor([[0.1, 0.1, 0.2, 0.2]])

                negative_indices = 1 + (~positive_indices)

                regression_diff = torch.abs(targets - regression[positive_indices, :])

                regression_loss = torch.where(
                    torch.le(regression_diff, 1.0 / 9.0),
                    0.5 * 9.0 * torch.pow(regression_diff, 2),
                    regression_diff - 0.5 / 9.0
                )
                regression_losses.append(regression_loss.mean())

                #Distance handling
                distance_pred = distance[positive_indices, :].squeeze()
                logger.debug(f"\ninside focal loss - distance_pred {distance_pred.shape}")
                logger.debug(f"inside focal loss - gt_distances {gt_distances.shape}")

                if self.distance_loss_type == 'l1':
                    distance_loss = nn.L1Loss(reduction='mean')(distance_pred, gt_distances)
                elif self.distance_loss_type == 'huber':
                    distance_loss = nn.HuberLoss(reduction='mean', delta=self.delta)(distance_pred, gt_distances)
                elif self.distance_loss_type == 'l2':
                    distance_loss = nn.MSELoss(reduction='mean')(distance_pred, gt_distances)
                elif self.distance_loss_type == 'smoothl1':
                    distance_loss = nn.SmoothL1Loss(reduction='mean')(distance_pred, gt_distances)
                elif self.distance_loss_type == 'logcosh':
                    distance_loss = logcosh_loss(distance_pred, gt_distances)
                else:
                    logger.error(f"${self.distance_loss_type} is not a valid loss function.")
                    raise ValueError(f"{self.distance_loss_type} is not a valid loss function.")

                distance_losses.append(distance_loss)

            else:
                if torch.cuda.is_available():
                    regression_losses.append(torch.tensor(0).float().cuda())
                else:
                    regression_losses.append(torch.tensor(0).float())
                
                # If there are no positive indices, we append zero loss
                if torch.cuda.is_available():
                    distance_losses.append(torch.tensor(0).float().cuda())
                else:
                    distance_losses.append(torch.tensor(0).float())

        classification_loss = torch.stack(classification_losses).mean(dim=0, keepdim=True)
        regression_loss = torch.stack(regression_losses).mean(dim=0, keepdim=True)
        distance_loss = torch.stack(distance_losses).mean(dim=0, keepdim=True)  # Calculate the mean distance loss

        return classification_loss, regression_loss, distance_loss


