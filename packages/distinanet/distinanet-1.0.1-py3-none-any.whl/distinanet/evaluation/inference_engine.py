"""
Inference Engine for DistinaNet Model Evaluation

This module handles the core inference operations needed for model evaluation:
- Running the model on validation datasets to get predictions
- Extracting ground truth annotations from datasets
- Managing the inference process and timing

Single Responsibility: Model inference and data extraction for evaluation.
"""

import torch
import numpy as np
import time
from distinanet.utils import setup_logger

logger = setup_logger("evaluation", "INFO")

def extract_model_predictions(dataset, distinanet, score_threshold=0.05, max_detections=100):
    """
    Extract predictions from the DistinaNet model for all images in the dataset.
    
    Args:
        dataset: The dataset to run inference on
        distinanet: The trained DistinaNet model
        score_threshold: Minimum confidence score for detections
        max_detections: Maximum number of detections per image
        
    Returns:
        tuple: (all_detections, mean_inference_time)
            - all_detections: List of detections per image per class
            - mean_inference_time: Average time per image inference
    """
    all_detections = [[None for i in range(dataset.num_classes())] for j in range(len(dataset))]

    distinanet.eval()
    inference_times = []
    
    with torch.no_grad():
        for index in range(len(dataset)):
            data = dataset[index]
            scale = data['scale']

            start_time = time.time()
            # run network
            if torch.cuda.is_available():
                scores, labels, boxes, distances = distinanet(data['img'].permute(2, 0, 1).cuda().float().unsqueeze(dim=0))
            else:
                scores, labels, boxes, distances = distinanet(data['img'].permute(2, 0, 1).float().unsqueeze(dim=0))
            inference_time = time.time() - start_time
            inference_times.append(inference_time)

            scores = scores.cpu().numpy()
            labels = labels.cpu().numpy()
            boxes  = boxes.cpu().numpy()
            distances = distances.cpu().numpy()
            
            # correct boxes for image scale
            boxes /= scale

            # select indices which have a score above the threshold
            indices = np.where(scores > score_threshold)[0]

            if indices.shape[0] > 0:
                # select those scores
                scores = scores[indices]

                # find the order with which to sort the scores
                scores_sort = np.argsort(-scores)[:max_detections]
                # select detections
                image_boxes      = boxes[indices[scores_sort], :]
                image_scores     = scores[scores_sort]
                image_labels     = labels[indices[scores_sort]]
                image_distances = distances[indices[scores_sort],:]
                image_detections = np.concatenate([image_boxes, np.expand_dims(image_scores, axis=1), image_distances, np.expand_dims(image_labels, axis=1)], axis=1)

                # copy detections to all_detections
                for label in range(dataset.num_classes()):
                    all_detections[index][label] = image_detections[image_detections[:, -1] == label, :-1]
            else:
                # copy detections to all_detections
                for label in range(dataset.num_classes()):
                    all_detections[index][label] = np.zeros((0, 6))

            logger.info('Generated: {}/{}'.format(index + 1, len(dataset)))

    mean_inference_time = np.mean(inference_times)
    return all_detections, mean_inference_time

def extract_ground_truth_annotations(dataset):
    """
    Extract ground truth annotations from the dataset.
    
    Args:
        dataset: The dataset containing ground truth annotations
        
    Returns:
        list: Ground truth annotations organized by image and class
              all_annotations[image_idx][class_idx] = annotations array
    """
    all_annotations = [[None for i in range(dataset.num_classes())] for j in range(len(dataset))]
    for i in range(len(dataset)):
        annotations = dataset.load_annotations(i)
        for label in range(dataset.num_classes()):
            all_annotations[i][label] = annotations[annotations[:, 4] == label, :6].copy()
        logger.debug('Extracting GT: {}/{}'.format(i + 1, len(dataset)))
    return all_annotations
